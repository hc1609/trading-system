<template>
  <el-container class="reports-container">
    <el-header class="reports-header">
      <h1>交易报表</h1>
      <el-button @click="$router.push('/')">返回看板</el-button>
    </el-header>
    
    <el-main class="reports-main">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>交易统计</span>
            </template>
            <el-empty description="功能开发中..." />
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
// 交易报表页面 - 待实现
</script>

<style scoped>
.reports-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.reports-header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.reports-header h1 {
  margin: 0;
  font-size: 20px;
}

.reports-main {
  padding: 20px;
}
</style>
