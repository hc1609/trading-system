"""
Tests for position management and trading operations.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

from apps.position.models import Position, Transaction


class PositionModelTestCase(TestCase):
    """持仓模型测试"""
    
    def setUp(self):
        """创建测试用户"""
        self.user = User.objects.create_user(
            username='testuser',
            password='test123456'
        )
    
    def test_position_creation(self):
        """测试持仓创建"""
        position = Position.objects.create(
            user=self.user,
            symbol='000001',
            name='平安银行',
            type='individual',
            logic='trend',
            buy_date=date.today(),
            buy_price=Decimal('15.50'),
            quantity=1000,
            stop_loss=Decimal('14.73'),
            status='holding'
        )
        
        self.assertIsNotNone(position.id)
        self.assertEqual(str(position.symbol), '000001')
        self.assertEqual(float(position.buy_price), 15.50)
        self.assertEqual(position.quantity, 1000)
        self.assertEqual(position.status, 'holding')
    
    def test_position_current_value(self):
        """测试持仓市值计算"""
        position = Position.objects.create(
            user=self.user,
            symbol='000001',
            name='平安银行',
            buy_price=Decimal('15.50'),
            quantity=1000,
            status='holding'
        )
        
        expected_value = 15.50 * 1000
        self.assertEqual(float(position.current_value), expected_value)
    
    def test_transaction_creation(self):
        """测试交易记录创建"""
        position = Position.objects.create(
            user=self.user,
            symbol='000001',
            name='平安银行',
            buy_price=Decimal('15.50'),
            quantity=1000,
            status='holding'
        )
        
        transaction = Transaction.objects.create(
            user=self.user,
            position=position,
            date=date.today(),
            direction='buy',
            price=Decimal('15.50'),
            quantity=1000,
            amount=Decimal('15500.00'),
            logic_type='trend'
        )
        
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.direction, 'buy')
        self.assertEqual(float(transaction.amount), 15500.00)
    
    def test_position_str_representation(self):
        """测试持仓字符串表示"""
        position = Position.objects.create(
            user=self.user,
            symbol='000001',
            name='平安银行',
            buy_price=Decimal('15.50'),
            quantity=1000,
            status='holding'
        )
        
        expected_str = f"{self.user.username} - 平安银行"
        self.assertEqual(str(position), expected_str)
    
    def test_position_status_choices(self):
        """测试持仓状态选项"""
        position = Position.objects.create(
            user=self.user,
            symbol='000001',
            name='平安银行',
            buy_price=Decimal('15.50'),
            quantity=1000,
            status='holding'
        )
        
        # 检查状态是否在允许的选项中
        valid_statuses = ['holding', 'sold', 'stopped']
        self.assertIn(position.status, valid_statuses)
