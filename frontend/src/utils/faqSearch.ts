export interface FaqSearchable {
  question: string
  answer: string
  keywords?: string | null
  category?: string | null
}

/** 短词 → 可匹配的主题词（标题模糊、关键词对照共用） */
const SEARCH_ALIASES: Record<string, readonly string[]> = {
  图书: ['图书馆', '借书', '阅览', '自习'],
  书馆: ['图书馆'],
  书: ['图书馆', '借书'],
  快递: ['快递', '取件', '驿站', '包裹'],
  食堂: ['餐厅', '伙食', '梅园', '桃园', '兰园', '菊园'],
  吃饭: ['餐厅', '食堂', '伙食'],
  宿舍: ['宿舍', '门禁', '公寓'],
  网: ['校园网', 'wifi', '网络', '营业厅'],
  医保: ['医疗保险', '参保'],
  体检: ['体检', '复查'],
  贷款: ['助学贷款', '生源地'],
  助学金: ['助学金', '励志奖学金', '困难补助'],
  报到: ['报到', '接站', '接待站', '入学'],
  校区: ['校区', '龙子湖', '英才', '北林'],
}

function norm(text: string): string {
  return text.trim().toLowerCase()
}

function keywordTokens(keywords?: string | null): string[] {
  if (!keywords) return []
  return keywords
    .split(/[,，、]/)
    .map((t) => t.trim().toLowerCase())
    .filter(Boolean)
}

function queryTouchesAlias(query: string, aliasKey: string): boolean {
  const key = aliasKey.toLowerCase()
  return query.includes(key) || (key.length >= 2 && key.includes(query))
}

function aliasHintsForQuery(query: string): string[] {
  const hints: string[] = []
  for (const [needle, targets] of Object.entries(SEARCH_ALIASES)) {
    if (!queryTouchesAlias(query, needle)) continue
    hints.push(...targets.map((t) => t.toLowerCase()))
  }
  return hints
}

/** 标题：子串 + 别名扩展（如「书」→ 含「图书馆」的标题） */
function questionMatches(query: string, question: string): boolean {
  const title = norm(question)
  if (title.includes(query)) return true

  const hints = aliasHintsForQuery(query)
  return hints.some((hint) => title.includes(hint))
}

/** 答案侧：只对照 keywords 字段，不搜 answer 正文 */
function keywordsMatch(query: string, keywords?: string | null): boolean {
  const tokens = keywordTokens(keywords)
  if (!tokens.length) return false

  if (tokens.some((t) => t.includes(query) || (query.length >= 2 && query.includes(t)))) {
    return true
  }

  const hints = aliasHintsForQuery(query)
  return hints.some((hint) => tokens.some((t) => t.includes(hint) || hint.includes(t)))
}

export function faqMatchesSearch(item: FaqSearchable, rawQuery: string): boolean {
  const q = norm(rawQuery)
  if (!q) return true
  return questionMatches(q, item.question) || keywordsMatch(q, item.keywords)
}
