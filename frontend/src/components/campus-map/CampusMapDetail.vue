<script setup lang="ts">
import { campusCategories } from './campusPlaces'
import type { CampusPlace } from './types'

defineProps<{ place: CampusPlace; sheet?: boolean; routePlanning?: boolean }>()

const emit = defineEmits<{ go: []; locate: []; close: [] }>()
</script>

<template>
  <aside class="campus-detail" :class="{ 'campus-detail--sheet': sheet }">
    <div class="detail-heading">
      <i :style="{ background: campusCategories.find((item) => item.key === place.category)?.color }">
        {{ campusCategories.find((item) => item.key === place.category)?.label[0] }}
      </i>
      <span>
        <small>{{ campusCategories.find((item) => item.key === place.category)?.label }} · {{ place.tags[0] }}</small>
        <h2>{{ place.name }}</h2>
      </span>
      <button
        v-if="sheet"
        type="button"
        class="detail-close"
        aria-label="关闭地点详情"
        @click="emit('close')"
      >
        ×
      </button>
    </div>
    <div class="photo-placeholder">
      <span>▧</span><strong>地点图片</strong><small>可后续补充英才校区实景照片</small>
    </div>
    <dl>
      <div><dt>⌖ 位置说明</dt><dd>{{ place.address }}</dd></div>
      <div><dt>◷ 开放时间</dt><dd>{{ place.openTime || '以学校实际安排为准' }}</dd></div>
    </dl>
    <section>
      <h3>地点简介</h3>
      <p>{{ place.description }}</p>
      <h3>标签</h3>
      <div class="tag-list"><span v-for="tag in place.tags" :key="tag">{{ tag }}</span></div>
    </section>
    <footer>
      <button v-if="!sheet" type="button" class="detail-locate-btn" @click="emit('locate')">⌖ 在地图中查看</button>
      <button
        class="primary detail-go-btn"
        type="button"
        :disabled="routePlanning"
        @click="emit('go')"
      >
        {{ routePlanning ? '规划中…' : '我要去这' }}
      </button>
    </footer>
  </aside>
</template>
