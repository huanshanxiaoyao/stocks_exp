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
  
  console.log('图表数据处理:', {
    dates: data.map(item => item.date),
    values: data.map(item => [item.open, item.close, item.low, item.high])
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
        const data = item.data
        const color = data[1] >= data[0] ? '#f56c6c' : '#67c23a'
        return `
          日期：${item.axisValue}<br/>
          <span style="color:${color}">
          开盘价：${data[0].toFixed(2)}<br/>
          收盘价：${data[1].toFixed(2)}<br/>
          最低价：${data[2].toFixed(2)}<br/>
          最高价：${data[3].toFixed(2)}<br/>
          涨跌：${((data[1] - data[0]) / data[0] * 100).toFixed(2)}%
          </span>
        `
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
      data: data.map(item => [
        item.open,   // 开盘价
        item.close,  // 收盘价
        item.low,    // 最低价
        item.high    // 最高价
      ]),
      itemStyle: {
        color: '#f56c6c',     // 上涨颜色
        color0: '#67c23a',    // 下跌颜色
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
  loading.value = true
  try {
    const data = await getStockDailyData({
      code: fullStockCode,
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    })
    console.log('获取到的数据:', data)  // 添加数据日志
    updateChart(data)
  } catch (error: any) {
    console.error('获取数据失败:', error)
    ElMessage.error(`获取数据失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initChart()
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