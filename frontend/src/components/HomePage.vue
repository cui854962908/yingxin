<script setup lang="ts">
import { ref, inject, computed, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProfileCard from './ProfileCard.vue'

import type { Student } from '../types/student'

const studentRef = inject<Ref<Student>>('student')
if (!studentRef) {
  console.error('[HomePage] student 未通过 provide 注入，请检查父组件')
  throw new Error('学生登录信息未初始化，请重新登录')
}
const student = computed(() => studentRef.value)
const logout = inject<() => void>('logout')
if (!logout) {
  throw new Error('[HomePage] logout 未通过 provide 注入，请检查父组件')
}
const route = useRoute()
const isAdmin = computed(() => student.value.role === 'admin')
const mobileNavOpen = ref(false)

const navItems = [
  { to: '/', label: '首页', key: 'home' },
  { to: '/announcements', label: '校园公告', key: 'notices' },
  { to: '/faq', label: '问题答疑', key: 'faq' },
  ...(isAdmin ? [{ to: '/admin', label: '学生管理', key: 'admin' }] : []),
]

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}

function closeNav() { mobileNavOpen.value = false }
</script>

<template>
  <div class="dashboard">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <div class="sb-logo-wrap">
          <img src="/logo-1.png" alt="校徽" class="sb-logo" />
        </div>
        <p class="sb-school">河南牧业经济学院</p>
        <div class="sb-rule" />
        <div class="sb-avatar">{{ student.name.charAt(0) }}</div>
        <p class="sb-name">{{ student.name }}</p>
        <span class="sb-role" :class="{ 'sb-role--admin': isAdmin }">
          {{ isAdmin ? '管理员' : '2026 级新生' }}
        </span>
      </div>

      <!-- 桌面导航 -->
      <nav class="sb-nav">
        <router-link v-for="item in navItems" :key="item.key"
          :to="item.to"
          class="sb-nav-item" :class="[`sb-nav-${item.key}`, { active: isActive(item.to) }]"
          @click="closeNav">
          <span class="sb-nav-icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <a class="sb-logout" @click="logout">退出登录</a>

      <!-- 手机汉堡菜单 -->
      <button class="sb-hamburger" @click="mobileNavOpen = !mobileNavOpen">
        <span :class="{ 'sb-ham-bar--open': mobileNavOpen }" />
      </button>
    </aside>

    <!-- 手机下拉导航 -->
    <Transition name="mobile-nav">
      <nav v-if="mobileNavOpen" class="sb-mobile-nav">
        <router-link v-for="item in navItems" :key="item.key"
          :to="item.to"
          class="sb-nav-item" :class="[`sb-nav-${item.key}`, { active: isActive(item.to) }]"
          @click="closeNav">
          <span class="sb-nav-icon" />
          <span>{{ item.label }}</span>
        </router-link>
        <a class="sb-nav-item sb-nav-logout-mobile" @click="logout">退出登录</a>
      </nav>
    </Transition>

    <!-- 右侧内容 -->
    <main class="main">
      <section class="profile-section">
        <ProfileCard />
      </section>

      <section class="bottom-section">
        <div class="section-card">
          <Transition name="module" mode="out-in">
            <router-view :key="route.fullPath" />
          </Transition>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* 布局 */
