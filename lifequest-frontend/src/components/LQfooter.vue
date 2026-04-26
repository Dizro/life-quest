<template>
  <footer class="site-footer" :style="footerStyle">
    <div class="footer-overlay"></div>
    <div class="footer-container">
      <div class="footer-content">
        <h2 class="footer-name">LifeQuest</h2>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'SiteFooter',
    data() {
    return {
      backgroundImage: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80',
      overlayOpacity: 0.7
    }
  },
  
  computed: {
    footerStyle() {
      return {
        backgroundImage: `url(${this.backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }
    }
  },
  
  methods: {
    updateFooter(name, imageUrl, overlayOpacity = 0.7) {
      if (name) this.footerName = name
      if (imageUrl) this.backgroundImage = imageUrl
      this.overlayOpacity = overlayOpacity
      
      const overlay = this.$el.querySelector('.footer-overlay')
      if (overlay) {
        overlay.style.backgroundColor = `rgba(0, 0, 0, ${this.overlayOpacity})`
      }
    }
  },
  
  mounted() {
    const overlay = this.$el.querySelector('.footer-overlay')
    if (overlay) {
      overlay.style.backgroundColor = `rgba(0, 0, 0, ${this.overlayOpacity})`
    }
  }
}
</script>

<style scoped>
.site-footer {
  position: relative;
  width: 100%;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: auto;
  flex-shrink: 0;
}

.footer-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  transition: background-color 0.3s ease;
}

.footer-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.footer-name {
  font-size: 3rem;
  font-weight: bold;
  margin: 0;
  letter-spacing: 2px;
  animation: fadeInUp 0.6s ease;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

@media (prefers-color-scheme: light){
.footer-name{
 color: #F9F9FA;
}
}

@media (prefers-color-scheme: dark){
.footer-name{
 color: #000000;
}
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

</style>