<script setup lang="ts">
import { campusCategories } from './campusPlaces'
import type { CampusPlace } from './types'

const props = defineProps<{
  place: CampusPlace
  favorite: boolean
}>()

const emit = defineEmits<{ favorite: []; route: []; locate: [] }>()
</script>

<template>
  <aside class="campus-detail">
    <div class="detail-heading">
      <i :style="{ background: campusCategories.find((item) => item.key === place.category)?.color }">
        {{ campusCategories.find((item) => item.key === place.category)?.label[0] }}
      </i>
      <span>
        <small>{{ campusCategories.find((item) => item.key === place.category)?.label }} · {{ place.tags[0] }}</small>
        <h2>{{ place.name }}</h2>
        <p>{{ place.area }}</p>
      </span>
      <button type="button" :class="{ active: favorite }" aria-label="收藏地点" @click="emit('favorite')">☆</button>
    </div>
    <div class="photo-placeholder">
      <span>▧</span><strong>地点图片</strong><small>可后续补充英才校区实景照片</small>
    </div>
    <div class="verify-row"><span>数据：校内导览</span><span>底图：高德地图</span></div>
    <dl>
      <div><dt>⌖ 位置说明</dt><dd>{{ place.address }}</dd></div>
      <div><dt>◷ 开放时间</dt><dd>{{ place.openTime || '以学校实际安排为准' }}</dd></div>
      <div><dt>ⓘ 使用说明</dt><dd>地点信息将持续根据学校实际情况更新。</dd></div>
    </dl>
    <section>
      <h3>地点简介</h3>
      <p>{{ place.description }}</p>
      <h3>标签</h3>
      <div class="tag-list"><span v-for="tag in place.tags" :key="tag">{{ tag }}</span></div>
      <h3>数据来源</h3>
      <p class="source">高德地图公开底图<br />河南牧业经济学院英才校区校内导览数据</p>
    </section>
    <footer>
      <button class="primary" type="button" @click="emit('locate')">⌖ 定位到地图</button>
      <button type="button" @click="emit('favorite')">☆ {{ favorite ? '已收藏' : '收藏' }}</button>
      <button type="button" @click="emit('route')">⌁ 路线规划</button>
    </footer>
  </aside>
</template>
