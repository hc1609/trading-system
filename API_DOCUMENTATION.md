# API接口文档

**版本**: V1.0  
**基础URL**: `http://localhost:8000/api`  
**认证方式**: JWT Bearer Token

---

## 认证说明

### 获取Token
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

# 响应
{
  "user": {...},
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 使用Token
所有需要认证的请求需要在Header中添加:
```
Authorization: Bearer <access_token>
```

### 刷新Token
```bash
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

---

## API端点清单

### 1. 用户认证 (`/api/auth/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register/` | 用户注册 | ❌ |
| POST | `/api/auth/login/` | 用户登录 | ❌ |
| POST | `/api/auth/logout/` | 用户登出 | ✅ |
| POST | `/api/auth/refresh/` | 刷新Token | ❌ |
| GET | `/api/auth/profile/` | 获取用户信息 | ✅ |
| PUT | `/api/auth/profile/` | 更新用户配置 | ✅ |

---

### 2. 市场数据 (`/api/market/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/market/data/` | 获取市场数据列表 | ✅ |
| POST | `/api/market/data/` | 创建市场数据 | ✅ |
| GET | `/api/market/data/{id}/` | 获取市场数据详情 | ✅ |
| PUT | `/api/market/data/{id}/` | 更新市场数据 | ✅ |
| DELETE | `/api/market/data/{id}/` | 删除市场数据 | ✅ |
| GET | `/api/market/indicators/` | 获取技术指标列表 | ✅ |
| GET | `/api/market/latest/` | 获取最新市场数据 | ✅ |
| POST | `/api/market/calculate/` | 手动触发指标计算 | ✅ |

**查询参数**:
- `index_code`: 指数代码 (如: 399006.SZ)
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

---

### 3. 策略状态 (`/api/strategy/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/strategy/states/` | 获取市场状态列表 | ✅ |
| GET | `/api/strategy/current/` | 获取当前市场状态 | ✅ |
| POST | `/api/strategy/calculate/` | 计算市场状态 | ✅ |
| GET | `/api/strategy/events/` | 获取事件日历列表 | ✅ |
| GET | `/api/strategy/events/active/` | 获取活跃事件 | ✅ |

**市场状态计算响应示例**:
```json
{
  "message": "市场状态计算完成",
  "data": {
    "id": 1,
    "date": "2026-04-21",
    "tech_state": "底部区",
    "cycle_state": "震荡期",
    "final_state": "底部区",
    "max_position": 100,
    "etf_action": "分批买入",
    "individual_action": "可积极选股"
  }
}
```

---

### 4. 持仓管理 (`/api/position/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/position/positions/` | 获取持仓列表 | ✅ |
| POST | `/api/position/open/` | 开仓 | ✅ |
| POST | `/api/position/{id}/close/` | 平仓 | ✅ |
| GET | `/api/position/positions/{id}/` | 获取持仓详情 | ✅ |
| PUT | `/api/position/positions/{id}/` | 更新持仓 | ✅ |
| GET | `/api/position/etf/recommendation/` | 获取ETF建议 | ✅ |
| GET | `/api/position/summary/` | 获取持仓汇总 | ✅ |
| GET | `/api/position/transactions/` | 获取交易记录 | ✅ |
| GET | `/api/position/keypoints/` | 获取关键点信号 | ✅ |

**开仓请求示例**:
```json
POST /api/position/open/
{
  "symbol": "000001",
  "name": "平安银行",
  "buy_price": 15.50,
  "quantity": 1000,
  "stop_loss": 14.73,
  "logic": "trend",
  "keypoint_type": "突破关键点"
}
```

---

### 5. 箱体分析 (`/api/box/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/box/` | 获取箱体列表 | ✅ |
| POST | `/api/box/` | 创建箱体 | ✅ |
| GET | `/api/box/{id}/` | 获取箱体详情 | ✅ |
| PUT | `/api/box/{id}/` | 更新箱体 | ✅ |
| DELETE | `/api/box/{id}/` | 删除箱体 | ✅ |
| GET | `/api/box/{id}/analysis/` | 获取箱体分析 | ✅ |

**查询参数**:
- `symbol`: 股票代码
- `status`: 状态 (active/broken_up/broken_down)

---

### 6. 做T管理 (`/api/daytrade/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/daytrade/records/` | 获取做T记录 | ✅ |
| POST | `/api/daytrade/records/` | 创建做T记录 | ✅ |
| GET | `/api/daytrade/stats/` | 获取做T统计 | ✅ |
| GET | `/api/daytrade/status/` | 获取做T状态 | ✅ |

**做T状态响应示例**:
```json
{
  "allowed": true,
  "reason": "",
  "stats": {
    "success_rate": 85.00,
    "total_count": 20,
    "success_count": 17,
    "consecutive_failures": 0,
    "is_paused": false
  }
}
```

---

### 7. 风险管理 (`/api/risk/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/risk/status/` | 获取风控状态列表 | ✅ |
| GET | `/api/risk/current/` | 获取当前风控状态 | ✅ |
| POST | `/api/risk/reset/` | 重置风控状态 | ✅ |
| GET | `/api/risk/logs/` | 获取风控日志 | ✅ |

**风控状态响应示例**:
```json
{
  "id": 1,
  "date": "2026-04-21",
  "total_capital": 100000.00,
  "daily_return": -0.50,
  "weekly_return": -1.20,
  "consecutive_losses": 0,
  "today_trades": 2,
  "risk_lock": false
}
```

---

### 8. 配置管理 (`/api/config/`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/config/` | 获取配置列表 | ✅ |
| POST | `/api/config/` | 创建配置 | ✅ |
| PUT | `/api/config/{id}/` | 更新配置 | ✅ |
| DELETE | `/api/config/{id}/` | 删除配置 | ✅ |
| POST | `/api/config/reset/` | 重置为默认配置 | ✅ |

---

## 响应格式

### 成功响应
```json
{
  "message": "操作成功",
  "data": {...}
}
```

### 错误响应
```json
{
  "error": "错误信息"
}
```

### 分页响应
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/...?page=2",
  "previous": null,
  "results": [...]
}
```

---

## HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 使用示例

### Python示例

```python
import requests

