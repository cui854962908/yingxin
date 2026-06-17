import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import { MOBILE_MAX, useBreakpoint } from './useBreakpoint'
import {
  viewportWidth, viewportHeight, bottomChromeReserve,
  onViewportChange, offViewportChange,
} from './useViewport'

/** 与 XiaoXinAssistant.vue 中 .xin-character 尺寸一致 */
const BUBBLE_SIZE = { mobile: 96, desktop: 180 } as const

function dragThreshold() {
  return viewportWidth() <= MOBILE_MAX ? 12 : 6
}

export function useDrag(open: Ref<boolean>, onOpen: () => void) {
  const lottieRef = ref<HTMLElement | null>(null)
  const { isMobile } = useBreakpoint()

  function bubblePad() {
    return viewportWidth() <= MOBILE_MAX ? BUBBLE_SIZE.mobile + 14 : BUBBLE_SIZE.desktop + 10
  }

  function clampX(v: number) {
    return Math.max(10, Math.min(viewportWidth() - bubblePad(), v))
  }

  function clampY(v: number) {
    return Math.max(10, Math.min(viewportHeight() - bubblePad() - bottomChromeReserve(), v))
  }

  const initPad = viewportWidth() <= MOBILE_MAX ? BUBBLE_SIZE.mobile + 24 : BUBBLE_SIZE.desktop + 40
  const x = ref(clampX(viewportWidth() - initPad))
  const y = ref(clampY(viewportHeight() - initPad - (viewportWidth() <= MOBILE_MAX ? 20 : 0)))
  const dragging = ref(false)
  const dragStart = ref({ x: 0, y: 0, bx: 0, by: 0 })
  let dragMoved = false
  let captureEl: HTMLElement | null = null
  let activePointerId: number | null = null

  function reclampPosition() {
    x.value = clampX(x.value)
    y.value = clampY(y.value)
  }

  function finishPointer(e: PointerEvent) {
    if (captureEl?.hasPointerCapture?.(e.pointerId)) {
      captureEl.releasePointerCapture(e.pointerId)
    }
    captureEl = null
    activePointerId = null
    dragging.value = false
  }

  function onPointerDown(e: PointerEvent) {
    if (e.pointerType === 'mouse' && e.button !== 0) return
    e.preventDefault()
    dragging.value = true
    dragMoved = false
    activePointerId = e.pointerId
    dragStart.value = { x: e.clientX, y: e.clientY, bx: x.value, by: y.value }
    captureEl = e.currentTarget as HTMLElement
    captureEl.setPointerCapture(e.pointerId)
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging.value || e.pointerId !== activePointerId) return
    const dx = e.clientX - dragStart.value.x
    const dy = e.clientY - dragStart.value.y
    if (Math.abs(dx) > dragThreshold() || Math.abs(dy) > dragThreshold()) {
      dragMoved = true
    }
    if (!dragMoved) return
    x.value = clampX(dragStart.value.bx + dx)
    y.value = clampY(dragStart.value.by + dy)
  }

  function onPointerUp(e: PointerEvent) {
    if (!dragging.value || e.pointerId !== activePointerId) return
    const wasTap = !dragMoved
    finishPointer(e)
    if (wasTap) {
      open.value = true
      onOpen()
    }
  }

  function onPointerCancel(e: PointerEvent) {
    if (!dragging.value || e.pointerId !== activePointerId) return
    finishPointer(e)
  }

  onMounted(() => {
    reclampPosition()
    onViewportChange(reclampPosition)
    document.addEventListener('pointermove', onPointerMove, { passive: false })
    document.addEventListener('pointerup', onPointerUp)
    document.addEventListener('pointercancel', onPointerCancel)
  })

  onUnmounted(() => {
    offViewportChange(reclampPosition)
    document.removeEventListener('pointermove', onPointerMove)
    document.removeEventListener('pointerup', onPointerUp)
    document.removeEventListener('pointercancel', onPointerCancel)
  })

  return {
    lottieRef, x, y, dragging, isMobile,
    onPointerDown, reclampPosition,
  }
}
