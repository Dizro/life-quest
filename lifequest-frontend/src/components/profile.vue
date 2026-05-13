<template>
  <div class="page-wrapper">
    <div class="profile-page">
      <header class="page-header">
        <h1 class="page-title">Профиль</h1>
        <p class="page-subtitle">Статистика твоего героя</p>
      </header>

      <div class="profile-card">
        <div class="avatar-col">
          <div class="avatar-scene">
            <img :src="getAsset('bodies', charStore.selectedBody)" class="avatar-body" alt="" />
            <img v-if="charStore.selectedTop" :src="getAsset('clothes/tops', charStore.selectedTop)" class="avatar-body" alt="" />
            <img :src="getAsset('hair', charStore.selectedHair)" class="avatar-body" alt="" />
          </div>
          <h2 class="hero-name">{{ authStore.displayName || 'Герой' }}</h2>
          <div class="hero-class">{{ authStore.user?.character_class || 'Авантюрист' }}</div>
          <div class="hero-level">{{ authStore.user?.rank_title || 'Новобранец' }} — Ур. {{ authStore.userLevel }}</div>
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
              <span class="stat-label">Стрик</span>
            </div>
          </div>
          <div class="stat-box">
            <span class="stat-icon">🏅</span>
            <div class="stat-info">
              <span class="stat-value">{{ totalCompleted }}</span>
              <span class="stat-label">Квестов</span>
            </div>
          </div>
          <div class="stat-box">
            <span class="stat-icon">📈</span>
            <div class="stat-info">
              <span class="stat-value">{{ authStore.user?.max_streak || 0 }}</span>
              <span class="stat-label">Макс. стрик</span>
            </div>
          </div>
        </div>
      </div>

      <div class="xp-section">
        <h3 class="section-title">Прогресс до Уровня {{ authStore.userLevel + 1 }}</h3>
        <div class="xp-bar-container">
          <div class="xp-bar" :style="{ width: xpPercentage + '%' }"></div>
        </div>
        <div class="xp-text">{{ authStore.userXP }} / {{ authStore.xpToNext }} XP</div>
      </div>

      <!-- Достижения -->
      <div class="achievements-section">
        <h3 class="section-title">🏅 Достижения</h3>
        <div v-if="achievements.length" class="achievements-grid">
          <div 
            v-for="a in achievements" :key="a.id" 
            class="achievement-card" 
            :class="{ unlocked: a.unlocked }"
          >
            <div class="ach-icon">{{ a.icon }}</div>
            <div class="ach-info">
              <div class="ach-name">{{ a.name }}</div>
              <div class="ach-desc">{{ a.description }}</div>
              <div class="ach-progress-bar">
                <div class="ach-progress-fill" :style="{ width: Math.min(a.progress, 100) + '%' }"></div>
              </div>
              <div class="ach-progress-text">{{ a.current_value }} / {{ a.target_value }}</div>
            </div>
            <div v-if="a.unlocked" class="ach-status done">✅ Выполнено!</div>
            <div v-else class="ach-status locked">🔒 Не выполнено</div>
          </div>
        </div>
        <div v-else class="empty-ach">Загружаем достижения...</div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'
import { analyticsApi, achievementsApi } from '@/services/api'

export default {
  name: 'ProfilePage',
  setup() {
    const authStore = useAuthStore()
    const charStore = useCharacterStore()
    return { authStore, charStore }
  },
  data() {
    return {
      totalCompleted: 0,
      achievements: []
    }
  },
  async created() {
    try {
      const data = await analyticsApi.getDashboard()
      this.totalCompleted = data.overview?.total_tasks_completed || 0
    } catch {}
    try {
      const res = await achievementsApi.getAll()
      this.achievements = res.achievements || []
    } catch {}
  },
  computed: {
    xpPercentage() {
      const p = (this.authStore.userXP / this.authStore.xpToNext) * 100
      return Math.min(Math.max(p, 0), 100)
    }
  },
  methods: {
    getAsset(folder, name, ext = '.png') {
      if (!name || name === 'undefined') return ''
      try {
        return new URL(`../assets/${folder}/${name}${ext}`, import.meta.url).href
      } catch { return '' }
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

.avatar-scene {
  width: 120px;
  height: 160px;
  position: relative;
  background: rgba(154,98,255,0.08);
  border: 3px solid #d5c8ff;
  border-radius: 16px;
  overflow: hidden;
}

.avatar-body {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.hero-name {
  font-family: 'Varela Round', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #2a1a5e;
  margin: 0;
}

.hero-class {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #9a62ff;
  font-weight: 700;
}

.hero-level {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #7c5cbf;
  background: #f4f0ff;
  padding: 4px 12px;
  border-radius: 12px;
}

.stats-col {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
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

@media (max-width: 768px) {
  .stats-col {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .profile-card {
    flex-direction: column;
    gap: 24px;
    padding: 24px;
  }
  .stats-col {
    width: 100%;
    grid-template-columns: repeat(2, 1fr);
  }
  .page-title { font-size: 28px; }
}

@media (max-width: 400px) {
  .stats-col {
    grid-template-columns: 1fr;
  }
}

/* ─── Достижения ─── */
.achievements-section {
  background: #fff;
  border-radius: 20px;
  padding: 24px 32px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
}

.achievements-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.achievement-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 16px;
  border: 2px solid #f0ebff;
  background: #faf8ff;
  transition: all 0.2s;
}
.achievement-card:hover { border-color: #d5c8ff; transform: translateY(-1px); }
.achievement-card.unlocked { border-color: #48bb78; background: #f0fff4; }

.ach-icon { font-size: 32px; flex-shrink: 0; }
.ach-info { flex: 1; min-width: 0; }
.ach-name { font-family: 'Varela Round', sans-serif; font-size: 15px; font-weight: 700; color: #2a1a5e; }
.ach-desc { font-size: 12px; color: #718096; margin-top: 2px; }

.ach-progress-bar {
  height: 6px; background: #e2e8f0; border-radius: 6px; margin-top: 8px; overflow: hidden;
}
.ach-progress-fill {
  height: 100%; background: linear-gradient(90deg, #9a62ff, #48bb78); border-radius: 6px; transition: width 0.4s ease;
}
.achievement-card.unlocked .ach-progress-fill { background: #48bb78; }

.ach-progress-text { font-size: 11px; color: #a0aec0; margin-top: 3px; font-weight: 700; }
.ach-status {
  font-size: 12px; font-weight: 700; flex-shrink: 0; padding: 5px 10px;
  border-radius: 10px; white-space: nowrap;
  font-family: 'Varela Round', sans-serif;
}
.ach-status.done { background: #c6f6d5; color: #22543d; }
.ach-status.locked { background: #f0ebff; color: #718096; }

.empty-ach {
  text-align: center; color: #a0aec0; font-weight: bold; padding: 24px;
}
</style>