<template>
    <div class="page">
        <div class="card">
            <div class="top">
                <h2>{{ t('title') }}</h2>

                <div class="top-buttons">
                    <button class="list-btn" @click="emit('go-list')">{{ t('myTrips') }}</button>
                    <button class="map-btn" @click="emit('go-map')">{{ t('map') }}</button>

                    <button v-if="role === 'admin'" class="scenic-btn" @click="emit('go-scenic')">
                        {{ t('scenic') }}
                    </button>

                    <button v-if="role === 'admin'" class="admin-btn" @click="emit('go-admin')">
                        {{ t('dashboard') }}
                    </button>


                    <button class="theme-btn" @click="emit('toggle-theme')">{{ t('theme') }}</button>
                    <button class="lang-btn" @click="toggleLang">中 / EN</button>
                    <button class="logout" @click="logout">{{ t('logout') }}</button>
                </div>
            </div>

            <div class="form">
                <input v-model="destination" :placeholder="t('destination')" />
                <input v-model.number="days" type="number" :placeholder="t('days')" />
                <input v-model="budget" :placeholder="t('budget')" />
                <input v-model="preference" :placeholder="t('preference')" />

                <button @click="generatePlan" :disabled="loading">
                    {{ loading ? t('generating') : t('generate') }}
                </button>

                <button class="save-btn" @click="savePlan" :disabled="!result">
                    {{ t('save') }}
                </button>
            </div>

            <div class="result">
                <h3>{{ t('result') }}</h3>
                <pre>{{ result || t('emptyResult') }}</pre>
            </div>

            <div v-if="result" class="route-map-box">
                <h3>行程地图路线</h3>
                <div ref="mapRef" class="route-map"></div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { t, toggleLang } from '../i18n'
import request, { API_BASE_URL } from '../api/request'

const destination = ref('北京')
const days = ref(3)
const budget = ref('3000元')
const preference = ref('美食、历史文化、轻松游')
const result = ref('')
const loading = ref(false)
const emit = defineEmits(['go-list', 'go-scenic', 'go-admin', 'go-map', 'toggle-theme'])

const role = localStorage.getItem('role')

declare const AMap: any

const mapRef = ref<HTMLDivElement | null>(null)
let map: any = null

const generatePlan = async () => {
  result.value = ''
  loading.value = true

  try {
    // 这里保留你原来的 AI 流式生成代码
    // 生成完成后，result.value 已经有内容了

  } catch (e) {
    console.error('AI规划生成失败：', e)
    result.value = 'AI生成失败，请检查后端是否正常运行'
    loading.value = false
    return
  }

  // 景点提取单独处理，失败也不影响 AI 结果
  try {
    await request.post('/ai/extract-spots', {
      destination: destination.value,
      content: result.value
    })
  } catch (e) {
    console.warn('景点提取失败，但不影响AI规划结果：', e)
  }

  loading.value = false
}
const searchPlace = (keyword: string) => {
  return new Promise<any>((resolve) => {
    AMap.plugin('AMap.PlaceSearch', () => {
      const placeSearch = new AMap.PlaceSearch({
        city: destination.value,
        pageSize: 1
      })

      placeSearch.search(keyword, (status: string, resultData: any) => {
        if (
          status === 'complete' &&
          resultData.poiList &&
          resultData.poiList.pois &&
          resultData.poiList.pois.length > 0
        ) {
          const poi = resultData.poiList.pois[0]

          resolve({
            name: keyword,
            address: poi.address,
            lng: poi.location.lng,
            lat: poi.location.lat
          })
        } else {
          resolve(null)
        }
      })
    })
  })
}

const drawFallbackLine = (points: any[]) => {
  const path = points.map((item: any) => [Number(item.lng), Number(item.lat)])

  new AMap.Polyline({
    path,
    strokeColor: '#409eff',
    strokeWeight: 5,
    strokeOpacity: 0.85,
    map
  })
}

const drawDrivingRoute = (points: any[]) => {
  if (points.length < 2) return

  AMap.plugin('AMap.Driving', () => {
    const driving = new AMap.Driving({
      map,
      hideMarkers: true
    })

    const start = new AMap.LngLat(points[0].lng, points[0].lat)
    const end = new AMap.LngLat(points[points.length - 1].lng, points[points.length - 1].lat)

    const waypoints = points.slice(1, -1).map((item: any) => {
      return new AMap.LngLat(item.lng, item.lat)
    })

    driving.search(start, end, { waypoints }, (status: string) => {
      if (status !== 'complete') {
        drawFallbackLine(points)
      }
    })
  })
}

