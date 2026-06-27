import { campusLngLatToXz, campusXzToLngLat, haversineMeters } from './campusGeo'
import { roadSegmentsInPoiSpace, type CampusRoadSegment } from './campusRoadNetwork'

export type CampusRouteMode = 'campus-road' | 'straight-fallback'

export interface CampusRouteResult {
  path: Array<[number, number]>
  mode: CampusRouteMode
  distanceMeters: number
  message?: string
}

interface XzPoint {
  x: number
  z: number
}

interface GraphNode {
  x: number
  z: number
  edges: Array<{ to: number; weight: number }>
}

const NODE_SNAP = 2.5
const MAX_ATTACH_DIST = 90
const BRIDGE_GAP = 4
/** 点落在路段上的判定容差（POI 空间单位） */
const ON_SEGMENT_TOL = 2.5

function dist(a: XzPoint, b: XzPoint): number {
  return Math.hypot(a.x - b.x, a.z - b.z)
}

function snapCoord(value: number): number {
  return Math.round(value / NODE_SNAP) * NODE_SNAP
}

function buildRoadGraph(segments: CampusRoadSegment[]): GraphNode[] {
  const keyToId = new Map<string, number>()
  const nodes: GraphNode[] = []

  function ensureNode(x: number, z: number): number {
    const sx = snapCoord(x)
    const sz = snapCoord(z)
    const key = `${sx},${sz}`
    let id = keyToId.get(key)
    if (id === undefined) {
      id = nodes.length
      keyToId.set(key, id)
      nodes.push({ x: sx, z: sz, edges: [] })
    }
    return id
  }

  function addEdge(a: number, b: number) {
    if (a === b) return
    const weight = dist(nodes[a], nodes[b])
    if (!nodes[a].edges.some((e) => e.to === b)) nodes[a].edges.push({ to: b, weight })
    if (!nodes[b].edges.some((e) => e.to === a)) nodes[b].edges.push({ to: a, weight })
  }

  for (const seg of segments) {
    const length = dist({ x: seg.x1, z: seg.z1 }, { x: seg.x2, z: seg.z2 })
    const steps = Math.max(1, Math.ceil(length / NODE_SNAP))
    let prev = ensureNode(seg.x1, seg.z1)
    for (let i = 1; i <= steps; i++) {
      const t = i / steps
      const next = ensureNode(
        seg.x1 + t * (seg.x2 - seg.x1),
        seg.z1 + t * (seg.z2 - seg.z1),
      )
      addEdge(prev, next)
      prev = next
    }
  }

  const endpointIds = collectSegmentEndpointIds(segments, nodes, keyToId)
  bridgeEndpointNodes(nodes, endpointIds, addEdge)

  return nodes
}

function collectSegmentEndpointIds(
  segments: CampusRoadSegment[],
  _nodes: GraphNode[],
  keyToId: Map<string, number>,
): Set<number> {
  const ids = new Set<number>()
  for (const seg of segments) {
    for (const pt of [
      { x: snapCoord(seg.x1), z: snapCoord(seg.z1) },
      { x: snapCoord(seg.x2), z: snapCoord(seg.z2) },
    ]) {
      const id = keyToId.get(`${pt.x},${pt.z}`)
      if (id !== undefined) ids.add(id)
    }
  }
  return ids
}

/** 只桥接路口端点，避免在直路中段拉对角线导致路线打弯 */
function bridgeEndpointNodes(
  nodes: GraphNode[],
  endpointIds: Set<number>,
  addEdge: (a: number, b: number) => void,
) {
  const ids = [...endpointIds]
  for (let a = 0; a < ids.length; a++) {
    for (let b = a + 1; b < ids.length; b++) {
      const i = ids[a]
      const j = ids[b]
      const gap = dist(nodes[i], nodes[j])
      if (gap > 0.8 && gap <= BRIDGE_GAP) addEdge(i, j)
    }
  }
}

