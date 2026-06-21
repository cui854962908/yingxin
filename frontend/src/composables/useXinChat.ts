import { ref, computed, nextTick, type Ref } from 'vue'
import { useAppNavigate } from './useAppNavigate'
import { usePreload } from './usePreload'
import type { Msg } from '../components/XinChatBubble.vue'
import type { XinTTS } from './useTTS'

interface FaqItem { question: string; answer: string }
interface AnnounceItem { title: string; content: string }
interface ClubItem { id: string; name: string; intro: string }

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

/** 小信答不上 / 知识库未命中时的跳转（问牧墙优先） */
const KB_HINT_LINKS = [
  { label: '查看问题答疑', to: '/faq' },
  { label: '查看校园公告', to: '/announcements' },
] as const

function wallAskTo(question: string, loggedIn: boolean): string {
  const q = question.trim().slice(0, 120)
  if (!loggedIn || !q) return '/wall'
  return `/wall/new?title=${encodeURIComponent(q)}`
}

function wallFallbackLinks(question: string, loggedIn: boolean): { label: string; to: string }[] {
  const askTo = wallAskTo(question, loggedIn)
  const hasQ = !!question.trim()
  return [
    {
      label: loggedIn && hasQ ? '🌾 去问牧墙提问' : '🌾 去问牧墙',
      to: askTo,
    },
    { label: '查看问题答疑', to: '/faq' },
    { label: '查看校园公告', to: '/announcements' },
  ]
}

/** SSE 返回的静态 /wall 链接按当前问题改写为发帖页预填 */
function applyWallAskToLinks(
  links: { label: string; to: string }[],
  question: string,
  loggedIn: boolean,
): { label: string; to: string }[] {
  return links.map((l) => {
    if (l.to !== '/wall') return l
    const to = wallAskTo(question, loggedIn)
    return {
      ...l,
      to,
      label: loggedIn && question.trim() ? '🌾 去问牧墙提问' : l.label,
    }
  })
}

function linksAfterAgent(
  source: string,
  question: string,
  loggedIn: boolean,
): { label: string; to: string }[] | null {
  if (source === 'fallback') return wallFallbackLinks(question, loggedIn)
  if (['faq', 'xiaoxin_kb', 'personal'].includes(source)) return [...KB_HINT_LINKS]
  return null
}

const QUICK_TAG_MAX = 6
const QUICK_TAG_LABEL_MAX = 12

/** 从 FAQ 排序生成快捷标签（与后台拖拽顺序一致） */
export function buildQuickTagsFromFaq(
  faqs: { question: string }[],
  max = QUICK_TAG_MAX,
): { label: string; text: string }[] {
  return faqs.slice(0, max).map((f) => {
    const text = f.question.trim()
    const label = text.length <= QUICK_TAG_LABEL_MAX
      ? text
      : `${text.slice(0, QUICK_TAG_LABEL_MAX)}…`
    return { label, text }
  })
}

