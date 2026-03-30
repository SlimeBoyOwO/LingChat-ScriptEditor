<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
    event: any
    index: number
    selected?: boolean
}>()

const emit = defineEmits(['update:event', 'delete', 'select', 'add-field'])

const localEvent = computed({
    get: () => props.event,
    set: (val) => emit('update:event', val)
})

// Optional Fields Management
const showCondition = computed(() => localEvent.value.condition !== undefined)
const showDuration = computed(() => localEvent.value.duration !== undefined && localEvent.value.duration !== 0)

const availableOptionalFields = computed(() => {
    const fields = []
    if (!showCondition.value) fields.push({ key: 'condition', label: 'Condition' })
    if (!showDuration.value) fields.push({ key: 'duration', label: 'Duration' })
    // Add other fields based on type if needed
    if (props.event.type === 'modify_character') {
         if (!props.event.emotion) fields.push({ key: 'emotion', label: 'Emotion' })
         if (!props.event.action) fields.push({ key: 'action', label: 'Action' })
    }
    if (props.event.type === 'choices') {
         if (props.event.allow_free === undefined) fields.push({ key: 'allow_free', label: 'Allow Free Input' })
    }
    return fields
})

function addField(key: string) {
    if (key === 'condition') localEvent.value.condition = ''
    if (key === 'duration') localEvent.value.duration = 1.0
    if (key === 'emotion') localEvent.value.emotion = 'normal'
    if (key === 'action') localEvent.value.action = 'appear'
    if (key === 'allow_free') localEvent.value.allow_free = true
}

function removeField(key: string) {
    delete localEvent.value[key]
}

function getNodeColor(type: string) {
    if (type.includes('dialogue')) return 'border-blue-500/50 bg-blue-900/20'
    if (type === 'narration') return 'border-purple-500/50 bg-purple-900/20'
    if (type === 'background' || type === 'music') return 'border-green-500/50 bg-green-900/20'
    if (type === 'choices') return 'border-indigo-500/50 bg-indigo-900/20'
    return 'border-gray-600 bg-gray-800'
}

// Choices Management
const isExpanded = ref(false)

// Ensure options array exists
const options = computed({
    get: () => localEvent.value.options || [],
    set: (val) => { localEvent.value.options = val }
})

function addOption() {
    if (!localEvent.value.options) {
        localEvent.value.options = []
    }
    localEvent.value.options.push({
        text: '',
        actions: []
    })
}

function removeOption(index: number) {
    localEvent.value.options.splice(index, 1)
}

function addAction(optionIndex: number) {
    if (!localEvent.value.options[optionIndex].actions) {
        localEvent.value.options[optionIndex].actions = []
    }
    localEvent.value.options[optionIndex].actions.push({
        type: 'add_line',
        content: ''
    })
}

function removeAction(optionIndex: number, actionIndex: number) {
    localEvent.value.options[optionIndex].actions.splice(actionIndex, 1)
}
</script>

