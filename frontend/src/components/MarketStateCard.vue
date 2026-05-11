<template>
  <el-card class="market-state-card">
    <template #header>
      <div class="card-header">
        <span>市场状态</span>
        <el-button size="small" :loading="loading" @click="handleCalculate">
          计算
        </el-button>
      </div>
    </template>
    
    <div v-if="marketStore.currentMarketState" class="state-content">
      <div class="state-item">
        <span class="label">最终状态:</span>
        <el-tag :type="getStateColor(marketStore.finalState)" size="large">
          {{ marketStore.finalState }}
        </el-tag>
      </div>
      
      <div class="state-item">
        <span class="label">技术状态:</span>
        <span>{{ marketStore.currentMarketState.tech_state }}</span>
      </div>
      
      <div class="state-item">
        <span class="label">大周期:</span>
        <span>{{ marketStore.currentMarketState.cycle_state }}</span>
      </div>
      
      <el-divider />
      
      <div class="state-item">
        <span class="label">建议仓位:</span>
        <el-tag type="success" size="large">
          {{ marketStore.maxPosition }}%
        </el-tag>
      </div>
      
      <div class="state-item">
        <span class="label">ETF操作:</span>
        <span class="action-text">{{ marketStore.etfAction }}</span>
      </div>
      
      <div class="state-item">
        <span class="label">个股操作:</span>
        <span class="action-text">{{ marketStore.individualAction }}</span>
      </div>
    </div>
    
    <el-empty v-else description="暂无数据" :image-size="80" />
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useMarketStore } from '@/store/market'

const marketStore = useMarketStore()

const loading = computed(() => marketStore.loading)

const getStateColor = (state) => {
  const colors = {
    '底部区': 'success',
    '上涨区': 'primary',
    '震荡区': 'warning',
    '陷阱区': 'danger'
  }
  return colors[state] || 'info'
}

const handleCalculate = async () => {
  const result = await marketStore.calculateState()
  if (result.success) {
    ElMessage.success('市场状态计算完成')
  } else {
    ElMessage.error(result.error)
  }
}
</script>

<style scoped>
.market-state-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.state-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.state-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #666;
  font-size: 14px;
}

.action-text {
  font-weight: 500;
  color: #409EFF;
}
</style>
