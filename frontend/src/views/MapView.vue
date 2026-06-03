<template>
  <div class="page">
    <div class="card">
      <div class="top">
        <h2>真实地图路线展示</h2>
        <button @click="emit('back')">返回AI规划</button>
      </div>

      <div ref="mapRef" class="map"></div>

      <div class="list">
        <div v-for="item in spots" :key="item.id" class="spot">
          <img v-if="item.cover_url" :src="item.cover_url" class="cover" />

          <h3>{{ item.name }} - {{ item.city }}</h3>
          <p>地址：{{ item.address }}</p>
          <p>门票：{{ item.price }}</p>
          <p>经纬度：{{ item.lng }}，{{ item.lat }}</p>
          <p>标签：{{ item.tags }}</p>
          <p>介绍：{{ item.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'

declare const AMap: any

const emit = defineEmits(['back'])

const mapRef = ref<HTMLDivElement | null>(null)
const spots = ref<any[]>([])

let map: any = null

const loadSpots = async () => {
  const res = await request.get('/scenic-spots')

  spots.value = res.data.data.filter((item: any) => {
    return item.lng && item.lat
  })

  await nextTick()
  initMap()
}

const initMap = () => {
  if (!mapRef.value) return

  if (typeof AMap === 'undefined') {
    alert('高德地图加载失败，请检查 index.html 中的 Key 和安全密钥')
    return
  }

  if (map) {
    map.destroy()
  }

  const firstSpot = spots.value[0]

  map = new AMap.Map(mapRef.value, {
    zoom: 12,
    center: firstSpot
      ? [Number(firstSpot.lng), Number(firstSpot.lat)]
      : [116.397, 39.916],
    viewMode: '2D'
  })

  const infoWindow = new AMap.InfoWindow({
    offset: new AMap.Pixel(0, -30)
  })

  const path: number[][] = []

  spots.value.forEach((item: any) => {
    const lng = Number(item.lng)
    const lat = Number(item.lat)

    if (!lng || !lat) return

    path.push([lng, lat])

    const marker = new AMap.Marker({
      position: [lng, lat],
      title: item.name,
      map
    })

    marker.on('click', () => {
      const imageHtml = item.cover_url
        ? `<img src="${item.cover_url}" style="width:220px;height:120px;object-fit:cover;border-radius:8px;margin-bottom:8px;" />`
        : ''

      infoWindow.setContent(`
        <div style="width:240px;">
          ${imageHtml}
          <h3 style="margin:4px 0;">${item.name}</h3>
          <p>地址：${item.address || ''}</p>
          <p>门票：${item.price || ''}</p>
          <p>标签：${item.tags || ''}</p>
        </div>
      `)

      infoWindow.open(map, marker.getPosition())
    })
  })

  // 简单路线连线：按景点数据顺序连接
  if (path.length > 1) {
    new AMap.Polyline({
      path,
      strokeColor: '#409eff',
      strokeWeight: 5,
      strokeOpacity: 0.8,
      map
    })
  }

  if (path.length > 0) {
    map.setFitView()
  }
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
  max-width: 1100px;
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

.map {
  width: 100%;
  height: 520px;
  margin-top: 25px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #eee;
}

.list {
  margin-top: 25px;
}

.spot {
  background: #f8f9fb;
  padding: 18px;
  border-radius: 10px;
  margin-bottom: 15px;
}

.cover {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 12px;
}

@media screen and (max-width: 768px) {
  .page {
    padding: 15px;
  }

  .card {
    padding: 20px;
  }

  .map {
    height: 360px;
  }

  .top {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>