<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import lottie from 'lottie-web'

const lottieRef = ref<HTMLElement | null>(null)
const x = ref(window.innerWidth - 220)
const y = ref(window.innerHeight - 280)
const dragging = ref(false)
const dragStart = ref({ x: 0, y: 0, bx: 0, by: 0 })
const isMobile = ref(false)
let dragMoved = false

function checkMobile() { isMobile.value = window.innerWidth < 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => { window.removeEventListener('resize', checkMobile) })

function onPointerDown(e: PointerEvent) {
  dragging.value = true; dragMoved = false
  dragStart.value = { x: e.clientX, y: e.clientY, bx: x.value, by: y.value };
  (e.target as HTMLElement).setPointerCapture(e.pointerId)
}
function onPointerMove(e: PointerEvent) {
  if (!dragging.value) return
  const dx = e.clientX - dragStart.value.x; const dy = e.clientY - dragStart.value.y
  if (Math.abs(dx) > 2 || Math.abs(dy) > 2) dragMoved = true
  x.value = Math.max(10, Math.min(window.innerWidth - 10, dragStart.value.bx + dx))
  y.value = Math.max(10, Math.min(window.innerHeight - 10, dragStart.value.by + dy))
}
function onPointerUp() { dragging.value = false }
function onClickXin() { if (!dragMoved) { open.value = true; nextTick(() => ensureWelcome()) } }

// ===== 聊天状态 =====
const open = ref(false)
const router = useRouter()

interface Msg { role: 'user' | 'xin'; text: string; time: string; displayText: string; done: boolean; links?: { label: string; to: string }[] }
const messages = ref<Msg[]>([])
const input = ref('')
const sending = ref(false)
const chatBody = ref<HTMLElement | null>(null)
let typeQueue: Array<{ idx: number; timer: ReturnType<typeof setTimeout> }> = []

function now() { return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }

function ensureWelcome() {
  if (messages.value.length === 0) {
    pushXinMsg('你好！我是来自河南牧业经济学院信息工程学院的小信，有什么不懂的请尽管问我吧。')
  }
}

function pushXinMsg(text: string) {
  messages.value.push({ role: 'xin', text, time: now(), displayText: '', done: false })
  const idx = messages.value.length - 1
  nextTick(() => scrollBottom())
  scheduleNextChar(idx, 0)
}

function scheduleNextChar(idx: number, i: number) {
  const msg = messages.value[idx]  // ← 从 reactive 数组取值，确保响应式
  if (!msg || i >= msg.text.length) {
    if (msg) msg.done = true
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

// ===== FAQ / 公告 / 回复 =====
const quickList = [
  { label: '📦 快递在哪', text: '快递在哪' },
  { label: '🏠 熄灯时间', text: '宿舍几点熄灯' },
  { label: '💰 学费', text: '学费怎么交' },
  { label: '🪪 校园卡', text: '校园卡补办' },
]
const faqData = ref<{ q: string; a: string }[]>([])
const announceData = ref<{ title: string; content: string }[]>([])
const useLLM = ref(true)  // 后端 /chat 可用时走 LLM，不可用自动回退

async function send() {
  const q = input.value.trim()
  if (!q || sending.value) return
  finishTyping()
  messages.value.push({ role: 'user', text: q, time: now(), displayText: q, done: true })
  input.value = ''
  sending.value = true
  await nextTick(); scrollBottom()

  // 优先尝试 /api/chat SSE 流
  if (useLLM.value) {
    const ok = await tryChatStream(q)
    if (ok) return
    useLLM.value = false  // 失败了下次直接走兜底
  }

  // 兜底：原有 FAQ/公告匹配
  await fallbackReply(q)
}

async function tryChatStream(q: string): Promise<boolean> {
  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q }),
      signal: AbortSignal.timeout(15000),
    })
    if (!resp.ok || !resp.body) return false

    const msg: Msg = { role: 'xin', text: '', time: now(), displayText: '', done: false }
    messages.value.push(msg)
    scrollBottom()

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // 解析 SSE: "data: {...}\n\n"
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const block of lines) {
        const dataLine = block.split('\n').find(l => l.startsWith('data: '))
        if (!dataLine) continue
        try {
          const json = JSON.parse(dataLine.slice(6))
          if (json.token) {
            msg.text += json.token
            msg.displayText = msg.text
          }
          if (json.done) {
            msg.done = true
            sending.value = false
            if (json.links?.length) pushLinkMsg(json.links)
            return true
          }
          if (json.error) {
            // 后端明确返回错误，回退
            messages.value.pop()
            return false
          }
        } catch { /* broken JSON, skip */ }
      }
      scrollBottom()
    }

    msg.done = true
    sending.value = false
    return true
  } catch {
    return false
  }
}

