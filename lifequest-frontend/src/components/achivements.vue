<template>
  <div class="page-wrapper">
    <div class="achievements-page">
      <header class="page-header">
        <h1 class="page-title">Достижения</h1>
        <p class="page-subtitle">Выполняй особые условия, чтобы получать уникальные награды и кристаллы.</p>
      </header>

      <div class="achievements-grid">
        <div 
          v-for="ach in achievements" 
          :key="ach.id" 
          class="achievement-card"
          :class="{ unlocked: ach.unlocked }"
        >
          <div class="ach-icon-wrapper">
            <span class="ach-icon">{{ ach.icon }}</span>
          </div>
          <div class="ach-info">
            <h3 class="ach-title">{{ ach.title }}</h3>
            <p class="ach-desc">{{ ach.description }}</p>
          </div>
          <div class="ach-reward">
            <span v-if="ach.unlocked" class="status-label done">✅ Выполнено!</span>
            <span v-else class="status-label not-done">🔒 Не выполнено</span>
            <span class="reward-badge">💎 +{{ ach.reward }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { achievementsApi } from '@/services/api'

const ICON_MAP = {
  'first_blood': '🗡️',
  'streak_7': '🔥',
  'streak_30': '🔥',
  'level_5': '⭐',
  'level_10': '⭐',
  'tasks_10': '⚔️',
  'tasks_50': '🏹',
  'tasks_100': '🏹',
  'shopaholic': '🛍️',
  'habit_master': '🔄',
}

export default {
  name: 'AchievementsPage',
  data() {
    return {
      achievements: []
    }
  },
  async created() {
    await this.loadAchievements()
  },
  methods: {
    async loadAchievements() {
      try {
        const data = await achievementsApi.getAll()
        this.achievements = (data.achievements || data || []).map(a => ({
          id: a.id,
          title: a.title || a.name,
          description: a.description,
          reward: a.crystal_reward || a.reward || 5,
          icon: ICON_MAP[a.key] || '🏅',
          unlocked: a.unlocked || false,
        }))
      } catch (err) {
        console.error('Achievements load error:', err)
        // Fallback to static list
        this.achievements = [
          { id: 1, title: 'Первая кровь', description: 'Выполни свою первую задачу.', reward: 5, icon: '🗡️', unlocked: false },
          { id: 2, title: 'Упорство', description: 'Поддерживай стрик активности 7 дней подряд.', reward: 15, icon: '🔥', unlocked: false },
          { id: 3, title: 'Авантюрист', description: 'Достигни 5 уровня.', reward: 20, icon: '⭐', unlocked: false },
          { id: 4, title: 'Шопоголик', description: 'Купи 3 предмета в магазине.', reward: 10, icon: '🛍️', unlocked: false },
          { id: 5, title: 'Охотник за головами', description: 'Выполни 50 задач с оценкой сложности 5 и выше.', reward: 50, icon: '🏹', unlocked: false },
          { id: 6, title: 'Мастер привычек', description: 'Отметь привычку 100 раз.', reward: 30, icon: '🔄', unlocked: false },
        ]
      }
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

.achievements-page {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 16px;
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

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.achievement-card {
  background: #fff;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 8px 24px rgba(66,41,116,0.08);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
}

.achievement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(66,41,116,0.15);
}

.achievement-card:not(.unlocked) {
  opacity: 0.7;
  filter: grayscale(100%);
}

.achievement-card.unlocked {
  border-color: #d5c8ff;
  background: #faf8ff;
}

.ach-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: #f4f0ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.achievement-card.unlocked .ach-icon-wrapper {
  background: linear-gradient(135deg, #e8d5ff, #c4aeff);
}

.ach-icon {
  font-size: 32px;
}

.ach-info {
  flex: 1;
}

.ach-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #2a1a5e;
  margin-bottom: 8px;
}

.ach-desc {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #7c5cbf;
  line-height: 1.4;
}

.ach-reward {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f0ebff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 10px;
}
.status-label.done { background: #c6f6d5; color: #22543d; }
.status-label.not-done { background: #f0ebff; color: #718096; }

.reward-badge {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #3182ce;
  background: #ebf8ff;
  padding: 6px 12px;
  border-radius: 12px;
}

/* ─── Адаптив ─── */
@media (max-width: 768px) {
  .achievements-page { padding: 24px 16px; }
  .page-title { font-size: 28px; }
  .achievements-grid { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
}

@media (max-width: 480px) {
  .achievements-page { padding: 16px 12px; }
  .page-title { font-size: 24px; }
  .page-subtitle { font-size: 13px; }
  .achievements-grid { grid-template-columns: 1fr; gap: 12px; }
  .achievement-card { padding: 14px; border-radius: 14px; gap: 12px; }
  .ach-icon-wrapper { width: 48px; height: 48px; border-radius: 12px; }
  .ach-icon { font-size: 26px; }
  .ach-title { font-size: 16px; }
  .ach-desc { font-size: 13px; }
}
</style>