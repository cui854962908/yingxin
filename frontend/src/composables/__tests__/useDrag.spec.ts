import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { useDrag } from '../useDrag'

/** jsdom 手动创建的 PointerEvent e.target 为 null，需显式设置 */
function ptrEvent(type: string, opts: PointerEventInit = {}) {
  const e = new PointerEvent(type, { bubbles: true, ...opts })
  Object.defineProperty(e, 'target', { value: document.body, configurable: true })
  return e
}

function makeWrapper(open = ref(false), onOpen = vi.fn()) {
  let exposed: ReturnType<typeof useDrag> | null = null
  const Comp = defineComponent({
    setup() {
      exposed = useDrag(open, onOpen)
      return () => h('div', { style: 'width:100vw;height:100vh' })
    },
  })
  const wrapper = mount(Comp, { attachTo: document.body })
  return { wrapper, getExposed: () => exposed!, open, onOpen }
}

describe('useDrag', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(window, 'innerWidth', { value: 1024, writable: true, configurable: true })
    Object.defineProperty(window, 'innerHeight', { value: 768, writable: true, configurable: true })
    if (!('setPointerCapture' in Element.prototype)) {
      ;(Element.prototype as any).setPointerCapture = vi.fn()
    }
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  describe('初始状态', () => {
    it('x/y 基于窗口尺寸计算', () => {
      const { getExposed } = makeWrapper()
      expect(getExposed().x.value).toBe(1024 - 220)
      expect(getExposed().y.value).toBe(768 - 280)
    })

    it('isMobile 在 width < 768 时为 true', () => {
      window.innerWidth = 375
      const { getExposed } = makeWrapper()
      expect(getExposed().isMobile.value).toBe(true)
    })

    it('isMobile 在 width >= 768 时为 false', () => {
      const { getExposed } = makeWrapper()
      expect(getExposed().isMobile.value).toBe(false)
    })
  })

  describe('resize 事件', () => {
    it('窗口缩放到移动端尺寸后 isMobile 更新', () => {
      const { getExposed } = makeWrapper()
      window.innerWidth = 375
      window.dispatchEvent(new Event('resize'))
      expect(getExposed().isMobile.value).toBe(true)
    })
  })

  describe('拖拽生命周期', () => {
    it('pointerdown → pointermove → pointerup 完整流程', () => {
      const { getExposed } = makeWrapper()
      const { x, y, dragging, onPointerDown } = getExposed()

      onPointerDown(ptrEvent('pointerdown', { clientX: 200, clientY: 300, pointerId: 1 }))
      expect(dragging.value).toBe(true)

      document.dispatchEvent(ptrEvent('pointermove', { clientX: 240, clientY: 350 }))
      expect(x.value).toBe(1024 - 220 + 40) // 804 + 40
      expect(y.value).toBe(768 - 280 + 50)  // 488 + 50

      document.dispatchEvent(ptrEvent('pointerup'))
      expect(dragging.value).toBe(false)
    })

    it('拖拽位置不超过边界', () => {
      window.innerWidth = 400
      window.innerHeight = 400
      const { getExposed } = makeWrapper()
      const { x, y, onPointerDown } = getExposed()

      onPointerDown(ptrEvent('pointerdown', { clientX: 10, clientY: 10, pointerId: 1 }))

      document.dispatchEvent(ptrEvent('pointermove', { clientX: -100, clientY: -100 }))
      expect(x.value).toBeGreaterThanOrEqual(10)
      expect(y.value).toBeGreaterThanOrEqual(10)
    })
  })

  describe('点击 vs 拖拽', () => {
    it('无移动时 onClickXin 打开面板', () => {
      const open = ref(false)
      const onOpen = vi.fn()
      const { getExposed } = makeWrapper(open, onOpen)

      getExposed().onClickXin()
      expect(open.value).toBe(true)
      expect(onOpen).toHaveBeenCalled()
    })

    it('拖拽移动后 onClickXin 不触发打开', () => {
      const open = ref(false)
      const onOpen = vi.fn()
      const { getExposed } = makeWrapper(open, onOpen)

      getExposed().onPointerDown(ptrEvent('pointerdown', { clientX: 100, clientY: 100, pointerId: 1 }))
      document.dispatchEvent(ptrEvent('pointermove', { clientX: 200, clientY: 200 }))
      document.dispatchEvent(ptrEvent('pointerup'))

      open.value = false
      onOpen.mockClear()
      getExposed().onClickXin()
      expect(open.value).toBe(false)
      expect(onOpen).not.toHaveBeenCalled()
    })
  })
})
