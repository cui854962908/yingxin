<script setup lang="ts">
withDefaults(defineProps<{
  size?: number
  color?: string
  trackColor?: string
}>(), {
  size: 28,
  color: '#b5343a',
  trackColor: '#e5dbcc',
})
</script>

<template>
  <span class="spinner" />
</template>

<style scoped>
.spinner {
  display: inline-block;
  width: v-bind(size + 'px');
  height: v-bind(size + 'px');
  border: 2.5px solid v-bind(trackColor);
  border-top-color: v-bind(color);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
