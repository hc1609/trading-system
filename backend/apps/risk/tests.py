"""
Tests for risk management.
"""

from django.test import TestCase
from apps.risk.services.risk_manager import RiskManager


class RiskManagerTestCase(TestCase):
    """风险管理服务测试"""
    
    def test_calculate_position_size_basic(self):
        """测试仓位计算"""
        size = RiskManager.calculate_position_size(
            total_capital=100000,
            risk_percentage=2.0,
            stop_loss_percentage=5.0
        )
        
        # 风险金额 = 100000 * 2% = 2000
        # 最大仓位 = 2000 / 5% = 40000
        expected = min(40000, 100000 * 0.2)
        self.assertEqual(size, expected)
    
    def test_calculate_position_size_max_limit(self):
        """测试单只最大仓位限制20%"""
        size = RiskManager.calculate_position_size(
            total_capital=100000,
            risk_percentage=5.0,  # 高风险比例
            stop_loss_percentage=1.0  # 小止损幅度
        )
        
        # 即使计算结果很大,也应该限制在20%以内
        self.assertLessEqual(size, 20000)
    
    def test_calculate_stop_loss_basic(self):
        """测试止损价计算"""
        stop = RiskManager.calculate_stop_loss(
            buy_price=100.0,
            stop_loss_percentage=5.0
        )
        
        expected = 100.0 * (1 - 0.05)
        self.assertEqual(stop, expected)
    
    def test_calculate_trailing_stop_basic(self):
        """测试跟踪止损计算"""
        stop = RiskManager.calculate_trailing_stop(
            current_price=120.0,
            highest_price=125.0,
            trailing_percentage=10.0
        )
        
        # 跟踪止损 = 125 * (1 - 10%) = 112.5
        expected = 125.0 * 0.9
        self.assertEqual(stop, expected)
    
    def test_calculate_trailing_stop_not_triggered(self):
        """测试跟踪止损未触发"""
        stop = RiskManager.calculate_trailing_stop(
            current_price=120.0,
            highest_price=120.0,
            trailing_percentage=10.0
        )
        
        # 最高价等于当前价,返回None
        self.assertIsNone(stop)
    
    def test_check_stop_loss_triggered(self):
        """测试止损触发"""
        result = RiskManager.check_stop_loss(
            current_price=95.0,
            stop_loss_price=96.0
        )
        
        self.assertTrue(result['triggered'])
        self.assertEqual(result['current_price'], 95.0)
        self.assertEqual(result['stop_loss_price'], 96.0)
    
    def test_check_stop_loss_not_triggered(self):
        """测试止损未触发"""
        result = RiskManager.check_stop_loss(
            current_price=100.0,
            stop_loss_price=95.0
        )
        
        self.assertFalse(result['triggered'])
    
    def test_check_daily_drawdown_limit(self):
        """测试日回撤限制3%"""
        status = {'daily_return': -4.0}
        result = RiskManager.check_daily_drawdown_limit(status)
        
        self.assertFalse(result['allowed'])
        self.assertIn('日回撤', result['reason'])
    
    def test_check_daily_drawdown_allowed(self):
        """测试日回撤在限制内"""
        status = {'daily_return': -2.0}
        result = RiskManager.check_daily_drawdown_limit(status)
        
        self.assertTrue(result['allowed'])
    
    def test_check_weekly_drawdown_limit(self):
        """测试周回撤限制5%"""
        status = {'weekly_return': -6.0}
        result = RiskManager.check_weekly_drawdown_limit(status)
        
        self.assertFalse(result['allowed'])
        self.assertIn('周回撤', result['reason'])
    
    def test_check_consecutive_losses_limit(self):
        """测试连续亏损限制3次"""
        status = {'consecutive_losses': 3}
        result = RiskManager.check_consecutive_losses_limit(status)
        
        self.assertFalse(result['allowed'])
        self.assertIn('连续亏损', result['reason'])
    
    def test_check_consecutive_losses_allowed(self):
        """测试连续亏损在限制内"""
        status = {'consecutive_losses': 2}
        result = RiskManager.check_consecutive_losses_limit(status)
        
        self.assertTrue(result['allowed'])
    
    def test_check_risk_lock(self):
        """测试风控锁定"""
        status = {'risk_lock': True}
        result = RiskManager.check_risk_lock(status)
        
        self.assertFalse(result['allowed'])
        self.assertIn('锁定', result['reason'])
    
    def test_get_risk_summary(self):
        """测试风险汇总"""
        status = {
            'daily_return': -2.0,
            'weekly_return': -3.0,
            'consecutive_losses': 1,
            'risk_lock': False,
        }
        
        summary = RiskManager.get_risk_summary(status)
        
        self.assertFalse(summary['risk_alert'])
        self.assertIn('daily_return', summary)
        self.assertIn('weekly_return', summary)


class RiskStatusModelTestCase(TestCase):
    """风控状态模型测试"""
    
    def test_risk_status_creation(self):
        """测试风控状态创建"""
        from django.contrib.auth.models import User
        from apps.risk.models import RiskStatus
        
        user = User.objects.create_user(
            username='testuser',
            password='test123456'
        )
        
        risk_status = RiskStatus.objects.create(
            user=user,
            date='2024-01-01',
            total_capital=100000,
            daily_return=-1.5,
            weekly_return=-2.0,
            risk_lock=False
        )
        
        self.assertIsNotNone(risk_status.id)
        self.assertEqual(float(risk_status.total_capital), 100000)
        self.assertFalse(risk_status.risk_lock)
