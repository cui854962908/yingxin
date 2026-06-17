<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'

interface Student {
  name: string; student_id: string; class_name: string
  dormitory: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

const studentRef = inject<Ref<Student>>('student')!
const student = computed(() => studentRef.value)
const avatarChar = computed(() => student.value?.name?.charAt(0) || '')
</script>

<template>
  <div class="card">
    <!-- 顶部：头像 + 姓名行 -->
    <div class="top-row">
      <div class="avatar-ring">
        <div class="avatar">{{ avatarChar }}</div>
      </div>
      <div class="top-info">
        <h2 class="name">{{ student.name }}</h2>
        <span class="badge">2026</span>
      </div>
    </div>

    <p class="klass">{{ student.class_name }}</p>

    <div class="meta">
      <div class="meta-item">
        <span class="meta-label">学号</span>
        <span class="meta-val">{{ student.student_id }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">宿舍</span>
        <span class="meta-val">{{ student.dormitory }}</span>
      </div>
    </div>

    <div class="divider" />

    <div class="contacts">
      <div class="ctc">
        <span class="ctc-role">辅导员</span>
        <span class="ctc-name">{{ student.advisor?.name || '' }}</span>
        <span class="ctc-phone">{{ student.advisor?.phone || '' }}</span>
      </div>
      <div class="ctc">
        <span class="ctc-role">班主任</span>
        <span class="ctc-name">{{ student.class_teacher?.name || '' }}</span>
        <span class="ctc-phone">{{ student.class_teacher?.phone || '' }}</span>
      </div>
      <div class="ctc">
        <span class="ctc-role">代 班</span>
        <span class="ctc-name">
          <template v-for="(a, i) in (student.assistants || [])" :key="i">
            <span v-if="i > 0" class="ctc-sep"> / </span>
            {{ a?.name || '' }}
            <small v-if="a?.class_name && a.class_name !== '—'">· {{ a.class_name }}</small>
          </template>
        </span>
        <span class="ctc-phone">{{ student.assistants?.[0]?.phone || '' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  height: 100%; background: #fff; border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 6px 20px rgba(0,0,0,.05);
  padding: 22px 32px 28px; display: flex; flex-direction: column;
  justify-content: flex-start; position: relative; overflow: hidden;
}
.card::after {
  content: ''; position: absolute; top: 0; right: 0; width: 120px; height: 120px;
  background: radial-gradient(circle, rgba(181,52,58,.03) 0%, transparent 70%);
  pointer-events: none;
}

/* 顶部行：头像 + 姓名 */
.top-row { display: flex; align-items: center; gap: 18px }
.avatar-ring {
  width: 60px; height: 60px; border-radius: 50%; padding: 3px; flex-shrink: 0;
  background: linear-gradient(135deg, #c9a96e, #e8d5a8, #c9a96e);
  box-shadow: 0 2px 14px rgba(181,52,58,.1);
}
.avatar {
  width: 100%; height: 100%; border-radius: 50%;
  background: linear-gradient(135deg, #b5343a, #8b2025);
  color: #fff; font-size: 1.8rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Noto Serif SC', 'KaiTi', serif;
}
.top-info { display: flex; align-items: center; gap: 12px; flex: 1 }
.name { font-size: 1.8rem; font-weight: 700; color: #2c2c2c; letter-spacing: .12em }
.badge {
  font-size: .68rem; color: #b5343a; font-weight: 700;
  border: 1.5px solid rgba(181,52,58,.25); padding: 2px 10px;
  border-radius: 10px; letter-spacing: .1em; white-space: nowrap;
}

.klass { font-size: .84rem; color: #8b7b65; margin-top: 6px; margin-left: 78px }

.meta { display: flex; gap: 28px; margin-top: 10px; margin-left: 78px }
.meta-item { display: flex; flex-direction: column; gap: 2px }
.meta-label { font-size: .7rem; color: #b0a090; letter-spacing: .04em }
.meta-val { font-size: .92rem; color: #3c3028; font-weight: 500 }

.divider {
  height: 1px; background: linear-gradient(90deg, #e5dbcc 0%, #e5dbcc 70%, transparent 100%);
  margin: 10px 0 10px;
}

.contacts { display: flex; flex-direction: column; gap: 5px }
.ctc {
  display: flex; align-items: center; gap: 10px; padding: 6px 14px;
  border-radius: 8px; background: #fdfaf6; border: 1px solid #f2ebe0;
}
.ctc-role { font-size: .7rem; color: #b0a090; font-weight: 500; min-width: 42px; text-align: center; letter-spacing: .04em }
.ctc-name { font-size: .88rem; color: #3c3028; font-weight: 500; flex: 1 }
.ctc-name small { font-size: .76rem; color: #a09888; font-weight: 400 }
.ctc-sep { color: #d4c8b0; font-weight: 400 }
.ctc-phone { font-size: .82rem; color: #8b7b65; font-family: 'SF Mono', 'Consolas', monospace }

@media(max-width:768px){
  .card{padding:22px;justify-content:flex-start}
  .top-row{gap:14px}
  .avatar-ring{width:60px;height:60px}
  .avatar{font-size:1.5rem}
  .name{font-size:1.4rem}
  .klass,.meta{margin-left:74px}
  .klass{font-size:.82rem}
  .meta{gap:24px}
}
@media(max-width:480px){
  .card{padding:16px;border-radius:12px}
  .top-row{gap:12px}
  .avatar-ring{width:50px;height:50px}
  .avatar{font-size:1.3rem}
  .name{font-size:1.2rem}
  .klass,.meta{margin-left:62px}
  .klass{font-size:.76rem;margin-top:6px}
  .meta{gap:16px;margin-top:10px}
  .meta-val{font-size:.8rem}
  .divider{margin:12px 0 10px}
  .ctc{padding:6px 10px}
  .ctc-name{font-size:.78rem}
  .ctc-phone{font-size:.72rem}
}
</style>
