/**
 * HTTP-клиент для LifeQuest API.
 *
 * Особенности:
 *  - Базовый URL через proxy Vite: /api/v1
 *  - Request interceptor: автоматически добавляет Authorization: Bearer <token>
 *  - Response interceptor: при 401 очищает токены и редиректит на /
 *  - Все методы возвращают data напрямую (не обёрнутый AxiosResponse)
 */

import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api/v1',
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// ── Request interceptor: добавляем токен ──────────────────────────────────
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// ── Response interceptor: обработка 401 с авто-обновлением токена ─────────
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) prom.reject(error)
        else prom.resolve(token)
    })
    failedQueue = []
}

api.interceptors.response.use(
    (response) => response.data,
    async (error) => {
        const originalRequest = error.config
        if (error.response?.status === 401 && !originalRequest._retry) {
            const refreshToken = localStorage.getItem('refresh_token')
            if (!refreshToken) {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/'
                return Promise.reject(error.response?.data || error)
            }

            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                }).then(token => {
                    originalRequest.headers.Authorization = `Bearer ${token}`
                    return api(originalRequest)
                })
            }

            originalRequest._retry = true
            isRefreshing = true

            try {
                const { data } = await axios.post(
                    (import.meta.env.VITE_API_URL || '/api/v1') + '/auth/refresh',
                    { refresh_token: refreshToken },
                    { headers: { 'Content-Type': 'application/json' } }
                )
                localStorage.setItem('access_token', data.access_token)
                localStorage.setItem('refresh_token', data.refresh_token)
                processQueue(null, data.access_token)
                originalRequest.headers.Authorization = `Bearer ${data.access_token}`
                return api(originalRequest)
            } catch (refreshError) {
                processQueue(refreshError, null)
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/'
                return Promise.reject(refreshError)
            } finally {
                isRefreshing = false
            }
        }
        return Promise.reject(error.response?.data || error)
    }
)

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
}

// ── Users / Profile ───────────────────────────────────────────────────────
export const usersApi = {
    getMe: () => api.get('/users/me'),
    updateMe: (data) => api.patch('/users/me', data),
    changePassword: (data) => api.post('/users/me/password', data),
    deleteAccount: () => api.delete('/users/me'),
}

// ── Tasks ─────────────────────────────────────────────────────────────────
export const tasksApi = {
    // ВЕРНУЛИ СЛЭШИ НА МЕСТО! Теперь никаких редиректов и потери токенов.
    getAll: (params = {}) => api.get('/tasks/', { params }),
    create: (data) => api.post('/tasks/', data),
    update: (id, data) => api.patch(`/tasks/${id}`, data),
    delete: (id) => api.delete(`/tasks/${id}`),
    complete: (id) => api.post(`/tasks/${id}/complete`),
    redeem: (id) => api.post(`/tasks/${id}/redeem`),
    habitMinus: (id) => api.post(`/tasks/${id}/habit-minus`),
}

// ── Analytics ─────────────────────────────────────────────────────────────
export const analyticsApi = {
    getDashboard: () => api.get('/analytics/dashboard'),
}

// ── Leaderboards ──────────────────────────────────────────────────────────
export const leaderboardsApi = {
    getWeeklyXp: (limit = 50) => api.get('/leaderboards/weekly-xp', { params: { limit } }),
    getStreak: (limit = 50) => api.get('/leaderboards/streak', { params: { limit } }),
    getCrystals: (limit = 50) => api.get('/leaderboards/crystals', { params: { limit } }),
}

// ── Achievements ──────────────────────────────────────────────────────────
export const achievementsApi = {
    getAll: () => api.get('/achievements/'),
}

// ── Chat (Farrix) ─────────────────────────────────────────────────────────
export const chatApi = {
    send: (message, history = []) => api.post('/chat/', { message, history }),
}

// ── Shop ─────────────────────────────────────────────────────────────────
export const shopApi = {
    buy: (item_id) => api.post('/shop/buy', { item_id }),
}

// ── Groups ───────────────────────────────────────────────────────────────
export const groupsApi = {
    list: () => api.get('/groups/'),
    create: (data) => api.post('/groups/', data),
    get: (id) => api.get(`/groups/${id}`),
    update: (id, data) => api.patch(`/groups/${id}`, data),
    remove: (id) => api.delete(`/groups/${id}`),
    join: (id) => api.post(`/groups/${id}/join`),
    leave: (id) => api.post(`/groups/${id}/leave`),
    getMessages: (id, limit = 50) => api.get(`/groups/${id}/messages?limit=${limit}`),
    sendMessage: (id, text) => api.post(`/groups/${id}/messages`, { text }),
}

// ── Equipment / Inventory ─────────────────────────────────────────────────
export const equipmentApi = {
    getInventory: () => api.get('/equipment/inventory'),
    equip: (data) => api.post('/equipment/equip', data),
}

export default api