export function useXinChat(
  autoSpeak: Ref<boolean>,
  tts: XinTTS,
  externalOpen?: Ref<boolean>,
) {
  const { speakSynced, stopSpeak } = tts
  const open = externalOpen ?? ref(false)
  const { appNavigate } = useAppNavigate()
  const messages = ref<Msg[]>([])
  const input = ref('')
  const sending = ref(false)
  const chatBody = ref<HTMLElement | null>(null)
  let typeQueue: Array<{ idx: number; timer: ReturnType<typeof setTimeout> }> = []

  const faqData = ref<{ q: string; a: string }[]>([])
  const announceData = ref<{ title: string; content: string }[]>([])
  const clubData = ref<ClubItem[]>([])
  const useLLM = ref(true)
  const { faqItems, announcements, clubs } = usePreload()
  const quickList = computed(() => buildQuickTagsFromFaq(faqItems.value))

  function syncFallbackFromCache() {
    if (faqData.value.length === 0 && faqItems.value.length > 0) {
      faqData.value = faqItems.value.map(x => ({ q: x.question, a: x.answer }))
    }
    if (announceData.value.length === 0 && announcements.value.length > 0) {
      announceData.value = announcements.value.map(x => ({ title: x.title, content: x.content }))
    }
    if (clubData.value.length === 0 && clubs.value.length > 0) {
      clubData.value = clubs.value.map((c: ClubItem) => ({ id: c.id, name: c.name, intro: c.intro }))
    }
  }

  function now() {
    return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  function scrollBottom() {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  }

  function pushLinkMsg(links: { label: string; to: string }[], wallAsk = false) {
    const text = wallAsk
      ? '要不要把刚才的问题发到问牧墙，让学长学姐帮你？'
      : '需要我帮你跳转到相关页面查看详细信息吗？'
    messages.value.push({
      role: 'xin', time: now(),
      text,
      displayText: text,
      done: true, links,
    })
    nextTick(() => scrollBottom())
  }

  function scheduleNextChar(idx: number, i: number) {
    const msg = messages.value[idx]
    if (!msg || i >= msg.text.length) {
      if (msg) msg.done = true
      return
    }
    msg.displayText = msg.text.slice(0, i + 1)
    nextTick(() => scrollBottom())
    let delay = 10 + Math.random() * 10
    const ch = msg.text[i]
    if ('，。！？、；：\n'.includes(ch)) delay = 40 + Math.random() * 50
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
    stopSpeak()
  }

  function revealXinMsg(idx: number, text: string) {
    const msg = messages.value[idx]
    if (!msg) return
    if (autoSpeak.value) {
      void speakSynced(
        text,
        (partial) => {
          msg.displayText = partial
          scrollBottom()
        },
        () => { msg.displayText = text; msg.done = true },
      )
    } else {
      scheduleNextChar(idx, 0)
    }
  }

  function pushXinMsg(text: string, source?: string) {
    messages.value.push({ role: 'xin', text, time: now(), displayText: '', done: false, source })
    const idx = messages.value.length - 1
    nextTick(() => {
      scrollBottom()
      revealXinMsg(idx, text)
    })
  }

  function ensureWelcome() {
    if (messages.value.length === 0) {
      pushXinMsg('你好！我是来自河南牧业经济学院信息工程学院的小信，有什么不懂的请尽管问我吧。')
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
    const source: string = data.data.source || 'agent'

    pushXinMsg(reply, source)

    const agentLinks = linksAfterAgent(source, q, !!token)
    if (agentLinks) {
      const wallAsk = source === 'fallback'
      setTimeout(() => pushLinkMsg(agentLinks, wallAsk), 300)
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

    messages.value.push({ role: 'xin', text: '', time: now(), displayText: '', done: false, source: 'sse' })
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

    const streamSyncSpeak = autoSpeak.value

    return new Promise((resolve) => {
      function drain() {
        if (tokenBuffer.length === 0) {
          if (streamDone) {
            const full = messages.value[idx].text
            if (streamSyncSpeak && full) {
              messages.value[idx].displayText = ''
              messages.value[idx].done = false
              revealXinMsg(idx, full)
            } else {
              messages.value[idx].done = true
            }
            if (doneLinks?.length) {
              const resolved = applyWallAskToLinks(doneLinks, q, !!authToken())
              const wallAsk = resolved.some(l => l.to.startsWith('/wall/new'))
              pushLinkMsg(resolved, wallAsk)
            }
            resolve(true)
            return
          }
          setTimeout(drain, 30)
          return
        }

        if (sending.value) sending.value = false

        const ch = tokenBuffer.shift()!
        messages.value[idx].text += ch
        if (!streamSyncSpeak) {
          messages.value[idx].displayText = messages.value[idx].text
          scrollBottom()
        }

        const delay = streamSyncSpeak
          ? 0
          : ('，。！？、；：\n'.includes(ch) ? 40 + Math.random() * 50 : 10 + Math.random() * 10)
        setTimeout(drain, delay)
      }
      drain()
    })
  }

  function findAnswer(q: string): { answer: string; links?: { label: string; to: string }[] } {
    const faqMatch = faqData.value.find(f => f.q.includes(q) || q.includes(f.q.slice(0, 4)))
    if (faqMatch) return {
      answer: faqMatch.a,
      links: [{ label: '查看问题答疑', to: '/faq' }],
    }

    const annMatch = announceData.value.find(a => a.title.includes(q) || q.includes(a.title.slice(0, 4)))
    if (annMatch) return {
      answer: `相关公告：${annMatch.title}\n\n${annMatch.content}`,
      links: [{ label: '查看校园公告', to: '/announcements' }],
    }

    // 社团搜索
    const clubKeywords = ['社', '社团', '俱乐部', '协会']
    const isClubQuery = clubKeywords.some(k => q.includes(k))
    if (isClubQuery && clubData.value.length > 0) {
      const cleanQ = q.replace(/有没有|有没有什么|有.*吗|在哪|在哪里/g, '')
      const clubMatch = clubData.value.find(c =>
        c.name.includes(cleanQ) || cleanQ.includes(c.name.slice(0, 3)),
      )
      if (clubMatch) {
        return {
          answer: `${clubMatch.name}：${clubMatch.intro}\n\n想了解更多详情吗？`,
          links: [{ label: `查看${clubMatch.name}详情`, to: `/clubs/${clubMatch.id}` }],
        }
      }
      const allMatches = clubData.value.filter(c => c.name.includes(cleanQ) || cleanQ.includes(c.name.charAt(0)))
      if (allMatches.length > 1) {
        return {
          answer: `我找到了 ${allMatches.length} 个相关社团：${allMatches.map(c => c.name).join('、')}`,
          links: allMatches.slice(0, 3).map(c => ({ label: c.name, to: `/clubs/${c.id}` })),
        }
      }
    }

    return {
      answer: `这个问题我暂时答不上来。\n\n关于「${q.slice(0, 15)}」，建议你：\n• 去「问牧墙」发帖，让学长学姐帮你\n• 查看校园公告或问题答疑\n• 联系辅导员获取一对一帮助`,
      links: wallFallbackLinks(q, !!authToken()),
    }
  }

  async function fallbackReply(q: string) {
    syncFallbackFromCache()
    if (faqData.value.length === 0) {
      try {
        const [faqRes, annRes, clubsRes] = await Promise.all([
          fetch('/api/faq'),
          fetch('/api/announcements'),
          fetch('/api/clubs'),
        ])
        const faqJson = await faqRes.json()
        const annJson = await annRes.json()
        const clubsJson = await clubsRes.json()
        if (faqJson.success) faqData.value = faqJson.data.map((x: FaqItem) => ({ q: x.question, a: x.answer }))
        if (annJson.success) announceData.value = annJson.data.map((x: AnnounceItem) => ({ title: x.title, content: x.content }))
        if (clubsJson.success) clubData.value = clubsJson.data.map((c: ClubItem) => ({ id: c.id, name: c.name, intro: c.intro }))
      } catch { /* 加载数据失败，继续使用本地兜底 */ }
    }

    const { answer, links } = findAnswer(q)
    setTimeout(() => {
      sending.value = false
      pushXinMsg(answer, 'local')
      if (links && links.length > 0) {
        const wallAsk = links.some(l => l.to.startsWith('/wall/new'))
        setTimeout(() => pushLinkMsg(links, wallAsk), 300)
      }
    }, 300)
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
    appNavigate(to)
  }

  function closeChat() { open.value = false }

  return {
    open, messages, input, sending, chatBody, quickList,
    send, onKeydown, closeChat, navigateTo, ensureWelcome, scrollBottom,
  }
}
