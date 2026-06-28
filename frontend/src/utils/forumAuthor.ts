/** 游客浏览牧院新生说时弱化作者信息（展示后端返回的年级标签，如「2025 级」） */
export function formatForumAuthor(
  name: string,
  className: string,
  guest: boolean,
): string {
  if (!guest) {
    const cls = className?.trim()
    return cls ? `${name} · ${cls}` : name
  }
  return name?.trim() || '牧院学子'
}
