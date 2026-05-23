<script setup lang="ts">
defineProps<{
  size: 40 | 26
  animated?: boolean
}>()
</script>

<template>
  <svg v-if="size === 40" viewBox="0 0 48 48" fill="none" class="xin-avatar-svg">
    <line x1="24" y1="6" x2="24" y2="2" stroke="#409eff" stroke-width="2" stroke-linecap="round"/>
    <circle cx="24" cy="1.5" r="1.5" fill="#409eff">
      <animate v-if="animated" attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <rect x="8" y="8" width="32" height="28" rx="6" fill="#15202b" stroke="#409eff" stroke-width="1.5"/>
    <rect x="4" y="18" width="4" height="8" rx="2" fill="#1a3050" stroke="#409eff" stroke-width="1"/>
    <rect x="40" y="18" width="4" height="8" rx="2" fill="#1a3050" stroke="#409eff" stroke-width="1"/>
    <circle cx="18" cy="19" r="3.5" fill="#409eff">
      <animate v-if="animated" attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="30" cy="19" r="3.5" fill="#409eff">
      <animate v-if="animated" attributeName="opacity" values="1;0.5;1" dur="2s" begin="0.3s" repeatCount="indefinite"/>
    </circle>
    <rect x="17" y="27" width="14" height="3" rx="1.5" fill="#409eff" opacity="0.6"/>
    <rect x="21" y="10" width="6" height="2" rx="1" fill="#409eff" opacity="0.4">
      <animate v-if="animated" attributeName="opacity" values="0.4;0.9;0.4" dur="2.5s" repeatCount="indefinite"/>
    </rect>
  </svg>

  <svg v-else viewBox="0 0 32 32" fill="none" class="xin-avatar-svg">
    <rect x="5" y="6" width="22" height="19" rx="5" fill="#15202b" stroke="#409eff" stroke-width="1.2"/>
    <line x1="16" y1="4" x2="16" y2="1.5" stroke="#409eff" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="16" cy="1" r="1.5" fill="#409eff"/>
    <circle cx="12" cy="13.5" r="2.5" fill="#409eff"/>
    <circle cx="20" cy="13.5" r="2.5" fill="#409eff"/>
    <rect x="10.5" y="19" width="11" height="2" rx="1" fill="#409eff" opacity="0.5"/>
  </svg>
</template>

<style scoped>
.xin-avatar-svg { width: 100%; height: 100%; display: block; }
</style>
