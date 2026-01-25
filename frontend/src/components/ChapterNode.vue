<script setup lang="ts">
import { computed, ref } from 'vue'
import draggable from 'vuedraggable'
import { EVENT_SCHEMAS } from '../config/events'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'

const props = defineProps<{
    chapterPath: string
    events: any[]
    x?: number
    y?: number
}>()

const emit = defineEmits(['update:events', 'select', 'delete', 'add-event', 'toggle-expand', 'start-connection', 'end-connection', 'delete-event'])

const localEvents = computed({
    get: () => props.events,
    set: (val) => emit('update:events', val)
})

const expandedEvents = ref<Record<number, boolean>>({})

function toggleEvent(index: number) {
    if (expandedEvents.value[index]) {
        delete expandedEvents.value[index]
    } else {
        expandedEvents.value[index] = true
    }
}

function getEventSchema(type: string) {
    return EVENT_SCHEMAS[type] || { label: type, color: 'border-gray-500 bg-gray-900', mandatory: [], optional: [] }
}

function addOptional(event: any, key: string, schema: any) {
    const field = schema.optional.find((f: any) => f.key === key)
    event[key] = field?.default ?? ''
}

function handleStartConnection(e: MouseEvent, side: 'left' | 'right') {
    emit('start-connection', e, props.chapterPath, side)
}

function handleEndConnection(e: MouseEvent, side: 'left' | 'right') {
    emit('end-connection', e, props.chapterPath, side)
}
</script>

