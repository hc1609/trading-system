# 交易策略系统 - 进度报告

**更新日期**: 2026-04-21  
**当前阶段**: 第三阶段 - 核心业务逻辑实现

---

## 总体进度

| 阶段 | 状态 | 完成度 | 说明 |
|------|------|--------|------|
| 第一阶段:项目初始化 | ✅ 完成 | 100% | Django项目结构、配置文件 |
| 第二阶段:数据库模型 | ✅ 完成 | 100% | 16个数据模型 |
| 第三阶段:核心业务逻辑 | 🚧 进行中 | 60% | 技术指标、状态判断、风险管理等 |
| 第四阶段:API接口 | ⏳ 待开始 | 10% | 仅完成用户认证API |
| 第五阶段:前端页面 | ⏳ 待开始 | 0% | Vue 3项目待初始化 |
| 第六阶段:定时任务 | ⏳ 待开始 | 0% | Celery配置待完善 |
| 第七阶段:纪律提醒 | ⏳ 待开始 | 0% | 前后端验证待实现 |
| 第八阶段:测试优化 | ⏳ 待开始 | 0% | 测试用例待编写 |
| 第九阶段:部署配置 | ⏳ 待开始 | 0% | 生产环境待配置 |

**总体完成度**: 约 **35%**

---

## 本次更新内容

### ✅ 新增核心业务逻辑服务

#### 1. 技术指标计算服务 (`apps/market/services/`)

**文件**: `technical_indicator_calculator.py`

**功能**:
- ✅ RSI指标计算(14日默认)
- ✅ 移动平均线计算(MA5/MA20/MA60)
- ✅ MACD指标计算(DIF/DEA/MACD柱)
- ✅ OBV累积能量线计算
- ✅ 量比计算
- ✅ 涨跌幅计算
- ✅ 背离检测(顶背离/底背离)
- ✅ OBV趋势分析
- ✅ 振幅计算

**技术实现**:
- 使用NumPy进行高效数值计算
- 支持自定义参数
- 完整的边界条件处理

#### 2. 量价关系分析服务 (`apps/market/services/`)

**文件**: `volume_price_service.py`

**功能**:
- ✅ 量价关系矩阵分析(9种组合)
- ✅ OBV信号分析
- ✅ 放量突破检测
- ✅ 缩量检测

**分析规则**:
```
放量大涨 → 多头力量强 → 持有或加仓
缩量大涨 → 多头逼空 → 可持有
放量大跌 → 空头力量强 → 减仓或离场
缩量大跌 → 空头逼多 → 离场观望
放量滞涨 → 多空焦灼 → 警惕
```

#### 3. 大盘状态判断服务 (`apps/strategy/services/`)

**文件**: `market_state_calculator.py`

**核心功能**:

##### 技术状态判断
按优先级判断:
1. 陷阱区: 20日最大涨幅>8% 且 5日振幅<3% 且 量斜度下降>5日
2. 底部区: (20日跌幅<-8% 且 RSI<35) 或 20日跌幅<-12% 或 RSI<25
3. 上涨区: 20日涨幅>5% 或 RSI>70
4. 震荡区: 20日涨跌幅在-5%到+5%之间

##### 大周期状态判断
按优先级判断:
1. 主升浪: 20日涨幅>10% 且 RSI>65 且 沿5日线上涨
2. 赶顶期: 20日涨幅>10% 且 出现顶背离
3. 正常趋势: 20日涨幅3%-10% 且 RSI 50-65
4. 下跌期: 20日跌幅>5% 或 跌破60日线
5. 震荡期: 不满足上述条件

##### 事件修正计算
- 支持多事件叠加
- 按优先级应用修正
- 限制修正范围在-2到+2

##### 综合状态输出
- 技术状态 + 事件修正 → 最终状态
- 自动计算建议仓位上限
- 生成ETF和个股操作建议

##### 分级离场判断
- 一级离场: 顶背离 → 卖出1/3
- 二级离场: 跌破10日线 → 再卖1/3
- 三级离场: 跌破20日线 → 清仓

#### 4. 风险管理服务 (`apps/risk/services/`)

**文件**: `risk_manager.py`

**功能**:
- ✅ 仓位计算(基于风险比例)
- ✅ 单日回撤监控(阈值-3%)
- ✅ 周回撤监控(阈值-6%)
- ✅ 连续亏损保护(2次触发)
- ✅ 单笔交易风险检查
- ✅ 仓位上限检查
- ✅ 止损价计算
- ✅ 止盈价计算
- ✅ 风险收益比计算

**计算公式**:
```python
仓位 = (总资金 × 风险比例) / 止损幅度
例: (100,000 × 2%) / 5% = 40,000元
```

#### 5. ETF策略服务 (`apps/position/services/`)

**文件**: `etf_service.py`