async function fallbackReply(q: string) {
  // 拉取 FAQ 和公告数据（仅首次）
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
    } catch { /* */ }
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

function findAnswer(q: string): { answer: string; links?: { label: string; to: string }[] } {
  // 1. FAQ 匹配
  const faqMatch = faqData.value.find(f => f.q.includes(q) || q.includes(f.q.slice(0, 4)))
  if (faqMatch) return {
    answer: faqMatch.a,
    links: [{ label: '📋 查看问题答疑', to: '/faq' }],
  }

  // 2. 公告匹配
  const annMatch = announceData.value.find(a => a.title.includes(q) || q.includes(a.title.slice(0, 4)))
  if (annMatch) return {
    answer: `📢 相关公告：${annMatch.title}\n\n${annMatch.content}`,
    links: [{ label: '📢 查看校园公告', to: '/announcements' }],
  }

  // 3. 内置关键词兜底
  const kw: Record<string, string> = {
    '快递': '快递站位于北苑食堂西侧，凭取件码和校园卡取件。\n\n① 收到短信后查看取件码\n② 按货架号找到包裹\n③ 出示校园卡核验\n④ 核验通过取走包裹',
    '宿舍': '周日到周四 23:00 熄灯，周五周六 23:30 熄灯。\n\n门禁每晚 22:30 只进不出，23:00 锁门。',
    '食堂': '学校有北苑食堂、南苑食堂、西区美食广场三个食堂，均支持校园卡和手机支付。',
    '军训': '军训为期两周，9月进行。服装在体育馆一楼领取，带录取通知书即可。',
    '学费': '通过学校统一支付平台缴费，支持微信/支付宝/银联。每学期开学两周内缴清，可申请助学贷款。',
    '图书馆': '图书馆位于校园中心，7:00-22:00 开放，凭校园卡入馆。期末周延长至 23:00。',
    '选课': '选课通过教务系统，开学前一周开放。热门课程拼手速！',
    '校园卡': '入学时统一发放。补办：行政楼一楼卡务中心，带身份证+学生证，工本费 20 元，立等可取。',
  }
  for (const [k, v] of Object.entries(kw)) {
    if (q.includes(k)) return {
      answer: v,
      links: [
        { label: '📋 查看问题答疑', to: '/faq' },
        { label: '📢 查看校园公告', to: '/announcements' },
      ],
    }
  }

  // 4. 通用引导
  return {
    answer: `这个问题小信目前还不知道 🥲\n\n关于「${q.slice(0, 15)}」，建议你：\n• 查看校园公告了解最新动态\n• 在问题答疑页面搜索 FAQ\n• 联系辅导员获取一对一帮助\n\n还有其他问题吗？😊`,
    links: [
      { label: '📢 查看校园公告', to: '/announcements' },
      { label: '📋 查看问题答疑', to: '/faq' },
    ],
  }
}

function pushLinkMsg(links: { label: string; to: string }[]) {
  const labels = links.map(l => l.label).join('  ')
  messages.value.push({
    role: 'xin', time: now(),
    text: `需要我帮你跳转到相关页面查看详细信息吗？\n\n${labels}`,
    displayText: `需要我帮你跳转到相关页面查看详细信息吗？\n\n${labels}`,
    done: true, links,
  })
  nextTick(() => scrollBottom())
}

