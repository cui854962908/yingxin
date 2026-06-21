import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useTTS } from '../useTTS'

describe('useTTS', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test')
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    // jsdom 的 HTMLAudioElement play/pause 需要 mock
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue(undefined)
    vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
  })

  describe('autoSpeak', () => {
    it('默认为 true', () => {
      const { autoSpeak } = useTTS()
      expect(autoSpeak.value).toBe(true)
    })

    it('当 localStorage 存储 "false" 时返回 false', () => {
      localStorage.setItem('xin-auto-speak', 'false')
      const { autoSpeak } = useTTS()
      expect(autoSpeak.value).toBe(false)
    })
  })

  describe('speak', () => {
    it('成功获取 TTS 并播放音频', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        blob: () => Promise.resolve(new Blob(['audio'])),
      } as Response)

      const { speak, isSpeaking } = useTTS()
      await speak('你好')

      expect(fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ text: '你好' }),
      }))
      expect(HTMLMediaElement.prototype.play).toHaveBeenCalled()
      expect(isSpeaking.value).toBe(true)
    })

    it('HTTP 错误时不播放', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({ ok: false } as Response)

      const { speak, isSpeaking } = useTTS()
      await speak('你好')

      expect(HTMLMediaElement.prototype.play).not.toHaveBeenCalled()
      expect(isSpeaking.value).toBe(false)
    })

    it('网络异常时 isSpeaking 为 false', async () => {
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('network'))

      const { speak, isSpeaking } = useTTS()
      await speak('你好')

      expect(isSpeaking.value).toBe(false)
    })

    it('播放前停止之前的音频', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValue({
        ok: true,
        blob: () => Promise.resolve(new Blob(['audio'])),
      } as Response)

      const { speak } = useTTS()
      await speak('你好')
      await speak('世界')

      expect(HTMLMediaElement.prototype.pause).toHaveBeenCalled()
    })
  })

  describe('stopSpeak', () => {
    it('停止当前音频并重置状态', () => {
      const { stopSpeak, isSpeaking } = useTTS()
      isSpeaking.value = true
      stopSpeak()
      expect(isSpeaking.value).toBe(false)
    })
  })

  describe('toggleSpeak', () => {
    it('切换 autoSpeak 并持久化到 localStorage', () => {
      const { toggleSpeak, autoSpeak } = useTTS()
      expect(autoSpeak.value).toBe(true)
      toggleSpeak()
      expect(autoSpeak.value).toBe(false)
      expect(localStorage.getItem('xin-auto-speak')).toBe('false')
    })

    it('关闭时停止播放', () => {
      const { toggleSpeak, autoSpeak, isSpeaking } = useTTS()
      isSpeaking.value = true
      toggleSpeak()
      expect(autoSpeak.value).toBe(false)
      expect(isSpeaking.value).toBe(false)
    })
  })

  describe('speakSynced', () => {
    it('TTS 失败时仍展示全文', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({ ok: false } as Response)

      const { speakSynced } = useTTS()
      let final = ''
      await speakSynced('测试', (p) => { final = p })

      expect(final).toBe('测试')
    })
  })
})
