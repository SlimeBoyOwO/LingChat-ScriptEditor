<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useScriptStore } from '@/stores/script'
import ChapterNode from './ChapterNode.vue'

const props = defineProps<{
    scriptId: string
}>()

const scriptStore = useScriptStore()
console.log("scriptStore:", scriptStore);
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

// Expose loaded chapters for parent components to access
const getLoadedChapters = () => loadedChapters.value

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

// Calculate connection paths with proper handle positions
const connectionPaths = computed(() => {
    return connections.value.map(conn => {
        const fromPos = chapterPositions.value[conn.from]
        const toPos = chapterPositions.value[conn.to]
        
        if (!fromPos || !toPos) return null
        
        // Calculate handle positions
        // Right handle: x + 320 (node width) + 10 (handle offset), y + 250 (center)
        const fromX = fromPos.x + 330
        const fromY = fromPos.y + 250
        
        // Left handle: x - 10 (handle offset), y + 250 (center)
        const toX = toPos.x - 10
        const toY = toPos.y + 250
        
        // Calculate control points for bezier curve
        const control1X = fromX + 100
        const control1Y = fromY
        const control2X = toX - 100
        const control2Y = toY
        
        return {
            from: conn.from,
            to: conn.to,
            condition: conn.condition,
            path: `M ${fromX} ${fromY} C ${control1X} ${control1Y}, ${control2X} ${control2Y}, ${toX} ${toY}`,
            conditionX: (fromX + toX) / 2,
            conditionY: (fromY + toY) / 2 - 20
        }
    }).filter(Boolean)
})

const isSpacePressed = ref(false)
const isCreatingConnection = ref(false)
const connectionStartNode = ref<string | null>(null)
const connectionStartSide = ref<'left' | 'right' | null>(null)
const tempConnection = ref<{x1: number, y1: number, x2: number, y2: number} | null>(null)

function onKeyDown(e: KeyboardEvent) {
    if (e.code === 'Space') isSpacePressed.value = true
}

function onKeyUp(e: KeyboardEvent) {
    if (e.code === 'Space') isSpacePressed.value = false
}

function startConnection(e: MouseEvent, path: string, side: 'left' | 'right') {
    if (e.button !== 0) return
    isCreatingConnection.value = true
    connectionStartNode.value = path
    connectionStartSide.value = side
    tempConnection.value = {
        x1: e.clientX,
        y1: e.clientY,
        x2: e.clientX,
        y2: e.clientY
    }
    e.stopPropagation()
}

function handleConnectionMove(e: MouseEvent) {
    if (isCreatingConnection.value && tempConnection.value) {
        tempConnection.value.x2 = e.clientX
        tempConnection.value.y2 = e.clientY
    }
}

function endConnection(e: MouseEvent, path: string, side: 'left' | 'right') {

    if (!isCreatingConnection.value || !connectionStartNode.value || !connectionStartSide.value) {
        isCreatingConnection.value = false
        connectionStartNode.value = null
        connectionStartSide.value = null
        tempConnection.value = null
        return
    }

    if (connectionStartNode.value !== path) {
        // Create connection in scriptStore
        createConnection(connectionStartNode.value, connectionStartSide.value, path, side)
    }
    
    isCreatingConnection.value = false
    connectionStartNode.value = null
    connectionStartSide.value = null
    tempConnection.value = null
    e.stopPropagation()
}

function cancelConnection() {
    isCreatingConnection.value = false
    connectionStartNode.value = null
    connectionStartSide.value = null
    tempConnection.value = null
}

function deleteEvent(chapterPath: string, eventIndex: number) {
    // Find the chapter content
    const chapterContent = loadedChapters.value[chapterPath]
    if (!chapterContent || !chapterContent.events) return

    // Remove the event at the specified index
    chapterContent.events.splice(eventIndex, 1)

    console.log(`Deleted event ${eventIndex} from chapter ${chapterPath}`)
}

