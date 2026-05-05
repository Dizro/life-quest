/**
 * Pinia-хранилище авторизации и профиля пользователя.
 *
 * Хранит: токены, профиль пользователя.
 * Предоставляет: login, register, logout, fetchProfile, isLoggedIn.
 *
 * Токены хранятся в localStorage (персистентность между перезагрузками).
 * Профиль обновляется при каждом входе и при явном вызове fetchProfile.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, usersApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
    // ── state ──────────────────────────────────────────────────────────────
    const accessToken = ref(localStorage.getItem('access_token') || null)
    const refreshToken = ref(localStorage.getItem('refresh_token') || null)
    const user = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // ── getters ────────────────────────────────────────────────────────────
    const isLoggedIn = computed(() => !!accessToken.value)
    const displayName = computed(() => user.value?.display_name || user.value?.username || '')
    const userLevel = computed(() => user.value?.level || 1)
    const userXP = computed(() => user.value?.xp || 0)
    const xpToNext = computed(() => user.value?.xp_to_next_level || 100)
    const xpPercentage = computed(() => Math.min(100, Math.round((userXP.value / xpToNext.value) * 100)))
    const streakDays = computed(() => user.value?.streak_days || 0)
    const gold = computed(() => user.value?.gold || 0)
    const crystals = computed(() => user.value?.crystals || 0)

    // ── actions ────────────────────────────────────────────────────────────
    function _saveTokens(data) {
        accessToken.value = data.access_token
        refreshToken.value = data.refresh_token
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
    }

    function _clearTokens() {
        accessToken.value = null
        refreshToken.value = null
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    }

    async function register(username, email, password, displayName) {
        loading.value = true
        error.value = null
        try {
            await authApi.register({ username, email, password, display_name: displayName })
            // Автоматически логинимся после регистрации
            await login(username, password)
        } catch (err) {
            error.value = err?.detail || 'Ошибка регистрации'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function login(username, password) {
        loading.value = true
        error.value = null
        try {
            const data = await authApi.login({ username, password })
            _saveTokens(data)
            await fetchProfile()
        } catch (err) {
            error.value = err?.detail || 'Неверный логин или пароль'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function fetchProfile() {
        try {
            user.value = await usersApi.getMe()
        } catch (err) {
            // Профиль не загрузился — токен мог протухнуть
            if (err?.status === 401) _clearTokens()
        }
    }

    function logout() {
        _clearTokens()
    }

    // При инициализации store пробуем загрузить профиль если есть токен
    if (accessToken.value) {
        fetchProfile()
    }

    return {
        // state
        user,
        loading,
        error,
        accessToken,
        // getters
        isLoggedIn,
        displayName,
        userLevel,
        userXP,
        xpToNext,
        xpPercentage,
        streakDays,
        gold,
        crystals,
        // actions
        register,
        login,
        logout,
        fetchProfile,
    }
})