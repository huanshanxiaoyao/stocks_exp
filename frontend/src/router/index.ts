import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/stock-detail',  // 修改这里，匹配 Home.vue 中的路径
      name: 'stock',
      component: () => import('@/components/StockDetail.vue')
    },
    {
      path: '/strategy',
      name: 'strategy',
      component: () => import('@/components/StrategySimulation.vue')
    }
  ]
})

export default router