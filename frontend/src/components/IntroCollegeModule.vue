<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import AppSpinner from './AppSpinner.vue'
import IntroFacultyGrid, { type FacultyCard } from './IntroFacultyGrid.vue'
import '../styles/intro-theme.css'

const props = defineProps<{
  overviewCategory: string
  facultyCategory: string
  overviewFallback: { title: string; content: string }[]
  facultyFallback: { title: string; content: string }[]
}>()

interface ContentBlock { id?: string; title: string; content: string }

const blocks = ref<ContentBlock[]>([])
const faculty = ref<FacultyCard[]>([])
const loading = ref(true)
const { isAdmin } = useAuth()

function photoFromHtml(html: string): string {
  const m = html.match(/<img[^>]+src=["']([^"']+)["']/i)
  return m?.[1] ?? ''
}

function bioText(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

function mapFaculty(items: { id?: string; title: string; content: string }[]): FacultyCard[] {
  return items.map((x) => ({
    id: x.id,
    name: x.title,
    bio: bioText(x.content),
    photo: photoFromHtml(x.content),
  }))
}

async function fetchCategory(category: string) {
  const res = await fetch(`/api/announcements?category=${encodeURIComponent(category)}`)
  const d = await res.json()
  return d.success && d.data?.length ? d.data : null
}

async function load() {
  loading.value = true
  try {
    const [overviewRaw, facultyRaw] = await Promise.all([
      fetchCategory(props.overviewCategory),
      fetchCategory(props.facultyCategory),
    ])
    blocks.value = overviewRaw
      ? overviewRaw.map((x: ContentBlock) => ({ id: x.id, title: x.title, content: x.content }))
      : props.overviewFallback
    faculty.value = facultyRaw
      ? mapFaculty(facultyRaw)
      : mapFaculty(props.facultyFallback)
  } catch {
    blocks.value = props.overviewFallback
    faculty.value = mapFaculty(props.facultyFallback)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="college-module">
    <div v-if="loading" class="college-loading"><AppSpinner /></div>
    <template v-else>
      <div id="section-overview" class="college-sections">
      <section
        v-for="(item, i) in blocks" :key="item.id ?? i"
        class="module-section"
        :class="{ 'module-section--lead': i === 0 }"
      >
        <header class="module-section-head">
          <span class="module-section-idx">{{ String(i + 1).padStart(2, '0') }}</span>
          <h3 class="module-section-title">{{ item.title }}</h3>
        </header>
        <div class="module-section-body" v-html="item.content" />
      </section>
      </div>

      <section id="section-faculty" class="module-section module-section--faculty">
        <header class="module-section-head">
          <span class="module-section-idx">师资</span>
          <h3 class="module-section-title">师资队伍</h3>
        </header>
        <IntroFacultyGrid :cards="faculty">
          <template #loading><AppSpinner /></template>
        </IntroFacultyGrid>
      </section>

      <p v-if="isAdmin" class="college-admin-hint">
        学院模块由公告维护：
        概况 <code>{{ overviewCategory }}</code>，
        师资 <code>{{ facultyCategory }}</code>（标题为姓名，正文为简介，可插图）。
      </p>
    </template>
  </div>
</template>

<style scoped>
.college-module { display: flex; flex-direction: column; gap: 10px }
.college-sections { display: flex; flex-direction: column; gap: 10px }
.college-loading { display: flex; justify-content: center; padding: 20px 0 }
.module-section {
  padding: 14px 16px; border-radius: var(--intro-radius-sm, 12px);
  background: #fff;
  border: 1px solid var(--intro-line, #f0e8dc);
  box-shadow: 0 2px 10px rgba(60,48,40,.04);
}
.module-section--lead {
  border-left: 3px solid var(--intro-accent, #b5343a);
  background: linear-gradient(135deg, #fff 0%, #fefcf9 100%);
}
.module-section--faculty {
  border-top: none;
  padding-top: 14px;
}
.module-section-head {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
}
.module-section-idx {
  flex-shrink: 0; font-size: 0.64rem; font-weight: 700;
  color: var(--intro-accent, #b5343a); background: rgba(181,52,58,.08);
  padding: 3px 7px; border-radius: 6px;
}
.module-section-title {
  margin: 0; font-size: 0.96rem; font-weight: 700; color: var(--intro-ink, #3c3028);
  font-family: 'Noto Serif SC', Georgia, serif;
}
.module-section-body {
  font-size: 0.84rem; line-height: 1.65; color: var(--intro-muted, #5a4e42);
}
.module-section-body :deep(p) { margin: 0 0 .75em }
.module-section-body :deep(img),
.module-section-body :deep(.intro-inline-photo) {
  display: block;
  width: 100%;
  max-width: 360px;
  max-height: 180px;
  object-fit: cover;
  border-radius: 10px;
  margin: 8px 0;
}
.module-section-body :deep(h4) {
  margin: 1em 0 .5em; font-size: .92rem; color: #3c3028;
}
.module-section-body :deep(ul) {
  margin: 0; padding-left: 1.1em;
}
.module-section-body :deep(li) {
  margin-bottom: .45em;
}
.module-section-body :deep(li)::marker {
  color: var(--intro-accent, #b51f2d);
}
.module-section-body :deep(.intro-feature-grid) {
  margin-top: 2px;
}
.module-section-body :deep(.intro-feature-note) {
  margin-top: 10px;
}
.college-admin-hint {
  font-size: .72rem; color: #b0a090; margin: 0; line-height: 1.6;
}
.college-admin-hint code {
  font-size: .7rem; background: #f5f0ea; padding: 1px 6px; border-radius: 4px;
}
@media (max-width: 768px) {
  .module-section { padding: 12px 12px; border-radius: 10px }
}
</style>
