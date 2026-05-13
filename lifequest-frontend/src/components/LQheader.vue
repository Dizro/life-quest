<template>
  <header class="lq-header">
    <div class="header-inner">
      <button class="burger-btn" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Меню">
        <span class="burger-line" :class="{ open: mobileMenuOpen }"></span>
        <span class="burger-line" :class="{ open: mobileMenuOpen }"></span>
        <span class="burger-line" :class="{ open: mobileMenuOpen }"></span>
      </button>

      <router-link to="/mainpage" class="logo">LifeQuest</router-link>

      <nav class="nav-links">
        <router-link to="/mainpage">Главная</router-link>
        <router-link to="/shop">Магазин</router-link>
        <router-link to="/groups">Группы</router-link>
        <router-link to="/statistics">Статистика</router-link>
        <router-link to="/chat" class="farryx-link">Фаррикс 🧙</router-link>
      </nav>

      <div class="header-right">
        <div class="stat-chip hide-mobile" title="Золото">
          <span class="stat-icon">💰</span>
          <span class="stat-val">{{ authStore.gold }}</span>
        </div>
        <div class="stat-chip hide-mobile" title="Кристаллы">
          <span class="stat-icon">💎</span>
          <span class="stat-val">{{ authStore.crystals }}</span>
        </div>
        <div class="stat-chip streak-chip hide-mobile" title="Стрик" v-if="authStore.streakDays >= 3">
          <span class="stat-icon">🔥</span>
          <span class="stat-val">{{ authStore.streakDays }}</span>
        </div>
        <div class="stat-chip hide-tablet" title="Опыт">
          <span class="stat-icon">✨</span>
          <span class="stat-val">{{ authStore.userXP }}</span>
        </div>

        <button class="icon-btn hide-mobile" @click="handleMessages" title="Сообщения">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
          </svg>
        </button>

        <div class="user-menu" @click="toggleDropdown" ref="menuRef">
          <div class="avatar-circle">{{ userInitial }}</div>
          <span class="username-label">{{ authStore.displayName }}</span>
          <span class="caret" :class="{ open: dropdownOpen }">&#x25be;</span>

          <Transition name="dropdown-fade">
            <div v-if="dropdownOpen" class="dropdown-panel" @click.stop>
              <div class="dropdown-header">
                <div class="avatar-circle avatar-lg">{{ userInitial }}</div>
                <div>
                  <div class="dname">{{ authStore.displayName }}</div>
                  <div class="dlevel">Уровень {{ authStore.userLevel }}</div>
                </div>
              </div>
              <div class="dropdown-xp">
                <div class="xp-label-row">
                  <span>XP</span>
                  <span>{{ authStore.userXP }} / {{ authStore.xpToNext }}</span>
                </div>
                <div class="xp-track">
                  <div class="xp-fill" :style="{ width: authStore.xpPercentage + '%' }"></div>
                </div>
              </div>
              <div class="dropdown-divider"></div>
              
              <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
                <span>👤</span> Профиль
              </router-link>
              <router-link to="/character" class="dropdown-item" @click="closeDropdown">
                <span>⚔️</span> Персонаж
              </router-link>
              <router-link to="/achivements" class="dropdown-item" @click="closeDropdown">
                <span>🏆</span> Достижения
              </router-link>
              <router-link to="/settings" class="dropdown-item" @click="closeDropdown">
                <span>⚙️</span> Настройки
              </router-link>
              
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout-item" @click="logout">
                <span>🚪</span> Выйти
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Mobile drawer -->
    <Transition name="drawer-fade">
      <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false"></div>
    </Transition>
    <Transition name="drawer-slide">
      <nav v-if="mobileMenuOpen" class="mobile-drawer">
        <div class="mobile-stats">
          <div class="stat-chip"><span class="stat-icon">💰</span><span class="stat-val">{{ authStore.gold }}</span></div>
          <div class="stat-chip"><span class="stat-icon">💎</span><span class="stat-val">{{ authStore.crystals }}</span></div>
          <div class="stat-chip" v-if="authStore.streakDays >= 3"><span class="stat-icon">🔥</span><span class="stat-val">{{ authStore.streakDays }}</span></div>
          <div class="stat-chip"><span class="stat-icon">✨</span><span class="stat-val">{{ authStore.userXP }}</span></div>
        </div>
        <div class="mobile-nav-links">
          <router-link to="/mainpage" @click="mobileMenuOpen = false">Главная</router-link>
          <router-link to="/shop" @click="mobileMenuOpen = false">Магазин</router-link>
          <router-link to="/groups" @click="mobileMenuOpen = false">Группы</router-link>
          <router-link to="/statistics" @click="mobileMenuOpen = false">Статистика</router-link>
          <router-link to="/chat" @click="mobileMenuOpen = false" class="farryx-link">Фаррикс 🧙</router-link>
        </div>
      </nav>
    </Transition>
  </header>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'LQheader',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      dropdownOpen: false,
      mobileMenuOpen: false
    }
  },
  computed: {
    userInitial() {
      const name = this.authStore.displayName
      return name ? name[0].toUpperCase() : 'Л'
    }
  },
  mounted() {
    document.addEventListener('click', this.handleOutsideClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleOutsideClick)
  },
  methods: {
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen
    },
    closeDropdown() {
      this.dropdownOpen = false
    },
    handleOutsideClick(e) {
      if (this.$refs.menuRef && !this.$refs.menuRef.contains(e.target)) {
        this.dropdownOpen = false
      }
    },
    handleMessages() {
      // Placeholder for messages functionality
    },
    logout() {
      this.authStore.logout()
      this.$router.push('/')
    }
  },
  watch: {
    '$route'() {
      this.mobileMenuOpen = false
    }
  }
}
</script>

