<template>
  <div class="page-wrapper">
    <div class="char-page">
      <!-- LEFT: Character Preview -->
      <aside class="preview-panel">
        <div class="preview-scene">
          <!-- Background layer -->
          <img
            v-if="characterStore.selectedBackground"
            :src="getAsset('backgrounds', characterStore.selectedBackground, '.png')"
            class="layer layer-bg"
            alt=""
          />
          <!-- Body layer -->
          <img
            :src="getAsset('bodies', characterStore.selectedBody, '.png')"
            class="layer layer-body"
            alt=""
          />
          <!-- Bottom clothes -->
          <img
            v-if="characterStore.selectedBottom"
            :src="getBottomAsset(characterStore.selectedBottom)"
            class="layer layer-bottom"
            alt=""
          />
          <!-- Top clothes -->
          <img
            v-if="characterStore.selectedTop"
            :src="getTopAsset(characterStore.selectedTop)"
            class="layer layer-top"
            alt=""
          />
          <!-- Hair layer -->
          <img
            :src="getAsset('hair', characterStore.selectedHair, '.png')"
            class="layer layer-hair"
            alt=""
          />
          <!-- Accessory layer -->
          <img
            v-if="characterStore.selectedAccessory"
            :src="getAsset('accessories', characterStore.selectedAccessory, '.png')"
            class="layer layer-accessory"
            alt=""
          />
          <!-- Item layer -->
          <img
            v-if="characterStore.selectedItem"
            :src="getAsset('items', characterStore.selectedItem, '.png')"
            class="layer layer-item"
            alt=""
          />
          <!-- Pet -->
          <img
            v-if="characterStore.selectedPet"
            :src="getAsset('pet', characterStore.selectedPet, '.png')"
            class="layer layer-pet"
            alt=""
          />
        </div>

        <div class="name-card">
          <div class="name-display">{{ authStore.displayName || 'Герой' }}</div>
          <div class="level-badge">Уровень {{ authStore.userLevel }}</div>
        </div>

        <button class="save-btn" @click="saveCharacter" :class="{ saved: justSaved }">
          {{ justSaved ? '✓ Сохранено!' : 'Сохранить образ' }}
        </button>
      </aside>

      <!-- RIGHT: Customizer Tabs -->
      <section class="customizer-panel">
        <!-- Tab headers -->
        <div class="tab-bar">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- Tab content -->
        <div class="items-grid">

          <!-- BODY tab -->
          <template v-if="activeTab === 'body'">
            <div
              v-for="item in bodies"
              :key="item.id"
              class="item-card"
              :class="{ selected: characterStore.selectedBody === item.id }"
              @click="characterStore.selectedBody = item.id"
            >
              <div class="item-preview body-preview">
                <img :src="getAsset('bodies', item.id, '.png')" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

          <!-- HAIR tab -->
          <template v-if="activeTab === 'hair'">
            <!-- None option -->
            <div
              class="item-card"
              :class="{ selected: characterStore.selectedHair === null }"
              @click="characterStore.selectedHair = null"
            >
              <div class="item-preview none-preview">✕</div>
              <span class="item-label">Нет</span>
            </div>
            <div
              v-for="item in hairStyles"
              :key="item.id"
              class="item-card"
              :class="{ selected: characterStore.selectedHair === item.id }"
              @click="characterStore.selectedHair = item.id"
            >
              <div class="item-preview hair-preview">
                <img :src="getAsset('hair', item.id, '.png')" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

          <!-- TOPS tab -->
          <template v-if="activeTab === 'tops'">
            <div
              class="item-card"
              :class="{ selected: characterStore.selectedTop === null }"
              @click="characterStore.selectedTop = null"
            >
              <div class="item-preview none-preview">✕</div>
              <span class="item-label">Нет</span>
            </div>
            <div
              v-for="item in tops"
              :key="item.id"
              class="item-card"
              :class="{ selected: characterStore.selectedTop === item.id }"
              @click="characterStore.selectedTop = item.id"
            >
              <div class="item-preview">
                <img :src="getTopAsset(item.id)" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

          <!-- BOTTOMS tab -->
          <template v-if="activeTab === 'bottoms'">
            <div
              class="item-card"
              :class="{ selected: characterStore.selectedBottom === null }"
              @click="characterStore.selectedBottom = null"
            >
              <div class="item-preview none-preview">✕</div>
              <span class="item-label">Нет</span>
            </div>
            <div
              v-for="item in bottoms"
              :key="item.id"
              class="item-card"
              :class="{ selected: characterStore.selectedBottom === item.id }"
              @click="characterStore.selectedBottom = item.id"
            >
              <div class="item-preview">
                <img :src="getBottomAsset(item.id)" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

          <!-- ACCESSORIES tab -->
          <template v-if="activeTab === 'accessories'">
            <div
              class="item-card"
              :class="{ selected: characterStore.selectedAccessory === null }"
              @click="characterStore.selectedAccessory = null"
            >
              <div class="item-preview none-preview">✕</div>
              <span class="item-label">Нет</span>
            </div>
            <div
              v-for="item in accessories"
              :key="item.id"
              class="item-card"
              :class="{ selected: characterStore.selectedAccessory === item.id }"
              @click="characterStore.selectedAccessory = item.id"
            >
              <div class="item-preview">
                <img :src="getAsset('accessories', item.id, '.png')" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

          <!-- BACKGROUNDS tab -->
          <template v-if="activeTab === 'background'">
            <div
              v-for="item in backgrounds"
              :key="item.id"
              class="item-card wide-card"
              :class="{ selected: characterStore.selectedBackground === item.id }"
              @click="characterStore.selectedBackground = item.id"
            >
              <div class="item-preview bg-preview">
                <img :src="getAsset('backgrounds', item.id, '.png')" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

          <!-- PETS tab -->
          <template v-if="activeTab === 'pets'">
            <div
              class="item-card"
              :class="{ selected: characterStore.selectedPet === null }"
              @click="characterStore.selectedPet = null"
            >
              <div class="item-preview none-preview">✕</div>
              <span class="item-label">Нет</span>
            </div>
            <div
              v-for="item in pets"
              :key="item.id"
              class="item-card"
              :class="{ selected: characterStore.selectedPet === item.id }"
              @click="characterStore.selectedPet = item.id"
            >
              <div class="item-preview">
                <img :src="getAsset('pet', item.id, '.png')" :alt="item.label" />
              </div>
              <span class="item-label">{{ item.label }}</span>
            </div>
          </template>

        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { useCharacterStore } from '@/stores/character'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'CharacterPage',
  setup() {
    const characterStore = useCharacterStore()
    const authStore = useAuthStore()
    return { characterStore, authStore }
  },
  data() {
    return {
      activeTab: 'body',
      justSaved: false,
      tabs: [
        { id: 'body',        icon: '🧍', label: 'Тело' },
        { id: 'hair',        icon: '💇', label: 'Причёска' },
        { id: 'tops',        icon: '👕', label: 'Верх' },
        { id: 'bottoms',     icon: '👖', label: 'Низ' },
        { id: 'accessories', icon: '🎩', label: 'Аксессуары' },
        { id: 'background',  icon: '🏞️', label: 'Фон' },
        { id: 'pets',        icon: '🐾', label: 'Питомец' },
      ],
      bodies: [
        { id: 'body_standard',  label: 'Стандарт' },
        { id: 'body_pale',      label: 'Светлая' },
        { id: 'body_light_tan', label: 'Загар' },
        { id: 'body_brown',     label: 'Коричневая' },
        { id: 'body_white',     label: 'Белая' },
      ],
      hairStyles: Array.from({ length: 36 }, (_, i) => {
        const nums = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]
        const n = nums[i]
        const padded = String(n).padStart(2, '0')
        return { id: `hair_${padded}`, label: `Стиль ${n}` }
      }),
      tops: [
        { id: 'hoodie_pink',           label: 'Худи розовое' },
        { id: 'hoodie_purple',         label: 'Худи фиолет.' },
        { id: 'hoodie_red',            label: 'Худи красное' },
        { id: 'hoodie_white',          label: 'Худи белое' },
        { id: 'jacket_green',          label: 'Куртка зел.' },
        { id: 'sweater_brown',         label: 'Свитер кор.' },
        { id: 'sweater_green',         label: 'Свитер зел.' },
        { id: 'sweater_striped_blue',  label: 'Полоска синяя' },
        { id: 'sweater_striped_green', label: 'Полоска зел.' },
        { id: 'sweater_striped_red',   label: 'Полоска кр.' },
        { id: 'tshirt_green',          label: 'Футболка зел.' },
        { id: 'tshirt_white',          label: 'Футболка бел.' },
      ],
      bottoms: [
        { id: 'pants_brown',       label: 'Брюки кор.' },
        { id: 'pants_pink_wide',   label: 'Брюки розов.' },
        { id: 'pants_plaid_purple',label: 'Брюки клетка' },
        { id: 'shorts_beige',      label: 'Шорты' },
        { id: 'skirt_layered_beige', label: 'Юбка слои' },
        { id: 'skirt_pink',        label: 'Юбка розовая' },
        { id: 'skirt_purple',      label: 'Юбка фиол.' },
        { id: 'skirt_white',       label: 'Юбка белая' },
      ],
      accessories: [
        { id: 'crown_leaves',        label: 'Венок' },
        { id: 'ears_orange',         label: 'Ушки' },
        { id: 'glasses_green_glow',  label: 'Очки зел.' },
        { id: 'glasses_orange_glow', label: 'Очки оранж.' },
        { id: 'hat_bee',             label: 'Шапка пчела' },
        { id: 'hat_feather_red',     label: 'Шляпа перо' },
        { id: 'hat_wizard_blue',     label: 'Шляпа маг' },
        { id: 'hat_wizard_yellow',   label: 'Шляпа желт.' },
      ],
      backgrounds: [
        { id: 'bg_beach',          label: 'Пляж' },
        { id: 'bg_city_purple',    label: 'Город ночь' },
        { id: 'bg_field_sky',      label: 'Поле' },
        { id: 'bg_forest_path',    label: 'Лес' },
        { id: 'bg_hills_village',  label: 'Деревня' },
        { id: 'bg_sky_clouds',     label: 'Облака' },
        { id: 'bg_sunset_powerlines', label: 'Закат' },
      ],
      pets: [
        { id: 'pet_boar',          label: 'Кабан' },
        { id: 'pet_cat',           label: 'Кошка' },
        { id: 'pet_dog_beagle',    label: 'Бигль' },
        { id: 'pet_dog_chihuahua', label: 'Чихуахуа' },
        { id: 'pet_dragon',        label: 'Дракон' },
        { id: 'pet_hamster',       label: 'Хомяк' },
        { id: 'pet_snake',         label: 'Змея' },
        { id: 'pet_water_dragon',  label: 'Водный дракон' },
      ],
    }
  },
  methods: {
    // Стандартный метод для папок первого уровня (тела, волосы, аксессуары, питомцы)
    getAsset(folder, name, ext = '.png') {
      return new URL(`../assets/${folder}/${name}${ext}`, import.meta.url).href
    },
    // Явный метод для верхней одежды
    getTopAsset(name) {
      return new URL(`../assets/clothes/tops/${name}.png`, import.meta.url).href
    },
    // Явный метод для нижней одежды
    getBottomAsset(name) {
      return new URL(`../assets/clothes/bottoms/${name}.png`, import.meta.url).href
    },
    saveCharacter() {
      this.justSaved = true
      setTimeout(() => { this.justSaved = false }, 2000)
    }
  }
}
</script>

