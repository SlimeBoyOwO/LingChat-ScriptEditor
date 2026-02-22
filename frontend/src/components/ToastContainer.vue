<script setup lang="ts">
import { useToast, type ToastType } from '@/composables/useToast'

const { toasts, removeToast } = useToast()

const getIcon = (type: ToastType) => {
  switch (type) {
    case 'success':
      return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>`
    case 'error':
      return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>`
    case 'warning':
      return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
      </svg>`
    default:
      return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>`
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
            v-html="getIcon(toast.type)"
          ></div>
          
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
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
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