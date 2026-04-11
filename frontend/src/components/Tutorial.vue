<script setup lang="ts">
import { ref } from 'vue'
import { IconClose } from '@/assets/icons'

// Tutorial state
const showTutorial = ref(false)
const tutorialStep = ref(0)
const tutorialMessages = [
    "哎呀，看来小杂鱼需要一点帮助呢😤",
    "让我来教你创建第一个故事脚本吧❤️",
    "首先，从点击“New Script”按钮开始。",
    "输入你的故事名称、描述和用户信息。",
    "特别注意“开场章节”字段，输入的路径将直接用于创建yaml文件。",
    "创建完成后，点击刚刚创建的剧本，将进入编辑器界面。",
    "在编辑器中，你可以添加各种事件来构建你的故事。",
    "每个事件都有不同的类型，比如对话、选择、结局等。",
    "点击“新增事件”按钮，选择Narration来创建第一个事件。",
    "创建好了以后再点击一下，就能编辑事件的内容了！",
    "编辑完成后，记得点击“全部保存”按钮保存你的修改。",
    "点击新增章节，就可以新建一个新的yaml文件。",
    "章节两边有小白点，你可以在章节之间拖拽出一条跳转的线路",
    "当然，你也可以增加End / Jump事件来跳转",
    "好了，以上就是创建和编辑故事的基本流程了！", 
    "小杂鱼学会了吗❤️"
]

function startTutorial() {
    showTutorial.value = true
    tutorialStep.value = 0
}

function nextTutorialStep() {
    if (tutorialStep.value < tutorialMessages.length - 1) {
        tutorialStep.value++
    }   else {
        // Tutorial completed - close tutorial
        showTutorial.value = false
        tutorialStep.value = 0
    }
}

function skipTutorial() {
    showTutorial.value = false
    tutorialStep.value = 0
}
</script>

<template>
    <!-- Tutorial Button -->
    <div class="fixed bottom-8 right-8 z-50">
      <button 
        @click="startTutorial"
        class="bg-gradient-to-r from-black-100 to-blue-600 border-2 text-white p-4 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110"
        title="教程" 
      >
      <img src="/小猫.png" style="height: 30px;width: 30px;object-fit: contain; "/>
      </button>
    </div>

    <!-- Tutorial Dialog -->
    <div v-if="showTutorial" class="fixed top-4 right-4 w-96 bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl z-50 transform transition-all duration-300" :class="showTutorial ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'">
      <!-- Character Header -->
      <div class="p-4 border-b border-gray-700 bg-gradient-to-r from-cyan-900/50 to-blue-900/50">
        <div class="flex items-center space-x-3">
          <img 
            src="/teacher.png" 
            alt="风雪" 
            class="w-24 h-24 rounded-full border-2 border-cyan-400 shadow-lg object-contain"
          />
          <div>
            <h3 class="text-lg font-bold text-white">风雪</h3>
          </div>
          <button 
            @click="skipTutorial"
            class="ml-auto text-gray-400 hover:text-gray-200 transition-colors"
          >
            <IconClose class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Tutorial Content -->
      <div class="p-4">
        <div class="mb-3">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs text-gray-400">步骤 {{ tutorialStep + 1 }}/{{ tutorialMessages.length }}</span>
            <div class="flex space-x-1">
              <div 
                v-for="(_, index) in tutorialMessages" 
                :key="index"
                :class="[
                  'w-2 h-2 rounded-full',
                  index <= tutorialStep ? 'bg-cyan-400' : 'bg-gray-600'
                ]"
              ></div>
            </div>
          </div>
          <div class="w-full bg-gray-700 rounded-full h-1.5">
            <div 
              class="bg-gradient-to-r from-cyan-500 to-blue-500 h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${((tutorialStep + 1) / tutorialMessages.length) * 100}%` }"
            ></div>
          </div>
        </div>

        <div class="bg-gray-800 rounded-lg p-3 border border-gray-600">
          <p class="text-gray-200 text-sm leading-relaxed h-[40px]">
            {{ tutorialMessages[tutorialStep] }}
          </p>
        </div>

        <!-- Tutorial Actions -->
        <div class="mt-4 flex justify-between items-center">
          <div class="flex space-x-2">
            <button 
              v-if="tutorialStep > 0"
              @click="tutorialStep--"
              class="px-3 py-1 text-xs text-gray-400 hover:text-gray-200 transition-colors border border-gray-600 rounded"
            >
              上一步
            </button>
          </div>
          
          <button 
            @click="nextTutorialStep"
            class="px-4 py-1.5 text-xs bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white rounded-lg transition-colors"
          >
            {{ tutorialStep === tutorialMessages.length - 1 ? '完成' : '下一步' }}
          </button>
        </div>
      </div>
    </div>
</template>