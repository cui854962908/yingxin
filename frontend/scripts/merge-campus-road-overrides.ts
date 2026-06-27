/**
 * 将校准页导出的路网 JSON 写进 campusRoadNetwork.ts
 * 用法：npx tsx scripts/merge-campus-road-overrides.ts ../campus-road-overrides.json
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { campusLngLatToXz } from '../src/components/campus-map/campusGeo'
import { CAMPUS_ROAD_POI_OFFSET } from '../src/components/campus-map/campusRoadNetwork'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const frontendRoot = path.resolve(__dirname, '..')
const roadPath = path.join(frontendRoot, 'src/components/campus-map/campusRoadNetwork.ts')

interface RoadLngLatSegment {
  start: [number, number]
  end: [number, number]
}

function toGlbLine(seg: RoadLngLatSegment): string {
  const [x1, z1] = campusLngLatToXz(seg.start[0], seg.start[1])
  const [x2, z2] = campusLngLatToXz(seg.end[0], seg.end[1])
  const { x: ox, z: oz } = CAMPUS_ROAD_POI_OFFSET
  return `  { x1: ${(x1 + ox).toFixed(2)}, z1: ${(z1 + oz).toFixed(2)}, x2: ${(x2 + ox).toFixed(2)}, z2: ${(z2 + oz).toFixed(2)}, width: 3 },`
}

function main() {
  const jsonPath = path.resolve(process.cwd(), process.argv[2] ?? 'data/campus-road-overrides.json')
  if (!fs.existsSync(jsonPath)) {
    console.error(`找不到 ${jsonPath}`)
    process.exit(1)
  }
  const segments = JSON.parse(fs.readFileSync(jsonPath, 'utf8')) as RoadLngLatSegment[]
  if (!Array.isArray(segments) || !segments.length) {
    console.error('JSON 须为非空路段数组')
    process.exit(1)
  }

  const lines = segments.map(toGlbLine)
  const arrayBody = ['/** 英才校区手绘路网（高德底图校准，维护导入） */', 'export const CAMPUS_ROAD_SEGMENTS: CampusRoadSegment[] = [', ...lines, ']'].join('\n')

  let content = fs.readFileSync(roadPath, 'utf8')
  content = content.replace(
    /\/\*\* 英才校区手绘路网[\s\S]*?export const CAMPUS_ROAD_SEGMENTS: CampusRoadSegment\[\] = \[[\s\S]*?\]/,
    arrayBody,
  )

  fs.writeFileSync(roadPath, content, 'utf8')
  console.log(`已写入 ${segments.length} 段路网 → ${roadPath}`)
}

main()
