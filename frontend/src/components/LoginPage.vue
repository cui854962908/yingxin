<script setup lang="ts">
import LoginForm from './LoginForm.vue'

const emit = defineEmits<{
  'login-success': [student: Record<string, any>, token: string]
}>()
</script>

<template>
  <div class="page">
    <!-- 左：品牌面板 -->
    <aside class="brand-panel">
      <!-- 背景水印：欢左迎右 -->
      <span class="water-char water-left">欢</span>
      <span class="water-char water-right">迎</span>
      <div class="brand-inner">
        <div class="logo-wrap">
          <img
            src="/logo-1.png"
            alt="校徽"
            class="logo"
            @error="(e: Event) => ((e.target as HTMLImageElement).style.display = 'none')"
          />
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
        <p class="brand-sub">迎 新 系 统</p>
      </div>
    </aside>

    <!-- 右：表单区域 -->
    <main class="form-panel">
      <!-- 背景网格纹理 -->
      <div class="grid-texture" />

      <!-- 底部大号水印 -->
      <span class="watermark">2026</span>

      <div class="form-inner">
        <p class="form-eyebrow">NEW STUDENT · IDENTITY VERIFICATION</p>
        <h2 class="form-heading">新生入学验证</h2>
        <div class="heading-rule" />
        <p class="form-desc">请输入你的入学信息以完成身份核验</p>

        <LoginForm @login-success="(s, t) => emit('login-success', s, t)" />

        <p class="footer-tip">姓名 · 学号 · 身份证号，三项验证通过即可进入系统</p>
      </div>
    </main>
  </div>
</template>

<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
body{font-family:'PingFang SC','Microsoft YaHei','Noto Serif SC',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased}
</style>

<style scoped>
.page{display:flex;min-height:100vh;overflow:hidden}

