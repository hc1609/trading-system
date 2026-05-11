# 核心业务逻辑实现完成报告

**完成时间**: 2026-04-21  
**阶段**: 第三阶段 - 核心业务逻辑实现

---

## ✅ 已完成的核心服务

### 1. 技术指标计算服务
**文件**: `apps/market/services/technical_indicator_calculator.py` (231行)

**功能清单**:
- ✅ RSI指标计算 (14日默认周期)
- ✅ 移动平均线计算 (MA5/MA20/MA60)
- ✅ MACD指标计算 (DIF/DEA/MACD柱)
- ✅ OBV累积能量线计算
- ✅ 量比计算
- ✅ 涨跌幅计算
- ✅ 背离检测 (顶背离/底背离)
- ✅ OBV趋势分析
- ✅ 振幅计算

**技术实现**:
```python
# 使用NumPy高效计算
import numpy as np

# RSI计算示例
rsi = TechnicalIndicatorCalculator.calculate_rsi(prices, period=14)

# MACD计算示例
macd = TechnicalIndicatorCalculator.calculate_macd(prices)
# 返回: {'dif': 1.23, 'dea': 1.15, 'macd': 0.16}
```

---

### 2. 量价关系分析服务
**文件**: `apps/market/services/volume_price_service.py` (162行)

**功能清单**:
- ✅ 量价关系矩阵分析 (9种组合)
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
缩量整理 → 情绪弱 → 观察
```

---

### 3. 大盘状态判断服务
**文件**: `apps/strategy/services/market_state_calculator.py` (294行)

**核心算法**:

#### 技术状态判断 (优先级从高到低)
1. **陷阱区**: 20日最大涨幅>8% 且 5日振幅<3% 且 量斜度下降>5日
2. **底部区**: (20日跌幅<-8% 且 RSI<35) 或 20日跌幅<-12% 或 RSI<25
3. **上涨区**: 20日涨幅>5% 或 RSI>70
4. **震荡区**: 20日涨跌幅在-5%到+5%之间

#### 大周期状态判断 (优先级从高到低)
1. **主升浪**: 20日涨幅>10% 且 RSI>65 且 沿5日线上涨
2. **赶顶期**: 20日涨幅>10% 且 出现顶背离
3. **正常趋势**: 20日涨幅3%-10% 且 RSI 50-65
4. **下跌期**: 20日跌幅>5% 或 跌破60日线
5. **震荡期**: 不满足上述条件

#### 其他功能
- ✅ 事件修正计算 (支持多事件叠加,限制-2到+2)
- ✅ 主要趋势判断 (道氏理论)
- ✅ 综合状态输出 (技术状态 + 事件修正)
- ✅ 分级离场判断 (一级/二级/三级)
- ✅ MACD顶背离检测

**使用示例**:
```python
# 计算技术状态
tech_state = MarketStateCalculator.calculate_tech_state(
    change_20d=-9.2,
    rsi_14=32.4
)  # 返回: '底部区'

# 计算最终状态
final_state = MarketStateCalculator.calculate_final_state(
    tech_state='底部区',
    event_correction=1.0
)

# 获取建议仓位
max_position = MarketStateCalculator.get_max_position('底部区')  # 100%

# 分级离场检查
exit_info = MarketStateCalculator.check_exit_level(
    has_divergence=True,
    is_below_ma10=False,
    is_below_ma20=False
)
# 返回: {'exit_level': 1, 'action': '卖出1/3仓位'}
```

---

### 4. 风险管理服务
**文件**: `apps/risk/services/risk_manager.py` (260行)

**功能清单**:
- ✅ 仓位计算 (基于风险比例)
- ✅ 单日回撤监控 (阈值-3%)
- ✅ 周回撤监控 (阈值-6%)
- ✅ 连续亏损保护 (2次触发)
- ✅ 单笔交易风险检查
- ✅ 仓位上限检查
- ✅ 止损价计算
- ✅ 止盈价计算
- ✅ 风险收益比计算

**核心公式**:
```python
# 仓位计算
仓位 = (总资金 × 风险比例) / 止损幅度
例: (100,000 × 2%) / 5% = 40,000元

