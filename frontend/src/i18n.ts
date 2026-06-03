import { ref } from 'vue'

export const lang = ref(localStorage.getItem('lang') || 'zh')

const messages: any = {
  zh: {
    title: 'AI智能旅游规划',
    myTrips: '我的行程',
    map: '地图展示',
    scenic: '景点管理',
    dashboard: '数据大屏',
    theme: '主题切换',
    logout: '退出登录',
    destination: '目的地，例如：北京',
    days: '天数，例如：3',
    budget: '预算，例如：3000元',
    preference: '偏好，例如：美食、历史文化、轻松游',
    generate: '生成旅游规划',
    generating: '生成中...',
    save: '保存行程',
    result: 'AI生成结果',
    emptyResult: '这里会显示 AI 生成的行程规划...'
  },
  en: {
    title: 'AI Travel Planner',
    myTrips: 'My Trips',
    map: 'Map',
    scenic: 'Scenic Manage',
    dashboard: 'Dashboard',
    theme: 'Theme',
    logout: 'Logout',
    destination: 'Destination, e.g. Beijing',
    days: 'Days, e.g. 3',
    budget: 'Budget, e.g. 3000 CNY',
    preference: 'Preference, e.g. food, history, relaxing',
    generate: 'Generate Plan',
    generating: 'Generating...',
    save: 'Save Trip',
    result: 'AI Result',
    emptyResult: 'AI generated travel plan will be shown here...'
  }
}

export const t = (key: string) => {
  return messages[lang.value][key] || key
}

export const toggleLang = () => {
  lang.value = lang.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('lang', lang.value)
}