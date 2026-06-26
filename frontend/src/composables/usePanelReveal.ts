import { onMounted, ref } from 'vue'

/** 等 DOM 稳定后再触发 panel-reveal，避免被外层 Transition 吞掉 */
export function usePanelReveal() {
  const ready = ref(false)
  onMounted(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        ready.value = true
      })
    })
  })
  return { ready }
}
