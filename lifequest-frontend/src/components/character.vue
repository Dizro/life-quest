<template>
  <div class="page-container">
    <div class="two-column-layout">
      <div class="left-block">
        <div class="featured-image-container">
          <img 
            :src="featuredImage.src" 
            :alt="featuredImage.alt"
            class="featured-image"
            @error="handleImageError"
          >
          <div class="name-block">
          <div class="image-label">{{ featuredImage.label }}</div>
          <div class="image-sublabel">
            {{ featuredImage.sublabel }}
          </div>
        </div>
        </div>
      </div>

      <div class="right-block">
        <div class="tab-headers">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            class="tab-button"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <div class="tab-icon-wrapper">
              <img 
                :src="tab.icon" 
                :alt="tab.label"
                class="tab-icon"
                @error="handleImageError"
              >
            </div>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <div class="tab-content">
          <transition name="fade" mode="out-in">
            <div :key="activeTab" class="images-grid">
              <div 
                v-for="(image, index) in currentTabImages" 
                :key="index"
                class="image-card"
                @click="handleImageClick(image)"
              >
                <div class="image-wrapper">
                  <img 
                    :src="image.src" 
                    :alt="image.title"
                    loading="lazy"
                    @error="handleImageError"
                  >
                  <div class="image-overlay">
                    <div class="overlay-content">
                      <span class="image-title">{{ image.title }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <div v-if="selectedImage" class="image-modal" @click.self="closeModal">
      <div class="modal-content">
        <button class="modal-close" @click="closeModal">&times;</button>
        <img :src="selectedImage.src" :alt="selectedImage.title">
        <div class="modal-info">
          <h3>{{ selectedImage.title }}</h3>
          <p>{{ selectedImage.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TabbedGalleryPage',
  
  data() {
    return {
      activeTab: 'body',
      selectedImage: null,
      
      featuredImage: {
        src: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80',
        alt: 'Character',
        label: 'Name',
        sublabel: 'Nickname'
      },
      
      // Tab Definitions with Images and Labels
      tabs: [
        {
          id: 'body',
          label: 'Body',
          icon: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/leaf.svg'
        },
        {
          id: 'skin',
          label: 'Skin',
          icon: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/building-office.svg'
        },
        {
          id: 'hair',
          label: 'Hair',
          icon: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/user-group.svg'
        },
        {
          id: 'extra',
          label: 'Extra',
          icon: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/paw.svg'
        },
        {
          id: 'background',
          label: 'Background',
          icon: 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/paint-brush.svg'
        }
      ],
      
      tabImages: {
        body: [
          { src: 'https://picsum.photos/id/1015/300/250', title: 'Mountain Majesty', description: 'Breathtaking mountain landscape with snow-capped peaks' },
          { src: 'https://picsum.photos/id/104/300/250', title: 'Forest Serenity', description: 'Peaceful forest path through ancient trees' },
          { src: 'https://picsum.photos/id/106/300/250', title: 'Garden Bloom', description: 'Vibrant flowers in full spring bloom' },
          { src: 'https://picsum.photos/id/15/300/250', title: 'Woodland Trail', description: 'Mysterious forest trail leading to adventure' },
          { src: 'https://picsum.photos/id/29/300/250', title: 'Ocean Sunset', description: 'Stunning sunset over the calm ocean' },
          { src: 'https://picsum.photos/id/48/300/250', title: 'Lake Retreat', description: 'Peaceful lake house surrounded by nature' },
          { src: 'https://picsum.photos/id/60/300/250', title: 'Waterfall Cascade', description: 'Powerful waterfall in lush forest' },
          { src: 'https://picsum.photos/id/66/300/250', title: 'River Flow', description: 'Gentle river flowing through valley' }
        ],
        skin: [
          { src: 'https://picsum.photos/id/26/300/250', title: 'City Skyline', description: 'Modern city skyline at dusk' },
          { src: 'https://picsum.photos/id/91/300/250', title: 'Night Lights', description: 'City lights illuminating the night' },
          { src: 'https://picsum.photos/id/96/300/250', title: 'Skyscrapers', description: 'Towering skyscrapers reaching the clouds' },
          { src: 'https://picsum.photos/id/82/300/250', title: 'Street Life', description: 'Busy city street with vibrant energy' },
          { src: 'https://picsum.photos/id/39/300/250', title: 'Modern Architecture', description: 'Contemporary building design' },
          { src: 'https://picsum.photos/id/44/300/250', title: 'Bridge Crossing', description: 'Iconic bridge over river' },
          { src: 'https://picsum.photos/id/58/300/250', title: 'Historic District', description: 'Old town with historic architecture' },
          { src: 'https://picsum.photos/id/70/300/250', title: 'Observation Tower', description: 'Tall tower with panoramic views' }
        ],
        hair: [
          { src: 'https://randomuser.me/api/portraits/men/32.jpg', title: 'Professional', description: 'Confident professional in modern office' },
          { src: 'https://randomuser.me/api/portraits/women/68.jpg', title: 'Creative Artist', description: 'Artist working in her studio' },
          { src: 'https://randomuser.me/api/portraits/men/45.jpg', title: 'Thinker', description: 'Deep in thoughtful contemplation' },
          { src: 'https://randomuser.me/api/portraits/women/33.jpg', title: 'Leader', description: 'Inspiring leader addressing team' },
          { src: 'https://randomuser.me/api/portraits/men/22.jpg', title: 'Adventurer', description: 'Explorer in natural environment' },
          { src: 'https://randomuser.me/api/portraits/women/44.jpg', title: 'Teacher', description: 'Educator sharing knowledge' },
          { src: 'https://randomuser.me/api/portraits/men/86.jpg', title: 'Musician', description: 'Performing with passion' },
          { src: 'https://randomuser.me/api/portraits/women/55.jpg', title: 'Wellness Coach', description: 'Leading meditation session' }
        ],
        extra: [
          { src: 'https://picsum.photos/id/200/300/250', title: 'Majestic Lion', description: 'King of the savanna in golden light' },
          { src: 'https://picsum.photos/id/219/300/250', title: 'Curious Cat', description: 'Playful feline exploring' },
          { src: 'https://picsum.photos/id/237/300/250', title: 'Loyal Dog', description: 'Faithful companion in nature' },
          { src: 'https://picsum.photos/id/180/300/250', title: 'Colorful Bird', description: 'Exotic bird in tropical forest' },
          { src: 'https://picsum.photos/id/130/300/250', title: 'Gentle Rabbit', description: 'Soft rabbit in meadow' },
          { src: 'https://picsum.photos/id/300/300/250', title: 'Wild Tiger', description: 'Powerful tiger in jungle' },
          { src: 'https://picsum.photos/id/400/300/250', title: 'Elephant Herd', description: 'Family of elephants crossing plain' },
          { src: 'https://picsum.photos/id/500/300/250', title: 'Dolphin Pod', description: 'Playful dolphins in ocean' }
        ],
        background: [
          { src: 'https://picsum.photos/id/1/300/250', title: 'Abstract Vision', description: 'Bold colors and abstract forms' },
          { src: 'https://picsum.photos/id/2/300/250', title: 'Digital Dreams', description: 'Modern digital art creation' },
          { src: 'https://picsum.photos/id/3/300/250', title: 'Pixel Perfect', description: 'Detailed pixel art masterpiece' },
          { src: 'https://picsum.photos/id/4/300/250', title: 'Oil Painting', description: 'Classic oil painting technique' },
          { src: 'https://picsum.photos/id/5/300/250', title: 'Pencil Sketch', description: 'Detailed pencil drawing' },
          { src: 'https://picsum.photos/id/6/300/250', title: 'Watercolor', description: 'Soft watercolor landscape' },
          { src: 'https://picsum.photos/id/7/300/250', title: 'Sculpture', description: 'Modern sculpture installation' },
          { src: 'https://picsum.photos/id/8/300/250', title: 'Street Art', description: 'Vibrant urban mural' }
        ]
      }
    }
  },
  
  computed: {
    currentTabImages() {
      return this.tabImages[this.activeTab] || []
    }
  },
  
  methods: {
    handleImageError(e) {
      e.target.src = 'https://via.placeholder.com/300x250?text=Image+Not+Found'
    },
    
    handleImageClick(image) {
      this.selectedImage = image
      this.$emit('image-clicked', image)
    },
    
    closeModal() {
      this.selectedImage = null
    }
  }
}
</script>

<style scoped>
.page-container {
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}


@media (prefers-color-scheme: light){
.page-container {
  background: linear-gradient( #F9F9FA, #422974);
}

.name-block {
  background: #F9F9FA;
}

.image-label {
  color: #000000;
}

.image-sublabel {
  color: #131313;
}

.right-block {
  background: #F9F9FA;
}

.tab-button:hover {
  background: #DAD9DB;
}

.tab-label {
  color: #131313;
}

.tab-button.active .tab-label {
  color: #F9F9FA;
}

.image-wrapper {
  background: #F9F9FA;
}

.overlay-content {
  color: #F9F9FA;
}

.modal-content {
  background: #F9F9FA;
}

.modal-close {
  color: #F9F9FA;
}

.modal-info h3 {
  color: #131313;
}

.modal-info p {
  color: #131313;
}

}


@media (prefers-color-scheme: dark){
.page-container {
  background: linear-gradient( #131313, #4C3087);
}

.name-block {
  background: #0D0D0D;
}

.image-label {
  color: #F9F9FA;
}

.image-sublabel {
  color: #F9F9FA;
}

.right-block {
  background: #0D0D0D;
}

.tab-button:hover {
  background: #1F1D20;
}

.tab-label {
  color: #F9F9FA;
}

.tab-button.active .tab-label {
  color: #F9F9FA;
}

.image-wrapper {
  background: #1F1D20;
}

.overlay-content {
  color: #F9F9FA;
}

.modal-content {
  background: #333333;
}

.modal-close {
  color: #131313;
}

.modal-info h3 {
  color: #F9F9FA;
}

.modal-info p {
  color: #F9F9FA;
}

}





.two-column-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-radius: 24px;
}


.left-block {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 500px;
}

.featured-image-container {
  text-align: center;
  width: 100%;
}

.featured-image {
  width: 100%;
  max-width: 260px;
  height: auto;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.featured-image:hover {
  transform: scale(1.02);
}

.name-block {
  border-radius: 20px;
}

.image-label {
  margin-top: 1.5rem;
  font-size: 1.3rem;
  font-weight: 700;
  text-align: center;
  letter-spacing: 1px;
  padding-top: 4px;
}

.image-sublabel {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  text-align: center;
  padding-bottom: 2px;
}

.right-block {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 24px;
}

.tab-headers {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  border-bottom: 2px solid #422974;
  padding-bottom: 0.5rem;
}

.tab-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 16px;
  flex: 1;
  min-width: 80px;
}

.tab-button:hover {
  transform: translateY(-2px);
}

.tab-button.active {
  background: #553496;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.tab-icon-wrapper {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.tab-button.active .tab-icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
}

.tab-icon {
  width: 24px;
  height: 24px;
  transition: transform 0.3s ease;
}

.tab-button:hover .tab-icon {
  transform: scale(1.1);
}

.tab-button.active .tab-icon {
  filter: brightness(0) invert(1);
}

.tab-label {
  font-size: 0.8rem;
  font-weight: 600;
  transition: color 0.3s ease;
}

.tab-content {
  flex: 1;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.tab-content::-webkit-scrollbar {
  width: 6px;
}

.tab-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.tab-content::-webkit-scrollbar-thumb {
  background: #553496;
  border-radius: 10px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}

.image-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-card:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.image-overlay {
  background: rgba(85, 52, 150, 0.8);
}

.image-wrapper img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.image-card:hover .image-wrapper img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.overlay-content {
  text-align: center;
  padding: 1rem;
}

.image-title {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.view-icon {
  font-size: 1.5rem;
  opacity: 0.8;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 24px;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 20px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  font-size: 2rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.modal-content img {
  max-width: 100%;
  max-height: 70vh;
  width: auto;
  height: auto;
  display: block;
  margin: 0 auto;
}

.modal-info {
  padding: 1.5rem;
}

.modal-info h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
}

.modal-info p {
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .two-column-layout {
    grid-template-columns: 280px 1fr;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }
  
  .two-column-layout {
    grid-template-columns: 1fr;
  }
  
  .left-block {
    padding: 2rem;
    min-height: auto;
  }
  
  .featured-image {
    max-width: 200px;
  }
  
  .right-block {
    padding: 1rem;
  }
  
  .tab-headers {
    gap: 0.5rem;
  }
  
  .tab-button {
    padding: 0.5rem;
    min-width: 65px;
  }
  
  .tab-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .tab-icon {
    width: 20px;
    height: 20px;
  }
  
  .tab-label {
    font-size: 0.7rem;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }
  
  .image-wrapper img {
    height: 160px;
  }
  
  .modal-info h3 {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .images-grid {
    grid-template-columns: 1fr;
  }
  
  .tab-button {
    min-width: 55px;
  }
  
  .tab-label {
    font-size: 0.65rem;
  }
}
</style>