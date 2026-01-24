<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useScriptStore } from '@/stores/script'
import ChapterNode from './ChapterNode.vue'

const props = defineProps<{
    scriptId: string
}>()

const scriptStore = useScriptStore()
const scale = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const dragStart = { x: 0, y: 0 }
const isDraggingNode = ref(false)
const draggedNodePath = ref<string | null>(null)
const nodeDragOffset = { x: 0, y: 0 }

const loadedChapters = ref<Record<string, any>>({})
const chapterPositions = ref<Record<string, {x: number, y: number}>>({})

// Helper to load all chapters
async function loadAllChapters() {
    console.log("Loading chapters list:", scriptStore.chapters)
    if (!scriptStore.chapters || scriptStore.chapters.length === 0) {
        console.warn("No chapters found in store.")
        return
    }
    
    for (const path of scriptStore.chapters) {
        // Ensure path is treated consistently (string)
        const chapterPath = String(path)
        
        if (!loadedChapters.value[chapterPath]) {
             try {
                 // Note: encodeURIComponent handles special chars, but for :path param, 
                 // standard practice depends on server. We keep it as is.
                 const res = await fetch(`/api/scripts/${props.scriptId}/chapters/${encodeURIComponent(chapterPath)}`)
                 if (!res.ok) throw new Error(`Status ${res.status}`)
                 const data = await res.json()
                 console.log("Loaded chapter:", chapterPath, data)
                 loadedChapters.value[chapterPath] = data
             } catch (e) {
                 console.error("Failed to load chapter", chapterPath, e)
             }
        }
        
        // Init position if not exists
        if (!chapterPositions.value[chapterPath]) {
            chapterPositions.value[chapterPath] = { x: 0, y: 0 } 
        }
    }
    autoLayout()
}

// Watch for store changes to ensure we load when data arrives
watch(() => scriptStore.chapters, (newVal) => {
    if (newVal && newVal.length > 0) {
         loadAllChapters()
    }
}, { immediate: true, deep: true })

function autoLayout() {
    let col = 0
    let row = 0
    const GAP_X = 400
    const GAP_Y = 500
    const COLS = 4
    
    scriptStore.chapters.forEach(path => {
        if (!chapterPositions.value[path]) {
             chapterPositions.value[path] = { x: 0, y: 0 }
        }
        
        if (chapterPositions.value[path].x === 0 && chapterPositions.value[path].y === 0) {
            chapterPositions.value[path].x = col * GAP_X + 50
            chapterPositions.value[path].y = row * GAP_Y + 50
            col++
            if (col >= COLS) {
                col = 0
                row++
            }
        }
    })
}

// Calculate Connections
interface Connection {
    from: string
    to: string
    condition?: string
}

const connections = computed(() => {
    const conns: Connection[] = []
    
    for (const [path, content] of Object.entries(loadedChapters.value)) {
        if (!content.events) continue
        
        content.events.forEach((event: any) => {
            if (event.type === 'end' && event.next) {
                if (event.next !== 'end') {
                     conns.push({
                         from: path,
                         to: event.next,
                         condition: event.condition
                     })
                }
            }
        })
    }
    return conns
})

const isSpacePressed = ref(false)

function onKeyDown(e: KeyboardEvent) {
    if (e.code === 'Space') isSpacePressed.value = true
}

function onKeyUp(e: KeyboardEvent) {
    if (e.code === 'Space') isSpacePressed.value = false
}

onMounted(() => {
    loadAllChapters()
    window.addEventListener('mouseup', stopInteraction)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
})

onUnmounted(() => {
     window.removeEventListener('mouseup', stopInteraction)
     window.removeEventListener('mousemove', handleMouseMove)
     window.removeEventListener('keydown', onKeyDown)
     window.removeEventListener('keyup', onKeyUp)
})

function handleWheel(e: WheelEvent) {
    if (e.ctrlKey) {
        e.preventDefault()
        scale.value = Math.min(Math.max(0.1, scale.value + e.deltaY * -0.001), 2)
    }
}

function startPan(e: MouseEvent) {
    if (e.button === 1 || (e.button === 0 && isSpacePressed.value)) {
        isPanning.value = true
        dragStart.x = e.clientX - panX.value
        dragStart.y = e.clientY - panY.value
        e.preventDefault()
    }
}

