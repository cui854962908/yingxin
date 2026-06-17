export interface Club {
  id: string
  name: string
  category: '信工团学会' | '校级组织' | '兴趣社团'
  cover_image: string | null
  hero_image: string | null
  intro: string
  status: '招新中' | '已结束'
  recruit_target: string | null
  recruit_start: string | null
  recruit_end: string | null
  recruit_count: number | null
  recruit_require: string | null
  founded_year: number | null
  member_count: number | null
  advisor_name: string | null
  description: string | null
  honor: string | null
  activity_photos: string | null   // JSON 字符串，使用时 JSON.parse
  leader_name: string | null
  leader_phone: string | null
  leaders: string | null
  qq_group: string | null
  wechat_qr: string | null
  owner_student_id: number | null
}
