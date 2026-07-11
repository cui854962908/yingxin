/**
 * authFetch —— 自动刷新 access token 的 fetch 包装。
 *
 * 用法：替代全局 fetch，对所有需要认证的 API 自动处理 token 过期。
 *    import { authFetch } from '../composables/useAuthFetch'
 *    const res = await authFetch('/api/forum/posts', { method: 'POST', body: ... })
 *
 * 行为：
 *  1. 用内存中的 access token 发起请求
 *  2. 若返回 401，尝试用 localStorage 中的 refresh token 换取新 token
 *  3. 刷新成功后重放原请求，用户无感
 *  4. 刷新失败则清除登录状态并跳转到登录页
 */

type AuthFetchOptions = RequestInit & { _retried?: boolean }

let _accessToken: string | null = null
let _refreshPromise: Promise<boolean> | null = null
let _onForceLogout: (() => void) | null = null

/** 设置内存中的 access token */
export function setAccessToken(token: string | null): void {
  _accessToken = token
}

/** 获取当前 access token */
export function getAccessToken(): string | null {
  return _accessToken
}

/** 注册强制登出回调（由 App.vue 提供） */
export function onForceLogout(fn: () => void): void {
  _onForceLogout = fn
}

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (_accessToken) {
    headers['Authorization'] = `Bearer ${_accessToken}`
  }
  return headers
}

async function tryRefresh(): Promise<boolean> {
  // 防止并发刷新
  if (_refreshPromise) return _refreshPromise

  _refreshPromise = (async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) return false

      const res = await fetch('/api/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      const d = await res.json()
      if (!d.success) return false

      _accessToken = d.data.access_token
      localStorage.setItem('refresh_token', d.data.refresh_token)
      return true
    } catch {
      return false
    } finally {
      _refreshPromise = null
    }
  })()

  return _refreshPromise
}

function forceLogout(): void {
  _accessToken = null
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('student')
  if (_onForceLogout) {
    _onForceLogout()
  }
}

export async function authFetch(url: string, options: AuthFetchOptions = {}): Promise<Response> {
  const { _retried, ...fetchOpts } = options
  const res = await fetch(url, {
    ...fetchOpts,
    headers: {
      ...authHeaders(),
      ...(options.headers || {}),
    },
  })

  if (res.status === 401 && !_retried) {
    const refreshed = await tryRefresh()
    if (refreshed) {
      // 重放原始请求（传入 _retried 标记防止无限循环）
      return authFetch(url, { ...fetchOpts, _retried: true })
    }
    // 刷新失败，强制登出
    forceLogout()
  }

  return res
}
