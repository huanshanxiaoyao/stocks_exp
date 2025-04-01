import { BaseStrategy, StockData, DailySimulationResult, StrategyConfig } from './base'

export class XueStrategy extends BaseStrategy {
  readonly config: StrategyConfig = {
    id: 'xue_strategy',
    name: '薛总高抛低吸',
    description: '持仓≤10万不卖出，持仓≥12万不买入，区间内高抛低吸'
  }

  private readonly INITIAL_QUANTITY = 100000
  private readonly TRADE_QUANTITY = 20000
  private readonly UP_THRESHOLD = 1.05
  private readonly DOWN_THRESHOLD = 0.95
  private readonly MIN_HOLDING_FOR_SELL = 100000  // 新增：最小卖出持仓
  private readonly MAX_HOLDING_FOR_BUY = 120000   // 新增：最大买入持仓

  execute(data: StockData[]): DailySimulationResult[] {
    if (!data || data.length === 0) {
      return []
    }

    const results: DailySimulationResult[] = []
    let currentQuantity = this.INITIAL_QUANTITY
    let currentAvgPrice = data[0].open
    let totalCost = currentQuantity * currentAvgPrice
    let totalCash = 0
    let lastDate = ''
    
    data.forEach((item, index) => {
      const currentDate = item.datetime.split(' ')[0]
      if (currentDate === lastDate) return
      
      const dailyResult: DailySimulationResult = {
        date: currentDate,
        holdingQuantity: currentQuantity,
        holdingAvgPrice: currentAvgPrice,
        buyQuantity: 0,
        buyPrice: 0,
        sellQuantity: 0,
        sellPrice: 0,
        totalCost,
        totalValue: totalCash + (currentQuantity * item.close)
      }
      
      if (index > 0) {
        const price = item.open
        // 修改买入条件：价格满足且持仓小于最大买入限制
        if (price <= currentAvgPrice * this.DOWN_THRESHOLD && currentQuantity < this.MAX_HOLDING_FOR_BUY) {
          dailyResult.buyQuantity = this.TRADE_QUANTITY
          dailyResult.buyPrice = price
          const newCost = price * this.TRADE_QUANTITY
          totalCost += newCost
          currentQuantity += this.TRADE_QUANTITY
          currentAvgPrice = (currentAvgPrice * (currentQuantity - this.TRADE_QUANTITY) + price * this.TRADE_QUANTITY) / currentQuantity
        } 
        // 修改卖出条件：价格满足且持仓大于最小卖出限制
        else if (price >= currentAvgPrice * this.UP_THRESHOLD && currentQuantity > this.MIN_HOLDING_FOR_SELL) {
          dailyResult.sellQuantity = this.TRADE_QUANTITY
          dailyResult.sellPrice = price
          currentQuantity -= this.TRADE_QUANTITY
          totalCash += price * this.TRADE_QUANTITY
        }
      }
      
      // 更新最终结果
      dailyResult.holdingQuantity = currentQuantity
      dailyResult.holdingAvgPrice = currentAvgPrice
      dailyResult.totalCost = totalCost
      dailyResult.totalValue = totalCash + (currentQuantity * item.close)
      
      results.push(dailyResult)
      lastDate = currentDate
    })
    
    return results
  }
}