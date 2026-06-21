/**
 * 从 hnuahe.edu.cn 校园风景页下载官方图片并压缩为 WebP。
 * 用法：cd frontend && node scripts/fetch-campus-official.mjs
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT = path.join(__dirname, '..', 'public', 'campus-official')
const BASE = 'https://www.hnuahe.edu.cn'

/** href 相对 xxgk/xyfj.htm，../ 即站点根目录 */
const ASSETS = [
  { url: `${BASE}/images/10.jpg`, out: 'hero-longzi-gate', maxW: 1920 },
  { url: `${BASE}/fengguang.JPG`, out: 'campus-longzi-scenery', maxW: 1400 },
  { url: `${BASE}/images/01.jpg`, out: 'campus-longzi-library', maxW: 1400 },
  { url: `${BASE}/images/100.jpg`, out: 'campus-yingcai-gate', maxW: 1400 },
  { url: `${BASE}/images/21.jpg`, out: 'campus-yingcai-lake', maxW: 1400 },
  { url: `${BASE}/fj2.jpg`, out: 'campus-beilin-aerial', maxW: 1400 },
]

async function fetchAndConvert({ url, out, maxW }) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${url} → HTTP ${res.status}`)
  const buf = Buffer.from(await res.arrayBuffer())
  const dest = path.join(OUT, `${out}.webp`)
  const meta = await sharp(buf).metadata()
  const pipeline = sharp(buf)
  if (meta.width && meta.width > maxW) {
    pipeline.resize({ width: maxW, withoutEnlargement: true })
  }
  await pipeline.webp({ quality: 82, effort: 4 }).toFile(dest)
  const size = fs.statSync(dest).size
  console.log(`${out}.webp  ${(size / 1024).toFixed(0)} KB  ← ${url}`)
}

fs.mkdirSync(OUT, { recursive: true })
for (const asset of ASSETS) {
  await fetchAndConvert(asset)
}
console.log('完成')
