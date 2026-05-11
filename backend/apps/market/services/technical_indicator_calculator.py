"""
技术指标计算服务
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from decimal import Decimal


class TechnicalIndicatorCalculator:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_rsi(prices: list, period: int = 14) -> Optional[float]:
        """
        计算RSI指标
        :param prices: 价格列表(收盘价)
        :param period: RSI周期,默认14
        :return: RSI值
        """
        if len(prices) < period + 1:
            return None
        
        # 计算价格变化
        deltas = np.diff(prices)
        
        # 分离上涨和下跌
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # 计算平均涨幅和平均跌幅
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(float(rsi), 4)
    
    @staticmethod
    def calculate_moving_average(prices: list, period: int) -> Optional[float]:
        """
        计算移动平均线
        :param prices: 价格列表
        :param period: 周期
        :return: MA值
        """
        if len(prices) < period:
            return None
        
        return round(float(np.mean(prices[-period:])), 4)
    
    @staticmethod
    def calculate_macd(prices: list, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        计算MACD指标
        :param prices: 价格列表
        :param fast: 快线周期
        :param slow: 慢线周期
        :param signal: 信号线周期
        :return: {'dif': float, 'dea': float, 'macd': float}
        """
        if len(prices) < slow + signal:
            return {'dif': None, 'dea': None, 'macd': None}
        
        # 计算EMA
        ema_fast = TechnicalIndicatorCalculator._calculate_ema(prices, fast)
        ema_slow = TechnicalIndicatorCalculator._calculate_ema(prices, slow)
        
        # DIF = EMA快 - EMA慢
        dif = ema_fast[-1] - ema_slow[-1]
        
        # 计算DIF的列表用于计算DEA
        dif_list = [f - s for f, s in zip(ema_fast, ema_slow)]
        
        # DEA = DIF的EMA
        dea = TechnicalIndicatorCalculator._calculate_ema_single(dif_list, signal)
        
        # MACD柱 = (DIF - DEA) * 2
        macd = (dif - dea) * 2
        
        return {
            'dif': round(float(dif), 4),
            'dea': round(float(dea), 4),
            'macd': round(float(macd), 4)
        }
    
    @staticmethod
    def _calculate_ema(prices: list, period: int) -> list:
        """计算EMA列表"""
        ema = []
        multiplier = 2 / (period + 1)
        
        # 第一个EMA使用SMA
        ema.append(np.mean(prices[:period]))
        
        # 计算后续EMA
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    @staticmethod
    def _calculate_ema_single(data: list, period: int) -> float:
        """计算单个EMA值"""
        multiplier = 2 / (period + 1)
        
        # 第一个值使用SMA
        if len(data) < period:
            return data[-1]
        
        ema = np.mean(data[:period])
        
        for value in data[period:]:
            ema = (value - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def calculate_obv(closes: list, volumes: list) -> Optional[int]:
        """
        计算OBV(累积能量线)
        :param closes: 收盘价列表
        :param volumes: 成交量列表
        :return: OBV值
        """
        if len(closes) < 2 or len(volumes) < 1:
            return None
        
        obv = 0
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i-1]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i-1]
        
        return int(obv)
    
    @staticmethod
    def calculate_volume_ratio(current_volume: int, avg_volume: int) -> Optional[float]:
        """
        计算量比
        :param current_volume: 当前成交量
        :param avg_volume: 平均成交量
        :return: 量比值
        """
        if avg_volume == 0:
            return None
        
        return round(float(current_volume / avg_volume), 4)
    
    @staticmethod
    def calculate_change_rate(current_price: float, historical_price: float) -> Optional[float]:
        """
        计算涨跌幅
        :param current_price: 当前价格
        :param historical_price: 历史价格
        :return: 涨跌幅(%)
        """
        if historical_price == 0:
            return None
        
        return round(float((current_price - historical_price) / historical_price * 100), 4)
    
    @staticmethod
    def detect_divergence(prices: list, indicator_values: list) -> str:
        """
        检测背离
        :param prices: 价格列表
        :param indicator_values: 指标值列表(如RSI)
        :return: '顶背离' / '底背离' / '无'
        """
        if len(prices) < 2 or len(indicator_values) < 2:
            return '无'
        
        # 简化版背离检测
        price_trend = prices[-1] - prices[-2]
        indicator_trend = indicator_values[-1] - indicator_values[-2]
        
        if price_trend > 0 and indicator_trend < 0:
            return '顶背离'
        elif price_trend < 0 and indicator_trend > 0:
            return '底背离'
        
        return '无'
    
    @staticmethod
    def analyze_obv_trend(obv_values: list) -> str:
        """
        分析OBV趋势
        :param obv_values: OBV值列表
        :return: '上升' / '下降' / '平稳'
        """
        if len(obv_values) < 2:
            return '平稳'
        
        recent_obv = obv_values[-1]
        prev_obv = obv_values[-2]
        
        change_rate = (recent_obv - prev_obv) / abs(prev_obv) if prev_obv != 0 else 0
        
        if change_rate > 0.01:
            return '上升'
        elif change_rate < -0.01:
            return '下降'
        else:
            return '平稳'
    
    @staticmethod
    def calculate_amplitude(high_prices: list, low_prices: list) -> Optional[float]:
        """
        计算振幅
        :param high_prices: 最高价列表
        :param low_prices: 最低价列表
        :return: 振幅(%)
        """
        if not high_prices or not low_prices:
            return None
        
        high = max(high_prices)
        low = min(low_prices)
        
        if low == 0:
            return None
        
        return round(float((high - low) / low * 100), 4)
