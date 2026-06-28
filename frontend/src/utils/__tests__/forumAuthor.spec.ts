import { describe, it, expect } from 'vitest'
import { formatForumAuthor } from '../forumAuthor'

describe('formatForumAuthor', () => {
  it('登录用户展示姓名与班级', () => {
    expect(formatForumAuthor('张三', '软件2026-1班', false)).toBe('张三 · 软件2026-1班')
  })

  it('游客展示后端返回的年级标签', () => {
    expect(formatForumAuthor('2025 级', '—', true)).toBe('2025 级')
    expect(formatForumAuthor('2026 级新生', '—', true)).toBe('2026 级新生')
  })

  it('游客无年级信息时回退牧院学子', () => {
    expect(formatForumAuthor('', '—', true)).toBe('牧院学子')
  })
})
