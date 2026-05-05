import { createWebHistory, createRouter } from 'vue-router'

import DefaultLayout from '../layouts/defaultlayout.vue'
import HeadlessLayout from '../layouts/headlesslayout.vue'

import mainpage from '../components/mainpage.vue'
import profile from '../components/profile.vue'
import shop from '../components/shop.vue'
import achivements from '../components/achivements.vue'
import groups from '../components/groups.vue'
import statistics from '../components/statistics.vue'
import register from '../components/register.vue'
import character from '../components/character.vue'
import onboarding from '../components/onboarding.vue'
import chat from '../components/chat.vue'

const routes = [
  // Страницы без авторизации
  {
    path: '/',
    component: HeadlessLayout,
    children: [
      { path: '', name: 'Register', component: register },
      { path: '/onboarding', name: 'Onboarding', component: onboarding },
    ],
  },

  // Страницы требующие авторизации (meta.requiresAuth = true)
  {
    path: '/',
    component: DefaultLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '/mainpage', name: 'Main', component: mainpage },
      { path: '/profile', name: 'Profile', component: profile },
      { path: '/shop', name: 'Shop', component: shop },
      { path: '/achivements', name: 'Achivements', component: achivements },
      { path: '/groups', name: 'Groups', component: groups },
      { path: '/statistics', name: 'Statistics', component: statistics },
      { path: '/character', name: 'Character', component: character },
      { path: '/chat', name: 'Chat', component: chat },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Navigation Guard ──────────────────────────────────────────────────────
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !token) {
    // Не авторизован — на страницу входа
    next({ name: 'Register' })
  } else if (to.name === 'Register' && token) {
    // Уже авторизован — на главную
    next({ name: 'Main' })
  } else {
    next()
  }
})

export default router