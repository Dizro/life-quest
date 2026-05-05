<template>
  <div class="headless-layout">
    <router-view></router-view>
    <LQfooter />
  </div>
</template>

<script>
import LQfooter from '../components/LQfooter.vue'
export default {
  name: 'HeadlessLayout',
    components: {
    LQfooter
  }
}
</script>

<style scoped>
.headless-layout {
  min-height: 100vh;
}
</style>