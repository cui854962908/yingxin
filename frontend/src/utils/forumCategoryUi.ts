import type { ForumCategory } from '../types/forum'
import { FORUM_CATEGORY_COLORS } from '../types/forum'

/** 与牧院新生说筛选栏一致的分类顺序。 */
export const FORUM_CATEGORY_ORDER: ForumCategory[] = ['报到', '宿舍', '学习', '生活', '社团', '其他']

const CATEGORY_ICON: Record<ForumCategory, string> = {
  报到: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2',
  宿舍: 'M3 21h18M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16M9 7h2m2 0h2M9 11h2m2 0h2M9 15h2m2 0h2',
  生活: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
  学习: 'M4 19.5A2.5 2.5 0 0 1 6.5 17H20 M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z',
  社团: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M23 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75',
  其他: 'M12 8v4m0 4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z',
}

export function categoryAccent(cat: ForumCategory): string {
  return FORUM_CATEGORY_COLORS[cat] ?? '#8b7b65'
}

export function categoryIconPath(cat: ForumCategory): string {
  return CATEGORY_ICON[cat] ?? CATEGORY_ICON['其他']
}

export function categoryTint(cat: ForumCategory): string {
  return `color-mix(in srgb, ${categoryAccent(cat)} 14%, #fff)`
}
