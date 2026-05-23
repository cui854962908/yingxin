import { ref } from 'vue'

export function useTTS() {
  const autoSpeak = ref(localStorage.getItem('xin-auto-speak') !== 'false')
  const isSpeaking = ref(false)
  let welcomeSpoken = false
  let audioEl: HTMLAudioElement | null = null

  async function speak(text: string) {
    stopSpeak()
    try {
      const resp = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      if (!resp.ok) return
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      audioEl = new Audio(url)
      isSpeaking.value = true
      audioEl.onended = () => { isSpeaking.value = false; URL.revokeObjectURL(url) }
      audioEl.onerror = () => { isSpeaking.value = false }
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

  return { autoSpeak, isSpeaking, welcomeSpoken, speak, stopSpeak, toggleSpeak }
}
