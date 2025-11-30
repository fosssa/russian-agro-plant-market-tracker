import time
import structlog
from celery.schedules import schedule as interval
from redbeat.schedulers import RedBeatSchedulerEntry
from .celery_app import celery_app, _configure_structlog

# Ensure logging is initialized when running as a plain Python module (non-Celery context)
_configure_structlog()

logger = structlog.get_logger()

def upsert_entry(name: str, task: str, seconds: int, args=(), kwargs=None):
    e = RedBeatSchedulerEntry(
        name=name,
        task=task,
        schedule=interval(run_every=seconds),
        args=args,
        kwargs=kwargs or {},
        app=celery_app,
    )
    e.save()
    logger.info("redbeat.entry_saved", name=name, task=task, every_seconds=seconds, args=args)

def update_schedule_only(name: str, seconds: int):
    key = f'redbeat:{name}'
    entry = RedBeatSchedulerEntry.from_key(key, app=celery_app)  # load existing
    entry.schedule = interval(run_every=seconds)
    entry.save()
    logger.info("redbeat.entry_updated", name=name, every_seconds=seconds)

if __name__ == "__main__":
    upsert_entry("demo-add", "demo.add", 30, args=(2, 3))
    logger.info("app.sleeping_before_update", seconds=60)
    time.sleep(120)
    update_schedule_only("demo-add", 10)
    logger.info("app.idle")
    while True:
        time.sleep(3600)
