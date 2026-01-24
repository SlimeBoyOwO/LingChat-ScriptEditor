<script setup lang="ts">
import { ref, computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { ChevronRightIcon } from '@heroicons/vue/20/solid' // Need to install heroicons or use svg

const props = defineProps<{
  nodes: any
  currentPath: string | null
}>()

const emit = defineEmits(['select'])
</script>

<template>
  <ul class="space-y-1">
    <li v-for="(node, key) in nodes" :key="key">
      <template v-if="!node.isLeaf">
        <Disclosure v-slot="{ open }" :defaultOpen="true">
          <DisclosureButton class="flex items-center w-full text-left px-2 py-1.5 rounded-md hover:bg-gray-800 text-xs font-semibold text-gray-500 uppercase tracking-wider transition focus:outline-none">
            <svg 
                class="w-3 h-3 mr-1 transition-transform" 
                :class="open ? 'rotate-90' : ''"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            {{ node.name }}
          </DisclosureButton>
          <DisclosurePanel class="pl-3 border-l border-gray-800 ml-1.5 mt-1 space-y-1">
             <ChapterTree :nodes="node.children" :currentPath="currentPath" @select="$emit('select', $event)" />
          </DisclosurePanel>
        </Disclosure>
      </template>
      <template v-else>
         <div 
            @click="$emit('select', node.path)"
            class="px-3 py-2 rounded text-sm cursor-pointer border transition truncate flex items-center"
            :class="[
                currentPath === node.path 
                    ? 'bg-purple-900/30 border-purple-500 text-purple-200 shadow-[0_0_10px_rgba(168,85,247,0.2)]' 
                    : 'bg-gray-800/30 text-gray-400 border-gray-800/50 hover:bg-gray-800 hover:text-gray-200 hover:border-gray-700'
            ]"
         >
            <span class="w-1.5 h-1.5 rounded-full bg-purple-500/50 mr-2" :class="currentPath === node.path ? 'bg-purple-400 animate-pulse' : 'opacity-0'"></span>
            {{ node.name }}
         </div>
      </template>
    </li>
  </ul>
</template>
