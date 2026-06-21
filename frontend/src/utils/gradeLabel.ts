/** 当前迎新届（6 月起算新一届，与学号前缀展示一致） */
export function currentEnrollmentYear(now = new Date()): number {
  const y = now.getFullYear()
  const m = now.getMonth() + 1
  return m >= 6 ? y : y - 1
}

export function enrollmentYearFromStudentId(studentId: string): number | null {
  const m = studentId?.trim().match(/^(\d{4})/)
  if (!m) return null
  const y = Number(m[1])
  return Number.isFinite(y) && y >= 2000 && y <= 2100 ? y : null
}

/** 侧边栏角色标签：管理员 / 社团管理员 / 年级文案 */
export function studentGradeLabel(studentId: string, now = new Date()): string {
  const year = enrollmentYearFromStudentId(studentId)
  if (!year) return '学生'
  if (year === currentEnrollmentYear(now)) return `${year} 级新生`
  return `${year} 级`
}

/** 首页资料卡右上角年份徽章 */
export function studentGradeBadge(studentId: string): string {
  const year = enrollmentYearFromStudentId(studentId)
  return year ? String(year) : ''
}
