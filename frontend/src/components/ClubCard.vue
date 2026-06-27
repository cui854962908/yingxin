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
</script>

<template>
  <div class="club-card" @click="emit('click')">
    <!-- ====== 顶部：装饰背景 + 团徽 + 标题 + 封面 ====== -->
    <div class="card-hero">
      <!-- 装饰层 -->
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
            {{ club.member_count ? club.member_count + ' 人' : '人数待定' }}
          </span>
        </div>
      </div>

      <!-- 封面图 — 右向左渐变，置于文字下方 -->
      <div v-if="club.hero_image || club.cover_image" class="card-cover">
        <img
          :src="club.hero_image || club.cover_image!"
          class="card-cover-img"
          @error="(e: Event) => ((e.target as HTMLImageElement).style.display = 'none')"
        />
      </div>

      <!-- 状态标签 -->
      <span
        class="card-status"
        :class="{ ended: club.status === '已结束', clickable: canEdit || isAdmin }"
        @click.stop="(canEdit || isAdmin) && onToggleStatus($event)"
      >
        <span class="card-status-dot" />
        {{ club.status }}
      </span>

      <!-- 状态下拉 -->
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

    <!-- ====== 底部：操作按钮 ====== -->
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

    <!-- 管理按钮（hover 出现） -->
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

<style scoped>
/* ==========================================
   卡片容器
   ========================================== */
.club-card {
  position: relative;
  width: 100%;
  min-height: 340px;
  background: linear-gradient(90deg, #FFF5EC 0%, #FFFDFB 50%, #FFFDFB 100%);
  border-radius: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #F3E7E2;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.33, 1, 0.68, 1), box-shadow 0.3s;
}

.club-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 44px rgba(0, 0, 0, 0.1);
}

/* ==========================================
   顶部 Hero 区
   ========================================== */
.card-hero {
  position: relative;
  height: 195px;
  overflow: hidden;
}

