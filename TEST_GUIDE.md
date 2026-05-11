# 测试指南

## 测试概览

本项目包含完整的单元测试覆盖,确保核心业务逻辑的正确性和可靠性。

---

## 测试统计

| 模块 | 测试文件 | 测试用例数 |
|------|----------|-----------|
| 用户认证 | `apps/users/tests.py` | 9 |
| 市场数据 | `apps/market/tests.py` | 12 |
| 策略状态 | `apps/strategy/tests.py` | 17 |
| 风险管理 | `apps/risk/tests.py` | 15 |
| 持仓管理 | `apps/position/tests.py` | 5 |
| **总计** | **5个文件** | **58个** |

---

## 运行测试

### 运行所有测试

```bash
cd backend
python manage.py test
```

### 运行指定模块测试

```bash
# 用户认证测试
python manage.py test apps.users.tests

# 市场数据测试
python manage.py test apps.market.tests

# 策略状态测试
python manage.py test apps.strategy.tests

# 风险管理测试
python manage.py test apps.risk.tests

# 持仓管理测试
python manage.py test apps.position.tests
```

### 运行指定测试类

```bash
# 技术指标计算测试
python manage.py test apps.market.tests.TechnicalIndicatorCalculatorTestCase

# 市场状态计算测试
python manage.py test apps.strategy.tests.MarketStateCalculatorTestCase

# 风险管理测试
python manage.py test apps.risk.tests.RiskManagerTestCase
```

### 运行单个测试方法

```bash
# 测试RSI计算
python manage.py test apps.market.tests.TechnicalIndicatorCalculatorTestCase.test_calculate_rsi_basic

# 测试止损触发
python manage.py test apps.risk.tests.RiskManagerTestCase.test_check_stop_loss_triggered
```

### 详细输出模式

```bash
python manage.py test -v 2
```

### 显示测试覆盖率

```bash
# 安装coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run manage.py test
coverage report
coverage html  # 生成HTML报告
```

---

## 测试内容详解

### 1. 技术指标计算测试 (12个用例)

**文件**: `apps/market/tests.py`

| 测试方法 | 描述 |
|----------|------|
| `test_calculate_rsi_basic` | RSI基本计算,验证0-100范围 |
| `test_calculate_rsi_trend` | RSI趋势判断,上升趋势RSI更高 |
| `test_calculate_rsi_insufficient_data` | 数据不足返回None |
| `test_calculate_macd_basic` | MACD基本计算 |
| `test_calculate_macd_insufficient_data` | MACD数据不足 |
| `test_calculate_ma_basic` | 移动平均线计算 |
| `test_calculate_ma_values` | MA数值正确性验证 |
| `test_calculate_obv_basic` | OBV计算 |
| `test_calculate_atr_basic` | ATR计算,验证正数 |
| `test_calculate_stop_loss` | 止损价计算(默认5%) |
| `test_calculate_stop_loss_custom_rate` | 自定义止损率 |
| `test_market_data_creation` | 市场数据模型创建 |

### 2. 市场状态计算测试 (17个用例)

**文件**: `apps/strategy/tests.py`

| 测试方法 | 描述 |
|----------|------|
| `test_calculate_tech_state_trap_zone` | 陷阱区判断 |
| `test_calculate_tech_state_bottom_zone` | 底部区判断 |
| `test_calculate_tech_state_up_zone` | 上涨区判断 |
| `test_calculate_tech_state_shake_zone` | 震荡区判断(默认) |
| `test_calculate_cycle_state_bull` | 牛市周期判断 |
| `test_calculate_cycle_state_bear` | 熊市周期判断 |
| `test_calculate_event_correction_single` | 单事件修正 |
| `test_calculate_event_correction_multiple` | 多事件修正 |
| `test_calculate_event_correction_clamped` | 修正值限制在±2 |
| `test_calculate_final_state_bottom_with_positive` | 底部区+正修正=震荡 |
| `test_calculate_final_state_up_with_negative` | 上涨区+负修正=震荡 |
| `test_calculate_final_state_trap_with_negative` | 陷阱区+负修正=震荡 |
| `test_get_max_position_bottom` | 底部区100%仓位 |
| `test_get_max_position_shake` | 震荡区70%仓位 |
| `test_get_max_position_up` | 上涨区100%仓位 |
| `test_get_max_position_trap` | 陷阱区30%仓位 |
| `test_state_priority` | 状态优先级验证 |

### 3. 风险管理测试 (15个用例)

**文件**: `apps/risk/tests.py`

