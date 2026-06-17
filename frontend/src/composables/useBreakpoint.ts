import { ref, onMounted, onUnmounted } from 'vue'
import { viewportWidth, onViewportChange, offViewportChange } from './useViewport'

/** 与全局 CSS @media (max-width: 768px) 保持一致 */
export const MOBILE_MAX = 768
export const NARROW_MAX = 480

/** 移动端底栏高度（与 MobileBottomNav 一致，不含 safe-area） */
export const MOBILE_BOTTOM_NAV_H = 56

function readWidth() {
  return viewportWidth()
}

export function useBreakpoint() {
  const width = ref(readWidth())
  const isMobile = ref(width.value <= MOBILE_MAX)
  const isNarrow = ref(width.value <= NARROW_MAX)

  function sync() {
    width.value = readWidth()
    isMobile.value = width.value <= MOBILE_MAX
    isNarrow.value = width.value <= NARROW_MAX
  }

  onMounted(() => {
    sync()
    onViewportChange(sync)
  })

  onUnmounted(() => {
    offViewportChange(sync)
  })

  return { width, isMobile, isNarrow }
}
