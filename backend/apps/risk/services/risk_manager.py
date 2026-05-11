"""
风险管理服务
"""

from typing import Dict, Optional
from decimal import Decimal
from datetime import date, timedelta


class RiskManager:
    """风险管理器"""
    
    @staticmethod
    def calculate_position_size(
        total_capital: float,
        risk_percentage: float = 2.0,
        stop_loss_percentage: float = 5.0,
        max_single_position: float = 20.0
    ) -> Dict:
        """
        计算建议买入仓位
        
        :param total_capital: 总资金
        :param risk_percentage: 单笔风险比例(%)
        :param stop_loss_percentage: 止损幅度(%)
        :param max_single_position: 单只个股最大仓位(%)
        :return: {'max_amount': float, 'position_percentage': float, 'risk_amount': float}
        """
        # 计算最大可承受损失金额
        risk_amount = total_capital * (risk_percentage / 100)
        
        # 计算最大买入金额
        if stop_loss_percentage > 0:
            max_amount = risk_amount / (stop_loss_percentage / 100)
        else:
            max_amount = total_capital
        
        # 限制单只个股最大仓位
        max_amount_by_position = total_capital * (max_single_position / 100)
        max_amount = min(max_amount, max_amount_by_position)
        
        # 计算仓位占比
        position_percentage = (max_amount / total_capital * 100) if total_capital > 0 else 0
        
        return {
            'max_amount': round(max_amount, 2),
            'position_percentage': round(position_percentage, 2),
            'risk_amount': round(risk_amount, 2)
        }
    
    @staticmethod
    def check_daily_drawdown(
        current_value: float,
        previous_value: float,
        threshold: float = -3.0
    ) -> Dict:
        """
        检查单日回撤
        
        :param current_value: 当前总市值
        :param previous_value: 昨日总市值
        :param threshold: 回撤阈值(%)
        :return: {'triggered': bool, 'drawdown': float, 'action': str}
        """
        if previous_value == 0:
            return {
                'triggered': False,
                'drawdown': 0.0,
                'action': ''
            }
        
        drawdown = ((current_value - previous_value) / previous_value) * 100
        
        if drawdown <= threshold:
            return {
                'triggered': True,
                'drawdown': round(drawdown, 4),
                'action': f'单日回撤超{abs(threshold)}%,建议非ETF仓位降至10%以下,休息3天'
            }
        
        return {
            'triggered': False,
            'drawdown': round(drawdown, 4),
            'action': ''
        }
    
    @staticmethod
    def check_weekly_drawdown(
        current_value: float,
        week_start_value: float,
        threshold: float = -6.0
    ) -> Dict:
        """
        检查周回撤
        
        :param current_value: 当前总市值
        :param week_start_value: 周初总市值
        :param threshold: 回撤阈值(%)
        :return: {'triggered': bool, 'drawdown': float, 'action': str}
        """
        if week_start_value == 0:
            return {
                'triggered': False,
                'drawdown': 0.0,
                'action': ''
            }
        
        drawdown = ((current_value - week_start_value) / week_start_value) * 100
        
        if drawdown <= threshold:
            return {
                'triggered': True,
                'drawdown': round(drawdown, 4),
                'action': f'周回撤超{abs(threshold)}%,强制风控,请休息3个交易日'
            }
        
        return {
            'triggered': False,
            'drawdown': round(drawdown, 4),
            'action': ''
        }
    
    @staticmethod
    def check_consecutive_losses(
        consecutive_losses: int,
        threshold: int = 2
    ) -> Dict:
        """
        检查连续亏损
        
        :param consecutive_losses: 连续亏损次数
        :param threshold: 阈值
        :return: {'triggered': bool, 'action': str}
        """
        if consecutive_losses >= threshold:
            return {
                'triggered': True,
                'action': f'已触发连续亏损保护({consecutive_losses}次),今日停止个股交易'
            }
        
        return {
            'triggered': False,
            'action': ''
        }
    
    @staticmethod
    def check_single_trade_risk(
        position_size: float,
        stop_loss_percentage: float,
        total_capital: float,
        risk_limit: float = 2.0
    ) -> Dict:
        """
        检查单笔交易风险
        
        :param position_size: 仓位大小
        :param stop_loss_percentage: 止损幅度(%)
        :param total_capital: 总资金
        :param risk_limit: 风险限额(%)
        :return: {'exceeded': bool, 'risk_percentage': float, 'warning': str}
        """
        if position_size == 0 or stop_loss_percentage == 0:
            return {
                'exceeded': False,
                'risk_percentage': 0.0,
                'warning': ''
            }
        
        # 计算实际风险比例
        risk_amount = position_size * (stop_loss_percentage / 100)
        actual_risk_percentage = (risk_amount / total_capital * 100) if total_capital > 0 else 0
        
        if actual_risk_percentage >= risk_limit * 0.9:  # 接近限额90%时警告
            return {
                'exceeded': actual_risk_percentage > risk_limit,
                'risk_percentage': round(actual_risk_percentage, 4),
                'warning': f'单笔风险接近限额({actual_risk_percentage:.2f}%/{risk_limit}%),请注意'
            }
        
        return {
            'exceeded': False,
            'risk_percentage': round(actual_risk_percentage, 4),
            'warning': ''
        }
    
    @staticmethod
    def check_position_limit(
        current_position: float,
        new_position: float,
        total_capital: float,
        limit_percentage: float = 50.0
    ) -> Dict:
        """
        检查仓位上限
        
        :param current_position: 当前持仓金额
        :param new_position: 新开仓金额
        :param total_capital: 总资金
        :param limit_percentage: 仓位上限(%)
        :return: {'allowed': bool, 'current_percentage': float, 'new_percentage': float}
        """
        current_percentage = (current_position / total_capital * 100) if total_capital > 0 else 0
        new_percentage = ((current_position + new_position) / total_capital * 100) if total_capital > 0 else 0
        
        return {
            'allowed': new_percentage <= limit_percentage,
            'current_percentage': round(current_percentage, 2),
            'new_percentage': round(new_percentage, 2)
        }
    
    @staticmethod
    def calculate_stop_loss(
        entry_price: float,
        stop_loss_percentage: float = 5.0
    ) -> float:
        """
        计算止损价
        
        :param entry_price: 入场价格
        :param stop_loss_percentage: 止损幅度(%)
        :return: 止损价
        """
        return round(entry_price * (1 - stop_loss_percentage / 100), 4)
    
    @staticmethod
    def calculate_take_profit(
        entry_price: float,
        take_profit_percentage: float = 10.0
    ) -> float:
        """
        计算止盈价
        
        :param entry_price: 入场价格
        :param take_profit_percentage: 止盈幅度(%)
        :return: 止盈价
        """
        return round(entry_price * (1 + take_profit_percentage / 100), 4)
    
    @staticmethod
    def calculate_risk_reward_ratio(
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> float:
        """
        计算风险收益比
        
        :param entry_price: 入场价格
        :param stop_loss: 止损价
        :param take_profit: 止盈价
        :return: 风险收益比
        """
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        
        if risk == 0:
            return 0
        
        return round(reward / risk, 2)
