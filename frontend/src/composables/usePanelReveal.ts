import { onMounted, ref } from 'vue'
import { MOBILE_MAX } from './useBreakpoint'

/** 等 DOM 稳定后再触发 panel-reveal；移动端 Tab 切换直出，不等待 */
export function usePanelReveal() {
  const ready = ref(typeof window !== 'undefined' && window.innerWidth > MOBILE_MAX)

  onMounted(() => {
    if (window.innerWidth <= MOBILE_MAX) {
      ready.value = true
      return
    }
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        ready.value = true
      })
    })
  })

  return { ready }
}
