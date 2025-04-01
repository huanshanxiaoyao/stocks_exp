import { BaseStrategy } from './base'
import { XueStrategy } from './xue-strategy'
import { YuStrategy } from './yu-strategy'

class StrategyRegistry {
  private strategies: Map<string, BaseStrategy> = new Map()

  constructor() {
    this.registerStrategy(new XueStrategy())
    this.registerStrategy(new YuStrategy())  // 注册新策略
  }

  registerStrategy(strategy: BaseStrategy) {
    this.strategies.set(strategy.config.id, strategy)
  }

  getStrategy(id: string): BaseStrategy | undefined {
    return this.strategies.get(id)
  }

  getAllStrategies(): BaseStrategy[] {
    return Array.from(this.strategies.values())
  }
}

export const strategyRegistry = new StrategyRegistry()