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
  <aside v-if="open" class="route-origin-prompt" role="dialog" aria-label="设置路线起点">
    <button class="route-origin-prompt__close" type="button" aria-label="关闭" @click="$emit('cancel')">×</button>
    <strong>先设置路线起点</strong>
    <p>{{ message }}</p>
    <div class="route-origin-prompt__actions">
      <button v-if="dormLabel" class="primary" type="button" @click="$emit('dorm')">
        <span>◎</span> {{ dormLabel }}
      </button>
      <button type="button" :disabled="locating" @click="$emit('device')">
        <span>⊙</span> {{ locating ? '定位中…' : '定位当前位置' }}
      </button>
      <button type="button" @click="$emit('map')"><span>⌖</span> 手动选择当前位置</button>
    </div>
    <small>宿舍与地图选点为校内导览坐标，不等同于实时 GPS。设好起点后，再点目的地「我要去这」即可规划路线。</small>
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
