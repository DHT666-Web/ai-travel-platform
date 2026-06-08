<template>
  <div class="page">
    <div class="card">
      <div class="top">
        <h2>我的规划</h2>
        <button @click="emit('back')">返回AI规划</button>
      </div>

      <button class="refresh" @click="loadPlans">刷新列表</button>

      <div v-if="plans.length === 0" class="empty">
        暂无保存的行程
      </div>

      <div v-for="item in plans" :key="item.id" class="plan-item">
        <div class="plan-header">
          <h3>{{ item.destination }} {{ item.days }}日游</h3>
          <button class="delete" @click="deletePlan(item.id)">删除</button>
        </div>

        <p>偏好：{{ item.preference }}</p>

        <pre>{{ item.plan_content }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../api/request'

const emit = defineEmits(['back'])

const plans = ref<any[]>([])

const loadPlans = async () => {
  const res = await request.get('/travel-plans')
  plans.value = res.data.data
}

const deletePlan = async (id: number) => {
  if (!confirm('确定要删除这条行程吗？')) return

  await request.delete(`/travel-plans/${id}`)
  alert('删除成功')
  loadPlans()
}

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 40px;
}

.card {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  padding: 30px;
  border-radius: 14px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

button {
  height: 38px;
  padding: 0 18px;
  border: none;
  border-radius: 6px;
  background: #409eff;
  color: white;
  cursor: pointer;
}

.refresh {
  margin: 20px 0;
}

.delete {
  background: #f56c6c;
}

.empty {
  color: #999;
  text-align: center;
  padding: 40px;
}

.plan-item {
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fafafa;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

pre {
  white-space: pre-wrap;
  line-height: 1.7;
  background: white;
  padding: 15px;
  border-radius: 8px;
}
</style>