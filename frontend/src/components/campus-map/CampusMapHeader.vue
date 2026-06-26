<script setup lang="ts">
import type { CampusTab } from './types'

defineProps<{ activeTab: CampusTab; favoriteCount: number }>()
const emit = defineEmits<{ change: [tab: CampusTab]; back: [] }>()

const tabs: { key: CampusTab; label: string }[] = [
  { key: 'map', label: '地图' },
  { key: 'route', label: '路线规划' },
  { key: 'favorites', label: '收藏夹' },
  { key: 'data', label: '数据说明' },
]
</script>

<template>
  <header class="campus-header">
    <div class="campus-header-start">
      <button type="button" class="campus-header-back" aria-label="返回导览方式选择" @click="emit('back')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true">
          <path d="M15 18l-6-6 6-6" />
        </svg>
        <span class="campus-header-back__text">返回</span>
      </button>
      <div class="campus-brand">
        <img class="brand-logo" src="/logo-1.webp" alt="河南牧业经济学院校徽" />
        <span><strong>牧院导览</strong><small>英才校区信息地图</small></span>
      </div>
    </div>
    <nav aria-label="2D 校园导览功能">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        :class="{ active: activeTab === tab.key }"
        @click="emit('change', tab.key)"
      >
        <svg v-if="tab.key === 'map'" viewBox="0 0 24 24" aria-hidden="true">
          <path d="m3 6 5-2 8 3 5-2v13l-5 2-8-3-5 2Z" />
          <path d="M8 4v13M16 7v13" />
        </svg>
        <svg v-else-if="tab.key === 'route'" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="5" cy="18" r="2" />
          <circle cx="19" cy="6" r="2" />
          <path d="M7 17c3-1 2-5 5-6s3-3 5-4" />
        </svg>
        <svg v-else-if="tab.key === 'favorites'" viewBox="0 0 24 24" aria-hidden="true">
          <path d="m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z" />
        </svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 11v6M12 7h.01" />
        </svg>
        {{ tab.label }}
        <b v-if="tab.key === 'favorites' && favoriteCount">{{ favoriteCount }}</b>
      </button>
    </nav>
    <div class="data-status"><i />真实底图 · 校内导览数据</div>
  </header>
</template>