<style scoped>
.page-wrapper {
  min-height: calc(100vh - 67px);
  background: linear-gradient(160deg, #f4f0ff 0%, #e8d5ff 40%, #c9a6ff 100%);
  padding: 24px;
}

.char-page {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  min-height: calc(100vh - 115px);
}

/* ── Preview Panel ── */
.preview-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.preview-scene {
  position: relative;
  width: 100%;
  max-width: 300px;
  aspect-ratio: 3/4;
  border-radius: 20px;
  overflow: hidden;
  background: #2e1f5a;
  box-shadow: 0 8px 32px rgba(66,41,116,0.35);
}

.layer {
  position: absolute;
  object-fit: contain;
  image-rendering: pixelated; /* Делает пиксель-арт четким! */
}

/* --- Z-index Stacking --- */
.layer-bg {
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  object-fit: cover;
}

.layer-body {
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
}

/* --- Подгонка размеров и позиций --- */
/* --- Подгонка размеров и позиций --- */
.layer-bottom {
  z-index: 3;
  width: 46%;
  height: auto;
  top: 52%;
  left: 50%;
  transform: translateX(-50%);
}

.layer-top {
  z-index: 4;
  width: 48%;
  height: auto;
  top: 32%;
  left: 50%;
  transform: translateX(-50%);
}

.layer-hair {
  z-index: 5;
  width: 55%;
  height: auto;
  top: 1%;
  left: 54%;
  transform: translateX(-50%);
}

.layer-accessory {
  z-index: 6;
  width: 45%;
  height: auto;
  top: -10%;
  left: 52%;
  transform: translateX(-50%);
}

.layer-item {
  z-index: 7;
  width: 30%;
  height: auto;
  top: 45%;
  left: 10%;
}

.layer-pet {
  z-index: 8;
  width: 35%;
  height: auto;
  bottom: 4%;
  right: 4%;
}

.name-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px 24px;
  text-align: center;
  width: 100%;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(66,41,116,0.12);
}

