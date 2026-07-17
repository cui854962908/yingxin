<script setup lang="ts">
import LoginForm from './LoginForm.vue'
import {
  GUEST_ENTRY_LABEL,
  PASSWORD_RECOVERY,
  PASSWORD_RECOVERY_HINT,
  PRODUCT_TAGLINE,
} from '../constants/product'

const emit = defineEmits<{
  'login-success': [student: Record<string, any>, token: string, refreshToken?: string]
  'guest-enter': []
}>()
import '../styles/pages/login-page.css'
</script>

<template>
  <div class="page login-shell">
    <!-- 左：品牌面板 -->
    <aside class="brand-panel">
      <!-- 背景水印：欢左迎�?-->
      <picture>
        <source srcset="/dengluzuo.webp" type="image/webp" />
        <img src="/dengluzuo.png" alt="" class="brand-bg" decoding="async" />
      </picture>
      <div class="brand-inner">
        <div class="logo-wrap">
          <img src="/logo-1.webp" alt="校徽" class="logo" decoding="async" />
        </div>
        <h1 class="school-name">河南牧业经济学院</h1>
        <p class="motto">
          <span class="motto-bracket">「</span>
          尚严崇实 · 善知敏行
          <span class="motto-bracket">」</span>
        </p>
        <div class="brand-rule">
          <span class="brand-rule-dot">◆</span>
        </div>
        <p class="year-badge">2026</p>
        <p class="brand-sub">迎新 · 启程</p>
        <p class="brand-tagline">{{ PRODUCT_TAGLINE }}</p>
      </div>
    </aside>

    <!-- 右：表单区域 -->
    <main class="form-panel">
      <!-- 背景网格纹理 -->
      <div class="grid-texture" />

      <picture>
        <source srcset="/dengluyou3.webp" type="image/webp" />
        <img src="/dengluyou3.png" alt="" class="form-watermark" decoding="async" />
      </picture>

      <!-- 底部大号水印 -->
      <span class="watermark">2026</span>

      <div class="form-inner">
        <p class="form-eyebrow">NEW STUDENT · PASSWORD LOGIN</p>
        <h2 class="form-heading">新生登录</h2>
        <div class="heading-rule" />

        <LoginForm @login-success="(s, t, rt) => emit('login-success', s, t, rt)" />

        <p class="password-recovery">
          {{ PASSWORD_RECOVERY_HINT }}
          <a
            :href="`mailto:${PASSWORD_RECOVERY.contactEmail}`"
            class="password-recovery-phone"
          >{{ PASSWORD_RECOVERY.contactEmail }}</a>
        </p>

        <div class="guest-divider"><span>或</span></div>
        <button type="button" class="guest-btn" @click="emit('guest-enter')">
          {{ GUEST_ENTRY_LABEL }}
        </button>

        <p class="footer-tip">已录取新生：姓名 · 学号 · 密码登录；初始密码为 01234567，登录后请尽快修改</p>
      </div>
    </main>
  </div>
</template>