/* 暖色渐变底 */
.card-hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 500px 250px at 15% 70%, rgba(235, 215, 195, 0.45) 0%, transparent 65%),
    radial-gradient(ellipse 350px 200px at 85% 25%, rgba(250, 242, 235, 0.35) 0%, transparent 65%),
    linear-gradient(90deg, #F5E6D8 0%, #FBF3EB 35%, #FFF9F4 70%, #FFFDFB 100%);
  mask-image: linear-gradient(180deg, #000 0%, #000 85%, transparent 100%);
  -webkit-mask-image: linear-gradient(180deg, #000 0%, #000 85%, transparent 100%);
}

/* 装饰元素：虚线网格 + 光晕圆 */
.card-hero-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.18;
  background-image:
    /* 水平线 */
    repeating-linear-gradient(0deg, transparent, transparent 39px, #E8D5C0 39px, #E8D5C0 40px),
    /* 垂直线 */
    repeating-linear-gradient(90deg, transparent, transparent 39px, #E8D5C0 39px, #E8D5C0 40px);
  -webkit-mask-image: radial-gradient(ellipse 80% 60% at 50% 50%, black 30%, transparent 70%);
  mask-image: radial-gradient(ellipse 80% 60% at 50% 50%, black 30%, transparent 70%);
}

/* 团徽 — 左上，金色描边 + 立体阴影 */
.card-badge-ring {
  position: absolute;
  top: 28px;
  left: 28px;
  z-index: 3;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  padding: 4px;
  background: linear-gradient(135deg, #D4A853 0%, #F0D78C 30%, #C49B3C 70%, #A67C27 100%);
  box-shadow:
    0 4px 16px rgba(180, 140, 60, 0.3),
    0 2px 4px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-badge {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(145deg, #C0392B 0%, #A53125 40%, #8B1A1A 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.15);
}

.card-badge-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-badge-text {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  font-family: 'Georgia', 'Noto Serif SC', serif;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 标题区 */
.card-title-area {
  position: absolute;
  top: 32px;
  left: 124px;
  right: 28px;
  z-index: 2;
  min-width: 0;
}

.card-name {
  margin: 0 0 6px;
  font-size: 1.9rem;
  font-weight: 700;
  color: #3C2415;
  letter-spacing: 0.04em;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-subtitle {
  margin: 0 0 8px;
  font-size: 0.82rem;
  color: #8B7355;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-title-meta {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-title-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.84rem;
  font-weight: 500;
  color: #5C3D2E;
  white-space: nowrap;
}

.card-title-meta-item svg {
  color: #B5343A;
  flex-shrink: 0;
}

/* 封面图 — 满铺上半部，右向左渐变淡出 */
.card-cover {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  border-radius: 20px 20px 0 0;
  -webkit-mask-image: linear-gradient(270deg, #000 25%, transparent 80%);
  mask-image: linear-gradient(270deg, #000 25%, transparent 80%);
}

.card-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 状态胶囊标签 */
.card-status {
  position: absolute;
  top: 22px;
  right: 24px;
  z-index: 4;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 16px;
  border-radius: 20px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.96);
  color: #2E7D32;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(46, 125, 50, 0.15);
}

.card-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4CAF50;
  box-shadow: 0 0 6px rgba(76, 175, 80, 0.5);
}

.card-status.ended {
  color: #66BB6A;
  border-color: rgba(102, 187, 106, 0.2);
}

.card-status.ended .card-status-dot {
  background: #A5D6A7;
  box-shadow: 0 0 6px rgba(165, 214, 167, 0.4);
}

.card-status.clickable {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.card-status.clickable:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

/* 状态下拉 */
.card-status-drop {
  position: absolute;
  top: 56px;
  right: 24px;
  z-index: 10;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.14);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-status-drop button {
  padding: 8px 20px;
  border: none;
  background: #fff;
  font-size: 0.76rem;
  color: #3C2415;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: background 0.12s;
}

.card-status-drop button:hover {
  background: #FFF8F4;
}

.card-status-drop button.active {
  color: #2E7D32;
  font-weight: 600;
  background: #F1F8F2;
}

/* 下拉动画 */
.sd-enter-active { animation: sdIn 0.15s ease-out; }
.sd-leave-active { animation: sdOut 0.1s ease-in; }

@keyframes sdIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes sdOut {
  to { opacity: 0; transform: translateY(-6px); }
}

/* ==========================================
   中部信息区
   ========================================== */
.card-info {
  display: flex;
  gap: 10px;
  padding: 12px 24px 8px;
  flex-wrap: wrap;
}

.card-info-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #FFF9F4;
  border: 1px solid #F0E4D8;
  border-radius: 10px;
  transition: border-color 0.2s, background 0.2s;
}

.card-info-chip:hover {
  border-color: #D4B896;
  background: #FFF5EC;
}

.card-info-icon {
  color: #C49B3C;
  flex-shrink: 0;
}

.card-info-chip-label {
  font-size: 0.7rem;
  color: #A09181;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.card-info-chip-val {
  font-size: 0.78rem;
  color: #3C2415;
  font-weight: 600;
  white-space: nowrap;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ==========================================
   底部操作区
   ========================================== */
.card-actions {
  display: flex;
  gap: 12px;
  padding: 6px 24px 12px;
}

.card-btn-detail,
.card-btn-join {
  flex: 1;
  height: 48px;
  border-radius: 24px;
  font-size: 0.92rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.25s cubic-bezier(0.33, 1, 0.68, 1);
  position: relative;
  overflow: hidden;
}

/* 查看详情：白底描边 */
.card-btn-detail {
  background: #fff;
  border: 1.5px solid #E0D3C5;
  color: #5C4A3A;
}

.card-btn-detail:hover {
  border-color: #C49B3C;
  color: #3C2415;
  background: #FFFCF8;
  box-shadow: 0 2px 12px rgba(180, 140, 60, 0.12);
  transform: translateY(-1px);
}

/* 立即加入：红色渐变 */
.card-btn-join {
  border: none;
  color: #fff;
  background: linear-gradient(135deg, #C0392B 0%, #A53125 100%);
  box-shadow: 0 3px 12px rgba(192, 57, 43, 0.25);
}

.card-btn-join::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 50%);
  pointer-events: none;
}

.card-btn-join:hover {
  background: linear-gradient(135deg, #D44637 0%, #B5343A 100%);
  box-shadow: 0 6px 20px rgba(192, 57, 43, 0.35);
  transform: translateY(-1px);
}

.card-btn-detail:active,
.card-btn-join:active {
  transform: translateY(0);
}

/* ==========================================
   管理按钮（hover 出现，左上角）
   ========================================== */
.card-admin-actions {
  position: absolute;
  top: 14px;
  left: 14px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.25s;
  z-index: 10;
}

.club-card:hover .card-admin-actions {
  opacity: 1;
}

.card-admin-edit,
.card-admin-del {
  height: 30px;
  padding: 0 12px;
  border: none;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s;
}

.card-admin-edit {
  background: rgba(255, 255, 255, 0.85);
  color: #2E7D32;
  border: 1px solid rgba(46, 125, 50, 0.15);
}

.card-admin-edit:hover {
  background: #fff;
  border-color: #2E7D32;
}

.card-admin-del {
  background: rgba(255, 255, 255, 0.85);
  color: #B5343A;
  border: 1px solid rgba(181, 52, 58, 0.15);
}

.card-admin-del:hover {
  background: #fff;
  border-color: #B5343A;
}

/* ==========================================
   加入弹窗
   ========================================== */
.join-overlay {
  position: fixed; inset: 0; z-index: 5000;
  background: rgba(0,0,0,.52); display: flex;
  align-items: center; justify-content: center;
}
.join-modal {
  position: relative; width: 360px; max-width: 90vw;
  background: #fff; border-radius: 20px; padding: 32px 28px 24px;
  box-shadow: 0 16px 48px rgba(0,0,0,.18);
}
.join-modal-close {
  position: absolute; top: 14px; right: 14px;
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: #f5f0eb; color: #8b7b65; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.join-modal-close:hover { background: #e8e0d5 }
.join-modal-title { margin: 0 0 20px; font-size: 1.1rem; font-weight: 700; color: #3C2415; text-align: center; letter-spacing: .04em }
.join-modal-empty { text-align: center; color: #b0a090 }
.join-modal-empty p { margin: 0 0 4px; font-size: .88rem }
.join-modal-empty-hint { font-size: .76rem !important; color: #c4b8a4 }
.join-modal-row { margin-bottom: 18px }
.join-modal-row:last-child { margin-bottom: 0 }
.join-modal-label { display: block; font-size: .78rem; color: #8b7b65; margin-bottom: 8px; font-weight: 500 }
.join-modal-qq { display: flex; align-items: center; gap: 10px }
.join-modal-qq-num { flex: 1; padding: 10px 14px; background: #faf6f0; border-radius: 10px; font-size: 1.05rem; font-weight: 700; color: #3C2415; letter-spacing: .06em; text-align: center; font-family: inherit }
.join-modal-copy { height: 38px; padding: 0 16px; border: none; border-radius: 10px; background: #4a8c5c; color: #fff; font-size: .8rem; font-weight: 600; cursor: pointer; font-family: inherit; white-space: nowrap; transition: opacity .15s }
.join-modal-copy:hover { opacity: .85 }
.join-modal-qr { display: block; width: 200px; height: 200px; margin: 0 auto; object-fit: contain; border-radius: 12px; border: 1px solid #f0e4d8 }

.join-modal-enter-active { animation: jmIn .25s ease-out }
.join-modal-leave-active { animation: jmOut .18s ease-in }
@keyframes jmIn { from { opacity:0; transform:scale(.95) } to { opacity:1; transform:scale(1) } }
@keyframes jmOut { to { opacity:0; transform:scale(.95) } }

/* ==========================================
   响应式
   ========================================== */
@media (max-width: 1100px) {
  .card-title-area {
    right: 24px;
  }

  .card-name {
    font-size: 1.5rem;
  }

  .card-subtitle {
    font-size: 0.76rem;
  }
}

@media (max-width: 768px) {
  .card-hero-decor { display: none }

  .card-hero {
    height: 200px;
  }

  .card-badge-ring {
    top: 20px;
    left: 20px;
    width: 64px;
    height: 64px;
    padding: 3px;
  }

  .card-badge-text {
    font-size: 1.5rem;
  }

  .card-title-area {
    top: 24px;
    left: 96px;
    right: 20px;
  }

  .card-name {
    font-size: 1.35rem;
  }

  .card-subtitle {
    font-size: 0.7rem;
    -webkit-line-clamp: 1;
  }

  .card-title-meta-item {
    font-size: 0.68rem;
  }

  .card-status {
    top: 18px;
    right: 16px;
    font-size: 0.68rem;
    padding: 4px 12px;
  }

  .card-info {
    padding: 12px 16px 8px;
    gap: 6px;
  }

  .card-info-chip {
    padding: 5px 10px;
    gap: 4px;
  }

  .card-info-chip-label {
    font-size: 0.64rem;
  }

  .card-info-chip-val {
    font-size: 0.7rem;
    max-width: 70px;
  }

  .card-actions {
    padding: 6px 16px 20px;
    gap: 10px;
  }

  .card-btn-detail,
  .card-btn-join {
    height: 42px;
    font-size: 0.82rem;
    border-radius: 21px;
  }

  .card-status-drop {
    top: 48px;
    right: 16px;
  }
}

@media (max-width: 480px) {
  .club-card {
    min-height: 260px;
  }

  .card-hero {
    height: 160px;
  }

  .card-badge-ring {
    top: 14px;
    left: 14px;
    width: 56px;
    height: 56px;
    padding: 3px;
  }

  .card-badge-text {
    font-size: 1.3rem;
  }

  .card-title-area {
    top: 14px;
    left: 82px;
    right: 14px;
  }

  .card-name {
    font-size: 1.2rem;
  }

  .card-subtitle {
    display: none;
  }

  .card-title-meta-item {
    font-size: 0.72rem;
    gap: 3px;
  }

  .card-title-meta-item svg {
    width: 12px;
    height: 12px;
  }

  .card-status {
    top: 12px;
    right: 8px;
    font-size: 0.6rem;
    padding: 2px 8px;
    gap: 3px;
  }

  .card-status-dot {
    width: 5px;
    height: 5px;
  }

  .card-info {
    padding: 8px 12px 4px;
    gap: 4px;
  }

  .card-info-chip {
    padding: 3px 8px;
    gap: 3px;
    border-radius: 6px;
  }

  .card-info-icon {
    width: 11px;
    height: 11px;
  }

  .card-info-chip-label {
    font-size: 0.58rem;
  }

  .card-info-chip-val {
    font-size: 0.64rem;
    max-width: 50px;
  }

  .card-actions {
    padding: 4px 12px 12px;
    gap: 8px;
  }

  .card-btn-detail,
  .card-btn-join {
    height: 36px;
    font-size: 0.76rem;
    border-radius: 18px;
  }
}
</style>
