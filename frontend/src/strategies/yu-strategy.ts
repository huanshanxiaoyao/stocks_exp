import { BaseStrategy, StockData, DailySimulationResult, StrategyConfig } from './base'

export class YuStrategy extends BaseStrategy {
  readonly config: StrategyConfig = {
    id: 'yu_strategy_1',
    name: '于博简易1',
    description: '跌10%买入1万股(最多持仓5万)，涨15%卖出1万股(最少持仓2万)'
  }

  private readonly TRADE_QUANTITY = 10000
  private readonly MAX_HOLDING = 50000
  private readonly MIN_HOLDING_FOR_SELL = 20000
  private readonly DOWN_THRESHOLD = 0.95  // 下跌5%
  private readonly UP_THRESHOLD = 1.10    // 上涨10%

  execute(data: StockData[]): DailySimulationResult[] {
    const results: DailySimulationResult[] = []
    let currentQuantity = 0
    let currentAvgPrice = 0
    let totalCost = 0
    let totalCash = 0
    let lastDate = ''
    let todayBoughtQuantity = 0  // 新增：记录当天新买入的数量
    
    data.forEach((item) => {
      const currentDate = item.datetime.split(' ')[0]
      
      // 新的一天，重置当天的交易记录
      if (currentDate !== lastDate) {
        todayBoughtQuantity = 0
        results.push({
          date: currentDate,
          holdingQuantity: currentQuantity,
          holdingAvgPrice: currentAvgPrice,
          buyQuantity: 0,
          buyPrice: 0,
          sellQuantity: 0,
          sellPrice: 0,
          totalCost: totalCost,
          totalValue: totalCash + currentQuantity * item.close
        })
        lastDate = currentDate
        return
      }
      
      const lastResult = results[results.length - 1]
      const historicalQuantity = currentQuantity - todayBoughtQuantity  // 历史持仓数量
      
      // 买入逻辑
      if (item.low <= item.open * this.DOWN_THRESHOLD) {
        if (currentQuantity === 0 || (currentQuantity < this.MAX_HOLDING && item.low <= currentAvgPrice * this.DOWN_THRESHOLD)) {
          // 买入操作
          const oldValue = currentQuantity * currentAvgPrice
          const newValue = this.TRADE_QUANTITY * item.low
          currentQuantity += this.TRADE_QUANTITY
          todayBoughtQuantity += this.TRADE_QUANTITY
          currentAvgPrice = (oldValue + newValue) / currentQuantity
          totalCost += item.low * this.TRADE_QUANTITY
          
          lastResult.buyQuantity = this.TRADE_QUANTITY
          lastResult.buyPrice = item.low
          lastResult.holdingQuantity = currentQuantity
          lastResult.holdingAvgPrice = currentAvgPrice
          lastResult.totalCost = totalCost
          lastResult.totalValue = totalCash + currentQuantity * item.close
        }
      }
      
      // 卖出逻辑 - 只能卖出历史持仓
      if (historicalQuantity >= this.MIN_HOLDING_FOR_SELL && item.high >= currentAvgPrice * this.UP_THRESHOLD) {
        currentQuantity -= this.TRADE_QUANTITY
        totalCash += item.high * this.TRADE_QUANTITY
        
        lastResult.sellQuantity = this.TRADE_QUANTITY
        lastResult.sellPrice = item.high
        lastResult.holdingQuantity = currentQuantity
        lastResult.totalValue = totalCash + currentQuantity * item.close
      }
    })
    
    return results
}
}