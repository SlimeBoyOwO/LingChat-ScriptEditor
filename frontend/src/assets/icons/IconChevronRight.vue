<template>
  <svg :class="class" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
  </svg>
</template>

<script setup lang="ts">
defineProps<{
  class?: string
}>()
</script>