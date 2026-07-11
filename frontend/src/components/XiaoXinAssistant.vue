<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, inject, computed, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { registerMobileChatOpen } from '../router/index'
import lottie, { type AnimationItem } from 'lottie-web'
import XinAvatar from './XinAvatar.vue'
import XinQuickTags from './XinQuickTags.vue'
import XinChatBubble from './XinChatBubble.vue'
import { useTTS } from '../composables/useTTS'
import { useDrag } from '../composables/useDrag'
import { useXinChat } from '../composables/useXinChat'

const { autoSpeak, isSpeaking, speak, speakSynced, enqueueSpeak, stopSpeak, toggleSpeak } = useTTS()

const route = useRoute()
const injectedOpen = inject<Ref<boolean>>('xinOpen')
const sidebarOpen = inject<Ref<boolean>>('sidebarOpen', ref(false))

const {
  open, messages, input, sending, chatBody, quickList,
  send, onKeydown, closeChat, navigateTo, ensureWelcome,
} = useXinChat(autoSpeak, { speak, speakSynced, enqueueSpeak, stopSpeak }, injectedOpen)

const { lottieRef, x, y, dragging, isMobile, onPointerDown, reclampPosition } = useDrag(
  open,
  () => { nextTick(() => ensureWelcome()) },
)

// 校园地图页 / 手机端侧边栏打开时隐藏悬浮球
const hideOnCampus = computed(() => route.path.startsWith('/campus'))
const hideBySidebar = computed(() => isMobile.value && sidebarOpen.value)
const showTypingIndicator = computed(() => sending.value && !messages.value.some(m => m.role === 'xin' && !m.done))

function onKeyup(e: KeyboardEvent) { if (e.key === 'Escape') closeChatAndStop() }

// 手机端：系统返回键先关闭聊天层，而不是逐页回退
let chatHistoryPushed = false
let suppressChatPopstate = false

function closeChatAndStop() {
  const syncHistory = chatHistoryPushed && isMobile.value
  closeChat()
  stopSpeak()
  if (syncHistory) {
    chatHistoryPushed = false
    suppressChatPopstate = true
    history.back()
  }
}

function onChatPopstate() {
  if (suppressChatPopstate) {
    suppressChatPopstate = false
    return
  }
  if (open.value && isMobile.value) {
    closeChat()
    stopSpeak()
    chatHistoryPushed = false
  }
}

// 打开聊天 → 确保欢迎语（悬浮球/服务卡片/外部触发均覆盖）
// 关闭聊天 → 手机端悬浮球回到可视区域内
watch(open, (val) => {
  if (val) {
    nextTick(() => ensureWelcome())
    if (isMobile.value && !chatHistoryPushed) {
      history.pushState({ ...(history.state ?? {}), xinChat: 1 }, '')
      chatHistoryPushed = true
    }
  } else if (isMobile.value) {
    nextTick(() => reclampPosition())
  }
})

// Lottie 悬浮形象（移动端/桌面统一；文件缺失时保留光晕轨道）
const lottieReady = ref(false)
let anim: AnimationItem | null = null
onMounted(async () => {
  if (lottieRef.value) {
    try {
      const res = await fetch('/animation/Live chatbot.json', { method: 'HEAD' })
      if (res.ok) {
        anim = lottie.loadAnimation({
          container: lottieRef.value, renderer: 'svg', loop: true, autoplay: true,
          path: '/animation/Live chatbot.json',
        })
        lottieReady.value = true
      }
    } catch {
      /* 无 Lottie 资源时由 CSS 光晕 + 轨道环展示 */
    }
  }
  document.addEventListener('keyup', onKeyup)
  window.addEventListener('popstate', onChatPopstate)
  registerMobileChatOpen(() => open.value)
})
onUnmounted(() => {
  anim?.destroy()
  document.removeEventListener('keyup', onKeyup)
  window.removeEventListener('popstate', onChatPopstate)
  registerMobileChatOpen(() => false)
})
</script>

