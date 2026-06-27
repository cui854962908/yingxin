const START_COLOR = '#278b70'
const END_COLOR = '#b5343a'

function routeDotElement(label: string, color: string): HTMLDivElement {
  const wrap = document.createElement('div')
  wrap.style.cssText =
    'width:28px;height:28px;display:flex;align-items:center;justify-content:center;pointer-events:none;'
  const dot = document.createElement('div')
  dot.textContent = label
  dot.style.cssText = [
    'width:22px',
    'height:22px',
    'display:flex',
    'align-items:center',
    'justify-content:center',
    'border:2px solid #fff',
    'border-radius:50%',
    `background:${color}`,
    'color:#fff',
    'font-size:11px',
    'font-weight:700',
    'line-height:1',
    'box-shadow:0 2px 8px rgba(0,0,0,0.25)',
    'box-sizing:border-box',
  ].join(';')
  wrap.appendChild(dot)
  return wrap
}

export function createRoutePointMarker(
  AMap: any,
  lnglat: [number, number],
  kind: 'start' | 'end',
): any {
  const color = kind === 'start' ? START_COLOR : END_COLOR
  const label = kind === 'start' ? '起' : '终'
  return new AMap.Marker({
    position: lnglat,
    anchor: 'center',
    zIndex: 900,
    bubble: true,
    content: routeDotElement(label, color),
  })
}
