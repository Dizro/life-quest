import {createWebHistory, createRouter } from 'vue-router'

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

const routes = [
  { path: '/', component: HeadlessLayout, children: 
    [{path:'', name: 'Register', component: register }]},
  
  { path: '/', component: DefaultLayout, children:[
    { path: '/mainpage', name: 'Main', component: mainpage },
    { path: '/profile', name: 'Profile', component: profile },
    { path: '/shop', name: 'Shop', component: shop },
    { path: '/achivements', name: 'Achivements', component: achivements },
    { path: '/groups', name: 'Groups', component: groups },
    { path: '/statistics', name: 'Statistics', component: statistics },
    { path: '/character', name: 'Character', component: character }
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router