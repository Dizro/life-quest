<template>
  <div class="page-container">
    <div class="blocks">
        <div class="profile-block">
      <div class="profile-image">
        <img 
          :src="profileImage" 
          :alt="profileName"
          @error="handleImageError"
        >
      </div>
      
      <div class="profile-info">
        <h1 class="profile-name">{{ profileName }}</h1>
        <div class="xp-container">
          <div class="xp-header">
            <span class="xp-label">Current Level: {{profileLevel}}</span>
            <span class="xp-value">{{ currentXP }} / {{ nextLevelXP }}</span>
          </div>
          <div class="xp-bar-container">
            <div 
              class="xp-bar" 
              :style="{ width: `${xpPercentage}%` }"
            ></div>
          </div>
          <div class="xp-details">
            <span>{{ xpPercentage }}% to next level</span>
          </div>
        </div>
      </div>
    </div>

    <div class="tabs-section">
      <div class="tab-headers">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          class="tab-button"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <div v-if="activeTab === 'tab1'" class="tab-content">
        <div class="two-column-layout">
          <div class="left-half">
            <label class="section-label">About Me</label>
            <div class="text-block">
              <p>{{ tab1Text }}</p>
            </div>
          </div>
          
          <div class="right-half">
            <button class="action-button" @click="handleButtonClick" :disabled="isLoading">
              {{ isLoading ? 'Processing...' : buttonText }}
            </button>
            <div class="small-text-block">
              <p>Profile created: {{ CreateDate }}</p>
              <p>Log-in counter: {{ LogInCounter }}</p>
              <p>Last Log-in: {{ LastLogIn }}</p>
              <p>Next reward for log-in: {{ NextReward }} days</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'tab2'" class="tab-content">
        <div class="single-column-layout">
          <label class="section-label">Information</label>
          <div class="text-block full-width">
            <p>{{ tab2Text }}</p>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'tab3'" class="tab-content">
        <div class="images-grid">
          <div 
            v-for="(image, index) in squareImages" 
            :key="index"
            class="square-image-container"
            @click="handleImageClick(image)"
          >
            <img 
              :src="image.src" 
              :alt="image.alt"
              class="square-image"
              @error="handleImageError"
            >
            <div class="image-overlay">
              <span>{{ image.title }}</span>
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
  name: 'ProfilePage',
  
  data() {
    return {
      profileImage: '\LifeQuest\src\components\tasks.png',
      profileName: 'Lorem Ipsum',
      profileLevel: '5',
      currentXP: 3450,
      nextLevelXP: 5000,
      
      activeTab: 'tab1',
      tabs: [
        { id: 'tab1', name: 'Profile' },
        { id: 'tab2', name: 'Details' },
        { id: 'tab3', name: 'Achievements' }
      ],
      
      buttonText: 'Change Profile',
      isLoading: false,
      tab1Text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nunc turpis, faucibus id tempus id, tincidunt ut urna. Interdum et malesuada fames ac ante ipsum primis in faucibus. Nullam commodo, nisi eget accumsan volutpat, diam dui venenatis lectus, vel mollis quam mi vitae lorem. Phasellus tempor, est vel pellentesque mollis, ex nisl scelerisque purus, eget consectetur risus tortor vulputate ipsum. Aenean eu metus ac ex consectetur suscipit. Maecenas dictum ipsum bibendum tincidunt euismod.',
      CreateDate: '01.01.2026',
      LogInCounter: '17',
      LastLogIn: '20.03.2026',
      NextReward:'4',
      
      tab2Text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nunc turpis, faucibus id tempus id, tincidunt ut urna. Interdum et malesuada fames ac ante ipsum primis in faucibus. Nullam commodo, nisi eget accumsan volutpat, diam dui venenatis lectus, vel mollis quam mi vitae lorem. Phasellus tempor, est vel pellentesque mollis, ex nisl scelerisque purus, eget consectetur risus tortor vulputate ipsum. Aenean eu metus ac ex consectetur suscipit. Maecenas dictum ipsum bibendum tincidunt euismod.',
      
      squareImages: [
        {
          src: 'https://picsum.photos/id/1015/200/200',
          alt: 'Mountain Landscape',
          title: 'Mountain View'
        },
        {
          src: 'https://picsum.photos/id/104/200/200',
          alt: 'Nature Scene',
          title: 'Beautiful Nature'
        },
        {
          src: 'https://picsum.photos/id/106/200/200',
          alt: 'Flower Garden',
          title: 'Flower Garden'
        },
        {
          src: 'https://picsum.photos/id/15/200/200',
          alt: 'Forest Path',
          title: 'Forest Trail'
        },
        {
          src: 'https://picsum.photos/id/20/200/200',
          alt: 'Coffee Shop',
          title: 'Coffee Time'
        },
        {
          src: 'https://picsum.photos/id/26/200/200',
          alt: 'City Architecture',
          title: 'City View'
        },
        {
          src: 'https://picsum.photos/id/29/200/200',
          alt: 'Beach Sunset',
          title: 'Sunset Beach'
        },
        {
          src: 'https://picsum.photos/id/36/200/200',
          alt: 'City Street',
          title: 'Urban Life'
        },
        {
          src: 'https://picsum.photos/id/42/200/200',
          alt: 'Piano Music',
          title: 'Music Time'
        }
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
    
    handleButtonClick() {
      this.isLoading = true
      
      setTimeout(() => {
        this.addXP(100)
        this.isLoading = false
        this.$emit('action-completed', { message: 'Action completed! +100 XP' })
        
        alert('Action completed! You earned 100 XP!')
      }, 1000)
    },
    
    addXP(amount) {
      let newXP = this.currentXP + amount
      
      if (newXP >= this.nextLevelXP) {
        const overflow = newXP - this.nextLevelXP
        this.userLevel++
        this.currentXP = overflow
        this.nextLevelXP = Math.floor(this.nextLevelXP * 1.2)
        this.$emit('level-up', { newLevel: this.userLevel })
        alert(`🎉 Congratulations! You've reached Level ${this.userLevel}! 🎉`)
      } else {
        this.currentXP = newXP
      }
    },
    
    handleImageClick(image) {
      console.log('Image clicked:', image)
      this.$emit('image-clicked', image)
      alert(`You clicked: ${image.title}`)
    },
    
    switchTab(tabId) {
      this.activeTab = tabId
      this.$emit('tab-changed', tabId)
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

.xp-container {
  background: #F9F9FA;
} 

.xp-label {
  color: #000000;
}

.xp-value {
  color: #422974;
}

.xp-bar-container {
  background: #e0e0e0;
}

.xp-bar {
  background: #422974;
}

.xp-header {
  color: #000000;
}

.xp-details {
  color: #131313;
}

.tabs-section {
  background: #F9F9FA;
}

.tab-headers {
  background: #F9F9FA;
}

.tab-button {
  color: #131313;
}

.section-label {
  color: #131313;
}

.text-block {
  background: #F9F9FA;
  color: #131313;
}

.action-button {
  color: #F9F9FA;
}

.small-text-block {
  background: #F9F9FA;
}

.small-text-block p {
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

.xp-container {
  background: #333333;
} 

.xp-value {
  color: #9864FF;
}

.xp-header {
  color: #000000;
}

.tabs-section {
  background: #1F1D20;
}

.tab-headers {
  background: #1F1D20;
}

.tab-button {
  color: #F9F9FA;
}

.section-label {
  color: #F9F9FA;
}

.text-block {
  background: #0D0D0D;
  color: #F9F9FA;
}

.action-button {
  color: #000000;
}

.small-text-block {
  background: #0D0D0D;
}

.small-text-block p {
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

.profile-image {
  flex-shrink: 0;
}

.profile-image img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border: 4px solid #553496;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 2rem;
  margin: 0 0 1rem 0;
}

.xp-container {
  padding: 1rem;
  border-radius: 12px;
}

.xp-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.xp-label {
  font-weight: 500;
}

.xp-value {
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

.tabs-section {
  border-radius: 20px;
  overflow: hidden;
  width: 312%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.tab-headers {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem 0 2rem;
  border-bottom: 2px solid #422974;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab-button:hover {
  color: #9864FF;
}

.tab-button.active {
  color: #9864FF;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #422974;
}

.tab-content {
  padding: 2rem;
}

.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.left-half,
.right-half {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-label {
  font-size: 1.1rem;
  font-weight: 600;
  display: block;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #422974;
}

.text-block {
  padding: 1.5rem;
  border-radius: 12px;
  line-height: 1.6;
}

.text-block p {
  margin: 0;
}

.full-width {
  width: 100%;
}

.action-button {
  background: #422974;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.action-button:active:not(:disabled) {
  transform: translateY(0);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.small-text-block {
  padding: 1rem;
  border-radius: 10px;
  border-left: 4px solid #553496;
}

.small-text-block p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.single-column-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.square-image-container {
  position: relative;
  aspect-ratio: 1 / 1;
  cursor: pointer;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.square-image-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.square-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.square-image-container:hover .square-image {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 1rem;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.square-image-container:hover .image-overlay {
  transform: translateY(0);
}

.image-overlay span {
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}


@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }
  
  .profile-block {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .two-column-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .tab-headers {
    padding: 1rem 1rem 0 1rem;
  }
  
  .tab-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .tab-content {
    padding: 1.5rem;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  .profile-name {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>