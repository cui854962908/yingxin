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
  display: flex; gap: 8px; padding: 10px 16px 12px;
  overflow-x: auto; flex-shrink: 0;
  width: 100%; max-width: 100%; min-width: 0;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.quick-tags::-webkit-scrollbar { display: none; }
.quick-tag {
  flex-shrink: 0; padding: 9px 15px; min-height: 38px;
  border-radius: 20px;
  border: 1px solid rgba(64,158,255,.22);
  background: linear-gradient(180deg, rgba(64,158,255,.12) 0%, rgba(64,158,255,.05) 100%);
  color: #a8c8f0; font-size: .78rem; letter-spacing: .02em;
  cursor: pointer; white-space: nowrap;
  transition: border-color .2s, background .2s, color .2s, transform .15s;
  font-family: inherit;
}
.quick-tag:hover {
  border-color: rgba(64,158,255,.45); color: #d0e4ff;
  background: linear-gradient(180deg, rgba(64,158,255,.2) 0%, rgba(64,158,255,.08) 100%);
  transform: translateY(-1px);
}
.quick-tag:active { transform: translateY(0); }

@media (max-width: 768px) {
  .quick-tags {
    flex-wrap: wrap;
    overflow-x: visible;
    row-gap: 8px;
  }
}
</style>
