<template>
  <div class="onboarding-wrapper">
    <div class="stars"></div>

    <Transition name="slide" mode="out-in">
      <!-- Screen 1: Create Character -->
      <div v-if="step === 1" key="step1" class="ob-screen">
        <div class="ob-card">
          <div class="farryx-bubble">
            <span class="farryx-avatar">🧙</span>
            <div class="farryx-text">Приветствую, путник! Я Фаррикс — твой наставник. Давай создадим твоего героя!</div>
          </div>
          <h1 class="ob-title">Создание персонажа</h1>
          <p class="ob-subtitle">Придумай имя и настрой внешность</p>

          <div class="form-group">
            <label>Имя героя</label>
            <input
              v-model="displayName"
              class="ob-input"
              type="text"
              placeholder="Введи имя героя..."
              maxlength="30"
              @keyup.enter="step1Next"
            />
          </div>

          <!-- RPG-style character preview -->
          <div class="char-creator">
            <div class="char-preview-area">
              <div class="char-image-wrapper">
                <img :src="getAsset('bodies', selectedBodyAsset)" :alt="displayName" class="char-preview-img" />
              </div>
              <div class="char-name-plate">{{ displayName || '???' }}</div>
            </div>

            <div class="char-options">
              <div class="option-section">
                <div class="option-label">Тон кожи</div>
                <div class="skin-palette">
                  <button
                    v-for="skin in skinTones"
                    :key="skin.id"
                    class="skin-circle"
                    :class="{ active: selectedBody === skin.id }"
                    :title="skin.label"
                    @click="selectedBody = skin.id"
                  >
                    <img :src="getAsset('bodies', skin.asset)" :alt="skin.label" class="skin-thumb" />
                  </button>
                </div>
              </div>
              <div class="selected-tone">{{ currentSkinLabel }}</div>
            </div>
          </div>

          <button class="ob-btn primary" :disabled="!displayName.trim()" @click="step1Next">
            Начать приключение →
          </button>
        </div>
        <div class="progress-dots">
          <span class="dot active"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>

      <!-- Screen 2: First Task -->
      <div v-else-if="step === 2" key="step2" class="ob-screen">
        <div class="ob-card">
          <div class="farryx-bubble">
            <span class="farryx-avatar">🧙</span>
            <div class="farryx-text">Отлично, {{ displayName }}! Теперь создай свой первый квест. Напиши что хочешь сделать сегодня.</div>
          </div>
          <h1 class="ob-title">Каждое великое дело начинается с одного шага</h1>

          <div class="form-group">
            <label>Твой первый квест</label>
            <input
              v-model="firstTask"
              class="ob-input"
              type="text"
              placeholder="Например: Прочитать 10 страниц книги"
              @keyup.enter="step2Next"
            />
            <div class="nlp-hint">💡 Пиши свободно — система всё поймёт</div>
          </div>

          <div v-if="firstTask.trim()" class="task-preview">
            <div class="task-preview-icon">⚔️</div>
            <div class="task-preview-info">
              <div class="task-preview-title">{{ firstTask }}</div>
              <div class="task-preview-meta">
                Оценка сложности: 
                <span v-if="effortScoring" class="es-badge scoring">
                  <span class="scoring-dots"></span> {{ effortText }}
                </span>
                <span v-else-if="effortResult" class="es-badge done">
                  {{ effortResult }}
                </span>
                <span v-else class="es-badge">Ожидание...</span>
              </div>
            </div>
          </div>

          <div class="step-btns">
            <button class="ob-btn ghost" @click="step--">← Назад</button>
            <button class="ob-btn primary" :disabled="!firstTask.trim()" @click="step2Next">
              Создать квест →
            </button>
          </div>
        </div>
        <div class="progress-dots">
          <span class="dot done"></span><span class="dot active"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>

      <!-- Screen 3: First Reward -->
      <div v-else-if="step === 3" key="step3" class="ob-screen">
        <div class="ob-card">
          <div class="farryx-bubble">
            <span class="farryx-avatar">🧙</span>
            <div class="farryx-text">Нажми на галочку — выполни квест прямо сейчас для обучения!</div>
          </div>
          <h1 class="ob-title">Первая награда!</h1>

          <div class="task-card-demo" :class="{ completed: taskCompleted }">
            <button class="checkbox" :class="{ checked: taskCompleted }" @click="completeTask">
              <span v-if="taskCompleted">✔</span>
            </button>
            <div class="task-text">{{ firstTask || 'Ознакомительный квест' }}</div>
          </div>

          <Transition name="reward-pop">
            <div v-if="taskCompleted" class="reward-display">
              <div class="reward-item xp">✨ +20 XP</div>
              <div class="reward-item gold">💰 +10 монет</div>
              <div class="reward-item">🔥 Первый квест выполнен!</div>
            </div>
          </Transition>

          <div class="step-btns">
            <button class="ob-btn ghost" @click="step--">← Назад</button>
            <button class="ob-btn primary" :disabled="!taskCompleted" @click="step++">
              Далее →
            </button>
          </div>
        </div>
        <div class="progress-dots">
          <span class="dot done"></span><span class="dot done"></span><span class="dot active"></span><span class="dot"></span>
        </div>
      </div>

      <!-- Screen 4: App Tour -->
      <div v-else-if="step === 4" key="step4" class="ob-screen">
        <div class="ob-card tour-card">
          <div class="farryx-bubble">
            <span class="farryx-avatar">🧙</span>
            <div class="farryx-text">Всё готово! В магазине тебя уже ждут первые предметы. Удачи, {{ displayName }}!</div>
          </div>
          <h1 class="ob-title">Добро пожаловать в LifeQuest!</h1>

          <div class="tour-grid">
            <div v-for="section in sections" :key="section.id" class="tour-item">
              <span class="tour-icon">{{ section.icon }}</span>
              <strong>{{ section.name }}</strong>
              <p>{{ section.desc }}</p>
            </div>
          </div>

          <div class="starter-pack">
            <div class="pack-title">🎁 Стартовый пакет</div>
            <div class="pack-items">
              <span>💰 50 монет</span>
              <span>🐛 Питомец Светлячок</span>
              <span>⚡ Бафф ×2 XP на 3 дня</span>
            </div>
          </div>

          <button class="ob-btn primary large" @click="finishOnboarding" :disabled="loading">
            {{ loading ? 'Начинаем...' : 'Начать игру! 🚀' }}
          </button>
        </div>
        <div class="progress-dots">
          <span class="dot done"></span><span class="dot done"></span><span class="dot done"></span><span class="dot active"></span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'
