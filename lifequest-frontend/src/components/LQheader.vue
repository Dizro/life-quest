<template>
  <header class="site-header">
    <div class="header-container">
      <div class="site-label">
        <router-link to="/" class="site-link">
          <span class="site-name">LifeQuest</span>
        </router-link>
      </div>

      <nav class="nav-links">
        <router-link 
          v-for="link in navLinks" 
          :key="link.path"
          :to="link.path"
          class="nav-link"
          active-class="active-link"
          exact-active-class="exact-active-link"
        >
          {{ link.name }}
        </router-link>
      </nav>

      <div class="right-section">
         <div class="currency-wrapper" @click="handleCurrency1Click">
          <div class="currency-container">
            <img 
              src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/star.svg" 
              alt="Gems"
              class="currency-icon"
              @error="handleImageError"
            >
            <span class="currency-amount">{{ formatCurrency(currency1Amount) }}</span>
            <span class="currency-label">{{ currency1Label }}</span>
          </div>
        </div>

        <div class="currency-wrapper" @click="handleCurrency2Click">
          <div class="currency-container">
            <img 
              src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/currency-dollar.svg" 
              alt="Coins"
              class="currency-icon"
              @error="handleImageError"
            >
            <span class="currency-amount">{{ formatCurrency(currency2Amount) }}</span>
            <span class="currency-label">{{ currency2Label }}</span>
          </div>
        </div>

        <div class="icon-wrapper" @click="handleNotificationClick">
          <div class="icon-container">
            <img 
              src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/bell.svg" 
              alt="Notifications"
              class="icon-image"
              @error="handleImageError">
            <span v-if="notificationCount > 0" class="icon-counter">
              {{ notificationCount > 99 ? '99+' : notificationCount }}
            </span>
          </div>
        </div>

        <div class="icon-wrapper" @click="handleImage2Click">
          <img 
            src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/user.svg" 
            alt="Profile"
            class="icon-image"
            @error="handleImageError">
        </div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'SiteHeader',
  
  data() {
    return {
      navLinks: [
        { name: 'Main', path: '/mainpage' },
        { name: 'Profile', path: '/profile' },
        { name: 'Shop', path: '/shop' },
        { name: 'Achivements', path: '/achivements' },
        { name: 'Groups', path: '/groups' },
        { name: 'Statistics', path: '/statistics' },
        { name: 'Character', path: '/character' },
      ],
      currency1Amount: 125,
      currency1Label: 'Gems',
      currency2Amount: 34,
      currency2Label: 'Coins',
      image1Src: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/bell.svg',
      image1Alt: 'Notifications',
      image2Src: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/user-circle.svg',
      image2Alt: 'Profile'
    }
  },
  
  methods: {
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US').format(amount)
    },
    
    handleImageError(e) {
      e.target.src = 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/circle-stack.svg'
    },
    
    handleCurrency1Click() {
      this.$emit('currency1-click', { 
        amount: this.currency1Amount, 
        label: this.currency1Label 
      })
      console.log(`${this.currency1Label} clicked:`, this.currency1Amount)
    },
    
    handleCurrency2Click() {
      this.$emit('currency2-click', { 
        amount: this.currency2Amount, 
        label: this.currency2Label 
      })
      console.log(`${this.currency2Label} clicked:`, this.currency2Amount)
    },
    
    handleImage1Click() {
      this.$emit('image1-click')
      console.log('Image 1 clicked')
    },
    
    handleImage2Click() {
      this.$emit('image2-click')
      console.log('Image 2 clicked')
    },
    
    updateCurrency(currency, amount) {
      if (currency === 'coins') {
        this.currency1Amount = amount
      } else if (currency === 'gems') {
        this.currency2Amount = amount
      }
    },
    
    addToCurrency(currency, amount) {
      if (currency === 'coins') {
        this.currency1Amount += amount
      } else if (currency === 'gems') {
        this.currency2Amount += amount
      }
    },
    
    subtractFromCurrency(currency, amount) {
      if (currency === 'coins') {
        this.currency1Amount = Math.max(0, this.currency1Amount - amount)
      } else if (currency === 'gems') {
        this.currency2Amount = Math.max(0, this.currency2Amount - amount)
      }
    },
    
    updateImage(imageNumber, src, alt) {
      if (imageNumber === 1) {
        this.image1Src = src
        if (alt) this.image1Alt = alt
      } else if (imageNumber === 2) {
        this.image2Src = src
        if (alt) this.image2Alt = alt
      }
    }
  }
}
</script>

<style scoped>
.site-header {
  background-color: #422974;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
}

@media (prefers-color-scheme: light) {
  .site-name {
    background: #F9F9FA;
  }
  .nav-link {
      color: #F9F9FA;
  }
  .nav-link:hover {
  color: #F9F9FA;
  background: #947ACC;
  }
  .nav-link.active-link {
  color: #F9F9FA;
  background: #947ACC;
}
}

@media (prefers-color-scheme: dark) {
  .site-header {
    background-color: #4C3087;
  }
  .site-name {
    background: #000000;
  }
  .nav-link {
      color: #000000;
  }
  .nav-link:hover {
  color: #F9F9FA;
  background: #311F57;
  }
  .nav-link.active-link {
  color: #F9F9FA;
  background: #311F57;
}
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.site-label {
  flex-shrink: 0;
}

.site-link {
  text-decoration: none;
}

.site-name {
  font-size: 1.5rem;
  font-weight: bold;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: opacity 0.3s ease;
}

.site-link:hover .site-name {
  opacity: 0.8;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex: 1;
  justify-content: center;
}

.nav-link {
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  font-size: 0.95rem;
  white-space: nowrap;
}

.nav-link.active-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: #F9F9FA;
  border-radius: 2px;
}

.right-section {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-shrink: 0;
}


.currency-wrapper {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.currency-wrapper:hover {
  transform: scale(1.05);
}

.currency-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #F9F9FA;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.currency-wrapper:hover .currency-container {
  background: #F9F9FA;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.currency-icon {
  width: 20px;
  height: 20px;
}

.currency-amount {
  font-weight: bold;
  font-size: 0.9rem;
  color: #000000;
}

.currency-label {
  font-size: 0.8rem;
  color: #000000;
  margin-left: 0.25rem;
}


.image-wrapper {
  cursor: pointer;
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
}

.image-wrapper:hover {
  transform: scale(1.05);
}

.right-image {
  width: 24px;
  height: 24px;
  display: block;
  transition: opacity 0.2s ease;
}

.image-wrapper:hover .right-image {
  opacity: 0.8;
}

@keyframes currencyPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.currency-updated {
  animation: currencyPulse 0.3s ease;
}


.image-wrapper {
  position: relative;
}

.image-wrapper::before {
  content: attr(data-tooltip);
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #2d3748;
  color: #4C3087;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 1000;
}

.image-wrapper:hover::before {
  opacity: 1;
  visibility: visible;
  bottom: -35px;
}

.image-wrapper:nth-child(3):before {
  content: "Notifications";
}

.image-wrapper:nth-child(4):before {
  content: "Profile";
}
</style>