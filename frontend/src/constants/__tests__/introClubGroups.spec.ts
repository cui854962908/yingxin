import { describe, expect, it } from 'vitest'
import {
  filterClubsByIntroGroupId,
  INTRO_TABS,
  resolveIntroClubGroups,
  resolveIntroTabGroups,
} from '../intro'

describe('intro club groups', () => {
  it('resolves category groups for college filter', () => {
    expect(resolveIntroClubGroups({ categories: ['信工团学会'] })).toEqual([
      {
        id: '信工团学会',
        label: '信工团学会',
        subtitle: '学院团学组织与各科室、社团',
        kind: 'category',
      },
    ])
  })

  it('builds intro tab groups with each school org as its own card', () => {
    const groups = resolveIntroTabGroups([
      { id: 'a', name: '学生会', category: '校级组织', intro: '服务全校同学' },
      { id: 'b', name: '街舞社', category: '兴趣社团', intro: '' },
      { id: 'c', name: '信工篮协', category: '信工团学会', intro: '' },
    ])
    expect(groups.map((g) => g.label)).toEqual(['信工团学会', '学生会', '兴趣社团'])
    expect(groups[1]).toMatchObject({ id: 'club:a', kind: 'club', label: '学生会' })
  })

  it('filters clubs inside selected group', () => {
    const all = [
      { id: '1', category: '信工团学会' },
      { id: '2', category: '兴趣社团' },
    ]
    expect(
      filterClubsByIntroGroupId(all, '信工团学会', { categories: ['信工团学会', '兴趣社团'] }),
    ).toEqual([{ id: '1', category: '信工团学会' }])
  })

  it('filters a single school org club card', () => {
    const all = [
      { id: 'school-1', category: '校级组织' },
      { id: 'school-2', category: '校级组织' },
    ]
    expect(filterClubsByIntroGroupId(all, 'club:school-1')).toEqual([
      { id: 'school-1', category: '校级组织' },
    ])
  })

  it('uses consistent module tab labels', () => {
    expect(INTRO_TABS.map((item) => item.label)).toEqual(['牧院大百科', '学院介绍', '社团介绍'])
  })
})
