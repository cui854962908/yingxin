/**
 * 复制 Edge LevelDB 快照，用 Playwright 读取 campus-map-poi-overrides 并写 JSON。
 * 用法：node scripts/extract-poi-from-leveldb.mjs
 */
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { chromium } from 'playwright'

const KEY = 'campus-map-poi-overrides'
const outPath = path.resolve('data/campus-poi-overrides.json')
const profileCopy = path.resolve('.tmp/edge-profile-copy')
const leveldbSrc = path.join(
  process.env.LOCALAPPDATA ?? path.join(os.homedir(), 'AppData', 'Local'),
  'Microsoft/Edge/User Data/Default/Local Storage/leveldb',
)
const leveldbDst = path.join(profileCopy, 'Default/Local Storage/leveldb')

async function main() {
  if (!fs.existsSync(leveldbSrc)) {
    console.error('未找到 Edge Local Storage')
    process.exit(1)
  }
  fs.mkdirSync(leveldbDst, { recursive: true })
  for (const name of fs.readdirSync(leveldbSrc)) {
    if (!name.endsWith('.ldb') && !name.endsWith('.log')) continue
    try {
      fs.copyFileSync(path.join(leveldbSrc, name), path.join(leveldbDst, name))
    } catch {
      /* 文件被 Edge 锁定时跳过 */
    }
  }

  const ctx = await chromium.launchPersistentContext(profileCopy, {
    channel: 'msedge',
    headless: true,
  })
  try {
    const page = await ctx.newPage()
    await page.goto('http://localhost:5173/campus/2d', {
      waitUntil: 'domcontentloaded',
      timeout: 12000,
    })
    const raw = await page.evaluate((k) => localStorage.getItem(k), KEY)
    if (!raw) {
      console.error('localStorage 无 POI 暂存，请先在 ?calibrate=1 拖点保存')
      process.exit(1)
    }
    const overrides = JSON.parse(raw)
    fs.mkdirSync(path.dirname(outPath), { recursive: true })
    fs.writeFileSync(outPath, JSON.stringify(overrides, null, 2), 'utf8')
    console.log(`extracted ${Object.keys(overrides).length} POIs → ${outPath}`)
  } finally {
    await ctx.close()
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
