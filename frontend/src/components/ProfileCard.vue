<script setup lang="ts">
import { computed } from 'vue'

interface Student {
  name: string; student_id: string; class_name: string
  dormitory: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

const props = defineProps<{ student: Student }>()
const avatarChar = computed(() => props.student.name.charAt(0))
</script>

<template>
  <div class="card">
    <!-- 头像 -->
    <div class="left">
      <div class="avatar-ring">
        <div class="avatar">{{ avatarChar }}</div>
      </div>
      <span class="badge">2026</span>
    </div>

    <!-- 信息 -->
    <div class="info">
      <h2 class="name">{{ props.student.name }}</h2>
      <p class="klass">{{ props.student.class_name }}</p>

      <div class="meta">
        <div class="meta-item">
          <span class="meta-label">学号</span>
          <span class="meta-val">{{ props.student.student_id }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">宿舍</span>
          <span class="meta-val">{{ props.student.dormitory }}</span>
        </div>
      </div>

      <div class="divider" />

      <div class="contacts">
        <div class="ctc">
          <span class="ctc-role">辅导员</span>
          <span class="ctc-name">{{ props.student.advisor.name }}</span>
          <span class="ctc-phone">{{ props.student.advisor.phone }}</span>
        </div>
        <div class="ctc">
          <span class="ctc-role">班主任</span>
          <span class="ctc-name">{{ props.student.class_teacher.name }}</span>
          <span class="ctc-phone">{{ props.student.class_teacher.phone }}</span>
        </div>
        <div class="ctc">
          <span class="ctc-role">代 班</span>
          <span class="ctc-name">
            <template v-for="(a, i) in props.student.assistants" :key="i">
              <span v-if="i > 0" class="ctc-sep"> / </span>
              {{ a.name }}
              <small v-if="a.class_name && a.class_name !== '—'">· {{ a.class_name }}</small>
            </template>
          </span>
          <span class="ctc-phone">{{ props.student.assistants[0]?.phone }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  height: 100%; background: #fff; border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 6px 20px rgba(0,0,0,.05);
  display: flex; padding: 32px; gap: 28px; position: relative; overflow: hidden;
}
.card::after {
  content: ''; position: absolute; top: 0; right: 0; width: 120px; height: 120px;
  background: radial-gradient(circle, rgba(181,52,58,.03) 0%, transparent 70%);
  pointer-events: none;
}

.left { display: flex; flex-direction: column; align-items: center; gap: 10px; flex-shrink: 0 }
.avatar-ring {
  width: 100px; height: 100px; border-radius: 50%; padding: 3px;
  background: linear-gradient(135deg, #c9a96e, #e8d5a8, #c9a96e);
  box-shadow: 0 2px 14px rgba(181,52,58,.1);
}
.avatar {
  width: 100%; height: 100%; border-radius: 50%;
  background: linear-gradient(135deg, #b5343a, #8b2025);
  color: #fff; font-size: 2.4rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Noto Serif SC', 'KaiTi', serif;
}
.badge {
  font-size: .7rem; color: #b5343a; font-weight: 700;
  border: 1.5px solid rgba(181,52,58,.25); padding: 2px 10px;
  border-radius: 10px; letter-spacing: .1em;
}

.info { flex: 1; display: flex; flex-direction: column; justify-content: center }
.name { font-size: 1.8rem; font-weight: 700; color: #2c2c2c; letter-spacing: .12em }
.klass { font-size: .88rem; color: #8b7b65; margin-top: 4px }

.meta { display: flex; gap: 32px; margin-top: 16px }
.meta-item { display: flex; flex-direction: column; gap: 2px }
.meta-label { font-size: .7rem; color: #b0a090; letter-spacing: .04em }
.meta-val { font-size: .92rem; color: #3c3028; font-weight: 500 }

.divider {
  height: 1px; background: linear-gradient(90deg, #e5dbcc 0%, #e5dbcc 70%, transparent 100%);
  margin: 18px 0 16px;
}

.contacts { display: flex; flex-direction: column; gap: 8px }
.ctc {
  display: flex; align-items: center; gap: 12px; padding: 8px 14px;
  border-radius: 8px; background: #fdfaf6; border: 1px solid #f2ebe0;
}
.ctc-role { font-size: .7rem; color: #b0a090; font-weight: 500; min-width: 42px; text-align: center; letter-spacing: .04em }
.ctc-name { font-size: .88rem; color: #3c3028; font-weight: 500; flex: 1 }
.ctc-name small { font-size: .76rem; color: #a09888; font-weight: 400 }
.ctc-sep { color: #d4c8b0; font-weight: 400 }
.ctc-phone { font-size: .82rem; color: #8b7b65; font-family: 'SF Mono', 'Consolas', monospace }

@media (max-width: 720px) {
  .card { flex-direction: column; align-items: center; text-align: center; padding: 24px; gap: 16px }
  .meta { justify-content: center }
  .contacts { align-items: stretch }
  .ctc { flex-wrap: wrap; justify-content: center }
  .divider { background: linear-gradient(90deg, transparent 0%, #e5dbcc 20%, #e5dbcc 80%, transparent 100%) }
}
</style>
