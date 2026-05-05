<template>
  <div class="page-wrapper">
    <div class="shop-page">
      <header class="page-header">
        <h1 class="page-title">Магазин</h1>
        <p class="page-subtitle">Трать заработанные монеты и кристаллы на снаряжение и питомцев.</p>
        
        <div v-if="error" class="error-banner">{{ error }}</div>
        <div v-if="successMsg" class="success-banner">{{ successMsg }}</div>
      </header>

      <!-- Shop categories -->
      <div class="tab-bar">
        <button 
          v-for="cat in categories" 
          :key="cat.id"
          class="tab-btn"
          :class="{ active: activeCategory === cat.id }"
          @click="activeCategory = cat.id"
        >
          <span class="tab-icon">{{ cat.icon }}</span>
          <span class="tab-label">{{ cat.label }}</span>
        </button>
      </div>

      <div class="shop-grid">
        <div v-for="item in filteredItems" :key="item.id" class="shop-card">
          <div class="item-image-wrapper">
            <img :src="getAsset(item.folder, item.asset, '.png')" :alt="item.name" class="item-img" />
          </div>
          <div class="item-info">
            <h3 class="item-name">{{ item.name }}</h3>
            <p class="item-desc">{{ item.description }}</p>
          </div>
          <div class="item-action">
            <button class="buy-btn" @click="buyItem(item)" :disabled="loading">
              <span v-if="item.priceGold" class="price gold">💰 {{ item.priceGold }}</span>
              <span v-if="item.priceCrystal" class="price crystal">💎 {{ item.priceCrystal }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { tasksApi } from '@/services/api'

export default {
  name: 'ShopPage',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      activeCategory: 'clothes',
      error: null,
      successMsg: null,
      loading: false,
      categories: [
        { id: 'clothes', icon: '👕', label: 'Одежда' },
        { id: 'accessories', icon: '🎩', label: 'Аксессуары' },
        { id: 'pets', icon: '🐾', label: 'Питомцы' },
        { id: 'buffs', icon: '⚡', label: 'Баффы' }
      ],
      items: [
        { id: 'hat_adv', category: 'accessories', folder: 'accessories', asset: 'hat_wizard_blue', name: 'Шляпа авантюриста', description: 'Базовый косметический предмет', priceGold: 50, priceCrystal: 0 },
        { id: 'cloak_traveler', category: 'clothes', folder: 'clothes/tops', asset: 'jacket_green', name: 'Плащ путника', description: 'Скин персонажа ≈ 2 дня честной игры', priceGold: 120, priceCrystal: 0 },
        { id: 'armor_hero', category: 'clothes', folder: 'clothes/tops', asset: 'sweater_striped_red', name: 'Доспехи героя', description: 'Продвинутый скин ≈ 5–6 дней игры', priceGold: 300, priceCrystal: 0 },
        { id: 'buff_gold', category: 'buffs', folder: 'items', asset: 'potion_gold', name: 'Победный дух', description: '×1.5 Gold на 24 часа', priceGold: 50, priceCrystal: 0 },
        { id: 'theme_night', category: 'buffs', folder: 'items', asset: 'scroll_night', name: 'Тема «Ночь»', description: 'Тёмная тема интерфейса', priceGold: 200, priceCrystal: 0 },
        { id: 'pet_slime', category: 'pets', folder: 'pet', asset: 'pet_snake', name: 'Слизень', description: 'Базовый питомец ≈ уровень 5', priceGold: 0, priceCrystal: 5 },
        { id: 'pet_phoenix', category: 'pets', folder: 'pet', asset: 'pet_cat', name: 'Феникс', description: 'Редкий питомец ≈ 30 дней игры', priceGold: 0, priceCrystal: 25 },
        { id: 'pet_dragon', category: 'pets', folder: 'pet', asset: 'pet_dragon', name: 'Дракончик', description: 'Эксклюзив: только для стрика 30+ дней', priceGold: 0, priceCrystal: 50 },
      ]
    }
  },
  computed: {
    filteredItems() {
      return this.items.filter(i => i.category === this.activeCategory)
    }
  },
  methods: {
    getAsset(folder, name, ext = '.png') {
      try {
        return new URL(`../assets/${folder}/${name}${ext}`, import.meta.url).href
      } catch (e) {
        return 'https://via.placeholder.com/150x150?text=Item'
      }
    },
    async buyItem(item) {
      this.error = null
      this.successMsg = null
      
      // Check funds locally first to avoid unnecessary requests
      if (item.priceGold > this.authStore.gold) {
        this.error = 'Недостаточно золота!'
        return
      }
      if (item.priceCrystal > this.authStore.crystals) {
        this.error = 'Недостаточно кристаллов!'
        return
      }

      this.loading = true
      try {
        // Mock API call for MVP
        // await axios.post('/api/v1/shop/buy', { item_id: item.id })
        
        // Update local store
        this.authStore.user.coins -= item.priceGold
        // this.authStore.user.crystals -= item.priceCrystal // if crystals existed in user object
        
        this.successMsg = `Вы успешно купили: ${item.name}!`
        setTimeout(() => { this.successMsg = null }, 3000)
      } catch (err) {
        this.error = err?.response?.data?.detail || 'Ошибка при покупке (INSUFFICIENT_FUNDS)'
      } finally {
        this.loading = false
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

.shop-page {
  max-width: 1200px;
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

.error-banner {
  background: #fff5f5;
  color: #c53030;
  border: 1px solid #feb2b2;
  padding: 12px;
  border-radius: 8px;
  margin-top: 16px;
  font-family: 'Varela Round', sans-serif;
}

.success-banner {
  background: #f0fff4;
  color: #2f855a;
  border: 1px solid #9ae6b4;
  padding: 12px;
  border-radius: 8px;
  margin-top: 16px;
  font-family: 'Varela Round', sans-serif;
}

.tab-bar {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 16px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #fff;
  border: 2px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(66,41,116,0.08);
}

.tab-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66,41,116,0.12);
}

.tab-btn.active {
  background: #432874;
  color: #fff;
}

.tab-btn.active .tab-label {
  color: #fff;
}

.tab-icon {
  font-size: 20px;
}

.tab-label {
  font-family: 'Varela Round', sans-serif;
  font-weight: 700;
  font-size: 14px;
  color: #5a4a7a;
}

.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.shop-card {
  background: #fff;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 8px 24px rgba(66,41,116,0.08);
  transition: all 0.3s;
}

.shop-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(66,41,116,0.15);
}

.item-image-wrapper {
  background: #f4f0ff;
  border-radius: 16px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.item-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.item-info {
  flex: 1;
  text-align: center;
}

.item-name {
  font-family: 'Varela Round', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #2a1a5e;
  margin-bottom: 8px;
}

.item-desc {
  font-family: 'Varela Round', sans-serif;
  font-size: 13px;
  color: #7c5cbf;
  line-height: 1.4;
}

.item-action {
  margin-top: auto;
}

.buy-btn {
  width: 100%;
  background: #f4f0ff;
  border: 2px solid #d5c8ff;
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.buy-btn:hover:not(:disabled) {
  background: #e8d5ff;
  border-color: #9a62ff;
}

.buy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.price {
  font-family: 'Varela Round', sans-serif;
  font-weight: 700;
  font-size: 15px;
}

.price.gold { color: #d69e2e; }
.price.crystal { color: #3182ce; }
</style>