function handleRightClick(e: MouseEvent) {
    // Only cancel connection if we're currently creating one
    if (isCreatingConnection.value) {
        e.preventDefault() // Prevent context menu
        cancelConnection()
    }
}

async function createConnection(fromNode: string, fromSide: 'left' | 'right', toNode: string, toSide: 'left' | 'right') {
    try {
        // Find the fromNode content
        const fromContent = loadedChapters.value[fromNode]
        if (!fromContent || !fromContent.events) return

        // Create a new end event
        fromContent.events.push({
            type: 'end',
            next: toNode
        })

        // Save the updated chapter
        await fetch(`/api/scripts/${props.scriptId}/chapters/${encodeURIComponent(fromNode)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(fromContent)
        })

        console.log(`Connected ${fromNode} to ${toNode}`)
        
        // Update the store to reflect the change
        scriptStore.loadChapter(props.scriptId, fromNode)
        
    } catch (error) {
        console.error('Failed to create connection:', error)
    }
}

onMounted(() => {
    loadAllChapters()
    window.addEventListener('mouseup', stopInteraction)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mousemove', handleConnectionMove)
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    window.addEventListener('contextmenu', handleRightClick)
})

onUnmounted(() => {
     window.removeEventListener('mouseup', stopInteraction)
     window.removeEventListener('mousemove', handleMouseMove)
     window.removeEventListener('mousemove', handleConnectionMove)
     window.removeEventListener('keydown', onKeyDown)
     window.removeEventListener('keyup', onKeyUp)
     window.removeEventListener('contextmenu', handleRightClick)
     
     // Clear all data in script store when component is unmounted
     scriptStore.chapters = []
     scriptStore.assets = {}
     scriptStore.currentChapterPath = null
     scriptStore.currentChapterContent = null
     console.log("ChapterFlowCanvas unmounted, cleared script store data")
})

// Expose methods to parent component
defineExpose({
    getLoadedChapters
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
    class="w-full h-full relative overflow-auto cursor-grab active:cursor-grabbing select-none"
    @wheel="handleWheel"
    @mousedown="startPan"
  >

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
            <!-- Existing Connections -->
            <template v-for="(connPath, i) in connectionPaths" :key="i">
                <g v-if="connPath">
                    <path 
                        :d="connPath.path"
                        fill="none"
                        stroke="#f59e0b"
                        stroke-width="3"
                        marker-end="url(#arrowhead-flow)"
                        stroke-dasharray="5,5"
                        opacity="0.8"
                    />
                     <text 
                        v-if="connPath.condition"
                        :x="connPath.conditionX"
                        :y="connPath.conditionY"
                        fill="#fbbf24"
                        text-anchor="middle"
                        font-size="12"
                        font-weight="bold"
                     >{{ connPath.condition }}</text>
                </g>
            </template>
            
            <!-- Temporary Connection Line -->
            <path 
                v-if="tempConnection"
                :d="`M ${tempConnection.x1} ${tempConnection.y1} L ${tempConnection.x2} ${tempConnection.y2}`"
                fill="none"
                stroke="#f59e0b"
                stroke-width="2"
                stroke-dasharray="5,5"
                opacity="0.8"
            />
        </svg>

        <!-- Chapter Nodes -->
        <ChapterNode 
            v-for="(content, path) in loadedChapters"
            :key="path"
            :chapterPath="String(path)"
            :events="content.events"
            :x="chapterPositions[path]?.x || 0"
            :y="chapterPositions[path]?.y || 0"
            @select="(e: MouseEvent) => startDragNode(e, String(path))"
            @add-event="(type) => content.events.push({ type, text: '' })"
            @delete-event="(index: number) => deleteEvent(String(path), index)"
            @swap-events="(oldIndex: number, newIndex: number) => {
                content.events.splice(newIndex, 0, content.events.splice(oldIndex, 1)[0])
            }"
            @start-connection="startConnection"
            @end-connection="endConnection"
        />

    </div>
  </div>
</template>

<style scoped>
.transform-origin-tl { transform-origin: 0 0; }
</style>
