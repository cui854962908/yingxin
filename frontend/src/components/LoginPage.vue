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
        <p class="brand-sub">迎 新 系 统</p>
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
/* 手机端红金迎新皮肤：只覆盖移动端，桌面端保持原布局 */
@media(max-width:768px){
  .page{
    display:block;
    min-height:100dvh;
    overflow-x:hidden;
    overflow-y:auto;
    background:
      radial-gradient(circle at 50% 10%,rgba(255,255,255,.12),transparent 24%),
      linear-gradient(180deg,#75171d 0%,#8c2028 38%,#540b13 100%);
  }
  .page::before{
    content:'迎';
    position:fixed;
    z-index:0;
    top:1.2rem;
    right:-1.4rem;
    color:rgba(255,255,255,.055);
    font-family:'STKaiti','KaiTi','Noto Serif SC',serif;
    font-size:9rem;
    line-height:1;
    pointer-events:none;
  }
  .brand-panel{
    display:block;
    min-height:48vh;
    background:transparent;
    overflow:hidden;
  }
  .brand-panel::before{
    background:
      linear-gradient(180deg,rgba(72,7,13,.12) 0%,rgba(86,9,16,.52) 72%,rgba(84,11,19,.92) 100%),
      radial-gradient(circle at 50% 12%,rgba(242,230,208,.16),transparent 28%);
  }
  .brand-bg{
    object-fit:cover;
    object-position:center bottom;
    opacity:.30;
    filter:saturate(.8) contrast(1.12);
    mix-blend-mode:screen;
  }
  .brand-inner{
    width:100%;
    padding:7vh 20px 0;
  }
  .logo-wrap{
    width:86px;
    height:86px;
    box-shadow:0 12px 30px rgba(0,0,0,.22);
  }
  .school-name{
    font-size:1.72rem;
    margin-top:24px;
    color:#f6dfad;
    letter-spacing:.08em;
    text-shadow:0 3px 16px rgba(0,0,0,.26);
  }
  .motto{
    font-size:1rem;
    margin-top:10px;
    color:#e7c78e;
    letter-spacing:.18em;
  }
  .brand-rule{
    margin:18px auto 14px;
  }
  .brand-rule::before,
  .brand-rule::after{
    width:68px;
    background:linear-gradient(90deg,transparent,rgba(232,213,168,.6),transparent);
  }
  .year-badge{
    font-size:2.55rem;
    color:#f6dfad;
    letter-spacing:.24em;
    text-indent:.24em;
  }
  .brand-sub{
    font-size:.9rem;
    color:#f2e6d0;
    letter-spacing:.42em;
    text-indent:.42em;
  }
  .form-panel{
    display:block;
    min-height:auto;
    margin-top:-4.5vh;
    padding:0 18px max(30px,env(safe-area-inset-bottom));
    background:transparent;
    overflow:visible;
  }
  .form-panel::before{
    content:'';
    position:absolute;
    inset:-24vh 0 0;
    z-index:0;
    pointer-events:none;
    background:linear-gradient(180deg,transparent 0%,rgba(41,0,7,.20) 68%,rgba(41,0,7,.45) 100%);
  }
  .grid-texture,
  .watermark,
  .form-watermark{
    display:none;
  }
  .form-inner{
    width:100%;
    max-width:520px;
    margin:0 auto;
    padding:34px 28px 30px;
    border-radius:24px;
    background:rgba(255,255,255,.97);
    box-shadow:
      0 18px 44px rgba(39,0,5,.36),
      0 0 0 8px rgba(255,255,255,.08);
    backdrop-filter:blur(12px);
  }
  .form-eyebrow{
    text-align:center;
    margin-bottom:10px;
    color:#b08b6e;
    font-size:.72rem;
    letter-spacing:.16em;
  }
  .form-heading{
    text-align:center;
    font-size:2.05rem;
    color:#29313a;
    letter-spacing:.16em;
    text-indent:.16em;
  }
  .heading-rule{
    width:54px;
    height:4px;
    margin:16px auto 0;
    background:#a31522;
    border-radius:999px;
  }
  .form-desc{
    text-align:center;
    margin:18px 0 28px;
    font-size:.92rem;
    color:#76716c;
  }
  .footer-tip{
    display:none;
  }
}

@media(max-width:480px){
  .page::before{
    font-size:7.6rem;
    right:-2rem;
    top:.8rem;
  }
  .brand-panel{
    min-height:43vh;
  }
  .brand-inner{
    padding:5.8vh 18px 0;
  }
  .logo-wrap{
    width:70px;
    height:70px;
  }
  .school-name{
    font-size:1.42rem;
    margin-top:18px;
  }
  .motto{
    font-size:.88rem;
    margin-top:8px;
  }
  .year-badge{
    font-size:2rem;
  }
  .brand-rule{
    margin:14px auto 10px;
  }
  .brand-rule::before,
  .brand-rule::after{
    width:48px;
  }
  .brand-sub{
    font-size:.78rem;
    margin-top:4px;
  }
  .form-panel{
    margin-top:-4.4vh;
    padding:0 16px max(24px,env(safe-area-inset-bottom));
  }
  .form-inner{
    max-width:100%;
    padding:30px 22px 28px;
    border-radius:22px;
  }
  .form-eyebrow{
    font-size:.62rem;
  }
  .form-heading{
    font-size:1.72rem;
  }
  .heading-rule{
    margin-top:14px;
  }
  .form-desc{
    font-size:.84rem;
    margin:16px 0 24px;
  }
}

@media(max-width:380px){
  .brand-panel{
    min-height:40vh;
  }
  .brand-inner{
    padding-top:4.8vh;
  }
  .logo-wrap{
    width:62px;
    height:62px;
  }
  .school-name{
    font-size:1.24rem;
    margin-top:14px;
  }
  .motto{
    font-size:.8rem;
  }
  .year-badge{
    font-size:1.72rem;
  }
  .form-panel{
    margin-top:-3.2vh;
  }
  .form-inner{
    padding:26px 18px 24px;
  }
  .form-heading{
    font-size:1.52rem;
  }
  .form-desc{
    font-size:.8rem;
    margin-bottom:20px;
  }
}
/* 最终版手机端登录页：贴近参考图，覆盖前面的旧移动端规则 */
@media(max-width:768px){
  .page{
    display:block !important;
    min-height:100dvh !important;
    overflow-x:hidden !important;
    overflow-y:auto !important;
    background:
      radial-gradient(circle at 50% 8%, rgba(255,255,255,.12), transparent 22%),
      linear-gradient(180deg, #651219 0%, #8b2028 42%, #4a0910 100%) !important;
  }
  .page::before{
    content:'迎' !important;
    position:fixed !important;
    top:1.2rem !important;
    right:-1.8rem !important;
    z-index:0 !important;
    color:rgba(255,255,255,.055) !important;
    font-family:'STKaiti','KaiTi','Noto Serif SC',serif !important;
    font-size:9rem !important;
    line-height:1 !important;
    pointer-events:none !important;
  }
  .brand-panel{
    display:block !important;
    min-height:45vh !important;
    background:transparent !important;
    overflow:hidden !important;
  }
  .brand-panel::before{
    background:
      linear-gradient(180deg, rgba(75,6,12,.04) 0%, rgba(107,13,21,.34) 62%, rgba(73,7,14,.82) 100%),
      radial-gradient(circle at 50% 14%, rgba(242,230,208,.13), transparent 28%) !important;
  }
  .brand-bg{
    object-fit:cover !important;
    object-position:center bottom !important;
    opacity:.48 !important;
    filter:saturate(.85) contrast(1.22) brightness(1.08) !important;
    mix-blend-mode:screen !important;
  }
  .brand-inner{
    width:100% !important;
    padding:6.2vh 20px 0 !important;
    text-align:center !important;
  }
  .logo-wrap{
    width:82px !important;
    height:82px !important;
    box-shadow:0 12px 30px rgba(0,0,0,.22) !important;
  }
  .school-name{
    margin-top:22px !important;
    color:#f6dfad !important;
    font-size:1.72rem !important;
    letter-spacing:.08em !important;
    line-height:1.35 !important;
    text-shadow:0 3px 16px rgba(0,0,0,.26) !important;
  }
  .motto{
    margin-top:10px !important;
    color:#e7c78e !important;
    font-size:1rem !important;
    letter-spacing:.18em !important;
  }
  .brand-rule{
    margin:18px auto 14px !important;
  }
  .brand-rule::before,
  .brand-rule::after{
    width:68px !important;
    background:linear-gradient(90deg, transparent, rgba(232,213,168,.62), transparent) !important;
  }
  .year-badge{
    color:#f6dfad !important;
    font-size:2.55rem !important;
    letter-spacing:.24em !important;
    text-indent:.24em !important;
  }
  .brand-sub{
    margin-top:4px !important;
    color:#f2e6d0 !important;
    font-size:.9rem !important;
    letter-spacing:.42em !important;
    text-indent:.42em !important;
  }
  .form-panel{
    display:block !important;
    min-height:auto !important;
    margin-top:-4.1vh !important;
    padding:0 15.5vw max(34px, env(safe-area-inset-bottom)) !important;
    background:transparent !important;
    overflow:visible !important;
  }
  .form-panel::before{
    content:'' !important;
    position:absolute !important;
    inset:-24vh 0 0 !important;
    z-index:0 !important;
    pointer-events:none !important;
    background:linear-gradient(180deg, transparent 0%, rgba(41,0,7,.18) 68%, rgba(41,0,7,.42) 100%) !important;
  }
  .grid-texture,
  .watermark,
  .form-watermark{
    display:none !important;
  }
  .form-inner{
    width:100% !important;
    max-width:620px !important;
    margin:0 auto !important;
    padding:42px 38px 38px !important;
    border-radius:26px !important;
    background:rgba(255,255,255,.975) !important;
    box-shadow:
      0 18px 44px rgba(39,0,5,.38),
      0 0 0 8px rgba(255,255,255,.08) !important;
    backdrop-filter:blur(12px) !important;
  }
  .form-eyebrow{
    margin-bottom:12px !important;
    color:#b08b6e !important;
    text-align:center !important;
    font-size:.76rem !important;
    letter-spacing:.18em !important;
  }
  .form-heading{
    color:#29313a !important;
    text-align:center !important;
    font-size:2.24rem !important;
    letter-spacing:.16em !important;
    text-indent:.16em !important;
    line-height:1.25 !important;
  }
  .heading-rule{
    width:58px !important;
    height:4px !important;
    margin:18px auto 0 !important;
    border-radius:999px !important;
    background:#a31522 !important;
  }
  .form-desc{
    margin:20px 0 34px !important;
    color:#76716c !important;
    text-align:center !important;
    font-size:.96rem !important;
  }
  .footer-tip{
    display:none !important;
  }
}

@media(max-width:480px){
  .page::before{
    top:.8rem !important;
    right:-2rem !important;
    font-size:7.6rem !important;
  }
  .brand-panel{
    min-height:41vh !important;
  }
  .brand-inner{
    padding:5.1vh 18px 0 !important;
  }
  .logo-wrap{
    width:70px !important;
    height:70px !important;
  }
  .school-name{
    margin-top:18px !important;
    font-size:1.42rem !important;
  }
  .motto{
    margin-top:8px !important;
    font-size:.88rem !important;
  }
  .brand-rule{
    margin:14px auto 10px !important;
  }
  .brand-rule::before,
  .brand-rule::after{
    width:48px !important;
  }
  .year-badge{
    font-size:2rem !important;
  }
  .brand-sub{
    font-size:.78rem !important;
  }
  .form-panel{
    margin-top:-3.6vh !important;
    padding:0 6vw max(26px, env(safe-area-inset-bottom)) !important;
  }
  .form-inner{
    padding:34px 24px 30px !important;
    border-radius:24px !important;
  }
  .form-eyebrow{
    font-size:.64rem !important;
  }
  .form-heading{
    font-size:1.78rem !important;
  }
  .heading-rule{
    margin-top:14px !important;
  }
  .form-desc{
    margin:16px 0 26px !important;
    font-size:.86rem !important;
  }
}

@media(max-width:380px){
  .brand-panel{
    min-height:38vh !important;
  }
  .brand-inner{
    padding-top:4.4vh !important;
  }
  .logo-wrap{
    width:62px !important;
    height:62px !important;
  }
  .school-name{
    margin-top:14px !important;
    font-size:1.25rem !important;
  }
  .motto{
    font-size:.8rem !important;
  }
  .year-badge{
    font-size:1.72rem !important;
  }
  .form-panel{
    margin-top:-2.8vh !important;
  }
  .form-inner{
    padding:28px 18px 24px !important;
  }
  .form-heading{
    font-size:1.54rem !important;
  }
  .form-desc{
    margin-bottom:20px !important;
    font-size:.8rem !important;
  }
}
/* 手机端最终紧凑版：缩小登录模块，减少卡片内部空白 */
@media(max-width:768px){
  .form-panel{
    margin-top:-3.8vh !important;
    padding:0 17vw max(30px,env(safe-area-inset-bottom)) !important;
  }
  .form-inner{
    max-width:540px !important;
    padding:30px 30px 28px !important;
    border-radius:24px !important;
  }
  .form-eyebrow{
    margin-bottom:7px !important;
    font-size:.68rem !important;
  }
  .form-heading{
    font-size:1.9rem !important;
  }
  .heading-rule{
    width:50px !important;
    height:4px !important;
    margin:12px auto 0 !important;
  }
  .form-desc{
    margin:13px 0 20px !important;
    font-size:.86rem !important;
  }
}

@media(max-width:480px){
  .brand-panel{
    min-height:40vh !important;
  }
  .brand-inner{
    padding-top:4.8vh !important;
  }
  .form-panel{
    margin-top:-3vh !important;
    padding:0 7vw max(24px,env(safe-area-inset-bottom)) !important;
  }
  .form-inner{
    padding:25px 20px 22px !important;
    border-radius:22px !important;
  }
  .form-eyebrow{
    margin-bottom:6px !important;
    font-size:.58rem !important;
  }
  .form-heading{
    font-size:1.5rem !important;
  }
  .heading-rule{
    width:44px !important;
    height:3px !important;
    margin-top:10px !important;
  }
  .form-desc{
    margin:10px 0 16px !important;
    font-size:.76rem !important;
  }
}

@media(max-width:380px){
  .brand-panel{
    min-height:37vh !important;
  }
  .form-panel{
    margin-top:-2.4vh !important;
    padding-inline:6vw !important;
  }
  .form-inner{
    padding:22px 16px 20px !important;
  }
  .form-heading{
    font-size:1.36rem !important;
  }
}
</style>

<style scoped>
.page{display:flex;min-height:100vh;min-height:calc(var(--vh,1vh)*100);overflow:hidden}

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
.brand-bg{
  position:absolute;inset:0;width:100%;height:100%;
  object-fit:cover;object-position:50% 30%;pointer-events:none;opacity:.6;
}
.brand-inner{position:relative;z-index:1;text-align:center;padding:40px 32px}
.logo-wrap{
  width:110px;height:110px;border-radius:50%;padding:3px;margin:0 auto;
  background:linear-gradient(135deg,#c9a96e 0%,#e8d5a8 50%,#c9a96e 100%);
  overflow:hidden;position:relative;
}
.logo{
  position:absolute;top:50%;left:48%;
  width:125%;height:125%;transform:translate(-50%,-50%);
  border-radius:50%;object-fit:cover;background:transparent;display:block;
}
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
.form-watermark{
  position:absolute;bottom:0;left:0;width:100%;
  object-fit:contain;pointer-events:none;opacity:.5;
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
  .school-name{font-size:1.3rem}
  .motto{font-size:1rem}
  .year-badge{font-size:2.8rem}
}
/* 平板竖屏 / 大手机横屏 */
@media(max-width:768px){
  .page{flex-direction:column}
  .brand-panel{flex:0 0 auto;min-height:42vh}
  .brand-bg{object-fit:cover;object-position:center bottom}
  .brand-inner{padding:20px 24px}
  .logo-wrap{width:70px;height:70px}
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
  .form-watermark{display:none}
}
/* 手机 */
@media(max-width:480px){
  .brand-panel{min-height:33vh}
  .brand-inner{padding:14px 16px}
  .logo-wrap{width:60px;height:60px}
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