# 登录获取Token
response = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'testuser',
    'password': 'test123456'
})
token = response.json()['access']

# 设置认证Header
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 获取当前市场状态
response = requests.get(
    'http://localhost:8000/api/strategy/current/',
    headers=headers
)
print(response.json())

# 开仓
response = requests.post(
    'http://localhost:8000/api/position/open/',
    headers=headers,
    json={
        'symbol': '000001',
        'name': '平安银行',
        'buy_price': 15.50,
        'quantity': 1000,
        'logic': 'trend'
    }
)
print(response.json())
```

### JavaScript示例

```javascript
// 登录
const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'testuser',
    password: 'test123456'
  })
});

const {access: token} = await loginResponse.json();

// 获取市场状态
const stateResponse = await fetch('http://localhost:8000/api/strategy/current/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const marketState = await stateResponse.json();
console.log(marketState);
```

---

## 注意事项

1. **Token有效期**: Access Token 24小时有效,Refresh Token 7天有效
2. **分页**: 所有列表接口支持分页,默认每页20-30条
3. **日期格式**: 使用 ISO 8601 格式 (YYYY-MM-DD)
4. **权限**: 所有业务接口都需要认证
5. **限流**: 建议客户端添加请求限流,避免触发服务器限流

---

## API完成度

| 模块 | 端点数 | 状态 |
|------|--------|------|
| 用户认证 | 6 | ✅ 100% |
| 市场数据 | 8 | ✅ 100% |
| 策略状态 | 5 | ✅ 100% |
| 持仓管理 | 9 | ✅ 100% |
| 箱体分析 | 6 | ✅ 100% |
| 做T管理 | 4 | ✅ 100% |
| 风险管理 | 4 | ✅ 100% |
| 配置管理 | 5 | ✅ 100% |
| **总计** | **47个** | **✅ 100%** |

---

**文档更新日期**: 2026-04-21  
**API版本**: V1.0  
**状态**: 全部完成 ✅
