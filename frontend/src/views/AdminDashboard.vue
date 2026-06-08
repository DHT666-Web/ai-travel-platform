<template>
  <div class="page">
    <div class="card">
      <div class="top">
        <h2>后台数据统计</h2>
        <button @click="emit('back')">返回AI规划</button>
      </div>

      <div class="stats">
        <div class="stat">
          <h3>{{ stats.user_count }}</h3>
          <p>用户总数</p>
        </div>

        <div class="stat">
          <h3>{{ stats.trip_count }}</h3>
          <p>行程数量</p>
        </div>

        <div class="stat">
          <h3>{{ stats.scenic_count }}</h3>
          <p>景点数量</p>
        </div>

        <div class="stat">
          <h3>{{ stats.ai_count }}</h3>
          <p>AI调用次数</p>
        </div>
      </div>

      <h3>热门目的地 Top 10</h3>

      <div ref="chartRef" class="chart"></div>

      <div v-if="stats.top_destinations.length === 0" class="empty">
        暂无数据
      </div>

      <div v-for="item in stats.top_destinations" :key="item.destination" class="rank-item">
        <span>{{ item.destination }}</span>
        <span>{{ item.count }} 次</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'

const emit = defineEmits(['back'])

const chartRef = ref<HTMLDivElement | null>(null)

const stats = ref({
  user_count: 0,
  trip_count: 0,
  scenic_count: 0,
  ai_count: 0,
  top_destinations: [] as any[]
})
// 数据加载函数
const loadStats = async () => {
  const res = await request.get('/admin/statistics')
  stats.value = res.data.data

  await nextTick()
  renderChart()
}
// 图表渲染函数
const renderChart = () => {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)

  // ECharts部分：
  chart.setOption({
    title: {
      text: '热门目的地统计',
      left: 'center'
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: stats.value.top_destinations.map((item: any) => item.destination)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '次数',
        type: 'bar',
        data: stats.value.top_destinations.map((item: any) => item.count)
      }
    ]
  })
}

onMounted(() => {
  loadStats()
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

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin: 25px 0;
}

.stat {
  background: #f8f9fb;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat h3 {
  font-size: 30px;
  color: #409eff;
}

.stat p {
  color: #666;
}

.rank-item {
  display: flex;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #eee;
}

.empty {
  color: #999;
  padding: 30px;
  text-align: center;
}
.chart {
  width: 100%;
  height: 360px;
  margin-top: 30px;
}
</style>