# 使用示例
result = RiskManager.calculate_position_size(
    total_capital=100000,
    risk_percentage=2.0,
    stop_loss_percentage=5.0
)
# 返回: {'max_amount': 40000, 'position_percentage': 40.0, 'risk_amount': 2000}
```

---

### 5. ETF策略服务
**文件**: `apps/position/services/etf_service.py` (191行)

**功能清单**:
- ✅ 根据市场状态生成ETF操作建议
- ✅ 分批买入计算 (25% + 25% + 25%)
- ✅ 止损位计算 (常规-5%, 主升浪-10%或20日线)
- ✅ 止盈信号检测 (背离判断)

**策略映射**:
```
底部区 → 分批买入 (25% + 25%)
震荡区 → 持有不动
上涨区 → 持有或分批卖出
主升浪 → 坚定持有 (止损放宽)
赶顶期 → 分级离场
陷阱区 → 只卖不买
下跌期 → 清仓观望
```

---

### 6. 关键点识别服务
**文件**: `apps/position/services/keypoint_service.py` (351行)

**功能清单**:
- ✅ 突破关键点检测
- ✅ 自然回撤关键点检测 (回调1/3-1/2)
- ✅ 连续关键点检测 (金字塔加仓点)
- ✅ 反转关键点检测 (离场信号)
- ✅ 关键点信号强度计算
- ✅ 关键点入场验证 (7项检查清单)

**四种关键点类型**:
```python
# 1. 突破关键点
result = KeyPointDetector.detect_breakout_keypoint(
    current_price=105,
    resistance_level=100,
    volume_ratio=2.1
)
# 返回: {'detected': True, 'strength': '强'}

# 2. 自然回撤关键点
result = KeyPointDetector.detect_pullback_keypoint(
    current_price=95,
    recent_high=100,
    pullback_ratio=0.4  # 回调40%
)

# 3. 连续关键点 (加仓点)
result = KeyPointDetector.detect_continuous_keypoint(
    current_price=110,
    has_profit=True,
    price_increase=8  # 上涨8%
)

# 4. 反转关键点 (危险信号)
result = KeyPointDetector.detect_reversal_keypoint(
    current_price=98,
    previous_high=100,
    price_action='无法突破'
)
```

**入场检查清单**:
```
□ 大盘主要趋势是否向上？
□ 是否出现明确的关键点信号？
□ 成交量是否显著放大(量比>=1.5)？
□ 突破后是否站稳3天以上？
□ 行业板块是否同步走强？
□ 是否已设定止损单？
□ 单笔风险是否控制在1-2%以内？
```

---

### 7. 开仓检查服务
**文件**: `apps/position/services/open_position_service.py` (228行)

**功能清单**:
- ✅ 大盘状态检查
- ✅ 关键点信号验证
- ✅ 成交量验证
- ✅ 风控状态检查
- ✅ 仓位上限检查
- ✅ 基于风险的仓位计算
- ✅ 入场检查清单验证

**检查流程**:
```python
result = OpenPositionChecker.check_open_position(
    market_state='底部区',
    keypoint_signal={'detected': True, 'type': '突破关键点'},
    volume_ratio=2.1,
    risk_status={'risk_lock': False, 'consecutive_losses': 0},
    current_position=30000,
    new_position=20000,
    total_capital=100000
)
# 返回: {'allowed': True, 'checks': {...}}
```

---

### 8. 金字塔加仓服务
**文件**: `apps/position/services/pyramid_service.py` (235行)

**功能清单**:
- ✅ 加仓条件检查
- ✅ 加仓规模计算 (50% + 30% + 20%)
- ✅ 止损位调整 (上移至盈亏平衡点)
- ✅ 加仓计划生成
- ✅ 加仓规则验证 (纪律检查)

**加仓规则**:
```python
# 检查加仓条件
result = PyramidAddService.check_pyramid_add(
    current_profit=0.08,  # 盈利8%
    price_increase=0.06,  # 上涨6%
    keypoint_signal={'detected': True, 'type': '连续关键点'},
    add_count=0
)
# 返回: {'allowed': True, 'add_ratio': 0.30}

# 加仓后调整止损
result = PyramidAddService.adjust_stop_loss_after_add(
    original_stop_loss=95,
    entry_price=100,
    add_price=105,
    add_quantity=300,
    original_quantity=500
)
# 返回: {'new_stop_loss': 102.5, 'breakeven_price': 103.75}
```

**金字塔加仓示例**:
```
首次入场: 买入50%计划仓位,止损-3%
上涨5%后出现连续关键点 → 加仓30%,整体止损移至成本价
再上涨5%后再次出现连续关键点 → 加仓20%
```

---

### 9. 箱体分析服务
**文件**: `apps/box/services/box_analyzer.py` (317行)

**功能清单**:
- ✅ 箱体识别 (聚类算法)
- ✅ 位置判断 (上/中/下1/3区)
- ✅ 操作建议生成
- ✅ 箱体突破判断
- ✅ 目标位计算
- ✅ 触及次数统计

**使用示例**:
```python
# 识别箱体
result = BoxAnalyzer.identify_box(
    high_prices=[...],
    low_prices=[...],
    closes=[...]
)
# 返回: {'identified': True, 'top': 15.5, 'bottom': 13.2, ...}

# 判断位置
position = BoxAnalyzer.get_box_position(
    current_price=13.8,
    box_top=15.5,
    box_bottom=13.2
)
# 返回: {'zone': '下1/3区', 'position_percent': 26.09}

