import request from '@/utils/request'
import type { StockQueryParams, StockDailyData } from '@/types/stock'

export const getStockDailyData = async (params: StockQueryParams) => {
  return request.get<any, StockDailyData[]>('/api/stock/daily', { params })
}