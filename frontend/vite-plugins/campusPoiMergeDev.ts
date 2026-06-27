import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import type { Plugin } from 'vite'

const DATA_JSON = 'data/campus-poi-overrides.json'
const PUBLIC_JSON = 'public/campus-map/poi-overrides.json'

function writePublishedPoi(cwd: string, overrides: Record<string, unknown>): number {
  const count = Object.keys(overrides).length
  const dataDir = path.resolve(cwd, 'data')
  fs.mkdirSync(dataDir, { recursive: true })
  fs.mkdirSync(path.dirname(path.resolve(cwd, PUBLIC_JSON)), { recursive: true })
  const payload = JSON.stringify(overrides, null, 2)
  fs.writeFileSync(path.resolve(cwd, DATA_JSON), payload, 'utf8')
  fs.writeFileSync(path.resolve(cwd, PUBLIC_JSON), payload, 'utf8')
  return count
}

function readJsonBody(req: import('http').IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = []
    req.on('data', (chunk) => chunks.push(chunk))
    req.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')))
      } catch (error) {
        reject(error)
      }
    })
    req.on('error', reject)
  })
}

function sendJson(res: import('http').ServerResponse, status: number, body: Record<string, unknown>) {
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.end(JSON.stringify(body))
}

/** 开发环境：校准页发布 POI 到局域网，或合并进 campusPlaces.ts */
export function campusPoiMergeDevPlugin(): Plugin {
  return {
    name: 'campus-poi-merge-dev',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        if (req.method !== 'POST') {
          next()
          return
        }
        const cwd = process.cwd()
        if (req.url === '/__dev/publish-campus-poi') {
          try {
            const overrides = await readJsonBody(req) as Record<string, unknown>
            if (!overrides || typeof overrides !== 'object') {
              sendJson(res, 400, { ok: false, error: '请求体须为 JSON 对象' })
              return
            }
            const updated = writePublishedPoi(cwd, overrides)
            sendJson(res, 200, { ok: true, updated })
          } catch (error) {
            sendJson(res, 400, {
              ok: false,
              error: error instanceof Error ? error.message : String(error),
            })
          }
          return
        }
        if (req.url !== '/__dev/merge-campus-poi') {
          next()
          return
        }
        try {
          const overrides = await readJsonBody(req) as Record<string, unknown>
          if (!overrides || typeof overrides !== 'object') {
            sendJson(res, 400, { ok: false, error: '请求体须为 JSON 对象' })
            return
          }
          const jsonPath = path.resolve(cwd, DATA_JSON)
          writePublishedPoi(cwd, overrides)
          const result = spawnSync(
            'npx',
            ['tsx', 'scripts/merge-campus-poi-overrides.ts', jsonPath],
            { cwd, encoding: 'utf8', shell: true },
          )
          if (result.status !== 0) {
            sendJson(res, 500, { ok: false, error: result.stderr || result.stdout || 'merge failed' })
            return
          }
          sendJson(res, 200, {
            ok: true,
            updated: Object.keys(overrides).length,
            log: result.stdout?.trim(),
          })
        } catch (error) {
          sendJson(res, 400, {
            ok: false,
            error: error instanceof Error ? error.message : String(error),
          })
        }
      })
    },
  }
}
