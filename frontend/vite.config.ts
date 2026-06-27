import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { campusPoiMergeDevPlugin } from './vite-plugins/campusPoiMergeDev'

export default defineConfig({
  plugins: [vue(), campusPoiMergeDevPlugin()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/_AMapService': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
