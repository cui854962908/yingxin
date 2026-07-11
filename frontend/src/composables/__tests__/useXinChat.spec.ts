import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick, type Ref } from 'vue'
import { useXinChat, buildQuickTagsFromFaq } from '../useXinChat'
import { usePreload } from '../usePreload'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

function makeTtsMock() {
  const speak = vi.fn(async (_text: string) => {})
  const stopSpeak = vi.fn()
  const enqueueSpeak = vi.fn((_text: string) => {})
  const speakSynced = vi.fn(async (
    text: string,
    onReveal: (partial: string) => void,
    onComplete?: () => void,
  ) => {
    for (let i = 0; i < text.length; i++) {
      onReveal(text.slice(0, i + 1))
    }
    onComplete?.()
  })
  return { speak, speakSynced, enqueueSpeak, stopSpeak }
}

describe('useXinChat', () => {
  let autoSpeak: Ref<boolean>
  let tts: ReturnType<typeof makeTtsMock>
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
    localStorage.setItem('token', 'test-token')
    autoSpeak = ref(true)
    tts = makeTtsMock()
    usePreload().faqItems.value = []
  })

  afterEach(() => {
    chat?.closeChat()
  })

  function createChat() {
    chat = useXinChat(autoSpeak, tts)
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

    it('开启语音时同步朗读欢迎语', async () => {
      const { ensureWelcome } = createChat()
      ensureWelcome()
      await nextTick()
      await vi.waitFor(() => {
        expect(tts.speakSynced).toHaveBeenCalledWith(
          expect.stringContaining('河南牧业经济学院'),
          expect.any(Function),
          expect.any(Function),
        )
      })
    })

    it('第二次调用不再朗读', async () => {
      const { ensureWelcome } = createChat()
      ensureWelcome()
      await nextTick()
      tts.speakSynced.mockClear()

      ensureWelcome()
      await nextTick()
      expect(tts.speakSynced).not.toHaveBeenCalled()
    })
  })

  describe('send', () => {
    it('空输入不发送', async () => {
      const { send, input, messages } = createChat()
      input.value = '   '
      await send()
      expect(messages.value.length).toBe(0)
    })

    it('未登录时不调用接口', async () => {
      localStorage.removeItem('token')
      const { send, input, messages } = createChat()
      input.value = 'hello'
      await send()
      expect(messages.value.some(m => m.role === 'user')).toBe(false)
      expect(messages.value.some(m => m.text.includes('登录'))).toBe(true)
    })

    it('发送后清空输入框', async () => {
      mockFetch(true, { success: true, data: { reply: 'ok', source: 'faq' } })
      const { send, input } = createChat()
      input.value = 'hello'
      await send()
      expect(input.value).toBe('')
    })
  })

  describe('quickList', () => {
    it('buildQuickTagsFromFaq 按 FAQ 顺序取前 3 条', () => {
      const tags = buildQuickTagsFromFaq([
        { question: '快递在哪' },
        { question: '宿舍几点熄灯' },
        { question: '学费怎么交' },
        { question: '有没有街舞社' },
        { question: '报到要带什么' },
        { question: '食堂开放时间' },
        { question: '多余条目' },
      ])
      expect(tags).toHaveLength(3)
      expect(tags[0]).toEqual({ label: '快递在哪', text: '快递在哪' })
      expect(tags[2].text).toBe('学费怎么交')
    })

    it('过长问题截断展示、点击仍发完整问题', () => {
      const longQ = '新生报到需要携带哪些材料和证件'
      const tags = buildQuickTagsFromFaq([{ question: longQ }])
      expect(tags[0].label).toBe('新生报到需要携带哪些材料…')
      expect(tags[0].text).toBe(longQ)
    })

    it('FAQ 预加载后 quickList 同步更新', () => {
      const { faqItems } = usePreload()
      faqItems.value = [
        { id: '1', question: '快递在哪', answer: '菜鸟驿站' },
        { id: '2', question: '宿舍几点熄灯', answer: '23:00' },
      ]
      const { quickList } = createChat()
      expect(quickList.value).toHaveLength(2)
      expect(quickList.value[0].text).toBe('快递在哪')
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

      vi.spyOn(globalThis, 'fetch')
        .mockRejectedValueOnce(new Error('agent down'))
        .mockResolvedValueOnce({ ok: false } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [{ question: '快递在哪', answer: '菜鸟驿站' }] }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        } as Response)

      send()
      await vi.advanceTimersByTimeAsync(500)

      expect(messages.value.length).toBeGreaterThanOrEqual(2)
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

    it('agent fallback 时推送牧院新生说跳转链接', async () => {
      localStorage.setItem('token', 'test-token')
      autoSpeak.value = false
      const { send, input, messages } = createChat()
      input.value = '食堂几点开门'

      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: { reply: '这个问题我暂时答不上来，可以去牧院新生说问问学长学姐哦', source: 'fallback' },
        }),
      } as Response)

      send()
      await vi.runAllTimersAsync()

      const answerMsg = messages.value.find(m => m.role === 'xin' && m.text.includes('答不上'))
      const linkMsg = messages.value.find(m => m.links?.some(l => l.to.startsWith('/wall/new')))
      expect(answerMsg?.done).toBe(true)
      expect(linkMsg).toBeDefined()
      expect(linkMsg!.links![0].label).toContain('牧院新生说')
      expect(decodeURIComponent(linkMsg!.links![0].to)).toContain('食堂几点开门')
    })

    it('agent 回答完成后才添加细节引导', async () => {
      autoSpeak.value = false
      const { send, input, messages, sending } = createChat()
      input.value = '学校食堂在哪里'

      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: { reply: '学校共有三个食堂，分布在各宿舍区附近。', source: 'faq' },
        }),
      } as Response)

      const pending = send()
      await vi.advanceTimersByTimeAsync(1)

      const answer = messages.value.find(m => m.role === 'xin' && m.source === 'faq')
      expect(answer?.done).toBe(false)
      expect(sending.value).toBe(false)
      expect(messages.value.some(m => m.links?.length)).toBe(false)

      await vi.runAllTimersAsync()
      await pending
      expect(answer?.done).toBe(true)
      expect(messages.value.some(m => m.links?.length)).toBe(true)
    })

    it('本地兜底未知问题时文案含牧院新生说', async () => {
      localStorage.setItem('token', 'test-token')
      const { send, input, messages } = createChat()
      input.value = '完全不知道的问题xyz'

      vi.spyOn(globalThis, 'fetch')
        .mockRejectedValueOnce(new Error('agent down'))
        .mockResolvedValueOnce({ ok: false } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        } as Response)

      send()
      await vi.advanceTimersByTimeAsync(700)

      const xinMsgs = messages.value.filter(m => m.role === 'xin')
      const unknownReply = xinMsgs.find(m => m.text.includes('答不上'))
      expect(unknownReply?.text).toContain('牧院新生说')
      const linkMsg = xinMsgs.find(m => m.links?.some(l => l.to.startsWith('/wall/new')))
      expect(linkMsg).toBeDefined()
    })
  })
})
