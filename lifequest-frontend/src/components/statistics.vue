<template>
  <div class="page-wrapper">
    <div class="statistics-page">
      <header class="page-header">
        <h1 class="page-title">Статистика</h1>
        <p class="page-subtitle">Твои достижения и активность в LifeQuest</p>
      </header>

      <div class="stats-grid">
        <!-- Main Stats Overview -->
        <div class="stat-card overview-card">
          <h2 class="card-title">Обзор</h2>
          <div class="overview-stats">
            <div class="overview-item">
              <span class="o-icon">🔥</span>
              <div class="o-info">
                <span class="o-value">{{ authStore.streakDays }}</span>
                <span class="o-label">Дней подряд</span>
              </div>
            </div>
            <div class="overview-item">
              <span class="o-icon">⚔️</span>
              <div class="o-info">
                <span class="o-value">124</span>
                <span class="o-label">Задач выполнено</span>
              </div>
            </div>
            <div class="overview-item">
              <span class="o-icon">⭐</span>
              <div class="o-info">
                <span class="o-value">{{ authStore.userLevel }}</span>
                <span class="o-label">Уровень</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Heatmap (Activity Calendar) -->
        <div class="stat-card heatmap-card">
          <h2 class="card-title">Активность (последние 30 дней)</h2>
          <div class="heatmap-container">
            <div class="heatmap-grid">
              <div 
                v-for="(day, i) in heatmapData" 
                :key="i"
                class="heatmap-cell"
                :class="getHeatmapClass(day.count)"
                :title="`${day.date}: ${day.count} задач`"
              ></div>
            </div>
            <div class="heatmap-legend">
              <span>Меньше</span>
              <div class="legend-scale">
                <div class="heatmap-cell level-0"></div>
                <div class="heatmap-cell level-1"></div>
                <div class="heatmap-cell level-2"></div>
                <div class="heatmap-cell level-3"></div>
                <div class="heatmap-cell level-4"></div>
              </div>
              <span>Больше</span>
            </div>
          </div>
        </div>

        <!-- Weekly Progress -->
        <div class="stat-card chart-card">
          <h2 class="card-title">Опыт за неделю</h2>
          <div class="bar-chart">
            <div v-for="(day, i) in weeklyData" :key="i" class="bar-col">
              <div class="bar-fill" :style="{ height: `${day.percent}%` }">
                <span class="bar-tooltip">{{ day.xp }} XP</span>
              </div>
              <span class="bar-label">{{ day.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'StatisticsPage',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      // Mock Data for MVP
      weeklyData: [
        { label: 'Пн', xp: 120, percent: 40 },
        { label: 'Вт', xp: 250, percent: 80 },
        { label: 'Ср', xp: 300, percent: 100 },
        { label: 'Чт', xp: 50,  percent: 20 },
        { label: 'Пт', xp: 180, percent: 60 },
        { label: 'Сб', xp: 210, percent: 70 },
        { label: 'Вс', xp: 90,  percent: 30 },
      ],
      heatmapData: []
    }
  },
  created() {
    this.generateHeatmap()
  },
  methods: {
    generateHeatmap() {
      // Generate 30 days of mock data
      const data = []
      const today = new Date()
      for (let i = 29; i >= 0; i--) {
        const d = new Date(today)
        d.setDate(d.getDate() - i)
        data.push({
          date: d.toLocaleDateString(),
          count: Math.floor(Math.random() * 8) // 0 to 7 tasks
        })
      }
      this.heatmapData = data
    },
    getHeatmapClass(count) {
      if (count === 0) return 'level-0'
      if (count <= 2) return 'level-1'
      if (count <= 4) return 'level-2'
      if (count <= 6) return 'level-3'
      return 'level-4'
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

.statistics-page {
  max-width: 1000px;
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

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
}

.overview-card {
  grid-column: span 2;
}

.card-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #2a1a5e;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0ebff;
}

.overview-stats {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.o-icon {
  font-size: 36px;
  background: #faf8ff;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  border: 1px solid #f0ebff;
}

.o-info {
  display: flex;
  flex-direction: column;
}

.o-value {
  font-family: 'Varela Round', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #2a1a5e;
}

.o-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #7c5cbf;
}

.heatmap-card {
  grid-column: span 2;
}

.heatmap-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.heatmap-grid {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 800px;
}

.heatmap-cell {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.heatmap-cell:hover {
  transform: scale(1.2);
}

.level-0 { background: #f0ebff; }
.level-1 { background: #d5c8ff; }
.level-2 { background: #bda8ff; }
.level-3 { background: #9a62ff; }
.level-4 { background: #553496; }

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #7c5cbf;
  font-family: 'Varela Round', sans-serif;
  margin-top: 8px;
}

.legend-scale {
  display: flex;
  gap: 4px;
}

.chart-card {
  grid-column: span 2;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 200px;
  padding-top: 20px;
}

.bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  height: 100%;
  justify-content: flex-end;
  width: 40px;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #9a62ff 0%, #c4aeff 100%);
  border-radius: 8px 8px 0 0;
  position: relative;
  transition: height 0.5s ease;
}

.bar-fill:hover {
  filter: brightness(1.1);
}

.bar-tooltip {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #2a1a5e;
  color: #fff;
  font-family: 'Varela Round', sans-serif;
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 6px;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
  white-space: nowrap;
}

.bar-fill:hover .bar-tooltip {
  opacity: 1;
}

.bar-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #5a4a7a;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .overview-card, .heatmap-card, .chart-card {
    grid-column: span 1;
  }
}
</style>