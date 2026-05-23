import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick, type Ref } from 'vue'
import { useXinChat } from '../useXinChat'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

describe('useXinChat', () => {
  let autoSpeak: Ref<boolean>
  let speak = vi.fn<(text: string) => void>()
  let chat: ReturnType<typeof useXinChat>

  const mockFetch = (ok: boolean, data: unknown) => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok,
      json: () => Promise.resolve(data),
    } as Response)
  }

  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
    autoSpeak = ref(false)
    speak = vi.fn<(text: string) => void>()
  })

  afterEach(() => {
    chat?.closeChat()
  })

  function createChat() {
    chat = useXinChat(autoSpeak, speak)
    return chat
  }

  describe('ensureWelcome', () => {
    it('消息列表为空时推送欢迎消息', async () => {
      const { messages, ensureWelcome } = createChat()
      ensureWelcome()
      await nextTick()
      expect(messages.value.length).toBe(1)
      expect(messages.value[0].role).toBe('xin')
      expect(messages.value[0].text).toContain('河南牧业经济学院')
    })

    it('第二次调用不重复推送', async () => {
      const { messages, ensureWelcome } = createChat()
      ensureWelcome()
      await nextTick()
      ensureWelcome()
      await nextTick()
      expect(messages.value.length).toBe(1)
    })

    it('首次调用后自动朗读（延迟）', async () => {
      vi.useFakeTimers()
      const { ensureWelcome } = createChat()
      ensureWelcome()
      vi.advanceTimersByTime(800)
      expect(speak).toHaveBeenCalledWith(expect.stringContaining('河南牧业经济学院'))
      vi.useRealTimers()
    })

    it('第二次调用不再朗读', async () => {
      vi.useFakeTimers()
      const { ensureWelcome } = createChat()
      ensureWelcome()
      vi.advanceTimersByTime(800)
      speak.mockClear()

      ensureWelcome()
      vi.advanceTimersByTime(800)
      expect(speak).not.toHaveBeenCalled()
      vi.useRealTimers()
    })
  })

  describe('send', () => {
    it('空输入时不发送', () => {
      const { send, input, messages, sending } = createChat()
      input.value = '   '
      send()
      expect(sending.value).toBe(false)
      expect(messages.value.length).toBe(0)
    })

    it('发送中时不重复发送', () => {
      const { send, input, sending, messages } = createChat()
      input.value = '你好'
      sending.value = true
      send()
      expect(messages.value.length).toBe(0)
    })

    it('输入和发送后清空 input', async () => {
      const { send, input, messages } = createChat()
      input.value = '测试消息'

      // agent chat 返回有效响应
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: { reply: '测试回复', source: 'faq' },
        }),
      } as Response)

      send()
      expect(input.value).toBe('')
      expect(messages.value[0].text).toBe('测试消息')
      expect(messages.value[0].role).toBe('user')
    })
  })

  describe('closeChat / navigateTo', () => {
    it('closeChat 设置 open 为 false', () => {
      const { open, closeChat } = createChat()
      open.value = true
      closeChat()
      expect(open.value).toBe(false)
    })

    it('navigateTo 关闭面板并跳转', () => {
      const { navigateTo, open } = createChat()
      open.value = true
      navigateTo('/faq')
      expect(open.value).toBe(false)
    })
  })

  describe('onKeydown', () => {
    it('Enter 触发 send', () => {
      const { onKeydown, input } = createChat()
      input.value = '测试'
      const e = new KeyboardEvent('keydown', { key: 'Enter', shiftKey: false })
      // send 内部会调用 fetch，我们验证 input 清空即可
      e.preventDefault = vi.fn()
      onKeydown(e)
      expect(e.preventDefault).toHaveBeenCalled()
      expect(input.value).toBe('')
    })

    it('Shift+Enter 不触发 send', () => {
      const { onKeydown, input } = createChat()
      input.value = '测试'
      const e = new KeyboardEvent('keydown', { key: 'Enter', shiftKey: true })
      e.preventDefault = vi.fn()
      onKeydown(e)
      expect(e.preventDefault).not.toHaveBeenCalled()
      expect(input.value).toBe('测试')
    })

    it('其他按键不触发 send', () => {
      const { onKeydown, input } = createChat()
      input.value = '测试'
      const e = new KeyboardEvent('keydown', { key: 'a' })
      e.preventDefault = vi.fn()
      onKeydown(e)
      expect(e.preventDefault).not.toHaveBeenCalled()
    })
  })

  describe('quickList', () => {
    it('包含 4 个快捷入口', () => {
      const { quickList } = createChat()
      expect(quickList).toHaveLength(4)
      expect(quickList.map(q => q.text)).toContain('快递在哪')
      expect(quickList.map(q => q.text)).toContain('宿舍几点熄灯')
    })
  })

  describe('complete flow: agent → fallback', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })
    afterEach(() => {
      vi.useRealTimers()
    })

    it('当 agent 和 stream 均失败时走本地 fallback', async () => {
      const { send, input, messages } = createChat()
      input.value = '快递在哪'

      // Agent chat 失败
      vi.spyOn(globalThis, 'fetch')
        .mockRejectedValueOnce(new Error('agent down')) // agent
        .mockResolvedValueOnce({ ok: false } as Response) // stream
        .mockResolvedValueOnce({ // faq fetch
          ok: true,
          json: () => Promise.resolve({ success: true, data: [{ question: '快递在哪', answer: '菜鸟驿站' }] }),
        } as Response)
        .mockResolvedValueOnce({ // announcements fetch
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        } as Response)

      send()
      // 推进 fallbackReply 的 setTimeout(..., 400)
      await vi.advanceTimersByTimeAsync(500)

      expect(messages.value.length).toBeGreaterThanOrEqual(2) // user + xin reply
      const xinMsg = messages.value.find((m) => m.role === 'xin')
      expect(xinMsg?.text).toContain('菜鸟驿站')
    })

    it('当 agent 成功时直接使用 agent 回复', async () => {
      const { send, input, messages } = createChat()
      input.value = '学费怎么交'

      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: { reply: '学费通过学校统一支付平台缴纳', source: 'faq' },
        }),
      } as Response)

      send()
      await vi.advanceTimersByTimeAsync(100)

      const xinMsg = messages.value.find((m) => m.role === 'xin')
      expect(xinMsg).toBeDefined()
      expect(xinMsg!.text).toContain('统一支付平台')
    })
  })
})
