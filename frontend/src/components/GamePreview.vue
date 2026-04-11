<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useScriptStore } from '@/stores/script'
import { apiBaseUrl } from '@/config/api'
import { IconPlay, IconRefresh, IconClose, IconWarning, IconDocument } from '@/assets/icons'

const props = defineProps<{
    isOpen: boolean
}>()

const emit = defineEmits(['close'])

const scriptStore = useScriptStore()

// Game State
const isLoading = ref(true)
const error = ref('')
const config = ref<Record<string, any>>({})
const chapters = ref<Record<string, any>>({})
const assets = ref<Record<string, string>>({})
const characters = ref<any[]>([])

const currentChapter = ref<string | null>(null)
const currentEventIndex = ref(0)
const currentBackground = ref('')
const currentCharacters = ref<Record<string, string>>({})
const autoMode = ref(false)
const autoInterval = ref<number | null>(null)

// Choices state
const showChoices = ref(false)
const currentChoices = ref<any[]>([])
const allowFreeInput = ref(false)
const freeInputText = ref('')

const audioContext = ref<AudioContext | null>(null)
const currentAudioSource = ref<AudioBufferSourceNode | null>(null)

// Computed
const currentChapterData = computed(() => {
    if (!currentChapter.value) return null
    return chapters.value[currentChapter.value]
})

const currentEvent = computed(() => {
    if (!currentChapterData.value?.events) return null
    return currentChapterData.value.events[currentEventIndex.value]
})

const speakerName = computed(() => {
    if (!currentEvent.value) return ''
    const event = currentEvent.value
    
    switch (event.type) {
        case 'narration':
            return ''
        case 'player':
            return '玩家'
        case 'dialogue':
        case 'ai_dialogue':
            return findCharacterName(event.character)
        default:
            return ''
    }
})

const dialogueText = computed(() => {
    if (!currentEvent.value) return ''
    const event = currentEvent.value
    
    switch (event.type) {
        case 'narration':
            return event.text || ''
        case 'player':
            return event.text || ''
        case 'dialogue':
            return event.text || ''
        case 'ai_dialogue':
            return '[AI] ' + (event.text || '等待AI生成...')
        case 'input':
            return '[玩家输入] ' + (event.hint || '')
        default:
            return ''
    }
})

const isEndOfChapter = computed(() => {
    return !currentEvent.value && currentChapterData.value
})

const showClickIndicator = computed(() => {
    const event = currentEvent.value
    if (!event) return false
    return ['narration', 'player', 'dialogue', 'ai_dialogue'].includes(event.type)
})

// Methods
function getApiUrl(path: string): string {
    return apiBaseUrl ? `${apiBaseUrl}${path}` : path
}

async function loadGameData() {
    const scriptId = scriptStore.currentScript?.id
    if (!scriptId) return
    
    isLoading.value = true
    error.value = ''
    
    try {
        const response = await fetch(getApiUrl(`/api/preview/${scriptId}/data`))
        if (!response.ok) throw new Error('Failed to load game data')
        
        const data = await response.json()
        config.value = data.config || {}
        chapters.value = data.chapters || {}
        assets.value = data.assets || {}
        characters.value = data.characters || []
        
        // Start with intro chapter
        const introChapter = config.value.intro_chapter
        if (introChapter && chapters.value[introChapter]) {
            currentChapter.value = introChapter || null
        } else {
            const chapterKeys = Object.keys(chapters.value)
            if (chapterKeys.length > 0) {
                currentChapter.value = chapterKeys[0] || null
            }
        }
        
        currentEventIndex.value = 0
        currentCharacters.value = {}
        currentBackground.value = ''
        
        // Process the first event
        processEvent()
        
    } catch (e) {
        error.value = '加载游戏数据失败: ' + (e instanceof Error ? e.message : String(e))
    } finally {
        isLoading.value = false
    }
}

