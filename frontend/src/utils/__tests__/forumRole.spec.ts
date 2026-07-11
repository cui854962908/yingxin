import { describe, expect, it } from 'vitest'
import { forumRoleLabel } from '../forumRole'

describe('forumRoleLabel', () => {
  it('maps the supported forum roles to user-facing labels', () => {
    expect(forumRoleLabel('teacher')).toBe('老师')
    expect(forumRoleLabel('assistant')).toBe('代班')
  })

  it('does not create a badge label when the account has no forum role', () => {
    expect(forumRoleLabel(null)).toBeNull()
  })
})
