import { describe, expect, it } from 'vitest'
import {
  formatRoadOverridesForSource,
  roadOverridesToPoiSegments,
} from '../campusRoadCalibration'

describe('campusRoadCalibration', () => {
  it('converts lng/lat segments to poi space', () => {
    const segments = roadOverridesToPoiSegments([
      { start: [113.641263, 34.862948], end: [113.641263, 34.863374] },
    ])
    expect(segments).toHaveLength(1)
    expect(segments[0].width).toBe(3)
  })

  it('exports GLB snippet for campusRoadNetwork.ts', () => {
    const text = formatRoadOverridesForSource([
      { start: [113.641263, 34.862948], end: [113.641263, 34.863374] },
    ])
    expect(text).toContain('CAMPUS_ROAD_SEGMENTS')
    expect(text).toContain('x1:')
  })
})
