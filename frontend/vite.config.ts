import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

const isTauri = process.env.TAURI_ENV_DEBUG !== undefined

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  define: {
    __TAURI_ENV_DEBUG__: JSON.stringify(process.env.TAURI_ENV_DEBUG || ''),
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
  server: {
    port: 5174,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: !isTauri,
    minify: isTauri ? 'terser' : 'esbuild',
    terserOptions: isTauri ? {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    } : undefined,
  },
  clearScreen: false,
})
