import structlog
from .celery_app import celery_app

logger = structlog.get_logger()

@celery_app.task(name="demo.add", bind=True)
def add(self, x, y):
    logger.info("task.start", task=self.name, x=x, y=y)
    result = x + y
    logger.info("task.done", task=self.name, result=result)
    return result

@celery_app.task(name="demo.ping", bind=True)
def ping(self):
    logger.info("task.ping", task=self.name, status="ok")
    return "pong"
