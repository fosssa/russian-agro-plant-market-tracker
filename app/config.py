class CeleryConfig:
    broker_url = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'

    timezone = 'UTC'
    enable_utc = True

    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    task_ignore_result = False
    worker_send_task_events = True

    # Ensure tasks are registered on worker start
    imports = ('app.tasks',)

    # RedBeat / Beat
    beat_scheduler = 'redbeat.RedBeatScheduler'
    redbeat_redis_url = 'redis://redis:6379/1'
