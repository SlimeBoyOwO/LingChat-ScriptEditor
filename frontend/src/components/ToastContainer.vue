<script setup lang="ts">
import { useToast, type ToastType } from '@/composables/useToast'
import { IconSuccess, IconClose, IconWarning, IconInfo } from '@/assets/icons'

const { toasts, removeToast } = useToast()

const getIcon = (type: ToastType) => {
  switch (type) {
    case 'success':
      return 'success'
    case 'error':
      return 'error'
    case 'warning':
      return 'warning'
    default:
      return 'info'
  }
}

const getStyle = (type: ToastType) => {
  switch (type) {
    case 'success':
      return {
        bg: 'green',
        border: 'border-emerald-400/50',
        shadow: 'shadow-emerald-500/20',
        icon: 'text-white'
      }
    case 'error':
      return {
        bg: 'red',
        border: 'border-red-400/50',
        shadow: 'shadow-red-500/20',
        icon: 'text-white'
      }
    case 'warning':
      return {
        bg: 'orange',
        border: 'border-amber-400/50',
        shadow: 'shadow-amber-500/20',
        icon: 'text-white'
      }
    default:
      return {
        bg: 'blue',
        border: 'border-blue-400/50',
        shadow: 'shadow-blue-500/20',
        icon: 'text-white'
      }
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-3 max-w-sm w-100 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl border shadow-lg transform transition-all duration-300 bg-amber-100"
          :style="`backgroundColor:${getStyle(toast.type).bg}`"
        >
          <!-- Icon -->
          <div 
            class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
            :class="getStyle(toast.type).icon"
          >
            <IconSuccess v-if="getIcon(toast.type) === 'success'" class="w-5 h-5" />
            <IconClose v-else-if="getIcon(toast.type) === 'error'" class="w-5 h-5" />
            <IconWarning v-else-if="getIcon(toast.type) === 'warning'" class="w-5 h-5" />
            <IconInfo v-else class="w-5 h-5" />
          </div>
          
          <!-- Message -->
          <div class="flex-1 min-w-0">
            <p class="text-white text-sm font-medium leading-relaxed whitespace-pre-wrap break-words">
              {{ toast.message }}
            </p>
          </div>
          
          <!-- Close Button -->
          <button
            @click="removeToast(toast.id)"
            class="flex-shrink-0 w-6 h-6 rounded-full hover:bg-white/20 flex items-center justify-center text-white/80 hover:text-white transition-all duration-200"
          >
            <IconClose class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in forwards;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
}
</style>