**功能**:
- ✅ 根据市场状态生成ETF操作建议
- ✅ 分批买入计算(25% + 25% + 25%)
- ✅ 止损位计算(常规-5%, 主升浪-10%)
- ✅ 止盈信号检测(背离判断)

**策略映射**:
```
底部区 → 分批买入
震荡区 → 持有不动
上涨区 → 持有或分批卖出
主升浪 → 坚定持有
赶顶期 → 分级离场
陷阱区 → 只卖不买
下跌期 → 清仓观望
```

---

## 已创建文件清单

### 业务逻辑服务 (5个文件)
1. `backend/apps/market/services/technical_indicator_calculator.py` (231行)
2. `backend/apps/market/services/volume_price_service.py` (162行)
3. `backend/apps/strategy/services/market_state_calculator.py` (294行)
4. `backend/apps/risk/services/risk_manager.py` (260行)
5. `backend/apps/position/services/etf_service.py` (191行)

**总计**: 约 **1,138行** 核心业务逻辑代码

---

## 待完成的核心服务

### 高优先级
1. ⏳ **关键点识别服务** (`apps/position/services/keypoint_service.py`)
   - 突破关键点检测
   - 自然回撤关键点检测
   - 连续关键点检测
   - 反转关键点检测

2. ⏳ **开仓检查服务** (`apps/position/services/open_position_service.py`)
   - 大盘状态检查
   - 关键点信号验证
   - 成交量验证
   - 风控状态检查
   - 仓位上限检查

3. ⏳ **金字塔加仓服务** (`apps/position/services/pyramid_service.py`)
   - 加仓条件检查
   - 加仓规模计算
   - 止损位调整

4. ⏳ **箱体分析服务** (`apps/box/services/box_identifier.py`)
   - 箱体识别算法
   - 位置判断
   - 操作建议生成

5. ⏳ **做T管理服务** (`apps/daytrade/services/daytrade_manager.py`)
   - 做T开关控制
   - 成功率统计
   - 暂停条件检查

6. ⏳ **数据同步服务** (`apps/sync/services/tushare_client.py`)
   - Tushare API封装
   - 增量同步策略
   - 错误重试机制

---

## 技术亮点

1. **完整的指标计算**: 支持RSI、MACD、OBV等主流技术指标
2. **状态机设计**: 大盘状态判断采用优先级状态机,逻辑清晰
3. **风险管理**: 多层次风控(单笔、日回撤、周回撤、连续亏损)
4. **策略映射**: ETF策略与市场状态完整映射
5. **数值精度**: 使用Decimal保证金融计算精度
6. **边界处理**: 完善的空值和边界条件处理

---

## 下一步计划

### 本周目标
1. 完成剩余核心业务逻辑服务
2. 开始实现API接口层
3. 创建基础的Serializers和Views

### 下周目标
1. 完成所有API接口
2. 初始化Vue 3前端项目
3. 实现登录注册页面

---

## 使用示例

### 技术指标计算
```python
from apps.market.services.technical_indicator_calculator import TechnicalIndicatorCalculator

# 计算RSI
prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
rsi = TechnicalIndicatorCalculator.calculate_rsi(prices, period=14)

# 计算MACD
macd = TechnicalIndicatorCalculator.calculate_macd(prices)
```

### 大盘状态判断
```python
from apps.strategy.services.market_state_calculator import MarketStateCalculator

# 计算技术状态
tech_state = MarketStateCalculator.calculate_tech_state(
    change_20d=-9.2,
    rsi_14=32.4
)  # 返回: '底部区'

# 计算最终状态
final_state = MarketStateCalculator.calculate_final_state(
    tech_state='底部区',
    event_correction=1.0
)  # 返回: '底部区'

# 获取建议仓位
max_position = MarketStateCalculator.get_max_position('底部区')  # 返回: 100
```

### 风险管理
```python
from apps.risk.services.risk_manager import RiskManager

# 计算仓位
result = RiskManager.calculate_position_size(
    total_capital=100000,
    risk_percentage=2.0,
    stop_loss_percentage=5.0
)
# 返回: {'max_amount': 40000, 'position_percentage': 40.0, 'risk_amount': 2000}
```

---

## 注意事项

1. **依赖安装**: 确保已安装NumPy (`pip install numpy`)
2. **数据准备**: 技术指标计算需要足够的历史数据
3. **参数调整**: 阈值参数可根据实际情况在配置中调整
4. **单元测试**: 建议为每个服务编写单元测试验证计算准确性

---

## 相关文档

- [需求文档](../requestment.md)
- [设计文档](../design.md)
- [实现总结](../IMPLEMENTATION_SUMMARY.md)
- [交付文档](../DELIVERY.md)
- [安装指南](../SETUP.md)

---

**报告生成时间**: 2026-04-21  
**下次更新**: 完成API接口实现后
