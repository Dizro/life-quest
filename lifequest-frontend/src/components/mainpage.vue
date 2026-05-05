<template>
  <div class="page-wrapper">
    <div class="main-container">
      
      <section class="profile-card">
        <div class="avatar-scene">
          <img v-if="charStore.selectedBackground" :src="getAsset('backgrounds', charStore.selectedBackground)" class="layer layer-bg" alt="" />
          <img :src="getAsset('bodies', charStore.selectedBody)" class="layer layer-body" alt="" />
          <img v-if="charStore.selectedBottom" :src="getAsset('clothes/bottoms', charStore.selectedBottom)" class="layer layer-bottom" alt="" />
          <img v-if="charStore.selectedTop" :src="getAsset('clothes/tops', charStore.selectedTop)" class="layer layer-top" alt="" />
          <img :src="getAsset('hair', charStore.selectedHair)" class="layer layer-hair" alt="" />
          <img v-if="charStore.selectedAccessory" :src="getAsset('accessories', charStore.selectedAccessory)" class="layer layer-accessory" alt="" />
          <img v-if="charStore.selectedItem" :src="getAsset('items', charStore.selectedItem)" class="layer layer-item" alt="" />
          <img v-if="charStore.selectedPet" :src="getAsset('pet', charStore.selectedPet)" class="layer layer-pet" alt="" />
        </div>
        
        <div class="profile-info">
          <div class="profile-header">
            <div class="header-titles">
              <span class="label-text">Персонаж</span>
              <h1 class="hero-name">{{ authStore.displayName || authStore.user?.username || 'Герой' }}</h1>
            </div>
            <div class="header-badges">
              <span class="class-badge">{{ authStore.user?.character_class || 'Авантюрист' }}</span>
              <span class="rank-badge">{{ authStore.user?.rank_title || 'Новобранец' }}</span>
            </div>
          </div>
          
          <div class="stats-row">
            <div class="stat-pill level-pill">
              <span class="icon">⭐</span> Уровень {{ authStore.userLevel || 1 }}
            </div>
            <div class="stat-pill">
              <span class="icon">💰</span> {{ authStore.user?.gold || 0 }}
            </div>
            <div class="stat-pill crystal-pill">
              <span class="icon">💎</span> {{ authStore.user?.crystals || 0 }}
            </div>
            <div class="stat-pill fire-pill">
              <span class="icon">🔥</span> Стрик: {{ authStore.user?.streak_days || 0 }}
            </div>
          </div>
          
          <div class="xp-container">
            <div class="xp-header">
              <span>Прогресс (XP)</span>
              <span>{{ authStore.userXP || 0 }} / {{ authStore.xpToNext || 100 }}</span>
            </div>
            <div class="xp-track">
              <div class="xp-fill" :style="{ width: (authStore.xpPercentage || 0) + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="task-board">
        <div class="filters-bar">
          <button :class="['filter-btn', { active: activeFilter === 'active' }]" @click="activeFilter = 'active'">
            Активные квесты
          </button>
          <button :class="['filter-btn', { active: activeFilter === 'completed' }]" @click="activeFilter = 'completed'">
            Завершенные
          </button>
          <button :class="['filter-btn trial-btn', { active: activeFilter === 'trials' }]" @click="activeFilter = 'trials'">
            Испытания (Просрочено)
          </button>
        </div>

        <div class="columns-grid">
          
          <div class="board-column">
            <div class="column-header purple-header">
              <div class="col-title">
                <span class="col-icon">🔄</span>
                <h2>Рутина и Привычки</h2>
              </div>
              <button class="add-btn" @click="openModal('daily')">+</button>
            </div>
            
            <div class="task-list">
              <TransitionGroup name="list">
                <div v-for="task in filteredLeftTasks" :key="task.id" class="task-card" :class="{ 'completed': task.status === 'completed' }">
                  <div class="color-stripe" :class="getStripeColor(task.category)">
                    <div v-if="task.status === 'pending_es'" class="spinner"></div>
                    <div v-else class="custom-checkbox" :class="{ checked: task.status === 'completed' }" @click="completeTask(task)">
                      <span v-if="task.status === 'completed'" class="check-icon">✔</span>
                    </div>
                  </div>
                  <div class="task-content">
                    <h3 class="task-title" :class="{ 'strike': task.status === 'completed' }">
                      <span v-if="task.task_type === 'habit'" class="type-badge">Привычка</span>
                      {{ task.title }}
                    </h3>
                    <p v-if="task.description" class="task-desc">{{ task.description }}</p>
                  </div>
                  <div class="task-rewards">
                    <span v-if="task.status !== 'pending_es'" class="xp-reward">{{ task.xp_reward }} XP</span>
                    <span v-if="task.status !== 'pending_es'" class="gold-reward">{{ task.gold_reward }} 💰</span>
                  </div>
                </div>
              </TransitionGroup>
              <div v-if="!filteredLeftTasks.length" class="empty-state">
                Здесь пока пусто. Нажми «+», чтобы добавить ежедневные дела для поддержания стрика.
              </div>
            </div>
          </div>

          <div class="board-column">
            <div class="column-header blue-header">
              <div class="col-title">
                <span class="col-icon">⚔️</span>
                <h2>Разовые Квесты</h2>
              </div>
              <button class="add-btn" @click="openModal('regular')">+</button>
            </div>
            
            <div class="task-list">
              <TransitionGroup name="list">
                <div v-for="task in filteredRightTasks" :key="task.id" class="task-card" :class="{ 'completed': task.status === 'completed', 'trial': task.status === 'trial' }">
                  <div class="color-stripe" :class="getStripeColor(task.category)">
                    <div v-if="task.status === 'pending_es'" class="spinner"></div>
                    <div v-else class="custom-checkbox" :class="{ checked: task.status === 'completed' }" @click="completeTask(task)">
                      <span v-if="task.status === 'completed'" class="check-icon">✔</span>
                    </div>
                  </div>
                  <div class="task-content">
                    <h3 class="task-title" :class="{ 'strike': task.status === 'completed', 'trial-text': task.status === 'trial' }">
                      <span v-if="task.status === 'trial'" class="trial-badge">☠️ [Испытание]</span>
                      {{ task.title }}
                    </h3>
                    <div v-if="task.deadline && task.status !== 'completed'" class="task-deadline" :class="{ 'overdue': task.status === 'trial' }">
                      ⏱ {{ new Date(task.deadline).toLocaleString('ru-RU', {day: 'numeric', month: 'short', hour: '2-digit', minute:'2-digit'}) }}
                    </div>
                    <div v-if="task.status === 'pending_es'" class="ai-loading">✨ Оценка ИИ (Слой 1)...</div>
                  </div>
                  <div class="task-rewards" :class="{ 'trial-bg': task.status === 'trial' }">
                    <span v-if="task.status !== 'pending_es'" class="xp-reward" :class="{ 'strike trial-text': task.status === 'trial' }">{{ task.xp_reward }} XP</span>
                    <span v-if="task.status !== 'pending_es'" class="gold-reward">{{ task.gold_reward }} 💰</span>
                  </div>
                </div>
              </TransitionGroup>
              <div v-if="!filteredRightTasks.length" class="empty-state">
                Нет активных квестов. Добавь задачу с дедлайном, а ИИ оценит её сложность.
              </div>
            </div>
          </div>

        </div>
      </section>
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <button @click="closeModal" class="close-btn">✕</button>
            
            <div class="modal-header">
              <div class="modal-icon">{{ newTask.task_type === 'regular' ? '⚔️' : '🔄' }}</div>
              <h2 class="modal-title">
                {{ newTask.task_type === 'regular' ? 'Новый Квест' : 'Новая Рутина' }}
              </h2>
            </div>
            <p class="modal-subtitle">
              <template v-if="newTask.task_type === 'regular'">
                Разовое дело. Фаррикс объективно оценит сложность с помощью ИИ.
              </template>
              <template v-else>
                Регулярные действия. Не оцениваются ИИ, но берегут твой стрик.
              </template>
            </p>
            
            <div class="modal-body">
              <div v-if="modalError" class="modal-error">
                <span class="error-icon">⚠️</span> {{ modalError }}
              </div>

              <div v-if="newTask.task_type !== 'regular'" class="type-toggle">
                <label class="radio-label">
                  <input type="radio" v-model="newTask.task_type" value="daily"> 
                  <span>Ежедневная (Стрик)</span>
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="newTask.task_type" value="habit"> 
                  <span>Привычка (+/-)</span>
                </label>
              </div>

              <div class="form-group">
                <label>Что нужно сделать?</label>
                <textarea 
                  v-model="newTask.title" 
                  rows="3" 
                  class="custom-input" 
                  placeholder="Опиши свою задачу..." 
                  @keyup.enter.prevent="submitTask"
                ></textarea>
                <div class="hint-text">
                  <span class="hint-icon">✦</span> Слой 0: минимум 3 слова и 10 символов
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Категория</label>
                  <select v-model="newTask.category" class="custom-input select-input">
                    <option value="work">💼 Работа</option>
                    <option value="study">📚 Учёба</option>
                    <option value="health">❤️ Здоровье и Спорт</option>
                    <option value="creativity">🎨 Творчество</option>
                    <option value="family">👨‍👩‍👧 Семья</option>
                    <option value="personal">🏠 Личное / Другое</option>
                  </select>
                </div>
                
                <div class="form-group" v-if="newTask.task_type === 'regular'">
                  <label>Дедлайн</label>
                  <input 
                    v-model="newTask.deadline" 
                    type="datetime-local" 
                    class="custom-input" 
                  >
                </div>
              </div>

              <div class="modal-actions">
                <button @click="closeModal" class="btn-ghost">Отмена</button>
                <button @click="submitTask" class="btn-primary" :disabled="isSubmitting">
                  <div v-if="isSubmitting" class="btn-spinner"></div>
                  {{ isSubmitting ? 'Создаём...' : 'Отправить' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="reward-pop">
        <div v-if="rewardPopup" class="reward-overlay" @click.self="rewardPopup = null">
          <div class="reward-card">
            <div class="reward-trophy">🏆</div>
            <h2 class="reward-title">Квест Завершён!</h2>
            <div class="reward-phrase-box">
              <p class="reward-phrase">«{{ rewardPopup.farrix_phrase }}»</p>
            </div>
            <div class="reward-items">
              <div class="reward-item">
                <span class="reward-val xp">+{{ rewardPopup.xp_gained }}</span>
                <span class="reward-label">Опыта (XP)</span>
              </div>
              <div class="reward-item">
                <span class="reward-val gold">+{{ rewardPopup.gold_gained }}</span>
                <span class="reward-label">Монет</span>
              </div>
            </div>
            <div v-if="rewardPopup.leveled_up" class="level-up-banner">
              🌟 НОВЫЙ УРОВЕНЬ: {{ rewardPopup.new_level }}!
            </div>
            <div v-if="rewardPopup.achievement_unlocked" class="achievement-banner">
              🏅 Разблокировано: {{ rewardPopup.achievement_unlocked }}
            </div>
            <button @click="rewardPopup = null" class="btn-claim">Продолжить Путь</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { tasksApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'

export default {
  name: 'MainPage',
  setup() {
    const authStore = useAuthStore()
    const charStore = useCharacterStore()

    const tasks = ref([])
    const activeFilter = ref('active') // 'active' | 'completed' | 'trials'

    const isModalOpen = ref(false)
    const isSubmitting = ref(false)
    const modalError = ref(null)
    const newTask = ref({ title: '', task_type: 'regular', category: 'personal', deadline: '' })

    const rewardPopup = ref(null)
    let pollingInterval = null

    const getAsset = (folder, name, ext = '.png') => {
      try {
        return new URL(`../assets/${folder}/${name}${ext}`, import.meta.url).href
      } catch (e) {
        return ''
      }
    }

    const getStripeColor = (category) => {
      const colors = {
        work: 'stripe-cyan',
        study: 'stripe-orange',
        health: 'stripe-green',
        creativity: 'stripe-purple',
        family: 'stripe-pink',
        personal: 'stripe-yellow'
      }
      return colors[category] || 'stripe-yellow'
    }

    const filteredLeftTasks = computed(() => {
      let list = tasks.value.filter(t => t.task_type === 'daily' || t.task_type === 'habit')
      if (activeFilter.value === 'completed') return list.filter(t => t.status === 'completed')
      if (activeFilter.value === 'trials') return list.filter(t => t.status === 'trial')
      return list.filter(t => t.status === 'active' || t.status === 'pending_es')
    })

    const filteredRightTasks = computed(() => {
      let list = tasks.value.filter(t => t.task_type === 'regular')
      if (activeFilter.value === 'completed') return list.filter(t => t.status === 'completed')
      if (activeFilter.value === 'trials') return list.filter(t => t.status === 'trial')
      return list.filter(t => t.status === 'active' || t.status === 'pending_es')
    })

    const loadTasks = async () => {
      try {
        tasks.value = await tasksApi.getAll()
        checkPollingNeeded()
      } catch (err) {
        console.error('Ошибка загрузки задач:', err)
      }
    }

    const validateLayer0 = (text) => {
      if (!text || text.length < 10) return "Описание слишком короткое (минимум 10 символов)."
      const words = text.trim().split(/\s+/)
      if (words.length < 3) return "Пожалуйста, опиши задачу подробнее (минимум 3 слова)."
      if (/^\d+$/.test(text.replace(/\s/g, ''))) return "Задача не может состоять только из цифр."
      
      const isDuplicate = tasks.value.some(t => t.title.toLowerCase() === text.toLowerCase() && t.status !== 'completed')
      if (isDuplicate) return "У тебя уже есть активная задача с точно таким же описанием."
      return null
    }

    const openModal = (type) => {
      modalError.value = null
      // По умолчанию для левой колонки ставим 'daily'
      newTask.value = { title: '', task_type: type, category: 'personal', deadline: '' }
      isModalOpen.value = true
    }

    const closeModal = () => {
      isModalOpen.value = false
    }

    const submitTask = async () => {
      modalError.value = null
      const err = validateLayer0(newTask.value.title)
      if (err) {
        modalError.value = err
        return
      }

      isSubmitting.value = true
      try {
        const payload = { ...newTask.value }
        // Если это не регулярная задача, принудительно стираем дедлайн
        if (payload.task_type !== 'regular' || !payload.deadline) {
          delete payload.deadline
        }
        
        const created = await tasksApi.create(payload)
        tasks.value.unshift(created)
        closeModal()
        checkPollingNeeded()
      } catch (err) {
        modalError.value = err?.response?.data?.detail || "Ошибка связи с сервером"
      } finally {
        isSubmitting.value = false
      }
    }

    const completeTask = async (task) => {
      if (task.status === 'pending_es') {
        alert("Подождите, Фаррикс еще оценивает сложность задачи (Слой 1)!")
        return
      }
      if (task.status === 'completed') return

      const originalStatus = task.status
      task.status = 'completed'

      try {
        const response = await tasksApi.complete(task.id)
        await authStore.fetchProfile() 
        
        if (response.xp_gained > 0 || response.gold_gained > 0 || response.farrix_phrase) {
          rewardPopup.value = response
        } else {
          alert("Дневной лимит наград достигнут. Задача засчитана в стрик, но XP и Золото = 0.")
        }
        await loadTasks()
      } catch (err) {
        console.error('Ошибка выполнения:', err)
        task.status = originalStatus
        alert(err?.response?.data?.detail || "Ошибка завершения задачи")
      }
    }

    const checkPollingNeeded = () => {
      const needsPolling = tasks.value.some(t => t.status === 'pending_es')
      if (needsPolling && !pollingInterval) {
        pollingInterval = setInterval(async () => {
          try {
            const freshTasks = await tasksApi.getAll()
            let stillPending = false
            
            freshTasks.forEach(ft => {
              const local = tasks.value.find(lt => lt.id === ft.id)
              if (local && local.status !== ft.status) {
                Object.assign(local, ft)
              }
              if (ft.status === 'pending_es') stillPending = true
            })
            
            if (!stillPending) {
              clearInterval(pollingInterval)
              pollingInterval = null
            }
          } catch (e) {
            // Игнорируем сетевые ошибки поллинга
          }
        }, 3000)
      }
    }

    onMounted(async () => {
      await authStore.fetchProfile()
      await loadTasks()
    })

    onUnmounted(() => {
      if (pollingInterval) clearInterval(pollingInterval)
    })

    return {
      authStore,
      charStore,
      activeFilter,
      filteredLeftTasks,
      filteredRightTasks,
      isModalOpen,
      isSubmitting,
      modalError,
      newTask,
      rewardPopup,
      openModal,
      closeModal,
      submitTask,
      completeTask,
      getAsset,
      getStripeColor
    }
  }
}
</script>

<style scoped>
/* ─── Базовые стили ─── */
.page-wrapper {
  min-height: calc(100vh - 67px);
  background: linear-gradient(160deg, #f4f0ff 0%, #e8d5ff 40%, #c9a6ff 100%);
  padding: 32px 24px;
  display: flex;
  justify-content: center;
  font-family: 'Varela Round', sans-serif;
}

.main-container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* ─── Секция профиля ─── */
.profile-card {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  display: flex;
  gap: 40px;
  align-items: center;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
}

.avatar-scene {
  position: relative;
  width: 220px;
  height: 220px;
  border-radius: 20px;
  overflow: hidden;
  background: #2e1f5a;
  flex-shrink: 0;
  border: 4px solid #d5c8ff;
}

.layer {
  position: absolute;
  object-fit: contain;
  image-rendering: pixelated;
}

.layer-bg { inset: 0; width: 100%; height: 100%; z-index: 1; object-fit: cover; }
.layer-body { inset: 0; width: 100%; height: 100%; z-index: 2; }
.layer-bottom { z-index: 3; width: 46%; height: auto; top: 52%; left: 50%; transform: translateX(-50%); }
.layer-top { z-index: 4; width: 48%; height: auto; top: 32%; left: 50%; transform: translateX(-50%); }
.layer-hair { z-index: 5; width: 55%; height: auto; top: 1%; left: 54%; transform: translateX(-50%); }
.layer-accessory { z-index: 6; width: 45%; height: auto; top: -10%; left: 52%; transform: translateX(-50%); }
.layer-item { z-index: 7; width: 30%; height: auto; top: 45%; left: 10%; }
.layer-pet { z-index: 8; width: 35%; height: auto; bottom: 4%; right: 4%; }

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.label-text {
  font-size: 13px;
  color: #8b8b8b;
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 1px;
}

.hero-name {
  font-family: 'Intro Black', sans-serif;
  font-size: 36px;
  font-weight: 900;
  color: #432874;
  margin: 4px 0 0 0;
}

.header-badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  background: #f4f0ff;
  padding: 8px 16px;
  border-radius: 12px;
}

.class-badge {
  font-size: 16px;
  font-weight: bold;
  color: #422974;
}

.rank-badge {
  font-size: 12px;
  color: #6133b4;
  font-weight: bold;
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.stat-pill {
  background: #fff;
  border: 1px solid #f0ebff;
  color: #422974;
  padding: 8px 16px;
  border-radius: 16px;
  font-weight: bold;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.level-pill { background: #6133b4; color: white; border-color: #6133b4; }
.crystal-pill { color: #3182ce; }
.fire-pill { background: #fff5f0; border-color: #ffe6d5; color: #d69e2e; }
.icon { font-size: 18px; }

.xp-container {
  background: #faf8ff;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #f0ebff;
}

.xp-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  font-weight: bold;
  color: #432874;
  margin-bottom: 8px;
}

.xp-track {
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.xp-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff944c, #fdd243);
  transition: width 0.5s ease-out;
}

/* ─── Доска задач ─── */
.task-board {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
}

.filters-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  border-bottom: 2px solid #f0ebff;
  padding-bottom: 8px;
}

.filter-btn {
  background: none;
  border: none;
  font-family: 'Varela Round', sans-serif;
  font-size: 16px;
  color: #8b8b8b;
  font-weight: bold;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s;
}

.filter-btn:hover { background: #f4f0ff; color: #432874; }
.filter-btn.active { background: #432874; color: #fff; }
.filter-btn.trial-btn.active { background: #b85450; }

.columns-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.board-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-radius: 16px;
  color: white;
}

.purple-header { background: #6133b4; }
.blue-header { background: #3B72A9; }

.col-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.col-title h2 {
  font-size: 20px;
  font-weight: 900;
  margin: 0;
}
.col-icon { font-size: 24px; }

.add-btn {
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.add-btn:hover { background: white; color: #333; }

/* ─── Карточки задач ─── */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  min-height: 200px;
}

.task-card {
  display: flex;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #f0ebff;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: all 0.3s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

.task-card.completed { opacity: 0.6; filter: grayscale(100%); }
.task-card.trial { border-color: #fc8181; background: #fff5f5; }

.color-stripe {
  width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stripe-cyan { background: #3bcad7; }
.stripe-green { background: #24cc8f; }
.stripe-yellow { background: #fdd243; }
.stripe-orange { background: #ff944c; }
.stripe-purple { background: #9a62ff; }
.stripe-pink { background: #ed64a6; }

.custom-checkbox {
  width: 32px;
  height: 32px;
  background: rgba(255,255,255,0.9);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.custom-checkbox:hover { transform: scale(1.1); }
.custom-checkbox.checked { background: transparent; }
.check-icon { font-size: 18px; color: #fff; font-weight: bold; }

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.task-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.task-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.type-badge {
  font-size: 11px;
  background: #f0ebff;
  color: #6133b4;
  padding: 2px 8px;
  border-radius: 8px;
  text-transform: uppercase;
}

.strike { text-decoration: line-through; color: #a0aec0; }
.trial-text { color: #c53030; }
.trial-badge { font-weight: bold; margin-right: 4px; }

.task-desc {
  font-size: 13px;
  color: #718096;
  margin: 4px 0 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-deadline {
  font-size: 12px;
  font-weight: bold;
  color: #a0aec0;
  margin-top: 6px;
}
.task-deadline.overdue { color: #e53e3e; }

.ai-loading {
  font-size: 12px;
  font-weight: bold;
  color: #ed8936;
  margin-top: 6px;
  animation: pulse 1.5s infinite;
}

.task-rewards {
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  background: #faf8ff;
  min-width: 80px;
}

.trial-bg { background: #fed7d7; }

.xp-reward { font-size: 18px; font-weight: 900; color: #6133b4; }
.gold-reward { font-size: 13px; font-weight: bold; color: #d69e2e; margin-top: 4px; }

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #a0aec0;
  font-weight: bold;
  padding: 40px 20px;
  background: #faf8ff;
  border-radius: 16px;
  border: 1px dashed #e2e8f0;
}

/* ─── Анимации ─── */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 50% { opacity: 0.5; } }

.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from { opacity: 0; transform: translateY(20px); }
.list-leave-to { opacity: 0; transform: translateY(-20px); }
.list-leave-active { position: absolute; width: 100%; }

/* ─── Модальное окно ─── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 32px;
  width: 100%;
  max-width: 500px;
  padding: 32px;
  position: relative;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.close-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  background: #f4f0ff;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: #5a4a7a;
  cursor: pointer;
  transition: background 0.2s;
}
.close-btn:hover { background: #e8d5ff; }

.modal-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.modal-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #9a62ff, #6133b4);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.modal-title {
  font-family: 'Intro Black', sans-serif;
  font-size: 28px;
  color: #432874;
  margin: 0;
}

.modal-subtitle {
  color: #718096;
  font-size: 14px;
  margin-bottom: 24px;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-error {
  background: #fff5f5;
  color: #c53030;
  padding: 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: bold;
  border: 1px solid #fed7d7;
}

.type-toggle {
  display: flex;
  gap: 16px;
  background: #f4f0ff;
  padding: 12px;
  border-radius: 16px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: bold;
  color: #432874;
  cursor: pointer;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 12px;
  font-weight: bold;
  color: #432874;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.custom-input {
  background: #f9f9fa;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  outline: none;
  transition: all 0.2s;
  resize: none;
}

.custom-input:focus {
  border-color: #9a62ff;
  background: #fff;
}

.custom-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-input {
  appearance: none;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.hint-text {
  font-size: 12px;
  color: #a0aec0;
  font-weight: bold;
}
.hint-icon { color: #9a62ff; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 24px;
  border-top: 1px solid #f0ebff;
}

.btn-ghost {
  background: transparent;
  border: none;
  color: #718096;
  font-weight: bold;
  padding: 12px 24px;
  border-radius: 16px;
  cursor: pointer;
}

.btn-primary {
  background: #432874;
  color: #fff;
  border: none;
  font-weight: bold;
  padding: 12px 32px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) { background: #6133b4; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* ─── Попап Награды ─── */
.reward-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(6px);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.reward-card {
  background: linear-gradient(180deg, #432874 0%, #2a1a5e 100%);
  border: 6px solid #fdd243;
  border-radius: 40px;
  padding: 40px;
  width: 100%;
  max-width: 440px;
  text-align: center;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.reward-trophy {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 80px;
  filter: drop-shadow(0 10px 10px rgba(0,0,0,0.2));
}

.reward-title {
  font-family: 'Intro Black', sans-serif;
  font-size: 32px;
  color: #fff;
  margin: 20px 0 16px 0;
}

.reward-phrase-box {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 24px;
}

.reward-phrase {
  font-size: 15px;
  color: #e8d5ff;
  margin: 0;
  font-style: italic;
}

.reward-items {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
}

.reward-item {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 24px;
  padding: 16px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.reward-val {
  font-size: 36px;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 8px;
}
.reward-val.xp { color: #fdd243; }
.reward-val.gold { color: #ff944c; }

.reward-label {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: bold;
}

.level-up-banner {
  background: linear-gradient(90deg, #24cc8f, #10b981);
  color: white;
  font-weight: 900;
  font-size: 18px;
  padding: 12px;
  border-radius: 16px;
  margin-bottom: 16px;
  animation: bounce 1s infinite;
}

.achievement-banner {
  background: linear-gradient(90deg, #3bcad7, #3182ce);
  color: white;
  font-weight: bold;
  padding: 12px;
  border-radius: 16px;
  margin-bottom: 16px;
}

.btn-claim {
  background: linear-gradient(90deg, #fdd243, #d69e2e);
  color: #2a1a5e;
  border: none;
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-claim:hover { transform: scale(1.02); }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

.reward-pop-enter-active { animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }
@keyframes popIn {
  0% { opacity: 0; transform: scale(0.5) translateY(50px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* ─── Адаптив ─── */
@media (max-width: 900px) {
  .profile-card { flex-direction: column; text-align: center; }
  .profile-header { flex-direction: column; align-items: center; gap: 16px; }
  .header-badges { align-items: center; }
  .stats-row { justify-content: center; }
  .columns-grid { grid-template-columns: 1fr; }
}
</style>