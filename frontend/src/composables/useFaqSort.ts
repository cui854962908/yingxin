import { ref, onMounted, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { authHeaders } from './useAuth'

export interface FaqSortable {
  id: string
  sort_order?: number
}

/** 手动 pointer 拖拽排序 FAQ 列表（替代 HTML5 DnD，便于控制视觉反馈） */
export function useFaqSort(
  allItems: Ref<FaqSortable[]>,
  displayItems: ComputedRef<FaqSortable[]>,
) {
  const sortMode = ref(false)
  const dragIdx = ref<number | null>(null)
  const dropIdx = ref<number | null>(null)

  let dragClone: HTMLElement | null = null
  let dragOffsetX = 0
  let dragOffsetY = 0
  let dragCaptureEl: HTMLElement | null = null

  function enterSortMode() {
    sortMode.value = true
    allItems.value.forEach((item, i) => {
      item.sort_order = i
    })
  }

  function exitSortMode() {
    sortMode.value = false
  }

  function domIndexToAllIndex(domIdx: number): number {
    const list = displayItems.value
    if (domIdx >= list.length) return allItems.value.length
    const id = list[domIdx]?.id
    return allItems.value.findIndex(x => x.id === id)
  }

  function startDrag(itemId: string, e: PointerEvent) {
    if (!sortMode.value) return
    e.preventDefault()
    e.stopPropagation()
    const from = allItems.value.findIndex(i => i.id === itemId)
    if (from < 0) return
    dragIdx.value = from
    dropIdx.value = from

    const el = (e.currentTarget as HTMLElement).closest('.faq-item') as HTMLElement
    if (!el) return
    const rect = el.getBoundingClientRect()
    dragOffsetX = e.clientX - rect.left
    dragOffsetY = e.clientY - rect.top

    const clone = el.cloneNode(true) as HTMLElement
    clone.classList.add('faq-item--clone')
    clone.style.position = 'fixed'
    clone.style.zIndex = '9999'
    clone.style.width = `${rect.width}px`
    clone.style.left = `${e.clientX - dragOffsetX}px`
    clone.style.top = `${e.clientY - dragOffsetY}px`
    clone.style.pointerEvents = 'none'
    document.body.appendChild(clone)
    dragClone = clone

    dragCaptureEl = e.currentTarget as HTMLElement
    dragCaptureEl.setPointerCapture(e.pointerId)
  }

  function onDocMove(e: PointerEvent) {
    if (!dragClone || dragIdx.value === null) return
    dragClone.style.left = `${e.clientX - dragOffsetX}px`
    dragClone.style.top = `${e.clientY - dragOffsetY}px`

    const container = document.querySelector('.faq')
    if (!container) return
    const items = container.querySelectorAll<HTMLElement>('.faq-item:not(.faq-item--clone)')
    let found = items.length
    for (let i = 0; i < items.length; i++) {
      const r = items[i].getBoundingClientRect()
      if (e.clientY < r.top + r.height / 2) {
        found = i
        break
      }
    }
    dropIdx.value = domIndexToAllIndex(found)
  }

  function persistReorder(items: FaqSortable[]) {
    fetch('/api/admin/faq/reorder', {
      method: 'PATCH',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        items: items.map(item => ({ id: item.id, sort_order: item.sort_order })),
      }),
    }).catch(() => {})
  }

  function onDocUp(e: PointerEvent) {
    if (dragIdx.value === null && !dragClone) return

    if (dragCaptureEl?.hasPointerCapture?.(e.pointerId)) {
      dragCaptureEl.releasePointerCapture(e.pointerId)
    }
    dragCaptureEl = null

    const from = dragIdx.value
    const to = dropIdx.value
    dragIdx.value = null
    dropIdx.value = null

    if (dragClone) {
      dragClone.remove()
      dragClone = null
    }

    if (from === null || to === null || from === to) return

    const items = [...allItems.value]
    const [moved] = items.splice(from, 1)
    const insertAt = to > from ? to - 1 : to
    items.splice(insertAt, 0, moved)
    items.forEach((item, i) => {
      item.sort_order = i
    })
    allItems.value = items
    persistReorder(items)
  }

  onMounted(() => {
    document.addEventListener('pointermove', onDocMove)
    document.addEventListener('pointerup', onDocUp)
    document.addEventListener('pointercancel', onDocUp)
  })
  onUnmounted(() => {
    document.removeEventListener('pointermove', onDocMove)
    document.removeEventListener('pointerup', onDocUp)
    document.removeEventListener('pointercancel', onDocUp)
  })

  return {
    sortMode,
    dragIdx,
    dropIdx,
    enterSortMode,
    exitSortMode,
    startDrag,
  }
}
