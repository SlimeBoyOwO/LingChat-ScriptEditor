<script setup lang="ts">
import { useScriptStore } from '@/stores/script'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const scriptStore = useScriptStore()
const router = useRouter()

onMounted(() => {
  scriptStore.fetchScripts()
})

function openScript(id: string) {
  router.push(`/editor/${id}`)
}
</script>

<template>
  <div class="home-bg min-h-screen text-white p-8 font-sans">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-4xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 tracking-tight">
        Script Editor
      </h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="script in scriptStore.scripts" 
          :key="script.id"
          @click="openScript(script.id!)"
          class="bg-gray-800/80 backdrop-blur rounded-xl p-6 cursor-pointer hover:bg-gray-700 transition duration-300 border border-gray-700 hover:border-purple-500 group shadow-lg"
        >
          <h2 class="text-xl font-bold mb-2 group-hover:text-purple-300 transition-colors">{{ script.script_name }}</h2>
          <p class="text-gray-400 text-sm mb-4 line-clamp-2">{{ script.description }}</p>
          <div class="flex items-center justify-between text-xs text-gray-500 mt-auto">
            <span class="bg-gray-900 px-2 py-1 rounded border border-gray-700">Start: {{ script.intro_charpter }}</span>
            <span v-if="script.script_settings?.user_name">Pro: {{ script.script_settings.user_name }}</span>
          </div>
        </div>
        
        <!-- Create New Button -->
        <div class="bg-gray-800/30 rounded-xl p-6 cursor-pointer hover:bg-gray-800 transition border-2 border-dashed border-gray-700 hover:border-gray-500 flex flex-col items-center justify-center text-gray-500 hover:text-gray-300 h-full min-h-[160px]">
          <span class="text-5xl mb-2 font-light">+</span>
          <span class="font-medium">New Script</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-bg {
  --grid-size: 50px;
  --grid-line-color: rgba(100, 180, 255, 0.15);
  --glow-color: rgba(0, 200, 255, 0.5);
  background-color: #050a15;
  position: relative;
  overflow: hidden;
  background-image:
    /* 菱形发光点（右上方向） */
    linear-gradient(135deg, var(--glow-color) 0%, rgba(0, 200, 255, 0.25) 1px, transparent 2.5px),
    /* 菱形发光点（左上方向） */
    linear-gradient(45deg, var(--glow-color) 0%, rgba(0, 200, 255, 0.25) 1px, transparent 2.5px),
    /* 菱形发光点（右下方向） */
    linear-gradient(-45deg, var(--glow-color) 0%, rgba(0, 200, 255, 0.25) 1px, transparent 2.5px),
    /* 菱形发光点（左下方向） */
    linear-gradient(-135deg, var(--glow-color) 0%, rgba(0, 200, 255, 0.25) 1px, transparent 2.5px),
    /* 水平网格线 */
    linear-gradient(180deg, var(--grid-line-color) 1px, transparent 1px),
    /* 竖直网格线 */
    linear-gradient(90deg, var(--grid-line-color) 1px, transparent 1px),
    /* 底层渐变 */
    linear-gradient(135deg, rgba(0, 150, 255, 0.08) 0%, transparent 50%, rgba(120, 80, 255, 0.05) 100%);
  background-size:
    var(--grid-size) var(--grid-size),
    var(--grid-size) var(--grid-size),
    var(--grid-size) var(--grid-size),
    var(--grid-size) var(--grid-size),
    var(--grid-size) var(--grid-size),
    var(--grid-size) var(--grid-size),
    200% 200%;
  background-position: 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0;
  background-attachment: fixed, fixed, fixed, fixed, fixed, fixed, fixed;
}

/* 内容在伪元素上方 */
.home-bg > * {
  position: relative;
  z-index: 1;
}

/* 轻微脉冲动画 */
@media (prefers-reduced-motion: no-preference) {
  .home-bg::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
      radial-gradient(circle at 20% 30%, rgba(0, 200, 255, 0.04), transparent 25%),
      radial-gradient(circle at 80% 70%, rgba(120, 80, 255, 0.03), transparent 30%);
    mix-blend-mode: screen;
    opacity: 1;
    animation: tech-pulse 8s ease-in-out infinite;
    z-index: 0;
  }

  @keyframes tech-pulse {
    0%, 100% {
      opacity: 0.7;
      transform: scale(1);
    }
    50% {
      opacity: 1;
      transform: scale(1.01);
    }
  }
}
</style>