function findCharacterName(charId: string): string {
    if (!charId) return '未知角色'
    // Special handling for MAIN character
    if (charId === 'MAIN') return 'MAIN'
    const char = characters.value.find((c: any) => c.id === charId || c.name === charId)
    return char ? (char.name || char.id) : charId
}

function processEvent() {
    const event = currentEvent.value
    console.log("currentEvent.value:", currentEvent.value);
    if (!event) return
    
    switch (event.type) {
        case 'background':
            setBackground(event.imagePath)
            advanceEvent()
            break
        case 'music':
            console.log('Playing music:', event.musicPath)
            playGameAudio(event.musicPath, event.duration)
            advanceEvent()
            break
        case 'modify_character':
            modifyCharacter(event)
            advanceEvent()
            break
        case 'set_variable':
            advanceEvent()
            break
        case 'choices':
            displayChoices(event)
            break
        case 'chapter_end':
            handleChapterEnd(event)
            break
        case 'end':
            // Legacy support for old 'end' type
            if (event.next && event.next !== 'end') {
                jumpToChapter(event.next)
            }
            break
    }
}

// Chapter end handling
function handleChapterEnd(event: any) {
    switch (event.end_type) {
        case 'linear':
            // Linear: just jump to next chapter
            if (event.next_chapter && event.next_chapter !== 'end') {
                jumpToChapter(event.next_chapter)
            }
            break
        case 'branching':
        case 'ai_judged':
            // Branching/AI judged: show options
            if (event.options && event.options.length > 0) {
                displayChapterEndChoices(event)
            }
            break
        default:
            if (event.next_chapter && event.next_chapter !== 'end') {
                jumpToChapter(event.next_chapter)
            }
    }
}

function displayChapterEndChoices(event: any) {
    currentChoices.value = event.options || []
    allowFreeInput.value = false
    freeInputText.value = ''
    showChoices.value = true
}

// Choices handling
function displayChoices(event: any) {
    currentChoices.value = event.options || []
    allowFreeInput.value = event.allow_free === true || event.allow_free === 'true'
    freeInputText.value = ''
    showChoices.value = true
}

function selectChoice(option: any) {
    showChoices.value = false
    
    // Execute the actions for this choice
    if (option.actions && option.actions.length > 0) {
        for (const action of option.actions) {
            executeAction(action)
        }
    }
    
    // Advance to next event
    advanceEvent()
}

function submitFreeInput() {
    if (!freeInputText.value.trim()) return
    
    showChoices.value = false
    
    // Create a virtual action for the free input
    executeAction({
        type: 'add_line',
        content: freeInputText.value
    })
    
    // Advance to next event
    advanceEvent()
}

function executeAction(action: any) {
    switch (action.type) {
        case 'add_line':
            // For preview, we can log or display the content
            console.log('Action: add_line -', action.content)
            break
        case 'set_variable':
            console.log('Action: set_variable -', action.name, '=', action.content)
            break
        default:
            console.log('Unknown action type:', action.type)
    }
}

// Default path prefixes for different asset types
const defaultPathPrefixes: Record<string, string> = {
    background: 'Backgrounds/',
    music: 'Musics/',
    sound: 'Sounds/'
}

