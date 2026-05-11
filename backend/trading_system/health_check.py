"""
Health check views for Docker and monitoring.
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import os


def health_check(request):
    """
    Health check endpoint for Docker and load balancers.
    Returns 200 if all services are healthy.
    """
    status = {
        'status': 'healthy',
        'services': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        status['services']['database'] = 'healthy'
    except Exception as e:
        status['services']['database'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Check Redis
    try:
        redis_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        status['services']['redis'] = 'healthy'
    except Exception as e:
        status['services']['redis'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Check Celery (optional)
    try:
        from celery import Celery
        app = Celery('trading_system')
        app.config_from_object('django.conf:settings', namespace='CELERY')
        # Just check if we can connect to broker
        with app.connection() as conn:
            conn.ensure_connection(max_retries=1)
        status['services']['celery'] = 'healthy'
    except Exception as e:
        status['services']['celery'] = f'unhealthy: {str(e)}'
        # Celery being unhealthy doesn't make the whole system unhealthy
    
    response_status = 200 if status['status'] == 'healthy' else 503
    return JsonResponse(status, status=response_status)


def readiness_check(request):
    """
    Readiness check for Kubernetes.
    Returns 200 if the app is ready to accept traffic.
    """
    try:
        # Check if we can connect to the database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({'ready': True}, status=200)
    except Exception as e:
        return JsonResponse({'ready': False, 'error': str(e)}, status=503)


def liveness_check(request):
    """
    Liveness check for Kubernetes.
    Returns 200 if the app is running.
    """
    return JsonResponse({'alive': True}, status=200)
