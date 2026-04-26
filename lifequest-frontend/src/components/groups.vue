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

        <div class="unified-name-block">
            <h2>Team Name</h2>
        </div>

    <div class="lower-block">
      <div class="left-column">
        <div class="column-header">
          <h3>Team Members</h3>
          <button class="sort-button" @click="toggleSort">
            <span class="sort-icon">⇅</span>
            Sort by {{ sortBy === 'name' ? 'Name' : 'Level' }}
          </button>
        </div>
        <div class="blocks-list">
          <div 
            v-for="member in sortedMembers" 
            :key="member.id"
            class="member-block"
          >
            <div class="member-image">
              <img :src="member.image" :alt="member.name" @error="handleImageError">
              <div class="online-status" :class="{ online: member.online }"></div>
            </div>
            <div class="member-info">
              <div class="member-name">{{ member.name }}</div>
              <div class="member-level">Level: {{ member.level }}</div>
              <div class="member-exp">
                <span class="exp-label">XP</span>
                <span class="exp-value">{{ member.xp.toLocaleString() }}</span>
                <div class="exp-bar">
                  <div class="exp-fill" :style="{ width: (member.xp % 1000) / 10 + '%' }"></div>
                </div>
              </div>
            </div>
                <div class="member-menu">
              <button class="three-dot-btn" @click.stop="toggleMemberMenu(member.id)">
                <span>•••</span>
              </button>
              <div v-if="activeMenuId === member.id" class="dropdown-menu">
                <div @click="viewProfile(member)">View Profile</div>
                <div @click="sendMessageTo(member)">Send Message</div>
                <div @click="viewAchievements(member)">View Achievements</div>
                <div class="divider"></div>
                <div @click="deleteMember(member)" class="danger">Delete</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="middle-column">
        <div class="column-header">
          <h3>Team Chat</h3>
          <span class="online-count">{{ onlineUsers }} online</span>
        </div>
        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div 
              v-for="(message, index) in chatMessages" 
              :key="index"
              class="chat-message"
              :class="{ own: message.isOwn }"
            >
              <div class="message-sender">{{ message.sender }}</div>
              <div class="message-text">{{ message.text }}</div>
              <div class="message-time">{{ message.time }}</div>
            </div>
          </div>
          <div class="chat-input-area">
            <input 
              type="text" 
              v-model="newMessage" 
              @keyup.enter="sendMessage"
              placeholder="Type a message..."
              class="chat-input"
            >
            <button @click="sendMessage" class="send-button">Send</button>
          </div>
        </div>
      </div>

      <div class="right-column">
        <div class="text-block">
          <h3>Summary</h3>
          <div class="summary-content">
            <p>Maecenas pharetra ac odio sed accumsan. Donec vel dignissim eros. Phasellus eget aliquet dolor, ut pharetra nisl. Ut dignissim sagittis massa. Nunc ultrices, enim ac auctor molestie, libero lectus interdum diam, vitae finibus sem quam id purus. Nam ultricies dui nec augue pellentesque feugiat. </p>
          </div>
        </div>
        
        <div class="top-members-block">
          <h4>🏆 Top Members</h4>
          <div class="top-members-list">
            <div 
              v-for="(member, index) in topMembers" 
              :key="member.id"
              class="top-member-item"
              :class="{ gold: index === 0, silver: index === 1, bronze: index === 2 }"
            >
              <div class="rank">{{ index + 1 }}</div>
              <div class="top-member-image">
                <img :src="member.image" :alt="member.name" @error="handleImageError">
              </div>
              <div class="top-member-info">
                <div class="top-member-name">{{ member.name }}</div>
                <div class="top-member-xp">{{ member.xp.toLocaleString() }} XP</div>
              </div>
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
  name: 'GroupsPage',
  
  data() {
    return {
      profileImage: '\LifeQuest\src\components\i.png',
      profileName: 'Lorem Ipsum',
      userLevel: 5,
      currentXP: 3450,
      nextLevelXP: 5000,
      
      sortBy: 'name',
      
      teamMembers: [
        { 
          id: 1, 
          name: 'Lorem Ipsum', 
          level: 5,
          image: '\LifeQuest\src\components\i.png',
          xp: 12500,
          online: true
        },
        { 
          id: 2, 
          name: 'Dolor Sit', 
          level: 5,
          image: '\LifeQuest\src\components\i.png',
          xp: 15400,
          online: true
        },
        { 
          id: 3, 
          name: 'Nullam Vitae', 
          level: 3,
          image: '\LifeQuest\src\components\i.png',
          xp: 11200,
          online: false
        },
        { 
          id: 4, 
          name: 'Viverra Urna', 
          level: 1,
          image: '\LifeQuest\src\components\i.png',
          xp: 18900,
          online: true
        },
        { 
          id: 5, 
          name: 'Aliquam Nonmiquam', 
          level: 2,
          image: '\LifeQuest\src\components\i.png',
          xp: 7200,
          online: false
        },
        { 
          id: 6, 
          name: 'Sed Imperdiet', 
          level: 5,
          image: '\LifeQuest\src\components\i.png',
          xp: 6800,
          online: true
        },
        { 
          id: 7, 
          name: 'Mattis Arcu', 
          level: 4,
          image: '\LifeQuest\src\components\i.png',
          xp: 14300,
          online: true
        }
      ],
      
      onlineUsers: 5,
      chatMessages: [
        { sender: 'Dolor', text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.', time: '10:32 AM', isOwn: false },
        { sender: 'Nullam', text: 'Nullam sollicitudin augue vitae facilisis hendrerit.', time: '10:35 AM', isOwn: false },
        { sender: 'You', text: 'Nam faucibus ultrices tincidunt. Nam a odio posuere, mattis erat eu, pellentesque mi. ', time: '10:38 AM', isOwn: true },
        { sender: 'Viverra', text: 'Nullam vitae libero nibh. Interdum et malesuada fames ac ante ipsum primis in faucibus.', time: '10:42 AM', isOwn: false },
        { sender: 'You', text: 'Aenean elementum lectus quam, ut condimentum ligula iaculis et. ', time: '10:45 AM', isOwn: true }
      ],
      newMessage: '',
      
      animatedExp: 0
    }
  },
  
  computed: {
    xpPercentage() {
      return Math.min(100, (this.currentXP / this.nextLevelXP) * 100)
    },
    
    sortedMembers() {
      if (this.sortBy === 'name') {
        return [...this.teamMembers].sort((a, b) => a.name.localeCompare(b.name))
      } else {
        return [...this.teamMembers].sort((a, b) => b.level - a.level)
      }
    },
    
    topMembers() {
      return [...this.teamMembers].sort((a, b) => b.level - a.level).slice(0, 3)
    },
      
  },
  
  mounted() {
    this.animateCounter()
    this.scrollChatToBottom()
  },
  
  updated() {
    this.scrollChatToBottom()
  },
  
  methods: {
    handleImageError(e) {
      e.target.src = 'https://via.placeholder.com/50x50?text=User'
    },
    
    animateCounter() {
      let start = 0
      const end = this.currentExp
      const duration = 2000
      const increment = end / (duration / 16)
      
      const timer = setInterval(() => {
        start += increment
        if (start >= end) {
          this.animatedExp = end
          clearInterval(timer)
        } else {
          this.animatedExp = Math.floor(start)
        }
      }, 16)
    },
    
    toggleSort() {
      this.sortBy = this.sortBy === 'name' ? 'level' : 'name'
    },

    toggleMemberMenu(id) {
      this.activeMenuId = this.activeMenuId === id ? null : id
    },
    
    handleClickOutside(event) {
      if (!event.target.closest('.member-menu')) {
        this.activeMenuId = null
      }
    },
    
    viewProfile(member) {
      alert(`Viewing profile of ${member.name}`)
      this.activeMenuId = null
    },
    
    sendMessageTo(member) {
      alert(`Send message to ${member.name}`)
      this.activeMenuId = null
    },
    
    viewAchievements(member) {
      alert(`View achievements of ${member.name}`)
      this.activeMenuId = null
    },
    
    deleteMember(member) {
      alert(`Delete ${member.name}`)
      this.activeMenuId = null
    },
    
    sendMessage() {
      if (this.newMessage.trim()) {
        this.chatMessages.push({
          sender: 'You',
          text: this.newMessage,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOwn: true
        })
        this.newMessage = ''
      }
    },
    
    scrollChatToBottom() {
      const container = this.$refs.chatMessages
      if (container) {
        container.scrollTop = container.scrollHeight
      }
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

.xp-bar {
  background: #422974;
}

.xp-bar-container {
  background: #F9F9FA;
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

.unified-name-block h2 {
  color: #F9F9FA;
}

.left-column,
.middle-column,
.right-column {
  background: #F9F9FA;
}

.column-header h3 {
  color: #000000;
}

.sort-button {
  background: #F9F9FA;
  border: 1px solid #8A8A8A;
}

.member-block {
  background: #F9F9FA;
}

.member-block:hover {
  background: #F9F9FA;
}

.member-name {
  color: #131313;
}

.member-level {
  color: #8A8A8A;
}

.exp-value {
  color: #422974;
}

.exp-label {
  color: #8A8A8A;
}

.exp-bar {
  background: #e0e0e0;
}

.exp-fill {
  background: #422974;
}

.three-dot-btn {
  color: #8A8A8A;
}

.dropdown-menu {
  background: #F9F9FA;
}

.dropdown-menu div:hover {
  background: #F9F9FA;
}

.dropdown-menu .divider {
  background: #422974;
}

.chat-message {
  background: #D9D9D9;
  color: #131313;
}

.message-time {
  color: #8A8A8A;
}

.chat-message.own .message-time {
  color: #F9F9FA;
}

.chat-input-area {
  background: #F9F9FA;
  border-top: 1px solid #422974;
}

.chat-input {
  border: 1px solid #553496;
}

.text-block {
  border-bottom: 1px solid #422974;
}

.text-block h3 {
  color: #131313;
}

.summary-content p {
  color: #131313;
}

.top-members-block h4 {
  color: #131313;
}

.top-member-item {
  background: #F9F9FA;
}

.top-member-item:hover {
  background: #F9F9FA;
}

.top-member-name {
  color: #131313;
}

.top-member-xp {
  color: #422974;
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

.unified-name-block h2 {
  color: #131313;
}

.left-column,
.middle-column,
.right-column {
  background: #0D0D0D;
}

.column-header h3 {
  color: #F9F9FA;
}

.sort-button {
  background: #0D0D0D;
  border: 1px solid #F9F9FA;
  color: #F9F9FA;
}

.member-block {
  background: #333333;
}

.member-block:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 41, 116, 0.3);
}

.member-name {
  color: #F9F9FA;
}

.member-level {
  color: #F9F9FA;
}

.exp-value {
  color: #9864FF;
}

.exp-label {
  color: #F9F9FA;
}

.exp-bar {
  background: #131313;
}

.exp-fill {
  background: #9864FF;
}

.three-dot-btn {
  color: #F9F9FA;
}

.dropdown-menu {
  background: white;
}

.dropdown-menu div:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 41, 116, 0.3);
}

.dropdown-menu .divider {
  background: #F9F9FA;
}

.chat-message {
  background: #333333;
  color: ;
}

.message-time {
  color: #F9F9FA;
}

.chat-message.own .message-time {
  color: #131313;
}

.chat-input-area {
  background: #333333;
  border-top: 1px solid #422974;
}

.chat-input {
  border: 1px solid #422974;
}

.text-block {
  border-bottom: 1px solid #422974;
}

.text-block h3 {
  color: #F9F9FA;
}

.summary-content p {
  color: #F9F9FA;
}

.top-members-block h4 {
  color: #F9F9FA;
}

.top-member-item {
  background: #333333;
}

.top-member-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 41, 116, 0.3);
}