async function playGameAudio(musicPath: string, duration: number) {
    try {
        // Stop any currently playing audio
        if (currentAudioSource.value) {
            try {
                currentAudioSource.value.stop()
            } catch (e) {
                // Ignore errors from already stopped source
            }
            currentAudioSource.value = null
        }
        
        // Get or create AudioContext
        if (!audioContext.value) {
            audioContext.value = new (window.AudioContext || (window as any).webkitAudioContext)()
        }
        
        // Resume AudioContext if it's suspended (browser autoplay policy)
        if (audioContext.value.state === 'suspended') {
            await audioContext.value.resume()
        }
        
        // Build the music URL
        const prefixedPath = defaultPathPrefixes.music + musicPath
        let musicUrl = assets.value[prefixedPath]
        
        // If URL exists in assets map, prefix with apiBaseUrl
        if (musicUrl) {
            musicUrl = getApiUrl(musicUrl)
        } else {
            // Fallback to API endpoint if not in assets map
            const scriptId = scriptStore.currentScript?.id
            musicUrl = getApiUrl(`/api/preview/${scriptId}/assets/${prefixedPath}`)
        }
        
        console.log('Loading music from:', musicUrl)
        
        // Fetch and decode audio
        const response = await fetch(musicUrl)
        if (!response.ok) {
            throw new Error(`Failed to load music: ${response.status}`)
        }
        
        const arrayBuffer = await response.arrayBuffer()
        const audioBuffer = await audioContext.value.decodeAudioData(arrayBuffer)
        
        // Create and configure source
        const source = audioContext.value.createBufferSource()
        source.buffer = audioBuffer
        source.connect(audioContext.value.destination)
        
        // Store reference to stop later
        currentAudioSource.value = source
        
        const startTime = audioContext.value.currentTime
        
        // Handle duration: duration is in seconds, no conversion needed
        // AudioContext uses seconds, not milliseconds
        if (duration > 0) {
            source.start(startTime)
            source.stop(startTime + duration) // duration is already in seconds
        } else {
            // duration is 0 means play until next music event or end
            // Set loop to true for infinite playback
            source.loop = true
            source.start(startTime)
        }
        
        // Clean up reference when audio ends
        source.onended = () => {
            if (currentAudioSource.value === source) {
                currentAudioSource.value = null
            }
        }
        
    } catch (error) {
        console.error('Failed to play audio:', error)
        // Don't throw - just log the error and continue
    }
}


function setBackground(imagePath: string) {
    if (!imagePath) return

    const prefixedPath = defaultPathPrefixes.background + imagePath
    let assetUrl = assets.value[prefixedPath]

    if (assetUrl) {
        // Prefix with apiBaseUrl
        currentBackground.value = getApiUrl(assetUrl)
    } else {
        // Try direct API path with default prefix
        const scriptId = scriptStore.currentScript?.id
        const apiPath = `Backgrounds/${imagePath}`
        currentBackground.value = getApiUrl(`/api/preview/${scriptId}/assets/${apiPath}`)
    }
}



function modifyCharacter(event: any) {
    const action = event.action
    const character = event.character
    const emotion = event.emotion
    
    switch (action) {
        case 'show_character':
            currentCharacters.value[character] = emotion
            console.log("currentCharacters:", currentCharacters.value)
            break
        case 'hide_character':
            delete currentCharacters.value[character]
            break
    }
}

function getCharacterImageUrl(charId: string, emotion: string): string {
    const scriptId = scriptStore.currentScript?.id
    
    // Special handling for MAIN character - use MAIN.png from public folder
    if (charId === 'MAIN') {
        return '/MAIN.png'
    }
    
    const key = `Characters/${charId}/avatar/${emotion}`;
    
    if (assets.value[key]) {
        // Prefix with apiBaseUrl
        return getApiUrl(assets.value[key])
    }
    
    // Fallback to API endpoint
    return getApiUrl(`/api/preview/${scriptId}/character/${encodeURIComponent(charId)}`)
}

function advanceEvent() {
    currentEventIndex.value++
    processEvent()
}

function jumpToChapter(chapterPath: string) {
    if (chapters.value[chapterPath]) {
        currentChapter.value = chapterPath
        currentEventIndex.value = 0
        processEvent()
    }
}

function restartGame() {
    currentEventIndex.value = 0
    currentCharacters.value = {}
    currentBackground.value = ''
    processEvent()
}

function toggleAuto() {
    autoMode.value = !autoMode.value
    if (autoMode.value) {
        autoInterval.value = window.setInterval(() => {
            advanceEvent()
        }, 3000)
    } else {
        if (autoInterval.value) {
            clearInterval(autoInterval.value)
            autoInterval.value = null
        }
    }
}

function handleClick() {
    if (!autoMode.value) {
        advanceEvent()
    }
}

