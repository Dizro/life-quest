<template>
  <div class="page-wrapper">
    <div class="settings-page">
      <header class="page-header">
        <h1 class="page-title">Настройки</h1>
        <p class="page-subtitle">Управляй своим аккаунтом и предпочтениями</p>
      </header>

      <div v-if="successMsg" class="toast success">{{ successMsg }}</div>
      <div v-if="errorMsg" class="toast error">{{ errorMsg }}</div>

      <!-- Profile Section -->
      <section class="settings-section">
        <h2 class="section-title">👤 Профиль</h2>
        <div class="settings-card">
          <div class="field-row">
            <label>Имя героя</label>
            <input v-model="form.display_name" class="settings-input" placeholder="Твоё имя..." maxlength="100" />
          </div>
          <div class="field-row">
            <label>Имя пользователя</label>
            <input :value="authStore.user?.username" class="settings-input disabled" disabled />
          </div>
          <div class="field-row">
            <label>Email</label>
            <input :value="authStore.user?.email" class="settings-input disabled" disabled />
          </div>
          <div class="field-row">
            <label>Класс</label>
            <input :value="authStore.user?.character_class" class="settings-input disabled" disabled />
          </div>
          <div class="field-row">
            <label>Дата регистрации</label>
            <input :value="registeredDate" class="settings-input disabled" disabled />
          </div>
          <button class="save-btn" @click="saveProfile" :disabled="saving">
            {{ saving ? 'Сохраняем...' : 'Сохранить профиль' }}
          </button>
        </div>
      </section>

      <!-- Notifications Section -->
      <section class="settings-section">
        <h2 class="section-title">🔔 Уведомления</h2>
        <div class="settings-card">
          <div class="toggle-row">
            <div class="toggle-info">
              <span class="toggle-label">Напоминания о дедлайнах</span>
              <span class="toggle-desc">Уведомления когда задача скоро истекает</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="form.notifications_deadlines" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="toggle-row">
            <div class="toggle-info">
              <span class="toggle-label">Вечерние напоминания</span>
              <span class="toggle-desc">Напоминание выполнить задачи вечером</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="form.notifications_evening" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="toggle-row">
            <div class="toggle-info">
              <span class="toggle-label">Достижения</span>
              <span class="toggle-desc">Уведомления о новых достижениях</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="form.notifications_achievements" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <button class="save-btn" @click="saveNotifications" :disabled="saving">
            {{ saving ? 'Сохраняем...' : 'Сохранить' }}
          </button>
        </div>
      </section>

      <!-- Appearance Section -->
      <section class="settings-section">
        <h2 class="section-title">🎨 Оформление</h2>
        <div class="settings-card">
          <div class="field-row">
            <label>Тема</label>
            <div class="theme-selector">
              <button
                class="theme-btn"
                :class="{ active: form.theme === 'light' }"
                @click="form.theme = 'light'"
              >☀️ Светлая</button>
              <button
                class="theme-btn"
                :class="{ active: form.theme === 'dark', locked: !hasNightTheme }"
                @click="hasNightTheme ? form.theme = 'dark' : null"
                :disabled="!hasNightTheme"
              >🌙 Тёмная
                <span v-if="!hasNightTheme" class="lock-hint">🔒 Магазин</span>
              </button>
            </div>
            <p v-if="!hasNightTheme" class="theme-hint">Тема «Ночь» доступна в магазине за 200 💰</p>
          </div>
          <div class="field-row">
            <label>Язык</label>
            <div class="theme-selector">
              <button
                class="theme-btn"
                :class="{ active: form.language === 'ru' }"
                @click="form.language = 'ru'"
              >🇷🇺 Русский</button>
              <button
                class="theme-btn"
                :class="{ active: form.language === 'en' }"
                @click="form.language = 'en'"
              >🇺🇸 English</button>
            </div>
          </div>
          <button class="save-btn" @click="saveAppearance" :disabled="saving">
            {{ saving ? 'Сохраняем...' : 'Сохранить' }}
          </button>
        </div>
      </section>

      <!-- Security Section -->
      <section class="settings-section">
        <h2 class="section-title">🔒 Безопасность</h2>
        <div class="settings-card">
          <div class="field-row">
            <label>Текущий пароль</label>
            <input v-model="passwordForm.current" type="password" class="settings-input" placeholder="••••••••" />
          </div>
          <div class="field-row">
            <label>Новый пароль</label>
            <input v-model="passwordForm.newPass" type="password" class="settings-input" placeholder="Минимум 8 символов" />
          </div>
          <div class="field-row">
            <label>Подтверждение</label>
            <input v-model="passwordForm.confirm" type="password" class="settings-input" placeholder="Повтори новый пароль" />
          </div>
          <button class="save-btn" @click="changePassword" :disabled="saving">
            {{ saving ? 'Меняем...' : 'Сменить пароль' }}
          </button>
        </div>
      </section>

      <!-- Danger Zone -->
      <section class="settings-section danger-zone">
        <h2 class="section-title">⚠️ Опасная зона</h2>
        <div class="settings-card danger-card">
          <div class="danger-row">
            <div class="danger-info">
              <span class="danger-label">Выйти из аккаунта</span>
              <span class="danger-desc">Ты будешь перенаправлен на страницу входа</span>
            </div>
            <button class="logout-btn" @click="handleLogout">Выйти</button>
          </div>
          <div class="danger-divider"></div>
          <div class="danger-row">
            <div class="danger-info">
              <span class="danger-label">Удалить аккаунт</span>
              <span class="danger-desc">Все данные будут безвозвратно удалены</span>
            </div>
            <button class="delete-account-btn" @click="handleDeleteAccount">Удалить</button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { usersApi } from '@/services/api'
