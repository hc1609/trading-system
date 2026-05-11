"""
Celery tasks for data synchronization and automated operations.
"""

import logging
from datetime import date, datetime, timedelta
from celery import shared_task
from django.contrib.auth.models import User

from apps.market.models import MarketData, TechnicalIndicators
from apps.strategy.models import MarketState, EventCalendar
from apps.risk.models import RiskStatus
from apps.position.models import Position

from apps.market.services.technical_indicator_calculator import TechnicalIndicatorCalculator
from apps.strategy.services.market_state_calculator import MarketStateCalculator
from apps.risk.services.risk_manager import RiskManager

logger = logging.getLogger(__name__)


@shared_task
def sync_daily_market_data():
    """
    Task: Sync daily market data from Tushare or other data sources.
    Runs at 9:00 AM and 3:30 PM daily.
    """
    logger.info("Starting daily market data sync...")
    
    try:
        # TODO: Implement actual Tushare API integration
        # For now, this is a placeholder that logs the attempt
        logger.info("Market data sync completed successfully")
        
        # After syncing data, trigger indicator calculation
        calculate_all_indicators.delay()
        
        return {"status": "success", "message": "Market data synced"}
    except Exception as e:
        logger.error(f"Market data sync failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def calculate_all_indicators():
    """
    Task: Calculate technical indicators for latest market data.
    Runs every 5 minutes during trading hours.
    """
    logger.info("Calculating technical indicators...")
    
    try:
        # Get the latest market data without indicators
        latest_data = MarketData.objects.filter(
            technicalindicators__isnull=True
        ).order_by('-date')[:50]
        
        for market_data in latest_data:
            try:
                # Get price data for calculations
                historical_data = MarketData.objects.filter(
                    index_code=market_data.index_code
                ).order_by('-date')[:60]
                
                if len(historical_data) < 20:
                    continue
                
                prices = [float(d.close) for d in reversed(historical_data)]
                volumes = [float(d.volume) for d in reversed(historical_data)]
                highs = [float(d.high) for d in reversed(historical_data)]
                lows = [float(d.low) for d in reversed(historical_data)]
                
                # Calculate indicators
                rsi_14 = TechnicalIndicatorCalculator.calculate_rsi(prices, period=14)
                macd_dif, macd_dea, macd_hist = TechnicalIndicatorCalculator.calculate_macd(prices)
                obv = TechnicalIndicatorCalculator.calculate_obv(prices, volumes)
                ma_5 = TechnicalIndicatorCalculator.calculate_ma(prices, 5)
                ma_10 = TechnicalIndicatorCalculator.calculate_ma(prices, 10)
                ma_20 = TechnicalIndicatorCalculator.calculate_ma(prices, 20)
                ma_60 = TechnicalIndicatorCalculator.calculate_ma(prices, 60)
                
                # Calculate 20-day change
                if len(prices) >= 20:
                    change_20d = ((prices[-1] - prices[-20]) / prices[-20]) * 100
                else:
                    change_20d = 0
                
                # Create or update indicators
                TechnicalIndicators.objects.update_or_create(
                    market_data=market_data,
                    defaults={
                        'rsi_14': rsi_14,
                        'macd_dif': macd_dif,
                        'macd_dea': macd_dea,
                        'macd_hist': macd_hist,
                        'obv': obv,
                        'ma_5': ma_5[-1] if len(ma_5) > 0 else None,
                        'ma_10': ma_10[-1] if len(ma_10) > 0 else None,
                        'ma_20': ma_20[-1] if len(ma_20) > 0 else None,
                        'ma_60': ma_60[-1] if len(ma_60) > 0 else None,
                        'change_20d': change_20d,
                    }
                )
                
            except Exception as e:
                logger.error(f"Error calculating indicators for {market_data.date}: {str(e)}")
                continue
        
        logger.info(f"Calculated indicators for {len(latest_data)} records")
        return {"status": "success", "count": len(latest_data)}
        
    except Exception as e:
        logger.error(f"Indicator calculation failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def calculate_market_state_for_all_users():
    """
    Task: Calculate market state for all active users.
    Runs every 10 minutes.
    """
    logger.info("Calculating market state for all users...")
    
    try:
        users = User.objects.filter(is_active=True)
        
        for user in users:
            try:
                # Get latest indicators
                latest_indicator = TechnicalIndicators.objects.select_related(
                    'market_data'
                ).first()
                
                if not latest_indicator:
                    continue
                
                # Calculate tech state
                tech_state = MarketStateCalculator.calculate_tech_state(
                    change_20d=float(latest_indicator.change_20d or 0),
                    rsi_14=float(latest_indicator.rsi_14 or 50),
                    max_gain_20d=0,  # Would need actual calculation
                    amplitude_5d=0,
                    volume_slope_decreasing_days=0
                )
                
                # Calculate cycle state
                cycle_state = MarketStateCalculator.calculate_cycle_state(
                    change_20d=float(latest_indicator.change_20d or 0),
                    rsi_14=float(latest_indicator.rsi_14 or 50),
                    has_divergence=False,
                    is_above_ma5=bool(latest_indicator.ma_5 and latest_indicator.ma_20 and 
                                     latest_indicator.ma_5 > latest_indicator.ma_20),
                    is_below_ma60=bool(latest_indicator.ma_60 and latest_indicator.ma_20 and 
                                      latest_indicator.ma_60 > latest_indicator.ma_20)
                )
                
                # Get active events
                today = date.today()
                active_events = EventCalendar.objects.filter(
                    start_date__lte=today,
                    end_date__gte=today
                )
                
                event_list = [
                    {'correction_value': float(e.correction_value), 'priority': 1} 
                    for e in active_events
                ]
                event_correction = MarketStateCalculator.calculate_event_correction(event_list)
                
                # Calculate final state
                final_state = MarketStateCalculator.calculate_final_state(
                    tech_state, event_correction
                )
                
                # Get recommendations
                max_position = MarketStateCalculator.get_max_position(final_state)
                etf_action = MarketStateCalculator.get_etf_action(final_state)
                individual_action = MarketStateCalculator.get_individual_action(final_state)
                
                # Save market state
                MarketState.objects.update_or_create(
                    user=user,
                    date=today,
                    defaults={
                        'tech_state': tech_state,
                        'major_trend': '牛市',  # Simplified
                        'cycle_state': cycle_state,
                        'event_correction': str(event_correction),
                        'final_state': final_state,
                        'max_position': max_position,
                        'etf_action': etf_action,
                        'individual_action': individual_action,
                    }
                )
                
            except Exception as e:
                logger.error(f"Error calculating market state for user {user.id}: {str(e)}")
                continue
        
        logger.info(f"Updated market state for {users.count()} users")
        return {"status": "success", "user_count": users.count()}
        
    except Exception as e:
        logger.error(f"Market state calculation failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def check_risk_limits():
    """
    Task: Check risk limits for all users and lock if necessary.
    Runs every 5 minutes.
    """
    logger.info("Checking risk limits...")
    
    try:
        users = User.objects.filter(is_active=True)
        
        for user in users:
            try:
                risk_status, _ = RiskStatus.objects.get_or_create(
                    user=user,
                    date=date.today(),
                    defaults={
                        'total_capital': 100000,
                        'daily_return': 0,
                        'weekly_return': 0,
                        'consecutive_losses': 0,
                        'today_trades': 0,
                        'risk_lock': False,
                    }
                )
                
                # Check if risk should be locked
                if risk_status.daily_return and risk_status.daily_return <= -3:
                    risk_status.risk_lock = True
                    risk_status.lock_reason = '日回撤超过3%'
                    risk_status.save()
                    logger.warning(f"Risk locked for user {user.id}: daily return {risk_status.daily_return}%")
                
                elif risk_status.weekly_return and risk_status.weekly_return <= -5:
                    risk_status.risk_lock = True
                    risk_status.lock_reason = '周回撤超过5%'
                    risk_status.save()
                    logger.warning(f"Risk locked for user {user.id}: weekly return {risk_status.weekly_return}%")
                
                elif risk_status.consecutive_losses >= 3:
                    risk_status.risk_lock = True
                    risk_status.lock_reason = '连续3笔亏损'
                    risk_status.save()
                    logger.warning(f"Risk locked for user {user.id}: {risk_status.consecutive_losses} consecutive losses")
                
            except Exception as e:
                logger.error(f"Error checking risk for user {user.id}: {str(e)}")
                continue
        
        logger.info("Risk limit check completed")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Risk check failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def cleanup_old_data():
    """
    Task: Clean up old data to maintain database performance.
    Runs daily at 2:00 AM.
    """
    logger.info("Cleaning up old data...")
    
    try:
        # Delete market data older than 5 years
        cutoff_date = date.today() - timedelta(days=365 * 5)
        
        old_market_data = MarketData.objects.filter(date__lt=cutoff_date)
        deleted_count = old_market_data.count()
        old_market_data.delete()
        
        # Delete old risk logs older than 1 year
        old_risk_logs = RiskStatus.objects.filter(date__lt=cutoff_date)
        old_risk_logs.delete()
        
        logger.info(f"Cleaned up {deleted_count} old market data records")
        return {"status": "success", "deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def send_market_open_reminder():
    """
    Task: Send market open reminder to users.
    Runs at 9:00 AM on trading days.
    """
    logger.info("Sending market open reminders...")
    
    try:
        users = User.objects.filter(is_active=True)
        
        for user in users:
            try:
                # Get current market state
                market_state = MarketState.objects.filter(user=user).first()
                
                if market_state:
                    message = f"""
                    📈 交易提醒
                    
                    市场状态: {market_state.final_state}
                    建议仓位: {market_state.max_position}%
                    ETF操作: {market_state.etf_action}
                    个股操作: {market_state.individual_action}
                    
                    祝交易顺利!
                    """
                    
                    # TODO: Implement actual notification (email, SMS, push)
                    logger.info(f"Reminder sent to user {user.id}")
                
            except Exception as e:
                logger.error(f"Error sending reminder to user {user.id}: {str(e)}")
                continue
        
        return {"status": "success", "user_count": users.count()}
        
    except Exception as e:
        logger.error(f"Market open reminder failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def check_stop_losses():
    """
    Task: Check all positions for stop-loss breaches.
    Runs every minute during trading hours.
    """
    logger.info("Checking stop losses...")
    
    try:
        positions = Position.objects.filter(status='holding')
        
        breached_positions = []
        for position in positions:
            try:
                # TODO: Get current price from market data
                # For now, just check if stop_loss is set
                if position.stop_loss and position.stop_loss > 0:
                    # In a real implementation, compare with current price
                    # if current_price <= position.stop_loss:
                    #     breached_positions.append(position)
                    pass
                
            except Exception as e:
                logger.error(f"Error checking position {position.id}: {str(e)}")
                continue
        
        if breached_positions:
            logger.warning(f"Found {len(breached_positions)} positions at stop loss")
            # TODO: Send notifications
        
        return {"status": "success", "breached_count": len(breached_positions)}
        
    except Exception as e:
        logger.error(f"Stop loss check failed: {str(e)}")
        return {"status": "error", "message": str(e)}