function findNearestNodeId(graph: GraphNode[], x: number, z: number): number {
  const sx = snapCoord(x)
  const sz = snapCoord(z)
  const exact = graph.findIndex((node) => node.x === sx && node.z === sz)
  if (exact >= 0) return exact
  let bestId = 0
  let bestDist = Infinity
  for (let i = 0; i < graph.length; i++) {
    const d = dist(graph[i], { x, z })
    if (d < bestDist) {
      bestDist = d
      bestId = i
    }
  }
  return bestId
}

interface EntryLink {
  nodeId: number
  cost: number
  via: XzPoint | null
}

function projectToSegment(
  point: XzPoint,
  seg: CampusRoadSegment,
): { x: number; z: number; dist: number } | null {
  const dx = seg.x2 - seg.x1
  const dz = seg.z2 - seg.z1
  const len2 = dx * dx + dz * dz
  if (len2 < 0.01) return null
  let t = ((point.x - seg.x1) * dx + (point.z - seg.z1) * dz) / len2
  t = Math.max(0, Math.min(1, t))
  const x = seg.x1 + t * dx
  const z = seg.z1 + t * dz
  return { x, z, dist: dist(point, { x, z }) }
}

function networkEntryLinks(
  graph: GraphNode[],
  segments: CampusRoadSegment[],
  point: XzPoint,
): EntryLink[] {
  const bestByNode = new Map<number, EntryLink>()
  for (const seg of segments) {
    const proj = projectToSegment(point, seg)
    if (!proj || proj.dist > MAX_ATTACH_DIST) continue
    const projPt = { x: proj.x, z: proj.z }
    const nodeId = findNearestNodeId(graph, proj.x, proj.z)
    const node = graph[nodeId]
    const cost = proj.dist + dist(projPt, node)
    const prev = bestByNode.get(nodeId)
    if (!prev || cost < prev.cost) {
      bestByNode.set(nodeId, {
        nodeId,
        cost,
        via: proj.dist > 0.5 ? projPt : null,
      })
    }
  }
  return [...bestByNode.values()].sort((a, b) => a.cost - b.cost).slice(0, 8)
}

function astar(graph: GraphNode[], startId: number, endId: number): number[] | null {
  if (startId === endId) return [startId]
  const goal = graph[endId]
  const open = new Set<number>([startId])
  const cameFrom = new Map<number, number>()
  const gScore = new Map<number, number>([[startId, 0]])

  function fScore(id: number): number {
    return (gScore.get(id) ?? Infinity) + dist(graph[id], goal)
  }

  while (open.size > 0) {
    let current = -1
    let best = Infinity
    for (const id of open) {
      const f = fScore(id)
      if (f < best) {
        best = f
        current = id
      }
    }
    if (current === endId) {
      const path = [current]
      while (cameFrom.has(path[0])) path.unshift(cameFrom.get(path[0])!)
      return path
    }
    open.delete(current)
    for (const edge of graph[current].edges) {
      const tentative = (gScore.get(current) ?? Infinity) + edge.weight
      if (tentative >= (gScore.get(edge.to) ?? Infinity)) continue
      cameFrom.set(edge.to, current)
      gScore.set(edge.to, tentative)
      open.add(edge.to)
    }
  }
  return null
}

function findPathXz(
  graph: GraphNode[],
  segments: CampusRoadSegment[],
  start: XzPoint,
  end: XzPoint,
): XzPoint[] | null {
  const startLinks = networkEntryLinks(graph, segments, start)
  const endLinks = networkEntryLinks(graph, segments, end)
  if (!startLinks.length || !endLinks.length) return null

  let best: XzPoint[] | null = null
  let bestCost = Infinity

  for (const s of startLinks) {
    for (const e of endLinks) {
      const nodePath = astar(graph, s.nodeId, e.nodeId)
      if (!nodePath) continue
      const points: XzPoint[] = [{ ...start }]
      if (s.via) points.push({ ...s.via })
      for (const id of nodePath) points.push({ x: graph[id].x, z: graph[id].z })
      if (e.via) points.push({ ...e.via })
      points.push({ ...end })
      const roadCost = nodePath
        .slice(1)
        .reduce((sum, id, idx) => sum + dist(graph[nodePath[idx]], graph[id]), 0)
      const cost = s.cost + e.cost + roadCost
      if (cost < bestCost) {
        bestCost = cost
        best = straightenPathOnRoads(dedupePoints(points), segments)
      }
    }
  }
  return best
}

