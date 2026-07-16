<script setup lang="ts">
import type { ForumAnswer } from '../../types/forum'
import { formatForumAuthor } from '../../utils/forumAuthor'
import { forumRoleLabel } from '../../utils/forumRole'
import { formatRelativeTime } from '../../utils/formatTime'

defineProps<{
  answer: ForumAnswer
  index: number
  authorInitial: string
  isGuest: boolean
  canAccept: boolean
}>()

defineEmits<{ like: []; accept: [] }>()
</script>

<template>
  <article class="fthread-ans-card" :class="{ 'fthread-ans-card--accepted': answer.is_accepted }">
    <span class="fthread-ans-index" aria-hidden="true">{{ index + 1 }}</span>
    <div class="fthread-ans-inner">
      <div class="fthread-ans-top">
        <span class="fthread-avatar fthread-avatar--xs">{{ authorInitial }}</span>
        <span v-if="answer.is_accepted" class="fthread-accept-badge">最佳回答</span>
        <span class="fthread-ans-author">{{ formatForumAuthor(answer.author.name, answer.author.class_name, isGuest) }}</span>
        <span v-if="forumRoleLabel(answer.author.forum_role)" class="forum-role-badge">
          {{ forumRoleLabel(answer.author.forum_role) }}
        </span>
        <time class="fthread-ans-time" :datetime="answer.created_at">{{ formatRelativeTime(answer.created_at) }}</time>
        <div v-if="canAccept || !isGuest" class="fthread-ans-actions">
          <button
            v-if="canAccept"
            type="button"
            class="fthread-accept-btn"
            title="采纳此回答"
            @click="$emit('accept')"
          >
            采纳
          </button>
          <button
            v-if="!isGuest"
            type="button"
            class="fthread-like fthread-like--sm"
            :class="{ 'fthread-like--on': answer.liked_by_me }"
            @click="$emit('like')"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
            {{ answer.like_count > 0 ? answer.like_count : '赞' }}
          </button>
        </div>
      </div>
      <p class="fthread-ans-body">{{ answer.content }}</p>
    </div>
  </article>
</template>