/* 左面板 */
.brand-panel{
  flex:0 0 42%;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(170deg,#3d1114 0%,#591a1e 30%,#4a1519 60%,#361012 100%);
  position:relative;overflow:hidden;
}
.brand-panel::before{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:
    radial-gradient(circle at 30% 20%,rgba(201,169,110,.07) 0%,transparent 50%),
    radial-gradient(circle at 70% 80%,rgba(201,169,110,.04) 0%,transparent 50%),
    radial-gradient(circle at 50% 50%,rgba(255,255,255,.02) 0%,transparent 70%);
}
.water-char{position:absolute;font-weight:900;color:rgba(255,255,255,.02);pointer-events:none;line-height:1;font-family:'Noto Serif SC','KaiTi',serif}
.water-left{top:30px;left:30px;font-size:25rem}
.water-right{bottom:50px;right:30px;font-size:25rem}
.brand-inner{position:relative;z-index:1;text-align:center;padding:40px 32px}
.logo-wrap{
  width:100px;height:100px;border-radius:50%;padding:3px;margin:0 auto;
  background:linear-gradient(135deg,#c9a96e 0%,#e8d5a8 50%,#c9a96e 100%);
}
.logo{width:100%;height:100%;border-radius:50%;object-fit:cover;background:transparent;display:block}
.school-name{font-size:1.5rem;font-weight:700;color:#f2e6d0;letter-spacing:.08em;margin-top:22px;line-height:1.4;font-family:'Georgia','Noto Serif SC','KaiTi',serif;font-style:italic}
.motto{font-size:1.1rem;color:#c4a87e;margin-top:12px;letter-spacing:.14em;font-style:italic;font-family:'Georgia','Noto Serif SC','KaiTi',serif}
.motto-bracket{color:rgba(201,169,110,.5);font-size:.85rem}
.brand-rule{margin:32px auto 28px;display:flex;align-items:center;justify-content:center;gap:16px}
.brand-rule::before,.brand-rule::after{
  content:'';width:48px;height:1px;
  background:linear-gradient(90deg,transparent,rgba(201,169,110,.4),transparent);
}
.brand-rule-dot{font-size:.35rem;color:rgba(201,169,110,.5)}
.year-badge{font-size:3.2rem;font-weight:300;color:#f2e6d0;letter-spacing:.15em;font-family:'Georgia','Noto Serif SC',serif;line-height:1}
.brand-sub{font-size:.85rem;color:rgba(242,230,208,.5);letter-spacing:.3em;margin-top:8px}

/* 右面板 */
.form-panel{flex:1;background:#fefcf9;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.grid-texture{
  position:absolute;inset:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(181,52,58,.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(181,52,58,.03) 1px,transparent 1px);
  background-size:32px 32px;
  mask-image:radial-gradient(ellipse at 40% 50%,black 30%,transparent 70%);
}
.watermark{
  position:absolute;bottom:-60px;right:-40px;font-size:18rem;font-weight:900;
  color:rgba(181,52,58,.015);pointer-events:none;line-height:1;
  font-family:'Georgia','Noto Serif SC',serif;
}
.form-inner{position:relative;z-index:1;width:380px;max-width:86%;padding:48px 0}
.form-eyebrow{font-size:.65rem;color:#c4b298;letter-spacing:.2em;text-transform:uppercase;margin-bottom:6px}
.form-heading{font-size:2rem;font-weight:700;color:#2c2c2c;letter-spacing:.12em;line-height:1.3}
.heading-rule{width:36px;height:2px;background:#b5343a;margin-top:14px;border-radius:1px}
.form-desc{font-size:.9rem;color:#a09888;margin-top:14px;margin-bottom:36px}
.footer-tip{margin-top:24px;font-size:.76rem;color:#c4b8a8;text-align:center;line-height:1.6}

/* 平板竖屏 */
@media(max-width:1024px){
  .brand-panel{flex:0 0 38%}
  .brand-inner{padding:32px 24px}
  .water-left{font-size:20rem;top:20px;left:20px}
  .water-right{font-size:20rem;bottom:30px;right:20px}
  .school-name{font-size:1.3rem}
  .motto{font-size:1rem}
  .year-badge{font-size:2.8rem}
}
/* 平板竖屏 / 大手机横屏 */
@media(max-width:768px){
  .page{flex-direction:column}
  .brand-panel{flex:0 0 auto;min-height:42vh}
  .brand-inner{padding:20px 24px}
  .logo-wrap{width:70px;height:70px}
  .water-left{font-size:14rem;top:6px;left:12px}
  .water-right{font-size:14rem;bottom:16px;right:8px}
  .school-name{font-size:1.15rem;margin-top:12px}
  .motto{font-size:.9rem;margin-top:8px}
  .year-badge{font-size:2rem}
  .brand-rule{margin:16px auto 14px}
  .brand-sub{font-size:.76rem}
  .form-panel{flex:1;min-height:0}
  .form-inner{width:100%;max-width:92%;padding:20px 0 24px}
  .form-heading{font-size:1.5rem}
  .form-desc{margin-bottom:20px;font-size:.8rem}
  .watermark{font-size:10rem;bottom:-30px;right:-20px;opacity:.01}
}
/* 手机 */
@media(max-width:480px){
  .brand-panel{min-height:33vh}
  .brand-inner{padding:14px 16px}
  .logo-wrap{width:60px;height:60px}
  .water-left{font-size:10rem;top:4px;left:6px}
  .water-right{font-size:10rem;bottom:10px;right:4px}
  .school-name{font-size:1.05rem;margin-top:10px}
  .motto{font-size:.82rem;margin-top:6px}
  .year-badge{font-size:1.6rem}
  .brand-rule{margin:12px auto 10px}
  .brand-rule::before,.brand-rule::after{width:36px}
  .brand-sub{font-size:.7rem;margin-top:4px}
  .form-inner{padding:16px 0 20px;max-width:96%}
  .form-heading{font-size:1.3rem}
  .heading-rule{margin-top:8px}
  .form-eyebrow{font-size:.58rem}
  .form-desc{font-size:.76rem;margin-bottom:16px;margin-top:8px}
  .footer-tip{font-size:.68rem;margin-top:14px}
  .watermark{font-size:8rem;bottom:-20px;right:-16px}
}
</style>