.top-member-name {
  color: #F9F9FA;
}

.top-member-xp {
  color: #9864FF;
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

.unified-name-block {
  background: #422974;
  width: 301%;
  margin: 0 2rem;
  margin-bottom: -25px;
  padding: 1.5rem 2rem;
  border-radius: 20px 20px 0 0;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border-top: 1px solid #422974;
}

.unified-name-block h2 {
  font-size: 1.5rem;
  margin: 0 0 0.25rem;
}

.lower-block {
  width: 306%;
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 1.5rem;
  margin: 0 2rem 2rem;
  padding: 20px;
  border-radius: 0 0 20px 20px;
}

.left-column,
.middle-column,
.right-column {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #422974;
}

.column-header h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.sort-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-button:hover {
  background: #422974;
  color: #F9F9FA;
  border-color: #553496;
}

.sort-icon {
  font-size: 0.8rem;
}

.blocks-list {
  flex: 1;
  overflow-y: auto;
  max-height: 500px;
  padding: 0.5rem;
}

.member-block {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.member-block:hover {
  transform: translateX(3px);
}

.member-image {
  position: relative;
  flex-shrink: 0;
}

.member-image img {
  width: 55px;
  height: 55px;
  object-fit: cover;
  border: 2px solid #422974;
}

.online-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #ccc;
  border-radius: 50%;
  border: 2px solid white;
}

.online-status.online {
  background: #48bb78;
}

.member-info {
  flex: 1;
}

.member-name {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.member-level {
  font-size: 0.7rem;
  margin-bottom: 0.5rem;
}

.member-exp {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.exp-label {
  font-size: 0.65rem;
}

.exp-value {
  font-size: 0.85rem;
  font-weight: 600;
}

.exp-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  min-width: 80px;
}

.exp-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.member-menu {
  position: relative;
  flex-shrink: 0;
}

.three-dot-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0.25rem;
  transition: color 0.2s ease;
}

.three-dot-btn:hover {
  color: #553496;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
  min-width: 140px;
  z-index: 10;
  overflow: hidden;
}

.dropdown-menu div {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.dropdown-menu .divider {
  height: 1px;
  padding: 0;
  margin: 0.25rem 0;
}

.dropdown-menu .danger {
  color: #f56565;
}

.dropdown-menu .danger:hover {
  background: #fff5f5;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 500px;
}

.online-count {
  font-size: 0.7rem;
  color: #48bb78;
  font-weight: 500;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-message {
  max-width: 85%;
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
}

.chat-message.own {
  align-self: flex-end;
  background: #C0B8DB;
  color: #131313;
}

.message-sender {
  font-size: 0.7rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #1B0370;
}

.chat-message.own .message-sender {
  color: #1B0370;
}

.message-text {
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.message-time {
  font-size: 0.6rem;
  text-align: right;
}

.chat-input-area {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
}

.chat-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  outline: none;
}

.chat-input:focus {
  border-color: #553496;
}

.send-button {
  padding: 0.5rem 1rem;
  background: #553496;
  color: #F9F9FA;
  border: none;
  border-radius: 20px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.send-button:hover {
  background: #9864FF;
}

.text-block {
  padding: 1.25rem;
}

.text-block h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
}

.summary-content p {
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.summary-content p:last-child {
  margin-bottom: 0;
}

.top-members-block {
  padding: 1.25rem;
  flex: 1;
}

.top-members-block h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 1rem;
}

.top-members-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.top-member-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 12px;
  transition: all 0.2s ease;
  position: relative;
}

.top-member-item:hover {
  transform: translateX(3px);
}

.top-member-item.gold {
  border-left: 3px solid #ffd700;
}

.top-member-item.silver {
  border-left: 3px solid #c0c0c0;
}

.top-member-item.bronze {
  border-left: 3px solid #cd7f32;
}

.rank {
  font-size: 1.2rem;
  font-weight: bold;
  width: 35px;
  text-align: center;
}

.top-member-image img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.top-member-info {
  flex: 1;
}

.top-member-name {
  font-size: 0.85rem;
  font-weight: 600;
}

.top-member-xp {
  font-size: 0.7rem;
  font-weight: 500;
}


.blocks-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.blocks-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: #F9F9FA;
  border-radius: 4px;
}

.blocks-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #422974;
  border-radius: 4px;
}

@media (max-width: 1024px) {
  .lower-block {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin: 0 1rem 1rem;
  }
  
  .top-block {
    margin: 1rem;
    flex-direction: column;
    text-align: center;
  }
  
  .chat-container {
    height: 400px;
  }
  
  .blocks-list {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .counter-value .number {
    font-size: 1.8rem;
  }
  
  .member-block {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .member-exp {
    justify-content: center;
  }
  
  .top-member-item {
    flex-wrap: wrap;
  }
  
  .team-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-label {
    margin-bottom: 0;
  }
}
</style>