<script setup lang="ts">
import XinAvatar from './XinAvatar.vue'

export interface Msg {
  role: 'user' | 'xin'
  text: string
  time: string
  displayText: string
  done: boolean
  links?: { label: string; to: string }[]
}

const props = defineProps<{
  msg: Msg
}>()

const emit = defineEmits<{
  speak: [text: string]
  navigate: [to: string]
}>()
</script>

<template>
  <div :class="['msg-row', props.msg.role]">
    <div v-if="props.msg.role === 'xin'" class="msg-avatar">
      <XinAvatar :size="26" />
    </div>
    <div :class="['msg-bubble', props.msg.role]">
      <span
        class="msg-text"
        v-html="(props.msg.role === 'xin' ? (props.msg.displayText || '') : props.msg.text).replace(/\n/g, '<br>')"
      />
      <span v-if="props.msg.role === 'xin' && !props.msg.done" class="msg-cursor">|</span>
      <span class="msg-time">{{ props.msg.time }}</span>
      <div v-if="props.msg.role === 'xin' && props.msg.links && props.msg.links.length > 0 && props.msg.done" class="msg-links">
        <button v-for="(l, li) in props.msg.links" :key="li" class="msg-link-btn" @click="emit('navigate', l.to)">{{ l.label }}</button>
      </div>
    </div>
    <button
      v-if="props.msg.role === 'xin' && props.msg.done"
      class="msg-speak-btn" @click.stop="emit('speak', props.msg.text)" title="朗读"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 8.5v7a4.5 4.5 0 0 0 2.5-3.5z"/></svg>
    </button>
  </div>
</template>

<style scoped>
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

.msg-speak-btn {
  display: flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: 50%; border: none;
  background: transparent; color: rgba(64,158,255,.15);
  cursor: pointer; flex-shrink: 0; align-self: flex-end; margin-bottom: 2px;
  transition: all .15s;
}
.msg-speak-btn:hover { background: rgba(64,158,255,.1); color: #409eff; }

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
</style>
