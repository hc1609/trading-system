"""
开仓检查服务
"""

from typing import Dict, Optional


class OpenPositionChecker:
    """开仓条件检查器"""
    
    @staticmethod
    def check_open_position(
        market_state: str,
        keypoint_signal: Dict,
        volume_ratio: float,
        risk_status: Dict,
        current_position: float,
        new_position: float,
        total_capital: float,
        individual_position_limit: float = 50.0,
        single_stock_limit: float = 20.0
    ) -> Dict:
        """
        检查是否满足开仓条件
        
        :param market_state: 大盘状态
        :param keypoint_signal: 关键点信号
        :param volume_ratio: 量比
        :param risk_status: 风控状态
        :param current_position: 当前持仓金额
        :param new_position: 新开仓金额
        :param total_capital: 总资金
        :param individual_position_limit: 个股总仓位上限(%)
        :param single_stock_limit: 单只个股仓位上限(%)
        :return: {'allowed': bool, 'reasons': list, 'warnings': list}
        """
        result = {
            'allowed': False,
            'reasons': [],
            'warnings': [],
            'checks': {}
        }
        
        # 1. 检查大盘状态
        if market_state in ['陷阱区', '下跌期']:
            result['reasons'].append(f'当前为{market_state},禁止开新仓')
            result['checks']['大盘状态'] = False
        else:
            result['checks']['大盘状态'] = True
        
        # 2. 检查关键点信号
        if not keypoint_signal or not keypoint_signal.get('detected'):
            result['reasons'].append('没有出现关键点信号,请等待明确的入场时机')
            result['checks']['关键点信号'] = False
        else:
            result['checks']['关键点信号'] = True
        
        # 3. 检查成交量
        if volume_ratio < 1.5:
            result['reasons'].append(f'成交量未显著放大(量比{volume_ratio}<1.5),关键点信号不确认')
            result['checks']['成交量验证'] = False
        else:
            result['checks']['成交量验证'] = True
        
        # 4. 检查风控状态
        if risk_status.get('risk_lock'):
            result['reasons'].append(f'风控锁定: {risk_status.get("lock_reason", "")}')
            result['checks']['风控状态'] = False
        elif risk_status.get('consecutive_losses', 0) >= 2:
            result['reasons'].append('连续亏损2次,今日停止个股交易')
            result['checks']['风控状态'] = False
        else:
            result['checks']['风控状态'] = True
        
        # 5. 检查个股总仓位
        current_individual_percentage = (current_position / total_capital * 100) if total_capital > 0 else 0
        new_individual_percentage = ((current_position + new_position) / total_capital * 100) if total_capital > 0 else 0
        
        if new_individual_percentage > individual_position_limit:
            result['reasons'].append(f'个股总仓位将达{new_individual_percentage:.1f}%,超过上限{individual_position_limit}%')
            result['checks']['个股总仓位'] = False
        else:
            result['checks']['个股总仓位'] = True
        
        # 6. 检查单只个股仓位
        single_stock_percentage = (new_position / total_capital * 100) if total_capital > 0 else 0
        
        if single_stock_percentage > single_stock_limit:
            result['warnings'].append(f'单只个股仓位{single_stock_percentage:.1f}%,建议不超过{single_stock_limit}%')
            result['checks']['单只个股仓位'] = False
        else:
            result['checks']['单只个股仓位'] = True
        
        # 综合判断
        all_passed = all(result['checks'].values())
        
        if all_passed:
            result['allowed'] = True
            result['reasons'].append('满足所有开仓条件')
        else:
            result['allowed'] = False
        
        return result
    
    @staticmethod
    def check_sector_sync(
        stock_sector: str,
        sector_trend: str,
        market_trend: str
    ) -> bool:
        """
        检查板块是否同步
        
        :param stock_sector: 股票所属板块
        :param sector_trend: 板块趋势
        :param market_trend: 大盘趋势
        :return: 是否同步
        """
        # 板块和大盘同向
        if sector_trend == 'up' and market_trend in ['up', '牛市']:
            return True
        
        return False
    
    @staticmethod
    def calculate_position_size_by_risk(
        total_capital: float,
        entry_price: float,
        stop_loss_price: float,
        risk_percentage: float = 2.0,
        max_single_position: float = 20.0
    ) -> Dict:
        """
        根据风险计算仓位大小
        
        :param total_capital: 总资金
        :param entry_price: 入场价格
        :param stop_loss_price: 止损价格
        :param risk_percentage: 风险比例(%)
        :param max_single_position: 单只最大仓位(%)
        :return: {'quantity': int, 'amount': float, 'risk_amount': float}
        """
        # 计算每股风险
        risk_per_share = entry_price - stop_loss_price
        
        if risk_per_share <= 0:
            return {
                'quantity': 0,
                'amount': 0,
                'risk_amount': 0,
                'error': '止损价不能高于或等于入场价'
            }
        
        # 计算最大可承受损失
        max_risk_amount = total_capital * (risk_percentage / 100)
        
        # 计算买入数量
        quantity = int(max_risk_amount / risk_per_share)
        
        # 计算买入金额
        amount = quantity * entry_price
        
        # 检查是否超过单只仓位限制
        max_amount_by_position = total_capital * (max_single_position / 100)
        
        if amount > max_amount_by_position:
            quantity = int(max_amount_by_position / entry_price)
            amount = quantity * entry_price
        
        return {
            'quantity': quantity,
            'amount': round(amount, 2),
            'risk_amount': round(quantity * risk_per_share, 2)
        }
    
    @staticmethod
    def validate_entry_checklist(
        checklist: Dict
    ) -> Dict:
        """
        验证入场检查清单
        
        :param checklist: 检查项字典
        :return: {'passed': bool, 'score': int, 'failed_items': list}
        """
        required_items = [
            '大盘趋势向上',
            '关键点信号',
            '成交量放大',
            '止损设定',
            '风险可控'
        ]
        
        optional_items = [
            '站稳3天',
            '板块同步',
            '筹码充分换手'
        ]
        
        failed_items = []
        passed_count = 0
        
        # 检查必填项
        for item in required_items:
            if not checklist.get(item, False):
                failed_items.append(item)
            else:
                passed_count += 1
        
        # 检查可选项
        for item in optional_items:
            if checklist.get(item, False):
                passed_count += 1
        
        total_items = len(required_items) + len(optional_items)
        score = int((passed_count / total_items) * 100)
        
        # 必填项必须全部通过
        passed = len(failed_items) == 0 and score >= 70
        
        return {
            'passed': passed,
            'score': score,
            'failed_items': failed_items,
            'passed_count': passed_count,
            'total_count': total_items
        }
