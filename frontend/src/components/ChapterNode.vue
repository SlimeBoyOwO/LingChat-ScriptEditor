<script setup lang="ts">
import { computed, ref } from 'vue'
import draggable from 'vuedraggable'
import ResourceSelector from './common/ResourceSelector.vue'
import DeleteChapter from './dialog/DeleteChapter.vue'
import { DESCRIPTIONS, EVENT_SCHEMAS } from '../constants/events'
import { IconClose, IconDragHandle, IconChevronRight } from '@/assets/icons'

const props = defineProps<{
    chapterPath: string
    events: any[]
    x?: number
    y?: number
    isSelected?: boolean
}>()

const emit = defineEmits(['update:events', 'select', 'delete', 'add-event', 'toggle-expand', 'start-connection', 'end-connection', 'delete-event', 'swap-events', 'delete-chapter'])

const localEvents = computed({
    get: () => props.events,
    set: (val) => emit('update:events', val)
})

const expandedEvents = ref<Record<number, boolean>>({})
const showEventTypeDialog = ref(false)
const showDeleteDialog = ref(false)

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

function handleAddEvent() {
    showEventTypeDialog.value = true
}

function selectEventType(type: string) {
    console.log("select type:", type)
    emit('add-event', type)
    showEventTypeDialog.value = false
}

function getEventDescription(type: string): string {
    return DESCRIPTIONS[type] || '事件描述'
}

function onDragEnd(event: any) {
    emit('swap-events', event.moved.oldIndex, event.moved.newIndex)
}

function confirmDelete() {
    emit('delete-chapter')
    showDeleteDialog.value = false
}

function cancelDelete() {
    showDeleteDialog.value = false
}
</script>

