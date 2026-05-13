<template>
  <div class="lifequest-landing">
    <header class="nav">
      <div class="nav-container">
        <a class="logo" href="#" aria-label="LifeQuest — на главную">
          LifeQuest
        </a>
        <button class="nav-button" type="button" @click="toggleMode">
          {{ mode === 'login' ? 'Регистрация' : 'Войти' }}
        </button>
      </div>
    </header>

    <main class="main-content">
      <section class="hero-section">
        <div class="hero-container">
          
          <div class="hero-left">
            <div class="hero-text-content">
              <h1 class="heading-motivate">Превращай рутину<br>в квесты</h1>
              <p class="hero-subtitle">
                LifeQuest — это геймифицированный трекер задач в формате RPG с ИИ-наставником. 
                Твоя легенда начинается здесь.
              </p>
            </div>

            <div class="hero-visuals">
              <div class="flying-artifacts">
                <span class="artifact a-1">✨</span>
                <span class="artifact a-2">🛡️</span>
                <span class="artifact a-3">🗡️</span>
                <span class="artifact a-4">💎</span>
                <span class="artifact a-5">✨</span>
              </div>
              
              <div class="characters-wrapper">
                <img class="characters-image" src="../assets/characters/spritesheet_characters.png" alt="Герои LifeQuest" />
              </div>
            </div>
          </div>

          <div class="hero-right">
            <div class="auth-card">
              <h2 class="heading-sign-up">
                {{ mode === 'login' ? 'С возвращением!' : 'Зарегистрироваться' }}
              </h2>

              <div v-if="error" class="error-banner">{{ error }}</div>

              <form class="auth-form" @submit.prevent="handleSubmit">
                
                <div v-if="mode === 'register'" class="input-group">
                  <input 
                    v-model="displayName"
                    class="custom-input" 
                    type="text" 
                    placeholder="Имя персонажа"
                    autocomplete="nickname"
                  />
                </div>

                <div class="input-group">
                  <input 
                    v-model="username"
                    class="custom-input" 
                    :class="{ 'has-error': fieldErrors.username, 'has-success': mode === 'register' && touched.username && !fieldErrors.username && username.length >= 3 }"
                    type="text" 
                    placeholder="Логин (hero_knight)"
                    autocomplete="username"
                    @input="validateUsername"
                    @blur="touchField('username')"
                  />
                  <span v-if="fieldErrors.username" class="error-text">{{ fieldErrors.username }}</span>
                  <span v-else-if="mode === 'register' && touched.username && username.length >= 3" class="success-text">Логин свободен</span>
                </div>

                <div v-if="mode === 'register'" class="input-group">
                  <input 
                    v-model="email"
                    class="custom-input" 
                    :class="{ 'has-error': fieldErrors.email, 'has-success': touched.email && !fieldErrors.email && isValidEmail(email) }"
                    type="email" 
                    placeholder="Email"
                    autocomplete="email"
                    @input="validateEmail"
                    @blur="touchField('email')"
                  />
                  <span v-if="fieldErrors.email" class="error-text">{{ fieldErrors.email }}</span>
                  <span v-else-if="touched.email && isValidEmail(email)" class="success-text">Email корректный</span>
                </div>

                <div class="input-group">
                  <input 
                    v-model="password"
                    class="custom-input" 
                    :class="{ 'has-error': fieldErrors.password, 'has-success': touched.password && !fieldErrors.password && password.length >= 8 }"
                    type="password" 
                    placeholder="Пароль"
                    :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
                    @input="validatePassword"
                    @blur="touchField('password')"
                  />
                  <span v-if="fieldErrors.password" class="error-text">{{ fieldErrors.password }}</span>
                  <div v-else-if="mode === 'register' && password.length > 0" class="password-strength">
                    <div class="strength-bar">
                      <div class="strength-fill" :style="{ width: passwordStrength.percent + '%', background: passwordStrength.color }"></div>
                    </div>
                    <span class="strength-label" :style="{ color: passwordStrength.color }">{{ passwordStrength.label }}</span>
                  </div>
                </div>

                <div v-if="mode === 'register'" class="input-group">
                  <input 
                    v-model="confirmPassword"
                    class="custom-input" 
                    :class="{ 'has-error': fieldErrors.confirmPassword, 'has-success': touched.confirmPassword && !fieldErrors.confirmPassword && confirmPassword.length > 0 && confirmPassword === password }"
                    type="password" 
                    placeholder="Повторите пароль"
                    autocomplete="new-password"
                    @input="validateConfirmPassword"
                    @blur="touchField('confirmPassword')"
                  />
                  <span v-if="fieldErrors.confirmPassword" class="error-text">{{ fieldErrors.confirmPassword }}</span>
                  <span v-else-if="touched.confirmPassword && confirmPassword === password && confirmPassword.length > 0" class="success-text">Пароли совпадают</span>
                </div>

                <div class="submit-action">
                  <button class="submit-button" type="submit" :disabled="loading">
                    <span v-if="loading">Загрузка...</span>
                    <span v-else>Продолжить</span>
                  </button>
                </div>

                <div class="divider">
                  <span>ИЛИ</span>
                </div>

                <div class="oauth-buttons">
                  <button class="oauth-btn" type="button">Войти с помощью ВКонтакте</button>
                  <button class="oauth-btn" type="button">Войти с помощью Яндекс</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      <div class="pixel-transition">
        <svg viewBox="0 0 1896 237" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax slice">
          <g clip-path="url(#clip0_2002_281)">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M1896 117.97H1777.5V-0.530273H1896V117.97ZM1540.5 117.97H1422V-0.530273H1540.5V117.97ZM1659 236.47H1540.5V117.97H1659V236.47ZM1185 236.47H1066.5V117.97H1185V236.47ZM1303.5 117.97H1185V-0.530273H1303.5V117.97ZM1066.5 117.97H948V-0.530273H1066.5V117.97ZM355.5 117.97H237V-0.530273H355.5V117.97ZM829.5 236.47H711V117.97H829.5V236.47ZM474 117.97H355.5V-0.530273H474V117.97ZM711 117.97H592.5V-0.530273H711V117.97ZM237 236.47H118.5V117.97H237V236.47ZM118.5 117.97H0V-0.530273H118.5V117.97Z" fill="#2E71A9"/>
          </g>
          <defs>
            <clipPath id="clip0_2002_281">
              <rect width="1896" height="237" fill="white"/>
            </clipPath>
          </defs>
        </svg>
      </div>

      <section class="features-section">
        <div class="content-container">
          <h2 class="section-title">Игровые механики</h2>
          <p class="section-subtitle">
            LifeQuest объединяет классический таск-менеджмент с элементами RPG. 
            Фаррикс оценивает сложность задач и дает честные награды.
          </p>
          
          <div class="features-grid">
            <article class="feature-card">
              <h3>Трекер дел</h3>
              <p>Превращай рутинные дела в эпичные квесты. ИИ автоматически оценит сложность каждой задачи и назначит награду.</p>
            </article>
            <article class="feature-card">
              <h3>Дедлайны</h3>
              <p>Следи за временем. Невыполненные вовремя задачи наносят урон твоему персонажу, а победы восстанавливают силы.</p>
            </article>
            <article class="feature-card">
              <h3>Группы с друзьями</h3>
              <p>Объединяйтесь в гильдии, ходите в рейды на боссов-привычек и поддерживайте друг друга на пути к общим целям.</p>
            </article>
          </div>
        </div>
      </section>

      <section class="use-cases-section">
        <div class="content-container">
          <h2 class="section-title">Достигай любых целей</h2>
          <p class="section-subtitle">
            Гибкая система настройки делает платформу идеальным инструментом для любых сфер жизни.
          </p>
          
          <div class="features-grid">
            <article class="feature-card">
              <h3>Health and Fitness</h3>
              <p>Никак не начнете ходить в зал? Мы наконец-то сделаем процесс заботы о себе увлекательным.</p>
            </article>
            <article class="feature-card">
              <h3>School and Work</h3>
              <p>Готовите отчет для начальника или курсовую? Легко отслеживайте прогресс тяжелых и комплексных задач.</p>
            </article>
            <article class="feature-card">
              <h3>And much, much more!</h3>
              <p>Наш полностью настраиваемый список задач адаптируется под любые ваши цели, проекты и мечты.</p>
            </article>
          </div>
        </div>
      </section>

      
    </main>

    
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const mode = ref('register') // 'login' | 'register'
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const displayName = ref('')