<template>
  <!-- Teleport 到 body：避免 App 过渡 transform 导致 iOS 上 fixed 定位失效 -->
  <Teleport to="body">
    <div
      class="xin-character"
      :style="{ left: x + 'px', top: y + 'px' }"
      :class="{ 'xin-character--hide': hideOnCampus || (open && isMobile) || hideBySidebar, dragging }"
      @pointerdown.prevent="onPointerDown"
    >
      <div ref="lottieRef" class="xin-lottie" :class="{ 'xin-lottie--ready': lottieReady, 'xin-lottie--fallback': !lottieReady }" />
      <div class="xin-glow" />
      <div class="xin-orbit" />
      <div v-if="!lottieReady" class="xin-core" aria-hidden="true" />
    </div>

    <Transition name="overlay">
      <div v-if="open && !isMobile && !hideOnCampus" class="xin-overlay" @click="closeChatAndStop" />
    </Transition>

    <Transition :name="isMobile ? 'chat-mobile' : 'chat-desktop'">
      <div v-if="open && !hideOnCampus" :class="['xin-panel', { mobile: isMobile }]">
      <!-- 科技角标装饰 -->
      <div class="tech-corners">
        <span class="tc tl" /><span class="tc tr" /><span class="tc bl" /><span class="tc br" />
      </div>

      <!-- 头部 -->
      <div class="panel-header">
        <!-- 电路纹装饰 -->
        <div class="circuit-lines" />
        <button v-if="isMobile" class="back-btn" @click="closeChatAndStop">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <!-- 机器人头像 -->
        <div class="robot-avatar">
          <XinAvatar :size="40" :animated="true" />
        </div>
        <div class="panel-header-text">
          <span class="panel-title">小信</span>
          <span class="panel-subtitle">
            <span class="online-dot" />AI 迎新助手 · 在线
          </span>
        </div>
        <!-- 语音开关 -->
        <button class="speak-toggle" :class="{ on: autoSpeak, speaking: isSpeaking }" @click="toggleSpeak" title="语音播报开关">
          <svg v-if="autoSpeak" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 8.5v7a4.5 4.5 0 0 0 2.5-3.5zM14 3.23v2.06a7 7 0 0 1 0 13.42v2.06a9 9 0 0 0 0-17.54z"/></svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 8.5v7a4.5 4.5 0 0 0 2.5-3.5zM9 6.8v10.4L6.5 15H4V9h2.5L9 6.8z"/><line x1="23" y1="2" x2="1" y2="22" stroke="currentColor" stroke-width="2"/></svg>
        </button>
        <button v-if="!isMobile" class="panel-close" @click="closeChatAndStop">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- 消息区 -->
      <div ref="chatBody" class="panel-body">
        <XinChatBubble
          v-for="(m, i) in messages" :key="i"
          :msg="m"
          @speak="speak"
          @navigate="navigateTo"
        />
        <!-- 正在输入 -->
        <div v-if="showTypingIndicator" class="msg-row xin">
          <div class="msg-avatar">
            <XinAvatar :size="26" />
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

      <!-- 快捷标签（FAQ 排序前若干条，无数据时不展示） -->
      <XinQuickTags
        v-if="quickList.length"
        :quickList="quickList"
        @select="(t: string) => { input = t; send() }"
      />

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
  </Teleport>
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
.xin-character--hide { display: none; }
.xin-character:hover { transform: scale(1.1); filter: drop-shadow(0 0 36px rgba(64,158,255,.5)); }
.xin-character.dragging { cursor: grabbing; transform: scale(1.05); }
.xin-avatar-wrap {
  position: absolute; inset: 0; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  pointer-events: none;
}
.xin-lottie { width: 170px; height: 170px; pointer-events: none; position: relative; z-index: 2; }
.xin-lottie--fallback { opacity: 0; pointer-events: none; }
.xin-lottie--ready { opacity: 1; }
.xin-lottie :deep(svg) { width: 100% !important; height: 100% !important; }
/* 无 Lottie 时的能量核心（替代方块 SVG 头像，接近原版光球形象） */
.xin-core {
  position: absolute; z-index: 1; width: 52px; height: 52px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #b8dcff 0%, #409eff 45%, #1a5fb4 100%);
  box-shadow: 0 0 28px rgba(64,158,255,.65), 0 0 56px rgba(64,158,255,.25);
  pointer-events: none;
}
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
  overflow-x: hidden;
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
.panel-subtitle { font-size: .72rem; opacity: .75; display: flex; align-items: center; gap: 5px; }
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

/* 语音开关 */
.speak-toggle {
  background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1); color: rgba(255,255,255,.35);
  width: 30px; height: 30px; border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s; flex-shrink: 0; position: relative; z-index: 1;
}
.speak-toggle.on { color: #4effa0; border-color: rgba(78,255,160,.3); background: rgba(78,255,160,.1); }
.speak-toggle.speaking { animation: speakPulse .6s ease-in-out infinite; }
.speak-toggle:hover { background: rgba(255,255,255,.1); }
@keyframes speakPulse {
  0%, 100% { box-shadow: 0 0 0 rgba(78,255,160,0); }
  50% { box-shadow: 0 0 12px rgba(78,255,160,.4); }
}

/* ===== 消息区 ===== */
.panel-body {
  flex: 1; overflow-y: auto; overflow-x: hidden;
  padding: 20px 16px;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(64,158,255,.04) 0%, transparent 50%),
    radial-gradient(ellipse at 100% 100%, rgba(64,158,255,.03) 0%, transparent 40%),
    #0c1a2d;
  display: flex; flex-direction: column; gap: 16px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.panel-body::-webkit-scrollbar { display: none; }

.msg-row { display: flex; align-items: flex-end; gap: 8px; }
.msg-row.xin { align-items: flex-start; }
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

@media(max-width: 768px) {
  .xin-character { width: 96px; height: 96px; }
  .xin-lottie { width: 88px; height: 88px; }
  .xin-core { width: 36px; height: 36px; box-shadow: 0 0 20px rgba(64,158,255,.7), 0 0 40px rgba(64,158,255,.3); }
  .xin-glow {
    inset: -12px;
    background: radial-gradient(circle, rgba(64,158,255,.42) 0%, rgba(64,158,255,.12) 55%, transparent 72%);
  }
  .xin-orbit { inset: -6px; border-width: 2px; border-color: rgba(64,158,255,.45); }
  .xin-panel.mobile { height: 100dvh; height: calc(var(--vh, 1vh) * 100); }
  .xin-panel.mobile .panel-header {
    padding-top: calc(14px + env(safe-area-inset-top, 0px));
  }
  .xin-panel.mobile .panel-footer {
    padding-bottom: calc(14px + env(safe-area-inset-bottom, 0px));
  }
  .chat-input { font-size: 16px; }
  .online-dot { animation: none }
  .speak-toggle.speaking { animation: none }
  .xin-overlay { backdrop-filter: none; background: rgba(5,12,30,.65) }
  .data-stream { display: none }
  /* 用静态发光代替动画 */
  .xin-character { filter: drop-shadow(0 0 16px rgba(64,158,255,.2)) }
}
</style>
