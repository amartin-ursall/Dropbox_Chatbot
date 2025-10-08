import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Determine if we should use HTTPS
const useHttps = process.env.VITE_USE_HTTPS !== 'false'
const sslPath = path.resolve(__dirname, 'ssl')
const keyPath = path.join(sslPath, 'key.pem')
const certPath = path.join(sslPath, 'cert.pem')

// Check if SSL files exist
const sslExists = fs.existsSync(keyPath) && fs.existsSync(certPath)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all network interfaces for external access
    port: process.env.VITE_PORT ? parseInt(process.env.VITE_PORT) : 5173,
    strictPort: false,
    https: useHttps && sslExists ? {
      key: fs.readFileSync(keyPath),
      cert: fs.readFileSync(certPath),
    } : undefined,
    cors: true, // Enable CORS for network access
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://dropboxaiorganizer.com:8000',
        changeOrigin: true,
        secure: false,
        ws: true, // Enable WebSocket proxy
      },
      '/auth': {
        target: process.env.VITE_BACKEND_URL || 'http://dropboxaiorganizer.com:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    cors: true,
    https: useHttps && sslExists ? {
      key: fs.readFileSync(keyPath),
      cert: fs.readFileSync(certPath),
    } : undefined,
  },
})
