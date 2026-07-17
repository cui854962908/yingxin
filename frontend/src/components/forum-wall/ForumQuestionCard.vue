<script setup lang="ts">
import type { CSSProperties } from 'vue'
import type { ForumPostBrief } from '../../types/forum'
import { formatForumAuthor } from '../../utils/forumAuthor'
import { forumRoleLabel } from '../../utils/forumRole'
import { formatRelativeTime } from '../../utils/formatTime'
import { categoryAccent, categoryIconPath, categoryTint } from '../../utils/forumCategoryUi'

const props = defineProps<{
  item: ForumPostBrief
  isGuest: boolean
  canDelete: boolean
}>()

defineEmits<{ open: []; delete: [event: Event] }>()

const cardStyle = {
  '--wall-accent': categoryAccent(props.item.category),
  '--wall-icon-bg': categoryTint(props.item.category),
} as CSSProperties

function statusInfo() {
  if (props.item.has_accepted) return { label: '已解决', className: 'wall-status--solved' }
  if (props.item.is_closed) return { label: '已关闭', className: 'wall-status--closed' }
  if (props.item.answer_count === 0) return { label: '待解答', className: 'wall-status--await' }
  return null
}
</script>

<template>
  <article
    class="wall-card"
    :class="{ 'wall-card--pinned': item.is_pinned }"
    :style="cardStyle"
    tabindex="0"
    @click="$emit('open')"
    @keydown.enter="$emit('open')"
  >
    <button v-if="canDelete" type="button" class="wall-del-btn" @click.stop="$emit('delete', $event)">删除</button>

    <div class="wall-card-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path :d="categoryIconPath(item.category)" /></svg>
    </div>

    <div class="wall-card-body">
      <div class="wall-card-head">
        <div class="wall-card-title-row">
          <span v-if="item.is_pinned" class="wall-pin">置顶</span>
          <h2 class="wall-card-title">{{ item.title }}</h2>
        </div>
        <span v-if="statusInfo()" class="wall-status" :class="statusInfo()?.className">
          {{ statusInfo()?.label }}
        </span>
      </div>

      <p class="wall-card-preview">{{ item.content_preview }}</p>

      <footer class="wall-card-foot">
        <div class="wall-card-meta">
          <span class="wall-cat">{{ item.category }}</span>
          <span class="wall-author-dot" aria-hidden="true"></span>
          <span>{{ formatForumAuthor(item.author.name, item.author.class_name, isGuest) }}</span>
          <span v-if="forumRoleLabel(item.author.forum_role)" class="forum-role-badge">
            {{ forumRoleLabel(item.author.forum_role) }}
          </span>
          <span class="wall-meta-separator">·</span>
          <time :datetime="item.created_at">{{ formatRelativeTime(item.created_at) }}</time>
        </div>
        <div class="wall-card-stats" aria-label="帖子数据">
          <span title="浏览数">
            <svg viewBox="0 0 24 24"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></svg>
            {{ item.view_count ?? 0 }}
          </span>
          <span title="回答数">
            <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg>
            {{ item.answer_count }}
          </span>
          <span title="点赞数">
            <svg viewBox="0 0 24 24"><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3m0 11V11l4-9a3 3 0 0 1 3 3v4h5.3a2 2 0 0 1 2 2.3l-1.4 9A2 2 0 0 1 18 22Z"/></svg>
            {{ item.like_count }}
          </span>
        </div>
      </footer>
    </div>
  </article>
</template>
