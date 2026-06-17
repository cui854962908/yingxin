import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { useDrag } from '../useDrag'

function makeCaptureEl() {
  const el = document.createElement('div')
  el.setPointerCapture = vi.fn()
  el.releasePointerCapture = vi.fn()
  el.hasPointerCapture = vi.fn(() => true)
  return el
}

/** jsdom 手动创建的 PointerEvent 需显式设置 target / currentTarget */
function ptrEvent(type: string, opts: PointerEventInit = {}, currentTarget?: HTMLElement) {
  const el = currentTarget ?? makeCaptureEl()
  const e = new PointerEvent(type, { bubbles: true, ...opts })
  Object.defineProperty(e, 'target', { value: document.body, configurable: true })
  Object.defineProperty(e, 'currentTarget', { value: el, configurable: true })
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
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  describe('初始状态', () => {
    it('x/y 基于窗口尺寸计算', () => {
      const { getExposed } = makeWrapper()
      expect(getExposed().x.value).toBe(1024 - 220)
      expect(getExposed().y.value).toBe(768 - 220)
    })

    it('isMobile 在 width <= 768 时为 true', () => {
      window.innerWidth = 375
      const { getExposed } = makeWrapper()
      expect(getExposed().isMobile.value).toBe(true)
    })

    it('移动端初始 y 避让底栏', () => {
      window.innerWidth = 375
      window.innerHeight = 812
      const { getExposed } = makeWrapper()
      expect(getExposed().y.value).toBe(812 - 110 - 68)
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
      const el = makeCaptureEl()

      onPointerDown(ptrEvent('pointerdown', { clientX: 200, clientY: 300, pointerId: 1 }, el))
      expect(dragging.value).toBe(true)

      document.dispatchEvent(ptrEvent('pointermove', { clientX: 240, clientY: 350, pointerId: 1 }))
      expect(x.value).toBe(1024 - 190)
      expect(y.value).toBe(768 - 190 - 10)

      document.dispatchEvent(ptrEvent('pointerup', { pointerId: 1 }))
      expect(dragging.value).toBe(false)
    })

    it('拖拽位置不超过边界', () => {
      window.innerWidth = 400
      window.innerHeight = 400
      const { getExposed } = makeWrapper()
      const { x, y, onPointerDown } = getExposed()

      onPointerDown(ptrEvent('pointerdown', { clientX: 10, clientY: 10, pointerId: 1 }))

      document.dispatchEvent(ptrEvent('pointermove', { clientX: -100, clientY: -100, pointerId: 1 }))
      expect(x.value).toBeGreaterThanOrEqual(10)
      expect(y.value).toBeGreaterThanOrEqual(10)
    })
  })

  describe('点击 vs 拖拽', () => {
    it('轻触（无移动）pointerup 时打开面板', () => {
      const open = ref(false)
      const onOpen = vi.fn()
      const { getExposed } = makeWrapper(open, onOpen)

      getExposed().onPointerDown(ptrEvent('pointerdown', { clientX: 100, clientY: 100, pointerId: 1 }))
      document.dispatchEvent(ptrEvent('pointerup', { clientX: 100, clientY: 100, pointerId: 1 }))

      expect(open.value).toBe(true)
      expect(onOpen).toHaveBeenCalled()
    })

    it('拖拽移动后 pointerup 不触发打开', () => {
      const open = ref(false)
      const onOpen = vi.fn()
      const { getExposed } = makeWrapper(open, onOpen)

      getExposed().onPointerDown(ptrEvent('pointerdown', { clientX: 100, clientY: 100, pointerId: 1 }))
      document.dispatchEvent(ptrEvent('pointermove', { clientX: 200, clientY: 200, pointerId: 1 }))
      document.dispatchEvent(ptrEvent('pointerup', { pointerId: 1 }))

      expect(open.value).toBe(false)
      expect(onOpen).not.toHaveBeenCalled()
    })
  })
})
