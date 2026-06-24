import { ref } from 'vue'

const MS_PER_CHAR_MIN = 18
const MS_PER_CHAR_MAX = 120

export function useTTS() {
  const autoSpeak = ref(localStorage.getItem('xin-auto-speak') !== 'false')
  const isSpeaking = ref(false)
  let audioEl: HTMLAudioElement | null = null
  let speakToken = 0
  let syncTimer: ReturnType<typeof setTimeout> | null = null

  // 逐句播放队列（SSE 流式场景：文字边打边显，语音逐句播报）
  let speakQueue: string[] = []
  let queueRunning = false

  function clearSyncTimer() {
    if (syncTimer) {
      clearTimeout(syncTimer)
      syncTimer = null
    }
  }

  function waitAudioMeta(audio: HTMLAudioElement): Promise<void> {
    return new Promise((resolve, reject) => {
      if (audio.readyState >= 1 && Number.isFinite(audio.duration) && audio.duration > 0) {
        resolve()
        return
      }
      const fallback = setTimeout(() => resolve(), 3000)
      audio.onloadedmetadata = () => {
        clearTimeout(fallback)
        resolve()
      }
      audio.onerror = () => {
        clearTimeout(fallback)
        reject(new Error('audio load failed'))
      }
    })
  }

  async function fetchAudio(text: string, token: number): Promise<{ url: string; audio: HTMLAudioElement } | null> {
    const resp = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
    if (!resp.ok || token !== speakToken) return null
    const blob = await resp.blob()
    if (token !== speakToken) return null
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    return { url, audio }
  }

  async function speak(text: string) {
    stopSpeak()
    const token = ++speakToken
    if (!text.trim()) return
    try {
      const loaded = await fetchAudio(text, token)
      if (!loaded || token !== speakToken) return
      const { url, audio } = loaded
      audioEl = audio
      isSpeaking.value = true
      audio.onended = () => {
        isSpeaking.value = false
        URL.revokeObjectURL(url)
      }
      audio.onerror = () => { isSpeaking.value = false }
      if (token !== speakToken) {
        URL.revokeObjectURL(url)
        return
      }
      await audio.play()
    } catch {
      isSpeaking.value = false
    }
  }

  /** 按 TTS 音频时长同步逐字展示并播放（手动朗读按钮/Agent 非流式回复仍用此方法） */
  async function speakSynced(
    text: string,
    onReveal: (partial: string) => void,
    onComplete?: () => void,
  ) {
    stopSpeak()
    const token = ++speakToken
    const content = text.trim()
    if (!content) {
      onComplete?.()
      return
    }

    try {
      const loaded = await fetchAudio(content, token)
      if (!loaded || token !== speakToken) {
        onReveal(content)
        onComplete?.()
        return
      }

      const { url, audio } = loaded
      audioEl = audio
      try {
        await waitAudioMeta(audio)
      } catch {
        URL.revokeObjectURL(url)
        onReveal(content)
        onComplete?.()
        return
      }

      if (token !== speakToken) {
        URL.revokeObjectURL(url)
        return
      }

      const duration = Number.isFinite(audio.duration) && audio.duration > 0
        ? audio.duration
        : content.length * 0.08
      const msPerChar = Math.min(
        MS_PER_CHAR_MAX,
        Math.max(MS_PER_CHAR_MIN, (duration * 1000) / content.length),
      )

      isSpeaking.value = true
      audio.onended = () => {
        isSpeaking.value = false
        URL.revokeObjectURL(url)
        audioEl = null
      }
      audio.onerror = () => { isSpeaking.value = false }

      let i = 0
      onReveal(content.slice(0, 1))
      void audio.play()

      await new Promise<void>((resolve) => {
        const step = () => {
          if (token !== speakToken) {
            resolve()
            return
          }
          i += 1
          if (i >= content.length) {
            onReveal(content)
            onComplete?.()
            resolve()
            return
          }
          onReveal(content.slice(0, i + 1))
          syncTimer = setTimeout(step, msPerChar)
        }
        syncTimer = setTimeout(step, msPerChar)
      })
    } catch {
      isSpeaking.value = false
      onReveal(content)
      onComplete?.()
    }
  }

  /** 将一句文字加入 TTS 播放队列（不阻塞调用方，逐句 FIFO 播放） */
  function enqueueSpeak(text: string) {
    if (!autoSpeak.value || !text.trim()) return
    speakQueue.push(text.trim())
    if (!queueRunning) {
      void processQueue()
    }
  }

  async function processQueue() {
    queueRunning = true
    while (speakQueue.length > 0) {
      const token = speakToken // 拍快照：若中途 stopSpeak 会递增，下轮循环退出
      const sentence = speakQueue.shift()!
      try {
        const loaded = await fetchAudio(sentence, token)
        if (!loaded || token !== speakToken) break
        const { url, audio } = loaded
        audioEl = audio
        isSpeaking.value = true

        await new Promise<void>((resolve) => {
          audio.onended = () => {
            isSpeaking.value = false
            URL.revokeObjectURL(url)
            audioEl = null
            resolve()
          }
          audio.onerror = () => {
            isSpeaking.value = false
            URL.revokeObjectURL(url)
            audioEl = null
            resolve()
          }
          if (token !== speakToken) {
            URL.revokeObjectURL(url)
            audioEl = null
            resolve()
            return
          }
          audio.play().catch(() => resolve())
        })
      } catch {
        // 某句 TTS 失败不影响队列中后续句子
      }
      if (token !== speakToken) break
    }
    queueRunning = false
    isSpeaking.value = false
  }

  function stopSpeak() {
    clearSyncTimer()
    speakToken += 1
    speakQueue = []
    queueRunning = false
    if (audioEl) {
      audioEl.pause()
      audioEl = null
    }
    isSpeaking.value = false
  }

  function toggleSpeak() {
    autoSpeak.value = !autoSpeak.value
    localStorage.setItem('xin-auto-speak', String(autoSpeak.value))
    if (!autoSpeak.value) stopSpeak()
  }

  return { autoSpeak, isSpeaking, speak, speakSynced, enqueueSpeak, stopSpeak, toggleSpeak }
}

export type XinTTS = Pick<ReturnType<typeof useTTS>, 'speak' | 'speakSynced' | 'enqueueSpeak' | 'stopSpeak'>
