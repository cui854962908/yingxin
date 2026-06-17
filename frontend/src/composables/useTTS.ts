import { ref } from 'vue'

export function useTTS() {
  const autoSpeak = ref(localStorage.getItem('xin-auto-speak') !== 'false')
  const isSpeaking = ref(false)
  let audioEl: HTMLAudioElement | null = null
  let speakToken = 0

  async function speak(text: string) {
    stopSpeak()
    const token = ++speakToken
    try {
      const resp = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      if (!resp.ok || token !== speakToken) return
      const blob = await resp.blob()
      if (token !== speakToken) return
      const url = URL.createObjectURL(blob)
      audioEl = new Audio(url)
      isSpeaking.value = true
      audioEl.onended = () => { isSpeaking.value = false; URL.revokeObjectURL(url) }
      audioEl.onerror = () => { isSpeaking.value = false }
      if (token !== speakToken) { URL.revokeObjectURL(url); return }
      audioEl.play()
    } catch { isSpeaking.value = false }
  }

  function stopSpeak() {
    if (audioEl) { audioEl.pause(); audioEl = null }
    isSpeaking.value = false
  }

  function toggleSpeak() {
    autoSpeak.value = !autoSpeak.value
    localStorage.setItem('xin-auto-speak', String(autoSpeak.value))
    if (!autoSpeak.value) stopSpeak()
  }

  return { autoSpeak, isSpeaking, speak, stopSpeak, toggleSpeak }
}
