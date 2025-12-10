import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const jobId = ref<string | null>(null)
  const overviewCache = ref<any>(null)

  function setJob(id: string) {
    jobId.value = id
  }

  function setOverview(data: any) {
    overviewCache.value = data
  }

  return {
    jobId,
    overviewCache,
    setJob,
    setOverview
  }
})
