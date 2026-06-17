import { MOBILE_MAX, MOBILE_BOTTOM_NAV_H } from './useBreakpoint'

let safeBottomCache: number | null = null

/** 真机可视宽度（优先 visualViewport，避免地址栏/滚动条偏差） */
export function viewportWidth(): number {
  return window.visualViewport?.width ?? window.innerWidth
}

/** 真机可视高度（优先 visualViewport，避免 iOS 地址栏压缩） */
export function viewportHeight(): number {
  return window.visualViewport?.height ?? window.innerHeight
}

export function resetSafeAreaCache() {
  safeBottomCache = null
}

/** 读取 iPhone 底部安全区（DevTools 模拟常为 0，真机有值） */
export function readSafeAreaBottom(): number {
  if (safeBottomCache !== null) return safeBottomCache
  if (typeof document === 'undefined' || !document.body) return 0
  const el = document.createElement('div')
  el.style.cssText = 'position:fixed;visibility:hidden;padding-bottom:env(safe-area-inset-bottom,0px)'
  document.body.appendChild(el)
  safeBottomCache = parseFloat(getComputedStyle(el).paddingBottom) || 0
  el.remove()
  return safeBottomCache
}

/** 移动端底栏 + 安全区预留（供悬浮球 clamp 等） */
export function bottomChromeReserve(): number {
  if (viewportWidth() > MOBILE_MAX) return 10
  return MOBILE_BOTTOM_NAV_H + readSafeAreaBottom() + 12
}

export function onViewportChange(cb: () => void) {
  window.addEventListener('resize', cb)
  window.addEventListener('orientationchange', () => {
    resetSafeAreaCache()
    cb()
  })
  window.visualViewport?.addEventListener('resize', cb)
  window.visualViewport?.addEventListener('scroll', cb)
}

export function offViewportChange(cb: () => void) {
  window.removeEventListener('resize', cb)
  window.visualViewport?.removeEventListener('resize', cb)
  window.visualViewport?.removeEventListener('scroll', cb)
}