<template>
  <div 
    class="absolute w-80 rounded-xl border bg-gray-900/90 shadow-2xl backdrop-blur flex flex-col overflow-visible transition-all duration-200"
    :class="isSelected ? 'border-purple-500 ring-2 ring-purple-500/50 shadow-purple-500/20' : 'border-gray-700'"
    :style="{ left: (x || 0) + 'px', top: (y || 0) + 'px' }"
    @mousedown.stop="$emit('select', $event)"
  >
    <!-- Chapter Header -->
    <div class="px-4 py-3 bg-gray-800 border-b border-gray-700 flex items-center justify-between cursor-move handle">
        <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-purple-500"></div>
            <span class="font-bold text-sm text-gray-200 truncate max-w-[180px]" :title="chapterPath">{{ chapterPath }}</span>
        </div>
        <div class="flex items-center space-x-2">
            <div class="text-[10px] text-gray-500">{{ events.length }} events</div>
            <button @click="showDeleteDialog = true" class="ml-2 group-hover:opacity-100 transition-opacity bg-red-500/20 hover:bg-red-500/40 border border-red-500/30 rounded p-1" title="删除章节">
                <IconClose class="w-3 h-3 text-red-400" />
            </button>
        </div>
    </div>

    <!-- Events List -->
    <draggable 
        v-model="localEvents" 
        item-key="id" 
        class="flex-1 overflow-y-auto max-h-[400px] min-h-[400px] p-2 space-y-2 scrollbar-thin scrollbar-thumb-gray-700"
        handle=".event-handle"
        @change="onDragEnd"
    >
        <template #item="{ element, index }">
            <div 
                class="rounded border transition-all text-xs group"
                :class="[getEventSchema(element.type).color, expandedEvents[index] ? 'bg-opacity-30' : 'bg-opacity-10']"
            >
                <!-- Compact Row -->
                <div class="flex items-center p-2 cursor-pointer hover:bg-white/5 group" @click="toggleEvent(index)">
                    <div class="event-handle cursor-move mr-2 opacity-0 group-hover:opacity-50 hover:opacity-100" @mousedown.stop>
                        <IconDragHandle class="w-3 h-3" />
                    </div>
                    
                    <span class="font-bold uppercase opacity-70 mr-2 min-w-[60px] text-[10px]">{{ getEventSchema(element.type).label }}</span>
                    
                    <span class="truncate flex-1 opacity-90">
                        {{ element.text || element.imagePath || element.musicPath || element.hint || element.action || (element.type === 'choices' ? (element.options?.length || 0) + ' 个选项' : '') || (element.type === 'chapter_end' ? (element.end_type || 'linear') + ' → ' + (element.next_chapter || 'end') : '') || '...' }}
                    </span>

                    <!-- Indicators -->
                     <span v-if="element.condition" class="w-2 h-2 rounded-full bg-yellow-500 ml-2" title="Has Condition"></span>
                    
                    <!-- Delete Button -->
                    <button 
                        @click.stop="$emit('delete-event', index)"
                        class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500/20 hover:bg-red-500/40 border border-red-500/30 rounded p-1"
                        title="Delete Event"
                    >
                        <IconClose class="w-3 h-3 text-red-400" />
                    </button>
                </div>

                <!-- Expanded Details -->
                <div v-if="expandedEvents[index]" class="p-3 border-t border-white/10 space-y-3 bg-black/20 text-gray-300 cursor-default" @mousedown.stop>
                     <!-- Choices Event Special Editor -->
                     <template v-if="element.type === 'choices'">
                         <!-- Options Editor -->
                         <div>
                             <label class="block text-[10px] uppercase font-bold opacity-50 mb-2">选项列表</label>
                             <div class="space-y-2">
                                 <div v-for="(option, optIdx) in element.options" :key="optIdx" class="bg-black/30 rounded p-2 border border-indigo-500/20">
                                     <div class="flex items-center gap-2 mb-2">
                                         <span class="text-[9px] text-indigo-400 w-4">{{ Number(optIdx) + 1 }}.</span>
                                         <input 
                                             v-model="option.text" 
                                             class="flex-1 bg-black/30 border border-indigo-500/20 rounded px-2 py-1 text-xs text-gray-200 focus:border-indigo-400/50 outline-none"
                                             placeholder="选项文本..."
                                         />
                                         <button 
                                             @click="element.options.splice(optIdx, 1)"
                                             class="text-gray-500 hover:text-red-400 text-xs"
                                         >✕</button>
                                     </div>
                                     <!-- Actions for this option -->
                                     <div class="pl-4 space-y-1">
                                         <div class="flex items-center justify-between">
                                             <span class="text-[9px] text-gray-500">Actions</span>
                                             <button 
                                                 @click="option.actions = option.actions || []; option.actions.push({ type: 'add_line', content: '' })"
                                                 class="text-[9px] px-1 py-0.5 bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 rounded"
                                             >+ action</button>
                                         </div>
                                         <div v-for="(action, actIdx) in option.actions" :key="actIdx" class="flex items-center gap-1">
                                             <select 
                                                 v-model="action.type" 
                                                 class="bg-black/30 border border-gray-600/30 rounded px-1 py-0.5 text-[9px] text-gray-300 outline-none"
                                             >
                                                 <option value="add_line">add_line</option>
                                                 <option value="set_variable">set_variable</option>
                                             </select>
                                             <input 
                                                 v-model="action.content"
                                                 class="flex-1 bg-black/20 border border-gray-700/30 rounded px-1 py-0.5 text-[9px] text-gray-400 outline-none"
                                                 placeholder="content..."
                                             />
                                             <button 
                                                 @click="option.actions.splice(actIdx, 1)"
                                                 class="text-gray-600 hover:text-red-400 text-[9px]"
                                             >✕</button>
                                         </div>
                                     </div>
                                 </div>
                                 <button 
                                     @click="element.options = element.options || []; element.options.push({ text: '', actions: [] })"
                                     class="w-full text-[10px] px-2 py-1.5 bg-cyan-600/30 hover:bg-cyan-600/50 text-white-300 rounded border border-cyan-500/30"
                                 >+ 添加选项</button>
                             </div>
                         </div>
                         <!-- Allow Free Input -->
                         <div class="flex items-center gap-2">
                             <input 
                                 type="checkbox" 
                                 :checked="element.allow_free === true || element.allow_free === 'true'"
                                 @change="element.allow_free = ($event.target as HTMLInputElement).checked"
                                 class="rounded bg-black/30 border-indigo-500/30"
                             />
                             <label class="text-[10px] text-gray-400">允许自由输入</label>
                         </div>
                     </template>

                     <!-- Chapter End Event Special Editor -->
                     <template v-else-if="element.type === 'chapter_end'">
                         <!-- End Type -->
                         <div>
                             <label class="block text-[10px] uppercase font-bold opacity-50 mb-1">结束类型</label>
                             <select 
                                 v-model="element.end_type"
                                 class="w-full bg-black/30 border border-white/10 rounded p-1.5 focus:border-purple-500/50 outline-none text-xs"
                             >
                                 <option value="linear">linear (线性)</option>
                                 <option value="branching">branching (分支)</option>
                                 <option value="ai_judged">ai_judged (AI判断)</option>
                             </select>
                         </div>
                         <!-- Next Chapter -->
                         <div>
                             <label class="block text-[10px] uppercase font-bold opacity-50 mb-1">下一章节</label>
                             <input 
                                 v-model="element.next_chapter"
                                 class="w-full bg-black/30 border border-white/10 rounded p-1.5 focus:border-purple-500/50 outline-none text-xs"
                                 placeholder="章节路径或 'end'"
                             />
                         </div>
                         <!-- Options for branching/ai_judged -->
                         <div v-if="element.end_type === 'branching' || element.end_type === 'ai_judged'">
                             <label class="block text-[10px] uppercase font-bold opacity-50 mb-2">分支选项</label>
                             <div class="space-y-2">
                                 <div v-for="(option, optIdx) in element.options" :key="optIdx" class="bg-black/30 rounded p-2 border border-white/10">
                                     <div class="flex items-center gap-2 mb-2">
                                         <span class="text-[9px] text-gray-400 w-4">{{ Number(optIdx) + 1 }}.</span>
                                         <input 
                                             v-model="option.text" 
                                             class="flex-1 bg-black/30 border border-white/10 rounded px-2 py-1 text-xs text-gray-200 focus:border-white/30 outline-none"
                                             placeholder="选项文本..."
                                         />
                                         <button 
                                             @click="element.options.splice(optIdx, 1)"
                                             class="text-gray-500 hover:text-red-400 text-xs"
                                         >✕</button>
                                     </div>
                                     <!-- Actions for this option -->
                                     <div class="pl-4 space-y-1">
                                         <div class="flex items-center justify-between">
                                             <span class="text-[9px] text-gray-500">Actions</span>
                                             <button 
                                                 @click="option.actions = option.actions || []; option.actions.push({ type: 'add_line', content: '' })"
                                                 class="text-[9px] px-1 py-0.5 bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 rounded"
                                             >+ action</button>
                                         </div>
                                         <div v-for="(action, actIdx) in option.actions" :key="actIdx" class="flex items-center gap-1">
                                             <select 
                                                 v-model="action.type" 
                                                 class="bg-black/30 border border-gray-600/30 rounded px-1 py-0.5 text-[9px] text-gray-300 outline-none"
                                             >
                                                 <option value="add_line">add_line</option>
                                                 <option value="set_variable">set_variable</option>
                                             </select>
                                             <input 
                                                 v-model="action.content"
                                                 class="flex-1 bg-black/20 border border-gray-700/30 rounded px-1 py-0.5 text-[9px] text-gray-400 outline-none"
                                                 placeholder="content..."
                                             />
                                             <button 
                                                 @click="option.actions.splice(actIdx, 1)"
                                                 class="text-gray-600 hover:text-red-400 text-[9px]"
                                             >✕</button>
                                         </div>
                                     </div>
                                 </div>
                                 <button 
                                     @click="element.options = element.options || []; element.options.push({ text: '', actions: [] })"
                                     class="w-full text-[10px] px-2 py-1.5 bg-white/10 hover:bg-white/20 text-gray-300 rounded border border-white/10"
                                 >+ 添加选项</button>
                             </div>
                         </div>
                     </template>

                     <!-- Non-choices Mandatory Fields -->
                     <template v-else>
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
                             <ResourceSelector 
                                v-else-if="field.type === 'file' && field.resourceType"
                                v-model="element[field.key]"
                                :resourceType="field.resourceType"
                                :placeholder="'选择' + field.label"
                             />
                             <input 
                                v-else
                                v-model="element[field.key]"
                                class="w-full bg-black/30 border border-white/10 rounded p-1.5 focus:border-purple-500/50 outline-none text-xs"
                             />
                         </div>
                     </template>

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
                    <template v-if="element.type !== 'chapter_end' && element.type !== 'choices'">
                        <div class="relative group/add inline-block mt-2">
                            <button class="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded border border-gray-700">+ Add Option</button>
                            <div class="absolute top-full left-0 bg-gray-800 border border-gray-700 rounded shadow-lg hidden group-hover/add:block min-w-[120px] z-50">
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
                     </template>
                </div>
            </div>
        </template>
    </draggable>

    <!-- Footer -->
    <div class="p-2 bg-gray-800/50 border-t border-gray-700">
        <button @click="handleAddEvent" class="w-full py-1.5 rounded border border-dashed border-gray-600 text-gray-500 hover:text-purple-400 hover:border-purple-500/50 text-xs transition">+ 新增事件</button>
    </div>

    <!-- Event Type Dialog -->
    <div v-if="showEventTypeDialog" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-full max-w-md">
            <div class="p-4 border-b border-gray-700">
                <h3 class="text-lg font-bold text-gray-200">选择事件类型</h3>
                <p class="text-sm text-gray-400 mt-1">选择要添加的事件类型</p>
            </div>
            
            <div class="p-4 space-y-2 max-h-64 overflow-y-auto">
                <div 
                    v-for="(schema, type) in EVENT_SCHEMAS" 
                    :key="type"
                    @click="selectEventType(type)"
                    class="flex items-center p-3 rounded-lg border border-gray-700 hover:border-gray-600 cursor-pointer transition-all group"
                    :class="schema.color"
                >
                    <div class="w-3 h-3 rounded-full mr-3" :class="schema.color.replace('bg-', 'bg-').replace('/20', '')"></div>
                    <div class="flex-1">
                        <div class="font-bold text-sm text-gray-200">{{ schema.label }}</div>
                        <div class="text-xs text-gray-400">{{ getEventDescription(type) }}</div>
                    </div>
                    <div class="text-xs text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
                        <IconChevronRight class="w-4 h-4" />
                    </div>
                </div>
            </div>
            
            <div class="p-4 border-t border-gray-700 flex justify-end">
                <button 
                    @click="showEventTypeDialog = false"
                    class="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
                >
                    取消
                </button>
            </div>
        </div>
    </div>

    <!-- Connection Handles -->
    <!-- Left Handle -->
    <div 
        class="absolute left-[-4px] top-1/2 w-2 h-2 bg-white rounded-full border-2 border-gray-300 cursor-pointer hover:bg-purple-200 hover:border-purple-400 transform -translate-y-1/2 z-10"
        @mousedown.stop="handleStartConnection($event, 'left')"
        @mouseup.stop="handleEndConnection($event, 'left')"
        title="连接终点"
    ></div>
    
    <!-- Right Handle -->
    <div 
        class="absolute right-[-4px] top-1/2 w-2 h-2 bg-white rounded-full border-2 border-gray-300 cursor-pointer hover:bg-purple-200 hover:border-purple-400 transform -translate-y-1/2 z-10"
        @mousedown.stop="handleStartConnection($event, 'right')"
        @mouseup.stop="handleEndConnection($event, 'right')"
        title="连接起点"
    ></div>

    <!-- Delete Confirmation Dialog -->
    <DeleteChapter
        :show-delete-dialog="showDeleteDialog" 
        :chapter-path="chapterPath"
        @cancel-delete="cancelDelete"
        @confirm-delete="confirmDelete"
    />
  </div>
</template>