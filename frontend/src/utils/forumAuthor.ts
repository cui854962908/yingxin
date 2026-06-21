/** 游客浏览问牧墙时弱化作者信息 */
export function formatForumAuthor(
  name: string,
  className: string,
  guest: boolean,
): string {
  if (!guest) {
    const cls = className?.trim()
    return cls ? `${name} · ${cls}` : name
  }
  return '2026 级新生'
}
