<script setup lang="ts">
import { ref, inject, type Ref } from 'vue'
import { INTRO_SCHOOL } from '../../constants/intro'

const emit = defineEmits<{
  pickTopic: [keyword: string]
}>()

const xinOpen = inject<Ref<boolean>>('xinOpen')
const isAuthenticated = inject<Ref<boolean>>('isAuthenticated', ref(false))

const topicSets = [
  ['#新生报到', '#宿舍生活', '#选课指南', '#社团招新', '#校园地图', '#军训须知'],
  ['#龙子湖校区', '#英才校区', '#北林校区', '#食堂推荐', '#图书馆', '#转专业'],
]
const topicIndex = ref(0)
const hotTopics = ref(topicSets[0])

function rotateTopics() {
  topicIndex.value = (topicIndex.value + 1) % topicSets.length
  hotTopics.value = topicSets[topicIndex.value]
}

function openXin() {
  if (!isAuthenticated.value) {
    window.alert('登录后可使用小信 AI 助手')
    return
  }
  if (xinOpen) xinOpen.value = true
}
</script>

<template>
  <aside class="wall-aside" aria-label="牧院新生说侧边栏">
    <section class="wall-aside-card">
      <h3 class="wall-aside-title">提问说明</h3>
      <ol class="wall-aside-tips">
        <li>先搜索是否已有类似问题，避免重复提问</li>
        <li>标题简明、正文写清背景，方便学长学姐回答</li>
        <li>文明用语，互助氛围靠大家共同维护</li>
      </ol>
    </section>

    <section class="wall-aside-card">
      <div class="wall-aside-head">
        <h3 class="wall-aside-title">热门话题</h3>
        <button type="button" class="wall-aside-link" @click="rotateTopics">换一换 ›</button>
      </div>
      <div class="wall-aside-tags">
        <button
          v-for="tag in hotTopics"
          :key="tag"
          type="button"
          class="wall-aside-tag"
          @click="emit('pickTopic', tag.replace(/^#/, ''))"
        >
          {{ tag }}
        </button>
      </div>
    </section>

    <section class="wall-aside-card wall-aside-xin">
      <div class="wall-aside-xin-text">
        <h3 class="wall-aside-title">小信助手</h3>
        <p>常见问题可先问小信，秒级回复</p>
        <button type="button" class="wall-aside-xin-btn" @click="openXin">去咨询小信</button>
      </div>
      <div class="wall-aside-xin-avatar" aria-hidden="true">信</div>
    </section>

    <p class="wall-aside-copy">
      © {{ new Date().getFullYear() }} {{ INTRO_SCHOOL }}迎新系统 · 信息化管理办公室
    </p>
  </aside>
</template>
