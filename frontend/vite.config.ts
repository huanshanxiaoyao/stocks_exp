import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'  // 修改这行
import { resolve } from 'path'
import os from 'os'

// 获取本机IP地址
function getLocalIP() {
  const interfaces = os.networkInterfaces()
  for (const name of Object.keys(interfaces)) {
    for (const interface_ of interfaces[name] ?? []) {
      const { address, family, internal } = interface_
      if (family === 'IPv4' && !internal) {
        return address
      }
    }
  }
  return 'localhost'
}

const localIP = getLocalIP()

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',  // 监听所有网络接口
    port: 3000,
    proxy: {
      '/api': {
        target: `http://${localIP}:8000`,  // 使用本机IP
        changeOrigin: true
      }
    }
  }
})
