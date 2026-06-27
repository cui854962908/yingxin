<script setup lang="ts">
const emit = defineEmits<{ back: [] }>()
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
  </header>
</template>