const loading = ref(false)
const error = ref(null)
const fieldErrors = ref({
  username: null,
  email: null,
  password: null,
  confirmPassword: null
})
const touched = ref({
  username: false,
  email: false,
  password: false,
  confirmPassword: false
})

const touchField = (field) => {
  touched.value[field] = true
  if (field === 'username') validateUsername()
  if (field === 'email') validateEmail()
  if (field === 'password') validatePassword()
  if (field === 'confirmPassword') validateConfirmPassword()
}

const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

const passwordStrength = computed(() => {
  const p = password.value
  if (p.length < 8) return { percent: Math.min(30, p.length * 4), color: '#ff6b6b', label: 'Слишком короткий' }
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  if (score <= 2) return { percent: 40, color: '#ff6b6b', label: 'Слабый' }
  if (score <= 3) return { percent: 65, color: '#f6c90e', label: 'Средний' }
  return { percent: 100, color: '#48bb78', label: 'Надёжный' }
})

const validateUsername = () => {
  if (!touched.value.username && !username.value) return
  if (!username.value || username.value.length < 3) {
    fieldErrors.value.username = 'Минимум 3 символа'
  } else if (!/^[a-zA-Z0-9_]+$/.test(username.value)) {
    fieldErrors.value.username = 'Только латинские буквы, цифры и _'
  } else {
    fieldErrors.value.username = null
  }
}

