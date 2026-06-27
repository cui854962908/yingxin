import { describe, it, expect } from 'vitest'
import { faqMatchesSearch } from '../faqSearch'

const library = {
  question: '图书馆在哪里？开放时间是几点？',
  answer: '英才校区图书馆位于南门进入校园后右手边，南门是地标。',
  keywords: '图书馆,开放时间,借书,自习',
  category: '学习资源',
}

describe('faqMatchesSearch', () => {
  it('空关键词匹配全部', () => {
    expect(faqMatchesSearch(library, '')).toBe(true)
  })

  it('标题子串命中', () => {
    expect(faqMatchesSearch(library, '图书馆在哪')).toBe(true)
  })

  it('标题短词「书」可命中含图书馆的问题', () => {
    expect(faqMatchesSearch(library, '书')).toBe(true)
  })

  it('keywords 字段命中', () => {
    expect(faqMatchesSearch(library, '自习')).toBe(true)
  })

  it('答案正文有、keywords 无时不命中', () => {
    expect(faqMatchesSearch(library, '南门')).toBe(false)
  })

  it('无关词不匹配', () => {
    expect(faqMatchesSearch(library, '游泳')).toBe(false)
  })
})
