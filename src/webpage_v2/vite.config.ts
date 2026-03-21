import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 4452,
    host: '0.0.0.0',
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // Enable source maps for better debugging in production
  },
})

