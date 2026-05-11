"""
大盘状态判断服务
"""

from typing import Dict, Optional
from datetime import date, timedelta


class MarketStateCalculator:
    """大盘状态计算器"""
    
    @staticmethod
    def calculate_tech_state(
        change_20d: float,
        rsi_14: float,
        max_gain_20d: float = 0,
        amplitude_5d: float = 0,
        volume_slope_decreasing_days: int = 0
    ) -> str:
        """
        计算技术状态
        优先级: 陷阱区 > 底部区 > 上涨区 > 震荡区
        
        :param change_20d: 20日涨跌幅(%)
        :param rsi_14: 14日RSI
        :param max_gain_20d: 20日最大涨幅(%)
        :param amplitude_5d: 最近5日振幅(%)
        :param volume_slope_decreasing_days: 成交量斜度持续下降天数
        :return: 技术状态
        """
        # 1. 陷阱区判断
        if (max_gain_20d > 8 and 
            amplitude_5d < 3 and 
            volume_slope_decreasing_days > 5):
            return '陷阱区'
        
        # 2. 底部区判断
        if (change_20d < -8 and rsi_14 < 35) or \
           change_20d < -12 or \
           rsi_14 < 25:
            return '底部区'
        
        # 3. 上涨区判断
        if change_20d > 5 or rsi_14 > 70:
            return '上涨区'
        
        # 4. 震荡区判断
        if -5 <= change_20d <= 5:
            return '震荡区'
        
        # 默认返回震荡区
        return '震荡区'
    
    @staticmethod
    def calculate_cycle_state(
        change_20d: float,
        rsi_14: float,
        has_divergence: bool = False,
        is_above_ma5: bool = False,
        is_below_ma60: bool = False
    ) -> str:
        """
        计算大周期状态
        优先级: 主升浪 > 赶顶期 > 正常趋势 > 下跌期 > 震荡期
        
        :param change_20d: 20日涨跌幅(%)
        :param rsi_14: 14日RSI
        :param has_divergence: 是否出现顶背离
        :param is_above_ma5: 是否沿5日线上涨
        :param is_below_ma60: 是否跌破60日线
        :return: 大周期状态
        """
        # 1. 主升浪
        if change_20d > 10 and rsi_14 > 65 and is_above_ma5:
            return '主升浪'
        
        # 2. 赶顶期
        if change_20d > 10 and has_divergence:
            return '赶顶期'
        
        # 3. 正常趋势
        if 3 <= change_20d <= 10 and 50 <= rsi_14 <= 65:
            return '正常趋势'
        
        # 4. 下跌期
        if change_20d < -5 or is_below_ma60:
            return '下跌期'
        
        # 5. 震荡期
        return '震荡期'
    
    @staticmethod
    def calculate_major_trend(
        is_above_ma60: bool,
        ma60_direction: str,
        index_verification: bool = True
    ) -> str:
        """
        计算主要趋势(道氏理论)
        
        :param is_above_ma60: 是否在60日线上方
        :param ma60_direction: 60日线方向('向上'/'向下'/'走平')
        :param index_verification: 指数验证是否一致
        :return: 主要趋势
        """
        if is_above_ma60 and ma60_direction == '向上' and index_verification:
            return '牛市'
        elif not is_above_ma60 and ma60_direction == '向下':
            return '熊市'
        else:
            return '震荡'
    
    @staticmethod
    def calculate_event_correction(active_events: list) -> float:
        """
        计算事件修正值
        
        :param active_events: 活跃事件列表 [{'correction_value': float, 'priority': int}]
        :return: 修正值
        """
        if not active_events:
            return 0.0
        
        # 按优先级排序(数字越小优先级越高)
        sorted_events = sorted(active_events, key=lambda x: x.get('priority', 999))
        
        # 取最高优先级事件的修正值
        main_correction = sorted_events[0].get('correction_value', 0)
        
        # 如果有多个事件,可以叠加累加,但限制在-2到2范围
        total_correction = main_correction
        for event in sorted_events[1:]:
            total_correction += event.get('correction_value', 0)
        
        # 限制范围
        total_correction = max(-2.0, min(2.0, total_correction))
        
        return round(total_correction, 2)
    
    @staticmethod
    def calculate_final_state(tech_state: str, event_correction: float) -> str:
        """
        计算最终状态(技术状态 + 事件修正)
        
        :param tech_state: 技术状态
        :param event_correction: 事件修正值
        :return: 最终状态
        """
        # 状态等级映射
        state_levels = {
            '底部区': 1,
            '震荡区': 2,
            '上涨区': 3,
            '陷阱区': 4
        }
        
        # 反向映射
        level_states = {v: k for k, v in state_levels.items()}
        
        # 获取当前状态等级
        current_level = state_levels.get(tech_state, 2)
        
        # 应用修正
        if event_correction > 0:
            # 正向修正(向上调)
            new_level = max(1, current_level - int(event_correction))
        elif event_correction < 0:
            # 负向修正(向下调)
            new_level = min(4, current_level + abs(int(event_correction)))
        else:
            new_level = current_level
        
        return level_states.get(new_level, tech_state)
    
    @staticmethod
    def get_max_position(final_state: str) -> int:
        """
        根据最终状态获取建议仓位上限
        
        :param final_state: 最终状态
        :return: 仓位上限(%)
        """
        position_map = {
            '底部区': 100,
            '震荡区': 30,
            '上涨区': 50,
            '陷阱区': 10
        }
        return position_map.get(final_state, 30)
    
    @staticmethod
    def get_etf_action(final_state: str) -> str:
        """
        根据最终状态获取ETF操作建议
        
        :param final_state: 最终状态
        :return: 操作建议
        """
        action_map = {
            '底部区': '分批买入',
            '震荡区': '持有不动',
            '上涨区': '持有或分批卖出',
            '陷阱区': '只卖不买',
            '主升浪': '坚定持有',
            '赶顶期': '分批卖出',
            '下跌期': '清仓观望'
        }
        return action_map.get(final_state, '持有')
    
    @staticmethod
    def get_individual_action(final_state: str) -> str:
        """
        根据最终状态获取个股操作建议
        
        :param final_state: 最终状态
        :return: 操作建议
        """
        action_map = {
            '底部区': '可积极选股',
            '震荡区': '仅做T和箱体操作',
            '上涨区': '谨慎操作',
            '陷阱区': '禁止开新仓',
            '下跌期': '绝对空仓'
        }
        return action_map.get(final_state, '观望')
    
    @staticmethod
    def check_exit_level(
        has_divergence: bool,
        is_below_ma10: bool,
        is_below_ma20: bool,
        ma5_cross_ma20: bool = False
    ) -> Dict:
        """
        检查分级离场信号
        
        :param has_divergence: 是否出现顶背离
        :param is_below_ma10: 是否跌破10日线
        :param is_below_ma20: 是否跌破20日线
        :param ma5_cross_ma20: 5日线是否下穿20日线
        :return: {'exit_level': int, 'exit_reason': str, 'action': str}
        """
        # 三级离场(最高优先级)
        if is_below_ma20 or ma5_cross_ma20:
            return {
                'exit_level': 3,
                'exit_reason': '跌破20日线或5日线下穿20日线',
                'action': '清仓剩余'
            }
        
        # 二级离场
        if is_below_ma10:
            return {
                'exit_level': 2,
                'exit_reason': '跌破10日线',
                'action': '再卖出1/3'
            }
        
        # 一级离场
        if has_divergence:
            return {
                'exit_level': 1,
                'exit_reason': '出现顶背离',
                'action': '卖出1/3仓位'
            }
        
        # 无离场信号
        return {
            'exit_level': 0,
            'exit_reason': '',
            'action': '继续持有'
        }
    
    @staticmethod
    def check_macd_divergence(
        prices: list,
        macd_values: list
    ) -> bool:
        """
        检查MACD顶背离
        
        :param prices: 价格列表
        :param macd_values: MACD值列表
        :return: 是否顶背离
        """
        if len(prices) < 2 or len(macd_values) < 2:
            return False
        
        # 简化版: 价格创新高但MACD未创新高
        price_new_high = prices[-1] > max(prices[-20:-1]) if len(prices) > 20 else False
        macd_not_high = macd_values[-1] < max(macd_values[-20:-1]) if len(macd_values) > 20 else False
        
        return price_new_high and macd_not_high
