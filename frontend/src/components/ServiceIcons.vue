<script setup lang="ts">
import { ICON_PATHS } from '../constants/icons'

const props = defineProps<{ name: string }>()

function svg(name: string): string {
  const p = ICON_PATHS[name]
  if (!p) return ''
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">${p}</svg>`
}
</script>

<template>
  <div v-if="ICON_PATHS[props.name]" class="icon-wrap" v-html="svg(props.name)" />
</template>

<style scoped>
.icon-wrap {
  width: 56px; height: 56px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #fef3f3 0%, #fdf0ea 100%);
  border: 1px solid rgba(181,52,58,.08);
  flex-shrink: 0;
}
.icon-wrap :deep(svg) {
  width: 32px; height: 32px;
  fill: #b5343a;
}
</style>