const validateEmail = () => {
  if (!touched.value.email && !email.value) return
  if (mode.value === 'register') {
    if (!email.value) {
      fieldErrors.value.email = 'Email обязателен'
    } else if (!isValidEmail(email.value)) {
      fieldErrors.value.email = 'Введи корректный email (например user@mail.ru)'
    } else {
      fieldErrors.value.email = null
    }
  }
}

const validatePassword = () => {
  if (!touched.value.password && !password.value) return
  if (!password.value || password.value.length < 8) {
    fieldErrors.value.password = 'Минимум 8 символов'
  } else {
    fieldErrors.value.password = null
  }
  if (confirmPassword.value) validateConfirmPassword()
}

const validateConfirmPassword = () => {
  if (!touched.value.confirmPassword && !confirmPassword.value) return
  if (mode.value === 'register' && password.value !== confirmPassword.value) {
    fieldErrors.value.confirmPassword = 'Пароли не совпадают'
  } else {
    fieldErrors.value.confirmPassword = null
  }
}

const toggleMode = () => {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = null
  fieldErrors.value = { username: null, email: null, password: null, confirmPassword: null }
  touched.value = { username: false, email: false, password: false, confirmPassword: false }
}

const validate = () => {
  touched.value = { username: true, email: true, password: true, confirmPassword: true }
  validateUsername()
  validateEmail()
  validatePassword()
  validateConfirmPassword()
  return !fieldErrors.value.username && !fieldErrors.value.email && !fieldErrors.value.password && !fieldErrors.value.confirmPassword
}

