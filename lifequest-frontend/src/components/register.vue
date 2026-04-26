<template>
  <div class="page-container">
    <div class="header-container">
      <div class="site-name">
        <h1>LifeQuest</h1>
      </div>

      <div class="auth-buttons">
        <button class="signin-btn" @click="openSignInModal">Sign In</button>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Sign In</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="handleStandardSignIn" class="standard-signin">
            <div class="form-group-signin">
              <label for="email">Email</label>
              <input 
                type="email" 
                id="email" 
                v-model="email" 
                placeholder="Enter your email"
                required
              >
            </div>
            <div class="form-group-signin">
              <label for="password">Password</label>
              <input 
                type="password" 
                id="password" 
                v-model="password" 
                placeholder="Enter your password"
                required
              >
            </div>
            <button type="submit" class="submit-btn">Sign In</button>
          </form>

          <div class="divider">
            <span>or</span>
          </div>

          <div class="external-options">
            <button class="external-btn yandex" @click="handleYandexSignIn">
              <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/chart-bar.svg" alt="Yandex">
              Sign in with Yandex
            </button>
            
            <button class="external-btn VK" @click="handleVKSignIn">
              <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/code-bracket.svg" alt="VK">
              Sign in with VK
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="top-section">
      <div class="hero-image">
        <img 
          src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80" 
          alt="Character Image"
          @error="handleImageError"
        >
        <div class="hero-overlay">
          <h2>Gameify your life</h2>
          <p>Start your journey with us today</p>
        </div>
      </div>

      <div class="signup-form">
        <h2>Register</h2>
        <form @submit.prevent="handleSignUp">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input 
              type="email" 
              id="email"
              v-model="formData.email"
              placeholder="Enter your email"
              required
              :class="{ error: emailError }"
            >
            <span v-if="emailError" class="error-message">{{ emailError }}</span>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input 
              type="password" 
              id="password"
              v-model="formData.password"
              placeholder="Create a password"
              required
              :class="{ error: passwordError }"
            >
            <span v-if="passwordError" class="error-message">{{ passwordError }}</span>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input 
              type="password" 
              id="confirmPassword"
              v-model="formData.confirmPassword"
              placeholder="Confirm your password"
              required
              :class="{ error: confirmPasswordError }"
            >
            <span v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</span>
          </div>

          <button type="submit" class="continue-button" :disabled="isLoading">
            {{ isLoading ? 'Creating Account...' : 'Continue' }}
          </button>

          <div class="divider">
            <span>or</span>
          </div>

          <div class="alternative-buttons">
            <button type="button" class="alt-button yandex" @click="signUpWithYandex">
              <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/chart-bar.svg" alt="Yandex">
              Yandex
            </button>
            <button type="button" class="alt-button vk" @click="signUpWithVK">
              <img src="https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/code-bracket.svg" alt="VK">
              VK
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="lower-section">
        <div class="general-info">
        <div class="info-content">
          <h3>Lorem ipsum dolor sit amet</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ultrices quis est in varius. Cras eu nibh congue, ullamcorper tortor at, hendrerit quam.</p>
        </div>
      </div>

      <div class="three-columns">
        <div v-for="(item, index) in textBlocks" :key="index" class="text-card">
          <h4>{{ item.title }}</h4>
          <p>{{ item.description }}</p>
        </div>
      </div>

      <div class="wide-image-section">
        <div class="center-text">
          <h3>Vestibulum dignissim</h3>
        </div>
        <div class="wide-image-container">
          <img 
            :src="wideImageSrc" 
            alt="Platform showcase"
            class="wide-image"
            @error="handleImageError"
          >
        </div>
      </div>
    </div>

    <div v-if="showSuccess" class="modal" @click.self="showSuccess = false">
      <div class="modal-content">
        <div class="modal-icon">✓</div>
        <h3>Account Created Successfully!</h3>
        <p>Welcome to our community. Please check your email to verify your account.</p>
        <button @click="HandleConfirm" class="modal-button">Got it</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignUpPage',
  redirectPath: '/mainpage',
  
  data() {
    return {
      formData: {
        email: '',
        password: '',
        confirmPassword: ''
      },
      showModal: false,
      email: '',
      password: '',
      isLoading: false,
      showSuccess: false,
      emailError: '',
      passwordError: '',
      confirmPasswordError: '',
      
      textBlocks: [
        {
          title: 'Aliquam luctus',
          description: 'Proin dignissim finibus elementum. Mauris ac venenatis justo, vitae blandit nulla. Sed pellentesque eros massa, dignissim iaculis dolor mollis malesuada. '
        },
        {
          title: 'Quisque molestie consequat enim',
          description: 'Etiam non quam nec massa vestibulum commodo. Nulla neque tellus, sagittis eu erat et, venenatis accumsan arcu.'
        },
        {
          title: 'Aliquam sed eros elit',
          description: 'Nunc vehicula turpis eget hendrerit commodo. Fusce id leo odio. Praesent nec quam tellus. Nullam non magna et turpis placerat sagittis.'
        }
      ],
    }
  },
  
  watch: {
    'formData.email'(newVal) {
      this.validateEmail(newVal)
    },
    'formData.password'(newVal) {
      this.validatePassword(newVal)
    },
    'formData.confirmPassword'(newVal) {
      this.validateConfirmPassword(newVal)
    }
  },
  
  methods: {
    handleImageError(e) {
      e.target.src = 'https://via.placeholder.com/400x300?text=Image'
    },
    
    validateEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!email) {
        this.emailError = ''
      } else if (!emailRegex.test(email)) {
        this.emailError = 'Please enter a valid email address'
      } else {
        this.emailError = ''
      }
    },
    
    validatePassword(password) {
      if (!password) {
        this.passwordError = ''
      } else if (password.length < 6) {
        this.passwordError = 'Password must be at least 6 characters'
      } else {
        this.passwordError = ''
      }
      
      if (this.formData.confirmPassword) {
        this.validateConfirmPassword(this.formData.confirmPassword)
      }
    },
    
    validateConfirmPassword(confirmPassword) {
      if (!confirmPassword) {
        this.confirmPasswordError = ''
      } else if (confirmPassword !== this.formData.password) {
        this.confirmPasswordError = 'Passwords do not match'
      } else {
        this.confirmPasswordError = ''
      }
    },
    
    validateForm() {
      let isValid = true
      
      if (!this.formData.email || this.emailError) {
        isValid = false
        if (!this.formData.email) this.emailError = 'Email is required'
      }
      
      if (!this.formData.password || this.passwordError) {
        isValid = false
        if (!this.formData.password) this.passwordError = 'Password is required'
      }
      
      if (!this.formData.confirmPassword || this.confirmPasswordError) {
        isValid = false
        if (!this.formData.confirmPassword) this.confirmPasswordError = 'Please confirm your password'
      }
      
      return isValid
    },

    HandleConfirm(){
      this.showSuccess = false
      this.$router.push('/mainpage')
    },
    
    async handleSignUp() {
      if (!this.validateForm()) {
        return
      }
      
      this.isLoading = true
      
      setTimeout(() => {
        this.isLoading = false
        this.showSuccess = true
        this.resetForm()
        this.$emit('signup-success', this.formData.email)
      }, 1500)
    },
  
    resetForm() {
      this.formData = {
        email: '',
        password: '',
        confirmPassword: ''
      }
      this.emailError = ''
      this.passwordError = ''
      this.confirmPasswordError = ''
    },
    
    signUpWithYandex() {
      console.log('Sign up with Yandex')
      this.$emit('social-signup', { provider: 'yandex' })
      alert('Yandex sign up would redirect here')
    },
    
    signUpWithVK() {
      console.log('Sign up with VK')
      this.$emit('social-signup', { provider: 'vk' })
      alert('VK sign up would redirect here')
    },

      openSignInModal() {
      this.showModal = true
      this.resetSignInForm()
    },
    
    closeModal() {
      this.showModal = false
      this.resetSignInForm()
    },
    
    resetSignInForm() {
      this.email = ''
      this.password = ''
    },
    
    handleStandardSignIn() {
      console.log('Standard sign in:', { email: this.email, password: this.password })
      this.$emit('standard-sign-in', { email: this.email, password: this.password })
      this.closeModal()
    },
    
    handleYandexSignIn() {
      console.log('Yandex sign in')
      this.$emit('external-sign-in', { provider: 'yandex' })
      this.closeModal()
    },
    
    handleVKSignIn() {
      console.log('VK sign in')
      this.$emit('external-sign-in', { provider: 'vk' })
      this.closeModal()
    },
  }
}
</script>

