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
    baseURL: '/api/v1',
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

// ── Response interceptor: обработка 401 ──────────────────────────────────
api.interceptors.response.use(
    (response) => response.data,
    async (error) => {
        if (error.response?.status === 401) {
            // Токен истёк — очищаем локальное хранилище и перенаправляем на вход
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/'
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

// ── Equipment / Inventory ─────────────────────────────────────────────────
export const equipmentApi = {
    getInventory: () => api.get('/equipment/inventory'),
    equip: (data) => api.post('/equipment/equip', data),
}

export default api