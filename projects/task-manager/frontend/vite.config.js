import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,                // 前端开发服务器端口
    proxy: {
      '/api': {
        target: 'http://localhost:5000',  // 后端地址
        changeOrigin: true,
      }
    }
  }
})