function startDragNode(e: MouseEvent, path: string) {
    if (e.button !== 0 || isSpacePressed.value) return
    const pos = chapterPositions.value[path]
    if (!pos) return
    
    isDraggingNode.value = true
    draggedNodePath.value = path
    nodeDragOffset.x = e.clientX - panX.value - (pos.x * scale.value)
    nodeDragOffset.y = e.clientY - panY.value - (pos.y * scale.value)
}

function handleMouseMove(e: MouseEvent) {
    if (isPanning.value) {
        panX.value = e.clientX - dragStart.x
        panY.value = e.clientY - dragStart.y
    } else if (isDraggingNode.value && draggedNodePath.value) {
        const pos = chapterPositions.value[draggedNodePath.value]
        if (pos) {
            pos.x = (e.clientX - panX.value - nodeDragOffset.x) / scale.value
            pos.y = (e.clientY - panY.value - nodeDragOffset.y) / scale.value
        }
    }
}

function stopInteraction() {
    isPanning.value = false
    isDraggingNode.value = false
    draggedNodePath.value = null
}
</script>

<template>
  <div 
    class="w-full h-full bg-gray-950 relative overflow-hidden cursor-grab active:cursor-grabbing select-none"
    @wheel="handleWheel"
    @mousedown="startPan"
  >
    <!-- Background -->
    <div 
        class="absolute inset-0 opacity-20 pointer-events-none"
        :style="{
            backgroundImage: 'radial-gradient(circle, #4b5563 1px, transparent 1px)',
            backgroundSize: `${40 * scale}px ${40 * scale}px`,
            backgroundPosition: `${panX}px ${panY}px`
        }"
    ></div>

    <!-- Canvas -->
    <div 
        class="absolute transform-origin-tl"
        :style="{ transform: `translate(${panX}px, ${panY}px) scale(${scale})` }"
    >
        <!-- Connections -->
        <svg class="absolute top-0 left-0 w-[50000px] h-[50000px] pointer-events-none -z-10 overflow-visible">
            <defs>
                 <marker id="arrowhead-flow" markerWidth="12" markerHeight="10" refX="11" refY="5" orient="auto">
                    <polygon points="0 0, 12 5, 0 10" fill="#a855f7" />
                 </marker>
            </defs>
            <template v-for="(conn, i) in connections" :key="i">
                <g v-if="chapterPositions[conn.from] && chapterPositions[conn.to]">
                     <!-- Bezier Curve from Right Center to Left Center -->
                     <path 
                        :d="`M ${chapterPositions[conn.from].x + 320} ${chapterPositions[conn.from].y + 100} 
                             C ${chapterPositions[conn.from].x + 420} ${chapterPositions[conn.from].y + 100},
                               ${chapterPositions[conn.to].x - 100} ${chapterPositions[conn.to].y + 100},
                               ${chapterPositions[conn.to].x} ${chapterPositions[conn.to].y + 100}`"
                        fill="none"
                        stroke="#a855f7"
                        stroke-width="3"
                        marker-end="url(#arrowhead-flow)"
                        stroke-opacity="0.6"
                     />
                     <text 
                        v-if="conn.condition"
                        :x="(chapterPositions[conn.from].x + 320 + chapterPositions[conn.to].x) / 2"
                        :y="(chapterPositions[conn.from].y + 100 + chapterPositions[conn.to].y + 100) / 2 - 10"
                        fill="#fbbf24"
                        text-anchor="middle"
                        font-size="12"
                        font-weight="bold"
                     >{{ conn.condition }}</text>
                </g>
            </template>
        </svg>

        <!-- Chapter Nodes -->
        <ChapterNode 
            v-for="(content, path) in loadedChapters"
            :key="path"
            :chapterPath="String(path)"
            :events="content.events"
            :x="chapterPositions[path]?.x"
            :y="chapterPositions[path]?.y"
            @select="(e: MouseEvent) => startDragNode(e, String(path))"
            @add-event="content.events.push({ type: 'narration', text: '' })"
        />

    </div>
  </div>
</template>

<style scoped>
.transform-origin-tl { transform-origin: 0 0; }
</style>
