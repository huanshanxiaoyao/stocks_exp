export interface StockData {
  datetime: string
  open: number
  close: number
  high: number
  low: number
  volume: number
  money: number
}

export interface DailySimulationResult {
  date: string
  holdingQuantity: number
  holdingAvgPrice: number
  buyQuantity: number
  buyPrice: number
  sellQuantity: number
  sellPrice: number
  totalCost: number
  totalValue: number
}

export interface StrategyConfig {
  id: string
  name: string
  description: string
}

export abstract class BaseStrategy {
  abstract readonly config: StrategyConfig
  protected params: any = {}

  setParams(params: any) {
    this.params = params
  }

  abstract execute(data: StockData[]): DailySimulationResult[]
}