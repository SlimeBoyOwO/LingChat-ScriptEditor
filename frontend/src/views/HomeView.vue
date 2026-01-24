<script setup lang="ts">
import { useScriptStore } from '@/stores/script'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const scriptStore = useScriptStore()
const router = useRouter()

onMounted(() => {
  scriptStore.fetchScripts()
})

function openScript(id: string) {
  router.push(`/editor/${id}`)
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white p-8 font-sans">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-4xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 tracking-tight">
        Script Editor
      </h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="script in scriptStore.scripts" 
          :key="script.id"
          @click="openScript(script.id!)"
          class="bg-gray-800/80 backdrop-blur rounded-xl p-6 cursor-pointer hover:bg-gray-700 transition duration-300 border border-gray-700 hover:border-purple-500 group shadow-lg"
        >
          <h2 class="text-xl font-bold mb-2 group-hover:text-purple-300 transition-colors">{{ script.script_name }}</h2>
          <p class="text-gray-400 text-sm mb-4 line-clamp-2">{{ script.description }}</p>
          <div class="flex items-center justify-between text-xs text-gray-500 mt-auto">
            <span class="bg-gray-900 px-2 py-1 rounded border border-gray-700">Start: {{ script.intro_charpter }}</span>
            <span v-if="script.script_settings?.user_name">Pro: {{ script.script_settings.user_name }}</span>
          </div>
        </div>
        
        <!-- Create New Button -->
        <div class="bg-gray-800/30 rounded-xl p-6 cursor-pointer hover:bg-gray-800 transition border-2 border-dashed border-gray-700 hover:border-gray-500 flex flex-col items-center justify-center text-gray-500 hover:text-gray-300 h-full min-h-[160px]">
          <span class="text-5xl mb-2 font-light">+</span>
          <span class="font-medium">New Script</span>
        </div>
      </div>
    </div>
  </div>
</template>
