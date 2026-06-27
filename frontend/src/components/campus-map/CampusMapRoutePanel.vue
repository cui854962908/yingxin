<script setup lang="ts">
import type { RoutePickStep } from '../../composables/useCampusRoutePick'

defineProps<{
  startLabel: string
  endLabel: string
  pickStep: RoutePickStep
  pickMessage: string
  routeDistance: number
  routeMessage: string
  canPlan: boolean
  planning?: boolean
  hasGps?: boolean
}>()

const emit = defineEmits<{
  plan: []
  'pick-start': []
  'pick-end': []
  reset: []
  'use-gps-start': []
}>()
</script>

<template>
  <div class="route-planner">
    <div class="route-planner__desktop">
      <header><strong>路线规划</strong><span>起点可地图选点，终点须选地点标记</span></header>
      <div class="route-points">
        <div class="route-point route-point--start">
          <span class="route-point-tag">起</span>
          <span class="route-point-label">{{ startLabel }}</span>
          <button type="button" @click="emit('pick-start')">重选</button>
        </div>
        <div class="route-point route-point--end">
          <span class="route-point-tag">终</span>
          <span class="route-point-label">{{ endLabel }}</span>
          <button type="button" @click="emit('pick-end')">选地点</button>
        </div>
      </div>
      <p class="route-hint" :class="{ 'route-hint--active': pickStep === 'start' || pickStep === 'end' }">
        {{ pickMessage }}
      </p>
      <button
        v-if="hasGps"
        class="route-gps"
        type="button"
        @click="emit('use-gps-start')"
      >
        ⊙ 用 GPS 位置作起点
      </button>
      <div class="route-actions">
        <button class="route-reset" type="button" @click="emit('reset')">清空</button>
        <button
          class="route-submit"
          type="button"
          :disabled="planning || !canPlan"
          @click="emit('plan')"
        >
          {{ planning ? '规划中…' : '沿校内道路规划' }}
        </button>
      </div>
      <p v-if="routeDistance" class="route-meta">约 {{ routeDistance }} 米 · {{ routeMessage }}</p>
    </div>

    <div class="route-planner__mobile">
      <header class="route-mobile-head">
        <strong>路线规划</strong>
        <span>终点请点地图上的地点</span>
      </header>
      <div class="route-mobile-points">
        <button
          type="button"
          class="route-mobile-point route-mobile-point--start"
          :class="{ 'route-mobile-point--active': pickStep === 'start' }"
          @click="emit('pick-start')"
        >
          <span class="route-point-tag">起</span>
          <span class="route-mobile-point__label">{{ startLabel }}</span>
          <span class="route-mobile-point__action">选地点</span>
        </button>
        <button
          type="button"
          class="route-mobile-point route-mobile-point--end"
          :class="{ 'route-mobile-point--active': pickStep === 'end' }"
          @click="emit('pick-end')"
        >
          <span class="route-point-tag">终</span>
          <span class="route-mobile-point__label">{{ endLabel }}</span>
          <span class="route-mobile-point__action">选地点</span>
        </button>
      </div>
      <div class="route-mobile-bar">
        <button
          v-if="hasGps"
          class="route-mobile-bar__ghost"
          type="button"
          @click="emit('use-gps-start')"
        >
          GPS 起点
        </button>
        <button class="route-mobile-bar__ghost" type="button" @click="emit('reset')">清空</button>
        <button
          class="route-mobile-bar__primary"
          type="button"
          :disabled="planning || !canPlan"
          @click="emit('plan')"
        >
          {{ planning ? '规划中…' : '规划路线' }}
        </button>
      </div>
      <p v-if="routeDistance" class="route-mobile-meta">约 {{ routeDistance }} 米 · {{ routeMessage }}</p>
    </div>
  </div>
</template>
