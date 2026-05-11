"""
金字塔加仓服务
"""

from typing import Dict, Optional


class PyramidAddService:
    """金字塔加仓管理器"""
    
    # 默认加仓比例
    DEFAULT_ADD_RATIOS = [0.50, 0.30, 0.20]  # 第一次50%, 第二次30%, 第三次20%
    
    @staticmethod
    def check_pyramid_add(
        current_profit: float,
        price_increase: float,
        keypoint_signal: Dict,
        add_count: int = 0,
        max_add_count: int = 3,
        min_increase: float = 5.0
    ) -> Dict:
        """
        检查是否满足金字塔加仓条件
        
        :param current_profit: 当前浮盈(%)
        :param price_increase: 自上次加仓后涨幅(%)
        :param keypoint_signal: 关键点信号
        :param add_count: 已加仓次数
        :param max_add_count: 最大加仓次数
        :param min_increase: 最小涨幅要求(%)
        :return: {'allowed': bool, 'reason': str, 'add_ratio': float}
        """
        result = {
            'allowed': False,
            'reason': '',
            'add_ratio': 0.0,
            'add_count': add_count
        }
        
        # 1. 检查是否盈利
        if current_profit <= 0:
            result['reason'] = '当前持仓未盈利,禁止加仓(永不摊平亏损)'
            return result
        
        # 2. 检查加仓次数
        if add_count >= max_add_count:
            result['reason'] = f'已达最大加仓次数({max_add_count}次)'
            return result
        
        # 3. 检查涨幅
        if price_increase < min_increase:
            result['reason'] = f'涨幅{price_increase:.2%}不足{min_increase}%'
            return result
        
        # 4. 检查关键点信号
        if not keypoint_signal or not keypoint_signal.get('detected'):
            result['reason'] = '未出现连续关键点信号'
            return result
        
        # 5. 检查关键点类型
        keypoint_type = keypoint_signal.get('type', '')
        if keypoint_type != '连续关键点':
            result['reason'] = f'关键点类型"{keypoint_type}"不适合加仓,需要"连续关键点"'
            return result
        
        # 满足所有条件
        result['allowed'] = True
        result['add_count'] = add_count + 1
        result['add_ratio'] = PyramidAddService.DEFAULT_ADD_RATIOS[add_count]
        result['reason'] = f'满足加仓条件:盈利{current_profit:.2%},涨幅{price_increase:.2%},出现连续关键点'
        
        return result
    
    @staticmethod
    def calculate_add_position(
        total_planned_amount: float,
        add_count: int,
        current_price: float,
        add_ratios: list = None
    ) -> Dict:
        """
        计算加仓仓位
        
        :param total_planned_amount: 计划总投入金额
        :param add_count: 已加仓次数(0表示首次入场)
        :param current_price: 当前价格
        :param add_ratios: 加仓比例列表
        :return: {'amount': float, 'quantity': int, 'ratio': float}
        """
        if add_ratios is None:
            add_ratios = PyramidAddService.DEFAULT_ADD_RATIOS
        
        if add_count >= len(add_ratios):
            return {
                'amount': 0,
                'quantity': 0,
                'ratio': 0,
                'error': '超过最大加仓次数'
            }
        
        # 计算本次加仓金额
        ratio = add_ratios[add_count]
        amount = total_planned_amount * ratio
        
        # 计算买入数量
        quantity = int(amount / current_price) if current_price > 0 else 0
        
        return {
            'amount': round(amount, 2),
            'quantity': quantity,
            'ratio': ratio,
            'add_count': add_count + 1
        }
    
    @staticmethod
    def adjust_stop_loss_after_add(
        original_stop_loss: float,
        entry_price: float,
        add_price: float,
        add_quantity: int,
        original_quantity: int
    ) -> Dict:
        """
        加仓后调整止损位
        
        :param original_stop_loss: 原止损价
        :param entry_price: 首次入场价
        :param add_price: 加仓价格
        :param add_quantity: 加仓数量
        :param original_quantity: 原持仓数量
        :return: {'new_stop_loss': float, 'breakeven_price': float, 'reason': str}
        """
        # 计算新的平均成本
        total_cost = (entry_price * original_quantity) + (add_price * add_quantity)
        total_quantity = original_quantity + add_quantity
        breakeven_price = total_cost / total_quantity if total_quantity > 0 else entry_price
        
        # 止损位上移至盈亏平衡点
        new_stop_loss = breakeven_price * 0.98  # 留2%缓冲
        
        # 确保新止损不低于原止损
        if new_stop_loss < original_stop_loss:
            new_stop_loss = original_stop_loss
        
        return {
            'new_stop_loss': round(new_stop_loss, 4),
            'breakeven_price': round(breakeven_price, 4),
            'reason': f'止损位上移至盈亏平衡点{breakeven_price:.4f}'
        }
    
    @staticmethod
    def get_pyramid_plan(
        total_capital: float,
        entry_price: float,
        risk_percentage: float = 2.0,
        stop_loss_percentage: float = 5.0
    ) -> Dict:
        """
        生成金字塔加仓计划
        
        :param total_capital: 总资金
        :param entry_price: 入场价格
        :param risk_percentage: 风险比例(%)
        :param stop_loss_percentage: 止损幅度(%)
        :return: 完整的加仓计划
        """
        # 计算总计划金额
        risk_amount = total_capital * (risk_percentage / 100)
        total_amount = risk_amount / (stop_loss_percentage / 100)
        
        # 限制单只最大仓位
        max_amount = total_capital * 0.20
        total_amount = min(total_amount, max_amount)
        
        # 计算各阶段
        plan = {
            'total_amount': round(total_amount, 2),
            'total_quantity': int(total_amount / entry_price),
            'stages': []
        }
        
        ratios = PyramidAddService.DEFAULT_ADD_RATIOS
        remaining_amount = total_amount
        
        for i, ratio in enumerate(ratios):
            stage_amount = total_amount * ratio
            stage_quantity = int(stage_amount / entry_price)
            
            plan['stages'].append({
                'stage': i + 1,
                'name': ['首次入场', '第一次加仓', '第二次加仓'][i],
                'amount': round(stage_amount, 2),
                'quantity': stage_quantity,
                'ratio': ratio,
                'price_condition': '关键点入场' if i == 0 else f'上涨5%+连续关键点'
            })
            
            remaining_amount -= stage_amount
        
        return plan
    
    @staticmethod
    def validate_add_rules(
        current_profit: float,
        add_count: int,
        price_increase: float
    ) -> Dict:
        """
        验证加仓规则(纪律检查)
        
        :param current_profit: 当前浮盈
        :param add_count: 已加仓次数
        :param price_increase: 涨幅
        :return: {'valid': bool, 'violations': list}
        """
        violations = []
        
        # 规则1: 亏损时禁止加仓
        if current_profit <= 0:
            violations.append('违反金字塔加仓原则:禁止在亏损时加仓摊低成本')
        
        # 规则2: 检查加仓次数
        if add_count >= 3:
            violations.append('超过最大加仓次数(3次)')
        
        # 规则3: 检查涨幅间隔
        if add_count > 0 and price_increase < 5:
            violations.append('加仓间隔不足5%')
        
        return {
            'valid': len(violations) == 0,
            'violations': violations
        }
