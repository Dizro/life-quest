/**
 * Pinia store for character customization state.
 * Persists selections to localStorage and syncs with backend when possible.
 */

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'lq_character'

function loadFromStorage() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        return raw ? JSON.parse(raw) : {}
    } catch {
        return {}
    }
}

export const useCharacterStore = defineStore('character', () => {
    const saved = loadFromStorage()

    const selectedBody = ref(saved.body || 'body_standard')
    const selectedHair = ref(saved.hair || 'hair_01')
    const selectedTop = ref(saved.top || null)
    const selectedBottom = ref(saved.bottom || null)
    const selectedAccessory = ref(saved.accessory || null)
    const selectedBackground = ref(saved.background || 'bg_sky_clouds')
    const selectedPet = ref(saved.pet || null)
    const selectedItem = ref(saved.item || null)

    const gender = ref(saved.gender || 'neutral') // 'neutral' | 'male' | 'female'

    function persist() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
            body: selectedBody.value,
            hair: selectedHair.value,
            top: selectedTop.value,
            bottom: selectedBottom.value,
            accessory: selectedAccessory.value,
            background: selectedBackground.value,
            pet: selectedPet.value,
            item: selectedItem.value,
            gender: gender.value,
        }))
    }

    watch([selectedBody, selectedHair, selectedTop, selectedBottom,
        selectedAccessory, selectedBackground, selectedPet, selectedItem, gender],
        persist, { immediate: false })

    function resetToDefault() {
        selectedBody.value = 'body_standard'
        selectedHair.value = 'hair_01'
        selectedTop.value = null
        selectedBottom.value = null
        selectedAccessory.value = null
        selectedBackground.value = 'bg_sky_clouds'
        selectedPet.value = null
        selectedItem.value = null
        gender.value = 'neutral'
    }

    return {
        selectedBody,
        selectedHair,
        selectedTop,
        selectedBottom,
        selectedAccessory,
        selectedBackground,
        selectedPet,
        selectedItem,
        gender,
        resetToDefault,
    }
})