<style scoped>
.page-container {
  margin: 0 auto;
  background: #3B72A9;
  min-height: 100vh;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (prefers-color-scheme: light){
.site-name h1 {
color: #F9F9FA;
}

.signin-btn {
color: #F9F9FA;
}

.submit-btn{
  background: #F9F9FA;
  color: #756D78;
}

.external-btn:hover{
  background: #F9F9FA;
} 

.signup-form h2 {
color: #F9F9FA;
}

.form-subtitle {
  color: #F9F9FA;
}

.form-group label{
  color: #F9F9FA;
} 

.continue-button{
  background: #F9F9FA;
  color: #756D78;
}

.external-btn{
  border: 2px solid #F9F9FA;
}

.alt-button{
  border: 2px solid #F9F9FA;
}

.alt-button:hover{
  background: #F9F9FA;
} 

.divider span{ 
  color: #F9F9FA;
}

.divider::before,
.divider::after{ 
  background: #F9F9FA;
}

.info-content h3 {
  color: #F9F9FA;
}

.info-content p {
  color: #F9F9FA;
}

.text-card h4 {
  color: #F9F9FA;
}

.text-card p {
  color: #F9F9FA;
}

.center-text h3 {
  color: #F9F9FA;
}

.modal-content {
  background: #F9F9FA;
}

.modal-content h3 {
  color: #131313;
}

.modal-content p {
  color: #131313;
}
}

@media (prefers-color-scheme: dark){
.site-name h1 {
color: #000000;
}

.signin-btn {
color: #000000;
}

.submit-btn{
  background: #131313;
  color: #756D78;
}

.external-btn:hover {
  background: #131313;
}

.signup-form h2 {
  color: #000000;
}

.form-subtitle {
  color: #000000;
}

.form-group label{
  color: #000000;
} 

.continue-button{
  background: #131313;
  color: #756D78;
}

.external-btn{
  border: 2px solid #000000;
}

.alt-button{
  border: 2px solid #000000;
}

.alt-button:hover{
  background: #131313;
} 

.divider span{ 
  color: #131313;
}

.divider::before,
.divider::after{ 
  background: #131313;
}

.info-content h3 {
  color: #000000;
}

.info-content p {
  color: #000000;
}

.text-card h4 {
  color: #000000;
}

.text-card p {
  color: #000000;
}

.center-text h3 {
  color: #000000;
}

.modal-content {
  background: #131313;
}

.modal-content h3 {
  color: #F9F9FA;
}

.modal-content p {
  color: #F9F9FA;
}
}


.site-name {
  padding-left: 30px;
}

.site-name h1 {
  font-weight: bold;
  text-decoration: none;
}

.site-name h1:hover {
  opacity: 0.8;
}

.signin-btn {
  background: #9864FF;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.signin-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  background: #3B72A9;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
  overflow: hidden;
  animation: slideUp 0.3s ease;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #F9F9FA;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #F9F9FA;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: #999;
}

.modal-body {
  padding: 1.5rem;
}

.standard-signin {
  margin-bottom: 1.5rem;
}

.form-group-signin {
  margin-bottom: 1rem;
  width: 93.5%;
}

.form-group-signin label {
  display: block;
  margin-bottom: 0.5rem;
  color: #F9F9FA;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-group-signin input {
  width: 100%;
  padding: 0.75rem;
  background: #422974;
  border: 1px solid #553496;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #553496;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
}

.divider {
  text-align: center;
  margin: 1.5rem 0;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: calc(50% - 30px);
  height: 1px;
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.divider span {
  padding: 0 1rem;
  font-size: 0.85rem;
}

.external-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.external-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem;
  border-radius: 10px;
  background: #3B72A9;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.external-icon {
  width: 20px;
  height: 20px;
}

.top-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 600px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.hero-image {
  position: relative;
  overflow: hidden;
}

.hero-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 2rem;
  color: white;
}

