import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import XinChatBubble, { type Msg } from '../XinChatBubble.vue'

function makeMsg(overrides: Partial<Msg> = {}): Msg {
  return {
    role: 'xin',
    text: '你好！',
    time: '14:30',
    displayText: '你好！',
    done: true,
    ...overrides,
  }
}

describe('XinChatBubble', () => {
  it('renders xin message with avatar', () => {
    const wrapper = mount(XinChatBubble, { props: { msg: makeMsg() } })
    expect(wrapper.find('.msg-row.xin').exists()).toBe(true)
    expect(wrapper.find('.msg-avatar').exists()).toBe(true)
    expect(wrapper.find('.msg-bubble.xin').exists()).toBe(true)
  })

  it('renders user message without avatar', () => {
    const wrapper = mount(XinChatBubble, { props: { msg: makeMsg({ role: 'user' }) } })
    expect(wrapper.find('.msg-row.user').exists()).toBe(true)
    expect(wrapper.find('.msg-avatar').exists()).toBe(false)
  })

  it('shows typing cursor when xin message is not done', () => {
    const wrapper = mount(XinChatBubble, { props: { msg: makeMsg({ done: false }) } })
    expect(wrapper.find('.msg-cursor').exists()).toBe(true)
  })

  it('hides typing cursor when xin message is done', () => {
    const wrapper = mount(XinChatBubble, { props: { msg: makeMsg({ done: true }) } })
    expect(wrapper.find('.msg-cursor').exists()).toBe(false)
  })

  it('shows navigation links when done and links provided', () => {
    const wrapper = mount(XinChatBubble, {
      props: {
        msg: makeMsg({
          links: [{ label: '查看公告', to: '/announcements' }],
        }),
      },
    })
    expect(wrapper.find('.msg-links').exists()).toBe(true)
    expect(wrapper.find('.msg-link-btn').text()).toBe('查看公告')
  })

  it('hides links when not done even if links provided', () => {
    const wrapper = mount(XinChatBubble, {
      props: {
        msg: makeMsg({
          done: false,
          links: [{ label: '查看公告', to: '/announcements' }],
        }),
      },
    })
    expect(wrapper.find('.msg-links').exists()).toBe(false)
  })

  it('emits navigate when link button clicked', async () => {
    const wrapper = mount(XinChatBubble, {
      props: {
        msg: makeMsg({
          links: [{ label: '去首页', to: '/' }],
        }),
      },
    })
    await wrapper.find('.msg-link-btn').trigger('click')
    expect(wrapper.emitted('navigate')).toBeTruthy()
    expect(wrapper.emitted('navigate')![0]).toEqual(['/'])
  })

  it('emits speak when speak button clicked', async () => {
    const wrapper = mount(XinChatBubble, { props: { msg: makeMsg() } })
    await wrapper.find('.msg-speak-btn').trigger('click')
    expect(wrapper.emitted('speak')).toBeTruthy()
    expect(wrapper.emitted('speak')![0]).toEqual(['你好！'])
  })

  it('displays message time', () => {
    const wrapper = mount(XinChatBubble, { props: { msg: makeMsg({ time: '09:15' }) } })
    expect(wrapper.find('.msg-time').text()).toBe('09:15')
  })
})
