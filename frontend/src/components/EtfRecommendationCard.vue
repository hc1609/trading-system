<template>
  <el-card class="etf-card">
    <template #header>
      <span>ETF建议</span>
    </template>
    
    <div v-if="positionStore.etfRecommendation" class="etf-content">
      <div class="recommendation">
        <el-tag 
          :type="getActionType(positionStore.etfRecommendation.recommendation)" 
          size="large"
        >
          {{ positionStore.etfRecommendation.recommendation }}
        </el-tag>
      </div>
      
      <el-divider />
      
      <div class="info-item">
        <span class="label">市场状态:</span>
        <span>{{ positionStore.etfRecommendation.market_state }}</span>
      </div>
      
      <div class="info-item">
        <span class="label">大周期:</span>
        <span>{{ positionStore.etfRecommendation.cycle_state }}</span>
      </div>
    </div>
    
    <el-empty v-else description="暂无建议" :image-size="80" />
  </el-card>
</template>

<script setup>
import { usePositionStore } from '@/store/position'

const positionStore = usePositionStore()

const getActionType = (action) => {
  if (!action) return 'info'
  if (action.includes('买入')) return 'success'
  if (action.includes('卖出') || action.includes('清仓')) return 'danger'
  if (action.includes('持有')) return 'warning'
  return 'info'
}
</script>

<style scoped>
.etf-card {
  height: 100%;
}

.etf-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation {
  text-align: center;
  padding: 16px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #666;
  font-size: 14px;
}
</style>
