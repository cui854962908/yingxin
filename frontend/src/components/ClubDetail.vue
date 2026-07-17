<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import AppSpinner from './AppSpinner.vue'
import ClubDetailGallery from './ClubDetailGallery.vue'
import { useClubDetail } from '../composables/useClubDetail'
import { useBreakpoint } from '../composables/useBreakpoint'
import '../styles/club-detail-editor.css'
import '../styles/components/club-detail.css'

const {
  isNew, club, loading, editing, saving, uploadMsg, activeTab, editForm, isAdmin,
  parseLeaders, formatRecruitCount, activityPhotosValue, goBack, canEdit, enterEdit,
  cancelEdit, saveEdit, uploadAndSet, uploadPhoto, removePhoto, uploadQr, backLabel,
  joinModal, joinCopyOk, openJoinModal, closeJoinModal, copyJoinQQ,
} = useClubDetail()
const { isMobile } = useBreakpoint()
const showHeroToolbar = computed(() => {
  if (editing.value) return true
  if (isNew) return false
  return canEdit() || isAdmin.value
})
/** 横幅图：优先 hero，无则用 logo，保证移动端封面区高度一致 */
const heroBannerSrc = computed(() => {
  if (editing.value && editForm.hero_image) return editForm.hero_image
  const c = club.value
  if (c?.hero_image) return c.hero_image
  if (c?.cover_image) return c.cover_image
  return ''
})
</script>

