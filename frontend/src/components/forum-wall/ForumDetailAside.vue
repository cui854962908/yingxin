<script setup lang="ts">
import type { ForumPostDetail } from '../../types/forum'
import { formatForumAuthor } from '../../utils/forumAuthor'
import { forumRoleLabel } from '../../utils/forumRole'

defineProps<{
  post: ForumPostDetail
  isGuest: boolean
  authorInitial: string
  statusLabel: string
  statusClass: string
}>()

defineEmits<{ like: [] }>()
</script>

<template>
  <aside class="fthread-aside" aria-label="提问信息">
    <section class="fthread-aside-card fthread-aside-author">
      <p class="fthread-aside-kicker">提问者</p>
      <div class="fthread-aside-profile">
        <span class="fthread-avatar fthread-avatar--lg">{{ authorInitial }}</span>
        <div>
          <p class="fthread-aside-name">{{ formatForumAuthor(post.author.name, post.author.class_name, isGuest) }}</p>
          <p v-if="forumRoleLabel(post.author.forum_role)" class="fthread-aside-role">
            <span class="forum-role-badge">{{ forumRoleLabel(post.author.forum_role) }}</span>
          </p>
        </div>
      </div>
    </section>

    <section class="fthread-aside-card">
      <p class="fthread-aside-kicker">提问状态</p>
      <span class="fthread-status" :class="statusClass">{{ statusLabel }}</span>
      <ul class="fthread-stat-grid">
        <li><strong>{{ post.view_count }}</strong><span>浏览</span></li>
        <li><strong>{{ post.answer_count }}</strong><span>回答</span></li>
        <li><strong>{{ post.like_count }}</strong><span>点赞</span></li>
        <li><strong>{{ post.category }}</strong><span>分类</span></li>
      </ul>
      <button
        v-if="!isGuest"
        type="button"
        class="fthread-like fthread-like--block"
        :class="{ 'fthread-like--on': post.liked_by_me }"
        @click="$emit('like')"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
        {{ post.liked_by_me ? '已点赞' : '给提问点赞' }}
      </button>
    </section>

    <section class="fthread-aside-card fthread-aside-tips">
      <p class="fthread-aside-kicker">回答小贴士</p>
      <ol>
        <li>先确认理解问题，再给出具体建议</li>
        <li>分享亲身经历比空泛安慰更有帮助</li>
        <li>不确定时可以说明并建议问辅导员</li>
      </ol>
    </section>
  </aside>
</template>
