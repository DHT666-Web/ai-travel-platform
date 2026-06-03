# AI智能旅游规划平台

## 一、项目简介

本项目是一个基于 Vue3 + FastAPI + MySQL + DeepSeek 的 AI 智能旅游规划平台。

系统支持用户登录注册、AI 流式生成旅游行程、行程保存与管理、景点管理、地图路线展示、后台数据统计、主题切换、中英文切换、文件上传等功能。

项目重点实现了 RAG + 轻量 Agent 的 AI 规划流程：系统会先检索本地景点数据，再结合用户输入生成旅游规划，减少大模型胡编，提高行程规划的准确性和可解释性。

---

## 二、技术栈

### 前端

- Vue3
- TypeScript
- Vite
- Axios
- ECharts
- 高德地图 JS API

### 后端

- FastAPI
- SQLAlchemy
- PyMySQL
- JWT 鉴权
- DeepSeek API
- 文件上传

### 数据库

- MySQL

---

## 三、核心功能

### 1. 用户登录注册

- 支持用户注册
- 支持用户登录
- 使用 JWT Token 进行身份认证

### 2. 权限控制

系统包含两种角色：

- 普通用户 user
- 管理员 admin

普通用户可以：

- 生成 AI 行程
- 保存自己的行程
- 查看自己的行程
- 删除自己的行程
- 查看地图路线

管理员可以：

- 使用普通用户全部功能
- 管理景点数据
- 查看后台数据大屏
- 上传景点封面图

### 3. AI 智能旅游规划

用户输入：

- 目的地
- 天数
- 预算
- 偏好

系统调用 DeepSeek API，以流式输出方式生成旅游规划。

### 4. RAG 景点检索增强

AI 生成前，系统会先从本地 `scenic_spots` 景点表中检索当前目的地相关景点，再把景点资料拼接进 Prompt 中，让 AI 优先参考本地数据生成行程。

### 5. 轻量 Agent 流程

AI 规划流程被拆分为：

1. 分析用户需求
2. 检索本地景点
3. 构造 Prompt
4. 调用 DeepSeek 生成行程
5. 保存 AI 调用记录

### 6. 行程管理

- 保存 AI 生成的行程
- 查看我的行程
- 删除行程
- 普通用户只能管理自己的行程
- 管理员可以查看全部行程

### 7. 景点管理

管理员可以：

- 新增景点
- 查询景点
- 删除景点
- 上传景点封面图

### 8. 地图路线展示

系统会根据 AI 生成的行程内容自动提取景点名称，并调用高德地图搜索景点位置，在地图上展示景点 Marker 和路线。

### 9. 后台数据大屏

后台统计展示：

- 用户总数
- 行程数量
- 景点数量
- AI 调用次数
- 热门目的地 Top10

### 10. 其他亮点

- 深色 / 浅色主题切换
- 中文 / 英文切换
- AI 输出语言跟随界面语言变化
- 移动端响应式适配
- 文件上传与景点封面图展示

---

## 四、项目目录结构

```text
ai-travel-platform
├── backend
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── agent_service.py
│   ├── requirements.txt
│   ├── .env
│   └── static
│       └── uploads
│
├── frontend
│   ├── src
│   │   ├── api
│   │   │   └── request.ts
│   │   ├── views
│   │   │   ├── Login.vue
│   │   │   ├── AiPlan.vue
│   │   │   ├── TripList.vue
│   │   │   ├── ScenicManage.vue
│   │   │   ├── AdminDashboard.vue
│   │   │   └── MapView.vue
│   │   ├── i18n.ts
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── nginx
├── docker-compose.yml
└── README.md