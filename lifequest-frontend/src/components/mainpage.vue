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

    <div class="main-block">
      <div class="main-header">
        <img 
          :src="headerImage" 
          :alt="headerTitle"
          class="header-image"
          @error="handleImageError"
        >
      </div>

      <div class="columns-container">
        <div class="column left-column">
          <div class="column-header">
            <div class="tabs-container">
              <button 
                v-for="tab in leftTabs" 
                :key="tab.id"
                class="tab-button"
                :class="{ active: activeLeftTab === tab.id }"
                @click="activeLeftTab = tab.id"
              >
                {{ tab.name }}
              </button>
            </div>
            <button class="header-button" @click="handleHeaderButtonClick">
              <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/plus.svg" alt="Groups">
            </button>
          </div>

          <button class="primary-button" @click="handlePrimaryAction">
            <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/refresh.svg" alt="Add">
            Add New
          </button>

          <div v-for="(item, index) in leftColumnItems" :key="item.id" class="checkbox-block">
            <div class="checkbox-container">
              <input 
                type="checkbox" 
                :id="`left-item-${item.id}`"
                v-model="item.checked"
                @change="handleCheckboxChange(item)"
                class="custom-checkbox"
              >
              <label :for="`left-item-${item.id}`" class="checkbox-label">
                <span class="checkbox-text">{{ item.text }}</span>
                  <span class="exp-number">
                    <div class="star-corner">
                      <svg class="star-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" />
                      </svg>
                    </div>
                    
                    <div class="number-display">
                      <span class="small-number">{{ item.number }}</span>
                    </div>
                  </span>
              </label>
            </div>
          </div>
        </div>

        <div class="column right-column">
          <div class="column-header-right"></div>
          <button class="action-button" @click="handleRightColumnAction">
            <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/arrow-path.svg" alt="Add">
            Add New
          </button>

          <div v-for="(item, index) in rightColumnItems" :key="item.id" class="detailed-block">
            <div class="block-header">
              <input 
                type="checkbox" 
                :id="`right-item-${item.id}`"
                v-model="item.checked"
                @change="handleCheckboxChange(item)"
                class="custom-checkbox"
              >
              <label :for="`right-item-${item.id}`" class="block-title">
                {{ item.title }}
              </label>
            </div>

            <div class="counter-container">
              <img 
                :src="item.counterIcon" 
                alt="Counter"
                class="counter-icon"
              >
              <span class="counter-value">{{ item.counterValue }}</span>
              <span class="counter-label">{{ item.counterLabel }}</span>
            </div>

            <div class="items-list">
              <div 
                v-for="(subItem, subIndex) in item.items" 
                :key="subIndex"
                class="list-item"
                :class="{ completed: subItem.completed }"
              >
                <div class="list-item-content">
                  <span class="list-item-bullet">•</span>
                  <span class="list-item-text">{{ subItem.text }}</span>
                </div>
                <button 
                  v-if="subItem.actionable" 
                  class="list-item-button"
                  @click="handleSubItemAction(item, subItem)"
                >
                  Complete
                </button>
              </div>
            <span class="exp-number">
                    <div class="star-corner">
                      <svg class="star-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" />
                      </svg>
                    </div>
                    
                    <div class="number-display">
                      <span class="small-number">{{ item.ExpCounter }}</span>
                    </div>
                  </span>
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
  name: 'ProfileSite',
  
  data() {
    return {
      profileImage: '\LifeQuest\src\components\tasks.png',
      profileName: 'Lorem Ipsum',
      userLevel: 5,
      currentXP: 3450,
      nextLevelXP: 5000,
      
      headerImage: 'LifeQuest\src\components\tasks.png',
      headerTitle: 'Task Dashboard',
      headerSubtitle: 'Tasks',
      
      props: {
        number: {
          type: [Number, String],
          default: 1
        }
      },

      leftTabs: [
        { id: 'all', name: 'All Tasks' },
        { id: 'pending', name: 'Pending' },
        { id: 'completed', name: 'Completed' }
      ],
      activeLeftTab: 'all',
      
      leftColumnItems: [
        { id: 1, text: 'Wake up at 6 am', number: 3, checked: false, status: 'pending', category: 'morning' },
        { id: 2, text: 'Learn English', number: 5, checked: false, status: 'pending', category: 'education' },
        { id: 3, text: 'Do homework for 2-3 hours', number: 2, checked: false, status: 'pending', category: 'education' },
        { id: 4, text: 'Gym', number: 1, checked: false, status: 'pending', category: 'training' },
        { id: 5, text: 'Stretch in the morning', number: 4, checked: true, status: 'completed', category: 'morning' }
      ],
      
      rightColumnItems: [
        {
          id: 1,
          title: 'Make Posts',
          checked: false,
          counterIcon: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/code-bracket.svg',
          counterValue: 3,
          ExpCounter: 5,
          counterLabel: 'active tasks',
          items: [
            { text: 'Text', completed: true, actionable: false },
            { text: 'Image', completed: false, actionable: true },
            { text: 'Get approval', completed: false, actionable: true },
            { text: 'Put into "Later"', completed: false, actionable: true }
          ]
        },
      ]
    }
  },
  
  computed: {
    xpPercentage() {
      return Math.min(100, (this.currentXP / this.nextLevelXP) * 100)
    }
  },
  
  methods: {
    handleImageError(e) {
      e.target.src = 'https://via.placeholder.com/150x150?text=Image'
    },
    
    handleImageError(e) {
      e.target.src = 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/photo.svg'
    },
    
    handleHeaderButtonClick() {
      console.log('Header button clicked')
      this.$emit('add-new-click')
      alert('Add new task dialog would open here')
    },
    
    handlePrimaryAction() {
      console.log('Primary action button clicked')
      this.$emit('refresh-tasks')
      alert('Refreshing tasks...')
    },
    
    handleRightColumnAction() {
      console.log('Right column action button clicked')
      this.$emit('sync-data')
      alert('Syncing data...')
    },
    
    handleCheckboxChange(item) {
      console.log('Checkbox changed:', item)
      this.$emit('checkbox-change', item)
      
      if (this.leftColumnItems.includes(item)) {
        item.status = item.checked ? 'completed' : 'pending'
      }
    },
    
    handleSubItemAction(parentItem, subItem) {
      console.log('Sub-item action:', parentItem.title, subItem.text)
      subItem.completed = true
      this.$emit('sub-item-complete', { parentItem, subItem })
      
      const activeItems = parentItem.items.filter(i => !i.completed).length
      parentItem.counterValue = activeItems
      
      alert(`Completed: ${subItem.text}`)
    },
    
    getProgressStats() {
      const total = this.leftColumnItems.length
      const completed = this.leftColumnItems.filter(i => i.checked).length
      return { total, completed, percentage: (completed / total) * 100 }
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

.xp-bar-container {
  background: #F9F9FA
}

.xp-bar {
  background: #422974;
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

.main-block {
  background: #EDECEE;
}

.main-header {
  color: #F9F9FA;
}

.tab-button {
  color: #8A8A8A;
}

.tab-button:hover {
  background: #D9D9D9;
}

.tab-button.active {
  color: #F9F9FA;
}

.header-button {
  color: #F9F9FA;
  background: #E1DFE2;
}

.primary-button {
  color: #131313;
  background: #E1DFE2;
}

.checkbox-block {
  background: #F9F9FA;
}

.checkbox-block:hover {
  background: #F9F9FA;
}

.checkbox-text {
  color: #131313;
}

.exp-number {
  color: #131313;
}

.action-button {
  color: #131313;
  background: #E1DFE2;
}

.detailed-block {
  background: #F9F9FA;
}

.detailed-block:hover {
  background: #F9F9FA;
}

.block-title {
  color: #131313;
}

.counter-container {
  background: #F9F9FA;
}

.counter-label {
  color: #131313;
}

.bigtask-number {
  color: #131313;
}

.list-item {
  background: #F9F9FA;
}

.list-item:hover {
  background: #F9F9FA;
}

.list-item-text {
  color: #131313;
}

.list-item-count {
  background: #F9F9FA;
}

.list-item-button {
  color: #F9F9FA;
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

.xp-bar {
  background: #9864FF;
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

.xp-label {
  color: #F9F9FA;
}

.xp-details {
  color: #F9F9FA;
}

.main-block {
  background: #1F1D20;
}

.main-header {
  color: #F9F9FA;
}

.tab-button {
  color: #8A8A8A;
}

.tab-button:hover {
  background: #2C292D;
}

.tab-button.active {
  color: #F9F9FA;
}

.header-button {
  color: #F9F9FA;
}

.primary-button {
  color: #F9F9FA;
  background: #2C292D;
}

.checkbox-block {
  background: #0D0D0D;
}

.checkbox-block:hover {
  background: #0D0D0D;
}

.checkbox-text {
  color: #F9F9FA;
}

.exp-number {
  color: #F9F9FA;
}

.action-button {
  color: #F9F9FA;
  background: #2C292D;
}

.detailed-block {
  background: #0D0D0D;
}

.detailed-block:hover {
  background: #0D0D0D;
}

.block-title {
  color: #F9F9FA;
}

.counter-container {
  background: #0D0D0D;
}

.counter-label {
  color: #F9F9FA;
}

.bigtask-number {
  color: #0D0D0D;
}

.list-item {
  background: #0D0D0D;
}

.list-item:hover {
  background: #333333;
}

.list-item-text {
  color: #F9F9FA;
}

.list-item-count {
  background: #0D0D0D;
}

.list-item-button {
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


.main-block {
  border-radius: 20px;
  width: 312%;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.main-header {
  background: #422974;
  padding: 2rem;
  text-align: center;
}

.header-image {
  width: 60px;
  height: 60px;
  filter: brightness(0) invert(1);
  margin-bottom: 1rem;
}

.header-title {
  font-size: 2rem;
  margin: 0 0 0.5rem;
}

.header-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.columns-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2rem;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 2px solid #422974;
}

.tabs-container {
  display: flex;
  gap: 0.5rem;
}

.tab-button {
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button.active {
  background: #422974;
}

.header-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #9864FF;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.header-button:hover {
  background: #693BC7;
  transform: translateY(-2px);
}

.header-button img {
  width: 16px;
  height: 16px;
  filter: brightness(0) invert(1);
}

.primary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 41, 116, 0.3);
}

.primary-button img {
  width: 18px;
  height: 18px;
  filter: brightness(0) invert(1);
}

.checkbox-block {
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s ease;
}

.checkbox-block:hover {
  transform: translateX(5px);
}

.checkbox-container {
  display: flex;
  align-items: flex-start;
}

.custom-checkbox {
  margin-right: 1rem;
  margin-top: 2px;
  cursor: pointer;
  width: 18px;
  height: 18px;
}

.checkbox-label {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.checkbox-text {
  font-size: 0.95rem;
  flex: 1;
}

.exp-number {
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  min-width: 24px;
  text-align: center;
}

.star-corner {
  position: relative;
  top: 26px;
  right: 15px;
}

.star-icon {
  width: 24px;
  height: 24px;
  color: #422974;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.number-display {
  bottom: 12px;
  left: 10px;
}

.small-number {
  font-size: 1rem;
  font-weight: bold;
  opacity: 0.8;
}

.column-header-right {
  min-height: 32px;
  padding-bottom: 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 2px solid #422974;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 41, 116, 0.3);
}

.action-button img {
  width: 18px;
  height: 18px;
  filter: brightness(0) invert(1);
}

.detailed-block {
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
}

.detailed-block:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.block-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.block-header .custom-checkbox {
  margin-right: 0.75rem;
}

.block-title {
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
}

.counter-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.counter-icon {
  width: 20px;
  height: 20px;
}

.counter-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: #422974
}

.counter-label {
  font-size: 0.8rem;
}

.bigtask-number {
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  min-width: 24px;
  text-align: right;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.list-item.completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.list-item-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.list-item-bullet {
  color: #422974;
  font-weight: bold;
}

.list-item-text {
  font-size: 0.85rem;
}

.list-item-count {
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  color: #422974;
  font-weight: bold;
}

.list-item-button {
  padding: 0.25rem 0.75rem;
  background: #422974;
  border: none;
  border-radius: 6px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.list-item-button:hover {
  background: #422974;
  transform: scale(1.05);
}

@media (max-width: 1024px) {
  .columns-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .column-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .tabs-container {
    justify-content: center;
  }
  
  .header-button {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .site-container {
    padding: 1rem;
  }
  
  .columns-container {
    padding: 1rem;
  }
  
  .checkbox-label {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .list-item {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .list-item-button {
    align-self: flex-end;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
}
</style>