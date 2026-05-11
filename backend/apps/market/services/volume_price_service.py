"""
量价关系分析服务
"""

from typing import Dict, Optional


class VolumePriceAnalyzer:
    """量价关系分析器"""
    
    @staticmethod
    def analyze_volume_price(price_change: float, volume_ratio: float) -> Dict:
        """
        分析量价关系
        :param price_change: 涨跌幅(%)
        :param volume_ratio: 量比
        :return: {'judgment': str, 'strength': str, 'action': str}
        """
        result = {
            'judgment': '',      # 判断结果
            'strength': '',      # 力量对比
            'action': ''         # 建议操作
        }
        
        # 定义阈值
        big_change = 3.0  # 大涨大跌阈值
        volume_breakout = 1.5  # 放量阈值
        volume_shrink = 0.7  # 缩量阈值
        
        # 判断涨跌
        if price_change > big_change:
            price_status = '大涨'
        elif price_change < -big_change:
            price_status = '大跌'
        else:
            price_status = '一般'
        
        # 判断成交量
        if volume_ratio > volume_breakout:
            volume_status = '放量'
        elif volume_ratio < volume_shrink:
            volume_status = '缩量'
        else:
            volume_status = '一般'
        
        # 量价关系矩阵
        if price_status == '大涨' and volume_status == '放量':
            result.update({
                'judgment': '放量大涨',
                'strength': '多头力量强',
                'action': '持有或加仓'
            })
        elif price_status == '大涨' and volume_status == '缩量':
            result.update({
                'judgment': '缩量大涨',
                'strength': '多头逼空,筹码锁定好',
                'action': '可持有'
            })
        elif price_status == '大跌' and volume_status == '放量':
            result.update({
                'judgment': '放量大跌',
                'strength': '空头力量强',
                'action': '减仓或离场'
            })
        elif price_status == '大跌' and volume_status == '缩量':
            result.update({
                'judgment': '缩量大跌',
                'strength': '空头逼多,无人接盘',
                'action': '离场观望'
            })
        elif price_status == '一般' and volume_status == '放量':
            result.update({
                'judgment': '放量滞涨',
                'strength': '多空焦灼,可能变盘',
                'action': '警惕'
            })
        elif price_status == '一般' and volume_status == '缩量':
            result.update({
                'judgment': '缩量整理',
                'strength': '情绪弱,焦灼',
                'action': '观察'
            })
        else:
            result.update({
                'judgment': '量价配合一般',
                'strength': '无明显特征',
                'action': '继续观察'
            })
        
        return result
    
    @staticmethod
    def analyze_obv_signal(price_trend: str, obv_trend: str) -> Dict:
        """
        分析OBV信号
        :param price_trend: 价格趋势('上升'/'下降'/'平稳')
        :param obv_trend: OBV趋势('上升'/'下降'/'平稳')
        :return: {'signal': str, 'meaning': str}
        """
        result = {
            'signal': '',
            'meaning': ''
        }
        
        if price_trend == '上升' and obv_trend == '下降':
            result.update({
                'signal': '量价背离',
                'meaning': '买盘无力,股价可能会跌'
            })
        elif price_trend == '下降' and obv_trend == '上升':
            result.update({
                'signal': '量价背离',
                'meaning': '买盘旺盛,逢低接手,股价可能止跌回升'
            })
        elif obv_trend == '上升':
            result.update({
                'signal': 'OBV上升',
                'meaning': '买气逐渐坚强,买进信号'
            })
        elif obv_trend == '下降':
            result.update({
                'signal': 'OBV下降',
                'meaning': '卖压增加,卖出信号'
            })
        else:
            result.update({
                'signal': 'OBV平稳',
                'meaning': '买卖平衡,继续观察'
            })
        
        return result
    
    @staticmethod
    def check_volume_breakout(current_volume: int, avg_volume: int, threshold: float = 1.5) -> bool:
        """
        检查是否放量突破
        :param current_volume: 当前成交量
        :param avg_volume: 平均成交量
        :param threshold: 放量阈值
        :return: 是否放量突破
        """
        if avg_volume == 0:
            return False
        
        volume_ratio = current_volume / avg_volume
        return volume_ratio >= threshold
    
    @staticmethod
    def check_volume_shrink(current_volume: int, avg_volume: int, threshold: float = 0.7) -> bool:
        """
        检查是否缩量
        :param current_volume: 当前成交量
        :param avg_volume: 平均成交量
        :param threshold: 缩量阈值
        :return: 是否缩量
        """
        if avg_volume == 0:
            return False
        
        volume_ratio = current_volume / avg_volume
        return volume_ratio <= threshold
