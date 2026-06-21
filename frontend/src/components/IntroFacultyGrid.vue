<script setup lang="ts">
export interface FacultyCard {
  id?: string
  name: string
  bio: string
  photo: string
}

defineProps<{
  cards: FacultyCard[]
  loading?: boolean
}>()
</script>

<template>
  <div class="faculty-grid-wrap">
    <div v-if="loading" class="faculty-grid-loading"><slot name="loading" /></div>
    <div v-else-if="cards.length === 0" class="faculty-grid-empty">暂无师资介绍</div>
    <div v-else class="faculty-grid">
      <article v-for="(c, i) in cards" :key="c.id ?? i" class="faculty-card">
        <div class="faculty-avatar" :class="{ 'faculty-avatar--photo': !!c.photo }">
          <img v-if="c.photo" :src="c.photo" :alt="c.name" loading="lazy" />
          <span v-else>{{ c.name.charAt(0) }}</span>
        </div>
        <h4 class="faculty-name">{{ c.name }}</h4>
        <p class="faculty-bio">{{ c.bio }}</p>
      </article>
    </div>
  </div>
</template>

<style scoped>
.faculty-grid-loading { display: flex; justify-content: center; padding: 16px 0 }
.faculty-grid-empty { text-align: center; color: #b0a090; font-size: .84rem; padding: 20px 0 }
.faculty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
.faculty-card {
  padding: 16px; border-radius: 14px; text-align: center;
  background: #fff; border: 1px solid #f2ebe0;
  transition: box-shadow .2s;
}
.faculty-card:hover { box-shadow: 0 8px 24px rgba(60,48,40,.08) }
.faculty-avatar {
  width: 72px; height: 72px; margin: 0 auto 12px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #75171d, #b5343a);
  color: #f2e6d0; font-size: 1.5rem; font-weight: 700;
  overflow: hidden;
}
.faculty-avatar--photo { background: #f5f0ea }
.faculty-avatar img { width: 100%; height: 100%; object-fit: cover }
.faculty-name { margin: 0 0 8px; font-size: .95rem; color: #3c3028; font-weight: 600 }
.faculty-bio {
  margin: 0; font-size: .78rem; line-height: 1.6; color: #6b5e4e;
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;
  overflow: hidden;
}
@media (max-width: 768px) {
  .faculty-grid { grid-template-columns: repeat(2, 1fr); gap: 12px }
}
</style>
