<template>
  <div class="app-wrapper">
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1 0 auto;
  width: 100%;
}
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.router-view {
  flex: 1;
}
</style>
