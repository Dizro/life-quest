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

 <div class="lower-block">
      <h1 class="block-title">{{ blockTitle }}</h1>
       <div class="section">
        <div class="section-header">
          <div class="section-label">{{ section1Label }}</div>

        </div>
        <div class="images-row">
          <div 
            v-for="(image, index) in section1Images" 
            :key="index"
            class="image-card"
            @click="handleImageClick(image)"
          >
            <div class="image-wrapper">
              <img 
                :src="image.src" 
                :alt="image.alt"
                @error="handleImageError"
              >
              <div class="image-overlay">
                <span>{{ image.title }}</span>
              </div>
            </div>
            <p class="image-caption">{{ image.caption }}</p>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <div class="section-label">{{ section2Label }}</div>
        </div>
        <div class="images-row">
          <div 
            v-for="(image, index) in section2Images" 
            :key="index"
            class="image-card"
            @click="handleImageClick(image)"
          >
            <div class="image-wrapper">
              <img 
                :src="image.src" 
                :alt="image.alt"
                @error="handleImageError"
              >
              <div class="image-overlay">
                <span>{{ image.title }}</span>
              </div>
            </div>
            <p class="image-caption">{{ image.caption }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedImage" class="image-modal" @click.self="closeModal">
      <div class="modal-content">
        <button class="modal-close" @click="closeModal">&times;</button>
        <img :src="selectedImage.src" :alt="selectedImage.alt">
        <h3>{{ selectedImage.title }}</h3>
        <p>{{ selectedImage.caption }}</p>
      </div>
    </div>
   </div>
  </div>
</template>

<script>
export default {
 data() {
    return {
      profileImage: '\LifeQuest\src\components\tasks.png',
      profileName: 'Lorem Ipsum',
      userLevel: 5,
      currentXP: 3450,
      nextLevelXP: 5000,
     
      blockTitle: 'Shop',
      
      section1Label: 'Character Customization',
      
      section1Images: [
        {
          src: 'https://picsum.photos/id/1015/300/200',
          alt: 'Mountain Landscape',
          title: 'Mountain View',
          caption: 'Beautiful mountain landscape with stunning views'
        },
        {
          src: 'https://picsum.photos/id/104/300/200',
          alt: 'Nature Scene',
          title: 'Nature\'s Beauty',
          caption: 'Serene natural environment perfect for relaxation'
        },
        {
          src: 'https://picsum.photos/id/106/300/200',
          alt: 'Flower Garden',
          title: 'Flower Garden',
          caption: 'Vibrant flowers in full bloom'
        },
        {
          src: 'https://picsum.photos/id/15/300/200',
          alt: 'Forest Path',
          title: 'Forest Trail',
          caption: 'Mysterious forest path leading to adventure'
        },
        {
          src: 'https://picsum.photos/id/20/300/200',
          alt: 'Coffee Shop',
          title: 'Coffee Time',
          caption: 'Cozy coffee shop atmosphere'
        },
        {
          src: 'https://picsum.photos/id/26/300/200',
          alt: 'City Architecture',
          title: 'Urban Life',
          caption: 'Modern city architecture and design'
        }
      ],
      
      section2Label: 'Pets',
      
      section2Images: [
        {
          src: 'https://picsum.photos/id/29/300/200',
          alt: 'Beach Sunset',
          title: 'Sunset Beach',
          caption: 'Breathtaking sunset over the ocean'
        },
        {
          src: 'https://picsum.photos/id/36/300/200',
          alt: 'City Street',
          title: 'Street View',
          caption: 'Vibrant city street life'
        },
        {
          src: 'https://picsum.photos/id/42/300/200',
          alt: 'Piano Music',
          title: 'Musical Moment',
          caption: 'Elegant piano performance'
        },
        {
          src: 'https://picsum.photos/id/48/300/200',
          alt: 'Lake House',
          title: 'Lake Retreat',
          caption: 'Peaceful lake house getaway'
        },
        {
          src: 'https://picsum.photos/id/55/300/200',
          alt: 'Art Gallery',
          title: 'Art Exhibition',
          caption: 'Contemporary art showcase'
        },
        {
          src: 'https://picsum.photos/id/60/300/200',
          alt: 'Mountain Lake',
          title: 'Alpine Lake',
          caption: 'Crystal clear mountain lake'
        }
      ],
      
      selectedImage: null
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
  background: #F9F9FA;
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

.lower-block {
  background: #EDECEE;
}

.block-title {
  color: #F9F9FA;
}

.section-header {
  background-color: #2E0A0B;
}

.section-label {
  color: #F9F9FA;
}

.image-overlay span {
  color: #F9F9FA;
}

.image-caption {
  color: #131313;
}

.modal-content {
  background: #F9F9FA;
}

.modal-close {
 color: #F9F9FA;
}

.modal-content h3 {
  color: #131313;
}

.modal-content p {
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

.profile-title {
  color: #F9F9FA;
}

.profile-right {
  background: #333333;
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

.xp-bar {
  background: #9864FF;
}

.xp-label {
  color: #F9F9FA;
}

.xp-details {
  color: #F9F9FA;
}

.lower-block {
  background: #1F1D20;
}

.block-title {
  color: #F9F9FA;
}

.section-header {
  background-color: #333333;
}

.section-label {
  color: #F9F9FA;
}

.image-overlay span {
  color: #F9F9FA;
}

.image-caption {
  color: #F9F9FA;
}

.modal-content {
  background: #1F1D20;
}

.modal-close {
 color: #1F1D20;
}

.modal-content h3 {
  color: #F9F9FA;
}

.modal-content p {
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


.lower-block {
  width: 312%;
  border-radius: 20px;
  padding-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.block-title {
  font-size: 2.5rem;
  text-align: center;
  margin: 0 0 0rem;
  position: relative;
  padding-bottom: 1rem;
  background-color: #422974;
  border-radius: 10px;
}

.section {
  padding: 2rem;
  margin-bottom: 3rem;
}

.section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  border-radius: 10px;
  padding: 2px;
}

.section-label {
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  padding-left: 1rem;
}

.images-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
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
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
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
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 1rem;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.image-card:hover .image-overlay {
  transform: translateY(0);
}

.image-overlay span {
  font-size: 0.9rem;
  font-weight: 500;
}

.image-caption {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  text-align: center;
  padding: 0 0.5rem;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  border-radius: 15px;
  padding: 1rem;
  text-align: center;
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
  top: -40px;
  right: 0;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.modal-close:hover {
  transform: scale(1.1);
}

.modal-content img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 10px;
  margin-bottom: 1rem;
}

.modal-content h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
}

.modal-content p {
  margin: 0;
}


@media (max-width: 1024px) {
  .images-row {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }
  
  .top-block {
    grid-template-columns: 1fr;
  }
  
  .top-block-image {
    max-height: 300px;
  }
  
  .top-block-content {
    padding: 1.5rem;
  }
  
  .top-block-content h2 {
    font-size: 1.5rem;
  }
  
  .lower-block {
    padding: 1.5rem;
  }
  
  .block-title {
    font-size: 1.8rem;
  }
  
  .section-label {
    font-size: 1.2rem;
  }
  
  .images-row {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .image-wrapper img {
    height: 150px;
  }
  
  .cta-button {
    align-self: stretch;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .images-row {
    grid-template-columns: 1fr;
  }
  
  .block-title {
    font-size: 1.5rem;
  }
  
  .modal-content h3 {
    font-size: 1.2rem;
  }
}
</style>