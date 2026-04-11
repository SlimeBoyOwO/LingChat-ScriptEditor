<script setup lang="ts">
    const props = defineProps<{
        showDeleteDialog: boolean,
        chapterPath: string,
    }>()

    const emit = defineEmits(['cancelDelete', 'confirmDelete'])
</script>

<template>
    <div v-if="showDeleteDialog" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-full max-w-md">
            <div class="p-4 border-b border-gray-700">
                <h3 class="text-lg font-bold text-gray-200">确认删除章节</h3>
                <p class="text-sm text-gray-400 mt-1">确定要删除章节 "{{ chapterPath }}" 吗？此操作无法撤销。</p>
            </div>
            
            <div class="p-4 space-y-4">
                <div class="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-red-500"></div>
                        <span class="text-sm font-medium text-red-400">警告</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-1">删除后，该章节的所有事件将被永久移除。</p>
                </div>
            </div>
            
            <div class="p-4 border-t border-gray-700 flex justify-end space-x-3">
                <button 
                    @click="emit('cancelDelete')"
                    class="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors border border-gray-600 rounded"
                >
                    取消
                </button>
                <button 
                    @click="emit('confirmDelete')"
                    class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                >
                    确定删除
                </button>
            </div>
        </div>
    </div>
</template>