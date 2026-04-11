<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useScriptStore } from '@/stores/script'
import { apiBaseUrl } from '@/config/api'
import { IconChevronDown, IconClose, IconStar, IconImage, IconMusic, IconUser, IconDocument } from '@/assets/icons'

const props = defineProps<{
    modelValue: string
    resourceType: 'background' | 'music' | 'character' | 'sound'
    placeholder?: string
}>()

const emit = defineEmits(['update:modelValue'])

const scriptStore = useScriptStore()
const showDropdown = ref(false)
const searchText = ref('')
const resources = ref<string[]>([])

// Map resource type to asset category
const categoryMap: Record<string, string[]> = {
    background: ['Backgrounds', 'background', 'images'],
    music: ['Musics', 'music', 'bgm'],
    character: ['Characters', 'characters'],
    sound: ['Sounds', 'sound', 'effects']
}

// Default path prefix to strip for each resource type
const defaultPathPrefix: Record<string, string> = {
    background: 'Backgrounds/',
    music: 'Musics/',
    character: '',
    sound: 'Sounds/'
}

// Fetch resources from backend
async function fetchResources() {
    const scriptId = scriptStore.currentScript?.id
    if (!scriptId) return

    try {
        // Fetch characters from dedicated endpoint
        if (props.resourceType === 'character') {
            const res = await fetch(`${apiBaseUrl}/api/scripts/${scriptId}/characters`)
            if (res.ok) {
                const data = await res.json()
                resources.value = data.map((c: any) => c)
            }
        } else {
            // Use assets from store
            const assets = scriptStore.assets
            const categories = categoryMap[props.resourceType] || []
            
            let allResources: string[] = []
            for (const cat of categories) {
                if (assets[cat]) {
                    allResources = [...allResources, ...assets[cat]]
                }
            }
            resources.value = [...new Set(allResources)] // Remove duplicates
        }
    } catch (e) {
        console.error('Failed to fetch resources:', e)
        resources.value = []
    }
}

// Filter resources based on search text
const filteredResources = computed(() => {
    if (!searchText.value) return resources.value
    const search = searchText.value.toLowerCase()
    return resources.value.filter(r => r.toLowerCase().includes(search))
})

// Special options for character type
const specialCharacterOptions = computed(() => {
    if (props.resourceType !== 'character') return []
    return ['MAIN']
})

// Combined resources with special options
const combinedResources = computed(() => {
    return [...specialCharacterOptions.value, ...filteredResources.value]
})

// Get display name from path
function getDisplayName(path: string): string {
    if (!path) return ''
    const parts = path.split('/')
    return parts[parts.length - 1] || path
}

function selectResource(resource: string) {
    // Strip the default path prefix when saving
    const prefix = defaultPathPrefix[props.resourceType] || ''
    let valueToSave = resource
    
    if (prefix && resource.startsWith(prefix)) {
        valueToSave = resource.slice(prefix.length)
    }
    
    emit('update:modelValue', valueToSave)
    showDropdown.value = false
    searchText.value = ''
}

function clearSelection() {
    emit('update:modelValue', '')
}

function toggleDropdown() {
    showDropdown.value = !showDropdown.value
    if (showDropdown.value) {
        fetchResources()
    }
}

// Watch for script changes
watch(() => scriptStore.currentScript?.id, (newId) => {
    if (showDropdown.value && newId) {
        fetchResources()
    }
})

onMounted(() => {
    if (showDropdown.value) {
        fetchResources()
    }
})
</script>

<template>
    <div class="relative" @mousedown.stop>
        <div class="flex items-center gap-1">
            <div 
                class="flex-1 bg-black/30 border border-white/10 rounded p-1.5 text-xs cursor-pointer hover:border-purple-500/30 transition flex items-center justify-between min-h-[28px]"
                @click="toggleDropdown"
            >
                <span v-if="modelValue" class="truncate text-gray-200">{{ getDisplayName(modelValue) }}</span>
                <span v-else class="text-gray-500">{{ placeholder || '选择资源...' }}</span>
                <IconChevronDown class="w-3 h-3 text-gray-400 flex-shrink-0 ml-1" />
            </div>
            <button 
                v-if="modelValue"
                @click="clearSelection"
                class="text-gray-500 hover:text-red-400 transition p-1"
                title="清除选择"
            >
                <IconClose class="w-3 h-3" />
            </button>
        </div>

        <!-- Dropdown -->
        <div 
            v-if="showDropdown"
            class="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 max-h-48 overflow-hidden"
        >
            <!-- Search Input -->
            <div class="p-2 border-b border-gray-700">
                <input 
                    v-model="searchText"
                    type="text"
                    placeholder="搜索..."
                    class="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs focus:outline-none focus:border-purple-500"
                    @mousedown.stop
                />
            </div>

            <!-- Resource List -->
            <div class="overflow-y-auto max-h-32">
                <div v-if="combinedResources.length === 0" class="p-2 text-gray-500 text-xs text-center">
                    没有找到资源
                </div>
                <div 
                    v-for="resource in combinedResources" 
                    :key="resource"
                    @click="selectResource(resource)"
                    class="px-3 py-1.5 text-xs cursor-pointer transition"
                    :class="resource === modelValue ? 'bg-purple-600/30 text-purple-300' : 'text-gray-300 hover:bg-gray-700'"
                >
                    <div class="flex items-center gap-2">
                        <!-- MAIN character special icon -->
                        <IconStar v-if="resourceType === 'character' && resource === 'MAIN'" class="w-3 h-3 text-orange-400 flex-shrink-0" />
                        <IconImage v-else-if="resourceType === 'background'" class="w-3 h-3 text-green-400 flex-shrink-0" />
                        <IconMusic v-else-if="resourceType === 'music'" class="w-3 h-3 text-yellow-400 flex-shrink-0" />
                        <IconUser v-else-if="resourceType === 'character'" class="w-3 h-3 text-blue-400 flex-shrink-0" />
                        <IconDocument v-else class="w-3 h-3 text-gray-400 flex-shrink-0" />
                        <span class="truncate">{{ getDisplayName(resource) }}</span>
                        <span v-if="resource === 'MAIN'" class="text-[10px] text-orange-400/70 ml-1">(默认角色)</span>
                    </div>
                    <div v-if="resource !== getDisplayName(resource) && resource !== 'MAIN'" class="text-[10px] text-gray-500 mt-0.5 ml-5 truncate">
                        {{ resource }}
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="p-2 border-t border-gray-700 bg-gray-900/50">
                <div class="flex items-center justify-between text-[10px] text-gray-500">
                    <span>{{ filteredResources.length }} 个资源</span>
                    <button 
                        @click="showDropdown = false"
                        class="text-gray-400 hover:text-gray-200"
                    >
                        关闭
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>