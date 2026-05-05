<template>
  <div class="page-wrapper">
    <div class="profile-page">
      <header class="page-header">
        <h1 class="page-title">Профиль</h1>
        <p class="page-subtitle">Статистика твоего героя</p>
      </header>

      <div class="profile-card">
        <div class="avatar-col">
          <div class="avatar-circle">{{ userInitial }}</div>
          <h2 class="hero-name">{{ authStore.displayName || 'Герой' }}</h2>
          <div class="hero-level">Уровень {{ authStore.userLevel }}</div>
        </div>

        <div class="stats-col">
          <div class="stat-box">
            <span class="stat-icon">✨</span>
            <div class="stat-info">
              <span class="stat-value">{{ authStore.userXP }}</span>
              <span class="stat-label">Опыт</span>
            </div>
          </div>
          <div class="stat-box">
            <span class="stat-icon">💰</span>
            <div class="stat-info">
              <span class="stat-value">{{ authStore.gold }}</span>
              <span class="stat-label">Золото</span>
            </div>
          </div>
          <div class="stat-box">
            <span class="stat-icon">💎</span>
            <div class="stat-info">
              <span class="stat-value">{{ authStore.crystals }}</span>
              <span class="stat-label">Кристаллы</span>
            </div>
          </div>
          <div class="stat-box">
            <span class="stat-icon">🔥</span>
            <div class="stat-info">
              <span class="stat-value">{{ authStore.streakDays }}</span>
              <span class="stat-label">Стрик (дней)</span>
            </div>
          </div>
        </div>
      </div>

      <div class="xp-section">
        <h3 class="section-title">Прогресс до Уровня {{ authStore.userLevel + 1 }}</h3>
        <div class="xp-bar-container">
          <div class="xp-bar" :style="{ width: xpPercentage + '%' }"></div>
        </div>
        <div class="xp-text">{{ authStore.userXP }} / {{ nextLevelXP }} XP</div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ProfilePage',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  computed: {
    userInitial() {
      const name = this.authStore.displayName
      return name ? name[0].toUpperCase() : 'Л'
    },
    nextLevelXP() {
      return Math.floor(100 * Math.pow(this.authStore.userLevel, 1.5))
    },
    xpPercentage() {
      const p = (this.authStore.userXP / this.nextLevelXP) * 100
      return Math.min(Math.max(p, 0), 100)
    }
  }
}
</script>

<style scoped>
.page-wrapper {
  min-height: calc(100vh - 67px);
  background: linear-gradient(160deg, #f4f0ff 0%, #e8d5ff 40%, #c9a6ff 100%);
  padding: 32px 24px;
}

.profile-page {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 8px;
}

.page-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 36px;
  font-weight: 700;
  color: #2a1a5e;
  margin-bottom: 8px;
}

.page-subtitle {
  font-family: 'Varela Round', sans-serif;
  font-size: 16px;
  color: #5a4a7a;
}

.profile-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  display: flex;
  gap: 40px;
  align-items: center;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
}

.avatar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 150px;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  background: #e8d5ff;
  border: 4px solid #9a62ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Varela Round', sans-serif;
  font-size: 40px;
  font-weight: 700;
  color: #432874;
}

.hero-name {
  font-family: 'Varela Round', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #2a1a5e;
  margin: 0;
}

.hero-level {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #7c5cbf;
  background: #f4f0ff;
  padding: 4px 12px;
  border-radius: 12px;
}

.stats-col {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #faf8ff;
  border: 1px solid #f0ebff;
  padding: 16px;
  border-radius: 16px;
  transition: transform 0.2s;
}

.stat-box:hover {
  transform: translateY(-2px);
  border-color: #d5c8ff;
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: 'Varela Round', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #2a1a5e;
}

.stat-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 12px;
  color: #7c5cbf;
}

.xp-section {
  background: #fff;
  border-radius: 20px;
  padding: 24px 32px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
}

.section-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #2a1a5e;
  margin-bottom: 16px;
}

.xp-bar-container {
  height: 16px;
  background: #f4f0ff;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 8px;
}

.xp-bar {
  height: 100%;
  background: linear-gradient(90deg, #9a62ff, #c4aeff);
  border-radius: 8px;
  transition: width 0.3s ease;
}

.xp-text {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #7c5cbf;
  text-align: right;
}

@media (max-width: 600px) {
  .profile-card {
    flex-direction: column;
    gap: 24px;
    padding: 24px;
  }
  .stats-col {
    width: 100%;
  }
}
</style>