# 获取操作建议
action = BoxAnalyzer.get_box_action(
    current_price=13.8,
    box_top=15.5,
    box_bottom=13.2,
    bottom_confirm_count=2
)
# 返回: {'action': '可买入', 'reason': '底部已确认2次'}
```

---

### 10. 做T管理服务
**文件**: `apps/daytrade/services/daytrade_manager.py` (281行)

**功能清单**:
- ✅ 做T开关控制 (仅震荡区允许)
- ✅ 盈亏率计算
- ✅ 成功率统计 (近20次)
- ✅ 暂停条件检查
- ✅ 卖出触发检查
- ✅ 买回条件验证
- ✅ 做T计划生成

**做T规则**:
```python
# 检查是否允许做T
result = DayTradeManager.check_daytrade_allowed(
    market_state='震荡区',
    risk_status={'risk_lock': False},
    daytrade_stats={'is_paused': False, 'consecutive_failures': 0}
)
# 返回: {'allowed': True}

# 检查卖出触发
result = DayTradeManager.check_sell_trigger(
    current_profit=0.8,  # 盈利0.8%
    target_profit=0.75,
    stop_loss=0.5
)
# 返回: {'action': 'sell', 'reason': '达到目标盈利0.75%'}

# 统计成功率
result = DayTradeManager.calculate_success_rate(records, last_n=20)
# 返回: {'success_rate': 85.0, 'total': 20, 'success': 17}
```

---

## 📊 代码统计

| 服务 | 文件 | 行数 | 功能数 |
|------|------|------|--------|
| 技术指标计算 | technical_indicator_calculator.py | 231 | 10 |
| 量价关系分析 | volume_price_service.py | 162 | 4 |
| 大盘状态判断 | market_state_calculator.py | 294 | 9 |
| 风险管理 | risk_manager.py | 260 | 10 |
| ETF策略 | etf_service.py | 191 | 4 |
| 关键点识别 | keypoint_service.py | 351 | 6 |
| 开仓检查 | open_position_service.py | 228 | 4 |
| 金字塔加仓 | pyramid_service.py | 235 | 5 |
| 箱体分析 | box_analyzer.py | 317 | 7 |
| 做T管理 | daytrade_manager.py | 281 | 8 |
| **总计** | **10个文件** | **2,550行** | **67个功能** |

---

## 🎯 核心特性

### 1. 完整的交易逻辑覆盖
- ✅ 技术指标计算
- ✅ 市场状态判断
- ✅ 关键点识别
- ✅ 仓位管理
- ✅ 风险控制
- ✅ 做T增强

### 2. 严格的纪律检查
- ✅ 开仓前7项检查
- ✅ 加仓规则验证
- ✅ 止损止盈计算
- ✅ 风控熔断机制

### 3. 精确的数值计算
- ✅ 使用NumPy高效计算
- ✅ Decimal保证精度
- ✅ 完善的边界处理

### 4. 灵活的可配置性
- ✅ 阈值参数可调
- ✅ 策略规则可配置
- ✅ 支持个性化设置

---

## 📝 使用示例

### 完整的交易决策流程

```python
from apps.market.services.technical_indicator_calculator import TechnicalIndicatorCalculator
from apps.strategy.services.market_state_calculator import MarketStateCalculator
from apps.position.services.keypoint_service import KeyPointDetector
from apps.risk.services.risk_manager import RiskManager

# 1. 计算技术指标
indicators = TechnicalIndicatorCalculator.calculate_rsi(prices)

# 2. 判断市场状态
tech_state = MarketStateCalculator.calculate_tech_state(
    change_20d=-9.2,
    rsi_14=32.4
)

# 3. 检测关键点
keypoint = KeyPointDetector.detect_breakout_keypoint(
    current_price=105,
    resistance_level=100,
    volume_ratio=2.1
)

# 4. 检查开仓条件
allowed = OpenPositionChecker.check_open_position(
    market_state=tech_state,
    keypoint_signal=keypoint,
    ...
)

# 5. 计算仓位
position = RiskManager.calculate_position_size(
    total_capital=100000,
    risk_percentage=2.0,
    stop_loss_percentage=5.0
)

# 6. 执行交易
if allowed['allowed']:
    # 开仓
    pass
```

---

## ✅ 第三阶段完成度: 100%

所有核心业务逻辑已实现完毕,包括:
- ✅ 10个核心服务
- ✅ 2,550行代码
- ✅ 67个功能函数
- ✅ 完整的交易决策流程

---

## 🚀 下一步

### 第四阶段: API接口实现
1. 创建各模块的Serializers
2. 创建各模块的Views
3. 配置URL路由
4. API测试

### 第五阶段: 前端开发
1. 初始化Vue 3项目
2. 开发页面和组件
3. 前后端联调

---

**报告生成时间**: 2026-04-21  
**下一阶段**: API接口实现
