import { test, expect } from '@playwright/test'

test.describe('学生核心用户流', () => {
  test.beforeEach(async ({ page }) => {
    // 清除 localStorage，确保每次从登录页开始
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())

    // Mock /api/verify 返回成功登录
    await page.route('**/api/verify', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '欢迎你，测试同学！',
          token: 'e2e-test-token-mock',
          refresh_token: 'e2e-test-refresh-mock',
          data: {
            name: '测试同学',
            student_id: '20260901001',
            role: 'student',
            class_name: '计算机科学2026-1班',
            dormitory: '1号楼101',
            photo: '',
            advisor: { name: '李老师', phone: '13800000001' },
            class_teacher: { name: '王老师', phone: '13800000002' },
            assistants: [{ name: '张代班', phone: '13800000003', class_name: '软件工程2025-1班' }],
          },
        }),
      })
    })

    // Mock /api/agent/chat 返回 AI 回复
    await page.route('**/api/agent/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            reply: '快递统一送到学校菜鸟驿站，凭取件码领取。驿站地址在图书馆北侧，营业时间 9:00-21:00。',
            source: 'faq',
            intent: 'logistics',
          },
        }),
      })
    })

    // Mock /api/faq 和 /api/announcements（兜底查询时会用到）
    await page.route('**/api/faq', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [] }),
      })
    })
    await page.route('**/api/announcements', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [] }),
      })
    })
  })

  test('登录 → 打开小信 → 发送消息 → 收到 AI 回复', async ({ page }) => {
    // === 阶段 1：等待欢迎动画结束，进入登录页 ===
    await page.goto('/')

    // 登录表单应在欢迎动画结束后可见（约 3.5s）
    const nameInput = page.locator('#name')
    await expect(nameInput).toBeVisible({ timeout: 8000 })

    // === 阶段 2：填写登录表单 ===
    await nameInput.fill('测试同学')
    await page.locator('#studentId').fill('20260901001')
    await page.locator('#password').fill('01234567')

    // 点击登录按钮
    await page.locator('button[type="submit"]').click()

    // === 阶段 3：登录成功，小信悬浮角色应出现 ===
    const xinCharacter = page.locator('.xin-character')
    await expect(xinCharacter).toBeVisible({ timeout: 5000 })

    // === 阶段 4：点击小信，打开聊天面板 ===
    await xinCharacter.click()
    const chatPanel = page.locator('.xin-panel')
    await expect(chatPanel).toBeVisible({ timeout: 3000 })

    // 应显示欢迎消息
    const welcomeMsg = chatPanel.locator('.msg-bubble.xin')
    await expect(welcomeMsg.first()).toBeVisible({ timeout: 5000 })

    // === 阶段 5：输入问题并发送 ===
    const chatInput = chatPanel.locator('.chat-input')
    await chatInput.fill('快递在哪')
    await page.keyboard.press('Enter')

    // === 阶段 6：验证 AI 回复出现在消息中 ===
    // 发送后应出现包含"菜鸟驿站"的回复（打字机效果会逐字显示，最长 ~10s）
    // 注意：600ms 后会追加链接消息，故不取 .last()，在整个面板中查找
    await expect(chatPanel).toContainText('菜鸟驿站', { timeout: 15000 })
  })

  test('未登录时小信不显示', async ({ page }) => {
    await page.goto('/')

    // 等待登录页显示
    await expect(page.locator('#name')).toBeVisible({ timeout: 8000 })

    // 小信角色不应出现
    const xinCharacter = page.locator('.xin-character')
    await expect(xinCharacter).not.toBeVisible()
  })

  test('Escape 键关闭聊天面板', async ({ page }) => {
    await page.goto('/')

    // 登录
    const nameInput = page.locator('#name')
    await expect(nameInput).toBeVisible({ timeout: 8000 })
    await nameInput.fill('测试同学')
    await page.locator('#studentId').fill('20260901001')
    await page.locator('#password').fill('01234567')
    await page.locator('button[type="submit"]').click()

    // 等待小信出现
    await expect(page.locator('.xin-character')).toBeVisible({ timeout: 5000 })

    // 打开聊天
    await page.locator('.xin-character').click()
    await expect(page.locator('.xin-panel')).toBeVisible({ timeout: 3000 })

    // 按 Escape 关闭
    await page.keyboard.press('Escape')
    await expect(page.locator('.xin-panel')).not.toBeVisible({ timeout: 3000 })
  })
})
