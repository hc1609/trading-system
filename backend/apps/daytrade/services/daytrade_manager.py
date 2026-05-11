"""
做T管理服务
"""

from typing import Dict, Optional
from datetime import date, timedelta


class DayTradeManager:
    """做T管理器"""
    
    @staticmethod
    def check_daytrade_allowed(
        market_state: str,
        risk_status: Dict,
        daytrade_stats: Dict
    ) -> Dict:
        """
        检查是否允许做T
        
        :param market_state: 大盘状态
        :param risk_status: 风控状态
        :param daytrade_stats: 做T统计
        :return: {'allowed': bool, 'reason': str}
        """
        result = {
            'allowed': False,
            'reason': ''
        }
        
        # 1. 检查市场状态(仅震荡区允许做T)
        if market_state != '震荡区':
            result['reason'] = f'当前为{market_state},做T已自动关闭(仅震荡区允许)'
            return result
        
        # 2. 检查风控锁定
        if risk_status.get('risk_lock'):
            result['reason'] = f'风控锁定: {risk_status.get("lock_reason", "")}'
            return result
        
        # 3. 检查做T暂停状态
        if daytrade_stats.get('is_paused'):
            pause_until = daytrade_stats.get('pause_until')
            if pause_until and date.today() <= pause_until:
                result['reason'] = f'做T暂停中,截止日期{pause_until}'
                return result
            else:
                # 暂停已过期,自动恢复
                result['allowed'] = True
                return result
        
        # 4. 检查今日连续失败
        consecutive_failures = daytrade_stats.get('consecutive_failures', 0)
        if consecutive_failures >= 2:
            result['reason'] = '今日连续失败2次,做T暂停至明日'
            return result
        
        # 通过所有检查
        result['allowed'] = True
        return result
    
    @staticmethod
    def calculate_profit_rate(
        buy_price: float,
        sell_price: float
    ) -> float:
        """
        计算做T盈亏率
        
        :param buy_price: 买入价
        :param sell_price: 卖出价
        :return: 盈亏率(%)
        """
        if buy_price <= 0:
            return 0.0
        
        return ((sell_price - buy_price) / buy_price) * 100
    
    @staticmethod
    def record_daytrade(
        buy_price: float,
        sell_price: float,
        target_profit: float = 0.75,
        stop_loss: float = 0.5
    ) -> Dict:
        """
        记录做T交易
        
        :param buy_price: 买入价
        :param sell_price: 卖出价
        :param target_profit: 目标盈利(%)
        :param stop_loss: 止损线(%)
        :return: 做T记录
        """
        profit_rate = DayTradeManager.calculate_profit_rate(buy_price, sell_price)
        
        # 判断是否成功(盈利>=0.5%)
        success = profit_rate >= 0.5
        
        return {
            'buy_price': buy_price,
            'sell_price': sell_price,
            'profit_rate': round(profit_rate, 4),
            'success': success,
            'note': f'{"成功" if success else "失败"},盈亏{profit_rate:.2f}%'
        }
    
    @staticmethod
    def calculate_success_rate(
        daytrade_records: list,
        last_n: int = 20
    ) -> Dict:
        """
        统计做T成功率
        
        :param daytrade_records: 做T记录列表
        :param last_n: 统计最近N次
        :return: {'success_rate': float, 'total': int, 'success': int}
        """
        if not daytrade_records:
            return {
                'success_rate': 0.0,
                'total': 0,
                'success': 0
            }
        
        # 取最近N次
        recent_records = daytrade_records[-last_n:]
        
        total = len(recent_records)
        success = sum(1 for r in recent_records if r.get('success', False))
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        return {
            'success_rate': round(success_rate, 2),
            'total': total,
            'success': success,
            'failed': total - success
        }
    
    @staticmethod
    def check_pause_condition(
        consecutive_failures: int,
        week_success_rate: float,
        today_trades: int
    ) -> Dict:
        """
        检查做T暂停条件
        
        :param consecutive_failures: 连续失败次数
        :param week_success_rate: 周成功率(%)
        :param today_trades: 今日交易次数
        :return: {'should_pause': bool, 'pause_until': date, 'reason': str}
        """
        result = {
            'should_pause': False,
            'pause_until': None,
            'reason': ''
        }
        
        # 条件1: 连续失败2次 → 当天暂停
        if consecutive_failures >= 2:
            result['should_pause'] = True
            result['pause_until'] = date.today() + timedelta(days=1)
            result['reason'] = '连续失败2次,当天暂停'
            return result
        
        # 条件2: 周成功率<60% → 暂停一周
        if week_success_rate < 60 and today_trades >= 5:
            result['should_pause'] = True
            result['pause_until'] = date.today() + timedelta(days=7)
            result['reason'] = f'周成功率{week_success_rate:.2f}%<60%,暂停一周'
            return result
        
        return result
    
    @staticmethod
    def check_sell_trigger(
        current_profit: float,
        target_profit: float = 0.75,
        stop_loss: float = 0.5
    ) -> Dict:
        """
        检查做T卖出触发条件
        
        :param current_profit: 当前盈利(%)
        :param target_profit: 目标盈利(%)
        :param stop_loss: 止损线(%)
        :return: {'action': str, 'reason': str}
        """
        # 达到目标盈利
        if current_profit >= target_profit:
            return {
                'action': 'sell',
                'reason': f'达到目标盈利{target_profit}%,立即卖出(不贪)'
            }
        
        # 触发止损
        if current_profit <= -stop_loss:
            return {
                'action': 'stop_loss',
                'reason': f'触发止损-{stop_loss}%,无条件卖出'
            }
        
        return {
            'action': 'hold',
            'reason': f'当前盈利{current_profit:.2f}%,继续持有'
        }
    
    @staticmethod
    def check_buy_back_allowed(
        action_type: str,
        sell_price: float,
        current_price: float,
        action_date: date
    ) -> Dict:
        """
        检查是否允许买回
        
        :param action_type: 'sold' 或 'stop_loss'
        :param sell_price: 卖出价
        :param current_price: 当前价格
        :param action_date: 卖出日期
        :return: {'allowed': bool, 'reason': str}
        """
        # 止损后处理: 当天不允许以更低价格买回
        if action_type == 'stop_loss':
            if action_date == date.today():
                if current_price < sell_price:
                    return {
                        'allowed': False,
                        'reason': '止损后当天不允许以更低价格买回'
                    }
        
        # 卖飞后处理: 当天不再追回
        if action_type == 'sold':
            if action_date == date.today():
                return {
                    'allowed': False,
                    'reason': '卖飞后当天不再追回,次日可考虑'
                }
        
        return {
            'allowed': True,
            'reason': '可以买回'
        }
    
    @staticmethod
    def generate_daytrade_plan(
        total_capital: float,
        max_position_percent: float = 25.0,
        target_profit: float = 0.75,
        stop_loss: float = 0.5
    ) -> Dict:
        """
        生成做T计划
        
        :param total_capital: 总资金
        :param max_position_percent: 最大仓位(%)
        :param target_profit: 目标盈利(%)
        :param stop_loss: 止损线(%)
        :return: 做T计划
        """
        max_amount = total_capital * (max_position_percent / 100)
        
        return {
            'max_amount': round(max_amount, 2),
            'max_position_percent': max_position_percent,
            'target_profit': target_profit,
            'stop_loss': stop_loss,
            'rules': [
                f'单次目标盈利{target_profit}%即可卖出',
                f'亏损超过{stop_loss}%无条件止损',
                '卖飞后当天不再追回',
                '止损后当天不允许以更低价格买回',
                '连续失败2次当天暂停',
                '周成功率<60%暂停一周'
            ]
        }
