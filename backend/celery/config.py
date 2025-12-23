import os


class CeleryConfig:
    """Celery configuration with RedBeat scheduler."""
    
    # Redis connection settings
    redis_host = os.getenv('REDIS_HOST', 'redis')
    redis_port = os.getenv('REDIS_PORT', '6379')
    
    broker_url = f'redis://{redis_host}:{redis_port}/0'
    result_backend = f'redis://{redis_host}:{redis_port}/0'

    timezone = 'UTC'
    enable_utc = True

    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    task_ignore_result = False
    worker_send_task_events = True

    # Ensure tasks are registered on worker start
    imports = ('celery.tasks',)

    # RedBeat / Beat scheduler configuration
    beat_scheduler = 'redbeat.RedBeatScheduler'
    redbeat_redis_url = f'redis://{redis_host}:{redis_port}/1'
