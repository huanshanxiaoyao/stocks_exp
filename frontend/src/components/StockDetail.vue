<template>
  <el-card class="stock-detail">
    <el-form :inline="true" @submit.prevent="handleQuery">
      <el-form-item label="股票代码">
        <el-input
          v-model="stockCode"
          placeholder="请输入股票代码，如：600519"
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
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :default-value="defaultDateRange"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleQuery">
          查询
        </el-button>
      </el-form-item>
    </el-form>

    <div ref="chartRef" style="height: 500px" v-loading="loading" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { getStockDailyData } from '@/api/stock'
import { ElMessage } from 'element-plus'
import type { StockQueryParams } from '@/types/stock'
import { useRoute } from 'vue-router'

const chartRef = ref<HTMLElement>()
const loading = ref(false)
const stockCode = ref('')
const exchange = ref('XSHG')
let chart: echarts.ECharts | null = null

const defaultDateRange = [
  '2024-10-22',
  '2024-12-21'
]

const dateRange = ref(defaultDateRange)

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    const resizeHandler = () => chart?.resize()
    window.addEventListener('resize', resizeHandler)
    return () => window.removeEventListener('resize', resizeHandler)
  }
}

const updateChart = (data: any[]) => {
  if (!chart) return
  
  // 添加更详细的数据日志
  console.log('图表数据处理:', {
    dates: data.map(item => item.date),
    values: data.map(item => [item.open, item.high, item.low, item.close]),
    rawData: data[0]
  })
  
  // 创建一个映射，用于在 tooltip 中查找正确的数据
  const dataMap = new Map()
  data.forEach(item => {
    dataMap.set(item.date, item)
  })
  
  const chartData = data.map(item => {
    const open = parseFloat(item.open)
    const close = parseFloat(item.close)
    const high = parseFloat(item.high)
    const low = parseFloat(item.low)
    
    console.log(`日期: ${item.date}, 开盘: ${open}, 收盘: ${close}, 涨跌: ${close > open ? '上涨' : '下跌'}`)
    
    // 修改数据顺序为 ECharts 期望的格式：[开盘价, 收盘价, 最低价, 最高价]
    return [open, close, low, high]
  })
  
  const option = {
    title: {
      text: `${stockCode.value} 股票K线图`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const item = params[0]
        const date = item.axisValue
        const stockData = dataMap.get(date)
        
        if (stockData) {
          const open = parseFloat(stockData.open)
          const high = parseFloat(stockData.high)
          const low = parseFloat(stockData.low)
          const close = parseFloat(stockData.close)
          const color = close >= open ? '#f56c6c' : '#67c23a'
          
          return `
            日期：${date}<br/>
            <span style="color:${color}">
            开盘价：${open.toFixed(2)}<br/>
            最高价：${high.toFixed(2)}<br/>
            最低价：${low.toFixed(2)}<br/>
            收盘价：${close.toFixed(2)}<br/>
            涨跌：${((close - open) / open * 100).toFixed(2)}%
            </span>
          `
        }
        
        return '数据加载中...'
      }
    },
    grid: {
      left: '10%',  // 调整左边距
      right: '10%', // 调整右边距
      bottom: '15%', // 调整底部边距
      top: '15%'    // 调整顶部边距
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date),
      axisLabel: { 
        rotate: 45,
        formatter: (value: string) => value.substring(5)
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [{
      name: '股价区间',
      type: 'candlestick',
      data: chartData,
      itemStyle: {
        // 修改颜色设置：红色表示上涨，绿色表示下跌
        color: '#f56c6c',     // 上涨颜色（红色）
        color0: '#67c23a',    // 下跌颜色（绿色）
        borderColor: '#f56c6c',     // 上涨边框颜色
        borderColor0: '#67c23a'     // 下跌边框颜色
      }
    }]
  }
  
  chart.setOption(option, true)
}

const handleQuery = async () => {
  if (!stockCode.value) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  const fullStockCode = `${stockCode.value}.${exchange.value}`
  console.log('开始查询数据:', { fullStockCode, dateRange: dateRange.value })
  
  loading.value = true
  try {
    const response = await getStockDailyData({
      code: fullStockCode,
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    })
    
    console.log('API返回原始数据:', response)
    const data = response.data || response  // 兼容两种可能的数据结构
    
    if (!data || !Array.isArray(data)) {
      console.error('数据格式错误:', { response, data })
      throw new Error('返回的数据格式不正确')
    }
    
    console.log('开始处理图表数据...')
    updateChart(data)
  } catch (error: any) {
    console.error('获取数据失败:', error)
    ElMessage.error(`获取数据失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const route = useRoute()

// 从 URL 参数中获取初始值
stockCode.value = route.query.code?.toString() || ''
exchange.value = route.query.exchange?.toString() || 'XSHG'

onMounted(() => {
  initChart()
  // 如果有初始参数，自动查询
  if (stockCode.value && exchange.value) {
    handleQuery()
  }
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', () => chart?.resize())
})
</script>

<style scoped>
.stock-detail {
  min-height: 600px;
}
</style>