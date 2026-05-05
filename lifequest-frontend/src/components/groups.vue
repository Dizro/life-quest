<template>
  <div class="page-wrapper">
    <div class="groups-page">
      <header class="page-header">
        <h1 class="page-title">Команда</h1>
        <p class="page-subtitle">Общайся с группой и выполняй совместные задания.</p>
      </header>

      <div class="groups-layout">
        <!-- Members List -->
        <div class="members-panel">
          <h2 class="panel-title">Участники ({{ members.length }})</h2>
          <div class="members-list">
            <div v-for="member in members" :key="member.id" class="member-card">
              <div class="member-avatar">{{ member.name[0] }}</div>
              <div class="member-info">
                <div class="member-name">{{ member.name }}</div>
                <div class="member-level">Ур. {{ member.level }}</div>
              </div>
              <div class="member-status" :class="{ online: member.online }"></div>
            </div>
          </div>
        </div>

        <!-- Chat Panel -->
        <div class="chat-panel">
          <div class="chat-header">
            <h2 class="panel-title">Командный чат</h2>
            <span class="connection-status" :class="connectionState">{{ connectionStateText }}</span>
          </div>
          
          <div class="chat-messages" ref="chatBox">
            <div 
              v-for="msg in messages" 
              :key="msg.id" 
              class="message-bubble"
              :class="{ 'mine': msg.senderId === authStore.user?.id }"
            >
              <div class="msg-sender" v-if="msg.senderId !== authStore.user?.id">{{ msg.senderName }}</div>
              <div class="msg-content">{{ msg.text }}</div>
              <div class="msg-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
            <div v-if="messages.length === 0" class="empty-chat">
              Здесь пока тихо... Напиши первым!
            </div>
          </div>

          <form class="chat-input-area" @submit.prevent="sendMessage">
            <input 
              v-model="newMessage" 
              type="text" 
              class="chat-input" 
              placeholder="Написать в чат..." 
              :disabled="connectionState !== 'connected'"
            />
            <button type="submit" class="send-btn" :disabled="!newMessage.trim() || connectionState !== 'connected'">
              ➤
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { tasksApi } from '@/services/api'

export default {
  name: 'GroupsPage',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      eventSource: null,
      connectionState: 'disconnected', // disconnected, connecting, connected
      newMessage: '',
      messages: [
        // Dummy data for MVP if backend is not ready
        { id: '1', senderId: 'server', senderName: 'Система', text: 'Добро пожаловать в командный чат!', timestamp: Date.now() - 3600000 }
      ],
      members: [
        { id: '1', name: 'Герой', level: 5, online: true },
        { id: '2', name: 'Маг', level: 12, online: false },
        { id: '3', name: 'Авантюрист', level: 8, online: true }
      ]
    }
  },
  computed: {
    connectionStateText() {
      if (this.connectionState === 'connected') return 'Подключено'
      if (this.connectionState === 'connecting') return 'Подключение...'
      return 'Отключено'
    }
  },
  mounted() {
    this.connectSSE()
    // Update active user's name from store
    if (this.authStore.displayName) {
      this.members[0].name = this.authStore.displayName
      this.members[0].level = this.authStore.userLevel
    }
  },
  beforeUnmount() {
    if (this.eventSource) {
      this.eventSource.close()
    }
  },
  methods: {
    connectSSE() {
      this.connectionState = 'connecting'
      // Connect to SSE stream
      // Mock for MVP:
      this.connectionState = 'connected'
      
      /* Real SSE implementation:
      this.eventSource = new EventSource('/api/v1/groups/chat/stream')
      
      this.eventSource.onopen = () => {
        this.connectionState = 'connected'
      }
      
      this.eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.messages.push(data)
        this.scrollToBottom()
      }
      
      this.eventSource.onerror = () => {
        this.connectionState = 'disconnected'
        this.eventSource.close()
        // Try to reconnect after 5s
        setTimeout(this.connectSSE, 5000)
      }
      */
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return
      
      const msgText = this.newMessage
      this.newMessage = ''
      
      // Optimistic update for MVP
      this.messages.push({
        id: Date.now().toString(),
        senderId: this.authStore.user?.id || '1',
        senderName: this.authStore.displayName || 'Я',
        text: msgText,
        timestamp: Date.now()
      })
      this.scrollToBottom()
      
      /* Real API call:
      try {
        await axios.post('/api/v1/groups/chat', { text: msgText })
      } catch (err) {
        console.error('Failed to send message', err)
      }
      */
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const box = this.$refs.chatBox
        if (box) {
          box.scrollTop = box.scrollHeight
        }
      })
    },
    formatTime(ts) {
      const d = new Date(ts)
      return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
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

.groups-page {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: calc(100vh - 131px); /* minus header, paddings */
}

.page-header {
  text-align: center;
  flex-shrink: 0;
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

.groups-layout {
  display: flex;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.members-panel {
  width: 300px;
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
  flex-shrink: 0;
  overflow-y: auto;
}

.panel-title {
  font-family: 'Varela Round', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #2a1a5e;
  margin: 0;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #faf8ff;
  border-radius: 12px;
  border: 1px solid #f0ebff;
}

.member-avatar {
  width: 40px;
  height: 40px;
  background: #e8d5ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #432874;
  font-family: 'Varela Round', sans-serif;
}

.member-info {
  flex: 1;
}

.member-name {
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #2a1a5e;
}

.member-level {
  font-size: 12px;
  color: #7c5cbf;
}

.member-status {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cbd5e0;
}
.member-status.online { background: #48bb78; }

.chat-panel {
  flex: 1;
  background: #fff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
  overflow: hidden;
}

.chat-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0ebff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #faf8ff;
}

.connection-status {
  font-size: 12px;
  font-family: 'Varela Round', sans-serif;
  padding: 4px 10px;
  border-radius: 12px;
  background: #e2e8f0;
  color: #4a5568;
}
.connection-status.connected { background: #c6f6d5; color: #22543d; }
.connection-status.connecting { background: #feebc8; color: #7b341e; }

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-chat {
  text-align: center;
  color: #a0aec0;
  font-family: 'Varela Round', sans-serif;
  margin-top: 40px;
}

.message-bubble {
  max-width: 70%;
  background: #f4f0ff;
  padding: 12px 16px;
  border-radius: 16px;
  border-bottom-left-radius: 4px;
  align-self: flex-start;
}

.message-bubble.mine {
  background: #432874;
  color: #fff;
  align-self: flex-end;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 4px;
}

.msg-sender {
  font-size: 11px;
  font-family: 'Varela Round', sans-serif;
  font-weight: 700;
  color: #7c5cbf;
  margin-bottom: 4px;
}

.message-bubble.mine .msg-sender { display: none; }

.msg-content {
  font-size: 15px;
  line-height: 1.4;
  word-wrap: break-word;
}

.msg-time {
  font-size: 10px;
  color: #a0aec0;
  text-align: right;
  margin-top: 4px;
}
.message-bubble.mine .msg-time { color: rgba(255,255,255,0.6); }

.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid #f0ebff;
  display: flex;
  gap: 12px;
  background: #faf8ff;
}

.chat-input {
  flex: 1;
  background: #fff;
  border: 1px solid #d5c8ff;
  border-radius: 20px;
  padding: 12px 20px;
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus { border-color: #9a62ff; }
.chat-input:disabled { background: #f7fafc; cursor: not-allowed; }

.send-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #9a62ff;
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) { background: #8a50ef; }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 900px) {
  .groups-layout { flex-direction: column; }
  .members-panel { width: 100%; max-height: 200px; }
}
</style>