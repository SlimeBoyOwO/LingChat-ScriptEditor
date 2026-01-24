<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import EventNode from './EventNode.vue'

const props = defineProps<{
    events: any[]
}>()

const emit = defineEmits(['update:events', 'add-event', 'delete-event'])

// Canvas State
const scale = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const dragStart = { x: 0, y: 0 }

// Node Drag State
const isDraggingNode = ref(false)
const draggedNodeIndex = ref(-1)
const nodeDragOffset = { x: 0, y: 0 }

// Zoom Logic
function handleWheel(e: WheelEvent) {
    if (e.ctrlKey) {
        e.preventDefault()
        const delta = e.deltaY * -0.001
        scale.value = Math.min(Math.max(0.1, scale.value + delta), 3)
    } else {
        // Pan with wheel? Or just scroll?
        // Let's stick to mouse drag for pan
    }
}

const isSpacePressed = ref(false)

window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') isSpacePressed.value = true
})
window.addEventListener('keyup', (e) => {
    if (e.code === 'Space') isSpacePressed.value = false
})

// Canvas Panning
function startPan(e: MouseEvent) {
    if (e.button === 1 || (e.button === 0 && isSpacePressed.value)) { // Middle click or Space+Left
        isPanning.value = true
        dragStart.x = e.clientX - panX.value
        dragStart.y = e.clientY - panY.value
        e.preventDefault()
    }
}

function handleMouseMove(e: MouseEvent) {
    if (isPanning.value) {
        panX.value = e.clientX - dragStart.x
        panY.value = e.clientY - dragStart.y
    } else if (isDraggingNode.value && draggedNodeIndex.value !== -1) {
        const event = props.events[draggedNodeIndex.value]
        // Calculate new position in canvas coordinates
        event.x = (e.clientX - panX.value - nodeDragOffset.x) / scale.value
        event.y = (e.clientY - panY.value - nodeDragOffset.y) / scale.value
    }
}

function stopInteraction() {
    isPanning.value = false
    isDraggingNode.value = false
    draggedNodeIndex.value = -1
}

// Node Dragging
function startDragNode(e: MouseEvent, index: number) {
    if (e.button !== 0) return
    isDraggingNode.value = true
    draggedNodeIndex.value = index
    
    const event = props.events[index]
    // Calculate offset from node top-left to mouse position, scaled
    // We need the screen position of the node to calculate offset correctly
    // But since event.x/y is relative to canvas origin (0,0) + pan, let's reverse calc
    
    // Mouse Screen Pos = Pan + (NodePos * Scale) + Offset
    // Offset = Mouse Screen Pos - Pan - (NodePos * Scale)
    
    nodeDragOffset.x = e.clientX - panX.value - (event.x || 0) * scale.value
    nodeDragOffset.y = e.clientY - panY.value - (event.y || 0) * scale.value
}

// Auto-layout helper if nodes have no coordinates
import { watch } from 'vue'

function layoutNodes() {
    let currentX = 50
    props.events.forEach((event, i) => {
        // If x,y are missing or both 0 (likely default init), layout them
        if (event.x === undefined || event.y === undefined || (event.x === 0 && event.y === 0)) {
             event.x = currentX
             event.y = 100
             currentX += 300 // Horizontal Spacing (Node width 256 + gap)
        }
    })
}

onMounted(() => {
    layoutNodes()
    window.addEventListener('mouseup', stopInteraction)
    window.addEventListener('mousemove', handleMouseMove)
})

watch(() => props.events, () => {
    layoutNodes()
}, { deep: true }) // Deep watch might be expensive but needed if array is replaced or items added without coords

onUnmounted(() => {
    window.removeEventListener('mouseup', stopInteraction)
    window.removeEventListener('mousemove', handleMouseMove)
})

function addEvent(type: string) {
    // Add at center of view
    const x = (-panX.value + window.innerWidth / 2) / scale.value
    const y = (-panY.value + window.innerHeight / 2) / scale.value
    emit('add-event', { type, x, y })
}

</script>

<template>
  <div 
    class="w-full h-full overflow-hidden bg-gray-950 relative cursor-grab active:cursor-grabbing select-none"
    @wheel="handleWheel"
    @mousedown="startPan"
  >
     <!-- Background Grid -->
     <div 
        class="absolute inset-0 pointer-events-none opacity-20"
        :style="{
            backgroundImage: 'radial-gradient(circle, #4b5563 1px, transparent 1px)',
            backgroundSize: `${20 * scale}px ${20 * scale}px`,
            backgroundPosition: `${panX}px ${panY}px`
        }"
     ></div>

     <!-- Canvas Layer -->
     <div 
        class="absolute transform-origin-tl transition-transform duration-75 relative"
        :style="{
            transform: `translate(${panX}px, ${panY}px) scale(${scale})`
        }"
     >
        <!-- Lines Layer -->
        <svg class="absolute top-0 left-0 w-[10000px] h-[10000px] pointer-events-none -z-10 overflow-visible">
            <defs>
                 <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
                 </marker>
            </defs>
            <template v-for="(event, i) in events" :key="'line-' + i">
                 <line 
                    v-if="i < events.length - 1"
                    :x1="(event.x || 0) + 256" 
                    :y1="(event.y || 0) + 20" 
                    :x2="(events[i+1].x || 0)" 
                    :y2="(events[i+1].y || 0) + 20" 
                    stroke="#4b5563" 
                    stroke-width="2" 
                    marker-end="url(#arrowhead)"
                 />
                 <!-- Note: y+20 assumes header height approx center. Node width is w-64 (256px) -->
            </template>
        </svg>

        <EventNode 
            v-for="(event, i) in events" 
            :key="i"
            :event="event"
            :index="i"
            @select="(e: MouseEvent) => startDragNode(e, i)"
            @delete="$emit('delete-event', i)"
        />
     </div>
     
     <!-- Controls Overlay -->
     <div class="absolute bottom-4 right-4 flex space-x-2 z-50">
         <button @click="scale = Math.min(scale + 0.1, 3)" class="bg-gray-800 p-2 rounded text-white">+</button>
         <button @click="scale = 1; panX=0; panY=0" class="bg-gray-800 p-2 rounded text-white text-xs">Reset</button>
         <button @click="scale = Math.max(scale - 0.1, 0.1)" class="bg-gray-800 p-2 rounded text-white">-</button>
     </div>
  </div>
</template>

<style scoped>
.transform-origin-tl {
    transform-origin: 0 0;
}
</style>
