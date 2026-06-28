export type ForumCategory = '报到' | '生活' | '学习' | '社团' | '其他'

export interface ForumAuthor {
  name: string
  class_name: string
}

export interface ForumPostBrief {
  id: string
  title: string
  content_preview: string
  category: ForumCategory
  author: ForumAuthor
  answer_count: number
  has_accepted: boolean
  is_closed: boolean
  is_pinned: boolean
  like_count: number
  liked_by_me: boolean
  created_at: string
  is_mine: boolean
}

export interface ForumAnswer {
  id: string
  content: string
  author: ForumAuthor
  is_accepted: boolean
  like_count: number
  liked_by_me: boolean
  created_at: string
  is_mine: boolean
}

export interface ForumPostDetail {
  id: string
  title: string
  content: string
  category: ForumCategory
  author: ForumAuthor
  author_id: number | null
  answer_count: number
  has_accepted: boolean
  is_closed: boolean
  is_pinned: boolean
  like_count: number
  liked_by_me: boolean
  created_at: string
  is_mine: boolean
  answers: ForumAnswer[]
}

export const FORUM_CATEGORIES: ForumCategory[] = ['报到', '学习', '生活', '社团', '其他']

export const FORUM_CATEGORY_COLORS: Record<ForumCategory, string> = {
  报到: '#b5343a',
  生活: '#4a8c5c',
  学习: '#6b5b95',
  社团: '#c9a96e',
  其他: '#8b7b65',
}
