<template>
  <el-card class="risk-card">
    <template #header>
      <span>风控状态</span>
    </template>
    
    <div v-if="positionStore.riskStatus" class="risk-content">
      <div class="risk-status">
        <el-tag :type="positionStore.riskStatus.risk_lock ? 'danger' : 'success'" size="large">
          {{ positionStore.riskStatus.risk_lock ? '已锁定' : '正常' }}
        </el-tag>
      </div>
      
      <el-divider />
      
      <div class="risk-item">
        <span class="label">日收益率:</span>
        <span :class="getReturnClass(positionStore.riskStatus.daily_return)">
          {{ positionStore.riskStatus.daily_return }}%
        </span>
      </div>
      
      <div class="risk-item">
        <span class="label">周收益率:</span>
        <span :class="getReturnClass(positionStore.riskStatus.weekly_return)">
          {{ positionStore.riskStatus.weekly_return }}%
        </span>
      </div>
      
      <div class="risk-item">
        <span class="label">连续亏损:</span>
        <span>{{ positionStore.riskStatus.consecutive_losses }} 次</span>
      </div>
      
      <div class="risk-item">
        <span class="label">今日交易:</span>
        <span>{{ positionStore.riskStatus.today_trades }} 次</span>
      </div>
      
      <el-alert
        v-if="positionStore.riskStatus.risk_lock"
        :title="positionStore.riskStatus.lock_reason"
        type="error"
        :closable="false"
        show-icon
      />
    </div>
    
    <el-empty v-else description="暂无数据" :image-size="80" />
  </el-card>
</template>

<script setup>
import { usePositionStore } from '@/store/position'

const positionStore = usePositionStore()

const getReturnClass = (value) => {
  if (!value) return ''
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}
</script>

<style scoped>
.risk-card {
  height: 100%;
}

.risk-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-status {
  text-align: center;
  padding: 16px 0;
}

.risk-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #666;
  font-size: 14px;
}

.positive {
  color: #67C23A;
  font-weight: 600;
}

.negative {
  color: #F56C6C;
  font-weight: 600;
}
</style>
