<script setup lang="ts">
import { ref } from 'vue'
import type { Club } from '../types/club'

const props = defineProps<{
  club: Club
  canEdit: boolean
  isAdmin: boolean
  statusMenuOpen: boolean
}>()

const emit = defineEmits<{
  click: []
  edit: []
  delete: []
  'update:statusMenuOpen': [value: boolean]
  'status-change': [status: string]
}>()

function parseLeaders(): { name: string; phone: string }[] {
  if (!props.club.leaders) return []
  try { return JSON.parse(props.club.leaders) } catch { return [] }
}

function onToggleStatus(e: Event) {
  e.stopPropagation()
  emit('update:statusMenuOpen', !props.statusMenuOpen)
}

function onSetStatus(status: string) {
  emit('status-change', status)
}

// 加入弹窗
const joinOpen = ref(false)
const copyOk = ref(false)

function openJoin(e: Event) {
  e.stopPropagation()
  joinOpen.value = true
}
function closeJoin() { joinOpen.value = false; copyOk.value = false }

async function copyQQ() {
  try {
    await navigator.clipboard.writeText(props.club.qq_group || '')
    copyOk.value = true
    setTimeout(() => { copyOk.value = false }, 2000)
  } catch { /* ignore */ }
}
import '../styles/components/club-card.css'
</script>

<template>
  <div class="club-card" @click="emit('click')">
    <!-- ====== 顶部：装饰背�?+ 团徽 + 标题 + 封面 ====== -->
    <div class="card-hero">
      <!-- 装饰�?-->
      <div class="card-hero-bg" />
      <div class="card-hero-decor" />

      <!-- 团徽 -->
      <div class="card-badge-ring">
        <div class="card-badge">
          <img
            v-if="club.cover_image"
            :src="club.cover_image"
            class="card-badge-img"
            @error="(e: Event) => ((e.target as HTMLImageElement).style.display = 'none')"
          />
          <span v-else class="card-badge-text">{{ club.name.charAt(0) }}</span>
        </div>
      </div>

      <!-- 标题信息 -->
      <div class="card-title-area">
        <h3 class="card-name">{{ club.name }}</h3>
        <p class="card-subtitle">{{ club.intro }}</p>
        <div class="card-title-meta">
          <span class="card-title-meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M5.3 18.3C6.8 16.5 9.2 15.3 12 15.3s5.2 1.2 6.7 3"/></svg>
            指导老师：{{ club.advisor_name || '暂无' }}
          </span>
          <span class="card-title-meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/></svg>
            {{ club.member_count ? `${club.member_count} 人` : '人数待定' }}
          </span>
        </div>
      </div>

      <!-- 封面�?�?右向左渐变，置于文字下方 -->
      <div v-if="club.hero_image || club.cover_image" class="card-cover">
        <img
          :src="club.hero_image || club.cover_image!"
          class="card-cover-img"
          @error="(e: Event) => ((e.target as HTMLImageElement).style.display = 'none')"
        />
      </div>

      <!-- 状态标�?-->
      <span
        class="card-status"
        :class="{ ended: club.status === '已结束', clickable: canEdit || isAdmin }"
        @click.stop="(canEdit || isAdmin) && onToggleStatus($event)"
      >
        <span class="card-status-dot" />
        {{ club.status }}
      </span>

      <!-- 状态下�?-->
      <Transition name="sd">
        <div v-if="statusMenuOpen" class="card-status-drop" @click.stop>
          <button
            :class="{ active: club.status === '招新中' }"
            @click="onSetStatus('招新中')"
          >招新中</button>
          <button
            :class="{ active: club.status === '已结束' }"
            @click="onSetStatus('已结束')"
          >已结束</button>
        </div>
      </Transition>
    </div>

    <!-- ====== 中部：信息卡片区 ====== -->
    <div class="card-info">
      <div class="card-info-chip">
        <svg class="card-info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        <span class="card-info-chip-label">成立</span>
        <span class="card-info-chip-val">{{ club.founded_year || '--' }}</span>
      </div>
      <div class="card-info-chip">
        <svg class="card-info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
        <span class="card-info-chip-label">类别</span>
        <span class="card-info-chip-val">{{ club.category }}</span>
      </div>
      <div class="card-info-chip">
        <svg class="card-info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span class="card-info-chip-label">招新</span>
        <span class="card-info-chip-val">{{ club.recruit_start || '待定' }}</span>
      </div>
    </div>

    <!-- ====== 底部：操作按�?====== -->
    <div class="card-actions">
      <button class="card-btn-detail" @click.stop="emit('click')">查看详情</button>
      <button class="card-btn-join" @click.stop="openJoin($event)">如何加入</button>
    </div>

    <!-- 加入弹窗 -->
    <Teleport to="body">
      <Transition name="join-modal">
        <div v-if="joinOpen" class="join-overlay" @click="closeJoin">
          <div class="join-modal" @click.stop>
            <button class="join-modal-close" @click="closeJoin">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
            <h3 class="join-modal-title">加入 {{ club.name }}</h3>
            <div v-if="!club.qq_group && !club.wechat_qr" class="join-modal-empty">
              <p>暂未开放报名方式</p>
              <p class="join-modal-empty-hint">请联系社团负责人获取入群信息</p>
            </div>
            <template v-else>
              <div v-if="club.qq_group" class="join-modal-row">
                <span class="join-modal-label">QQ群号</span>
                <div class="join-modal-qq">
                  <code class="join-modal-qq-num">{{ club.qq_group }}</code>
                  <button class="join-modal-copy" @click="copyQQ">{{ copyOk ? '已复制 ✓' : '复制' }}</button>
                </div>
              </div>
              <div v-if="club.wechat_qr" class="join-modal-row">
                <span class="join-modal-label">QQ群二维码</span>
                <img :src="club.wechat_qr" class="join-modal-qr" alt="QQ群二维码" />
              </div>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 管理按钮（hover 出现�?-->
    <div v-if="canEdit || isAdmin" class="card-admin-actions" @click.stop>
      <button v-if="canEdit" class="card-admin-edit" @click="emit('edit')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        编辑
      </button>
      <button v-if="isAdmin" class="card-admin-del" @click="emit('delete')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
        删除
      </button>
    </div>
  </div>
</template>
