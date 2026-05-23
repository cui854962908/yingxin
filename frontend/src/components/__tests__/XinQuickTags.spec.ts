import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import XinQuickTags from '../XinQuickTags.vue'

const mockList = [
  { label: '快递在哪', text: '快递在哪' },
  { label: '熄灯时间', text: '宿舍几点熄灯' },
]

describe('XinQuickTags', () => {
  it('renders all tags from quickList prop', () => {
    const wrapper = mount(XinQuickTags, { props: { quickList: mockList } })
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(2)
    expect(buttons[0].text()).toBe('快递在哪')
    expect(buttons[1].text()).toBe('熄灯时间')
  })

  it('emits select with tag text on click', async () => {
    const wrapper = mount(XinQuickTags, { props: { quickList: mockList } })
    await wrapper.findAll('button')[0].trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0]).toEqual(['快递在哪'])
  })

  it('renders empty when quickList is empty', () => {
    const wrapper = mount(XinQuickTags, { props: { quickList: [] } })
    expect(wrapper.findAll('button')).toHaveLength(0)
  })
})