<template>
  <div 
    class="absolute w-80 rounded-xl border border-gray-700 bg-gray-900/90 shadow-2xl backdrop-blur flex flex-col overflow-visible"
    :style="{ left: (x || 0) + 'px', top: (y || 0) + 'px' }"
    @mousedown.stop="$emit('select', $event)"
  >
    <!-- Chapter Header -->
    <div class="px-4 py-3 bg-gray-800 border-b border-gray-700 flex items-center justify-between cursor-move handle">
        <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-purple-500"></div>
            <span class="font-bold text-sm text-gray-200 truncate max-w-[180px]" :title="chapterPath">{{ chapterPath }}</span>
        </div>
        <div class="text-[10px] text-gray-500">{{ events.length }} events</div>
    </div>

    <!-- Events List -->
    <draggable 
        v-model="localEvents" 
        item-key="id" 
        class="flex-1 overflow-y-auto max-h-[400px] p-2 space-y-2 scrollbar-thin scrollbar-thumb-gray-700"
        handle=".event-handle"
    >
        <template #item="{ element, index }">
            <div 
                class="rounded border transition-all text-xs group"
                :class="[getEventSchema(element.type).color, expandedEvents[index] ? 'bg-opacity-30' : 'bg-opacity-10']"
            >
                <!-- Compact Row -->
                <div class="flex items-center p-2 cursor-pointer hover:bg-white/5 group" @click="toggleEvent(index)">
                    <div class="event-handle cursor-move mr-2 opacity-0 group-hover:opacity-50 hover:opacity-100">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path></svg>
                    </div>
                    
                    <span class="font-bold uppercase opacity-70 mr-2 min-w-[60px] text-[10px]">{{ getEventSchema(element.type).label }}</span>
                    
                    <span class="truncate flex-1 opacity-90">
                        {{ element.text || element.imagePath || element.musicPath || element.action || (element.type === 'end' ? 'Go to ' + element.next : '') || '...' }}
                    </span>

                    <!-- Indicators -->
                     <span v-if="element.condition" class="w-2 h-2 rounded-full bg-yellow-500 ml-2" title="Has Condition"></span>
                    
                    <!-- Delete Button -->
                    <button 
                        @click.stop="$emit('delete-event', index)"
                        class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500/20 hover:bg-red-500/40 border border-red-500/30 rounded p-1"
                        title="Delete Event"
                    >
                        <svg class="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>

                <!-- Expanded Details -->
                <div v-if="expandedEvents[index]" class="p-3 border-t border-white/10 space-y-3 bg-black/20 text-gray-300 cursor-default" @mousedown.stop>
                     <!-- Mandatory Fields -->
                     <div v-for="field in getEventSchema(element.type).mandatory" :key="field.key">
                         <label class="block text-[10px] uppercase font-bold opacity-50 mb-1">{{ field.label }}</label>
                         <textarea 
                            v-if="field.type === 'textarea'" 
                            v-model="element[field.key]" 
                            class="w-full bg-black/30 border border-white/10 rounded p-2 focus:border-purple-500/50 outline-none text-xs"
                         ></textarea>
                         <select 
                            v-else-if="field.type === 'select'"
                            v-model="element[field.key]"
                            class="w-full bg-black/30 border border-white/10 rounded p-1.5 focus:border-purple-500/50 outline-none text-xs"
                         >
                            <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                         </select>
                         <input 
                            v-else
                            v-model="element[field.key]"
                            class="w-full bg-black/30 border border-white/10 rounded p-1.5 focus:border-purple-500/50 outline-none text-xs"
                         />
                     </div>

                     <!-- Existing Optional Fields -->
                     <div v-for="(val, key) in element" :key="key">
                         <template v-if="getEventSchema(element.type).optional.find(f => f.key === key)">
                            <div class="relative group/opt">
                                <label class="block text-[10px] uppercase font-bold text-yellow-500/80 mb-1">{{ getEventSchema(element.type).optional.find(f => f.key === key)?.label }}</label>
                                <div class="flex items-center">
                                    <input v-model="element[key]" class="flex-1 bg-yellow-900/10 border border-yellow-500/20 rounded p-1.5 text-xs text-yellow-200 focus:outline-none focus:border-yellow-500/50" />
                                    <button @click="delete element[key]" class="ml-2 text-gray-600 hover:text-red-400">x</button>
                                </div>
                            </div>
                         </template>
                     </div>

                     <!-- Add Optional Button -->
                     <div class="relative group/add inline-block mt-2">
                         <button class="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded border border-gray-700">+ Add Option</button>
                         <div class="absolute top-full left-0 bg-gray-800 border border-gray-700 rounded shadow-lg z-20 hidden group-hover/add:block min-w-[120px]">
                              <div 
                                v-for="field in getEventSchema(element.type).optional.filter(f => element[f.key] === undefined)"
                                :key="field.key"
                                @click="addOptional(element, field.key, getEventSchema(element.type))"
                                class="px-3 py-1.5 hover:bg-gray-700 text-xs cursor-pointer"
                              >
                                {{ field.label }}
                              </div>
                         </div>
                     </div>
                </div>
            </div>
        </template>
    </draggable>

    <!-- Footer -->
    <div class="p-2 bg-gray-800/50 border-t border-gray-700">
        <button @click="$emit('add-event')" class="w-full py-1.5 rounded border border-dashed border-gray-600 text-gray-500 hover:text-purple-400 hover:border-purple-500/50 text-xs transition">+ Add Event</button>
    </div>

    <!-- Connection Handles -->
    <!-- Left Handle -->
    <div 
        class="absolute left-[-4px] top-1/2 w-2 h-2 bg-white rounded-full border-2 border-gray-300 cursor-pointer hover:bg-purple-200 hover:border-purple-400 transform -translate-y-1/2 z-10"
        @mousedown.stop="handleStartConnection($event, 'left')"
        @mouseup.stop="handleEndConnection($event, 'left')"
        title="Connect from left"
    ></div>
    
    <!-- Right Handle -->
    <div 
        class="absolute right-[-4px] top-1/2 w-2 h-2 bg-white rounded-full border-2 border-gray-300 cursor-pointer hover:bg-purple-200 hover:border-purple-400 transform -translate-y-1/2 z-10"
        @mousedown.stop="handleStartConnection($event, 'right')"
        @mouseup.stop="handleEndConnection($event, 'right')"
        title="Connect from right"
    ></div>
  </div>
</template>
