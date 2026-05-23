export interface Student {
  name: string
  student_id: string
  photo: string
  class_name: string
  dormitory: string
  role: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}
