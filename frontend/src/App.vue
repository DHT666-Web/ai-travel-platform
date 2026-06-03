<template>
  <div :class="theme">
    <Login v-if="!token" />

    <AiPlan
      v-else-if="page === 'ai'"
      @go-list="page = 'list'"
      @go-scenic="page = 'scenic'"
      @go-admin="page = 'admin'"
      @go-map="page = 'map'"
      @toggle-theme="toggleTheme"
    />

    <TripList
      v-else-if="page === 'list'"
      @back="page = 'ai'"
    />

    <ScenicManage
      v-else-if="page === 'scenic'"
      @back="page = 'ai'"
    />

    <AdminDashboard
      v-else-if="page === 'admin'"
      @back="page = 'ai'"
    />

    <MapView
      v-else
      @back="page = 'ai'"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Login from './views/Login.vue'
import AiPlan from './views/AiPlan.vue'
import TripList from './views/TripList.vue'
import ScenicManage from './views/ScenicManage.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import MapView from './views/MapView.vue'

const token = ref(localStorage.getItem('token'))
const page = ref('ai')

const theme = ref(localStorage.getItem('theme') || 'light')

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('theme', theme.value)
}
</script>