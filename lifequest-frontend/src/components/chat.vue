<template>
  <div class="page-wrapper">
    <div class="chat-page">
      <header class="page-header">
        <h1 class="page-title">Наставник Фаррикс</h1>
        <p class="page-subtitle">Получи совет, настройся на работу или просто поболтай.</p>
      </header>

      <div class="chat-container">
        <!-- Область сообщений -->
        <div class="chat-messages" ref="chatScroll">
          <div 
            v-for="(msg, i) in chatHistory" 
            :key="i" 
            class="message-wrapper"
            :class="{ 'mine': msg.role === 'user' }"
          >
            <div v-if="msg.role === 'assistant'" class="avatar-circle">🧙</div>
            
            <div class="message-bubble" :class="{ 'mine': msg.role === 'user' }">
              <span v-if="msg.role === 'assistant'" class="sender-name">Фаррикс</span>
              <span v-else class="sender-name">{{ authStore.displayName || 'Ты' }}</span>
              <div class="message-text">{{ msg.content }}</div>
            </div>

            <div v-if="msg.role === 'user'" class="avatar-circle mine">
              {{ (authStore.displayName || 'Г')[0].toUpperCase() }}
            </div>
          </div>

          <!-- Индикатор набора текста -->
          <div v-if="isChatTyping" class="message-wrapper">
            <div class="avatar-circle">🧙</div>
            <div class="message-bubble typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>

        <!-- Область ввода -->
        <div class="chat-input-area">
          <input 
            v-model="chatInput" 
            @keyup.enter="sendChatMessage" 
            type="text" 
            class="chat-input" 
            placeholder="Спроси совета или расскажи о своих планах..." 
            :disabled="isChatTyping"
          >
          <button 
            @click="sendChatMessage" 
            class="send-btn" 
            :disabled="isChatTyping || !chatInput.trim()"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { chatApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const isChatTyping = ref(false)
const chatInput = ref('')
const chatScroll = ref(null)

// Начальное приветствие
const chatHistory = ref([
  { 
    role: 'assistant', 
    content: `Приветствую, ${authStore.displayName || 'Герой'}! Я Фаррикс — твой ИИ-наставник. Я здесь, чтобы помочь тебе распланировать день, оценить сложность твоих задач или просто поддержать в трудную минуту. О чем поговорим?` 
  }
])

const scrollToBottom = () => {
  nextTick(() => {
    if (chatScroll.value) {
      chatScroll.value.scrollTop = chatScroll.value.scrollHeight
    }
  })
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || isChatTyping.value) return
  
  const userText = chatInput.value
  chatHistory.value.push({ role: 'user', content: userText })
  chatInput.value = ''
  isChatTyping.value = true
  scrollToBottom()

  try {
    // Отправляем историю (исключая текущее сообщение пользователя, чтобы бекенд получил его отдельно)
    const historyToSend = chatHistory.value.slice(0, -1).map(m => ({role: m.role, content: m.content}))
    const res = await chatApi.send(userText, historyToSend)
    
    chatHistory.value.push({ role: 'assistant', content: res.reply })
  } catch (err) {
    chatHistory.value.push({ 
      role: 'assistant', 
      content: "Моя магическая связь прервалась... Похоже, мы превысили лимит общения на сегодня, либо магия сети иссякла." 
    })
  } finally {
    isChatTyping.value = false
    scrollToBottom()
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchProfile()
  }
})
</script>

<style scoped>
.page-wrapper {
  min-height: calc(100vh - 67px);
  background: linear-gradient(160deg, #f4f0ff 0%, #e8d5ff 40%, #c9a6ff 100%);
  padding: 32px 24px;
}

.chat-page {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: calc(100vh - 131px); /* Чтобы чат не выходил за пределы экрана */
}

.page-header { text-align: center; flex-shrink: 0; }
.page-title { font-family: 'Varela Round', sans-serif; font-size: 36px; font-weight: 700; color: #2a1a5e; margin-bottom: 8px; }
.page-subtitle { font-family: 'Varela Round', sans-serif; font-size: 16px; color: #5a4a7a; }

.chat-container {
  flex: 1;
  background: #fff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(66,41,116,0.12);
  overflow: hidden;
  border: 2px solid #d5c8ff;
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #faf8ff;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  max-width: 85%;
}

.message-wrapper.mine {
  align-self: flex-end;
  flex-direction: row;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background: #e8d5ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  border: 2px solid #9a62ff;
}

.avatar-circle.mine {
  background: #9a62ff;
  color: white;
  font-weight: bold;
  border-color: #432874;
}

.message-bubble {
  background: #fff;
  padding: 14px 18px;
  border-radius: 20px;
  border-bottom-left-radius: 4px;
  border: 1px solid #e0d6ff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.message-bubble.mine {
  background: #432874;
  color: #fff;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 4px;
  border: none;
}

.sender-name {
  display: block;
  font-size: 12px;
  font-family: 'Varela Round', sans-serif;
  font-weight: 700;
  color: #9a62ff;
  margin-bottom: 4px;
}

.message-bubble.mine .sender-name {
  color: #d5c8ff;
  text-align: right;
}

.message-text {
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.chat-input-area {
  padding: 20px 24px;
  background: #fff;
  border-top: 1px solid #f0ebff;
  display: flex;
  gap: 12px;
}

.chat-input {
  flex: 1;
  background: #f4f0ff;
  border: 1px solid #d5c8ff;
  border-radius: 24px;
  padding: 16px 24px;
  font-family: 'Varela Round', sans-serif;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus { border-color: #9a62ff; }
.chat-input:disabled { opacity: 0.7; cursor: not-allowed; }

.send-btn {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #9a62ff;
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: background 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) { background: #8a50ef; }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Анимация печати */
.typing .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: #9a62ff;
  border-radius: 50%;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out;
}
.typing .dot:nth-child(1) { animation-delay: 0s; }
.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.typing .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
</style>