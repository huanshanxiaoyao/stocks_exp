export interface StockDailyData {
  date: string
  code: string
  open: number
  close: number
  high: number
  low: number
  volume: number
  money: number
}

export interface StockQueryParams {
  code: string
  startDate: string
  endDate: string
}