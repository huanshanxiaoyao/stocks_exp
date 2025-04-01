<template>
  <el-card class="strategy-simulation">
    <el-form :inline="true" @submit.prevent="handleSimulate">
      <el-form-item label="股票代码">
        <el-input
          v-model="stockCode"
          placeholder="请输入股票代码，如：831305"
          clearable
          style="width: 150px"
        />
      </el-form-item>
      <el-form-item label="交易所">
        <el-select v-model="exchange" style="width: 120px">
          <el-option label="上海证券交易所" value="XSHG" />
          <el-option label="深圳证券交易所" value="XSHE" />
          <el-option label="北京证券交易所" value="BJSE" />
        </el-select>
      </el-form-item>
      <el-form-item label="策略选择">
        <el-select v-model="strategy" style="width: 160px">
          <el-option
            v-for="s in availableStrategies"
            :key="s.config.id"
            :label="s.config.name"
            :value="s.config.id"
          >
            <div>
              <div>{{ s.config.name }}</div>
              <small style="color: #999">{{ s.config.description }}</small>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          :disabledDate="disabledDate"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleSimulate">
          开始模拟
        </el-button>
      </el-form-item>
    </el-form>
    

    <!-- 策略参数和说明 -->
    <div v-if="strategy" class="strategy-config">
      <!-- 策略详情描述 -->
      <div class="strategy-description">
        <el-divider>策略详情</el-divider>
        <div v-if="strategy === 'xue_strategy'">
          <h4>薛总高抛低吸策略</h4>
          <p>核心逻辑：</p>
          <ul>
            <li>初始持仓：{{ strategyParams.initialQuantity }} 股</li>
            <li>单次交易：{{ strategyParams.tradeQuantity }} 股</li>
            <li>持仓范围：{{ strategyParams.minHolding }} - {{ strategyParams.maxHolding }} 股</li>
            <li>当股价低于持仓均价 {{ ((1-strategyParams.downThreshold)*100).toFixed(0) }}% 时买入</li>
            <li>当股价高于持仓均价 {{ ((strategyParams.upThreshold-1)*100).toFixed(0) }}% 时卖出</li>
            <li>持仓低于等于{{ strategyParams.minHolding }}股时不卖出</li>
            <li>持仓高于等于{{ strategyParams.maxHolding }}股时不买入</li>
          </ul>
        </div>
        <div v-if="strategy === 'yu_strategy_1'">
          <h4>于博简易策略</h4>
          <p>核心逻辑：</p>
          <ul>
            <li>初始持仓：0 股</li>
            <li>单次交易：{{ strategyParams.tradeQuantity }} 股</li>
            <li>最大持仓：{{ strategyParams.maxHolding }} 股</li>
            <li>当日内最低价比开盘价下跌 {{ ((1-strategyParams.downThreshold)*100).toFixed(0) }}% 时买入</li>
            <li>当日内最高价比持仓均价上涨 {{ ((strategyParams.upThreshold-1)*100).toFixed(0) }}% 时卖出</li>
            <li>持仓低于{{ strategyParams.minHoldingForSell }}股时不卖出</li>
            <li>同一天买入的股票当天不能卖出</li>
          </ul>
        </div>
      </div>

      <!-- 策略参数配置 -->
      <div class="strategy-params">
        <el-divider>参数配置</el-divider>
        <el-form v-if="strategy === 'xue_strategy'" :inline="true">
          <el-form-item label="初始持仓">
            <el-input-number v-model="strategyParams.initialQuantity" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="最小持仓">
            <el-input-number v-model="strategyParams.minHolding" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="最大持仓">
            <el-input-number v-model="strategyParams.maxHolding" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="交易数量">
            <el-input-number v-model="strategyParams.tradeQuantity" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="下跌买入阈值">
            <el-input-number v-model="strategyParams.downThreshold" :min="0" :max="1" :step="0.01" :precision="2" />
          </el-form-item>
          <el-form-item label="上涨卖出阈值">
            <el-input-number v-model="strategyParams.upThreshold" :min="1" :max="2" :step="0.01" :precision="2" />
          </el-form-item>
        </el-form>

        <el-form v-if="strategy === 'yu_strategy_1'" :inline="true">
          <el-form-item label="交易数量">
            <el-input-number v-model="strategyParams.tradeQuantity" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="最大持仓">
            <el-input-number v-model="strategyParams.maxHolding" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="最小卖出持仓">
            <el-input-number v-model="strategyParams.minHoldingForSell" :min="0" :step="10000" />
          </el-form-item>
          <el-form-item label="下跌买入阈值">
            <el-input-number v-model="strategyParams.downThreshold" :min="0" :max="1" :step="0.01" :precision="2" />
          </el-form-item>
          <el-form-item label="上涨卖出阈值">
            <el-input-number v-model="strategyParams.upThreshold" :min="1" :max="2" :step="0.01" :precision="2" />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 结果表格 -->
    <div class="simulation-result" v-loading="loading">
      <el-table
        v-if="simulationResults.length > 0"
        :data="simulationResults"
        style="width: 100%"
        border
      >
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="holdingQuantity" label="持仓数量" width="120">
          <template #default="{ row }">
            {{ row.holdingQuantity.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="holdingAvgPrice" label="持仓均价" width="120">
          <template #default="{ row }">
            {{ row.holdingAvgPrice.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="buyQuantity" label="买入数量" width="120">
          <template #default="{ row }">
            {{ row.buyQuantity > 0 ? row.buyQuantity.toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="buyPrice" label="买入价格" width="120">
          <template #default="{ row }">
            {{ row.buyPrice > 0 ? row.buyPrice.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="sellQuantity" label="卖出数量" width="120">
          <template #default="{ row }">
            {{ row.sellQuantity > 0 ? row.sellQuantity.toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="sellPrice" label="卖出价格" width="120">
          <template #default="{ row }">
            {{ row.sellPrice > 0 ? row.sellPrice.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="totalCost" label="总成本" width="120">
          <template #default="{ row }">
            {{ row.totalCost.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="totalValue" label="总市值" width="120">
          <template #default="{ row }">
            {{ row.totalValue.toLocaleString() }}
          </template>
        </el-table-column>
        
        <el-table-column prop="closePrice" label="收盘价" width="120">
          <template #default="{ row }">
            {{ row.closePrice ? row.closePrice.toFixed(2) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getStockMinuteData, simulateStrategy } from '@/api/strategy'  // 添加 simulateStrategy 导入
import { strategyRegistry } from '@/strategies'
import type { DailySimulationResult } from '@/strategies/base'

const route = useRoute()
const loading = ref(false)
const stockCode = ref('831305')
const exchange = ref('BJSE')
const strategy = ref('xue_strategy')
const simulationResults = ref<DailySimulationResult[]>([])

const availableStrategies = computed(() => strategyRegistry.getAllStrategies())

const defaultDateRange = [
  '2024-10-22',
  '2024-12-21'
]

const dateRange = ref(defaultDateRange)

// 策略参数配置
const strategyParams = ref({
  // 薛总策略参数
  initialQuantity: 100000,
  minHolding: 100000,
  maxHolding: 120000,
  tradeQuantity: 20000,
  downThreshold: 0.95,
  upThreshold: 1.05,
  // 于博策略参数
  minHoldingForSell: 20000
})

// 修改模拟处理函数
const handleSimulate = async () => {
  if (!stockCode.value) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  const fullStockCode = `${stockCode.value}.${exchange.value}`
  
  // 根据不同策略类型，构建对应的参数
  let strategySpecificParams = {}
  if (strategy.value === 'xue_strategy') {
    strategySpecificParams = {
      initialQuantity: strategyParams.value.initialQuantity,
      minHolding: strategyParams.value.minHolding,
      maxHolding: strategyParams.value.maxHolding,
      tradeQuantity: strategyParams.value.tradeQuantity,
      downThreshold: strategyParams.value.downThreshold,
      upThreshold: strategyParams.value.upThreshold
    }
  } else if (strategy.value === 'yu_strategy_1') {
    strategySpecificParams = {
      tradeQuantity: strategyParams.value.tradeQuantity,
      maxHolding: strategyParams.value.maxHolding,
      minHoldingForSell: strategyParams.value.minHoldingForSell,
      downThreshold: strategyParams.value.downThreshold,
      upThreshold: strategyParams.value.upThreshold
    }
  }
  
  const params = {
    code: fullStockCode,
    startDate: dateRange.value[0],
    endDate: dateRange.value[1],
    strategy: strategy.value,
    params: strategySpecificParams
  }
  
  console.log('开始策略模拟:', params)
  
  loading.value = true
  try {
    const response = await simulateStrategy(params)
    console.log('API返回原始数据:', response)
    const data = response.data || response
    
    if (!data || !Array.isArray(data)) {
      console.error('数据格式错误:', { response, data })
      throw new Error('返回的数据格式不正确')
    }
    
    console.log('开始处理模拟结果...')
    simulationResults.value = data
  } catch (error: any) {
    console.error('模拟失败:', error)
    ElMessage.error(`策略模拟失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (stockCode.value && exchange.value) {
    handleSimulate()
  }
})

const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

// 移除 defaultDateRange 的定义和使用
</script>

<style scoped>
.strategy-simulation {
  min-height: 600px;
}

.strategy-config {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.strategy-description {
  margin-bottom: 20px;
}

.strategy-description ul {
  padding-left: 20px;
}

.strategy-description li {
  margin: 8px 0;
}

.strategy-params {
  margin-top: 20px;
}

.strategy-params .el-input-number {
  width: 150px;
}

.simulation-result {
  margin-top: 20px;
  min-height: 400px;
}
</style>
