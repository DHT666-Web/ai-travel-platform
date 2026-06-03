<template>
  <div class="page">
    <div class="card">
      <div class="top">
        <h2>景点管理</h2>
        <button @click="emit('back')">返回AI规划</button>
      </div>

      <div class="form">
        <input v-model="form.city" placeholder="城市，例如：北京" />
        <input v-model="form.name" placeholder="景点名称，例如：故宫博物院" />
        <input v-model="form.address" placeholder="地址" />
        <input v-model="form.price" placeholder="门票，例如：60元" />
        <input v-model="form.lng" placeholder="经度，例如：116.397" />
        <input v-model="form.lat" placeholder="纬度，例如：39.916" />
        <input v-model="form.tags" placeholder="标签，例如：历史文化,建筑" />
        <input v-model="form.description" placeholder="景点介绍" />

        <input type="file" @change="uploadCover" />

        <button @click="addSpot">新增景点</button>
      </div>

      <button class="refresh" @click="loadSpots">刷新列表</button>

      <div v-for="item in spots" :key="item.id" class="spot-item">
        <img v-if="item.cover_url" :src="item.cover_url" class="cover" />
        <h3>{{ item.name }} - {{ item.city }}</h3>
        <p>地址：{{ item.address }}</p>
        <p>门票：{{ item.price }}</p>
        <p>标签：{{ item.tags }}</p>
        <p>经纬度：{{ item.lng }}，{{ item.lat }}</p>
        <p>介绍：{{ item.description }}</p>

        <button class="delete" @click="deleteSpot(item.id)">删除</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../api/request'

const emit = defineEmits(['back'])

const spots = ref<any[]>([])

const form = ref({
  city: '北京',
  name: '故宫博物院',
  address: '北京市东城区景山前街4号',
  lng: '116.397',
  lat: '39.916',
  tags: '历史文化,建筑,博物馆',
  description: '故宫是明清两代皇家宫殿，是北京代表性历史文化景点。',
  price: '60元',
  cover_url: ''
})

const loadSpots = async () => {
  const res = await request.get('/scenic-spots')
  spots.value = res.data.data
}

const addSpot = async () => {
  await request.post('/scenic-spots', form.value)
  alert('新增成功')
  loadSpots()
}

const deleteSpot = async (id: number) => {
  if (!confirm('确定删除这个景点吗？')) return

  await request.delete(`/scenic-spots/${id}`)
  alert('删除成功')
  loadSpots()
}

const uploadCover = async (event: any) => {
  const file = event.target.files[0]

  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  const res = await request.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  form.value.cover_url = res.data.url

  alert('图片上传成功')
}

onMounted(() => {
  loadSpots()
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

.form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-top: 20px;
}

input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
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

.spot-item {
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 15px;
  background: #fafafa;
}

.cover {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 12px;
}
</style>