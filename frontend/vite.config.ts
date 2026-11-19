/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Явно слушаем IPv4 127.0.0.1: иначе на Windows vite занимает только ::1,
    // и ни прокси, ни проверка готовности (TCP по 127.0.0.1) не срабатывают.
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      // В dev-режиме запросы к /api уходят на FastAPI, поэтому CORS не нужен.
      '/api': 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
  },
})
