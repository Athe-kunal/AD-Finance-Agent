import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useModelStore = defineStore('Model', () => {
  const model = ref()

  return { model }
})