<template>
  <div v-if="loading" class="cd-loading"><AppSpinner :color="'#4a8c5c'" /></div>

  <div v-else-if="club || isNew" class="club-detail" :class="{ 'club-detail--editing': editing }" style="--tc: #4a8c5c; --tcl: #e8f5e9">
    <!-- Hero Banner -->
    <div class="cd-hero-wrapper">
      <div class="cd-hero" :class="{ 'cd-hero--no-toolbar': !showHeroToolbar, 'cd-hero--no-banner': !heroBannerSrc }">
        <div class="cd-hero-cover">
          <img v-if="heroBannerSrc" :src="heroBannerSrc" class="cd-hero-bg"
            @error="($event.target as HTMLImageElement).style.display='none'" />
          <div class="cd-hero-gradient" />
        </div>
        <button type="button" class="cd-back" :aria-label="backLabel" @click="goBack">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          <span class="cd-back__text">{{ isMobile ? '返回' : backLabel }}</span>
        </button>

        <div v-if="showHeroToolbar" class="cd-hero-actions">
          <template v-if="editing">
            <button class="cd-tag cd-tag-save" :disabled="saving" @click="saveEdit">{{ saving ? '保存中…' : (isNew ? '添加' : '保存') }}</button>
            <button class="cd-tag cd-tag-cancel" @click="cancelEdit">取消</button>
          </template>
          <template v-else>
            <button v-if="canEdit() || isAdmin" class="cd-tag cd-tag-edit" @click="enterEdit">编辑</button>
          </template>
          <select v-if="editing" v-model="editForm.status" class="cd-tag cd-tag-status-select">
            <option value="招新中">招新中</option>
            <option value="已结束">已结束</option>
          </select>
        </div>

        <div class="cd-hero-content">
          <div class="cd-hero-badge-ring">
            <div class="cd-hero-badge">
              <img v-if="(editing && editForm.cover_image) || club?.cover_image"
                :src="(editing && editForm.cover_image) || club?.cover_image!" class="cd-hero-badge-img"
                @error="($event.target as HTMLImageElement).style.display='none'" />
              <span v-else class="cd-hero-badge-text">{{ (club?.name || '社').charAt(0) }}</span>
            </div>
            <label v-if="editing" class="cd-badge-upload">
              <input type="file" accept="image/*" @change="uploadAndSet('cover_image', $event)" />
            </label>
          </div>
          <div class="cd-hero-info">
            <template v-if="editing">
              <input v-model="editForm.name" class="cd-hero-name-input" placeholder="社团名称" />
              <input v-model="editForm.intro" class="cd-hero-intro-input" placeholder="一句话简介" maxlength="300" />
              <select v-model="editForm.category" class="cd-hero-cat-select">
                <option value="信工团学会">信工团学会</option>
                <option value="校级组织">校级组织</option>
                <option value="兴趣社团">兴趣社团</option>
              </select>
            </template>
            <template v-else>
              <h1 class="cd-hero-name">{{ club?.name || '新社团' }}</h1>
              <p v-if="club?.intro || isNew" class="cd-hero-intro">{{ club?.intro || '请填写社团简介' }}</p>
              <div class="cd-hero-badges">
                <span class="cd-tag cd-tag-category">{{ club?.category || '兴趣社团' }}</span>
                <span class="cd-tag cd-tag-status" :class="{ ended: club?.status === '已结束' }">{{ club?.status || '招新中' }}</span>
              </div>
            </template>
          </div>
        </div>

        <label v-if="editing" class="cd-hero-bg-upload">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          更换背景
          <input type="file" accept="image/*" @change="uploadAndSet('hero_image', $event)" />
        </label>
        <span v-if="uploadMsg" class="cd-upload-toast" :class="{ ok: uploadMsg === '上传成功' || uploadMsg === '保存成功' }">{{ uploadMsg }}</span>

        <div class="cd-hero-meta">
          <template v-if="editing">
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成立年份</span>
              <input v-model.number="editForm.founded_year" type="number" class="cd-meta-input" placeholder="如 2018" />
            </div>
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">指导老师</span>
              <input v-model="editForm.advisor_name" class="cd-meta-input" placeholder="姓名" />
            </div>
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成员人数</span>
              <input v-model.number="editForm.member_count" type="number" class="cd-meta-input" placeholder="人数" />
            </div>
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">负责人</span>
              <input v-model="editForm.leader_name" class="cd-meta-input" placeholder="姓名" />
            </div>
          </template>
          <template v-else>
            <div v-if="club?.founded_year" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成立</span>
              <span class="cd-hero-meta-value">{{ club.founded_year }}</span>
            </div>
            <div v-if="club?.advisor_name" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">指导老师</span>
              <span class="cd-hero-meta-value">{{ club.advisor_name }}</span>
            </div>
            <div v-if="club?.member_count" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成员</span>
              <span class="cd-hero-meta-value">{{ club.member_count }} 人</span>
            </div>
            <div v-if="club && parseLeaders(club.leaders).length > 0" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">负责人</span>
              <span class="cd-hero-meta-value">{{ parseLeaders(club.leaders)[0].name }}</span>
            </div>
            <div v-else-if="club?.leader_name" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">负责人</span>
              <span class="cd-hero-meta-value">{{ club.leader_name }}</span>
            </div>
            <div v-if="isNew" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">新建社团</span>
              <span class="cd-hero-meta-value">编辑中…</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="cd-tabs">
      <button
        class="cd-tab-btn"
        :class="{ active: activeTab === 'info' }"
        @click="activeTab = 'info'"
      >基本信息</button>
      <button
        class="cd-tab-btn"
        :class="{ active: activeTab === 'gallery' }"
        @click="activeTab = 'gallery'"
      >风采展示</button>
    </div>

    <!-- 主内容区 -->
    <div class="cd-main">
      <template v-if="activeTab === 'info'">
        <div class="cd-section cd-section--intro">
          <h3 class="cd-section-title">
            <span class="cd-section-icon-wrap"><span class="cd-section-icon-inner">
              <svg width="20" height="20" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M232,48H160a40,40,0,0,0-32,16A40,40,0,0,0,96,48H24a8,8,0,0,0-8,8V200a8,8,0,0,0,8,8H96a24,24,0,0,1,24,24,8,8,0,0,0,16,0,24,24,0,0,1,24-24h72a8,8,0,0,0,8-8V56A8,8,0,0,0,232,48ZM96,192H32V64H96a24,24,0,0,1,24,24V200A39.81,39.81,0,0,0,96,192Zm128,0H160a39.81,39.81,0,0,0-24,8V88a24,24,0,0,1,24-24h64ZM160,88h40a8,8,0,0,1,0,16H160a8,8,0,0,1,0-16Zm48,40a8,8,0,0,1-8,8H160a8,8,0,0,1,0-16h40A8,8,0,0,1,208,128Zm0,32a8,8,0,0,1-8,8H160a8,8,0,0,1,0-16h40A8,8,0,0,1,208,160Z"/></svg>
            </span></span>
            <span class="cd-section-bar" style="background: #4a8c5c" />
            社团介绍
          </h3>
          <div v-if="!editing && club?.description" class="cd-desc-body" v-html="DOMPurify.sanitize(club!.description!)" />
          <textarea v-else-if="editing" v-model="editForm.description" class="cd-edit-textarea" rows="8" placeholder="社团详细介绍（支持HTML）" />
          <div v-else class="cd-desc-body" style="color:#b0a090">暂无介绍</div>
        </div>

        <!-- 招新信息 + 社团荣誉 -->
        <div class="cd-cards-row">
          <div class="cd-info-card cd-info-card--recruit">
            <div class="cd-info-card-head">
              <span class="cd-section-icon-wrap cd-section-icon-sm"><span class="cd-section-icon-inner">
                <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M238.73,43.67A8,8,0,0,0,232,40H152a8,8,0,0,0-7.28,4.69L135.94,64H28a8,8,0,0,0-5.92,13.38L57.19,116,22.08,154.62A8,8,0,0,0,28,168h73.09a8,8,0,0,0,7.28-4.69L117.15,144h62.43l-34.86,76.69a8,8,0,1,0,14.56,6.62l80-176A8,8,0,0,0,238.73,43.67ZM95.94,152H46.08l27.84-30.62a8,8,0,0,0,0-10.76L46.08,80h82.59Zm90.91-24H124.42l32.73-72h62.43Z"/></svg>
              </span></span>
              <span>招新信息</span>
            </div>
            <div class="cd-recruit-split">
              <div class="cd-recruit-left">
                <div class="cd-info-row">
                  <span class="cd-info-label">招新对象</span>
                  <input v-if="editing" v-model="editForm.recruit_target" class="cd-edit-input" />
                  <span v-else class="cd-info-val">{{ club?.recruit_target || '待定' }}</span>
                </div>
                <div class="cd-info-row">
                  <span class="cd-info-label">招新时间</span>
                  <template v-if="editing">
                    <div class="cd-edit-dates">
                      <input v-model="editForm.recruit_start" type="date" class="cd-edit-input" />
                      <span>至</span>
                      <input v-model="editForm.recruit_end" type="date" class="cd-edit-input" />
                    </div>
                  </template>
                  <span v-else class="cd-info-val">{{ club?.recruit_start || '待定' }} 至 {{ club?.recruit_end || '待定' }}</span>
                </div>
                <div class="cd-info-row">
                  <span class="cd-info-label">招新人数</span>
                  <input v-if="editing" v-model="editForm.recruit_count" class="cd-edit-input" placeholder="人数" />
                  <span v-else class="cd-info-val">{{ formatRecruitCount(club?.recruit_count) }}</span>
                </div>
                <div class="cd-info-row">
                  <span class="cd-info-label">招新要求</span>
                  <input v-if="editing" v-model="editForm.recruit_require" class="cd-edit-input" />
                  <span v-else class="cd-info-val">{{ club?.recruit_require || '暂无' }}</span>
                </div>
              </div>
              <div class="cd-recruit-right">
                <p class="cd-join-title">期待你的加入</p>
                <p class="cd-join-desc">一起用双手创建美好校园吧！</p>
                <button class="cd-join-btn" @click="openJoinModal">如何加入</button>
              </div>
            </div>
          </div>

          <div class="cd-info-card cd-info-card--honor">
            <div class="cd-info-card-head">
              <span class="cd-section-icon-wrap cd-section-icon-sm"><span class="cd-section-icon-inner">
                <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M232,64H208V48a8,8,0,0,0-8-8H56a8,8,0,0,0-8,8V64H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-29,64.64-64,64.9a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"/></svg>
              </span></span>
              <span>社团荣誉</span>
            </div>
            <div class="cd-info-card-body cd-honor-body">
              <p v-if="!editing && !club?.honor" class="cd-info-empty">暂无荣誉记录</p>
              <div v-else-if="!editing && club?.honor" class="cd-honor-text" v-html="DOMPurify.sanitize(club!.honor!)" />
              <textarea v-else v-model="editForm.honor" class="cd-edit-textarea cd-edit-textarea--sm" rows="4" placeholder="社团荣誉与成就…" />
            </div>
          </div>

          <!-- 报名方式编辑（仅编辑模式） -->
          <div v-if="editing" class="cd-info-card cd-info-card--contact">
            <div class="cd-info-card-head">
              <span class="cd-section-icon-wrap cd-section-icon-sm"><span class="cd-section-icon-inner">
                <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm40-68a28,28,0,0,1-28,28h-4a8,8,0,0,1-8-8v-4a28,28,0,0,1,28-28h4a12,12,0,0,0,0-24h-24a8,8,0,0,1,0-16h24a28,28,0,0,1,28,28A28,28,0,0,1,168,148Zm-64-8a8,8,0,0,1-8,8H92v12a8,8,0,0,1-16,0v-20a8,8,0,0,1,8-8h8a4,4,0,0,0,0-8H88a8,8,0,0,1,0-16h4a20,20,0,0,1,0,40Z"/></svg>
              </span></span>
              <span>报名方式</span>
            </div>
            <div class="cd-contact-edit">
              <div class="cd-info-row">
                <span class="cd-info-label">QQ群号</span>
                <input v-model="editForm.qq_group" class="cd-edit-input" placeholder="如 123456789" />
              </div>
              <div class="cd-info-row">
                <span class="cd-info-label">QQ群二维码</span>
                <div class="cd-qr-edit">
                  <img v-if="editForm.wechat_qr" :src="editForm.wechat_qr" class="cd-qr-preview" />
                  <label class="cd-qr-upload-btn">
                    {{ editForm.wechat_qr ? '更换二维码' : '上传二维码' }}
                    <input type="file" accept="image/*" @change="uploadQr($event)" />
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'gallery'">
        <ClubDetailGallery
          :activity-photos="activityPhotosValue()"
          :editing="editing"
          @upload-photo="uploadPhoto"
          @remove-photo="removePhoto"
        />
      </template>
    </div>

    <!-- 加入弹窗 -->
    <Teleport to="body">
      <Transition name="join-modal">
        <div v-if="joinModal" class="cd-join-overlay" @click="closeJoinModal">
          <div class="cd-join-modal" @click.stop>
            <button class="cd-join-close" @click="closeJoinModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
            <h3 class="cd-join-title-text">加入 {{ club?.name }}</h3>
            <div v-if="!club?.qq_group && !club?.wechat_qr" class="cd-join-empty">
              <p>暂未开放报名方式</p>
              <p class="cd-join-empty-hint">请联系社团负责人获取入群信息</p>
            </div>
            <template v-else>
              <div v-if="club?.qq_group" class="cd-join-row">
                <span class="cd-join-label">QQ群号</span>
                <div class="cd-join-qq">
                  <code class="cd-join-qq-num">{{ club.qq_group }}</code>
                  <button class="cd-join-copy" @click="copyJoinQQ">{{ joinCopyOk ? '已复制 ✓' : '复制' }}</button>
                </div>
              </div>
              <div v-if="club?.wechat_qr" class="cd-join-row">
                <span class="cd-join-label">QQ群二维码</span>
                <img :src="club.wechat_qr" class="cd-join-qr" alt="QQ群二维码" />
              </div>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
