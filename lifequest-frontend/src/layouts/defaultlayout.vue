<template>
  <div class="layout-container">
    <LQheader />
    <main class="main-content">
      <router-view></router-view>
    </main>
    <LQfooter />
  </div>
</template>

<script>
import LQheader from '../components/LQheader.vue'
import LQfooter from '../components/LQfooter.vue'

export default {
  name: 'DefaultLayout',
  components: {
    LQheader,
    LQfooter
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}
</style>