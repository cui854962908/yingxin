/**
 * 将 public/ 下页面引用的 PNG 转为 WebP（保留原 PNG 作回退）。
 * 用法：cd frontend && node scripts/optimize-public-images.mjs
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const PUBLIC = path.join(__dirname, '..', 'public')

/** 仅转换代码中实际引用的背景/插图 PNG */
const TARGETS = [
  'beijing1.png',
  'beijing2.png',
  'club1.png',
  'club2.png',
  'club3.png',
  'dengluzuo.png',
  'dengluyou3.png',
- `logo-1.webp`,
]

async function convertOne(name) {
  const src = path.join(PUBLIC, name)
  if (!fs.existsSync(src)) {
    console.warn(`跳过（不存在）: ${name}`)
    return
  }
  const dest = src.replace(/\.png$/i, '.webp')
  const before = fs.statSync(src).size
  await sharp(src)
    .webp({ quality: 82, effort: 4 })
    .toFile(dest)
  const after = fs.statSync(dest).size
  const pct = Math.round((1 - after / before) * 100)
  console.log(`${name} → ${path.basename(dest)}  ${(before / 1024).toFixed(0)}KB → ${(after / 1024).toFixed(0)}KB (-${pct}%)`)
}

for (const name of TARGETS) {
  await convertOne(name)
}
console.log('完成')
