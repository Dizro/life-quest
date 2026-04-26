<template>
  <div class="page-container">
    <div class="blocks">
    <div class="profile-block">
      <div class="profile-left">
        <div class="profile-image-container">
          <img 
            :src="profileImage" 
            :alt="profileName"
            class="profile-image"
            @error="handleImageError"
          >
        </div>
        <h2 class="profile-name">{{ profileName }}</h2>
      </div>

      <div class="profile-right">
        <div class="xp-counter">
            <div class="xp-header">
            <span class="xp-level">Level {{ userLevel }}</span>
          </div>
            <div class="xp-bar-container">
              <div 
                class="xp-bar" 
                :style="{ width: `${xpPercentage}%` }"
              ></div>
            </div>
            <div class="xp-text">
              <span class="xp-current">{{currentXP}} </span>
              <span class="xp-separator">/</span>
              <span class="xp-next">{{nextLevelXP}}</span>
              <span class="xp-label"> XP</span>
            </div>
          </div>
      </div>
    </div>


    <div class="statistics-block">
      
      <div class="stats-row">

        <div class="point-graph-container">
          <div class="chart-header">
            <h3>Multi-Series Experience Trend</h3>
            <div class="legend">
              <span v-for="series in multiSeriesData" :key="series.name" class="legend-item">
                <span class="legend-dot" :style="{ backgroundColor: series.color }"></span>
                {{ series.name }}
              </span>
            </div>
          </div>
          <div class="point-graph">
            <svg viewBox="0 0 650 350" class="multi-line-chart">
              <line v-for="i in 6" :key="`grid-${i}`" 
                x1="50" :y1="40 + i * 45" x2="620" :y2="40 + i * 45" 
                stroke="#e0e0e0" stroke-width="1" stroke-dasharray="4"/>
              
              <g v-for="(series, seriesIdx) in multiSeriesData" :key="seriesIdx">
                <polyline
                  :points="getSeriesPoints(series)"
                  fill="none"
                  :stroke="series.color"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  :stroke-dasharray="series.dash ? '6,4' : 'none'"
                />
                <circle 
                  v-for="(point, idx) in series.data"
                  :key="`${seriesIdx}-${idx}`"
                  :cx="50 + (idx * (570 / (series.data.length - 1)))"
                  :cy="310 - (point.value * 270 / maxMultiValue)"
                  r="4"
                  :fill="series.color"
                  stroke="white"
                  stroke-width="2"
                  @mouseenter="showMultiTooltip(series, point, idx, $event)"
                  @mouseleave="hideMultiTooltip"
                />
              </g>
              
              <text v-for="(point, idx) in multiSeriesData[0].data" 
                :key="`label-${idx}`"
                :x="50 + (idx * (570 / (multiSeriesData[0].data.length - 1))) - 15"
                y="330"
                font-size="10"
                fill="#666"
              >{{ point.label }}</text>
              
              <text v-for="i in 6" :key="`y-${i}`"
                x="45"
                :y="45 + i * 45"
                text-anchor="end"
                font-size="10"
                fill="#666"
              >{{ Math.round(maxMultiValue * (6 - i) / 6) }}</text>
            </svg>
          </div>
          <div v-if="multiTooltipVisible" class="chart-tooltip" :style="{ left: multiTooltipX + 'px', top: multiTooltipY + 'px' }">
            <strong>{{ multiTooltipSeries }}</strong><br>
            {{ multiTooltipLabel }}: {{ multiTooltipValue }} XP
          </div>
        </div>

        <div class="right-stats">
          <div class="streak-calendar">
            <div class="streak-header">
              <h3>Current Streak</h3>
              <div class="streak-badge">{{ currentStreak }} days</div>
            </div>
            <div class="calendar-grid">
              <div class="weekdays">
                <span v-for="day in weekdays" :key="day">{{ day }}</span>
              </div>
              <div class="calendar-days">
                <div 
                  v-for="(day, index) in calendarDays" 
                  :key="index"
                  class="calendar-day"
                  :class="{
                    active: day.active,
                    current: day.isCurrent,
                    streak: day.inStreak
                  }"
                >
                  {{ day.date }}
                </div>
              </div>
            </div>
            <div class="streak-stats">
              <div class="streak-stat">
                <span class="stat-label">Best Streak</span>
                <span class="stat-value">{{ bestStreak }}</span>
              </div>
              <div class="streak-stat">
                <span class="stat-label">Total Active</span>
                <span class="stat-value">{{ totalActiveDays }}</span>
              </div>
            </div>
          </div>

          <div class="upright-column-chart">
            <div class="chart-header">
              <h3>Daily XP</h3>
            </div>
            <div class="upright-columns">
              <div v-for="(item, idx) in dailyXPData" :key="idx" class="upright-column-item">
                <div class="upright-column-bar" :style="{ height: (item.value / maxDailyValue * 120) + 'px', backgroundColor: item.color }">
                  <span class="upright-value">{{ item.value }}</span>
                </div>
                <div class="upright-label">{{ item.day }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-column-chart">
        <div class="chart-label-before">
          <div class="label-content">
            <h3>Weekly Performance</h3>
            <p>Comparison of key metrics by day</p>
          </div>
        </div>
        <div class="bottom-chart-container">
          <div class="bottom-columns">
            <div v-for="(item, idx) in weeklyData" :key="idx" class="bottom-column-wrapper">
              <div class="bottom-column-bar" :style="{ height: (item.value / maxWeeklyValue * 140) + 'px', backgroundColor: item.color }">
                <span class="bottom-value">{{ item.value }}</span>
              </div>
              <div class="bottom-day">{{ item.day }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
   </div>
  </div>
</template>

<script>
export default {
  name: 'ExperienceDashboard',
  
  data() {
    return {
      profileImage: '\LifeQuest\src\components\tasks.png',
      profileName: 'Lorem Ipsum',
      userLevel: 5,
      currentXP: 3450,
      nextLevelXP: 5000,
      
      multiSeriesData: [
        {
          name: 'Quests',
          color: '#9864FF',
          data: [
            { label: 'Mon', value: 120 },
            { label: 'Tue', value: 180 },
            { label: 'Wed', value: 220 },
            { label: 'Thu', value: 195 },
            { label: 'Fri', value: 260 },
            { label: 'Sat', value: 145 },
            { label: 'Sun', value: 110 }
          ]
        },
        {
          name: 'Challenges',
          color: '#48bb78',
          data: [
            { label: 'Mon', value: 90 },
            { label: 'Tue', value: 110 },
            { label: 'Wed', value: 145 },
            { label: 'Thu', value: 130 },
            { label: 'Fri', value: 175 },
            { label: 'Sat', value: 95 },
            { label: 'Sun', value: 80 }
          ]
        },
        {
          name: 'Achievements',
          color: '#ed8936',
          dash: true,
          data: [
            { label: 'Mon', value: 50 },
            { label: 'Tue', value: 65 },
            { label: 'Wed', value: 80 },
            { label: 'Thu', value: 75 },
            { label: 'Fri', value: 95 },
            { label: 'Sat', value: 45 },
            { label: 'Sun', value: 40 }
          ]
        }
      ],
      
      dailyXPData: [
        { day: 'Mon', value: 260, color: '#667eea' },
        { day: 'Tue', value: 355, color: '#667eea' },
        { day: 'Wed', value: 445, color: '#667eea' },
        { day: 'Thu', value: 400, color: '#667eea' },
        { day: 'Fri', value: 530, color: '#667eea' },
        { day: 'Sat', value: 285, color: '#667eea' },
        { day: 'Sun', value: 230, color: '#667eea' }
      ],
      
      weeklyData: [
        { day: 'Mon', value: 1250, color: '#667eea' },
        { day: 'Tue', value: 1480, color: '#667eea' },
        { day: 'Wed', value: 1620, color: '#667eea' },
        { day: 'Thu', value: 1580, color: '#667eea' },
        { day: 'Fri', value: 1850, color: '#667eea' },
        { day: 'Sat', value: 980, color: '#667eea' },
        { day: 'Sun', value: 850, color: '#667eea' }
      ],
      
      weekdays: ['S', 'M', 'T', 'W', 'T', 'F', 'S'],
      calendarDays: [],
      
      currentStreak: 12,
      bestStreak: 28,
      totalActiveDays: 187,
      
      animatedExp: 0,
      
      multiTooltipVisible: false,
      multiTooltipX: 0,
      multiTooltipY: 0,
      multiTooltipValue: '',
      multiTooltipLabel: '',
      multiTooltipSeries: ''
    }
  },
  
  computed: {
    xpPercentage() {
      return Math.min(100, (this.currentXP / this.nextLevelXP) * 100)
    },
    
    maxMultiValue() {
      let maxVal = 0
      this.multiSeriesData.forEach(series => {
        series.data.forEach(point => {
          if (point.value > maxVal) maxVal = point.value
        })
      })
      return Math.max(maxVal, 300)
    },
    
    maxDailyValue() {
      return Math.max(...this.dailyXPData.map(d => d.value), 600)
    },
    
    maxWeeklyValue() {
      return Math.max(...this.weeklyData.map(d => d.value), 2000)
    }
  },
  
  mounted() {
    this.generateCalendarDays()
    this.animateCounter()
  },
  
  methods: {
    handleImageError(e) {
      e.target.src = 'https://via.placeholder.com/100x100?text=Profile'
    },
    
    animateCounter() {
      let start = 0
      const end = this.currentExp
      const duration = 2000
      const increment = end / (duration / 16)
      
      const timer = setInterval(() => {
        start += increment
        if (start >= end) {
          this.animatedExp = end
          clearInterval(timer)
        } else {
          this.animatedExp = Math.floor(start)
        }
      }, 16)
    },
    
    getSeriesPoints(series) {
      const data = series.data
      if (data.length === 0) return ''
      return data.map((point, idx) => {
        const x = 50 + (idx * (570 / (data.length - 1)))
        const y = 310 - (point.value * 270 / this.maxMultiValue)
        return `${x},${y}`
      }).join(' ')
    },
    
    generateCalendarDays() {
      const days = []
      const today = new Date()
      
      for (let i = 27; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        
        const dayOfMonth = date.getDate()
        const isActive = Math.random() > 0.3 || i === 0
        const isCurrent = date.getDate() === today.getDate()
        const inStreak = i <= this.currentStreak && isActive

        days.push({
          date: dayOfMonth,
          active: isActive,
          isCurrent: isCurrent,
          inStreak: inStreak && isActive
        })
      }
      
      this.calendarDays = days
    },
    
    showMultiTooltip(series, point, idx, event) {
      this.multiTooltipValue = point.value
      this.multiTooltipLabel = point.label
      this.multiTooltipSeries = series.name
      this.multiTooltipVisible = true
      this.multiTooltipX = event.clientX - 80
      this.multiTooltipY = event.clientY - 50
    },
    
    hideMultiTooltip() {
      this.multiTooltipVisible = false
    }
  }
}
</script>

<style scoped>
.page-container {
  margin: 0 auto;
  min-height: 100vh;
}



@media (prefers-color-scheme: light){
.page-container {
  background: linear-gradient( #F9F9FA, #422974);
}

.profile-block {
  background: #F9F9FA;
}

.profile-name {
  color: #000000;
}

.profile-title {
  color: #000000;
}

.profile-right {
  background: #D9D9D9;
}

.xp-bar {
  background: #422974;
}

.xp-bar-container {
  background: #F9F9FA;
}

.xp-header {
  color: #000000;
}

.xp-text {
  color: #000000;
}

.xp-label {
  color: #000000;
}

.xp-details {
  color: #131313;
}

.statistics-block {
  background: #F9F9FA;
}

.block-title {
  color: #131313;
}

.point-graph-container {
  background: #F9F9FA;
}

.chart-header h3 {
  color: #131313;
}

.legend-item {
  color: #131313;
}

.point-graph svg {
  background: #F9F9FA;
}

.streak-calendar {
  background: #F9F9FA;
}

.streak-header h3 {
  color: #131313;
}

.weekdays span {
  color: #131313;
}

.calendar-day {
  background: #F9F9FA;
}

.streak-stats {
  border-top: 1px solid #422974;
}

.streak-stat .stat-label {
  color: #131313;
}

.streak-stat .stat-value {
  color: #422974;
}

.upright-column-chart {
  background: #F9F9FA;
}

.upright-label {
  color: #131313;
}

.upright-value {
  color: #131313;
}

.bottom-column-chart {
  background: #F9F9FA;
}

.label-content h3 {
  color: #131313;
}

.label-content p {
  color: #131313;
}

.bottom-value {
  color: #131313;
}

.bottom-day {
 color: #131313;
}

.chart-tooltip {
 color: #F9F9FA;
}

.calendar-day {
  color: #131313;
}

}

@media (prefers-color-scheme: dark){
.page-container {
  background: linear-gradient( #131313, #4C3087);
}

.profile-block {
  background: #131313;
}

.profile-name {
  color: #F9F9FA;
}

.profile-title {
  color: #F9F9FA;
}

.profile-right {
  background: #333333;
}

.xp-header {
  color: #F9F9FA;
}

.xp-text {
  color: #F9F9FA;
}

.xp-bar-container {
  background: #131313;
}

.xp-bar {
  background: #9864FF;
}

.xp-label {
  color: #F9F9FA;
}

.xp-details {
  color: #F9F9FA;
}

.statistics-block {
  background: #2C292D;
}

.block-title {
  color: #F9F9FA;
}

.point-graph-container {
  background: #1F1D20;
}

.chart-header h3 {
  color: #F9F9FA;

}

.legend-item {
  color: #F9F9FA;
}

.point-graph svg {
  background: #1F1D20;
}

.streak-calendar {
  background: #1F1D20;
}

.streak-header h3 {
  color: #F9F9FA;
}

.weekdays span {
  color: #F9F9FA;
}

.calendar-day {
  background: #1F1D20;
}

.streak-stats {
  border-top: 1px solid #9864FF;
}

.streak-stat .stat-label {
  color: #F9F9FA;
}

.streak-stat .stat-value {
  color: #9864FF;
}

.upright-column-chart {
  background: #1F1D20;
}

.upright-value {
  color: #F9F9FA;
}

.upright-label {
  color: #F9F9FA;
}

.bottom-column-chart {
  background: #1F1D20;
}

.label-content h3 {
  color: #F9F9FA;
}

.label-content p {
  color: #F9F9FA;
}

.bottom-value {
  color: #F9F9FA;
}

.bottom-day {
 color: #F9F9FA;
}

.chart-tooltip {
 color: #1F1D20;
}

.calendar-day {
  color: #F9F9FA;
}

}






.blocks {
display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  max-width: 500px;
  margin: 0 auto;
}

.profile-block {
  width: 300%;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 3rem;
  border-radius: 10px;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.profile-left {
  flex: 1;
  text-align: center;
}

.profile-image-container {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.profile-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border: 4px solid #553496;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.profile-name {
  font-size: 1.5rem;
  margin: 0.5rem 0 0.25rem;
}

.profile-title {
  font-size: 0.9rem;
  margin: 0;
}

.profile-right {
  flex: 1;
  border-radius: 25px;
  padding: 15px;
}

.xp-container {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 15px;
}

.xp-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 1.4rem;
}

.xp-label {
  font-weight: 500;
}

.xp-value {
  color: #422974;
  font-weight: bold;
}

.xp-bar-container {
  border-radius: 10px;
  height: 10px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.xp-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.xp-details {
  font-size: 0.8rem;
  text-align: right;
}

.statistics-block {
  border-radius: 24px;
  margin: 0 2rem 2rem;
  padding: 2rem;
  width: 310%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.block-title {
  font-size: 1.5rem;
  margin: 0 0 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #553496;
}

.stats-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  align-items: start;
}

.point-graph-container {
  border-radius: 16px;
  padding: 1rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.chart-header h3 {
  font-size: 1rem;
  margin: 0;
}

.legend {
  display: flex;
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.7rem;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.point-graph svg {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.right-stats {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

.streak-calendar {
  border-radius: 16px;
  padding: 1rem;
}

.streak-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.streak-header h3 {
  font-size: 1rem;
  margin: 0;
}

.streak-badge {
  background: #422974;
  color: #F9F9FA;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.calendar-grid {
  margin-bottom: 1rem;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 0.5rem;
}

.weekdays span {
  font-size: 0.65rem;
  font-weight: 500;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  border-radius: 8px;
}

.calendar-day.active {
  background: #48bb78;
  color: white;
}

.calendar-day.streak {
  background: #553496;
  color: white;
}

.calendar-day.current {
  border: 2px solid #9864FF;
  font-weight: bold;
}

.streak-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 0.5rem;
}

.streak-stat {
  text-align: center;
}

.streak-stat .stat-label {
  font-size: 0.65rem;
  display: block;
}

.streak-stat .stat-value {
  font-size: 1rem;
  display: block;
  font-weight: bold;
}

.upright-column-chart {
  border-radius: 16px;
  padding: 1rem;
}

.upright-columns {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 0.5rem;
  padding-top: 20px;
  align-items: flex-end;
}

.upright-column-item {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upright-column-bar {
  width: 100%;
  max-width: 45px;
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  transition: height 0.5s ease;
  position: relative;
  min-height: 30px;
}

.upright-value {
  font-size: 0.7rem;
  font-weight: 600;
  margin-top: -18px;
  position: absolute;
  top: -5px;
}

.upright-label {
  margin-top: 0.5rem;
  font-size: 0.7rem;
  font-weight: 500;
}

.bottom-column-chart {
  border-radius: 16px;
  padding: 1.5rem;
  margin-top: 0.5rem;
}

.chart-label-before {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #422974;
}

.label-content h3 {
  font-size: 1.1rem;
  margin: 0 0 0.25rem;
}

.label-content p {
  font-size: 0.8rem;
  margin: 0;
}

.bottom-chart-container {
  overflow-x: auto;
  padding: 30px;
}

.bottom-columns {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-end;
}

.bottom-column-wrapper {
  flex: 1;
  text-align: center;
  max-width: 100px;
}

.bottom-column-bar {
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  transition: height 0.5s ease;
  position: relative;
  min-height: 40px;
}

.bottom-value {
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: -20px;
  position: absolute;
  top: -5px;
}

.bottom-day {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
}

.chart-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.85);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.75rem;
  pointer-events: none;
  z-index: 100;
  white-space: nowrap;
  text-align: center;
  line-height: 1.4;
}

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .top-block {
    margin: 1rem;
    flex-direction: column;
    text-align: center;
  }
  
  .statistics-block {
    margin: 0 1rem 1rem;
  }
  
  .bottom-columns {
    justify-content: flex-start;
  }
  
  .bottom-column-wrapper {
    min-width: 70px;
  }
}

@media (max-width: 768px) {
  .counter-value .number {
    font-size: 1.8rem;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .legend {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .upright-column-bar {
    max-width: 30px;
  }
  
  .upright-value {
    font-size: 0.6rem;
  }
  
  .bottom-column-wrapper {
    min-width: 55px;
  }
  
  .bottom-value {
    font-size: 0.65rem;
  }
  
  .bottom-day {
    font-size: 0.7rem;
  }
}
</style>