<script setup lang="ts">
import { RouterView } from 'vue-router'
import GridBackground from '@/components/GridBackground.vue'
import ToastContainer from '@/components/ToastContainer.vue'
</script>

<template>
  <GridBackground />
  <RouterView />
  <ToastContainer />
</template>

<style scoped>
:global(html, body) {
  margin: 0;
  padding: 0;
  background-color: #050a15;
}
</style>