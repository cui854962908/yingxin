<script setup lang="ts">
import { FORUM_MODULE_NAME } from '../../constants/product'

defineEmits<{ ask: [] }>()
</script>

<template>
  <header class="wall-hero wall-enter-head">
    <div class="wall-hero-text">
      <h1 class="wall-title">{{ FORUM_MODULE_NAME }}</h1>
      <p class="wall-sub">新生互助 · 学长学姐答疑 · 小信答不上来这里问</p>
    </div>
    <button type="button" class="wall-ask-btn" @click="$emit('ask')">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v8M8 12h8" />
      </svg>
      我要提问
    </button>
  </header>
</template>
