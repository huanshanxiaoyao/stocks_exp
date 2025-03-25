import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('请求错误:', error.response || error)
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

export default request