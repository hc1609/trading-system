# 交易策略系统 - 前端

基于 Vue 3 + Element Plus 的交易策略看板前端应用。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 组件库
- **Pinia** - Vue 状态管理
- **Vue Router** - Vue 路由管理
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化图表库

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 请求封装
│   ├── components/       # 可复用组件
│   │   ├── MarketStateCard.vue
│   │   ├── PositionSummaryCard.vue
│   │   ├── EtfRecommendationCard.vue
│   │   └── RiskStatusCard.vue
│   ├── router/           # 路由配置
│   ├── store/            # Pinia 状态管理
│   │   ├── auth.js       # 认证状态
│   │   ├── market.js     # 市场状态
│   │   └── position.js   # 持仓状态
│   ├── views/            # 页面视图
│   │   ├── Login.vue     # 登录页
│   │   ├── Register.vue  # 注册页
│   │   ├── Dashboard.vue # 主看板页
│   │   ├── Settings.vue  # 设置页
│   │   └── Reports.vue   # 报表页
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html            # HTML 模板
├── vite.config.js        # Vite 配置
└── package.json          # 项目依赖
```

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 生产构建

```bash
npm run build
```

构建产物将输出到 `backend/static/dist` 目录。

### 预览生产构建

```bash
npm run preview
```

## 核心功能

### 1. 认证系统
- 用户登录/注册
- JWT Token 管理
- 路由守卫

### 2. 交易看板
- 市场状态展示
- 持仓汇总
- ETF 操作建议
- 风控状态监控
- 实时数据刷新

### 3. 持仓管理
- 开仓操作
- 平仓操作
- 持仓列表展示
- 交易记录

### 4. 数据可视化
- 市场趋势图表
- 技术指标图表
- 实时数据更新

## API 集成

所有 API 请求通过 Axios 发送,自动携带 JWT Token。

```javascript
import axios from 'axios'

// 自动设置 Token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

// 发起请求
const response = await axios.get('/api/strategy/current/')
```

## 状态管理

使用 Pinia 进行状态管理,主要 store:

- **auth** - 用户认证状态
- **market** - 市场数据和策略状态
- **position** - 持仓和交易数据

```javascript
import { useMarketStore } from '@/store/market'

const marketStore = useMarketStore()
await marketStore.fetchCurrentState()
```

## 组件示例

### MarketStateCard - 市场状态卡片

显示当前市场状态、建议仓位、操作建议。

```vue
<MarketStateCard />
```

### PositionSummaryCard - 持仓汇总卡片

显示持仓数量、类型分布、总市值。

```vue
<PositionSummaryCard />
```

## 开发规范

### 代码风格
- 使用 Vue 3 Composition API
- 使用 `<script setup>` 语法
- 组件名使用 PascalCase
- 文件名使用 camelCase

### 组件设计
- 单一职责原则
- Props 向下传递,Events 向上触发
- 状态管理使用 Pinia

### 样式
- 使用 scoped 样式
- 遵循 Element Plus 设计规范
- 响应式设计

## 环境变量

创建 `.env` 文件配置环境变量:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 部署

### 开发环境

```bash
npm run dev
```

### 生产环境

1. 构建前端:
```bash
npm run build
```

2. Django 会自动提供静态文件服务。

3. 访问: http://localhost:8000

## 相关文档

- [API 文档](../API_DOCUMENTATION.md)
- [项目交付文档](../DELIVERY.md)
- [Element Plus 文档](https://element-plus.org/)
- [Vue 3 文档](https://vuejs.org/)

## 开发进度

- ✅ 项目初始化
- ✅ 认证页面 (登录/注册)
- ✅ 主看板页面
- ✅ 状态管理 (Pinia)
- ✅ 路由配置
- ✅ 核心组件 (4个卡片组件)
- ✅ ECharts 图表集成
- ⏳ 交易报表页面
- ⏳ 箱体分析页面
- ⏳ 做T管理页面
- ⏳ 响应式优化
- ⏳ 单元测试

## 许可证

MIT License
