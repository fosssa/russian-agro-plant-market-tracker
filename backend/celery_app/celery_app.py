import logging
import logging.config
import structlog
from celery import Celery
from celery.signals import setup_logging
from .config import CeleryConfig


def _configure_structlog():
    """Configure structlog for human-readable Celery task logging."""
    
    def human_readable_processor(logger, method_name, event_dict):
        timestamp = event_dict.get('timestamp', '')
        level = event_dict.get('level', '').upper()
        message = event_dict.get('message', event_dict.get('event', ''))
        
        # Extract task info if present
        task = event_dict.get('task', '')
        if task:
            args = event_dict.get('args', '')
            result = event_dict.get('result', '')
            
            if message == 'task.start':
                return f"[{timestamp}] STARTED: Task {task} with args {args}"
            elif result and message == 'task.done':
                return f"[{timestamp}] FINISHED: Task {task} with result: {result}"
        
        return f"[{timestamp}] {level}: {message}"

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.add_log_level,
            human_readable_processor,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    class TaskOnlyFilter(logging.Filter):
        def filter(self, record):
            return True

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(message)s',
            },
        },
        'filters': {
            'task_only': {
                '()': TaskOnlyFilter,
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'INFO',
                'filters': ['task_only'],
            },
        },
        'loggers': {
            'celery': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery.task': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery.worker': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery.beat': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['default'],
            'level': 'INFO',
        },
    })


@setup_logging.connect
def setup_celery_logging(**kwargs):
    """Signal handler to configure logging when Celery starts."""
    _configure_structlog()


# Create Celery application instance
celery_app = Celery("agro-backend")
celery_app.config_from_object(CeleryConfig)