.dashboard { display: flex; height: 100vh; background: #f5efe5 }

/* 侧边栏 */
.sidebar {
  flex: 0 0 240px; height: 100vh; position: sticky; top: 0;
  background: linear-gradient(170deg, #3d1114 0%, #591a1e 30%, #4a1519 60%, #361012 100%);
  display: flex; flex-direction: column; align-items: flex-start;
  padding: 32px 20px 20px; overflow: hidden;
}
.sidebar::after {
  content: '欢迎'; position: absolute; font-size: 14rem; font-weight: 900;
  color: rgba(255,255,255,.012); pointer-events: none; line-height: 1;
  top: 50%; left: 50%; transform: translate(-50%,-50%); font-family: 'Noto Serif SC', serif;
}
.sidebar-top { text-align: left; position: relative; z-index: 1; width: 100% }
.sb-logo-wrap {
  width: 56px; height: 56px; border-radius: 50%; padding: 2px;
  background: linear-gradient(135deg, #c9a96e, #e8d5a8, #c9a96e);
}
.sb-logo { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; background: transparent; display: block }
.sb-school { font-size: .75rem; color: rgba(242,230,208,.55); margin-top: 8px; letter-spacing: .03em }
.sb-rule { width: 30px; height: 1px; background: linear-gradient(90deg, rgba(201,169,110,.3), transparent); margin: 14px 0 }
.sb-avatar {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #c9a96e, #d4b87a); color: #3d1114;
  font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; justify-content: center;
  font-family: 'Noto Serif SC', serif;
}
.sb-name { font-size: 1rem; color: #f2e6d0; font-weight: 600; margin-top: 8px; letter-spacing: .04em }
.sb-role { display: inline-block; margin-top: 4px; font-size: .68rem; padding: 2px 12px; border-radius: 8px; color: #c4a87e; border: 1px solid rgba(201,169,110,.25) }
.sb-role--admin { color: #e8d5a8; border-color: rgba(232,213,168,.4) }

.sb-nav { flex: 1; width: 100%; margin-top: 28px; position: relative; z-index: 1 }
.sb-nav-item {
  display: flex; align-items: center; gap: 10px; padding: 10px 16px;
  border-radius: 8px; font-size: .94rem; color: rgba(242,230,208,.5);
  cursor: pointer; transition: all .2s; margin-bottom: 2px;
  font-style: italic; font-family: 'Georgia', 'Noto Serif SC', 'KaiTi', serif;
  text-decoration: none;
}
.sb-nav-item:hover { color: rgba(242,230,208,.8); background: rgba(255,255,255,.04) }
.sb-nav-item.active { color: #f2e6d0; background: rgba(255,255,255,.08); font-weight: 500 }
.sb-nav-icon{width:6px;height:6px;border-radius:50%;display:block;flex-shrink:0;transition:all .25s}
.sb-nav-home .sb-nav-icon{background:rgba(201,169,110,.5)}
.sb-nav-home.active .sb-nav-icon{background:#e8d5a8;box-shadow:0 0 8px rgba(232,213,168,.5)}
.sb-nav-notices .sb-nav-icon{background:rgba(180,160,140,.5)}
.sb-nav-notices.active .sb-nav-icon{background:#d4c0a8;box-shadow:0 0 8px rgba(212,192,168,.5)}
.sb-nav-faq .sb-nav-icon{background:rgba(160,180,190,.5)}
.sb-nav-faq.active .sb-nav-icon{background:#c0d8e8;box-shadow:0 0 8px rgba(192,216,232,.5)}
.sb-nav-admin .sb-nav-icon{background:rgba(170,150,180,.5)}
.sb-nav-admin.active .sb-nav-icon{background:#d0c0e0;box-shadow:0 0 8px rgba(208,192,224,.5)}
.sb-logout { position: relative; z-index: 1; font-size: .75rem; color: rgba(242,230,208,.3); cursor: pointer; transition: color .2s }
.sb-logout:hover { color: rgba(242,230,208,.6) }

/* 汉堡按钮 */
.sb-hamburger{display:none;position:relative;z-index:60;width:32px;height:32px;background:none;border:none;cursor:pointer;flex-shrink:0;padding:0}
.sb-hamburger span,.sb-hamburger span::before,.sb-hamburger span::after{display:block;position:absolute;left:4px;width:24px;height:2.5px;background:rgba(242,230,208,.6);border-radius:2px;transition:all .3s cubic-bezier(.16,1,.3,1)}
.sb-hamburger span{top:50%;transform:translateY(-50%)}
.sb-hamburger span::before,.sb-hamburger span::after{content:''}
.sb-hamburger span::before{top:-8px}
.sb-hamburger span::after{top:8px}
.sb-hamburger span.sb-ham-bar--open{background:transparent}
.sb-hamburger span.sb-ham-bar--open::before{top:0;transform:rotate(45deg)}
.sb-hamburger span.sb-ham-bar--open::after{top:0;transform:rotate(-45deg)}

/* 手机导航 */
.sb-mobile-nav{display:none;position:fixed;top:0;left:0;bottom:0;width:260px;z-index:55;background:linear-gradient(170deg,#3d1114,#591a1e,#4a1519);padding:20px;flex-direction:column;gap:2px;box-shadow:4px 0 32px rgba(0,0,0,.3);overflow-y:auto}
.sb-mobile-nav::after{content:'欢迎';position:absolute;font-size:12rem;font-weight:900;color:rgba(255,255,255,.015);pointer-events:none;bottom:0;right:0;font-family:'Noto Serif SC',serif}
.sb-nav-logout-mobile{margin-top:auto;border-top:1px solid rgba(255,255,255,.08);padding-top:12px}
.mobile-nav-enter-active{animation:mnavIn .3s cubic-bezier(.16,1,.3,1)}
.mobile-nav-leave-active{animation:mnavOut .25s ease-in}
@keyframes mnavIn{from{transform:translateX(-100%)}to{transform:translateX(0)}}
@keyframes mnavOut{to{transform:translateX(-100%)}}

/* 右侧 */
.main { flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding: 24px 32px 32px; gap: 24px }
.profile-section { flex: 0 0 42.8%; min-height: 0 }
.bottom-section { flex: 1; min-height: 0 }

.section-card {
  height: 100%; background: #fff; border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 6px 20px rgba(0,0,0,.05);
  padding: 24px 28px; overflow-y: auto;
}
@media(max-width:768px){ .section-card { border-radius: 12px; padding: 14px } }
@media(max-width:480px){ .section-card { border-radius: 10px; padding: 14px 12px } }

/* 模块切换动画 */
.module-enter-active{animation:velvetIn .7s cubic-bezier(.33,1,.68,1) both}
.module-leave-active{animation:velvetOut .35s ease-in both}
@keyframes velvetIn{from{opacity:0;transform:scale(.97)}to{opacity:1;transform:scale(1)}}
@keyframes velvetOut{to{opacity:0;transform:scale(1.02);filter:blur(2px)}}

.module-enter-active > :nth-child(1){animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both;animation-delay:.1s}
.module-enter-active > :nth-child(2){animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both;animation-delay:.2s}
.module-enter-active > :nth-child(3){animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both;animation-delay:.3s}
.module-enter-active > :nth-child(4){animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both;animation-delay:.4s}
.module-enter-active > :nth-child(5){animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both;animation-delay:.5s}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}

/* 入场动画 */
.sidebar{animation:slideInLeft .6s cubic-bezier(.16,1,.3,1) both}
.profile-section{animation:fadeInUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.2s}
.bottom-section{animation:fadeInUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.38s}
@keyframes slideInLeft{from{transform:translateX(-100%);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes fadeInUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}

@media(max-width:1024px){
  .sidebar{flex:0 0 200px}
  .main{padding:20px 24px 24px}
  .profile-section{flex:0 0 40%}
}
@media(max-width:768px){
  .dashboard{flex-direction:column}
  .sidebar{flex:0 0 auto;flex-direction:row;padding:10px 16px;align-items:center;gap:6px;height:auto;justify-content:space-between}
  .sidebar::after{display:none}
  .sidebar-top{display:flex;align-items:center;gap:10px;text-align:left}
  .sb-logo-wrap{width:72px;height:72px;padding:3px;background:linear-gradient(135deg,#c9a96e,#e8d5a8,#c9a96e);border-radius:50%}
  .sb-logo{border-radius:50%;object-fit:cover}
  .sb-school,.sb-rule,.sb-nav,.sb-logout{display:none}
  .sb-avatar{display:none}
  .sb-name{font-size:1.1rem;margin-top:0}
  .sb-role{font-size:.72rem}
  .sb-hamburger{display:block;margin-left:auto}
  .sb-mobile-nav{display:flex}
  .main{padding:14px;gap:10px}
  .profile-section{flex:0 0 auto}
  .bottom-section{flex:1;min-height:0}
}
@media(max-width:480px){
  .sidebar{padding:10px 12px;gap:6px}
  .sb-logo-wrap{width:30px;height:30px}
  .sb-avatar{width:30px;height:30px;font-size:.85rem}
  .sb-name{font-size:.78rem}
  .main{padding:12px;gap:12px}
}
</style>

<style>
/* 退出动画 */
.login-leave-active .sidebar{animation:slideOutLeft .6s ease-in both;animation-delay:.38s}
.login-leave-active .profile-section{animation:fadeOutDown .45s ease-in both;animation-delay:.18s}
.login-leave-active .bottom-section{animation:fadeOutDown .45s ease-in both;animation-delay:0s}
@keyframes slideOutLeft{to{transform:translateX(-100%);opacity:0}}
@keyframes fadeOutDown{to{transform:translateY(16px);opacity:0}}
</style>