import { tasksApi } from '@/services/api'

export default {
  name: 'OnboardingPage',
  setup() {
    const authStore = useAuthStore()
    const characterStore = useCharacterStore()
    return { authStore, characterStore }
  },
  data() {
    return {
      step: 1,
      displayName: this.$route.query.name || '',
      firstTask: '',
      selectedBody: 'body_standard',
      taskCompleted: false,
      loading: false,
      effortScoring: false,
      effortResult: null,
      effortText: '',
      effortTimer: null,
      effortDebounce: null,
      skinTones: [
        { id: 'body_pale',       label: 'Фарфоровая',  asset: 'body_pale' },
        { id: 'body_light_tan',  label: 'Светлая',     asset: 'body_light_tan' },
        { id: 'body_standard',   label: 'Песочная',    asset: 'body_standard' },
        { id: 'body_brown',      label: 'Каштановая',  asset: 'body_brown' },
        { id: 'body_white',      label: 'Эльфийская',  asset: 'body_white' },
      ],
      sections: [
        { id: 'tasks',    icon: '⚔️', name: 'Квесты',    desc: 'Создавай задачи и получай XP за их выполнение' },
        { id: 'char',     icon: '🧙', name: 'Персонаж',  desc: 'Настраивай внешность героя и одевай его' },
        { id: 'shop',     icon: '🏪', name: 'Магазин',   desc: 'Трать монеты на одежду, питомцев и баффы' },
        { id: 'groups',   icon: '⚡', name: 'Группы',    desc: 'Объединяйся с друзьями для совместных целей' },
        { id: 'stats',    icon: '📊', name: 'Статистика', desc: 'Следи за прогрессом и стриком активности' },
        { id: 'farryx',   icon: '🧙', name: 'Фаррикс',  desc: 'Твой ИИ-наставник всегда готов помочь' },
      ],
    }
  },
  computed: {
    selectedBodyAsset() {
      const tone = this.skinTones.find(s => s.id === this.selectedBody)
      return tone ? tone.asset : 'body_standard'
    },
    currentSkinLabel() {
      const tone = this.skinTones.find(s => s.id === this.selectedBody)
      return tone ? tone.label : ''
    }
  },
  watch: {
    firstTask(val) {
      clearTimeout(this.effortDebounce)
      this.effortResult = null
      this.effortScoring = false
      if (val.trim().length >= 3) {
        this.effortDebounce = setTimeout(() => this.simulateEffortScore(), 600)
      }
    }
  },
  beforeUnmount() {
    clearTimeout(this.effortTimer)
    clearTimeout(this.effortDebounce)
  },
  methods: {
    simulateEffortScore() {
      this.effortScoring = true
      this.effortResult = null
      const phases = [
        'Анализ задачи...',
        'Оценка трудозатрат...',
        'Расчёт награды...',
      ]
      let i = 0
      this.effortText = phases[0]
      const next = () => {
        i++
        if (i < phases.length) {
          this.effortText = phases[i]
          this.effortTimer = setTimeout(next, 800)
        } else {
          this.effortScoring = false
          const scores = [
            { label: 'Лёгкий', color: '#48bb78', xp: 10 },
            { label: 'Средний', color: '#f6c90e', xp: 25 },
            { label: 'Сложный', color: '#ff6b6b', xp: 50 },
          ]
          const len = this.firstTask.trim().length
          const pick = len < 15 ? scores[0] : len < 30 ? scores[1] : scores[2]
          this.effortResult = `${pick.label} — +${pick.xp} XP`
        }
      }
      this.effortTimer = setTimeout(next, 800)
    },
    async step1Next() {
      if (!this.displayName.trim()) return
      this.characterStore.selectedBody = this.selectedBody
      this.step++
    },
    step2Next() {
      if (!this.firstTask.trim()) return
      this.step++
    },
    completeTask() {
      this.taskCompleted = true
    },
    async finishOnboarding() {
      this.loading = true
      try {
        if (this.firstTask.trim()) {
          await tasksApi.create({
            title: this.firstTask,
            task_type: 'daily',
            difficulty: 'easy',
            category: 'other'
          }).catch(() => {})
        }
        localStorage.setItem('lq_onboarding_done', '1')
        await this.authStore.fetchProfile()
        this.$router.push({ name: 'Main' })
      } catch (e) {
        localStorage.setItem('lq_onboarding_done', '1')
        this.$router.push({ name: 'Main' })
      } finally {
        this.loading = false
      }
    },
    getAsset(folder, name, ext = '.png') {
      if (!name || name === 'undefined') return ''
      try {
        return new URL(`../assets/${folder}/${name}${ext}`, import.meta.url).href
      } catch {
        return ''
      }
    }
  }
}
</script>