function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && props.isOpen) {
        emit('close')
    } else if ((e.key === 'Space' || e.key === 'Enter') && props.isOpen) {
        advanceEvent()
    }
}

// Watch for panel open
watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        loadGameData()
    } else {
        // Stop auto mode when closing
        if (autoInterval.value) {
            clearInterval(autoInterval.value)
            autoInterval.value = null
            autoMode.value = false
        }
        // Stop any playing audio
        if (currentAudioSource.value) {
            try {
                currentAudioSource.value.stop()
            } catch (e) {}
            currentAudioSource.value = null
        }
    }
})

onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
    if (props.isOpen) {
        loadGameData()
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
    if (autoInterval.value) {
        clearInterval(autoInterval.value)
    }
})
</script>

<template>
    <!-- Backdrop -->
    <div 
        v-if="isOpen"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
        @click="$emit('close')"
    ></div>

    <!-- Popup Container -->
    <div 
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-8 pointer-events-none"
    >
        <div 
            class="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl flex flex-col pointer-events-auto overflow-hidden"
            style="width: 960px; max-width: 90vw; height: 600px; max-height: 85vh;"
            @click.stop
        >
            <!-- Header -->
            <div class="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
                <div class="flex items-center gap-2">
                    <IconPlay class="w-5 h-5 text-purple-400" />
                    <span class="font-bold text-gray-200">游戏预览</span>
                    <span class="text-xs text-gray-500 ml-2">{{ scriptStore.currentScript?.script_name || '' }}</span>
                </div>
                <div class="flex items-center gap-2">
                    <button 
                        @click="loadGameData"
                        class="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded transition"
                        title="刷新预览"
                    >
                        <IconRefresh class="w-4 h-4" />
                        <span>重新开始</span>
                    </button>
                    <button 
                        @click="restartGame"
                        class="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded transition"
                        title="回到章节开始"
                    >
                        <IconRefresh class="w-4 h-4" />
                        <span>重玩本章</span>
                    </button>
                    <button 
                        @click="toggleAuto"
                        class="flex items-center gap-1 px-3 py-1.5 text-xs rounded transition"
                        :class="autoMode ? 'text-purple-400 bg-purple-900/30' : 'text-gray-300 hover:text-white hover:bg-gray-700'"
                        title="自动播放"
                    >
                        <IconPlay class="w-4 h-4" />
                        <span>自动</span>
                    </button>
                    <button 
                        @click="$emit('close')"
                        class="p-1.5 text-gray-400 hover:text-white hover:bg-red-600 rounded transition"
                        title="关闭预览"
                    >
                        <IconClose class="w-5 h-5" />
                    </button>
                </div>
            </div>

            <!-- Game Preview Container -->
            <div 
                class="flex-1 relative overflow-hidden"
                @click="handleClick"
            >
                <!-- Loading -->
                <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-gray-950 z-10">
                    <div class="flex flex-col items-center gap-3">
                        <div class="w-10 h-10 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                        <span class="text-sm text-gray-400">加载游戏数据...</span>
                    </div>
                </div>

                <!-- Error -->
                <div v-else-if="error" class="absolute inset-0 flex items-center justify-center bg-gray-950 z-10 p-8">
                    <div class="bg-red-900/50 border border-red-700 rounded-lg p-4 max-w-md text-center">
                        <IconWarning class="w-12 h-12 text-red-400 mx-auto mb-3" />
                        <p class="text-red-300">{{ error }}</p>
                    </div>
                </div>

                <!-- No Script -->
                <div v-else-if="!scriptStore.currentScript?.id" class="absolute inset-0 flex items-center justify-center bg-gray-950 z-10">
                    <div class="flex flex-col items-center gap-3 text-center p-4">
                        <IconDocument class="w-16 h-16 text-gray-600" />
                        <span class="text-gray-500">请先选择一个脚本</span>
                    </div>
                </div>

                <!-- Game Content -->
                <template v-else>
                    <!-- Background Layer -->
                    <div 
                        class="absolute inset-0 bg-cover bg-center transition-all duration-500"
                        :style="{ 
                            backgroundColor: '#16213e',
                            backgroundImage: currentBackground ? `url(${currentBackground})` : 'none'
                        }"
                    ></div>

                    <!-- Character Layer -->
                    <div class="absolute inset-0 top-0 h-full flex justify-center items-end z-[2]">
                        <div 
                            v-for="(emotion, charId) in currentCharacters" 
                            :key="charId"
                            class="character-container h-full"
                            style="display: flex; justify-content: space-between;"
                        >
                            <img 
                                v-if="emotion"
                                :src="getCharacterImageUrl(charId, emotion)"
                                :alt="findCharacterName(charId)"
                                class="object-contain mx-[2%]"
                                style="user-select: none;"
                                @error="($event.target as HTMLImageElement).style.display = 'none'"
                            />
                        </div>
                    </div>

                    <!-- Dialogue Box -->
                    <div class="absolute bottom-0 left-0 right-0 z-[10]" style="background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 80%, transparent 100%); padding: 20px 40px 30px; user-select: none;">
                        <div 
                            v-if="speakerName"
                            class="text-lg font-bold text-purple-400 mb-2.5 px-4 py-1.5 bg-purple-500/20 rounded inline-block"
                        >
                            {{ speakerName }}
                        </div>
                        <div class="text-base leading-relaxed min-h-[60px]">
                            <template v-if="isEndOfChapter">
                                <span class="text-gray-400">— 章节结束 —</span>
                            </template>
                            <template v-else>
                                {{ dialogueText }}
                            </template>
                        </div>
                    </div>

                    <!-- Click Indicator -->
                    <div 
                        v-if="showClickIndicator && !isEndOfChapter && !showChoices"
                        class="absolute bottom-[220px] right-10 text-white/50 text-sm animate-pulse z-[15]"
                    >
                        点击继续 ▼
                    </div>

                    <!-- Choices Overlay -->
                    <div 
                        v-if="showChoices"
                        class="absolute inset-0 z-[20] flex items-center justify-center"
                        @click.stop
                    >
                        <div class="w-full max-w-lg px-4 space-y-3">
                            <!-- Choice Options -->
                            <div 
                                v-for="(option, index) in currentChoices" 
                                :key="index"
                                @click.stop="selectChoice(option)"
                                class="bg-black-900/10 border rounded-lg px-4 py-3 text-white cursor-pointer hover:bg-cyan-800/10 hover:border-cyan-200 transition-all duration-200 backdrop-blur-sm"
                            >
                                <span class="text-sm">{{ option.text }}</span>
                            </div>
                            
                            <!-- Free Input Option -->
                            <div 
                                v-if="allowFreeInput"
                                class="bg-gray-900/80 border border-gray-500/50 rounded-lg p-3 backdrop-blur-sm"
                            >
                                <div class="flex gap-2">
                                    <input 
                                        v-model="freeInputText"
                                        type="text"
                                        placeholder="输入自定义回复..."
                                        class="flex-1 bg-gray-800/50 border border-gray-600/50 rounded px-3 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500/50"
                                        @click.stop
                                        @keyup.enter="submitFreeInput"
                                    />
                                    <button 
                                        @click.stop="submitFreeInput"
                                        class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded transition"
                                    >
                                        发送
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Footer -->
            <div class="px-4 py-2 bg-gray-800 border-t border-gray-700 flex items-center justify-between text-xs text-gray-500">
                <div class="flex items-center gap-4">
                    <span class="flex items-center gap-1">
                        <span class="w-2 h-2 rounded-full bg-green-500"></span>
                        实时预览
                    </span>
                    <span v-if="Object.keys(chapters).length > 0">{{ Object.keys(chapters).length }} 章节</span>
                    <span v-if="currentChapter">{{ currentChapter }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.animate-spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.animate-pulse {
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}
</style>