<template>
  <div class="onboarding-wrapper">
    <div class="stars"></div>

    <!-- Screen 1: Create Character -->
    <Transition name="slide" mode="out-in">
      <div v-if="step === 1" key="step1" class="ob-screen">
        <div class="ob-card">
          <div class="farryx-bubble">
            <span class="farryx-avatar">🧙</span>
            <div class="farryx-text">Приветствую, путник! Я Фаррикс — твой наставник. Давай создадим твоего героя!</div>
          </div>
          <h1 class="ob-title">Твоя легенда начинается здесь</h1>
          <p class="ob-subtitle">Придумай имя и выбери внешность персонажа</p>

          <div class="form-group">
            <label>Имя персонажа</label>
            <input
              v-model="displayName"
              class="ob-input"
              type="text"
              placeholder="Введи имя героя..."
              maxlength="30"
              @keyup.enter="step1Next"
            />
          </div>

          <!-- Quick body picker -->
          <div class="appearance-row">
            <div
              v-for="body in quickBodies"
              :key="body.id"
              class="body-chip"
              :class="{ active: selectedBody === body.id }"
              @click="selectedBody = body.id"
            >
              <div class="body-swatch" :style="{ background: body.color }"></div>
              <span>{{ body.label }}</span>
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
    </Transition>

    <!-- Screen 2: First Task -->
    <Transition name="slide" mode="out-in">
      <div v-if="step === 2" key="step2" class="ob-screen">
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
              <div class="task-preview-meta">Оценка сложности: <span class="es-badge">Подождите...</span></div>
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
    </Transition>

    <!-- Screen 3: First Reward -->
    <Transition name="slide" mode="out-in">
      <div v-if="step === 3" key="step3" class="ob-screen">
        <div class="ob-card">
          <div class="farryx-bubble">
            <span class="farryx-avatar">🧙</span>
            <div class="farryx-text">Нажми на галочку — выполни квест прямо сейчас для обучения!</div>
          </div>
          <h1 class="ob-title">Первая награда!</h1>

          <!-- Task card to complete -->
          <div class="task-card-demo" :class="{ completed: taskCompleted }">
            <button class="checkbox" :class="{ checked: taskCompleted }" @click="completeTask">
              <span v-if="taskCompleted">✔</span>
            </button>
            <div class="task-text">{{ firstTask || 'Ознакомительный квест' }}</div>
          </div>

          <!-- Reward animation -->
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
    </Transition>

    <!-- Screen 4: App Tour -->
    <Transition name="slide" mode="out-in">
      <div v-if="step === 4" key="step4" class="ob-screen">
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
      quickBodies: [
        { id: 'body_pale',      label: 'Светлая', color: '#ffe0c8' },
        { id: 'body_standard',  label: 'Обычная', color: '#d4a57b' },
        { id: 'body_light_tan', label: 'Загар',   color: '#b87d5e' },
        { id: 'body_brown',     label: 'Тёмная',  color: '#7a5232' },
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
  methods: {
    async step1Next() {
      if (!this.displayName.trim()) return
      // Update display name if changed
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
        // Create the first task on backend
        if (this.firstTask.trim()) {
          await axios.post('/api/v1/tasks/', {
            title: this.firstTask,
            task_type: 'daily',
            difficulty: 'easy',
            category: 'other'
          }).catch(() => {}) // Non-blocking
        }
        // Mark onboarding complete in localStorage
        localStorage.setItem('lq_onboarding_done', '1')
        await this.authStore.fetchProfile()
        this.$router.push({ name: 'Main' })
      } catch (e) {
        localStorage.setItem('lq_onboarding_done', '1')
        this.$router.push({ name: 'Main' })
      } finally {
        this.loading = false
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

.appearance-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.body-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.06);
  border: 1.5px solid rgba(189,168,255,0.2);
  border-radius: 30px;
  padding: 8px 14px;
  cursor: pointer;
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #bda8ff;
  transition: all 0.2s;
}

.body-chip:hover { border-color: #9a62ff; }
.body-chip.active { border-color: #9a62ff; background: rgba(154,98,255,0.2); color: #fff; }

.body-swatch {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.3);
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
  transition: all 0.2s;
}

.ob-btn.primary {
  background: #9a62ff;
  color: #fff;
  box-shadow: 0 4px 16px rgba(154,98,255,0.4);
}
.ob-btn.primary:hover:not(:disabled) { background: #8a50ef; transform: translateY(-1px); }
.ob-btn.primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.ob-btn.ghost {
  background: rgba(255,255,255,0.06);
  color: #bda8ff;
  border: 1px solid rgba(189,168,255,0.2);
}
.ob-btn.ghost:hover { background: rgba(255,255,255,0.1); }

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
  transition: all 0.3s;
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
  transition: all 0.2s;
  flex-shrink: 0;
}
.checkbox:hover { border-color: #9a62ff; background: rgba(154,98,255,0.1); }
.checkbox.checked { background: #48bb78; border-color: #48bb78; color: #fff; }

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
.es-badge { background: rgba(154,98,255,0.2); border-radius: 8px; padding: 1px 6px; }

/* Slide transition */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
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
</style>