const renderTripMap = async () => {
  if (!mapRef.value) return

  if (typeof AMap === 'undefined') {
    alert('高德地图没有加载成功')
    return
  }

  if (map) {
    map.destroy()
  }

  // 1. 让后端从 AI 结果里提取景点名
  const extractRes = await request.post('/ai/extract-spots', {
    destination: destination.value,
    content: result.value,
    language: localStorage.getItem('lang') || 'zh'
  })

  const spotNames = extractRes.data.data || []

  if (spotNames.length === 0) {
    alert('没有从 AI 结果中提取到景点名称')
    return
  }

  // 2. 用高德搜索每个景点坐标
  const searchedPoints: any[] = []

  for (const name of spotNames) {
    const point = await searchPlace(name)

    if (point) {
      searchedPoints.push(point)
    }
  }

  if (searchedPoints.length === 0) {
    alert('高德没有搜索到这些景点的位置')
    return
  }

  // 3. 创建地图
  const first = searchedPoints[0]

  map = new AMap.Map(mapRef.value, {
    zoom: 12,
    center: [Number(first.lng), Number(first.lat)],
    viewMode: '2D'
  })

  const infoWindow = new AMap.InfoWindow({
    offset: new AMap.Pixel(0, -30)
  })

  // 4. 添加 Marker
  searchedPoints.forEach((point: any, index: number) => {
    const marker = new AMap.Marker({
      position: [Number(point.lng), Number(point.lat)],
      title: point.name,
      label: {
        content: `${index + 1}`,
        direction: 'top'
      },
      map
    })

    marker.on('click', () => {
      infoWindow.setContent(`
        <div style="width:220px;">
          <h3>${index + 1}. ${point.name}</h3>
          <p>地址：${point.address || ''}</p>
        </div>
      `)

      infoWindow.open(map, marker.getPosition())
    })
  })

  // 5. 根据搜索出的景点生成路线
  if (searchedPoints.length >= 2) {
    drawDrivingRoute(searchedPoints)
  }

  map.setFitView()
}

const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    location.reload()
}

const savePlan = async () => {
    if (!result.value) {
        alert('请先生成旅游规划')
        return
    }

    try {
        await request.post('/travel-plans', {
            destination: destination.value,
            days: days.value,
            preference: preference.value,
            plan_content: result.value
        })

        alert('保存成功')
    } catch (error) {
        console.error(error)
        alert('保存失败，请检查登录状态或后端接口')
    }
}
</script>

<style scoped>
.page {
    min-height: 100vh;
    background: #f5f7fb;
    padding: 40px;
}

.card {
    max-width: 900px;
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
    height: 42px;
    padding: 0 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
}

button {
    height: 42px;
    border: none;
    border-radius: 6px;
    background: #409eff;
    color: white;
    cursor: pointer;
}

button:disabled {
    background: #a0cfff;
    cursor: not-allowed;
}

.logout {
    width: 100px;
    background: #f56c6c;
}

.result {
    margin-top: 25px;
}

pre {
    min-height: 300px;
    white-space: pre-wrap;
    line-height: 1.7;
    background: #f8f9fb;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #eee;
}

.save-btn {
    background: #67c23a;
}

.save-btn:hover {
    background: #529b2e;
}

.top-buttons {
    display: flex;
    gap: 10px;
}

.list-btn {
    width: 100px;
    background: #67c23a;
}

.scenic-btn {
    width: 100px;
    background: #e6a23c;
}

.admin-btn {
    width: 100px;
    background: #909399;
}

.map-btn {
    width: 100px;
    background: #8e44ad;
}

.theme-btn {
    width: 100px;
    background: #606266;
}

.lang-btn {
    width: 100px;
    background: #303133;
}
.route-map-box {
  margin-top: 25px;
}

.route-map-box h3 {
  text-align: center;
  color: #666;
}

.route-map {
  width: 100%;
  height: 450px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #eee;
}
</style>