import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  base: './',
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
    // Only use Tailwind Vite plugin in dev mode
    mode === 'development' ? tailwindcss() : null,
    // Inject output.css only in build mode
    {
      name: 'inject-output-css',
      transformIndexHtml(html: string) {
        if (mode === 'production') {
          return html.replace(
            '</head>',
            '    <link href="./output.css" rel="stylesheet">\n  </head>'
          )
        }
        return html
      }
    }
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5174,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/preview': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
}))