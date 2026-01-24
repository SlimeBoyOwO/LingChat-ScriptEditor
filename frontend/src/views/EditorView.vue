<script setup lang="ts">
import { useScriptStore } from '@/stores/script'
import { onMounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import ChapterFlowCanvas from '../components/ChapterFlowCanvas.vue'

const route = useRoute()
const scriptStore = useScriptStore()

onMounted(() => {
  const id = route.params.scriptId as string
  if (id) {
    scriptStore.loadScript(id)
  }
})

function save() {
    // We need a way to save ALL modified chapters. 
    // Currently store only saves 'currentChapterContent'.
    // We should iterate and save all in 'loadedChapters' inside the canvas, 
    // or expose them. For now, let's just trigger a store action if we had one.
    // Since we don't have a bulk save yet, we might need to add it or save individually.
    alert("Save functionality for flow view not fully integrated yet.")
}

</script>

<template>
  <div class="flex h-screen bg-gray-950 text-white overflow-hidden font-sans">
    
    <!-- Main Content (Full Screen Canvas) -->
    <main class="flex-1 flex flex-col relative bg-gray-950 min-w-0">
       <!-- Editor Header -->
       <header class="absolute top-0 left-0 right-0 h-16 pointer-events-none flex items-center px-6 justify-between z-50">
         <div class="bg-gray-900/90 backdrop-blur border border-gray-700 rounded-full px-6 py-2 pointer-events-auto shadow-2xl flex items-center space-x-4">
               <h1 class="font-bold text-lg text-purple-400">{{ scriptStore.currentScript?.script_name || 'Loading...' }}</h1>
               <span class="text-gray-600">|</span>
               <button @click="save" class="text-sm font-medium text-gray-300 hover:text-white transition">Save All</button>
         </div>
       </header>
       
       <div class="flex-1 relative overflow-hidden">
            <template v-if="scriptStore.currentScript?.id">
                 <ChapterFlowCanvas 
                    :scriptId="scriptStore.currentScript.id"
                 />
            </template>
       </div>
    </main>
  </div>
</template>
