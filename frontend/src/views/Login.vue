<template>
  <div class="login-page">
    <div class="login-box">
      <h2>AI智能旅游规划平台</h2>

      <input v-model="username" placeholder="请输入用户名" />
      <input v-model="password" type="password" placeholder="请输入密码" />

      <button @click="handleLogin">登录</button>

      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import request from '../api/request'

const username = ref('admin')
const password = ref('123456')
const message = ref('')

const handleLogin = async () => {
  try {
    const res = await request.post('/login', {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('token', res.data.token)
    localStorage.setItem('role', res.data.role)
    message.value = '登录成功，token 已保存'
    location.reload()

    console.log('登录成功：', res.data)
  } catch (error) {
    console.error(error)
    message.value = '登录失败，请检查用户名或密码'
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  background: #f5f7fb;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  width: 360px;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

h2 {
  text-align: center;
}

input {
  height: 40px;
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

button:hover {
  background: #337ecc;
}

p {
  text-align: center;
  color: #409eff;
}
</style>