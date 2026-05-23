<script setup lang="ts">
defineProps<{
  quickList: { label: string; text: string }[]
}>()

const emit = defineEmits<{
  select: [text: string]
}>()
</script>

<template>
  <div class="quick-tags">
    <button
      v-for="(t, idx) in quickList" :key="idx"
      class="quick-tag" @click="emit('select', t.text)"
    >{{ t.label }}</button>
  </div>
</template>

<style scoped>
.quick-tags {
  display: flex; gap: 6px; padding: 10px 16px;
  overflow-x: auto; flex-shrink: 0;
}
.quick-tag {
  flex-shrink: 0; padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid rgba(64,158,255,.15);
  background: rgba(64,158,255,.04); color: #7aa8e0; font-size: .74rem;
  cursor: pointer; white-space: nowrap;
  transition: all .2s; font-family: inherit;
}
.quick-tag:hover {
  border-color: #409eff; color: #409eff;
  background: rgba(64,158,255,.1);
  box-shadow: 0 0 12px rgba(64,158,255,.15);
}
</style>
