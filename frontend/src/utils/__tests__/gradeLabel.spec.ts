import { describe, expect, it } from 'vitest'
import { currentEnrollmentYear, studentGradeBadge, studentGradeLabel } from '../gradeLabel'

const june2026 = new Date(2026, 5, 13)

describe('gradeLabel', () => {
  it('derives current enrollment year from calendar', () => {
    expect(currentEnrollmentYear(new Date(2026, 5, 1))).toBe(2026)
    expect(currentEnrollmentYear(new Date(2026, 4, 31))).toBe(2025)
  })

  it('shows 级新生 only for current cohort', () => {
    expect(studentGradeLabel('20260901001', june2026)).toBe('2026 级新生')
    expect(studentGradeLabel('20250901001', june2026)).toBe('2025 级')
  })

  it('extracts badge year from student id prefix', () => {
    expect(studentGradeBadge('20250901001')).toBe('2025')
    expect(studentGradeBadge('invalid')).toBe('')
  })
})
