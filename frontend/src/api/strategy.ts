import axios from 'axios'
import { API_BASE_URL } from './config'
import type { StrategyParams } from '@/types/strategy'

export const simulateStrategy = async (params: StrategyParams) => {
  const response = await axios.post(`${API_BASE_URL}/strategy/simulate`, params)
  return response.data  // 确保返回 response.data
}