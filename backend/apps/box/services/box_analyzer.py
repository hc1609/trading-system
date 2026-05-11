"""
箱体分析服务
"""

from typing import Dict, Optional, List, Tuple
import numpy as np


class BoxAnalyzer:
    """箱体分析器"""
    
    @staticmethod
    def identify_box(
        high_prices: List[float],
        low_prices: List[float],
        closes: List[float],
        min_touches: int = 2,
        min_height_percent: float = 3.0
    ) -> Dict:
        """
        识别箱体
        
        :param high_prices: 最高价列表
        :param low_prices: 最低价列表
        :param closes: 收盘价列表
        :param min_touches: 最小触及次数
        :param min_height_percent: 最小箱体高度(%)
        :return: 箱体信息
        """
        if len(high_prices) < 20 or len(low_prices) < 20:
            return {'identified': False, 'reason': '数据不足'}
        
        # 使用聚类方法识别支撑和压力位
        # 简化版: 使用最高价和最低价的统计
        
        # 找出主要压力位(高价的聚集区)
        resistance = BoxAnalyzer._find_cluster(high_prices[-60:], 'high')
        
        # 找出主要支撑位(低价的聚集区)
        support = BoxAnalyzer._find_cluster(low_prices[-60:], 'low')
        
        if not resistance or not support:
            return {'identified': False, 'reason': '未找到明确的箱体上下沿'}
        
        # 计算箱体高度
        box_height = resistance - support
        box_height_percent = (box_height / support * 100) if support > 0 else 0
        
        # 检查箱体高度是否合理
        if box_height_percent < min_height_percent:
            return {'identified': False, 'reason': f'箱体高度{box_height_percent:.2f}%不足{min_height_percent}%'}
        
        # 计算触及次数
        top_touches = BoxAnalyzer._count_touches(high_prices[-60:], resistance, tolerance=0.02)
        bottom_touches = BoxAnalyzer._count_touches(low_prices[-60:], support, tolerance=0.02)
        
        # 检查触及次数
        if top_touches < min_touches or bottom_touches < min_touches:
            return {
                'identified': False,
                'reason': f'触及次数不足(顶部{top_touches}次,底部{bottom_touches}次)'
            }
        
        return {
            'identified': True,
            'top': round(resistance, 4),
            'bottom': round(support, 4),
            'height': round(box_height, 4),
            'height_percent': round(box_height_percent, 4),
            'top_touches': top_touches,
            'bottom_touches': bottom_touches,
            'status': 'active'
        }
    
    @staticmethod
    def _find_cluster(prices: List[float], price_type: str) -> Optional[float]:
        """
        找出价格聚集区(简化版)
        
        :param prices: 价格列表
        :param price_type: 'high' 或 'low'
        :return: 聚集区价格
        """
        if not prices:
            return None
        
        # 使用分位数方法
        if price_type == 'high':
            # 压力位: 使用80%分位数
            return np.percentile(prices, 80)
        else:
            # 支撑位: 使用20%分位数
            return np.percentile(prices, 20)
    
    @staticmethod
    def _count_touches(
        prices: List[float],
        level: float,
        tolerance: float = 0.02
    ) -> int:
        """
        计算价格触及某水平的次数
        
        :param prices: 价格列表
        :param level: 目标水平
        :param tolerance: 容差(2%)
        :return: 触及次数
        """
        count = 0
        for price in prices:
            if abs(price - level) / level <= tolerance:
                count += 1
        return count
    
    @staticmethod
    def get_box_position(
        current_price: float,
        box_top: float,
        box_bottom: float
    ) -> Dict:
        """
        判断当前价格在箱体中的位置
        
        :param current_price: 当前价格
        :param box_top: 箱体上沿
        :param box_bottom: 箱体下沿
        :return: {'zone': str, 'position_percent': float}
        """
        box_height = box_top - box_bottom
        
        if box_height == 0:
            return {'zone': '未知', 'position_percent': 0}
        
        # 计算位置百分比
        position_percent = ((current_price - box_bottom) / box_height) * 100
        
        # 判断区域
        if position_percent >= 66.67:
            zone = '上1/3区'
        elif position_percent >= 33.33:
            zone = '中1/3区'
        else:
            zone = '下1/3区'
        
        return {
            'zone': zone,
            'position_percent': round(position_percent, 2),
            'distance_to_top': round(box_top - current_price, 4),
            'distance_to_bottom': round(current_price - box_bottom, 4)
        }
    
    @staticmethod
    def get_box_action(
        current_price: float,
        box_top: float,
        box_bottom: float,
        bottom_confirm_count: int,
        volume_ratio: float = 1.0,
        box_status: str = 'active'
    ) -> Dict:
        """
        获取箱体操作建议
        
        :param current_price: 当前价格
        :param box_top: 箱体上沿
        :param box_bottom: 箱体下沿
        :param bottom_confirm_count: 底部确认次数
        :param volume_ratio: 量比
        :param box_status: 箱体状态
        :return: {'action': str, 'reason': str, 'stop_loss': float}
        """
        result = {
            'action': '',
            'reason': '',
            'stop_loss': 0.0
        }
        
        # 检查是否跌破下沿
        if current_price < box_bottom * 0.98:
            result.update({
                'action': '清仓止损',
                'reason': '跌破箱体下沿,坚决止损',
                'stop_loss': box_bottom
            })
            return result
        
        # 检查是否突破上沿
        if current_price > box_top * 1.02:
            if volume_ratio >= 1.5:
                result.update({
                    'action': '有效突破,持有或加仓',
                    'reason': f'放量突破箱体上沿{box_top},量比{volume_ratio}',
                    'stop_loss': box_top
                })
            else:
                result.update({
                    'action': '减仓,可能是假突破',
                    'reason': f'缩量突破箱体上沿,大概率假突破',
                    'stop_loss': box_bottom
                })
            return result
        
        # 判断在箱体中的位置
        position = BoxAnalyzer.get_box_position(current_price, box_top, box_bottom)
        zone = position['zone']
        
        # 根据位置和确认次数给出建议
        if zone == '下1/3区':
            if bottom_confirm_count >= 3:
                result.update({
                    'action': '买入',
                    'reason': f'底部已确认{bottom_confirm_count}次,强支撑',
                    'stop_loss': box_bottom
                })
            elif bottom_confirm_count >= 2:
                result.update({
                    'action': '可买入',
                    'reason': f'底部已确认{bottom_confirm_count}次,支撑较强',
                    'stop_loss': box_bottom
                })
            else:
                result.update({
                    'action': '减仓或观望',
                    'reason': '首次底部不牢固,可能跌破',
                    'stop_loss': box_bottom
                })
        
        elif zone == '中1/3区':
            result.update({
                'action': '持有观察',
                'reason': '处于箱体中部,继续观察',
                'stop_loss': box_bottom
            })
        
        else:  # 上1/3区
            result.update({
                'action': '减仓或止盈',
                'reason': '接近箱体上沿,可考虑减仓',
                'stop_loss': box_bottom
            })
        
        return result
    
    @staticmethod
    def check_box_breakout(
        current_price: float,
        box_top: float,
        box_bottom: float,
        volume_ratio: float,
        stand_days: int = 0
    ) -> Dict:
        """
        检查箱体突破
        
        :param current_price: 当前价格
        :param box_top: 箱体上沿
        :param box_bottom: 箱体下沿
        :param volume_ratio: 量比
        :param stand_days: 突破后站稳天数
        :return: {'direction': str, 'valid': bool, 'confidence': float}
        """
        result = {
            'direction': 'none',
            'valid': False,
            'confidence': 0.0
        }
        
        # 向上突破
        if current_price > box_top * 1.02:
            result['direction'] = 'up'
            
            if volume_ratio >= 1.5 and stand_days >= 3:
                result['valid'] = True
                result['confidence'] = 0.9
            elif volume_ratio >= 1.5:
                result['valid'] = False
                result['confidence'] = 0.6
            else:
                result['valid'] = False
                result['confidence'] = 0.3
        
        # 向下突破
        elif current_price < box_bottom * 0.98:
            result['direction'] = 'down'
            
            if volume_ratio >= 1.5:
                result['valid'] = True
                result['confidence'] = 0.85
            else:
                result['valid'] = False
                result['confidence'] = 0.5
        
        return result
    
    @staticmethod
    def calculate_box_target(
        box_top: float,
        box_bottom: float,
        breakout_price: float,
        direction: str = 'up'
    ) -> float:
        """
        计算箱体突破后的目标位
        
        :param box_top: 箱体上沿
        :param box_bottom: 箱体下沿
        :param breakout_price: 突破价格
        :param direction: 突破方向
        :return: 目标位
        """
        box_height = box_top - box_bottom
        
        if direction == 'up':
            return breakout_price + box_height
        else:
            return breakout_price - box_height
