<script setup lang="ts">
defineProps<{
  open: boolean
  message: string
  dormLabel: string | null
  locating: boolean
}>()

defineEmits<{
  dorm: []
  device: []
  map: []
  cancel: []
}>()
</script>

<template>
  <aside v-if="open" class="route-origin-prompt" role="dialog" aria-label="选择路线起点">
    <button class="route-origin-prompt__close" type="button" aria-label="关闭起点选择" @click="$emit('cancel')">×</button>
    <strong>选择路线起点</strong>
    <p>{{ message }}</p>
    <div class="route-origin-prompt__actions">
      <button v-if="dormLabel" class="primary" type="button" @click="$emit('dorm')">
        <span>◎</span> {{ dormLabel }}
      </button>
      <button type="button" :disabled="locating" @click="$emit('device')">
        <span>⊙</span> {{ locating ? '定位中…' : '设备定位' }}
      </button>
      <button type="button" @click="$emit('map')"><span>⌖</span> 从地图选择</button>
    </div>
    <small>宿舍和地图选点是校内导览起点，不代表实时 GPS 位置。</small>
  </aside>
</template>

<style scoped>
.route-origin-prompt {
  position: absolute;
  z-index: 32;
  top: 50%;
  left: 50%;
  width: min(380px, calc(100% - 40px));
  padding: 20px;
  transform: translate(-50%, -50%);
  border: 1px solid #ead7d8;
  border-radius: 12px;
  background: rgba(255, 255, 255, .98);
  box-shadow: 0 18px 48px rgba(56, 31, 33, .2);
  color: #302b2c;
}

.route-origin-prompt strong { color: var(--brand-red); font-size: 17px; }
.route-origin-prompt p { margin: 9px 28px 15px 0; color: #6c6264; font-size: 13px; line-height: 1.6; }
.route-origin-prompt small { display: block; margin-top: 12px; color: #948a8c; font-size: 11px; line-height: 1.5; }
.route-origin-prompt__actions { display: grid; gap: 8px; }

.route-origin-prompt__actions button {
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid #dfd7d8;
  border-radius: 8px;
  background: #fff;
  color: #51484a;
  font: inherit;
  font-size: 13px;
  font-weight: 650;
  text-align: left;
  cursor: pointer;
}

.route-origin-prompt__actions button:hover { border-color: var(--brand-red); color: var(--brand-red); }
.route-origin-prompt__actions button.primary { border-color: var(--brand-red); background: var(--brand-red); color: #fff; }
.route-origin-prompt__actions button:disabled { opacity: .6; cursor: wait; }

.route-origin-prompt__close {
  position: absolute;
  top: 10px;
  right: 12px;
  border: 0;
  background: transparent;
  color: #8b8183;
  font-size: 22px;
  cursor: pointer;
}
</style>
