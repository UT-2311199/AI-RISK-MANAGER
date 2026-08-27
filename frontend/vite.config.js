import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to avoid CORS issues in development
      '/auth': 'http://localhost:8000',
      '/projects': 'http://localhost:8000',
      '/risks': 'http://localhost:8000',
    },
  },
})