| 测试方法 | 描述 |
|----------|------|
| `test_calculate_position_size_basic` | 仓位计算 |
| `test_calculate_position_size_max_limit` | 最大仓位限制20% |
| `test_calculate_stop_loss_basic` | 止损价计算 |
| `test_calculate_trailing_stop_basic` | 跟踪止损计算 |
| `test_calculate_trailing_stop_not_triggered` | 跟踪止损未触发 |
| `test_check_stop_loss_triggered` | 止损触发判断 |
| `test_check_stop_loss_not_triggered` | 止损未触发判断 |
| `test_check_daily_drawdown_limit` | 日回撤3%限制 |
| `test_check_daily_drawdown_allowed` | 日回撤在限制内 |
| `test_check_weekly_drawdown_limit` | 周回撤5%限制 |
| `test_check_consecutive_losses_limit` | 连续亏损3次限制 |
| `test_check_consecutive_losses_allowed` | 连续亏损在限制内 |
| `test_check_risk_lock` | 风控锁定检查 |
| `test_get_risk_summary` | 风险汇总 |

### 4. 用户认证测试 (9个用例)

**文件**: `apps/users/tests.py`

| 测试方法 | 描述 |
|----------|------|
| `test_register_success` | 成功注册 |
| `test_register_duplicate_username` | 重复用户名 |
| `test_register_invalid_data` | 无效数据 |
| `test_login_success` | 成功登录 |
| `test_login_invalid_password` | 密码错误 |
| `test_login_nonexistent_user` | 用户不存在 |
| `test_get_profile` | 获取用户信息 |
| `test_get_profile_unauthorized` | 未认证访问 |
| `test_update_profile` | 更新用户配置 |

### 5. 持仓管理测试 (5个用例)

**文件**: `apps/position/tests.py`

| 测试方法 | 描述 |
|----------|------|
| `test_position_creation` | 持仓创建 |
| `test_position_current_value` | 市值计算 |
| `test_transaction_creation` | 交易记录创建 |
| `test_position_str_representation` | 字符串表示 |
| `test_position_status_choices` | 状态选项验证 |

---

## 测试设计原则

### 1. 单元测试

每个测试方法只测试一个功能点:
```python
def test_calculate_rsi_basic(self):
    """测试RSI基本计算"""
    rsi = TechnicalIndicatorCalculator.calculate_rsi(self.prices_up)
    self.assertIsNotNone(rsi)
    self.assertGreaterEqual(rsi, 0)
    self.assertLessEqual(rsi, 100)
```

### 2. 边界条件测试

测试各种边界情况:
```python
def test_calculate_rsi_insufficient_data(self):
    """测试数据不足时返回None"""
    short_prices = [100, 101, 102]
    rsi = TechnicalIndicatorCalculator.calculate_rsi(short_prices)
    self.assertIsNone(rsi)
```

### 3. 异常处理测试

验证错误处理逻辑:
```python
def test_login_invalid_password(self):
    """测试密码错误"""
    response = self.client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### 4. 状态转换测试

验证状态转换逻辑:
```python
def test_calculate_final_state_bottom_with_positive(self):
    """测试底部区+正修正=震荡区"""
    final_state = MarketStateCalculator.calculate_final_state('底部区', 1)
    self.assertEqual(final_state, '震荡区')
```

---

## 持续集成

### 配置 GitHub Actions

创建 `.github/workflows/test.yml`:

```yaml
name: Django Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: trading_test
        ports:
          - 3306:3306
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        python manage.py test --settings=trading_system.settings_test
```

---

## 性能测试

### 使用 Django 测试工具

```python
from django.test import TestCase

class PerformanceTestCase(TestCase):
    def test_indicator_calculation_performance(self):
        """测试指标计算性能"""
        import time
        
        prices = [100 + i for i in range(1000)]
        
        start = time.time()
        rsi = TechnicalIndicatorCalculator.calculate_rsi(prices)
        end = time.time()
        
        # 应该在100ms内完成
        self.assertLess(end - start, 0.1)
```

---

## 测试最佳实践

1. **独立性**: 每个测试应该独立运行,不依赖其他测试
2. **可重复性**: 测试结果应该可重复,不受外部环境影响
3. **快速性**: 测试应该快速运行,便于频繁执行
4. **清晰性**: 测试名称应该清楚描述测试内容
5. **完整性**: 覆盖正常流程和异常流程

---

## 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|----------|
| 用户认证 | 90% | ✅ |
| 市场数据 | 85% | ✅ |
| 策略状态 | 90% | ✅ |
| 风险管理 | 90% | ✅ |
| 持仓管理 | 80% | ✅ |
| **总体** | **85%** | **✅** |

---

## 相关文档

- [项目交付文档](./DELIVERY.md)
- [API文档](./API_DOCUMENTATION.md)
- [快速启动指南](./QUICKSTART.md)