function dedupePoints(points: XzPoint[]): XzPoint[] {
  const out: XzPoint[] = []
  for (const p of points) {
    const last = out[out.length - 1]
    if (!last || dist(last, p) > 0.8) out.push(p)
  }
  return out
}

function segmentIndexForPoint(point: XzPoint, segments: CampusRoadSegment[]): number {
  for (let i = 0; i < segments.length; i++) {
    const proj = projectToSegment(point, segments[i])
    if (proj && proj.dist <= ON_SEGMENT_TOL) return i
  }
  return -1
}

/**
 * 同一路段上的连续点合并为直线端点，保留真正拐弯处。
 * 解决「直路本可走直线却锯齿/打弯」——不裁真实转弯。
 */
function straightenPathOnRoads(points: XzPoint[], segments: CampusRoadSegment[]): XzPoint[] {
  if (points.length <= 2) return points

  const out: XzPoint[] = [points[0]]
  let runSeg = segmentIndexForPoint(points[0], segments)

  for (let i = 1; i < points.length; i++) {
    const seg = segmentIndexForPoint(points[i], segments)
    const atEnd = i === points.length - 1

    if (seg >= 0 && seg === runSeg) {
      if (atEnd) out.push(points[i])
      continue
    }

    if (i > 1 && dist(out[out.length - 1], points[i - 1]) > 0.8) {
      out.push(points[i - 1])
    }
    runSeg = seg
    if (atEnd || seg < 0) out.push(points[i])
  }

  return dedupePoints(out)
}

function pathLengthMeters(path: Array<[number, number]>): number {
  let total = 0
  for (let i = 1; i < path.length; i++) total += haversineMeters(path[i - 1], path[i])
  return Math.round(total)
}

function resolveSegments(drawnSegments: CampusRoadSegment[]): CampusRoadSegment[] {
  if (drawnSegments.length > 0) return drawnSegments
  return roadSegmentsInPoiSpace()
}

/** 沿校内路网 A* 寻路；有手绘路段时优先只用手绘路网 */
export function planCampusRoute(
  startLngLat: [number, number],
  endLngLat: [number, number],
  drawnSegments: CampusRoadSegment[] = [],
): CampusRouteResult {
  const segments = resolveSegments(drawnSegments)
  const graph = buildRoadGraph(segments)
  const [sx, sz] = campusLngLatToXz(startLngLat[0], startLngLat[1])
  const [ex, ez] = campusLngLatToXz(endLngLat[0], endLngLat[1])
  const xzPath = findPathXz(graph, segments, { x: sx, z: sz }, { x: ex, z: ez })

  if (!xzPath || xzPath.length < 2) {
    const path: Array<[number, number]> = [startLngLat, endLngLat]
    return {
      path,
      mode: 'straight-fallback',
      distanceMeters: pathLengthMeters(path),
      message: drawnSegments.length
        ? '手绘路网未连通起终点，请补画中间路段'
        : '暂未连通校内路网，请在校准页标路网',
    }
  }

  const path = xzPath.map((p) => campusXzToLngLat(p.x, p.z))
  path[0] = startLngLat
  path[path.length - 1] = endLngLat
  return {
    path,
    mode: 'campus-road',
    distanceMeters: pathLengthMeters(path),
    message: drawnSegments.length ? '沿手绘校内道路规划' : '沿校内道路规划（步行示意）',
  }
}
