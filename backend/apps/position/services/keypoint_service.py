"""
关键点识别服务
"""

from typing import Dict, Optional, List


class KeyPointDetector:
    """关键点检测器"""
    
    @staticmethod
    def detect_breakout_keypoint(
        current_price: float,
        resistance_level: float,
        volume_ratio: float,
        avg_volume: int,
        current_volume: int,
        consolidation_days: int = 0
    ) -> Dict:
        """
        检测突破关键点
        
        :param current_price: 当前价格
        :param resistance_level: 阻力位(前期高点)
        :param volume_ratio: 量比
        :param avg_volume: 平均成交量
        :param current_volume: 当前成交量
        :param consolidation_days: 盘整天数
        :return: {'detected': bool, 'strength': str, 'confidence': float}
        """
        result = {
            'detected': False,
            'type': '突破关键点',
            'strength': '',
            'confidence': 0.0,
            'reason': ''
        }
        
        # 检查是否突破阻力位
        breakout = current_price >= resistance_level * 1.02  # 2%突破确认
        
        if not breakout:
            result['reason'] = '未突破阻力位'
            return result
        
        # 检查成交量
        volume_ok = volume_ratio >= 1.5
        
        if not volume_ok:
            result['reason'] = '成交量不足(量比<1.5)'
            return result
        
        # 判断强度
        if volume_ratio > 2.0:
            result['strength'] = '强'
            result['confidence'] = 0.9
        elif volume_ratio > 1.5:
            result['strength'] = '中'
            result['confidence'] = 0.7
        else:
            result['strength'] = '弱'
            result['confidence'] = 0.5
        
        result['detected'] = True
        result['reason'] = f'放量突破阻力位{resistance_level},量比{volume_ratio}'
        
        return result
    
    @staticmethod
    def detect_pullback_keypoint(
        current_price: float,
        recent_high: float,
        recent_low: float,
        volume_ratio: float,
        trend: str = 'up',
        pullback_ratio: float = 0
    ) -> Dict:
        """
        检测自然回撤关键点(回调买入点)
        
        :param current_price: 当前价格
        :param recent_high: 近期高点
        :param recent_low: 近期低点(回调低点)
        :param volume_ratio: 量比
        :param trend: 趋势方向
        :param pullback_ratio: 回调比例(%)
        :return: 检测结果
        """
        result = {
            'detected': False,
            'type': '自然回撤关键点',
            'strength': '',
            'confidence': 0.0,
            'reason': ''
        }
        
        # 只在上升趋势中检测
        if trend != 'up':
            result['reason'] = '非上升趋势'
            return result
        
        # 检查回调幅度(应为前一波段的1/3到1/2)
        if not (0.33 <= pullback_ratio <= 0.5):
            result['reason'] = f'回调幅度{pullback_ratio:.2%}不在合理范围(33%-50%)'
            return result
        
        # 检查是否缩量回调后放量启动
        if volume_ratio < 1.5:
            result['reason'] = '未放量启动'
            return result
        
        # 判断强度
        if volume_ratio > 2.0:
            result['strength'] = '强'
            result['confidence'] = 0.85
        else:
            result['strength'] = '中'
            result['confidence'] = 0.7
        
        result['detected'] = True
        result['reason'] = f'上升趋势中回调{pullback_ratio:.2%}后放量启动,量比{volume_ratio}'
        
        return result
    
    @staticmethod
    def detect_continuous_keypoint(
        current_price: float,
        resistance_level: float,
        volume_ratio: float,
        has_profit: bool = True,
        price_increase: float = 0
    ) -> Dict:
        """
        检测连续关键点(金字塔加仓点)
        
        :param current_price: 当前价格
        :param resistance_level: 整理区间上沿
        :param volume_ratio: 量比
        :param has_profit: 是否已有盈利
        :param price_increase: 涨幅(%)
        :return: 检测结果
        """
        result = {
            'detected': False,
            'type': '连续关键点',
            'strength': '',
            'confidence': 0.0,
            'reason': ''
        }
        
        # 必须在盈利状态下
        if not has_profit:
            result['reason'] = '当前持仓未盈利,不符合加仓条件'
            return result
        
        # 检查涨幅(每上涨5%可考虑加仓)
        if price_increase < 5:
            result['reason'] = f'涨幅{price_increase:.2%}不足5%'
            return result
        
        # 检查是否突破整理区间
        breakout = current_price >= resistance_level * 1.01
        
        if not breakout:
            result['reason'] = '未突破整理区间'
            return result
        
        # 检查成交量
        if volume_ratio < 1.5:
            result['reason'] = '成交量不足'
            return result
        
        # 判断强度
        if volume_ratio > 2.0 and price_increase >= 10:
            result['strength'] = '强'
            result['confidence'] = 0.8
        else:
            result['strength'] = '中'
            result['confidence'] = 0.65
        
        result['detected'] = True
        result['reason'] = f'趋势延续,涨幅{price_increase:.2%},放量突破整理区间'
        
        return result
    
    @staticmethod
    def detect_reversal_keypoint(
        current_price: float,
        previous_high: float,
        volume_ratio: float,
        support_level: float = 0,
        price_action: str = ''
    ) -> Dict:
        """
        检测反转关键点(离场信号)
        
        :param current_price: 当前价格
        :param previous_high: 前期高点
        :param volume_ratio: 量比
        :param support_level: 支撑位
        :param price_action: 价格行为('无法突破'/'跌破支撑')
        :return: 检测结果
        """
        result = {
            'detected': False,
            'type': '反转关键点',
            'strength': '',
            'confidence': 0.0,
            'reason': ''
        }
        
        # 情况1: 前高附近放量但无法突破
        if price_action == '无法突破':
            near_high = abs(current_price - previous_high) / previous_high < 0.02
            
            if near_high and volume_ratio > 1.5:
                result['detected'] = True
                result['strength'] = '强'
                result['confidence'] = 0.85
                result['reason'] = f'前高{previous_high}附近放量但无法突破,危险信号'
                return result
        
        # 情况2: 跌破重要支撑
        if price_action == '跌破支撑' and support_level > 0:
            if current_price < support_level * 0.98:
                result['detected'] = True
                result['strength'] = '强'
                result['confidence'] = 0.9
                result['reason'] = f'跌破重要支撑位{support_level},强烈离场信号'
                return result
        
        result['reason'] = '未检测到反转信号'
        return result
    
    @staticmethod
    def calculate_keypoint_strength(
        volume_ratio: float,
        market_trend: str = 'up',
        sector_sync: bool = False,
        consolidation_days: int = 0
    ) -> Dict:
        """
        计算关键点信号强度
        
        :param volume_ratio: 量比
        :param market_trend: 大盘趋势
        :param sector_sync: 板块是否同步
        :param consolidation_days: 盘整天数
        :return: {'strength': str, 'score': int}
        """
        score = 0
        
        # 大盘趋势(40分)
        if market_trend == 'up':
            score += 40
        elif market_trend == 'neutral':
            score += 20
        
        # 成交量(30分)
        if volume_ratio > 2.0:
            score += 30
        elif volume_ratio > 1.5:
            score += 20
        elif volume_ratio > 1.0:
            score += 10
        
        # 板块同步(20分)
        if sector_sync:
            score += 20
        
        # 盘整时间(10分)
        if consolidation_days > 20:
            score += 10
        elif consolidation_days > 10:
            score += 5
        
        # 强度评级
        if score >= 80:
            strength = '强'
        elif score >= 60:
            strength = '中'
        else:
            strength = '弱'
        
        return {
            'strength': strength,
            'score': score,
            'recommendation': '可入场' if score >= 60 else '观望'
        }
    
    @staticmethod
    def validate_keypoint_entry(
        market_trend: str,
        keypoint_detected: bool,
        volume_ratio: float,
        stand_days: int = 0,
        sector_sync: bool = False,
        stop_loss_set: bool = False,
        risk_ok: bool = False
    ) -> Dict:
        """
        验证关键点入场条件(检查清单)
        
        :param market_trend: 大盘趋势
        :param keypoint_detected: 是否检测到关键点
        :param volume_ratio: 量比
        :param stand_days: 突破后站稳天数
        :param sector_sync: 板块同步
        :param stop_loss_set: 是否设定止损
        :param risk_ok: 风险是否可控
        :return: {'allowed': bool, 'checklist': dict, 'reason': str}
        """
        checklist = {
            '大盘趋势向上': market_trend in ['up', '牛市'],
            '关键点信号': keypoint_detected,
            '成交量放大': volume_ratio >= 1.5,
            '站稳3天': stand_days >= 3,
            '板块同步': sector_sync,
            '止损设定': stop_loss_set,
            '风险可控': risk_ok
        }
        
        # 统计通过项
        passed = sum(1 for v in checklist.values() if v)
        total = len(checklist)
        
        # 前两项必须满足
        if not checklist['大盘趋势向上'] or not checklist['关键点信号']:
            return {
                'allowed': False,
                'checklist': checklist,
                'reason': '大盘趋势或关键点信号不满足',
                'passed': f'{passed}/{total}'
            }
        
        # 至少5项满足
        if passed >= 5:
            return {
                'allowed': True,
                'checklist': checklist,
                'reason': '满足入场条件',
                'passed': f'{passed}/{total}'
            }
        
        return {
            'allowed': False,
            'checklist': checklist,
            'reason': f'仅通过{passed}/{total}项,建议观望',
            'passed': f'{passed}/{total}'
        }
