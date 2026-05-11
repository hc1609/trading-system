"""
Tests for strategy and market state calculation.
"""

from django.test import TestCase
from apps.strategy.services.market_state_calculator import MarketStateCalculator


class MarketStateCalculatorTestCase(TestCase):
    """市场状态计算测试"""
    
    def test_calculate_tech_state_trap_zone(self):
        """测试陷阱区判断"""
        state = MarketStateCalculator.calculate_tech_state(
            change_20d=5,
            rsi_14=70,
            max_gain_20d=10,
            amplitude_5d=2,
            volume_slope_decreasing_days=7
        )
        self.assertEqual(state, '陷阱区')
    
    def test_calculate_tech_state_bottom_zone(self):
        """测试底部区判断"""
        state = MarketStateCalculator.calculate_tech_state(
            change_20d=-10,
            rsi_14=30
        )
        self.assertEqual(state, '底部区')
    
    def test_calculate_tech_state_up_zone(self):
        """测试上涨区判断"""
        state = MarketStateCalculator.calculate_tech_state(
            change_20d=15,
            rsi_14=60
        )
        self.assertEqual(state, '上涨区')
    
    def test_calculate_tech_state_shake_zone(self):
        """测试震荡区判断 (默认状态)"""
        state = MarketStateCalculator.calculate_tech_state(
            change_20d=-3,
            rsi_14=45
        )
        self.assertEqual(state, '震荡区')
    
    def test_calculate_cycle_state_bull(self):
        """测试牛市判断"""
        state = MarketStateCalculator.calculate_cycle_state(
            change_20d=15,
            rsi_14=65,
            is_above_ma5=True
        )
        self.assertIn(state, ['牛市', '上升期'])
    
    def test_calculate_cycle_state_bear(self):
        """测试熊市判断"""
        state = MarketStateCalculator.calculate_cycle_state(
            change_20d=-15,
            rsi_14=25,
            is_below_ma60=True
        )
        self.assertIn(state, ['熊市', '下降期'])
    
    def test_calculate_event_correction_single(self):
        """测试单个事件修正"""
        events = [{'correction_value': -1, 'priority': 1}]
        correction = MarketStateCalculator.calculate_event_correction(events)
        self.assertEqual(correction, -1)
    
    def test_calculate_event_correction_multiple(self):
        """测试多个事件修正"""
        events = [
            {'correction_value': -1, 'priority': 1},
            {'correction_value': -2, 'priority': 2},
        ]
        correction = MarketStateCalculator.calculate_event_correction(events)
        # 应该取高优先级的事件
        self.assertLessEqual(correction, -1)
    
    def test_calculate_event_correction_clamped(self):
        """测试修正值限制在-2到+2之间"""
        events = [{'correction_value': -5, 'priority': 1}]
        correction = MarketStateCalculator.calculate_event_correction(events)
        self.assertGreaterEqual(correction, -2)
        self.assertLessEqual(correction, 2)
    
    def test_calculate_final_state_bottom_with_positive_correction(self):
        """测试底部区+正修正=震荡区"""
        final_state = MarketStateCalculator.calculate_final_state('底部区', 1)
        self.assertEqual(final_state, '震荡区')
    
    def test_calculate_final_state_up_with_negative_correction(self):
        """测试上涨区+负修正=震荡区"""
        final_state = MarketStateCalculator.calculate_final_state('上涨区', -1)
        self.assertEqual(final_state, '震荡区')
    
    def test_calculate_final_state_trap_with_negative_correction(self):
        """测试陷阱区+负修正=震荡区"""
        final_state = MarketStateCalculator.calculate_final_state('陷阱区', -1)
        self.assertEqual(final_state, '震荡区')
    
    def test_get_max_position_bottom(self):
        """测试底部区最大仓位100%"""
        position = MarketStateCalculator.get_max_position('底部区')
        self.assertEqual(position, 100)
    
    def test_get_max_position_shake(self):
        """测试震荡区最大仓位70%"""
        position = MarketStateCalculator.get_max_position('震荡区')
        self.assertEqual(position, 70)
    
    def test_get_max_position_up(self):
        """测试上涨区最大仓位100%"""
        position = MarketStateCalculator.get_max_position('上涨区')
        self.assertEqual(position, 100)
    
    def test_get_max_position_trap(self):
        """测试陷阱区最大仓位30%"""
        position = MarketStateCalculator.get_max_position('陷阱区')
        self.assertEqual(position, 30)
    
    def test_get_etf_action_bottom(self):
        """测试底部区ETF操作"""
        action = MarketStateCalculator.get_etf_action('底部区')
        self.assertIn(action, ['分批买入', '积极买入'])
    
    def test_get_etf_action_trap(self):
        """测试陷阱区ETF操作"""
        action = MarketStateCalculator.get_etf_action('陷阱区')
        self.assertIn(action, ['持有不动', '清仓等待'])
    
    def test_get_individual_action_bottom(self):
        """测试底部区个股操作"""
        action = MarketStateCalculator.get_individual_action('底部区')
        self.assertIn(action, ['可积极选股', '积极做多'])
    
    def test_state_priority(self):
        """测试状态优先级"""
        priorities = {
            '陷阱区': 4,
            '底部区': 1,
            '震荡区': 2,
            '上涨区': 3,
        }
        
        # 陷阱区优先级最高(数值最大)
        self.assertEqual(
            priorities['陷阱区'],
            max(priorities.values())
        )


class EventCalendarModelTestCase(TestCase):
    """事件日历模型测试"""
    
    def test_event_creation(self):
        """测试事件创建"""
        from apps.strategy.models import EventCalendar
        
        event = EventCalendar.objects.create(
            year=2024,
            event_name='美联储议息会议',
            event_type='policy',
            start_date='2024-03-20',
            end_date='2024-03-21',
            correction_value=-1.0,
            description='3月FOMC会议'
        )
        
        self.assertIsNotNone(event.id)
        self.assertEqual(event.event_name, '美联储议息会议')
        self.assertEqual(float(event.correction_value), -1.0)
