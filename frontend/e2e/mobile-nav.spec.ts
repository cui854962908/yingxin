import { test, expect } from '@playwright/test'

test.describe('移动端底栏导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())

    await page.route('**/api/verify', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '欢迎你，测试同学！',
          token: 'e2e-mobile-token',
          data: {
            name: '测试同学',
            student_id: '20260901001',
            role: 'student',
            class_name: '计算机科学2026-1班',
            dormitory: '1号楼101',
            photo: '',
            advisor: { name: '李老师', phone: '13800000001' },
            class_teacher: { name: '王老师', phone: '13800000002' },
            assistants: [],
          },
        }),
      })
    })

    await page.route('**/api/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            name: '测试同学',
            student_id: '20260901001',
            role: 'student',
            class_name: '计算机科学2026-1班',
            dormitory: '1号楼101',
            photo: '',
            advisor: { name: '李老师', phone: '13800000001' },
            class_teacher: { name: '王老师', phone: '13800000002' },
            assistants: [],
          },
        }),
      })
    })

    await page.route('**/api/faq**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { items: [{ id: '1', question: '快递在哪', answer: '菜鸟驿站' }], total: 1 },
        }),
      })
    })

    await page.route('**/api/announcements', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: [] }) })
    })

    await page.route('**/api/clubs', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: [] }) })
    })
  })

  test('底栏可直达 FAQ 页', async ({ page }) => {
    await page.getByPlaceholder('请输入你的姓名').fill('测试同学')
    await page.getByPlaceholder('请输入你的学号').fill('20260901001')
    await page.getByRole('button', { name: /验.*登.*录/ }).click()

    await expect(page.getByRole('heading', { name: '测试同学' })).toBeVisible({ timeout: 10000 })

    await page.getByRole('button', { name: '答疑' }).click()
    await expect(page).toHaveURL(/\/faq/)
    await expect(page.getByText('常见问题')).toBeVisible()
  })
})