function navigateTo(to: string) {
  open.value = false
  router.push(to)
}

function scrollBottom() {
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
}
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
}
function onKeyup(e: KeyboardEvent) { if (e.key === 'Escape') open.value = false }

// ===== Lottie =====
let anim: any = null
onMounted(() => {
  if (lottieRef.value) {
    anim = lottie.loadAnimation({
      container: lottieRef.value, renderer: 'svg', loop: true, autoplay: true,
      path: '/animation/Live chatbot.json',
    })
  }
  document.addEventListener('pointermove', onPointerMove)
  document.addEventListener('pointerup', onPointerUp)
  document.addEventListener('keyup', onKeyup)
})
onUnmounted(() => {
  anim?.destroy()
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', onPointerUp)
  document.removeEventListener('keyup', onKeyup)
})

function closeChat() { open.value = false }
</script>

<template>
  <!-- ========== 小信悬浮角色 ========== -->
  <div
    class="xin-character"
    :style="{ left: x + 'px', top: y + 'px' }"
    :class="{ dragging }"
    @pointerdown.prevent="onPointerDown"
    @click="onClickXin"
  >
    <div ref="lottieRef" class="xin-lottie" />
    <div class="xin-glow" />
    <!-- 科技粒子环 -->
    <div class="xin-orbit" />
  </div>

  <!-- 桌面遮罩 -->
  <Transition name="overlay">
    <div v-if="open && !isMobile" class="xin-overlay" @click="closeChat" />
  </Transition>

  <!-- ========== 聊天面板 ========== -->
  <Transition :name="isMobile ? 'chat-mobile' : 'chat-desktop'">
    <div v-if="open" :class="['xin-panel', { mobile: isMobile }]">
      <!-- 科技角标装饰 -->
      <div class="tech-corners">
        <span class="tc tl" /><span class="tc tr" /><span class="tc bl" /><span class="tc br" />
      </div>

      <!-- 头部 -->
      <div class="panel-header">
        <!-- 电路纹装饰 -->
        <div class="circuit-lines" />
        <button v-if="isMobile" class="back-btn" @click="closeChat">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <!-- 机器人头像 -->
        <div class="robot-avatar">
          <svg viewBox="0 0 48 48" fill="none">
            <!-- 天线 -->
            <line x1="24" y1="6" x2="24" y2="2" stroke="#409eff" stroke-width="2" stroke-linecap="round"/>
            <circle cx="24" cy="1.5" r="1.5" fill="#409eff">
              <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <!-- 头部 -->
            <rect x="8" y="8" width="32" height="28" rx="6" fill="#15202b" stroke="#409eff" stroke-width="1.5"/>
            <!-- 耳轴 -->
            <rect x="4" y="18" width="4" height="8" rx="2" fill="#1a3050" stroke="#409eff" stroke-width="1"/>
            <rect x="40" y="18" width="4" height="8" rx="2" fill="#1a3050" stroke="#409eff" stroke-width="1"/>
            <!-- 眼睛 -->
            <circle cx="18" cy="19" r="3.5" fill="#409eff">
              <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="30" cy="19" r="3.5" fill="#409eff">
              <animate attributeName="opacity" values="1;0.5;1" dur="2s" begin="0.3s" repeatCount="indefinite"/>
            </circle>
            <!-- 嘴 -->
            <rect x="17" y="27" width="14" height="3" rx="1.5" fill="#409eff" opacity="0.6"/>
            <!-- 额头指示灯 -->
            <rect x="21" y="10" width="6" height="2" rx="1" fill="#409eff" opacity="0.4">
              <animate attributeName="opacity" values="0.4;0.9;0.4" dur="2.5s" repeatCount="indefinite"/>
            </rect>
          </svg>
        </div>
        <div class="panel-header-text">
          <span class="panel-title">小信</span>
          <span class="panel-subtitle">
            <span class="online-dot" />在线 · AI 引擎 v2.0
          </span>
        </div>
        <button v-if="!isMobile" class="panel-close" @click="closeChat">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- 消息区 -->
      <div ref="chatBody" class="panel-body">
        <!-- 空态欢迎 -->
        <div v-for="(m, i) in messages" :key="i" :class="['msg-row', m.role]">
          <div v-if="m.role === 'xin'" class="msg-avatar">
            <!-- 小机器人头像 -->
            <svg viewBox="0 0 32 32" fill="none">
              <rect x="5" y="6" width="22" height="19" rx="5" fill="#15202b" stroke="#409eff" stroke-width="1.2"/>
              <line x1="16" y1="4" x2="16" y2="1.5" stroke="#409eff" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="16" cy="1" r="1.5" fill="#409eff"/>
              <circle cx="12" cy="13.5" r="2.5" fill="#409eff"/>
              <circle cx="20" cy="13.5" r="2.5" fill="#409eff"/>
              <rect x="10.5" y="19" width="11" height="2" rx="1" fill="#409eff" opacity="0.5"/>
            </svg>
          </div>
          <div :class="['msg-bubble', m.role]">
            <span class="msg-text" v-html="(m.role === 'xin' ? (m.displayText || '') : m.text).replace(/\n/g, '<br>')" />
            <span v-if="m.role === 'xin' && !m.done" class="msg-cursor">|</span>
            <span class="msg-time">{{ m.time }}</span>
            <!-- 跳转链接按钮 -->
            <div v-if="m.role === 'xin' && m.links && m.links.length > 0 && m.done" class="msg-links">
              <button v-for="(l, li) in m.links" :key="li" class="msg-link-btn" @click="navigateTo(l.to)">{{ l.label }}</button>
            </div>
          </div>
        </div>
        <!-- 正在输入 -->
        <div v-if="sending" class="msg-row xin">
          <div class="msg-avatar">
            <svg viewBox="0 0 32 32" fill="none">
              <rect x="5" y="6" width="22" height="19" rx="5" fill="#15202b" stroke="#409eff" stroke-width="1.2"/>
              <line x1="16" y1="4" x2="16" y2="1.5" stroke="#409eff" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="16" cy="1" r="1.5" fill="#409eff"/>
              <circle cx="12" cy="13.5" r="2.5" fill="#409eff"/>
              <circle cx="20" cy="13.5" r="2.5" fill="#409eff"/>
              <rect x="10.5" y="19" width="11" height="2" rx="1" fill="#409eff" opacity="0.5"/>
            </svg>
          </div>
          <div class="msg-bubble xin typing-bubble">
            <span class="typing-dot" /><span class="typing-dot" /><span class="typing-dot" />
          </div>
        </div>
      </div>

      <!-- 数据流装饰条 -->
      <div class="data-stream">
        <span v-for="n in 6" :key="n" class="data-block" :style="{ animationDelay: n * 0.3 + 's' }" />
      </div>

      <!-- 快捷标签 -->
      <div class="quick-tags">
        <button v-for="(t, idx) in quickList" :key="idx"
          class="quick-tag" @click="input = t.text; send()">{{ t.label }}</button>
      </div>

      <!-- 输入区 -->
      <div class="panel-footer">
        <div class="input-box">
          <textarea v-model="input" class="chat-input" placeholder="输入消息，Enter 发送…"
            rows="1" @keydown="onKeydown" :disabled="sending" />
          <button class="send-btn" @click="send" :disabled="!input.trim() || sending">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* ===== 小信悬浮角色 ===== */
