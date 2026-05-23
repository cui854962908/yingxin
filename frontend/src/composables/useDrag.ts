import { ref, onMounted, onUnmounted, type Ref } from 'vue'

export function useDrag(open: Ref<boolean>, onOpen: () => void) {
  const lottieRef = ref<HTMLElement | null>(null)
  const x = ref(window.innerWidth - 220)
  const y = ref(window.innerHeight - 280)
  const dragging = ref(false)
  const dragStart = ref({ x: 0, y: 0, bx: 0, by: 0 })
  const isMobile = ref(false)
  let dragMoved = false

  function checkMobile() { isMobile.value = window.innerWidth < 768 }

  onMounted(() => {
    checkMobile()
    window.addEventListener('resize', checkMobile)
    document.addEventListener('pointermove', onPointerMove)
    document.addEventListener('pointerup', onPointerUp)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', checkMobile)
    document.removeEventListener('pointermove', onPointerMove)
    document.removeEventListener('pointerup', onPointerUp)
  })

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

  function onClickXin() {
    if (!dragMoved) { open.value = true; onOpen() }
  }

  return {
    lottieRef, x, y, dragging, isMobile,
    onPointerDown, onClickXin,
  }
}