<template>
  <div 
    class="absolute w-64 rounded-lg border shadow-lg backdrop-blur-md group flex flex-col"
    :class="[
        getNodeColor(localEvent.type),
        selected ? 'ring-2 ring-purple-400 z-10' : 'hover:border-opacity-100 border-opacity-60 z-0'
    ]"
    :style="{ left: (localEvent.x || 0) + 'px', top: (localEvent.y || 0) + 'px' }"
    @mousedown.stop="$emit('select', $event)"
  >
    <!-- Header -->
    <div class="px-3 py-2 border-b border-white/10 flex items-center justify-between bg-black/20 rounded-t-lg cursor-move">
        <span class="text-xs font-bold uppercase tracking-wider opacity-80">{{ localEvent.type }}</span>
        <button @click.stop="$emit('delete')" class="text-white/20 hover:text-red-400 transition ml-2">x</button>
    </div>

    <!-- Content -->
    <div class="p-3 text-xs space-y-2 flex-1">
        <!-- Main Text Area for certain types -->
        <textarea 
            v-if="['narration', 'player', 'dialogue', 'ai_dialogue'].includes(localEvent.type)"
            v-model="localEvent.text"
            class="w-full bg-black/20 rounded border border-white/5 p-2 text-gray-200 focus:border-purple-500/50 outline-none resize-none h-20"
            placeholder="..."
            @mousedown.stop
        ></textarea>

        <!-- Other specific fields -->
        <div v-if="localEvent.imagePath !== undefined">
            <label class="block text-[10px] text-blue-400 mb-0.5">Image</label>
            <input v-model="localEvent.imagePath" class="w-full bg-black/20 border border-white/10 rounded px-1 py-0.5" @mousedown.stop />
        </div>
         <div v-if="localEvent.musicPath !== undefined">
            <label class="block text-[10px] text-green-400 mb-0.5">Music</label>
            <input v-model="localEvent.musicPath" class="w-full bg-black/20 border border-white/10 rounded px-1 py-0.5" @mousedown.stop />
        </div>

        <!-- Choices Event Type -->
        <div v-if="localEvent.type === 'choices'" class="space-y-2">
            <div class="flex items-center justify-between">
                <span class="text-[10px] text-indigo-400 font-semibold">选项列表</span>
                <button 
                    @click.stop="addOption" 
                    class="text-[10px] px-1.5 py-0.5 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 rounded"
                >
                    + 添加选项
                </button>
            </div>
            
            <div 
                v-for="(option, optIndex) in options" 
                :key="optIndex"
                class="bg-black/30 rounded p-2 space-y-1.5 border border-indigo-500/20"
            >
                <div class="flex items-center gap-1">
                    <span class="text-[9px] text-indigo-400 w-4">{{ Number(optIndex) + 1 }}.</span>
                    <input 
                        v-model="option.text" 
                        class="flex-1 bg-black/30 border border-indigo-500/20 rounded px-1.5 py-1 text-[11px] text-gray-200 focus:border-indigo-400/50 outline-none"
                        placeholder="选项文本..."
                        @mousedown.stop
                    />
                    <button 
                        @click.stop="removeOption(Number(optIndex))" 
                        class="text-gray-500 hover:text-red-400 text-[10px]"
                    >
                        ✕
                    </button>
                </div>
                
                <!-- Actions for this option -->
                <div class="pl-4 space-y-1">
                    <div class="flex items-center justify-between">
                        <span class="text-[9px] text-gray-500">Actions</span>
                        <button 
                            @click.stop="addAction(Number(optIndex))"
                            class="text-[9px] px-1 py-0.5 bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 rounded"
                        >
                            + action
                        </button>
                    </div>
                    <div 
                        v-for="(action, actIndex) in option.actions" 
                        :key="actIndex"
                        class="flex items-center gap-1"
                    >
                        <select 
                            v-model="action.type" 
                            class="bg-black/30 border border-gray-600/30 rounded px-1 py-0.5 text-[9px] text-gray-300 outline-none"
                            @mousedown.stop
                        >
                            <option value="add_line">add_line</option>
                            <option value="set_variable">set_variable</option>
                        </select>
                        <input 
                            v-model="action.content"
                            class="flex-1 bg-black/20 border border-gray-700/30 rounded px-1 py-0.5 text-[9px] text-gray-400 outline-none"
                            placeholder="content..."
                            @mousedown.stop
                        />
                        <button 
                            @click.stop="removeAction(Number(optIndex), Number(actIndex))"
                            class="text-gray-600 hover:text-red-400 text-[9px]"
                        >
                            ✕
                        </button>
                    </div>
                </div>
            </div>
            
            <div v-if="options.length === 0" class="text-[10px] text-gray-500 text-center py-2">
                点击"添加选项"创建选择项
            </div>
        </div>

        <!-- Optional Fields Display -->
        <div v-if="localEvent.condition" class="flex items-center space-x-1 border-t border-white/10 pt-2">
            <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
            <input v-model="localEvent.condition" class="bg-transparent text-yellow-500 w-full focus:outline-none placeholder-yellow-800" placeholder="Condition..." @mousedown.stop />
            <button @click="removeField('condition')" class="text-gray-600 hover:text-red-400">x</button>
        </div>
        
        <div v-if="localEvent.duration && localEvent.duration !== 0" class="flex items-center space-x-1">
            <span class="text-[10px] text-gray-500">Dur:</span>
            <input v-model.number="localEvent.duration" type="number" step="0.1" class="w-12 bg-transparent border-b border-gray-700 text-gray-300 text-center" @mousedown.stop />
             <button @click="removeField('duration')" class="text-gray-600 hover:text-red-400">x</button>
        </div>
        
        <div v-if="localEvent.emotion" class="flex items-center space-x-1">
             <span class="text-[10px] text-pink-400">Emo:</span>
             <input v-model="localEvent.emotion" class="w-full bg-transparent border-b border-pink-900/50 text-pink-200" @mousedown.stop />
             <button @click="removeField('emotion')" class="text-gray-600 hover:text-red-400">x</button>
        </div>
    </div>

    <!-- Add Optional Field Button -->
    <div class="px-3 py-1 bg-black/10 rounded-b-lg flex justify-center group/add relative">
        <button class="text-gray-500 hover:text-purple-400 transition" title="Add Field">+</button>
        
        <!-- Dropdown -->
        <div class="absolute top-full left-0 right-0 bg-gray-800 border border-gray-700 rounded shadow-xl mt-1 hidden group-hover/add:block z-20">
            <div 
                v-for="field in availableOptionalFields" 
                :key="field.key"
                @click.stop="addField(field.key)"
                class="px-3 py-1.5 hover:bg-gray-700 text-xs text-gray-300 cursor-pointer text-left"
            >
                {{ field.label }}
            </div>
            <div v-if="availableOptionalFields.length === 0" class="px-3 py-1.5 text-gray-600 text-[10px]">No more fields</div>
        </div>
    </div>
  </div>
</template>