.hero-overlay h2 {
  font-size: 2rem;
  margin: 0 0 0.5rem;
}

.hero-overlay p {
  font-size: 1rem;
  margin: 0;
  opacity: 0.9;
}


.signup-form {
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.signup-form h2 {
  font-size: 2rem;
  margin: 0 0 0.5rem;
  text-align: center;
}

.form-subtitle {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #553496;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: #422974;
}

.form-group input:focus {
  outline: none;
  border-color: #553496;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error {
  border-color: #f56565;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #f56565;
}

.continue-button {
  width: 100%;
  padding: 0.875rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.continue-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.continue-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alternative-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.alt-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 10px;
  background: #3B72A9;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alt-button img {
  width: 20px;
  height: 20px;
}

.alt-button.google:hover {
  border-color: #db4437;
  background: #fef2f1;
}

.alt-button.github:hover {
  border-color: #333;
  background: #f5f5f5;
}

.lower-section {
  padding: 3rem;
  background: #422974;
  margin-top: 2rem;
}

.general-info {
  display: flex;
  justify-content: center;
  margin-bottom: 3rem;
}

.info-content {
  max-width: 800px;
  text-align: center;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.info-content h3 {
  font-size: 1.8rem;
  margin: 0 0 1rem;
}

.info-content p {
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
}

.three-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-bottom: 3rem;
}

.text-card {
  padding: 1.5rem;
  border-radius: 15px;
  transition: all 0.3s ease;
}

.text-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.text-card h4 {
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
}

.text-card p {
  line-height: 1.5;
  margin: 0;
}

.images-section {
  margin-top: 2rem;
}

.section-title {
  font-size: 2rem;
  color: #333;
  text-align: center;
  margin-bottom: 2rem;
}

.three-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.wide-image-section {
  text-align: center;
}

.center-text {
  max-width: 600px;
  margin: 0 auto 2rem;
}

.center-text h3 {
  font-size: 2rem;
  margin: 0 0 0.5rem;
}


.wide-image-container {
  max-width: 100%;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.wide-image-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.wide-image {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.wide-image-container:hover .wide-image {
  transform: scale(1.02);
}


.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  max-width: 400px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-icon {
  width: 60px;
  height: 60px;
  font-size: 2rem;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  background: #422974;
  color: #F9F9FA;
}

.modal-content h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
}

.modal-content p {
  margin-bottom: 1.5rem;
}

.modal-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
  background: #422974;
  color: #F9F9FA;
}


@media (max-width: 1024px) {
  .top-section {
    grid-template-columns: 1fr;
  }
  
  .hero-image {
    min-height: 300px;
  }
  
  .three-columns,
  .three-images {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .info-block {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .lower-section {
    padding: 1.5rem;
  }
  
  .signup-form {
    padding: 2rem;
  }
  
  .three-columns,
  .three-images {
    grid-template-columns: 1fr;
  }
  
  .alternative-buttons {
    grid-template-columns: 1fr;
  }
  
  .hero-overlay h2 {
    font-size: 1.5rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
}
</style>