import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import dns from 'node:dns'

dns.setDefaultResultOrder('ipv4first')

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
