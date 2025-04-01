<template>
  <div class="home">
    <el-card class="feature-card">
      <template #header>
        <div class="card-header">
          <span>股票交易分析工具</span>
        </div>
      </template>
      <div class="feature-list">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="box-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>个股K线详情</span>
                </div>
              </template>
              <div class="card-content">
                <p>查看个股历史K线数据、交易量等详细信息</p>
                <el-button 
                  type="primary" 
                  @click="$router.push('/stock-detail?code=600519&exchange=XSHG')"
                >
                  立即查看
                </el-button>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="box-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>策略模拟</span>
                </div>
              </template>
              <div class="card-content">
                <p>使用选定的交易策略进行历史数据回测模拟</p>
                <el-button 
                  type="primary" 
                  @click="$router.push('/strategy')"
                >
                  开始模拟
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.home {
  padding: 20px;
}

.feature-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.feature-list {
  margin-top: 20px;
}

.box-card {
  height: 200px;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100px;
}

.card-content p {
  color: #666;
  text-align: center;
}
</style>