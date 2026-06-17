<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  activityPhotos: string[]
  editing: boolean
}>()

const emit = defineEmits<{
  'upload-photo': [e: Event]
  'remove-photo': [index: number]
}>()

const lightboxOpen = ref(false)
const lightboxIndex = ref(0)

function openLightbox(idx: number) { lightboxIndex.value = idx; lightboxOpen.value = true }
function closeLightbox() { lightboxOpen.value = false }
function prevPhoto() { lightboxIndex.value = (lightboxIndex.value - 1 + props.activityPhotos.length) % props.activityPhotos.length }
function nextPhoto() { lightboxIndex.value = (lightboxIndex.value + 1) % props.activityPhotos.length }

function onLightboxKey(e: KeyboardEvent) {
  if (!lightboxOpen.value) return
  if (e.key === 'Escape') closeLightbox()
  if (e.key === 'ArrowLeft') prevPhoto()
  if (e.key === 'ArrowRight') nextPhoto()
}

onMounted(() => document.addEventListener('keyup', onLightboxKey))
onUnmounted(() => document.removeEventListener('keyup', onLightboxKey))
</script>

<template>
  <!-- 风采展示 -->
  <div class="cd-section">
    <h3 class="cd-section-title">
      <span class="cd-section-icon-wrap"><span class="cd-section-icon-inner">
        <svg width="20" height="20" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm0,16V158.75l-26.07-26.06a16,16,0,0,0-22.63,0l-20,20-44-44a16,16,0,0,0-22.62,0L40,149.37V56ZM40,172l52-52,80,80H40Zm176,28H194.63l-36-36,20-20L216,181.38V200ZM144,100a12,12,0,1,1,12,12A12,12,0,0,1,144,100Z"/></svg>
      </span></span>
      <span class="cd-section-bar" style="background: var(--tc)" />
      风采展示
    </h3>

    <!-- 空状态（仅查看模式 & 无照片） -->
    <div v-if="!editing && activityPhotos.length === 0" class="cd-photos-empty">
      <svg width="48" height="48" viewBox="0 0 256 256" fill="none" stroke="#c4b8a4" stroke-width="1.5" class="cd-photos-empty-icon">
        <rect x="32" y="48" width="192" height="160" rx="8" stroke="currentColor" fill="none"/>
        <circle cx="92" cy="108" r="12" fill="#c4b8a4" stroke="none"/>
        <path d="M32 176l56-56 32 32 48-48 56 56" stroke="currentColor" fill="none"/>
        <circle cx="184" cy="92" r="8" fill="#c4b8a4" stroke="none"/>
      </svg>
      <p class="cd-photos-empty-text">还没有添加照片</p>
      <p class="cd-photos-empty-hint">等待上传风采照片…</p>
    </div>

    <!-- 照片墙（查看/编辑共用） -->
    <div v-if="activityPhotos.length > 0 || editing" class="cd-photos-wall">
      <div
        v-for="(src, i) in activityPhotos" :key="i"
        class="cd-photo-card"
        :class="{ 'is-editing': editing }"
        @click="!editing && openLightbox(i)"
      >
        <img :src="src" class="cd-photo-card-img"
          @error="($event.target as HTMLImageElement).style.display='none'" />
        <button v-if="editing" class="cd-photo-card-del" @click.stop="emit('remove-photo', i)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <!-- 添加卡片：跟在上传的最后一张后面，融入网格 -->
      <label v-if="editing && activityPhotos.length < 10" class="cd-photo-card cd-photo-card-add">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#b0a090" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        <span class="cd-photo-card-add-text">添加照片</span>
        <input type="file" accept="image/*" @change="emit('upload-photo', $event)" />
      </label>
    </div>
    <p v-if="editing && activityPhotos.length >= 10" class="cd-photo-max-hint">已达上限，最多 10 张</p>
  </div>

  <!-- 灯箱 -->
  <Transition name="lightbox">
    <div v-if="lightboxOpen" class="cd-lightbox" @click="closeLightbox">
      <button class="cd-lightbox-close" @click="closeLightbox">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
      <button v-if="activityPhotos.length > 1" class="cd-lightbox-prev" @click.stop="prevPhoto">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <img :src="activityPhotos[lightboxIndex]" class="cd-lightbox-img" @click.stop
        @error="($event.target as HTMLImageElement).style.display='none'" />
      <button v-if="activityPhotos.length > 1" class="cd-lightbox-next" @click.stop="nextPhoto">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M9 18l6-6-6-6"/></svg>
      </button>
      <span class="cd-lightbox-counter">{{ lightboxIndex + 1 }} / {{ activityPhotos.length }}</span>
    </div>
  </Transition>
</template>

