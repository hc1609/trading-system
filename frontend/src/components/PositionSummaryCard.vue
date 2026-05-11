<template>
  <el-card class="position-summary-card">
    <template #header>
      <span>持仓汇总</span>
    </template>
    
    <div v-if="positionStore.summary" class="summary-content">
      <div class="summary-item">
        <span class="label">总持仓:</span>
        <el-tag type="primary" size="large">
          {{ positionStore.summary.total_positions }} 只
        </el-tag>
      </div>
      
      <div class="summary-item">
        <span class="label">ETF:</span>
        <span>{{ positionStore.summary.etf_count }} 只</span>
      </div>
      
      <div class="summary-item">
        <span class="label">个股:</span>
        <span>{{ positionStore.summary.individual_count }} 只</span>
      </div>
      
      <el-divider />
      
      <div class="summary-item total">
        <span class="label">总市值:</span>
        <span class="value">¥ {{ formatMoney(positionStore.totalValue) }}</span>
      </div>
    </div>
    
    <el-empty v-else description="暂无数据" :image-size="80" />
  </el-card>
</template>

<script setup>
import { usePositionStore } from '@/store/position'

const positionStore = usePositionStore()

const formatMoney = (value) => {
  if (!value) return '0.00'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}
</script>

<style scoped>
.position-summary-card {
  height: 100%;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-item.total {
  padding-top: 8px;
  font-size: 16px;
}

.label {
  color: #666;
  font-size: 14px;
}

.value {
  font-weight: 600;
  color: #67C23A;
  font-size: 18px;
}
</style>
