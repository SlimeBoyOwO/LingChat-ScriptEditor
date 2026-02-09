<script setup lang="ts">
import { useScriptStore } from '@/stores/script'
import { onMounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import ChapterFlowCanvas from '../components/ChapterFlowCanvas.vue'

const route = useRoute()
const scriptStore = useScriptStore()

// Reference to ChapterFlowCanvas component
const chapterFlowCanvasRef = ref()

// State for add chapter dialog
const showAddChapterDialog = ref(false)
const newChapterPath = ref('')

onMounted(() => {
  const id = route.params.scriptId as string
  if (id) {
    scriptStore.loadScript(id)
  }
})

async function save() {
    try {
        const scriptId = scriptStore.currentScript?.id
        if (!scriptId) {
            alert('未找到当前脚本')
            return
        }

        // Get loaded chapters from the canvas component
        const loadedChapters = chapterFlowCanvasRef.value?.getLoadedChapters()
        if (!loadedChapters || Object.keys(loadedChapters).length === 0) {
            alert('没有可保存的章节数据')
            return
        }

        let successCount = 0
        let errorCount = 0
        const errors: string[] = []

        // Save each chapter
        for (const [chapterPath, chapterContent] of Object.entries(loadedChapters)) {
            try {
                const response = await fetch(`/api/scripts/${scriptId}/chapters/${encodeURIComponent(chapterPath)}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(chapterContent)
                })

                if (!response.ok) {
                    throw new Error(`保存失败: ${response.status}`)
                }

                successCount++
                console.log(`成功保存章节: ${chapterPath}`)

            } catch (error) {
                errorCount++
                const errorMessage = error instanceof Error ? error.message : String(error)
                errors.push(`章节 ${chapterPath}: ${errorMessage}`)
                console.error(`保存章节失败: ${chapterPath}`, error)
            }
        }

        // Show results
        if (errorCount === 0) {
            alert(`保存成功! 共保存了 ${successCount} 个章节`)
        } else {
            alert(`保存完成，但有错误:\n成功: ${successCount} 个\n失败: ${errorCount} 个\n\n错误详情:\n${errors.join('\n')}`)
        }

    } catch (error) {
        console.error('保存失败:', error)
        const errorMessage = error instanceof Error ? error.message : String(error)
        alert('保存失败: ' + errorMessage)
    }
}

function showAddChapter() {
    showAddChapterDialog.value = true
    newChapterPath.value = ''
}

async function createNewChapter() {
    if (!newChapterPath.value.trim()) {
        alert('请输入章节路径')
        return
    }
    
    try {
        const scriptId = scriptStore.currentScript?.id
        if (!scriptId) {
            alert('未找到当前脚本')
            return
        }
        
        // Create empty chapter structure
        const chapterData = {
            events: []
        }
        
        // Send request to backend API
        const response = await fetch(`/api/scripts/${scriptId}/chapters/${encodeURIComponent(newChapterPath.value)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(chapterData)
        })
        
        if (!response.ok) {
            throw new Error(`创建章节失败: ${response.status}`)
        }
        
        // Reload chapters to include the new one
        await scriptStore.loadScript(scriptId)
        
        // Close dialog
        showAddChapterDialog.value = false
        
        console.log(`成功创建章节: ${newChapterPath.value}`)
        
    } catch (error) {
        console.error('创建章节失败:', error)
        alert('创建章节失败，请检查路径是否正确')
    }
}

function cancelAddChapter() {
    showAddChapterDialog.value = false
    newChapterPath.value = ''
}

</script>

<template>
  <div class="flex h-screen  text-white overflow-hidden font-sans">
    
    <!-- Main Content (Full Screen Canvas) -->
    <main class="flex-1 flex flex-col relative min-w-0">
       <!-- Editor Header -->
       <header class="absolute top-0 left-0 right-0 h-16 pointer-events-none flex items-center px-6 justify-between z-50">
         <div class="bg-gray-900/90 backdrop-blur border border-gray-700 rounded-full px-6 py-2 pointer-events-auto shadow-2xl flex items-center space-x-4">
               <h1 class="font-bold text-lg text-purple-400">{{ scriptStore.currentScript?.script_name || 'Loading...' }}</h1>
               <span class="text-gray-600">|</span>
               <button @click="save" class="text-sm font-medium text-gray-300 hover:text-white transition">全部保存</button>
               <button @click="showAddChapter" class="text-sm font-medium text-purple-300 hover:text-purple-100 transition">+ 新增章节</button>
         </div>
       </header>
       
       <div class="flex-1 relative overflow-hidden">
            <template v-if="scriptStore.currentScript?.id">
                 <ChapterFlowCanvas 
                    ref="chapterFlowCanvasRef"
                    :scriptId="scriptStore.currentScript.id"
                 />
            </template>
       </div>

       <!-- Add Chapter Dialog -->
       <div v-if="showAddChapterDialog" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
           <div class="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-full max-w-md">
               <div class="p-4 border-b border-gray-700">
                   <h3 class="text-lg font-bold text-gray-200">添加新章节</h3>
                   <p class="text-sm text-gray-400 mt-1">请输入章节的YAML文件相对路径</p>
               </div>
               
               <div class="p-4 space-y-4">
                   <div>
                       <label class="block text-sm font-medium text-gray-300 mb-2">章节路径</label>
                       <input 
                           v-model="newChapterPath"
                           type="text"
                           placeholder="例如: chapter1.yaml"
                           class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                           @keyup.enter="createNewChapter"
                       />
                       <p class="text-xs text-gray-500 mt-1">路径将用于创建YAML文件</p>
                   </div>
               </div>
               
               <div class="p-4 border-t border-gray-700 flex justify-end space-x-3">
                   <button 
                       @click="cancelAddChapter"
                       class="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors border border-gray-600 rounded-lg"
                   >
                       取消
                   </button>
                   <button 
                       @click="createNewChapter"
                       class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                   >
                       创建章节
                   </button>
               </div>
           </div>
       </div>
    </main>
  </div>
</template>