import { useRouter } from 'vue-router'

export default {
  name: 'SettingsPage',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    return { authStore, router }
  },
  data() {
    return {
      form: {
        display_name: '',
        theme: 'dark',
        language: 'ru',
        notifications_deadlines: true,
        notifications_evening: true,
        notifications_achievements: true,
      },
      passwordForm: {
        current: '',
        newPass: '',
        confirm: '',
      },
      saving: false,
      successMsg: null,
      errorMsg: null,
    }
  },
  computed: {
    registeredDate() {
      const d = this.authStore.user?.created_at
      if (!d) return '—'
      return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    },
    hasNightTheme() {
      // Тема «Ночь» доступна только если куплена в магазине (item_key: theme_night)
      const inv = this.authStore.user?.inventory || []
      return inv.some(i => i.item_key === 'theme_night')
    }
  },
  mounted() {
    this.loadFromStore()
  },
  methods: {
    loadFromStore() {
      const u = this.authStore.user
      if (!u) return
      this.form.display_name = u.display_name || ''
      this.form.theme = u.theme || 'dark'
      this.form.language = u.language || 'ru'
      this.form.notifications_deadlines = u.notifications_deadlines ?? true
      this.form.notifications_evening = u.notifications_evening ?? true
      this.form.notifications_achievements = u.notifications_achievements ?? true
    },

    flash(msg, isError = false) {
      if (isError) {
        this.errorMsg = msg
        this.successMsg = null
      } else {
        this.successMsg = msg
        this.errorMsg = null
      }
      setTimeout(() => { this.successMsg = null; this.errorMsg = null }, 3000)
    },

    async saveProfile() {
      this.saving = true
      try {
        await usersApi.updateMe({ display_name: this.form.display_name })
        await this.authStore.fetchProfile()
        this.flash('Профиль сохранён')
      } catch (e) {
        this.flash(e?.detail || 'Ошибка сохранения', true)
      } finally {
        this.saving = false
      }
    },

    async saveNotifications() {
      this.saving = true
      try {
        await usersApi.updateMe({
          notifications_deadlines: this.form.notifications_deadlines,
          notifications_evening: this.form.notifications_evening,
          notifications_achievements: this.form.notifications_achievements,
        })
        await this.authStore.fetchProfile()
        this.flash('Уведомления обновлены')
      } catch (e) {
        this.flash(e?.detail || 'Ошибка', true)
      } finally {
        this.saving = false
      }
    },

    async saveAppearance() {
      this.saving = true
      try {
        await usersApi.updateMe({
          theme: this.form.theme,
          language: this.form.language,
        })
        await this.authStore.fetchProfile()
        this.flash('Оформление сохранено')
      } catch (e) {
        this.flash(e?.detail || 'Ошибка', true)
      } finally {
        this.saving = false
      }
    },

    async changePassword() {
      if (!this.passwordForm.current) {
        this.flash('Введи текущий пароль', true)
        return
      }
      if (this.passwordForm.newPass.length < 8) {
        this.flash('Новый пароль — минимум 8 символов', true)
        return
      }
      if (this.passwordForm.newPass !== this.passwordForm.confirm) {
        this.flash('Пароли не совпадают', true)
        return
      }
      this.saving = true
      try {
        await usersApi.changePassword({
          current_password: this.passwordForm.current,
          new_password: this.passwordForm.newPass,
        })
        this.passwordForm = { current: '', newPass: '', confirm: '' }
        this.flash('Пароль изменён')
      } catch (e) {
        this.flash(e?.detail || 'Ошибка смены пароля', true)
      } finally {
        this.saving = false
      }
    },

    handleLogout() {
      this.authStore.logout()
      this.router.push('/')
    },

    async handleDeleteAccount() {
      if (!confirm('Ты уверен? Все данные, прогресс, достижения — всё будет удалено безвозвратно!')) return
      if (!confirm('ТОЧНО уверен? Это последнее предупреждение.')) return
      try {
        await usersApi.deleteAccount()
        this.authStore.logout()
        this.router.push('/')
      } catch (e) {
        this.flash(e?.detail || 'Ошибка удаления', true)
      }
    },
  }
}
</script>

