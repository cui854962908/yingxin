import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import XinAvatar from '../XinAvatar.vue'

describe('XinAvatar', () => {
  it('renders large SVG when size is 40', () => {
    const wrapper = mount(XinAvatar, { props: { size: 40 } })
    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
    expect(svg.attributes('viewBox')).toBe('0 0 48 48')
  })

  it('renders small SVG when size is 26', () => {
    const wrapper = mount(XinAvatar, { props: { size: 26 } })
    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
    expect(svg.attributes('viewBox')).toBe('0 0 32 32')
  })

  it('renders animate elements when animated is true', () => {
    const wrapper = mount(XinAvatar, { props: { size: 40, animated: true } })
    expect(wrapper.findAll('animate').length).toBeGreaterThan(0)
  })

  it('renders no animate elements when animated is false', () => {
    const wrapper = mount(XinAvatar, { props: { size: 40, animated: false } })
    expect(wrapper.findAll('animate').length).toBe(0)
  })
})
