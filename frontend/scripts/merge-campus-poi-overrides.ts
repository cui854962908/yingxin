/**
 * 将校准导出的 JSON 写进 campusPlaces.ts
 * 用法：npx tsx scripts/merge-campus-poi-overrides.ts data/campus-poi-overrides.json
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { campusLngLatToXz } from '../src/components/campus-map/campusGeo'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const frontendRoot = path.resolve(__dirname, '..')
const placesPath = path.join(frontendRoot, 'src/components/campus-map/campusPlaces.ts')

type Overrides = Record<string, [number, number]>

function findMatchingBracket(content: string, openIndex: number): number {
  let depth = 0
  for (let i = openIndex; i < content.length; i++) {
    if (content[i] === '[') depth++
    else if (content[i] === ']') {
      depth--
      if (depth === 0) return i
    }
  }
  throw new Error('DORM_LAYOUT 数组括号不匹配')
}

function updateDormLayout(content: string, dormIndex: number, x: number, z: number): string {
  const layoutStart = content.indexOf('const DORM_LAYOUT')
  const assign = content.indexOf('= [', layoutStart)
  if (assign < 0) throw new Error('DORM_LAYOUT 赋值未找到')
  const open = assign + 2
  const close = findMatchingBracket(content, open)
  const inner = content.slice(open + 1, close)
  const entries = inner.split(/\},\s*\{/).map((chunk, i, arr) => {
    let part = chunk
    if (i > 0) part = `{${part}`
    if (i < arr.length - 1) part = `${part}}`
    return part
  })
  if (dormIndex < 0 || dormIndex >= entries.length) {
    throw new Error(`dorm index ${dormIndex + 1} out of range`)
  }
  entries[dormIndex] = entries[dormIndex].replace(
    /x:\s*[-\d.]+,\s*z:\s*[-\d.]+/,
    `x: ${x.toFixed(2)}, z: ${z.toFixed(2)}`,
  )
  const merged = entries.join(',\n  ')
  return content.slice(0, open + 1) + merged + content.slice(close)
}

function updatePlaceBlock(content: string, id: string, x: number, z: number): string {
  const re = new RegExp(
    `(id:\\s*'${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}'[\\s\\S]*?\\bx:\\s*)([-\\d.]+)(,\\s*\\n\\s*z:\\s*)([-\\d.]+)`,
    'm',
  )
  if (!re.test(content)) {
    throw new Error(`place id not found in campusPlaces.ts: ${id}`)
  }
  return content.replace(re, `$1${x.toFixed(2)}$3${z.toFixed(2)}`)
}

function main() {
  const jsonPath = path.resolve(process.cwd(), process.argv[2] ?? 'data/campus-poi-overrides.json')
  if (!fs.existsSync(jsonPath)) {
    console.error(`找不到 ${jsonPath}，请先从 ?calibrate=1 页面下载 JSON`)
    process.exit(1)
  }
  const overrides = JSON.parse(fs.readFileSync(jsonPath, 'utf8')) as Overrides
  let content = fs.readFileSync(placesPath, 'utf8')

  for (const [id, [lng, lat]] of Object.entries(overrides)) {
    const [x, z] = campusLngLatToXz(lng, lat)
    if (/^dorm-\d+$/.test(id)) {
      const index = Number.parseInt(id.slice(5), 10) - 1
      content = updateDormLayout(content, index, x, z)
    } else {
      content = updatePlaceBlock(content, id, x, z)
    }
    console.log(`updated ${id} → x: ${x.toFixed(2)}, z: ${z.toFixed(2)}`)
  }

  fs.writeFileSync(placesPath, content, 'utf8')
  console.log(`已写入 ${placesPath}，共 ${Object.keys(overrides).length} 个点位`)
}

main()
