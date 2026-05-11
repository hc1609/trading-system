<template>
  <el-container class="dashboard-container">
    <!-- 顶部导航 -->
    <el-header class="dashboard-header">
      <div class="header-left">
        <h1>交易策略看板</h1>
        <el-button :loading="refreshing" @click="handleRefresh" :icon="Refresh">
          刷新数据
        </el-button>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32">{{ authStore.user?.username?.charAt(0) }}</el-avatar>
            <span class="username">{{ authStore.user?.username }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main class="dashboard-main">
      <!-- 第一行:市场状态 -->
      <el-row :gutter="20" class="status-row">
        <el-col :span="6">
          <MarketStateCard />
        </el-col>
        <el-col :span="6">
          <PositionSummaryCard />
        </el-col>
        <el-col :span="6">
          <EtfRecommendationCard />
        </el-col>
        <el-col :span="6">
          <RiskStatusCard />
        </el-col>
      </el-row>

      <!-- 第二行:持仓列表和事件 -->
      <el-row :gutter="20" class="content-row">
        <el-col :span="16">
          <el-card class="positions-card">
            <template #header>
              <div class="card-header">
                <span>持仓列表</span>
                <el-button type="primary" size="small" @click="showOpenDialog = true">
                  开仓
                </el-button>
              </div>
            </template>
            <el-table :data="positionStore.holdingPositions" style="width: 100%">
              <el-table-column prop="symbol" label="代码" width="100" />
              <el-table-column prop="name" label="名称" width="120" />
              <el-table-column prop="type" label="类型" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.type === 'etf' ? 'success' : 'primary'">
                    {{ row.type === 'etf' ? 'ETF' : '个股' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="buy_price" label="成本价" width="100" />
              <el-table-column prop="quantity" label="数量" width="100" />
              <el-table-column prop="stop_loss" label="止损价" width="100" />
              <el-table-column prop="buy_date" label="买入日期" width="120" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button type="danger" size="small" @click="handleClosePosition(row)">
                    平仓
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="events-card">
            <template #header>
              <span>活跃事件</span>
            </template>
            <el-empty v-if="marketStore.activeEvents.length === 0" description="暂无活跃事件" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="event in marketStore.activeEvents"
                :key="event.id"
                :timestamp="event.start_date"
                placement="top"
              >
                <el-card>
                  <h4>{{ event.event_name }}</h4>
                  <p>{{ event.description }}</p>
                  <el-tag size="small" type="warning">
                    修正: {{ event.correction_value }}
                  </el-tag>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第三行:图表区域 -->
      <el-row :gutter="20" class="chart-row">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>市场趋势</span>
            </template>
            <div ref="trendChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>技术指标</span>
            </template>
            <div ref="indicatorChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 开仓对话框 -->
    <el-dialog v-model="showOpenDialog" title="开仓" width="500px">
      <el-form :model="openForm" label-width="80px">
        <el-form-item label="股票代码">
          <el-input v-model="openForm.symbol" placeholder="如: 000001" />
        </el-form-item>
        <el-form-item label="股票名称">
          <el-input v-model="openForm.name" placeholder="如: 平安银行" />
        </el-form-item>
        <el-form-item label="买入价格">
          <el-input-number v-model="openForm.buy_price" :precision="2" :step="0.01" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="openForm.quantity" :step="100" />
        </el-form-item>
        <el-form-item label="止损价">
          <el-input-number v-model="openForm.stop_loss" :precision="2" :step="0.01" />
        </el-form-item>
        <el-form-item label="交易逻辑">
          <el-select v-model="openForm.logic" placeholder="选择交易逻辑">
            <el-option label="趋势交易" value="trend" />
            <el-option label="箱体操作" value="box" />
            <el-option label="短线交易" value="short_term" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOpenDialog = false">取消</el-button>
        <el-button type="primary" @click="handleOpenPosition">确认开仓</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'
import { useMarketStore } from '@/store/market'
import { usePositionStore } from '@/store/position'
import MarketStateCard from '@/components/MarketStateCard.vue'
import PositionSummaryCard from '@/components/PositionSummaryCard.vue'
import EtfRecommendationCard from '@/components/EtfRecommendationCard.vue'
import RiskStatusCard from '@/components/RiskStatusCard.vue'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()
const marketStore = useMarketStore()
const positionStore = usePositionStore()

const refreshing = ref(false)
const showOpenDialog = ref(false)
const trendChartRef = ref(null)
const indicatorChartRef = ref(null)
let trendChart = null
let indicatorChart = null

const openForm = reactive({
  symbol: '',
  name: '',
  buy_price: 0,
  quantity: 100,
  stop_loss: 0,
  logic: 'trend'
})

// 刷新所有数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      marketStore.refreshAll(),
      positionStore.refreshAll()
    ])
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 开仓
const handleOpenPosition = async () => {
  const result = await positionStore.openPosition(openForm)
  if (result.success) {
    ElMessage.success('开仓成功')
    showOpenDialog.value = false
    // 重置表单
    Object.assign(openForm, {
      symbol: '',
      name: '',
      buy_price: 0,
      quantity: 100,
      stop_loss: 0,
      logic: 'trend'
    })
  } else {
    ElMessage.error(result.error)
  }
}

// 平仓
const handleClosePosition = async (position) => {
  try {
    await ElMessageBox.confirm(
      `确认平仓 ${position.name}?`,
      '确认操作',
      { type: 'warning' }
    )
    
    const result = await positionStore.closePosition(position.id, {
      sell_price: position.buy_price, // 实际应该获取当前价格
      quantity: position.quantity
    })
    
    if (result.success) {
      ElMessage.success('平仓成功')
    } else {
      ElMessage.error(result.error)
    }
  } catch {
    // 用户取消
  }
}

// 用户菜单
const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}

// 初始化图表
const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    // 示例数据,实际应从API获取
    trendChart.setOption({
      title: { text: '指数走势' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [3200, 3250, 3180, 3220, 3280],
        type: 'line',
        smooth: true
      }]
    })
  }
  
  if (indicatorChartRef.value) {
    indicatorChart = echarts.init(indicatorChartRef.value)
    indicatorChart.setOption({
      title: { text: 'RSI指标' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五']
      },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [{
        data: [45, 52, 38, 55, 62],
        type: 'line',
        smooth: true,
        areaStyle: {}
      }]
    })
  }
}

// 生命周期
onMounted(async () => {
  await handleRefresh()
  initCharts()
  
  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    trendChart?.resize()
    indicatorChart?.resize()
  })
})

onUnmounted(() => {
  trendChart?.dispose()
  indicatorChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.dashboard-header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.dashboard-main {
  padding: 20px;
}

.status-row,
.content-row,
.chart-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}

:deep(.el-card) {
  margin-bottom: 20px;
}
</style>
