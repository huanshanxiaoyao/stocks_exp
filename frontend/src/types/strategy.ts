export interface MinuteData {
  datetime: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

export interface DailySimulationResult {
  date: string
  holdingQuantity: number
  holdingAvgPrice: number
  buyQuantity: number
  buyPrice: number
  sellQuantity: number
  sellPrice: number
}