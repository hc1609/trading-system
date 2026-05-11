"""
Tests for market data and technical indicators.
"""

import unittest
from decimal import Decimal
import numpy as np

from django.test import TestCase
from apps.market.services.technical_indicator_calculator import TechnicalIndicatorCalculator


class TechnicalIndicatorCalculatorTestCase(TestCase):
    """技术指标计算测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 生成模拟价格数据 (上升趋势)
        self.prices_up = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                         110, 112, 111, 113, 115, 114, 116, 118, 117, 119]
        
        # 生成模拟价格数据 (下降趋势)
        self.prices_down = [120, 118, 119, 117, 115, 116, 114, 112, 113, 111,
                           110, 108, 109, 107, 105, 106, 104, 102, 103, 101]
        
        # 生成模拟成交量数据
        self.volumes = [10000] * 20
        
        # 生成模拟高低价数据
        self.highs = [p + 2 for p in self.prices_up]
        self.lows = [p - 2 for p in self.prices_up]
    
    def test_calculate_rsi_basic(self):
        """测试RSI基本计算"""
        rsi = TechnicalIndicatorCalculator.calculate_rsi(self.prices_up)
        
        # RSI应该在0-100之间
        self.assertIsNotNone(rsi)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
    
    def test_calculate_rsi_trend(self):
        """测试RSI在上升趋势中应该偏高"""
        rsi_up = TechnicalIndicatorCalculator.calculate_rsi(self.prices_up)
        rsi_down = TechnicalIndicatorCalculator.calculate_rsi(self.prices_down)
        
        # 上升趋势的RSI应该大于下降趋势的RSI
        self.assertGreater(rsi_up, rsi_down)
    
    def test_calculate_rsi_insufficient_data(self):
        """测试数据不足时返回None"""
        short_prices = [100, 101, 102]
        rsi = TechnicalIndicatorCalculator.calculate_rsi(short_prices)
        
        # 数据不足应该返回None
        self.assertIsNone(rsi)
    
    def test_calculate_macd_basic(self):
        """测试MACD基本计算"""
        dif, dea, hist = TechnicalIndicatorCalculator.calculate_macd(self.prices_up)
        
        # 应该有返回值
        self.assertIsNotNone(dif)
        self.assertIsNotNone(dea)
        self.assertIsNotNone(hist)
        
        # DIF和DEA应该是数值
        self.assertIsInstance(float(dif), float)
        self.assertIsInstance(float(dea), float)
    
    def test_calculate_macd_insufficient_data(self):
        """测试MACD数据不足时返回None"""
        short_prices = [100, 101]
        dif, dea, hist = TechnicalIndicatorCalculator.calculate_macd(short_prices)
        
        self.assertIsNone(dif)
        self.assertIsNone(dea)
        self.assertIsNone(hist)
    
    def test_calculate_ma_basic(self):
        """测试移动平均线计算"""
        ma = TechnicalIndicatorCalculator.calculate_ma(self.prices_up, period=5)
        
        # 应该有返回值
        self.assertIsNotNone(ma)
        self.assertIsInstance(ma, np.ndarray)
        
        # 长度应该等于价格数组长度
        self.assertEqual(len(ma), len(self.prices_up))
    
    def test_calculate_ma_values(self):
        """测试MA数值正确性"""
        ma = TechnicalIndicatorCalculator.calculate_ma(self.prices_up, period=5)
        
        # 计算前5个数的平均值
        expected_ma_4 = sum(self.prices_up[:5]) / 5
        
        # 第4个位置(0-indexed)应该是前5个数的平均
        self.assertAlmostEqual(ma[4], expected_ma_4, places=1)
    
    def test_calculate_obv_basic(self):
        """测试OBV计算"""
        obv = TechnicalIndicatorCalculator.calculate_obv(self.prices_up, self.volumes)
        
        # 应该有返回值
        self.assertIsNotNone(obv)
        self.assertIsInstance(obv, np.ndarray)
    
    def test_calculate_atr_basic(self):
        """测试ATR计算"""
        atr = TechnicalIndicatorCalculator.calculate_atr(
            self.prices_up, self.highs, self.lows
        )
        
        # 应该有返回值
        self.assertIsNotNone(atr)
        self.assertIsInstance(atr, np.ndarray)
        
        # ATR应该是正数
        self.assertTrue(np.all(atr[13:] > 0))
    
    def test_calculate_stop_loss(self):
        """测试止损价计算"""
        buy_price = 100.0
        stop_loss = TechnicalIndicatorCalculator.calculate_stop_loss(buy_price)
        
        # 止损价应该低于买入价
        self.assertLess(stop_loss, buy_price)
        
        # 默认止损率是5%
        expected_stop = buy_price * 0.95
        self.assertAlmostEqual(stop_loss, expected_stop, places=2)
    
    def test_calculate_stop_loss_custom_rate(self):
        """测试自定义止损率"""
        buy_price = 100.0
        stop_loss = TechnicalIndicatorCalculator.calculate_stop_loss(
            buy_price, stop_loss_percentage=3.0
        )
        
        expected_stop = buy_price * 0.97
        self.assertAlmostEqual(stop_loss, expected_stop, places=2)


class MarketDataModelTestCase(TestCase):
    """市场数据模型测试"""
    
    def test_market_data_creation(self):
        """测试市场数据创建"""
        from apps.market.models import MarketData
        
        market_data = MarketData.objects.create(
            date='2024-01-01',
            index_code='399006.SZ',
            open=Decimal('2500.00'),
            high=Decimal('2550.00'),
            low=Decimal('2480.00'),
            close=Decimal('2520.00'),
            volume=Decimal('1000000'),
            amount=Decimal('2500000000')
        )
        
        self.assertIsNotNone(market_data.id)
        self.assertEqual(str(market_data.index_code), '399006.SZ')
        self.assertEqual(float(market_data.close), 2520.00)
    
    def test_technical_indicators_creation(self):
        """测试技术指标创建"""
        from apps.market.models import MarketData, TechnicalIndicators
        
        market_data = MarketData.objects.create(
            date='2024-01-01',
            index_code='399006.SZ',
            close=Decimal('2520.00')
        )
        
        indicator = TechnicalIndicators.objects.create(
            market_data=market_data,
            rsi_14=Decimal('55.5'),
            macd_dif=Decimal('1.2'),
            macd_dea=Decimal('0.8')
        )
        
        self.assertIsNotNone(indicator.id)
        self.assertEqual(float(indicator.rsi_14), 55.5)
