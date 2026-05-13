<template>
  <div class="page-wrapper">
    <div class="groups-page">
      <header class="page-header">
        <h1 class="page-title">Гильдии</h1>
        <p class="page-subtitle">Создай или вступи в группу, общайся и выполняй квесты вместе.</p>
      </header>

      <div class="groups-layout">
        <!-- Left: Group list -->
        <div class="groups-sidebar">
          <button class="create-group-btn" @click="showCreateModal = true">+ Создать гильдию</button>

          <div class="group-list">
            <div v-if="groups.length === 0" class="empty-list">Нет доступных гильдий</div>
            <div
              v-for="g in groups"
              :key="g.id"
              class="group-card"
              :class="{ active: selectedGroup?.id === g.id }"
              @click="selectGroup(g)"
            >
              <div class="group-card-icon">⚔️</div>
              <div class="group-card-info">
                <div class="group-card-name">{{ g.name }}</div>
                <div class="group-card-meta">{{ g.member_count }} участн.</div>
              </div>
              <span v-if="g.is_member" class="member-badge">✓</span>
            </div>
          </div>
        </div>

        <!-- Center: Chat -->
        <div class="chat-panel" v-if="selectedGroup && selectedGroup.is_member">
          <div class="chat-header">
            <h2 class="panel-title">{{ selectedGroup.name }}</h2>
          </div>
          <div class="chat-messages" ref="chatBox">
            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message-bubble"
              :class="{ mine: msg.user_id === authStore.user?.id }"
            >
              <div class="msg-sender" v-if="msg.user_id !== authStore.user?.id">{{ msg.sender_name }}</div>
              <div class="msg-content">{{ msg.text }}</div>
              <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
            </div>
            <div v-if="messages.length === 0" class="empty-chat">Здесь пока тихо... Напиши первым!</div>
          </div>
          <form class="chat-input-area" @submit.prevent="sendMessage">
            <input v-model="newMessage" type="text" class="chat-input" placeholder="Написать в чат..." />
            <button type="submit" class="send-btn" :disabled="!newMessage.trim()">➤</button>
          </form>
        </div>

        <!-- Center: Not a member -->
        <div class="chat-panel empty-state" v-else-if="selectedGroup && !selectedGroup.is_member">
          <div class="join-prompt">
            <div class="join-icon">🏰</div>
            <h2>{{ selectedGroup.name }}</h2>
            <p>{{ selectedGroup.description || 'Нет описания' }}</p>
            <p class="join-meta">Участников: {{ selectedGroup.member_count }}</p>
            <button class="join-btn" @click="joinGroup" :disabled="joining">
              {{ joining ? 'Вступаем...' : 'Вступить в гильдию' }}
            </button>
          </div>
        </div>

        <!-- Center: Nothing selected -->
        <div class="chat-panel empty-state" v-else>
          <div class="join-prompt">
            <div class="join-icon">👈</div>
            <h2>Выбери гильдию</h2>
            <p>Выбери гильдию из списка слева или создай свою.</p>
          </div>
        </div>

        <!-- Right: Group info -->
        <div class="info-panel" v-if="selectedGroup">
          <h3 class="info-title">{{ selectedGroup.name }}</h3>
          <p class="info-desc">{{ groupDetail?.description || selectedGroup.description || 'Нет описания' }}</p>
          <div class="info-stats">
            <div class="info-stat">
              <span class="info-stat-val">{{ groupDetail?.members?.length || selectedGroup.member_count }}</span>
              <span class="info-stat-label">Участников</span>
            </div>
          </div>

          <!-- Owner controls -->
          <div v-if="isOwner" class="owner-controls">
            <button class="edit-btn" @click="openEditModal">✏️ Редактировать</button>
            <button class="delete-btn" @click="deleteGroup">🗑️ Удалить</button>
          </div>

          <div v-if="groupDetail?.members?.length" class="members-section">
            <h4 class="members-title">Участники</h4>
            <div class="members-list">
              <div v-for="m in groupDetail.members" :key="m.user_id" class="member-row">
                <div class="member-avatar">{{ (m.display_name || m.username)[0].toUpperCase() }}</div>
                <div class="member-info">
                  <div class="member-name">{{ m.display_name || m.username }}
                    <span v-if="m.role === 'owner'" class="owner-tag">👑</span>
                  </div>
                  <div class="member-level">Ур. {{ m.level }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="!selectedGroup.is_member" class="members-locked">
            🔒 Вступи, чтобы увидеть участников
          </div>

          <button
            v-if="selectedGroup.is_member && !isOwner"
            class="leave-btn"
            @click="leaveGroup"
          >Покинуть гильдию</button>
        </div>
      </div>

      <!-- Create Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
            <div class="modal-card">
              <h2 class="modal-title">Создать гильдию</h2>
              <div v-if="createError" class="modal-error">{{ createError }}</div>
              <div class="form-group">
                <label>Название</label>
                <input v-model="createForm.name" class="custom-input" placeholder="Рыцари Рассвета..." maxlength="100" />
              </div>
              <div class="form-group">
                <label>Описание</label>
                <textarea v-model="createForm.description" class="custom-input textarea" placeholder="Расскажи о группе..." maxlength="500" rows="3"></textarea>
              </div>
              <div class="modal-actions">
                <button class="btn-ghost" @click="showCreateModal = false">Отмена</button>
                <button class="btn-primary" @click="createGroup" :disabled="creating">
                  {{ creating ? 'Создаём...' : 'Создать' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Edit Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
            <div class="modal-card">
              <h2 class="modal-title">Редактировать гильдию</h2>
              <div v-if="editError" class="modal-error">{{ editError }}</div>
              <div class="form-group">
                <label>Название</label>
                <input v-model="editForm.name" class="custom-input" maxlength="100" />
              </div>
              <div class="form-group">
                <label>Описание</label>
                <textarea v-model="editForm.description" class="custom-input textarea" maxlength="500" rows="3"></textarea>
              </div>
              <div class="modal-actions">
                <button class="btn-ghost" @click="showEditModal = false">Отмена</button>
                <button class="btn-primary" @click="saveEdit" :disabled="saving">
                  {{ saving ? 'Сохраняем...' : 'Сохранить' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { groupsApi } from '@/services/api'

export default {
  name: 'GroupsPage',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      groups: [],
      selectedGroup: null,
      groupDetail: null,
      messages: [],
      newMessage: '',
      chatPoll: null,

      showCreateModal: false,
      createForm: { name: '', description: '' },
      createError: null,
      creating: false,
      joining: false,

      showEditModal: false,
      editForm: { name: '', description: '' },
      editError: null,
      saving: false,
    }
  },
  computed: {
    isOwner() {
      return this.selectedGroup && this.selectedGroup.owner_id === this.authStore.user?.id
    }
  },
  async mounted() {
    await this.loadGroups()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    async loadGroups() {
      try {
        this.groups = await groupsApi.list()
      } catch (e) {
        console.error('Failed to load groups', e)
      }
    },

    async selectGroup(g) {
      this.selectedGroup = g
      this.messages = []
      this.stopPolling()

      try {
        this.groupDetail = await groupsApi.get(g.id)
        this.selectedGroup.is_member = this.groupDetail.is_member
      } catch (e) {
        console.error(e)
      }

      if (g.is_member) {
        await this.loadMessages()
        this.startPolling()
      }
    },

    async loadMessages() {
      if (!this.selectedGroup) return
      try {
        const newMsgs = await groupsApi.getMessages(this.selectedGroup.id)
        if (newMsgs.length !== this.messages.length || (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].id !== this.messages[this.messages.length - 1]?.id)) {
          this.messages = newMsgs
          this.scrollToBottom()
        }
      } catch (e) {
        console.error(e)
      }
    },

    startPolling() {
      this.chatPoll = setInterval(() => this.loadMessages(), 4000)
    },
    stopPolling() {
      if (this.chatPoll) { clearInterval(this.chatPoll); this.chatPoll = null }
    },

    async sendMessage() {
      if (!this.newMessage.trim() || !this.selectedGroup) return
      const text = this.newMessage
      this.newMessage = ''
      try {
        const msg = await groupsApi.sendMessage(this.selectedGroup.id, text)
        this.messages.push(msg)
        this.scrollToBottom()
      } catch (e) {
        console.error('Send failed', e)
      }
    },

    async joinGroup() {
      if (!this.selectedGroup) return
      this.joining = true
      try {
        await groupsApi.join(this.selectedGroup.id)
        this.selectedGroup.is_member = true
        this.selectedGroup.member_count++
        await this.selectGroup(this.selectedGroup)
        await this.loadGroups()
      } catch (e) {
        alert(e?.detail || 'Ошибка вступления')
      } finally {
        this.joining = false
      }
    },

    async leaveGroup() {
      if (!this.selectedGroup) return
      if (!confirm('Покинуть гильдию?')) return
      try {
        await groupsApi.leave(this.selectedGroup.id)
        this.selectedGroup = null
        this.groupDetail = null
        this.messages = []
        this.stopPolling()
        await this.loadGroups()
      } catch (e) {
        alert(e?.detail || 'Ошибка')
      }
    },

    async createGroup() {
      this.createError = null
      if (!this.createForm.name.trim()) {
        this.createError = 'Введите название'
        return
      }
      this.creating = true
      try {
        const g = await groupsApi.create(this.createForm)
        this.showCreateModal = false
        this.createForm = { name: '', description: '' }
        await this.loadGroups()
        await this.selectGroup(g)
      } catch (e) {
        this.createError = e?.detail || 'Ошибка создания'
      } finally {
        this.creating = false
      }
    },

    openEditModal() {
      this.editForm.name = this.selectedGroup.name
      this.editForm.description = this.groupDetail?.description || this.selectedGroup.description || ''
      this.editError = null
      this.showEditModal = true
    },

    async saveEdit() {
      this.editError = null
      this.saving = true
      try {
        const updated = await groupsApi.update(this.selectedGroup.id, this.editForm)
        this.selectedGroup.name = updated.name
        this.selectedGroup.description = updated.description
        if (this.groupDetail) {
          this.groupDetail.name = updated.name
          this.groupDetail.description = updated.description
        }
        this.showEditModal = false
        await this.loadGroups()
      } catch (e) {
        this.editError = e?.detail || 'Ошибка сохранения'
      } finally {
        this.saving = false
      }
    },

    async deleteGroup() {
      if (!confirm('Удалить гильдию? Это действие необратимо.')) return
      try {
        await groupsApi.remove(this.selectedGroup.id)
        this.selectedGroup = null
        this.groupDetail = null
        this.messages = []
        this.stopPolling()
        await this.loadGroups()
      } catch (e) {
        alert(e?.detail || 'Ошибка удаления')
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const box = this.$refs.chatBox
        if (box) box.scrollTop = box.scrollHeight
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
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 131px);
}
.page-header { text-align: center; flex-shrink: 0; }
.page-title { font-family: 'Varela Round', sans-serif; font-size: 36px; font-weight: 700; color: #2a1a5e; margin-bottom: 8px; }
.page-subtitle { font-family: 'Varela Round', sans-serif; font-size: 16px; color: #5a4a7a; }

.groups-layout { display: flex; gap: 20px; flex: 1; min-height: 0; }

/* ── Left sidebar ── */
.groups-sidebar {
  width: 260px; flex-shrink: 0;
  background: #fff; border-radius: 20px; padding: 20px;
  display: flex; flex-direction: column; gap: 14px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
  overflow-y: auto;
}
.create-group-btn {
  width: 100%; padding: 12px; border: 2px dashed #d5c8ff;
  border-radius: 14px; background: transparent;
  font-family: 'Varela Round', sans-serif; font-size: 15px;
  font-weight: 700; color: #9a62ff; cursor: pointer;
  transition: all 0.2s;
}
.create-group-btn:hover { background: #f4f0ff; border-color: #9a62ff; }
.group-list { display: flex; flex-direction: column; gap: 8px; }
.empty-list { text-align: center; color: #a0aec0; font-family: 'Varela Round', sans-serif; padding: 24px 0; font-size: 14px; }
.group-card {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-radius: 14px;
  border: 1px solid #f0ebff; background: #faf8ff;
  cursor: pointer; transition: all 0.2s;
}
.group-card:hover { border-color: #d5c8ff; background: #f4f0ff; }
.group-card.active { border-color: #9a62ff; background: #ede5ff; }
.group-card-icon { font-size: 24px; }
.group-card-info { flex: 1; min-width: 0; }
.group-card-name { font-family: 'Varela Round', sans-serif; font-size: 14px; font-weight: 700; color: #2a1a5e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.group-card-meta { font-size: 12px; color: #7c5cbf; }
.member-badge { font-size: 14px; color: #48bb78; font-weight: 700; }

/* ── Center chat ── */
.chat-panel {
  flex: 1; background: #fff; border-radius: 20px;
  display: flex; flex-direction: column;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
  overflow: hidden; min-width: 0;
}
.chat-panel.empty-state { justify-content: center; align-items: center; }
.chat-header { padding: 18px 24px; border-bottom: 1px solid #f0ebff; background: #faf8ff; }
.panel-title { font-family: 'Varela Round', sans-serif; font-size: 17px; font-weight: 700; color: #2a1a5e; margin: 0; }
.chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
.empty-chat { text-align: center; color: #a0aec0; font-family: 'Varela Round', sans-serif; margin-top: 40px; }
.message-bubble { max-width: 70%; background: #f4f0ff; padding: 10px 14px; border-radius: 16px; border-bottom-left-radius: 4px; align-self: flex-start; }
.message-bubble.mine { background: #432874; color: #fff; align-self: flex-end; border-bottom-left-radius: 16px; border-bottom-right-radius: 4px; }
.msg-sender { font-size: 11px; font-family: 'Varela Round', sans-serif; font-weight: 700; color: #7c5cbf; margin-bottom: 3px; }
.message-bubble.mine .msg-sender { display: none; }
.msg-content { font-size: 15px; line-height: 1.4; word-wrap: break-word; }
.msg-time { font-size: 10px; color: #a0aec0; text-align: right; margin-top: 3px; }
.message-bubble.mine .msg-time { color: rgba(255,255,255,0.6); }
.chat-input-area { padding: 14px 20px; border-top: 1px solid #f0ebff; display: flex; gap: 10px; background: #faf8ff; }
.chat-input { flex: 1; background: #fff; border: 1px solid #d5c8ff; border-radius: 20px; padding: 12px 20px; font-family: 'Varela Round', sans-serif; font-size: 15px; outline: none; transition: border-color 0.2s; }
.chat-input:focus { border-color: #9a62ff; }
.send-btn { width: 46px; height: 46px; border-radius: 50%; background: #9a62ff; color: #fff; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px; transition: background 0.2s; }
.send-btn:hover:not(:disabled) { background: #8a50ef; }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Join prompt ── */
.join-prompt { text-align: center; padding: 40px; }
.join-icon { font-size: 56px; margin-bottom: 16px; }
.join-prompt h2 { font-family: 'Varela Round', sans-serif; font-size: 24px; color: #2a1a5e; margin-bottom: 8px; }
.join-prompt p { font-family: 'Varela Round', sans-serif; font-size: 15px; color: #7c5cbf; margin-bottom: 4px; }
.join-meta { font-weight: 700; margin-bottom: 20px !important; }
.join-btn { padding: 14px 32px; border-radius: 14px; background: #9a62ff; color: #fff; border: none; font-family: 'Varela Round', sans-serif; font-size: 16px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.join-btn:hover:not(:disabled) { background: #8a50ef; }
.join-btn:disabled { opacity: 0.6; }

/* ── Right info panel ── */
.info-panel {
  width: 260px; flex-shrink: 0;
  background: #fff; border-radius: 20px; padding: 24px;
  box-shadow: 0 8px 32px rgba(66,41,116,0.08);
  display: flex; flex-direction: column; gap: 16px;
  overflow-y: auto;
}
.info-title { font-family: 'Varela Round', sans-serif; font-size: 18px; font-weight: 700; color: #2a1a5e; margin: 0; }
.info-desc { font-family: 'Varela Round', sans-serif; font-size: 14px; color: #7c5cbf; line-height: 1.5; margin: 0; }
.info-stats { display: flex; gap: 16px; }
.info-stat { display: flex; flex-direction: column; align-items: center; background: #faf8ff; border: 1px solid #f0ebff; border-radius: 14px; padding: 14px 20px; flex: 1; }
.info-stat-val { font-family: 'Varela Round', sans-serif; font-size: 22px; font-weight: 700; color: #2a1a5e; }
.info-stat-label { font-size: 11px; color: #7c5cbf; text-transform: uppercase; letter-spacing: 0.5px; }

.members-section { border-top: 1px solid #f0ebff; padding-top: 16px; }
.members-title { font-family: 'Varela Round', sans-serif; font-size: 14px; font-weight: 700; color: #2a1a5e; margin: 0 0 12px 0; }
.members-list { display: flex; flex-direction: column; gap: 8px; }
.member-row { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 10px; background: #faf8ff; }
.member-avatar { width: 34px; height: 34px; background: #e8d5ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #432874; font-family: 'Varela Round', sans-serif; font-size: 14px; flex-shrink: 0; }
.member-info { flex: 1; min-width: 0; }
.member-name { font-family: 'Varela Round', sans-serif; font-size: 13px; font-weight: 700; color: #2a1a5e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.member-level { font-size: 11px; color: #7c5cbf; }
.owner-tag { font-size: 12px; margin-left: 4px; }
.owner-controls { display: flex; gap: 8px; }
.edit-btn, .delete-btn { flex: 1; padding: 10px; border-radius: 12px; font-family: 'Varela Round', sans-serif; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; border: none; }
.edit-btn { background: #f4f0ff; color: #9a62ff; }
.edit-btn:hover { background: #ede5ff; }
.delete-btn { background: #fff5f5; color: #e53e3e; }
.delete-btn:hover { background: #fed7d7; }
.members-locked { text-align: center; padding: 20px; color: #a0aec0; font-family: 'Varela Round', sans-serif; font-size: 14px; background: #faf8ff; border-radius: 12px; }
.leave-btn { width: 100%; padding: 12px; border-radius: 14px; background: transparent; border: 2px solid #e53e3e; color: #e53e3e; font-family: 'Varela Round', sans-serif; font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: auto; }
.leave-btn:hover { background: #fff5f5; }

/* ── Modal ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); backdrop-filter: blur(6px); z-index: 3000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: #fff; border-radius: 24px; padding: 32px; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.modal-title { font-family: 'Varela Round', sans-serif; font-size: 22px; font-weight: 700; color: #2a1a5e; margin: 0 0 20px 0; }
.modal-error { background: #fff5f5; color: #e53e3e; padding: 10px 16px; border-radius: 12px; font-size: 14px; margin-bottom: 16px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-family: 'Varela Round', sans-serif; font-size: 14px; font-weight: 700; color: #2a1a5e; margin-bottom: 6px; }
.custom-input { width: 100%; padding: 12px 16px; border: 1px solid #d5c8ff; border-radius: 14px; font-family: 'Varela Round', sans-serif; font-size: 15px; outline: none; transition: border-color 0.2s; box-sizing: border-box; }
.custom-input:focus { border-color: #9a62ff; }
.textarea { resize: vertical; min-height: 70px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 8px; }
.btn-ghost { padding: 12px 24px; border-radius: 14px; background: transparent; border: 1px solid #d5c8ff; font-family: 'Varela Round', sans-serif; font-size: 15px; color: #7c5cbf; cursor: pointer; font-weight: 700; transition: background 0.2s; }
.btn-ghost:hover { background: #f4f0ff; }
.btn-primary { padding: 12px 24px; border-radius: 14px; background: #9a62ff; border: none; font-family: 'Varela Round', sans-serif; font-size: 15px; color: #fff; cursor: pointer; font-weight: 700; transition: background 0.2s; }
.btn-primary:hover:not(:disabled) { background: #8a50ef; }
.btn-primary:disabled { opacity: 0.6; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

/* ── Responsive ── */
@media (max-width: 1100px) {
  .info-panel { display: none; }
}
@media (max-width: 900px) {
  .groups-layout { flex-direction: column; }
  .groups-sidebar { width: 100%; max-height: 180px; flex-direction: row; flex-wrap: wrap; overflow-x: auto; }
  .group-list { flex-direction: row; gap: 8px; }
  .group-card { min-width: 180px; }
}
@media (max-width: 480px) {
  .page-title { font-size: 24px; }
  .page-subtitle { font-size: 13px; }
  .groups-sidebar { padding: 14px; }
}
</style>