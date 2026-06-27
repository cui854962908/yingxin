import { describe, it, expect } from 'vitest'
import { isShellRoute, shouldMobileBackToHome } from '../useAppNavigate'

describe('isShellRoute', () => {
  it('识别主模块根路径', () => {
    expect(isShellRoute('/')).toBe(true)
    expect(isShellRoute('/faq')).toBe(true)
    expect(isShellRoute('/intro/wiki')).toBe(true)
    expect(isShellRoute('/intro/clubs')).toBe(true)
    expect(isShellRoute('/announcements')).toBe(true)
  })

  it('子路径不算 shell', () => {
    expect(isShellRoute('/clubs/add')).toBe(false)
    expect(isShellRoute('/clubs/abc')).toBe(false)
    expect(isShellRoute('/intro/colleges')).toBe(true)
    expect(isShellRoute('/intro/sie')).toBe(true)
    expect(isShellRoute('/guide')).toBe(false)
    expect(isShellRoute('/campus')).toBe(false)
    expect(isShellRoute('/announcements/add')).toBe(false)
  })
})

describe('shouldMobileBackToHome', () => {
  it('主模块与独立页需要先回首页', () => {
    expect(shouldMobileBackToHome('/faq')).toBe(true)
    expect(shouldMobileBackToHome('/intro/wiki')).toBe(true)
    expect(shouldMobileBackToHome('/intro/colleges')).toBe(true)
    expect(shouldMobileBackToHome('/intro/sie')).toBe(true)
    expect(shouldMobileBackToHome('/campus')).toBe(true)
    expect(shouldMobileBackToHome('/campus/2d')).toBe(true)
    expect(shouldMobileBackToHome('/campus/3d')).toBe(true)
    expect(shouldMobileBackToHome('/guide')).toBe(true)
  })

  it('首页与 drill-down 子页不在此列', () => {
    expect(shouldMobileBackToHome('/')).toBe(false)
    expect(shouldMobileBackToHome('/clubs/abc')).toBe(false)
    expect(shouldMobileBackToHome('/announcements/add')).toBe(false)
  })
})
