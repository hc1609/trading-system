<template>
  <el-container class="settings-container">
    <el-header class="settings-header">
      <h1>系统设置</h1>
      <el-button @click="$router.push('/')">返回看板</el-button>
    </el-header>
    
    <el-main class="settings-main">
      <el-card>
        <template #header>
          <span>用户配置</span>
        </template>
        
        <el-form :model="profileForm" label-width="120px">
          <el-form-item label="初始资金">
            <el-input-number 
              v-model="profileForm.total_capital" 
              :precision="2"
              :step="10000"
            />
          </el-form-item>
          
          <el-form-item label="风险偏好">
            <el-select v-model="profileForm.risk_preference">
              <el-option label="保守" value="conservative" />
              <el-option label="稳健" value="moderate" />
              <el-option label="激进" value="aggressive" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="单笔风险(%)">
            <el-input-number 
              v-model="profileForm.per_trade_risk" 
              :precision="1"
              :step="0.5"
              :min="1"
              :max="5"
            />
          </el-form-item>
          
          <el-form-item label="止损率(%)">
            <el-input-number 
              v-model="profileForm.stop_loss_rate" 
              :precision="1"
              :step="0.5"
              :min="3"
              :max="10"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSave">保存配置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()

const profileForm = ref({
  total_capital: 100000,
  risk_preference: 'moderate',
  per_trade_risk: 2.0,
  stop_loss_rate: 5.0
})

onMounted(() => {
  const profile = authStore.userProfile
  if (profile) {
    profileForm.value = {
      total_capital: profile.total_capital || 100000,
      risk_preference: profile.risk_preference || 'moderate',
      per_trade_risk: profile.per_trade_risk || 2.0,
      stop_loss_rate: profile.stop_loss_rate || 5.0
    }
  }
})

const handleSave = async () => {
  const result = await authStore.updateProfile(profileForm.value)
  if (result.success) {
    ElMessage.success('配置保存成功')
  } else {
    ElMessage.error(result.error)
  }
}
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.settings-header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.settings-header h1 {
  margin: 0;
  font-size: 20px;
}

.settings-main {
  padding: 20px;
}
</style>