<style scoped>
.cd-section { margin-bottom: 20px; background: linear-gradient(90deg, #FFF8F4 0%, #FDEDE8 100%); border-radius: 16px; padding: 24px 28px; box-shadow: none }
.cd-section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: #333; margin: 0 0 16px; letter-spacing: .04em }
.cd-section-icon-wrap { width: 32px; height: 32px; border-radius: 8px; flex-shrink: 0; background: #fdf5ec; display: flex; align-items: center; justify-content: center }
.cd-section-icon-inner { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center }
.cd-section-icon { color: #E26A6A; flex-shrink: 0 }
.cd-section-bar { width: 4px; height: 18px; border-radius: 2px; flex-shrink: 0 }

.cd-photos-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 16px; gap: 8px }
.cd-photos-empty-icon { opacity: .5 }
.cd-photos-empty-text { margin: 0; font-size: .92rem; color: #b0a090; font-weight: 500 }
.cd-photos-empty-hint { margin: 0; font-size: .78rem; color: #c4b8a4 }

/* 照片墙 */
.cd-photos-wall {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: 200px;
  gap: 14px;
}
.cd-photo-card {
  position: relative; overflow: hidden; cursor: pointer;
  background: #fff; border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,.1), 0 1px 2px rgba(0,0,0,.06);
  transition: transform .25s, box-shadow .25s, z-index 0s;
}
.cd-photo-card:hover {
  transform: scale(1.03) rotate(0deg) !important;
  box-shadow: 0 8px 28px rgba(0,0,0,.16), 0 2px 6px rgba(0,0,0,.1);
  z-index: 2;
}
.cd-photo-card-img { width: 100%; height: 100%; object-fit: cover; display: block }

/* 大小不一：利用 nth-child 分配不同跨列/跨行（排除添加卡片） */
.cd-photo-card:not(.cd-photo-card-add):nth-child(1) { grid-column: span 2; grid-row: span 2; }
.cd-photo-card:not(.cd-photo-card-add):nth-child(4) { grid-row: span 2; }
.cd-photo-card:not(.cd-photo-card-add):nth-child(7) { grid-column: span 2; }

/* 微旋转模仿贴墙感（排除添加卡片和编辑模式） */
.cd-photo-card:not(.cd-photo-card-add):not(.is-editing):nth-child(2n) { transform: rotate(.6deg) }
.cd-photo-card:not(.cd-photo-card-add):not(.is-editing):nth-child(3n) { transform: rotate(-.5deg) }
.cd-photo-card:not(.cd-photo-card-add):not(.is-editing):nth-child(5n+1) { transform: rotate(.35deg) }

.cd-photo-max-hint { text-align: center; color: #b0a090; font-size: .82rem; margin: 8px 0 0 }

/* 编辑模式：删除按钮 */
.cd-photo-card.is-editing:hover { transform: scale(1.03) rotate(0deg) !important }
.cd-photo-card-del {
  position: absolute; top: 6px; right: 6px; z-index: 3;
  width: 26px; height: 26px; border-radius: 50%; border: none;
  background: rgba(0,0,0,.55); color: #fff;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity .2s;
}
.cd-photo-card.is-editing:hover .cd-photo-card-del { opacity: 1 }
.cd-photo-card-del:hover { background: #E26A6A }

/* 添加卡片：融入网格的虚线占位 */
.cd-photo-card-add {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 6px; cursor: pointer;
  border: 2px dashed #d5c9b3; background: rgba(255,255,255,.5);
  box-shadow: none; transform: none !important;
  transition: border-color .2s, background .2s;
}
.cd-photo-card-add:hover {
  border-color: #4a8c5c; background: rgba(255,255,255,.8);
  transform: none !important; box-shadow: none;
}
.cd-photo-card-add-text { font-size: .82rem; color: #b0a090; font-weight: 500 }
.cd-photo-card-add input { position: absolute; inset: 0; opacity: 0; cursor: pointer }

/* 灯箱 */
.cd-lightbox { position: fixed; inset: 0; z-index: 2000; background: rgba(0,0,0,.92); display: flex; align-items: center; justify-content: center }
.cd-lightbox-img { max-width: 85vw; max-height: 85vh; object-fit: contain; border-radius: 4px }
.cd-lightbox-close { position: absolute; top: 20px; right: 20px; z-index: 1; background: rgba(255,255,255,.1); border: none; color: #fff; cursor: pointer; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background .2s }
.cd-lightbox-close:hover { background: rgba(255,255,255,.2) }
.cd-lightbox-prev, .cd-lightbox-next { position: absolute; top: 50%; transform: translateY(-50%); z-index: 1; background: rgba(255,255,255,.1); border: none; color: #fff; cursor: pointer; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background .2s }
.cd-lightbox-prev:hover, .cd-lightbox-next:hover { background: rgba(255,255,255,.2) }
.cd-lightbox-prev { left: 20px }
.cd-lightbox-next { right: 20px }
.cd-lightbox-counter { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); color: rgba(255,255,255,.6); font-size: .82rem }
.lightbox-enter-active { animation: lbIn .2s ease-out }
.lightbox-leave-active { animation: lbOut .15s ease-in }
@keyframes lbIn { from{opacity:0} to{opacity:1} }
@keyframes lbOut { to{opacity:0} }

@media(max-width: 768px) {
  .cd-section { padding: 18px 16px; border-radius: 12px }
  .cd-photos-wall { grid-template-columns: repeat(2, 1fr); grid-auto-rows: 170px; gap: 10px }
  .cd-photo-card:not(.cd-photo-card-add):nth-child(1) { grid-column: span 2; grid-row: span 2 }
  .cd-photo-card:not(.cd-photo-card-add):nth-child(7) { grid-column: span 1 }
  .cd-photo-card-add { font-size: .76rem }
}
@media(max-width: 480px) {
  .cd-section { padding: 14px 12px; border-radius: 10px; margin-bottom: 14px }
  .cd-section-title { font-size: .88rem; gap: 6px; margin-bottom: 10px }
  .cd-photos-wall { grid-template-columns: 1fr 1fr; grid-auto-rows: 150px; gap: 8px }
  .cd-photo-card:not(.cd-photo-card-add):nth-child(1) { grid-column: span 2 }
  .cd-photo-card-add { font-size: .72rem }
}
</style>
