import type { ForumRole } from '../types/forum'

const FORUM_ROLE_LABELS: Record<ForumRole, string> = {
  teacher: '老师',
  assistant: '代班',
}

export function forumRoleLabel(role: ForumRole | null | undefined): string | null {
  return role ? FORUM_ROLE_LABELS[role] : null
}
