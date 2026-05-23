import { ref, nextTick, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import type { Msg } from '../components/XinChatBubble.vue'

interface AgentResponse {
  success: boolean
  message?: string
  data?: {
    reply: string
    intent?: string
    source?: string
    matched_title?: string | null
  }
}

export function useXinChat(autoSpeak: Ref<boolean>, speak: (text: string) => void) {
  const open = ref(false)
  const router = useRouter()
  const messages = ref<Msg[]>([])
  const input = ref('')
  const sending = ref(false)
  const chatBody = ref<HTMLElement | null>(null)
  let typeQueue: Array<{ idx: number; timer: ReturnType<typeof setTimeout> }> = []
  let welcomeSpoken = false

  const quickList = [
    { label: '📦 快递在哪', text: '快递在哪' },
    { label: '🏠 熄灯时间', text: '宿舍几点熄灯' },
    { label: '💰 学费', text: '学费怎么交' },
    { label: '🪪 校园卡', text: '校园卡补办' },
  ]
  const faqData = ref<{ q: string; a: string }[]>([])
  const announceData = ref<{ title: string; content: string }[]>([])
  const useLLM = ref(true)

  function now() {
    return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  function scrollBottom() {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  }

  function pushLinkMsg(links: { label: string; to: string }[]) {
    messages.value.push({
      role: 'xin', time: now(),
      text: '需要我帮你跳转到相关页面查看详细信息吗？',
      displayText: '需要我帮你跳转到相关页面查看详细信息吗？',
      done: true, links,
    })
    nextTick(() => scrollBottom())
  }

  function scheduleNextChar(idx: number, i: number) {
    const msg = messages.value[idx]
    if (!msg || i >= msg.text.length) {
      if (msg) {
        msg.done = true
        if (msg.role === 'xin' && messages.value.length > 1 && autoSpeak.value) speak(msg.text)
      }
      return
    }
    msg.displayText = msg.text.slice(0, i + 1)
    nextTick(() => scrollBottom())
    let delay = 25 + Math.random() * 20
    const ch = msg.text[i]
    if ('，。！？、；：\n'.includes(ch)) delay = 120 + Math.random() * 130
    const timer = setTimeout(() => scheduleNextChar(idx, i + 1), delay)
    typeQueue.push({ idx, timer })
  }

  function finishTyping() {
    typeQueue.forEach(({ idx, timer }) => {
      clearTimeout(timer)
      const msg = messages.value[idx]
      if (msg) { msg.displayText = msg.text; msg.done = true }
    })
    typeQueue = []
  }

  function pushXinMsg(text: string) {
    messages.value.push({ role: 'xin', text, time: now(), displayText: '', done: false })
    const idx = messages.value.length - 1
    nextTick(() => scrollBottom())
    scheduleNextChar(idx, 0)
  }

  function ensureWelcome() {
    if (messages.value.length === 0) {
      pushXinMsg('你好！我是来自河南牧业经济学院信息工程学院的小信，有什么不懂的请尽管问我吧。')
      if (!welcomeSpoken) {
        welcomeSpoken = true
        setTimeout(() => speak('你好！我是来自河南牧业经济学院信息工程学院的小信，有什么不懂的请尽管问我吧。'), 800)
      }
    }
  }

  function authToken(): string | null {
    return localStorage.getItem('token')
  }

  async function tryAgentChat(q: string): Promise<boolean> {
    const token = authToken()
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`

    let resp: Response
    try {
      resp = await fetch('/api/agent/chat', {
        method: 'POST', headers,
        body: JSON.stringify({ message: q }),
        signal: AbortSignal.timeout(15000),
      })
    } catch { return false }

    if (!resp.ok) return false

    let data: AgentResponse
    try { data = await resp.json() } catch { return false }
    if (!data?.success || !data?.data?.reply) return false

    const reply: string = data.data.reply
    const source: string = data.data.source || ''

    pushXinMsg(reply)

    const showLinks = ['faq', 'xiaoxin_kb', 'personal'].includes(source)
    if (showLinks) {
      setTimeout(() => pushLinkMsg([
        { label: '📋 查看问题答疑', to: '/faq' },
        { label: '📢 查看校园公告', to: '/announcements' },
      ]), 600)
    }

    sending.value = false
    return true
  }

  async function tryChatStream(q: string): Promise<boolean> {
    let resp: Response
    try {
      resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
        signal: AbortSignal.timeout(15000),
      })
      if (!resp.ok || !resp.body) return false
    } catch { return false }

    messages.value.push({ role: 'xin', text: '', time: now(), displayText: '', done: false })
    const idx = messages.value.length - 1
    scrollBottom()

    const tokenBuffer: string[] = []
    let streamDone = false
    let doneLinks: { label: string; to: string }[] | undefined

    async function readSSE() {
      try {
        const reader = resp.body!.getReader()
        const decoder = new TextDecoder()
        let buf = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buf += decoder.decode(value, { stream: true })
          const blocks = buf.split('\n\n')
          buf = blocks.pop() || ''
          for (const block of blocks) {
            const dataLine = block.split('\n').find(l => l.startsWith('data: '))
            if (!dataLine) continue
            try {
              const json = JSON.parse(dataLine.slice(6))
              if (json.token) tokenBuffer.push(json.token)
              if (json.done) { streamDone = true; doneLinks = json.links }
              if (json.error) { streamDone = true }
            } catch { /* SSE token JSON 解析失败，跳过 */ }
          }
        }
      } catch { streamDone = true }
    }

    readSSE()

    return new Promise((resolve) => {
      function drain() {
        if (tokenBuffer.length === 0) {
          if (streamDone) {
            messages.value[idx].done = true
            if (doneLinks?.length) pushLinkMsg(doneLinks)
            if (autoSpeak.value) speak(messages.value[idx].text)
            resolve(true)
            return
          }
          setTimeout(drain, 30)
          return
        }

        if (sending.value) sending.value = false

        const ch = tokenBuffer.shift()!
        messages.value[idx].text += ch
        messages.value[idx].displayText = messages.value[idx].text
        scrollBottom()

        const delay = '，。！？、；：\n'.includes(ch) ? 120 + Math.random() * 130 : 25 + Math.random() * 20
        setTimeout(drain, delay)
      }
      drain()
    })
  }

  function findAnswer(q: string): { answer: string; links?: { label: string; to: string }[] } {
    const faqMatch = faqData.value.find(f => f.q.includes(q) || q.includes(f.q.slice(0, 4)))
    if (faqMatch) return {
      answer: faqMatch.a,
      links: [{ label: '📋 查看问题答疑', to: '/faq' }],
    }

    const annMatch = announceData.value.find(a => a.title.includes(q) || q.includes(a.title.slice(0, 4)))
    if (annMatch) return {
      answer: `📢 相关公告：${annMatch.title}\n\n${annMatch.content}`,
      links: [{ label: '📢 查看校园公告', to: '/announcements' }],
    }

    return {
      answer: `这个问题小信目前还不知道 🥲\n\n关于「${q.slice(0, 15)}」，建议你：\n• 查看校园公告了解最新动态\n• 在问题答疑页面搜索 FAQ\n• 联系辅导员获取一对一帮助\n\n还有其他问题吗？😊`,
      links: [
        { label: '📢 查看校园公告', to: '/announcements' },
        { label: '📋 查看问题答疑', to: '/faq' },
      ],
    }
  }

  async function fallbackReply(q: string) {
    if (faqData.value.length === 0) {
      try {
        const [faqRes, annRes] = await Promise.all([
          fetch('/api/faq'),
          fetch('/api/announcements'),
        ])
        const faqJson = await faqRes.json()
        const annJson = await annRes.json()
        if (faqJson.success) faqData.value = faqJson.data.map((x: any) => ({ q: x.question, a: x.answer }))
        if (annJson.success) announceData.value = annJson.data.map((x: any) => ({ title: x.title, content: x.content }))
      } catch { /* 加载FAQ/公告数据失败，继续使用本地兜底 */ }
    }

    const { answer, links } = findAnswer(q)
    setTimeout(() => {
      sending.value = false
      pushXinMsg(answer)
      if (links && links.length > 0) {
        setTimeout(() => pushLinkMsg(links), 600)
      }
    }, 400)
  }

  async function send() {
    const q = input.value.trim()
    if (!q || sending.value) return
    finishTyping()
    messages.value.push({ role: 'user', text: q, time: now(), displayText: q, done: true })
    input.value = ''
    sending.value = true
    await nextTick(); scrollBottom()

    if (useLLM.value) {
      const ok = await tryAgentChat(q)
      if (ok) return
    }

    if (useLLM.value) {
      const ok = await tryChatStream(q)
      if (ok) return
    }

    useLLM.value = false
    await fallbackReply(q)
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  function navigateTo(to: string) {
    open.value = false
    router.push(to)
  }

  function closeChat() { open.value = false }

  return {
    open, messages, input, sending, chatBody, quickList,
    send, onKeydown, closeChat, navigateTo, ensureWelcome, scrollBottom,
  }
}
