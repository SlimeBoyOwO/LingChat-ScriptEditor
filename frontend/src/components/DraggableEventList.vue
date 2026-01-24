<script setup lang="ts">
import draggable from 'vuedraggable'
import { ref, computed } from 'vue'

const props = defineProps<{
  events: any[]
}>()

const emit = defineEmits(['update:events', 'delete', 'add'])

const localEvents = computed({
    get: () => props.events,
    set: (val) => emit('update:events', val)
})

function getEventColor(type: string) {
    switch (type) {
        case 'narration': return 'text-purple-300 border-purple-500/30 bg-purple-500/10';
        case 'dialogue': return 'text-blue-300 border-blue-500/30 bg-blue-500/10';
        case 'background': return 'text-green-300 border-green-500/30 bg-green-500/10';
        case 'music': return 'text-yellow-300 border-yellow-500/30 bg-yellow-500/10';
        case 'set_variable': return 'text-red-300 border-red-500/30 bg-red-500/10';
        default: return 'text-gray-300 border-gray-600 bg-gray-800';
    }
}
</script>

<template>
  <div class="relative">
      <!-- Connection Line -->
      <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-800 z-0"></div>

      <draggable 
        v-model="localEvents" 
        item-key="id" 
        handle=".drag-handle"
        class="space-y-6 relative z-10"
        ghost-class="opacity-50"
      >
        <template #item="{ element, index }">
            <div class="relative group">
                 <!-- Logic Connection Node -->
                 <div 
                    class="absolute left-6 top-6 w-4 h-4 rounded-full border-2 bg-gray-900 transform -translate-x-1/2 z-20 flex items-center justify-center"
                    :class="element.condition ? 'border-yellow-500' : 'border-gray-700 group-hover:border-purple-500/50'"
                    :title="element.condition ? 'Condition: ' + element.condition : 'Linear Flow'"
                 >
                    <span v-if="element.condition" class="block w-1 h-1 rounded-full bg-yellow-500"></span>
                 </div>

                 <!-- Condition Label -->
                 <div v-if="element.condition" class="absolute left-10 -top-3 bg-yellow-900/50 text-yellow-500 text-[10px] px-2 py-0.5 rounded border border-yellow-700/50 backdrop-blur">
                     if: {{ element.condition }}
                 </div>

                 <div 
                    class="ml-12 p-1 rounded-xl bg-gray-900/80 border transition-all duration-200 shadow-lg backdrop-blur"
                    :class="[getEventColor(element.type), 'group-hover:border-opacity-100 border-opacity-50']"
                 >
                    <!-- Header -->
                    <div class="flex items-center justify-between px-3 py-2 bg-black/20 rounded-t-lg">
                        <div class="flex items-center space-x-2">
                             <div class="drag-handle cursor-move p-1 hover:bg-white/10 rounded text-gray-500 hover:text-white transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path></svg>
                             </div>
                             <span class="font-mono text-xs font-bold uppercase tracking-wider opacity-90">{{ element.type }}</span>
                        </div>
                        
                        <div class="flex items-center space-x-3">
                             <div class="flex items-center space-x-1" title="Duration">
                                <span class="text-[10px] uppercase opacity-50">Dur</span>
                                <input v-model.number="element.duration" type="number" step="0.1" class="w-12 bg-black/20 border border-white/10 rounded px-1 text-xs text-center focus:outline-none focus:border-white/30" placeholder="0" />
                             </div>
                             <button @click="$emit('delete', index)" class="text-white/20 hover:text-red-400 transition" title="Delete">
                                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                             </button>
                        </div>
                    </div>

                    <!-- Body -->
                    <div class="p-4 space-y-3">
                        <!-- Common Text Field -->
                        <div v-if="element.text !== undefined || element.type.includes('dialogue') || element.type === 'narration' || element.type === 'player'">
                             <textarea 
                                v-model="element.text" 
                                class="w-full bg-black/20 text-gray-200 p-3 rounded-lg border border-white/5 focus:border-white/20 outline-none font-serif text-sm resize-y min-h-[80px] placeholder-white/10"
                                placeholder="Write content..."
                            ></textarea>
                        </div>
                        
                        <!-- Dynamic Fields -->
                        <div class="grid grid-cols-2 gap-4">
                             <div v-for="(value, key) in element" :key="key">
                                  <template v-if="key !== 'type' && key !== 'text' && key !== 'duration' && key !== 'condition'">
                                      <label class="text-[10px] uppercase font-bold opacity-40 mb-1 block tracking-wider">{{ key }}</label>
                                      <input 
                                        v-model="element[key]" 
                                        class="w-full bg-black/20 border border-white/5 rounded px-2 py-1.5 text-xs focus:outline-none focus:border-white/20 transition font-mono"
                                      />
                                  </template>
                             </div>
                        </div>
                        
                        <!-- Condition Editor -->
                        <div class="mt-2 pt-2 border-t border-white/5">
                            <div class="flex items-center space-x-2">
                                <span class="text-[10px] uppercase font-bold opacity-30 tracking-wider">Condition</span>
                                <input 
                                    v-model="element.condition" 
                                    placeholder="No condition (always run)"
                                    class="flex-1 bg-transparent border-b border-white/10 focus:border-yellow-500/50 text-xs px-1 py-0.5 focus:outline-none text-yellow-200/80 placeholder-white/10 transition"
                                />
                            </div>
                        </div>
                    </div>
                 </div>
            </div>
        </template>
      </draggable>
      
      <!-- Add Button at the end of the line -->
      <div class="pl-12 pt-4 relative z-10">
          <button @click="$emit('add')" class="flex items-center space-x-2 text-gray-500 hover:text-purple-400 transition group p-2 rounded hover:bg-gray-800/50">
              <div class="w-6 h-6 rounded-full border border-dashed border-gray-600 group-hover:border-purple-500 flex items-center justify-center">
                  <span class="text-lg leading-none mb-0.5">+</span>
              </div>
              <span class="text-sm font-medium">Add Next Event</span>
          </button>
      </div>
  </div>
</template>

<style scoped>
.ghost {
    opacity: 0.5;
    background: #c8ebfb;
}
</style>
