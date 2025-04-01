import axios from 'axios'
import { API_BASE_URL } from './config'
import type { StockQueryParams, StockDailyData } from '@/types/stock'

export const getStockDailyData = async (params: StockQueryParams) => {
  const response = await axios.get(`${API_BASE_URL}/stock/daily`, { params })
  return response.data  // 返回 response.data 而不是整个 response
}

// 如果有其他 API 请求，也需要类似修改
export const getStockMinuteData = (params: StockQueryParams) => {
  return axios.get(`${API_BASE_URL}/stock/minute`, { params })
}