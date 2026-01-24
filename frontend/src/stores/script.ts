import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface ScriptConfig {
  id?: string
  script_name: string
  intro_charpter: string
  description?: string
  script_settings?: any
}

export const useScriptStore = defineStore('script', () => {
  const scripts = ref<ScriptConfig[]>([])
  const currentScript = ref<ScriptConfig | null>(null)
  
  // Editor State
  const chapters = ref<string[]>([])
  const assets = ref<any>({})
  const currentChapterPath = ref<string | null>(null)
  const currentChapterContent = ref<any>(null)

  async function fetchScripts() {
    try {
      const res = await axios.get('/api/scripts')
      scripts.value = res.data
    } catch (e) {
      console.error('Failed to fetch scripts', e)
    }
  }

  async function loadScript(id: string) {
      const existing = scripts.value.find(s => s.id === id)
      if (existing) {
          currentScript.value = existing
      }
      try {
          const res = await axios.get(`/api/scripts/${id}`)
          currentScript.value = res.data
      } catch (e) {
          console.error(`Failed to load script ${id}`, e)
      }
      
      // Concurrently load chapters and assets
      await Promise.all([fetchChapters(id), fetchAssets(id)])
  }

  async function fetchChapters(id: string) {
      try {
          const res = await axios.get(`/api/scripts/${id}/chapters`)
          chapters.value = res.data
      } catch (e) {
          console.error("Failed to fetch chapters", e)
      }
  }

  async function fetchAssets(id: string) {
      try {
          const res = await axios.get(`/api/scripts/${id}/assets`)
          assets.value = res.data
      } catch (e) {
           console.error("Failed to fetch assets", e)
      }
  }

  async function loadChapter(scriptId: string, path: string) {
      try {
          const res = await axios.get(`/api/scripts/${scriptId}/chapters/${path}`)
          currentChapterContent.value = res.data
          currentChapterPath.value = path
      } catch (e) {
           console.error("Failed to load chapter", e)
      }
  }
  
  async function saveCurrentChapter() {
      if (!currentScript.value?.id || !currentChapterPath.value || !currentChapterContent.value) return;
      
      try {
          await axios.post(`/api/scripts/${currentScript.value.id}/chapters/${currentChapterPath.value}`, currentChapterContent.value)
          alert("Saved successfully!")
      } catch (e) {
          alert("Failed to save: " + e)
      }
  }

  return { 
      scripts, currentScript, 
      chapters, assets, currentChapterPath, currentChapterContent,
      fetchScripts, loadScript, loadChapter, saveCurrentChapter 
  }
})
