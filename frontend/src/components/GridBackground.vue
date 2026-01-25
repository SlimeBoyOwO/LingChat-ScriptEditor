<template>
  <div class="grid-background" />
</template>

<script setup lang="ts">
// Grid Background Component
</script>

<style scoped>
@reference "tailwindcss";

.grid-background {
  @apply fixed inset-0 w-full h-full pointer-events-none z-0;
  --grid-size: 50px;
  --grid-line-color: rgba(100, 180, 255, 0.15);
  --glow-color: rgba(0, 200, 255, 0.5);
  background-color: #050a15;
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

/* 轻微脉冲动画 */
@media (prefers-reduced-motion: no-preference) {
  .grid-background::after {
    content: "";
    @apply fixed inset-0 pointer-events-none z-[-1];
    background-image:
      radial-gradient(circle at 20% 30%, rgba(0, 200, 255, 0.04), transparent 25%),
      radial-gradient(circle at 80% 70%, rgba(120, 80, 255, 0.03), transparent 30%);
    mix-blend-mode: screen;
    opacity: 1;
    animation: tech-pulse 8s ease-in-out infinite;
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