<style scoped>
.lq-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #432874;
  height: 67px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}

.header-inner {
  width: 100%;
  max-width: 1920px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  gap: 0;
}

.logo {
  font-family: 'Intro Black', Helvetica, sans-serif;
  font-size: 24px;
  font-weight: 900;
  color: #fff;
  text-decoration: none;
  letter-spacing: 1px;
  white-space: nowrap;
  margin-right: 40px;
  flex-shrink: 0;
}

.nav-links {
  display: flex;
  gap: 24px;
  flex: 1;
}

.nav-links a {
  font-family: 'Varela Round', sans-serif;
  color: #d5c8ff;
  font-size: 15px;
  text-decoration: none;
  transition: color 0.2s;
  white-space: nowrap;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 4px 10px;
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #fff;
}

.stat-icon { font-size: 16px; }
.stat-val { font-weight: 700; }

.icon-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: #d5c8ff;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.icon-btn:hover { background: rgba(255,255,255,0.2); }

.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 30px;
  transition: background 0.2s;
  background: rgba(255,255,255,0.08);
}
.user-menu:hover { background: rgba(255,255,255,0.15); }

.avatar-circle {
  width: 32px;
  height: 32px;
  background: #d5c8ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #422974;
  font-weight: 900;
  font-size: 14px;
  flex-shrink: 0;
}

.avatar-lg {
  width: 44px;
  height: 44px;
  font-size: 18px;
}

.username-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #fff;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.caret {
  color: #d5c8ff;
  font-size: 12px;
  transition: transform 0.2s;
  line-height: 1;
}
.caret.open { transform: rotate(180deg); }

/* Dropdown */
.dropdown-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: #fff;
  min-width: 240px;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.2);
  overflow: hidden;
  z-index: 1001;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 16px 12px;
  background: #f8f4ff;
}

.dname {
  font-family: 'Varela Round', sans-serif;
  font-weight: 700;
  font-size: 15px;
  color: #1a1a1a;
}

.dlevel {
  font-size: 12px;
  color: #7c5cbf;
  font-family: 'Varela Round', sans-serif;
}

.dropdown-xp {
  padding: 10px 16px;
  background: #f8f4ff;
}

.xp-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #7c5cbf;
  font-family: 'Varela Round', sans-serif;
  margin-bottom: 4px;
}

.xp-track {
  height: 6px;
  background: #e0d6ff;
  border-radius: 3px;
  overflow: hidden;
}

.xp-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #9864ff);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.dropdown-divider {
  height: 1px;
  background: #f0ecf8;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 16px;
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #2a2a2a;
  text-decoration: none;
  transition: background 0.15s;
  cursor: pointer;
  width: 100%;
  background: none;
  border: none;
  text-align: left;
}

.dropdown-item:hover { background: #f5f0ff; color: #422974; }

.logout-item { color: #e53e3e; }
.logout-item:hover { background: #fff5f5; color: #c53030; }

/* Burger button - hidden on desktop */
.burger-btn {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  z-index: 10;
}
.burger-line {
  width: 22px;
  height: 2px;
  background: #d5c8ff;
  border-radius: 2px;
  transition: transform 0.25s, opacity 0.25s;
}
.burger-line.open:nth-child(1) { transform: translateY(6px) rotate(45deg); }
.burger-line.open:nth-child(2) { opacity: 0; }
.burger-line.open:nth-child(3) { transform: translateY(-6px) rotate(-45deg); }

/* Farryx link special color */
.farryx-link { color: #fdd243 !important; font-weight: 700 !important; }

/* Mobile drawer */
.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 998;
}
.mobile-drawer {
  display: none;
  position: fixed;
  top: 67px;
  left: 0;
  right: 0;
  background: #3a2063;
  z-index: 999;
  padding: 16px 20px 20px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  flex-direction: column;
  gap: 16px;
}
.mobile-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.mobile-nav-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.mobile-nav-links a {
  font-family: 'Varela Round', sans-serif;
  color: #d5c8ff;
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  transition: background 0.15s;
}
.mobile-nav-links a:hover,
.mobile-nav-links a.router-link-active {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

/* Transition */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity 0.2s; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity: 0; }
.drawer-slide-enter-active, .drawer-slide-leave-active { transition: transform 0.25s ease, opacity 0.25s ease; }
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateY(-10px); opacity: 0; }

/* ─── Responsive ─── */
@media (max-width: 1100px) {
  .header-inner { padding: 0 16px; }
  .logo { margin-right: 24px; font-size: 20px; }
  .nav-links { gap: 16px; }
  .nav-links a { font-size: 13px; }
  .header-right { gap: 8px; }
  .stat-chip { padding: 3px 8px; font-size: 12px; }
  .hide-tablet { display: none !important; }
}

@media (max-width: 768px) {
  .nav-links { display: none; }
  .hide-mobile { display: none !important; }
  .burger-btn { display: flex; }
  .mobile-overlay { display: block; }
  .mobile-drawer { display: flex; }
  .logo { margin-right: auto; font-size: 18px; }
  .header-inner { gap: 12px; }
  .username-label { display: none; }
  .caret { display: none; }
  .user-menu { padding: 4px; }
}

@media (max-width: 480px) {
  .header-inner { padding: 0 12px; }
  .logo { font-size: 16px; }
}
</style>