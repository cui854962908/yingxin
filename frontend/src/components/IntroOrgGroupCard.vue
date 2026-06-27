<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  subtitle: string
  count: number
  showCount?: boolean
}>()

const showCount = computed(() => props.showCount !== false)

defineEmits<{ click: [] }>()

const initial = computed(() => props.label.charAt(0) || '团')
</script>

<template>
  <button type="button" class="intro-org-card" @click="$emit('click')">
    <span class="intro-org-card__icon" aria-hidden="true">{{ initial }}</span>
    <span class="intro-org-card__body">
      <strong class="intro-org-card__title">{{ label }}</strong>
      <span class="intro-org-card__desc">{{ subtitle }}</span>
    </span>
    <span class="intro-org-card__side">
      <span v-if="showCount" class="intro-org-card__count">{{ count }} 个社团</span>
      <svg class="intro-org-card__chev" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M9 6l6 6-6 6"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </span>
  </button>
</template>
