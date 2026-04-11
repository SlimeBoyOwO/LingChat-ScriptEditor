<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { apiBaseUrl } from '@/config/api'
import { useScriptStore } from '@/stores/script'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  isOpen: boolean
  scriptId: string
  currentChapterPath?: string | null
  currentChapterContent?: any
  // Event functions passed from parent
  onAddEvent?: (type: string) => void
  onDeleteEvent?: (index: number) => void
  onDeleteChapter?: () => void
  onSwapEvents?: (oldIndex: number, newIndex: number) => void
}>()

const emit = defineEmits(['close', 'chapterModified'])

// Helper function to get full API URL
function getApiUrl(path: string): string {
  return apiBaseUrl ? `${apiBaseUrl}${path}` : path
}

// Handle chapter modification - save directly to YAML file
async function handleChapterModified(content: any) {
  debugger
  if (props.currentChapterPath) {
    try {
      const res = await fetch(getApiUrl(`/api/scripts/${props.scriptId}/chapters/${encodeURIComponent(props.currentChapterPath)}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(content)
      })
      
      if (!res.ok) throw new Error(`Status ${res.status}`)
      console.log(`[AIEditor] Saved chapter to YAML: ${props.currentChapterPath}`)
      toast.success('章节已更新')
    } catch (error) {
      console.error('[AIEditor] Failed to save chapter:', error)
      toast.error('保存章节失败')
    }
  }
}

const toast = useToast()
const scriptStore = useScriptStore()



// Configuration state
const config = ref({
  apiKey: localStorage.getItem('agent_api_key') || '',
  apiBase: localStorage.getItem('agent_api_base') || 'https://api.openai.com/v1',
  model: localStorage.getItem('agent_model') || 'gpt-4o-mini'
})

const showConfig = ref(!config.value.apiKey)
const configSaving = ref(false)
const configStatus = ref<'idle' | 'success' | 'error'>('idle')

// Chat state
const messages = ref<{role: 'user' | 'assistant', content: string}[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

// Tool results from last response
const lastToolResults = ref<any[]>([])

// Computed
const isConfigured = computed(() => !!config.value.apiKey)

// Current script context - use props from parent (EditorView)
const currentScriptId = computed(() => scriptStore.currentScript?.id)
const chapterPath = computed(() => props.currentChapterPath)
const chapterContent = computed(() => props.currentChapterContent)
const characters = computed(() => {
  const chars = scriptStore.assets?.Characters
  if (chars && Object.keys(chars).length > 0) {
    return Object.keys(chars)
  }
  return []
})
const assets = computed(() => scriptStore.assets || {})

// Debug log
console.log('[AIEditor] characters computed:', characters.value)
console.log('[AIEditor] scriptStore.assets:', scriptStore.assets)


// Save configuration
async function saveConfig() {
  if (!config.value.apiKey.trim()) {
    toast.error('请输入 API Key')
    return
  }
  
  configSaving.value = true
  try {
    const response = await fetch(`${apiBaseUrl}/api/agent/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_key: config.value.apiKey,
        api_base: config.value.apiBase || 'https://api.openai.com/v1',
        model: config.value.model || 'gpt-4o-mini'
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    // Save to localStorage
    localStorage.setItem('agent_api_key', config.value.apiKey)
    localStorage.setItem('agent_api_base', config.value.apiBase)
    localStorage.setItem('agent_model', config.value.model)
    
    configStatus.value = 'success'
    showConfig.value = false
    toast.success('配置已保存')
  } catch (error) {
    configStatus.value = 'error'
    toast.error('配置失败: ' + (error as Error).message)
  } finally {
    configSaving.value = false
  }
}

// Send message
async function sendMessage() {
  if (!inputMessage.value.trim() || isLoading.value) return
  if (!isConfigured.value) {
    showConfig.value = true
    toast.warning('请先配置 API Key')
    return
  }

  console.log("scriptStore", scriptStore);
  console.log("chapterPath.value", chapterPath.value);

  if (!currentScriptId.value || !chapterPath.value) {
    toast.warning('请先选择一个章节')
    return
  }
  
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  
  // Add user message
  messages.value.push({ role: 'user', content: userMessage })
  isLoading.value = true
  
  try {
    const response = await fetch(`${apiBaseUrl}/api/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: messages.value,
        script_id: currentScriptId.value,
        chapter_path: chapterPath.value,
        chapter_content: chapterContent.value,
        characters: characters.value,
        assets: assets.value
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success && data.content) {
      messages.value.push({ role: 'assistant', content: data.content })
    } else if (data.error) {
      messages.value.push({ role: 'assistant', content: `错误: ${data.error}` })
    }
    
// Store tool results
    lastToolResults.value = data.tool_results || []
    
    // Execute frontend tool handlers
    if (data.tool_results && data.tool_results.length > 0) {
      await executeToolResults(data.tool_results, data.modified_chapter)
    }
    
  } catch (error) {
    const errorMessage = (error as Error).message
    messages.value.push({ role: 'assistant', content: `请求失败: ${errorMessage}` })
    toast.error('请求失败: ' + errorMessage)
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// Scroll chat to bottom
function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// Clear chat history
function clearChat() {
  messages.value = []
  lastToolResults.value = []
}

// Handle key events
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// Toggle config visibility
function toggleConfig() {
  showConfig.value = !showConfig.value
}

// Format tool result for display
function formatToolResult(result: any): string {
  if (result.error) {
    return `❌ 错误: ${result.error}`
  }
  if (result.result) {
    return JSON.stringify(result.result, null, 2)
  }
  return JSON.stringify(result, null, 2)
}

// Frontend tool executor - parses and executes tool results
async function executeToolResults(toolResults: any[], modifiedChapter: any) {

  if (modifiedChapter) {
    await handleChapterModified(modifiedChapter)
    // Emit event to notify parent to reload chapters
    emit('chapterModified', modifiedChapter)
  }

  // TODO: current use replace content directly , can use function calling in future

  // for (const result of toolResults) {
  //   const functionName = result.function_name
  //   const functionResult = result.result
    

  //   // Skip if there was an error
  //   if (result.error) {
  //     console.warn(`[AIEditor] Tool ${functionName} had error:`, result.error)
  //     continue
  //   }

      
    
    // try {
    //   switch (functionName) {
    //     case 'append_event': {
    //       // Event was appended by AI with full content - just notify success
    //       // The modifiedChapter already contains the new event with all its data
    //       if (functionResult?.success) {
    //         const eventIndex = functionResult.total_events - 1
    //         const events = modifiedChapter?.events || []
    //         const newEvent = events[eventIndex]
    //         if (newEvent) {
    //           toast.success(`已添加事件: ${newEvent.type}`)
    //         }
    //       }
    //       break
    //     }
        
    //     case 'insert_event': {
    //       // Event was inserted by AI with full content
    //       if (functionResult?.success && functionResult.index !== undefined) {
    //         const eventIndex = functionResult.index
    //         const events = modifiedChapter?.events || []
    //         const newEvent = events[eventIndex]
    //         if (newEvent) {
    //           toast.success(`已在位置 ${eventIndex} 插入事件: ${newEvent.type}`)
    //         }
    //       }
    //       break
    //     }
        
    //     case 'update_event': {
    //       // Event was updated by AI
    //       if (functionResult?.success && functionResult.index !== undefined) {
    //         const eventIndex = functionResult.index
    //         toast.success(`已更新位置 ${eventIndex} 的事件`)
    //       }
    //       break
    //     }
        
    //     case 'delete_event': {
    //       // Event was deleted by AI
    //       if (functionResult?.success && functionResult.deleted_index !== undefined) {
    //         toast.success('已删除事件')
    //       }
    //       break
    //     }
        
    //     case 'list_characters':
    //     case 'list_assets':
    //     case 'get_chapter':
    //       // Read-only operations - no frontend action needed
    //       console.log(`[AIEditor] ${functionName} result:`, functionResult)
    //       break
        
    //     default:
    //       console.log(`[AIEditor] Unknown function: ${functionName}`)
    //   }
    // } catch (err) {
    //   console.error(`[AIEditor] Error executing ${functionName}:`, err)
    //   toast.error(`执行 ${functionName} 时出错`)
    // }
      // Always notify parent of chapter modification
}

onMounted(() => {
  // Check if config is already saved
  if (config.value.apiKey) {
    showConfig.value = false
  }
})
</script>

<template>
  <Transition name="slide">
    <div v-if="isOpen" class="ai-editor-sidebar">
      <!-- Header -->
      <div class="ai-header">
        <h2 class="ai-title">
          <img width="20px" height="20px" src="/小猫.png" />
          小猫AI
        </h2>
        <div class="ai-header-actions">
          <button @click="toggleConfig" class="config-btn" :class="{ 'active': showConfig }" title="设置">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.427l-1.003.792c-.292.23-.426.587-.379.953.014.107.02.215.02.323v.854c0 .108-.006.216-.02.323-.047.366.087.723.38.953l1.002.792c.425.336.474.963.26 1.427l-1.297 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124-.073.044-.146.087-.22.127-.332.184-.581.496-.644.87l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.427l1.003-.792c.292-.23.426-.587.379-.953a6.093 6.093 0 01-.02-.323v-.854c0-.108.006-.216.02-.323.047-.366-.087-.723-.379-.953l-1.002-.792a1.125 1.125 0 01-.26-1.427l1.297-2.247a1.125 1.125 0 011.37-.49l1.217.456c.355.133.75.072 1.075-.124.074-.044.148-.087.22-.127.332-.184.582-.496.645-.87l.213-1.281z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <button @click="emit('close')" class="close-btn" title="关闭">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Configuration Panel -->
      <Transition name="collapse">
        <div v-if="showConfig" class="config-panel">
          <div class="config-section">
            <h3 class="config-title">API 配置</h3>
            
            <div class="config-field">
              <label>API Key</label>
              <input 
                v-model="config.apiKey" 
                type="password" 
                placeholder="sk-..."
                class="config-input"
              />
            </div>
            
            <div class="config-field">
              <label>API Base URL</label>
              <input 
                v-model="config.apiBase" 
                type="text" 
                placeholder="https://api.openai.com/v1"
                class="config-input"
              />
              <p class="config-hint">支持 OpenAI 兼容的 API 端点</p>
            </div>
            
            <div class="config-field">
              <label>模型</label>
              <input 
                v-model="config.model" 
                type="text" 
                placeholder="gpt-4o-mini"
                class="config-input"
              />
            </div>
            
            <button 
              @click="saveConfig" 
              class="save-config-btn"
              :disabled="configSaving"
            >
              {{ configSaving ? '保存中...' : '保存配置' }}
            </button>
            
            <div v-if="configStatus === 'success'" class="config-status success">
              ✓ 配置成功
            </div>
            <div v-else-if="configStatus === 'error'" class="config-status error">
              ✗ 配置失败
            </div>
          </div>
        </div>
      </Transition>

      <!-- Chat Area -->
      <div class="chat-area">
        <!-- Messages -->
        <div ref="chatContainer" class="messages-container">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">🐈</div>
            <p>我是剧本写作助手，可以帮你创建和编辑剧本事件。</p>
            <p class="empty-hint">试试说："添加一段叙述：天空开始下起小雨"</p>
          </div>
          
          <div v-for="(message, index) in messages" :key="index" 
               class="message" 
               :class="message.role">
            <div class="message-avatar">
              {{ message.role === 'user' ? '🧑' : '🐈' }}
            </div>
            <div class="message-content">
              <div class="message-text" v-html="message.content.replace(/\n/g, '<br>')"></div>
              
              <!-- Tool results display -->
              <div v-if="message.role === 'assistant' && lastToolResults.length > 0 && index === messages.length - 1" 
                   class="tool-results">
                <details>
                  <summary>工具调用详情 ({{ lastToolResults.length }})</summary>
                  <div class="tool-result-list">
                    <div v-for="(result, i) in lastToolResults" :key="i" class="tool-result-item">
                      <span class="tool-name">{{ result.function_name }}</span>
                      <pre class="tool-output">{{ formatToolResult(result) }}</pre>
                    </div>
                  </div>
                </details>
              </div>
            </div>
          </div>
          
          <div v-if="isLoading" class="message assistant">
            <div class="message-avatar">🐈</div>
            <div class="message-content">
              <div class="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Input Area -->
        <div class="input-area">
          <textarea 
            v-model="inputMessage"
            @keydown="handleKeydown"
            placeholder="输入消息... (Enter 发送)"
            :disabled="isLoading"
            rows="3"
            class="message-input"
          ></textarea>
          <div class="input-actions">
            <button @click="clearChat" class="clear-btn" :disabled="messages.length === 0">
              清空
            </button>
            <button @click="sendMessage" class="send-btn" :disabled="!inputMessage.trim() || isLoading">
              {{ isLoading ? '发送中...' : '发送' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Context Info -->
      <div class="context-info">
        <div v-if="currentScriptId && chapterPath" class="context-active">
          <span class="context-label">当前章节:</span>
          <span class="context-value">{{ chapterPath }}</span>
        </div>
        <div v-else class="context-inactive">
          ⚠️ 请先选择一个章节
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.ai-editor-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: #1a1a2e;
  border-left: 1px solid #2a2a4e;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
}

/* Header */
.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #2a2a4e;
  background: #16162e;
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #a78bfa;
  margin: 0;
}

.ai-header-actions {
  display: flex;
  gap: 8px;
}

.config-btn, .close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.config-btn {
  background: transparent;
  color: #9ca3af;
}

.config-btn:hover {
  background: #2a2a4e;
  color: #a78bfa;
}

.config-btn.active {
  background: #4c1d95;
  color: white;
}

.close-btn {
  background: transparent;
  color: #9ca3af;
}

.close-btn:hover {
  background: #dc2626;
  color: white;
}

/* Config Panel */
.config-panel {
  padding: 16px;
  border-bottom: 1px solid #2a2a4e;
  background: #1e1e3e;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-title {
  font-size: 14px;
  font-weight: 600;
  color: #9ca3af;
  margin: 0;
}

.config-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-field label {
  font-size: 12px;
  color: #9ca3af;
}

.config-input {
  background: #2a2a4e;
  border: 1px solid #3a3a5e;
  border-radius: 6px;
  padding: 8px 12px;
  color: white;
  font-size: 14px;
  transition: border-color 0.2s;
}

.config-input:focus {
  outline: none;
  border-color: #a78bfa;
}

.config-input::placeholder {
  color: #6b7280;
}

.config-hint {
  font-size: 11px;
  color: #6b7280;
  margin: 0;
}

.save-config-btn {
  padding: 10px 16px;
  background: #7c3aed;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
}

.save-config-btn:hover:not(:disabled) {
  background: #6d28d9;
}

.save-config-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.config-status {
  font-size: 12px;
  padding: 8px;
  border-radius: 4px;
}

.config-status.success {
  background: #065f46;
  color: #34d399;
}

.config-status.error {
  background: #7f1d1d;
  color: #f87171;
}

/* Chat Area */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-hint {
  font-size: 12px;
  color: #4b5563;
  margin-top: 12px;
  padding: 8px 12px;
  background: #2a2a4e;
  border-radius: 6px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 100%;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #2a2a4e;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background: #4c1d95;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  background: #2a2a4e;
  border-radius: 12px;
  padding: 12px;
  color: #e5e7eb;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .message-text {
  background: #4c1d95;
  border-radius: 12px 12px 0 12px;
}

.message.assistant .message-text {
  border-radius: 12px 12px 12px 0;
}

.tool-results {
  margin-top: 8px;
}

.tool-results summary {
  font-size: 12px;
  color: #9ca3af;
  cursor: pointer;
}

.tool-results[open] summary {
  margin-bottom: 8px;
}

.tool-result-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-result-item {
  background: #1e1e3e;
  border-radius: 6px;
  padding: 8px;
}

.tool-name {
  font-size: 12px;
  font-weight: 600;
  color: #a78bfa;
  display: block;
  margin-bottom: 4px;
}

.tool-output {
  font-size: 11px;
  color: #9ca3af;
  background: #16162e;
  padding: 6px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 12px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #a78bfa;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
.loading-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Input Area */
.input-area {
  padding: 12px 16px;
  border-top: 1px solid #2a2a4e;
  background: #16162e;
}

.message-input {
  width: 100%;
  background: #2a2a4e;
  border: 1px solid #3a3a5e;
  border-radius: 8px;
  padding: 12px;
  color: white;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #a78bfa;
}

.message-input::placeholder {
  color: #6b7280;
}

.message-input:disabled {
  opacity: 0.5;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.clear-btn {
  padding: 8px 16px;
  background: transparent;
  color: #9ca3af;
  border: 1px solid #3a3a5e;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.clear-btn:hover:not(:disabled) {
  background: #2a2a4e;
  color: white;
}

.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  padding: 8px 16px;
  background: #7c3aed;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #6d28d9;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Context Info */
.context-info {
  padding: 8px 16px;
  border-top: 1px solid #2a2a4e;
  font-size: 12px;
}

.context-active {
  display: flex;
  align-items: center;
  gap: 6px;
}

.context-label {
  color: #6b7280;
}

.context-value {
  color: #a78bfa;
}

.context-inactive {
  color: #f59e0b;
}

/* Animations */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  max-height: 400px;
}
</style>