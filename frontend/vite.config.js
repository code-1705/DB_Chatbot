import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/chat': {
        target: 'https://db-chatbot.onrender.com',
        changeOrigin: true,
        secure: false,
      },
      '/history': {
        target: 'https://db-chatbot.onrender.com',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
