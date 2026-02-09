<script setup lang="ts">
import { useScriptStore } from '@/stores/script'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const scriptStore = useScriptStore()
const router = useRouter()

// State for create script dialog
const showCreateDialog = ref(false)
const newScriptName = ref('')
const newScriptDescription = ref('')
const newScriptUserName = ref('')
const newScriptUserSubtitle = ref('')
const newScriptIntroChapter = ref('')

onMounted(() => {
  scriptStore.fetchScripts()
})

function openScript(id: string) {
  router.push(`/editor/${id}`)
}

function showCreateScript() {
  showCreateDialog.value = true
  newScriptName.value = ''
  newScriptDescription.value = ''
}

async function createNewScript() {
  if (!newScriptName.value.trim()) {
    alert('请输入故事名称')
    return
  }
  
  try {
    // Send request to backend API with all required parameters
    const response = await scriptStore.createScript(
      newScriptName.value.trim(),
      newScriptDescription.value,
      newScriptUserName.value,
      newScriptUserSubtitle.value,
      newScriptIntroChapter.value
    )

    console.log("response:", response)

    if (response.status !== "success") {
      throw new Error(`创建脚本失败: ${response.status}`)
    }
    
    // Reload scripts to include the new one
    await scriptStore.fetchScripts()
    
    // Close dialog
    showCreateDialog.value = false
    
    console.log(`成功创建脚本: ${newScriptName.value}`)
    
  } catch (error) {
    console.error('创建脚本失败:', error)
    alert('创建脚本失败，请稍后重试')
  }
}

function cancelCreateScript() {
  showCreateDialog.value = false
  newScriptName.value = ''
  newScriptDescription.value = ''
}
</script>

<template>
  <div class="min-h-screen text-white p-8 font-sans relative z-1">
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
        <div 
          @click="showCreateScript"
          class="bg-gray-800/30 rounded-xl p-6 cursor-pointer hover:bg-gray-800 transition border-2 border-dashed border-gray-700 hover:border-purple-500 flex flex-col items-center justify-center text-gray-500 hover:text-gray-300 h-full min-h-[160px] group"
        >
          <span class="text-5xl mb-2 font-light group-hover:text-purple-400 transition-colors">+</span>
          <span class="font-medium group-hover:text-purple-300 transition-colors">New Script</span>
        </div>
      </div>
    </div>

    <!-- Create Script Dialog -->
    <div v-if="showCreateDialog" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-full max-w-md">
            <div class="p-4 border-b border-gray-700">
                <h3 class="text-lg font-bold text-gray-200">创建新脚本</h3>
            </div>
            
            <div class="p-4 space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">故事名称</label>
                    <input 
                        v-model="newScriptName"
                        type="text"
                        placeholder="例如: 小灵的冒险故事"
                        class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                        @keyup.enter="createNewScript"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">故事描述</label>
                    <input 
                        v-model="newScriptDescription"
                        type="text"
                        placeholder="例如: 这是一个简简单单的小剧本"
                        class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                        @keyup.enter="createNewScript"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">用户名称</label>
                    <input 
                        v-model="newScriptUserName"
                        type="text"
                        placeholder="例如: 钦灵"
                        class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                        @keyup.enter="createNewScript"
                    />
                </div>
        <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">用户副标题</label>
            <input 
                v-model="newScriptUserSubtitle"
                type="text"
                placeholder="例如: LingChat Studio"
                class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                @keyup.enter="createNewScript"
            />
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">开场章节</label>
            <input 
                v-model="newScriptIntroChapter"
                type="text"
                placeholder="例如: Intro/intro"
                class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                @keyup.enter="createNewScript"
            />
        </div>
            </div>
            
            <div class="p-4 border-t border-gray-700 flex justify-end space-x-3">
                <button 
                    @click="cancelCreateScript"
                    class="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors border border-gray-600 rounded-lg"
                >
                    取消
                </button>
                <button 
                    @click="createNewScript"
                    class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                    创建脚本
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