.name-display {
  font-family: 'Varela Round', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #2a1a5e;
}

.level-badge {
  font-size: 12px;
  color: #7c5cbf;
  margin-top: 2px;
  font-family: 'Varela Round', sans-serif;
}

.save-btn {
  background: #553496;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 12px 32px;
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  max-width: 300px;
}

.save-btn:hover { background: #7c3aed; transform: translateY(-1px); }
.save-btn.saved { background: #38a169; }

/* ── Customizer Panel ── */
.customizer-panel {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-bar {
  display: flex;
  gap: 4px;
  padding: 16px 20px 0;
  border-bottom: 2px solid #f0ebff;
  background: #faf8ff;
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 16px;
  background: none;
  border: none;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  transition: all 0.2s;
  color: #999;
  position: relative;
  bottom: -2px;
  border: 2px solid transparent;
}

.tab-btn:hover { color: #553496; background: #f0ebff; }

.tab-btn.active {
  color: #553496;
  background: #fff;
  border-color: #f0ebff #f0ebff #fff;
  font-weight: 700;
}

.tab-icon { font-size: 20px; }
.tab-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

/* Items grid */
.items-grid {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  align-content: start;
}

.items-grid::-webkit-scrollbar { width: 6px; }
.items-grid::-webkit-scrollbar-track { background: #f8f4ff; border-radius: 4px; }
.items-grid::-webkit-scrollbar-thumb { background: #c4aeff; border-radius: 4px; }

.item-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px;
  border-radius: 14px;
  border: 2px solid #f0ebff;
  cursor: pointer;
  transition: all 0.2s;
  background: #faf8ff;
}

.item-card:hover { border-color: #9864ff; transform: translateY(-2px); }
.item-card.selected { border-color: #553496; background: #f0ebff; }

.item-preview {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  overflow: hidden;
  background: #e8deff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.none-preview {
  font-size: 24px;
  color: #ccc;
  background: #f5f5f5;
}

.bg-preview {
  width: 100%;
  height: 70px;
  border-radius: 8px;
}

.bg-preview img { width: 100%; height: 100%; object-fit: cover; }

.wide-card {
  grid-column: span 1;
}

.item-label {
  font-family: 'Varela Round', sans-serif;
  font-size: 10px;
  text-align: center;
  color: #5a4a7a;
  font-weight: 600;
}

@media (max-width: 900px) {
  .char-page {
    grid-template-columns: 1fr;
  }
  .preview-scene { max-width: 220px; }
}
</style>