const handleSubmit = async () => {
  if (!validate()) return

  loading.value = true
  error.value = null

  try {
    if (mode.value === 'register') {
      await authStore.register(
        username.value,
        email.value,
        password.value,
        displayName.value || username.value
      )
      router.push({ name: 'Onboarding', query: { name: displayName.value || username.value } })
    } else {
      await authStore.login(username.value, password.value)
      if (!localStorage.getItem('lq_onboarding_done')) {
        router.push({ name: 'Onboarding' })
      } else {
        router.push({ name: 'Main' })
      }
    }
  } catch (err) {
    const detail = err?.detail
    if (typeof detail === 'string') {
      if (detail.toLowerCase().includes('username') || detail.toLowerCase().includes('логин')) {
        fieldErrors.value.username = detail
      } else if (detail.toLowerCase().includes('email') || detail.toLowerCase().includes('почт')) {
        fieldErrors.value.email = detail
      } else {
        error.value = detail
      }
    } else {
      error.value = authStore.error || 'Что-то пошло не так'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Глобальные стили для компонента */
.lifequest-landing {
  font-family: "Roboto", "Varela Round", Helvetica, sans-serif;
  color: #ffffff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  background-color: #36205d; /* Фон под весь экран, чтобы не было белых полос внизу */
}

/* Навигация */
.nav {
  height: 100px;
  background-color: #296699;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.nav-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-family: "Intro Black", Helvetica, sans-serif;
  font-weight: 900;
  font-size: 24px;
  color: #ffffff;
  text-decoration: none;
  letter-spacing: 1px;
}

.nav-button {
  background-color: #9a62ff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  padding: 8px 24px;
  font-size: 16px;
  font-family: "Varela Round", sans-serif;
  cursor: pointer;
  box-shadow: 0px 1px 3px rgba(26, 24, 29, 0.24);
  transition: background-color 0.2s, outline 0.2s;
}

.nav-button:hover {
  background-color: #894cee;
}
.nav-button:focus-visible {
  outline: 2px solid #ffffff;
  outline-offset: 2px;
}

/* Общие контейнеры */
.content-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* Секция Hero & Form */
.hero-section {
  background-color: #2d71a9;
  padding: 60px 20px 20px 20px;
  display: flex;
  align-items: center;
}

.hero-container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  gap: 60px;
  align-items: flex-start;
}

/* Левая часть и артефакты */
.hero-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding-top: 20px;
}

.heading-motivate {
  font-family: "Varela Round", sans-serif;
  font-size: 56px;
  line-height: 1.1;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 18px;
  line-height: 1.5;
  opacity: 0.9;
  max-width: 500px;
}

/* Зона персонажей и анимаций */
.hero-visuals {
  position: relative;
  width: 100%;
  max-width: 500px;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.flying-artifacts {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.artifact {
  position: absolute;
  font-size: 24px;
  opacity: 0.8;
  animation: float 4s ease-in-out infinite;
}

.a-1 { top: 10%; left: 10%; animation-delay: 0s; }
.a-2 { top: 20%; right: 15%; font-size: 32px; animation-delay: 1s; }
.a-3 { bottom: 30%; left: 5%; font-size: 28px; animation-delay: 2s; }
.a-4 { bottom: 15%; right: 20%; animation-delay: 1.5s; }
.a-5 { top: 50%; left: 80%; font-size: 18px; animation-delay: 0.5s; }

@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(10deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}

.characters-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.characters-image {
  max-width: 110%;
  max-height: 100%;
  object-fit: contain; 
  z-index: 2;
  filter: drop-shadow(0px 10px 20px rgba(0, 0, 0, 0.25)); 
}

/* Правая часть (Форма) */
.hero-right {
  flex: 0 0 420px;
  width: 100%;
}

.auth-card {
  width: 100%;
  background: transparent;
}

.heading-sign-up {
  font-family: "Varela Round", sans-serif;
  font-size: 32px;
  text-align: center;
  margin-bottom: 24px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.custom-input {
  width: 100%;
  background-color: #432874;
  border: 1px solid #563395;
  border-radius: 4px;
  padding: 14px 16px;
  color: #bda8ff;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.custom-input::placeholder {
  color: #bda8ff;
  opacity: 0.8;
}

.custom-input:focus {
  outline: none;
  border-color: #9a62ff;
}

.custom-input.has-error {
  border-color: #ff6b6b;
}

.custom-input.has-success {
  border-color: #48bb78;
}

.error-text {
  font-size: 12px;
  color: #ff6b6b;
  margin-left: 4px;
  animation: fadeIn 0.2s ease;
}

.success-text {
  font-size: 12px;
  color: #48bb78;
  margin-left: 4px;
  animation: fadeIn 0.2s ease;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s, background 0.3s;
}

.strength-label {
  font-size: 11px;
  font-family: 'Varela Round', sans-serif;
  white-space: nowrap;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-banner {
  background: rgba(255, 107, 107, 0.15);
  border: 1px solid #ff6b6b;
  border-radius: 4px;
  padding: 10px;
  color: #ffbaba;
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
}

/* Выравнивание кнопки по центру */
.submit-action {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.submit-button {
  background-color: #ffffff;
  color: #878190;
  border: none;
  border-radius: 4px;
  padding: 14px 40px;
  font-size: 14px;
  font-family: "Roboto", sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 200px;
}

.submit-button:hover:not(:disabled) {
  background-color: #f0f0f0;
}
.submit-button:active:not(:disabled) {
  transform: scale(0.98);
}
.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Разделитель "ИЛИ" */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #ffffff;
  font-size: 14px;
  margin: 10px 0;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.divider span {
  padding: 0 10px;
  font-family: "Varela Round", sans-serif;
}

/* Социальные кнопки */
.oauth-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.oauth-btn {
  background-color: transparent;
  border: 2px solid #bda8ff;
  color: #bda8ff;
  border-radius: 4px;
  padding: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.oauth-btn:hover {
  background-color: rgba(189, 168, 255, 0.1);
}

/* Переходной SVG */
.pixel-transition {
  width: 100%;
  background-color: #432874;
  line-height: 0;
  margin-top: -1px;
}

.pixel-transition svg {
  width: 100%;
  height: auto;
  display: block;
}

/* Секция Features */
.features-section {
  background-color: #432874;
  padding: 60px 20px 80px;
  text-align: center;
}

.section-title {
  font-family: "Varela Round", sans-serif;
  font-size: 48px;
  margin-bottom: 20px;
}

.section-subtitle {
  font-size: 18px;
  opacity: 0.9;
  max-width: 650px;
  margin: 0 auto 60px;
  line-height: 1.5;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.feature-card h3 {
  font-family: "Varela Round", sans-serif;
  font-size: 24px;
  margin-bottom: 16px;
}

.feature-card p {
  font-size: 16px;
  line-height: 1.5;
  opacity: 0.9;
}

/* Секция Use Cases */
.use-cases-section {
  background-color: #36205d;
  padding: 80px 20px 0 20px; /* Убрал отступ снизу, чтобы горы прилегали к контенту */
  text-align: center;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 900px) {
  .hero-container {
    flex-direction: column;
    align-items: center;
    gap: 40px;
  }
  .hero-left {
    text-align: center;
    align-items: center;
  }
  .hero-right {
    flex: unset;
    max-width: 100%;
    width: 100%;
  }
  .features-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  .heading-motivate {
    font-size: 42px;
  }
  .section-title { font-size: 36px; }
  .hero-visuals { height: 220px; }
}

@media (max-width: 600px) {
  .nav { height: 60px; padding: 0 16px; }
  .logo { font-size: 20px; }
  .nav-button { padding: 6px 16px; font-size: 14px; }
  .hero-section { padding: 40px 16px 16px; }
  .heading-motivate { font-size: 32px; }
  .hero-subtitle { font-size: 15px; }
  .heading-sign-up { font-size: 24px; margin-bottom: 16px; }
  .custom-input { padding: 12px 14px; font-size: 13px; }
  .submit-button { padding: 12px 32px; }
  .section-title { font-size: 28px; }
  .section-subtitle { font-size: 15px; margin: 0 auto 40px; }
  .features-section { padding: 40px 16px 60px; }
  .use-cases-section { padding: 40px 16px 0; }
  .hero-visuals { height: 180px; max-width: 300px; }
  .feature-card h3 { font-size: 20px; }
  .feature-card p { font-size: 14px; }
}

@media (max-width: 400px) {
  .heading-motivate { font-size: 26px; }
  .hero-subtitle { font-size: 14px; }
  .heading-sign-up { font-size: 20px; }
  .nav { height: 52px; }
  .logo { font-size: 18px; }
}
</style>