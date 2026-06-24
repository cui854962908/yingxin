import { useRouter, type RouteLocationRaw } from 'vue-router'
import { useBreakpoint } from './useBreakpoint'

/** 底栏/侧栏主模块根路径：移动端切换时用 replace，避免系统返回键逐页回溯 */
const SHELL_ROUTES = ['/', '/faq', '/wall', '/clubs', '/announcements', '/intro/wiki', '/intro/colleges', '/intro/clubs'] as const

/** 全屏/独立子页：系统返回时也应先回首页 */
const STANDALONE_MOBILE_BACK_ROUTES = ['/campus', '/campus/2d', '/campus/3d', '/guide', '/tips'] as const

export function isShellRoute(path: string): boolean {
  const p = (path.split('?')[0].replace(/\/$/, '') || '/')
  if (p === '/') return true
  return SHELL_ROUTES.slice(1).some((base) => p === base)
}

/** 移动端：在此类页按系统返回 → 先回首页（子路径如 /clubs/1 不在此列） */
export function shouldMobileBackToHome(path: string): boolean {
  const p = path.split('?')[0]
  if (p === '/') return false
  if (isShellRoute(p)) return true
  return STANDALONE_MOBILE_BACK_ROUTES.some((r) => p === r)
}

function routePath(to: string | RouteLocationRaw): string {
  return typeof to === 'string' ? to.split('?')[0] : (to.path ?? '/')
}

export function useAppNavigate() {
  const router = useRouter()
  const { isMobile } = useBreakpoint()

  function appNavigate(to: string | RouteLocationRaw) {
    if (isMobile.value && isShellRoute(routePath(to))) {
      return router.replace(to)
    }
    return router.push(to)
  }

  /** 从子页回到模块根：移动端 replace，桌面端走浏览器后退 */
  function appGoBackTo(to: string | RouteLocationRaw) {
    if (isMobile.value && isShellRoute(routePath(to))) {
      return router.replace(to)
    }
    return router.back()
  }

  return { appNavigate, appGoBackTo, isShellRoute }
}
