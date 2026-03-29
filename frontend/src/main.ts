import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Import Tailwind CSS in dev mode (handled by @tailwindcss/vite)
// In build mode, output.css is injected via vite config
if (import.meta.env.DEV) {
  import('../input.css')
}

import './styles/base.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')