<style scoped>
.onboarding-wrapper {
  min-height: 100vh;
  background: #36205d;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.stars {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(1px 1px at 10% 20%, #fff 0%, transparent 100%),
    radial-gradient(1px 1px at 25% 60%, #fff 0%, transparent 100%),
    radial-gradient(1px 1px at 50% 10%, #fff 0%, transparent 100%),
    radial-gradient(1px 1px at 70% 40%, #fff 0%, transparent 100%),
    radial-gradient(1px 1px at 85% 75%, #fff 0%, transparent 100%),
    radial-gradient(1px 1px at 40% 85%, #fff 0%, transparent 100%),
    radial-gradient(2px 2px at 90% 15%, #d5c8ff 0%, transparent 100%),
    radial-gradient(2px 2px at 15% 90%, #d5c8ff 0%, transparent 100%);
  opacity: 0.6;
  pointer-events: none;
}

.ob-screen {
  width: 100%;
  max-width: 580px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.ob-card {
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 28px;
  padding: 36px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.farryx-bubble {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 14px 18px;
}

.farryx-avatar { font-size: 28px; flex-shrink: 0; }

.farryx-text {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #e0d5ff;
  line-height: 1.6;
}

.ob-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  line-height: 1.25;
}

.ob-subtitle {
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  color: #bda8ff;
  margin: -8px 0 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #bda8ff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ob-input {
  background: rgba(255,255,255,0.08);
  border: 1.5px solid rgba(189,168,255,0.3);
  border-radius: 12px;
  padding: 14px 16px;
  font-family: 'Varela Round', sans-serif;
  font-size: 16px;
  color: #fff;
  outline: none;
  transition: border-color 0.2s;
}
.ob-input::placeholder { color: rgba(255,255,255,0.3); }
.ob-input:focus { border-color: #9a62ff; }

.nlp-hint {
  font-size: 12px;
  color: rgba(189,168,255,0.7);
  font-family: 'Varela Round', sans-serif;
}

/* Character Creator */
.char-creator {
  display: flex;
  gap: 24px;
  align-items: center;
  background: rgba(0,0,0,0.15);
  border: 1px solid rgba(189,168,255,0.15);
  border-radius: 16px;
  padding: 20px;
}

.char-preview-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-width: 100px;
}

.char-image-wrapper {
  width: 100px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.2);
  border-radius: 12px;
  overflow: hidden;
}

.char-preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4));
  animation: charFloat 3s ease-in-out infinite;
}

@keyframes charFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.char-name-plate {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  background: rgba(154,98,255,0.25);
  padding: 3px 14px;
  border-radius: 12px;
  border: 1px solid rgba(154,98,255,0.4);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center;
}

.char-options {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #bda8ff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.skin-palette {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.skin-circle {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  border: 3px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
  position: relative;
  background: rgba(0,0,0,0.2);
  overflow: hidden;
  padding: 2px;
}
.skin-circle:hover {
  transform: scale(1.1);
  box-shadow: 0 0 12px rgba(255,255,255,0.2);
}
.skin-circle.active {
  border-color: #9a62ff;
  transform: scale(1.1);
  box-shadow: 0 0 16px rgba(154,98,255,0.5);
}
.skin-thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
}

.selected-tone {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #e0d5ff;
  padding-left: 2px;
}

/* Buttons */
.ob-btn {
  border: none;
  border-radius: 12px;
  padding: 14px 28px;
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.15s, box-shadow 0.2s;
}

.ob-btn.primary {
  background: #9a62ff;
  color: #fff;
  box-shadow: 0 4px 16px rgba(154,98,255,0.4);
}
.ob-btn.primary:hover:not(:disabled) { background: #8a50ef; transform: translateY(-1px); box-shadow: 0 6px 20px rgba(154,98,255,0.5); }
.ob-btn.primary:active:not(:disabled) { transform: translateY(0); box-shadow: 0 2px 8px rgba(154,98,255,0.3); }
.ob-btn.primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.ob-btn.ghost {
  background: rgba(255,255,255,0.06);
  color: #bda8ff;
  border: 1px solid rgba(189,168,255,0.2);
}
.ob-btn.ghost:hover { background: rgba(255,255,255,0.1); }
.ob-btn.ghost:active { background: rgba(255,255,255,0.14); }

.ob-btn.large { padding: 16px 40px; font-size: 17px; width: 100%; }

.step-btns {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Task card demo */
.task-card-demo {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 16px;
  border: 1.5px solid rgba(189,168,255,0.2);
  transition: border-color 0.3s, background-color 0.3s;
}

.task-card-demo.completed {
  border-color: #48bb78;
  background: rgba(72,187,120,0.1);
}

.checkbox {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  border: 2px solid rgba(189,168,255,0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #48bb78;
  transition: background-color 0.2s, border-color 0.2s, transform 0.15s;
  flex-shrink: 0;
}
.checkbox:hover { border-color: #9a62ff; background: rgba(154,98,255,0.1); transform: scale(1.05); }
.checkbox:active { transform: scale(0.95); }
.checkbox.checked { background: #48bb78; border-color: #48bb78; color: #fff; animation: checkPop 0.3s ease; }

@keyframes checkPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.task-text {
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  color: #e0d5ff;
}

/* Reward */
.reward-display {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.reward-item {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 8px 16px;
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #fff;
  font-weight: 700;
}
.reward-item.xp { border-color: #9864ff; color: #c4a7ff; }
.reward-item.gold { border-color: #f6c90e; color: #fde68a; }

/* Tour */
.tour-card { gap: 16px; }

.tour-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.tour-item {
  background: rgba(255,255,255,0.04);
  border-radius: 14px;
  padding: 14px;
  border: 1px solid rgba(255,255,255,0.08);
}

.tour-icon { font-size: 24px; display: block; margin-bottom: 6px; }
.tour-item strong {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #fff;
  display: block;
  margin-bottom: 4px;
}
.tour-item p {
  font-size: 11px;
  color: #bda8ff;
  margin: 0;
  font-family: 'Varela Round', sans-serif;
  line-height: 1.4;
}

.starter-pack {
  background: linear-gradient(135deg, rgba(154,98,255,0.2), rgba(66,41,116,0.3));
  border: 1px solid rgba(189,168,255,0.3);
  border-radius: 14px;
  padding: 16px;
}

.pack-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 10px;
}

.pack-items {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pack-items span {
  background: rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 5px 12px;
  font-size: 12px;
  color: #e0d5ff;
  font-family: 'Varela Round', sans-serif;
}

/* Progress dots */
.progress-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background: rgba(255,255,255,0.2);
  transition: all 0.3s;
}
.dot.active { background: #9a62ff; width: 24px; }
.dot.done { background: #48bb78; }

/* Task preview */
.task-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(154,98,255,0.1);
  border: 1px solid rgba(154,98,255,0.3);
  border-radius: 12px;
  padding: 12px;
}
.task-preview-icon { font-size: 20px; }
.task-preview-title { font-size: 14px; color: #e0d5ff; font-family: 'Varela Round', sans-serif; }
.task-preview-meta { font-size: 11px; color: #9864ff; font-family: 'Varela Round', sans-serif; }
.es-badge { background: rgba(154,98,255,0.2); border-radius: 8px; padding: 2px 8px; display: inline-flex; align-items: center; gap: 4px; }
.es-badge.scoring { color: #e0d5ff; }
.es-badge.done { background: rgba(72,187,120,0.2); color: #48bb78; font-weight: 700; }

.scoring-dots::after {
  content: '';
  animation: dots 1.2s steps(4) infinite;
}
@keyframes dots {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
}

/* Slide transition */
.slide-enter-active, .slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.slide-enter-from { opacity: 0; transform: translateX(30px); }
.slide-leave-to { opacity: 0; transform: translateX(-30px); }

/* Reward pop */
.reward-pop-enter-active {
  animation: rewardBounce 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes rewardBounce {
  from { opacity: 0; transform: scale(0.5) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* ─── Адаптив ─── */
@media (max-width: 600px) {
  .onboarding-wrapper { padding: 16px 12px; }
  .ob-screen { max-width: 100%; }
  .ob-card { padding: 20px 16px; border-radius: 20px; gap: 16px; }
  .ob-title { font-size: 20px; }
  .ob-subtitle { font-size: 13px; }
  .farryx-bubble { padding: 10px 12px; gap: 8px; }
  .farryx-avatar { font-size: 22px; }
  .farryx-text { font-size: 13px; }
  .ob-input { padding: 12px 14px; font-size: 14px; }
  .char-creator { flex-direction: column; padding: 16px; gap: 16px; }
  .char-preview-area { min-width: unset; }
  .skin-circle { width: 32px; height: 32px; }
  .ob-btn { padding: 12px 20px; font-size: 14px; }
  .ob-btn.large { padding: 14px 24px; font-size: 15px; }
  .step-btns { flex-direction: column-reverse; gap: 8px; }
  .step-btns .ob-btn { width: 100%; text-align: center; }
  .tour-grid { grid-template-columns: 1fr; gap: 8px; }
  .tour-item { padding: 10px; }
  .reward-display { flex-direction: column; gap: 6px; }
  .starter-pack { padding: 12px; }
  .pack-items { flex-direction: column; gap: 4px; }
}
</style>