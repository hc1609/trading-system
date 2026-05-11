"""
ETF策略服务
"""

from typing import Dict, Optional


class ETFStrategy:
    """ETF策略管理器"""
    
    @staticmethod
    def get_etf_action(final_state: str, cycle_state: str = '') -> Dict:
        """
        根据市场状态获取ETF操作建议
        
        :param final_state: 最终状态
        :param cycle_state: 大周期状态
        :return: {'action': str, 'position': str, 'stop_loss': str, 'note': str}
        """
        actions = {
            '底部区': {
                'action': '分批买入',
                'position': '25%-50%',
                'stop_loss': '跌破前低',
                'note': '分2批买入:进入底部区买25%,继续下跌>5%再买25%'
            },
            '震荡区': {
                'action': '持有不动',
                'position': '维持当前',
                'stop_loss': '箱体下沿',
                'note': '不买不卖,观望为主'
            },
            '上涨区': {
                'action': '持有或分批卖出',
                'position': '逐步减仓',
                'stop_loss': '20日线',
                'note': '出现量价背离时卖出1/2,再次背离清仓'
            },
            '主升浪': {
                'action': '坚定持有',
                'position': '满仓持有',
                'stop_loss': '20日线或-10%',
                'note': 'RSI>70忽略,止损放宽至20日线,不做T'
            },
            '赶顶期': {
                'action': '分批卖出',
                'position': '逐步清仓',
                'stop_loss': '10日线',
                'note': '按分级离场规则执行:一级卖1/3,二级再卖1/3,三级清仓'
            },
            '陷阱区': {
                'action': '只卖不买',
                'position': '清仓或减仓',
                'stop_loss': '立即止损',
                'note': '如有持仓可卖出,不加仓'
            },
            '下跌期': {
                'action': '清仓观望',
                'position': '空仓',
                'stop_loss': '-',
                'note': '转为现金或逆回购'
            }
        }
        
        return actions.get(final_state, {
            'action': '观望',
            'position': '空仓',
            'stop_loss': '-',
            'note': '等待明确信号'
        })
    
    @staticmethod
    def calculate_batch_buy(
        total_capital: float,
        current_price: float,
        first_buy_triggered: bool = False,
        second_buy_drop: float = 0,
        extreme_drop: bool = False
    ) -> Dict:
        """
        计算分批买入建议
        
        :param total_capital: 总资金
        :param current_price: 当前价格
        :param first_buy_triggered: 是否触发第一批买入
        :param second_buy_drop: 第二批买入跌幅(%)
        :param extreme_drop: 是否极端超跌
        :return: 买入建议
        """
        result = {
            'first_buy': {'triggered': False, 'amount': 0, 'quantity': 0},
            'second_buy': {'triggered': False, 'amount': 0, 'quantity': 0},
            'third_buy': {'triggered': False, 'amount': 0, 'quantity': 0}
        }
        
        # 第一批:进入底部区买25%
        if first_buy_triggered and current_price > 0:
            amount = total_capital * 0.25
            result['first_buy'] = {
                'triggered': True,
                'amount': round(amount, 2),
                'quantity': int(amount / current_price)
            }
        
        # 第二批:继续下跌>5%再买25%
        if second_buy_drop >= 5 and current_price > 0:
            amount = total_capital * 0.25
            result['second_buy'] = {
                'triggered': True,
                'amount': round(amount, 2),
                'quantity': int(amount / current_price)
            }
        
        # 第三批:极端超跌买剩余
        if extreme_drop and current_price > 0:
            amount = total_capital * 0.25  # 剩余25%
            result['third_buy'] = {
                'triggered': True,
                'amount': round(amount, 2),
                'quantity': int(amount / current_price)
            }
        
        return result
    
    @staticmethod
    def calculate_stop_loss(
        entry_price: float,
        is_main_wave: bool = False,
        ma20_price: float = 0
    ) -> Dict:
        """
        计算ETF止损位
        
        :param entry_price: 买入价
        :param is_main_wave: 是否主升浪
        :param ma20_price: 20日均线价格
        :return: {'stop_loss': float, 'type': str}
        """
        if is_main_wave:
            # 主升浪:止损放宽至-10%或20日线
            stop_loss_percentage = entry_price * 0.90
            stop_loss = max(stop_loss_percentage, ma20_price) if ma20_price > 0 else stop_loss_percentage
            return {
                'stop_loss': round(stop_loss, 4),
                'type': '主升浪止损(-10%或20日线)'
            }
        else:
            # 常规:止损-5%
            stop_loss = entry_price * 0.95
            return {
                'stop_loss': round(stop_loss, 4),
                'type': '常规止损(-5%)'
            }
    
    @staticmethod
    def check_take_profit(
        current_price: float,
        entry_price: float,
        has_divergence: bool = False,
        divergence_count: int = 0
    ) -> Dict:
        """
        检查止盈信号
        
        :param current_price: 当前价格
        :param entry_price: 买入价
        :param has_divergence: 是否出现背离
        :param divergence_count: 背离次数
        :return: {'action': str, 'percentage': float}
        """
        profit_percentage = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
        
        if divergence_count >= 2:
            return {
                'action': '清仓',
                'percentage': profit_percentage,
                'reason': '第二次背离,清仓'
            }
        elif has_divergence:
            return {
                'action': '卖出1/2',
                'percentage': profit_percentage,
                'reason': '出现量价背离,卖出1/2'
            }
        
        return {
            'action': '持有',
            'percentage': profit_percentage,
            'reason': ''
        }