<style scoped>
.page-wrapper {
  min-height: calc(100vh - 67px);
  background: linear-gradient(160deg, #f4f0ff 0%, #e8d5ff 40%, #c9a6ff 100%);
  padding: 32px 24px;
}
.settings-page {
  max-width: 680px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.page-header { text-align: center; }
.page-title { font-family: 'Varela Round', sans-serif; font-size: 36px; font-weight: 700; color: #2a1a5e; margin-bottom: 8px; }
.page-subtitle { font-family: 'Varela Round', sans-serif; font-size: 16px; color: #5a4a7a; }

/* Toast */
.toast {
  padding: 14px 20px; border-radius: 14px; text-align: center;
  font-family: 'Varela Round', sans-serif; font-size: 15px; font-weight: 700;
  animation: fadeSlideDown 0.3s ease;
}
.toast.success { background: #c6f6d5; color: #22543d; }
.toast.error { background: #fed7d7; color: #9b2c2c; }
@keyframes fadeSlideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Section */
.settings-section { display: flex; flex-direction: column; gap: 12px; }
.section-title { font-family: 'Varela Round', sans-serif; font-size: 18px; font-weight: 700; color: #2a1a5e; margin: 0; }
.settings-card {
  background: #fff; border-radius: 20px; padding: 24px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
  display: flex; flex-direction: column; gap: 16px;
}

/* Field row */
.field-row { display: flex; flex-direction: column; gap: 6px; }
.field-row label {
  font-family: 'Varela Round', sans-serif; font-size: 13px;
  font-weight: 700; color: #5a4a7a; text-transform: uppercase; letter-spacing: 0.5px;
}
.settings-input {
  padding: 12px 16px; border: 1px solid #d5c8ff; border-radius: 14px;
  font-family: 'Varela Round', sans-serif; font-size: 15px;
  outline: none; transition: border-color 0.2s; background: #fff; color: #2a1a5e;
}
.settings-input:focus { border-color: #9a62ff; }
.settings-input.disabled { background: #f7f5ff; color: #a09abc; cursor: not-allowed; }

/* Toggle */
.toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0;
}
.toggle-info { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.toggle-label { font-family: 'Varela Round', sans-serif; font-size: 15px; font-weight: 700; color: #2a1a5e; }
.toggle-desc { font-size: 13px; color: #7c5cbf; }

.toggle-switch { position: relative; width: 52px; height: 28px; flex-shrink: 0; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
  position: absolute; cursor: pointer; inset: 0;
  background: #d5c8ff; border-radius: 28px; transition: 0.3s;
}
.toggle-slider::before {
  content: ''; position: absolute; width: 22px; height: 22px;
  left: 3px; bottom: 3px; background: #fff; border-radius: 50%;
  transition: 0.3s;
}
.toggle-switch input:checked + .toggle-slider { background: #9a62ff; }
.toggle-switch input:checked + .toggle-slider::before { transform: translateX(24px); }

/* Theme selector */
.theme-selector { display: flex; gap: 10px; }
.theme-btn {
  flex: 1; padding: 12px; border-radius: 14px;
  border: 2px solid #f0ebff; background: #faf8ff;
  font-family: 'Varela Round', sans-serif; font-size: 14px;
  font-weight: 700; color: #5a4a7a; cursor: pointer;
  transition: all 0.2s;
}
.theme-btn:hover:not(:disabled) { border-color: #d5c8ff; }
.theme-btn.active { border-color: #9a62ff; background: #ede5ff; color: #2a1a5e; }
.theme-btn.locked {
  opacity: 0.5; cursor: not-allowed; position: relative;
  border-style: dashed; background: #f7f5ff;
}
.theme-btn .lock-hint {
  display: block; font-size: 10px; color: #a09abc; margin-top: 2px;
}
.theme-hint {
  font-size: 12px; color: #a09abc; margin: 4px 0 0 0;
  font-style: italic;
}

/* Save button */
.save-btn {
  padding: 14px; border-radius: 14px; background: #9a62ff;
  color: #fff; border: none; font-family: 'Varela Round', sans-serif;
  font-size: 16px; font-weight: 700; cursor: pointer;
  transition: background 0.2s; margin-top: 4px;
}
.save-btn:hover:not(:disabled) { background: #8a50ef; }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* Danger zone */
.danger-zone .section-title { color: #e53e3e; }
.danger-card { border: 2px solid #fed7d7; }
.danger-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.danger-info { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.danger-label { font-family: 'Varela Round', sans-serif; font-size: 15px; font-weight: 700; color: #2a1a5e; }
.danger-desc { font-size: 13px; color: #7c5cbf; }
.danger-divider { height: 1px; background: #fed7d7; }

.logout-btn {
  padding: 10px 24px; border-radius: 12px;
  background: #f4f0ff; border: 2px solid #d5c8ff;
  font-family: 'Varela Round', sans-serif; font-size: 14px;
  font-weight: 700; color: #5a4a7a; cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.logout-btn:hover { background: #ede5ff; border-color: #9a62ff; }

.delete-account-btn {
  padding: 10px 24px; border-radius: 12px;
  background: #fff5f5; border: 2px solid #e53e3e;
  font-family: 'Varela Round', sans-serif; font-size: 14px;
  font-weight: 700; color: #e53e3e; cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.delete-account-btn:hover { background: #fed7d7; }

/* Responsive */
@media (max-width: 600px) {
  .page-title { font-size: 28px; }
  .settings-card { padding: 20px; }
  .theme-selector { flex-direction: column; }
  .danger-row { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>