.xin-character {
  position: fixed; z-index: 9999;
  width: 180px; height: 180px;
  cursor: pointer; user-select: none; touch-action: none;
  display: flex; align-items: center; justify-content: center;
  background: transparent;
  transition: transform .2s cubic-bezier(.33,1,.68,1), filter .3s;
  -webkit-tap-highlight-color: transparent;
}
.xin-character:hover { transform: scale(1.1); filter: drop-shadow(0 0 36px rgba(64,158,255,.5)); }
.xin-character.dragging { cursor: grabbing; transform: scale(1.05); }
.xin-lottie { width: 170px; height: 170px; pointer-events: none; }
.xin-lottie :deep(svg) { width: 100% !important; height: 100% !important; }
.xin-glow {
  position: absolute; inset: -20px; border-radius: 50%;
  background: radial-gradient(circle, rgba(64,158,255,.22) 0%, transparent 65%);
  animation: glowBreathe 3s ease-in-out infinite; pointer-events: none;
}
@keyframes glowBreathe {
  0%, 100% { opacity: .3; transform: scale(.85); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 科技粒子轨道环 */
.xin-orbit {
  position: absolute; inset: -10px; border-radius: 50%;
  border: 1.5px dashed rgba(64,158,255,.25);
  animation: orbitSpin 8s linear infinite; pointer-events: none;
}
@keyframes orbitSpin { to { transform: rotate(360deg) } }

/* ===== 遮罩 ===== */
.xin-overlay {
  position: fixed; inset: 0; z-index: 9997;
  background: rgba(5,12,30,.5); backdrop-filter: blur(6px);
}
.overlay-enter-active { animation: fadeIn .3s ease-out both; }
.overlay-leave-active { animation: fadeOut .2s ease-in both; }
@keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
@keyframes fadeOut { from { opacity: 1 } to { opacity: 0 } }

/* ===== 面板 ===== */
.xin-panel {
  position: fixed; z-index: 9998; top: 0; right: 0; bottom: 0;
  width: 420px; max-width: 100vw;
  background: #0c1a2d;
  box-shadow: -8px 0 50px rgba(0,0,0,.4);
  display: flex; flex-direction: column;
}
.xin-panel.mobile { width: 100vw; box-shadow: none; }

/* 科技角标 */
.tech-corners { position: absolute; inset: 0; z-index: 2; pointer-events: none; overflow: hidden; }
.tc { position: absolute; width: 20px; height: 20px; border-color: rgba(64,158,255,.3); border-style: solid; }
.tc.tl { top: 10px; left: 10px; border-width: 1.5px 0 0 1.5px; border-radius: 4px 0 0 0; }
.tc.tr { top: 10px; right: 10px; border-width: 1.5px 1.5px 0 0; border-radius: 0 4px 0 0; }
.tc.bl { bottom: 10px; left: 10px; border-width: 0 0 1.5px 1.5px; border-radius: 0 0 0 4px; }
.tc.br { bottom: 10px; right: 10px; border-width: 0 1.5px 1.5px 0; border-radius: 0 0 4px 0; }

.chat-desktop-enter-active { animation: slideIn .35s cubic-bezier(.22,1,.36,1) both; }
.chat-desktop-leave-active { animation: slideOut .25s cubic-bezier(.55,0,1,.45) both; }
@keyframes slideIn { from { transform: translateX(100%) } to { transform: translateX(0) } }
@keyframes slideOut { to { transform: translateX(100%) } }

.chat-mobile-enter-active { animation: mobileIn .3s cubic-bezier(.33,1,.68,1) both; }
.chat-mobile-leave-active { animation: mobileOut .25s ease-in both; }
@keyframes mobileIn { from { opacity: 0; transform: scale(1.03) } to { opacity: 1; transform: scale(1) } }
@keyframes mobileOut { to { opacity: 0; transform: scale(.98) } }

/* ===== 头部 ===== */
.panel-header {
  display: flex; align-items: center; gap: 10px;
  padding: 18px; flex-shrink: 0;
  background: linear-gradient(180deg, #0d1f38 0%, #0f2945 100%);
  position: relative; overflow: hidden;
  border-bottom: 1px solid rgba(64,158,255,.15);
}
/* 电路纹 */
.circuit-lines {
  position: absolute; inset: 0; opacity: .25;
  background:
    linear-gradient(90deg, transparent 48%, rgba(64,158,255,.5) 48%, rgba(64,158,255,.5) 49%, transparent 49%, transparent 51%, rgba(64,158,255,.3) 51%, rgba(64,158,255,.3) 52%, transparent 52%),
    linear-gradient(0deg, transparent 60%, rgba(64,158,255,.4) 60%, rgba(64,158,255,.4) 60.5%, transparent 60.5%);
  mask-image: radial-gradient(ellipse at 30% 50%, black 30%, transparent 60%);
}

.back-btn {
  width: 32px; height: 32px; border-radius: 8px; border: 1px solid rgba(64,158,255,.2);
  background: rgba(64,158,255,.08); color: #8cb8ff;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; position: relative; z-index: 1;
}

/* 机器人头像 */
.robot-avatar {
  width: 44px; height: 44px; border-radius: 10px;
  background: rgba(64,158,255,.08);
  border: 1px solid rgba(64,158,255,.2);
  flex-shrink: 0; position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.robot-avatar svg { width: 40px; height: 40px; }

.panel-header-text { flex: 1; display: flex; flex-direction: column; gap: 1px; color: #d8e8ff; position: relative; z-index: 1; }
.panel-title { font-weight: 700; font-size: 1rem; letter-spacing: .04em; }
.panel-subtitle { font-size: .68rem; opacity: .7; display: flex; align-items: center; gap: 5px; font-family: 'Courier New', monospace; }
.online-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #4effa0;
  box-shadow: 0 0 10px rgba(78,255,160,.7);
  animation: dotPulse 2s ease-in-out infinite;
}
@keyframes dotPulse {
  0%, 100% { box-shadow: 0 0 6px rgba(78,255,160,.5); }
  50% { box-shadow: 0 0 14px rgba(78,255,160,1); }
}
.panel-close {
  background: rgba(64,158,255,.08); border: 1px solid rgba(64,158,255,.15); color: #8cb8ff;
  width: 30px; height: 30px; border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s; flex-shrink: 0; position: relative; z-index: 1;
}
.panel-close:hover { background: rgba(64,158,255,.2); color: #fff; transform: rotate(90deg); }

/* ===== 消息区 ===== */
.panel-body {
  flex: 1; overflow-y: auto;
  padding: 20px 16px;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(64,158,255,.04) 0%, transparent 50%),
    radial-gradient(ellipse at 100% 100%, rgba(64,158,255,.03) 0%, transparent 40%),
    #0c1a2d;
  display: flex; flex-direction: column; gap: 16px;
  -webkit-overflow-scrolling: touch;
}
.panel-body::-webkit-scrollbar { width: 3px; }
.panel-body::-webkit-scrollbar-thumb { background: rgba(64,158,255,.2); border-radius: 2px; }
.panel-body::-webkit-scrollbar-track { background: transparent; }

.msg-row { display: flex; align-items: flex-end; gap: 8px; }
.msg-row.user { justify-content: flex-end; }

.msg-avatar {
  width: 30px; height: 30px; border-radius: 8px;
  background: rgba(64,158,255,.06);
  border: 1px solid rgba(64,158,255,.12);
  flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.msg-avatar svg { width: 26px; height: 26px; }

.msg-bubble { max-width: 78%; padding: 12px 16px; border-radius: 14px; position: relative; word-break: break-word; }
.msg-bubble.user {
  background: linear-gradient(135deg, #409eff, #2d6cb4);
  color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 16px rgba(64,158,255,.3);
}
.msg-bubble.xin {
  background: #132437;
  color: #c8d8f0;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(64,158,255,.1);
}
.msg-text { font-size: .95rem; line-height: 1.7; display: inline; }
.msg-bubble.xin .msg-text { font-size: .95rem; }
.msg-cursor { display: inline; color: #409eff; font-weight: 700; animation: blink .8s step-end infinite; }
@keyframes blink { 50% { opacity: 0 } }
.msg-time {
  font-size: .6rem; opacity: .3; display: block; margin-top: 5px;
  font-family: 'Courier New', monospace;
}
.msg-row.user .msg-time { text-align: right; }
.msg-row.xin .msg-time { text-align: left; }

/* 跳转链接按钮 */
.msg-links { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.msg-link-btn {
  padding: 6px 14px; border-radius: 8px;
  border: 1px solid rgba(64,158,255,.3);
  background: rgba(64,158,255,.08); color: #409eff;
  font-size: .78rem; cursor: pointer; font-family: inherit;
  transition: all .2s;
}
.msg-link-btn:hover {
  background: rgba(64,158,255,.18);
  border-color: #409eff;
  box-shadow: 0 0 12px rgba(64,158,255,.15);
}

/* 正在输入 */
.typing-bubble { display: flex; align-items: center; gap: 5px; padding: 16px 18px; }
.typing-dot {
  width: 7px; height: 7px; border-radius: 50%; background: rgba(64,158,255,.5);
  animation: dotBounce 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: .2s; }
.typing-dot:nth-child(3) { animation-delay: .4s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: .4; }
  40% { transform: translateY(-7px); opacity: 1; }
}

/* ===== 数据流装饰条 ===== */
.data-stream {
  display: flex; gap: 3px; padding: 0 18px; height: 2px;
}
.data-block {
  flex: 1; height: 100%; background: rgba(64,158,255,.15); border-radius: 1px;
  animation: dataPulse 2s ease-in-out infinite;
}
@keyframes dataPulse {
  0%, 100% { background: rgba(64,158,255,.1); }
  50% { background: rgba(64,158,255,.4); }
}

/* ===== 快捷标签 ===== */
.quick-tags {
  display: flex; gap: 6px; padding: 10px 16px;
  overflow-x: auto; flex-shrink: 0;
}
.quick-tag {
  flex-shrink: 0; padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid rgba(64,158,255,.15);
  background: rgba(64,158,255,.04); color: #7aa8e0; font-size: .74rem;
  cursor: pointer; white-space: nowrap;
  transition: all .2s; font-family: inherit;
}
.quick-tag:hover {
  border-color: #409eff; color: #409eff;
  background: rgba(64,158,255,.1);
  box-shadow: 0 0 12px rgba(64,158,255,.15);
}

/* ===== 输入区 ===== */
.panel-footer { padding: 10px 16px 14px; flex-shrink: 0; }
.input-box {
  display: flex; align-items: flex-end; gap: 10px;
  background: #132437; border-radius: 12px;
  padding: 5px 6px 5px 16px;
  border: 1px solid rgba(64,158,255,.12);
  transition: border-color .25s, box-shadow .25s;
}
.input-box:focus-within {
  border-color: #409eff;
  box-shadow: 0 0 0 4px rgba(64,158,255,.06), 0 0 20px rgba(64,158,255,.08);
}
.chat-input {
  flex: 1; border: none; background: transparent; resize: none;
  font-size: .88rem; line-height: 1.45; outline: none;
  max-height: 90px; font-family: inherit; color: #d8e8ff;
  padding: 7px 0;
}
.chat-input::placeholder { color: #3a5080; }
.send-btn {
  width: 38px; height: 38px; border-radius: 10px; border: none;
  background: #409eff; color: #fff;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all .2s;
  box-shadow: 0 0 16px rgba(64,158,255,.3);
}
.send-btn:disabled { opacity: .25; box-shadow: none; cursor: default; }
.send-btn:not(:disabled):hover { background: #5aaeff; box-shadow: 0 0 24px rgba(64,158,255,.5); transform: scale(1.05); }
.send-btn:not(:disabled):active { transform: scale(.94); }
</style>
