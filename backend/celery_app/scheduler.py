"""RedBeat scheduler utilities for dynamic task scheduling.

This module provides helper functions for managing periodic task schedules
stored in Redis via RedBeat.
"""
import structlog
from celery.schedules import schedule as interval
from redbeat.schedulers import RedBeatSchedulerEntry
from .celery_app import celery_app, _configure_structlog

# Ensure logging is initialized when running as a plain Python module
_configure_structlog()

logger = structlog.get_logger()


def upsert_entry(
    name: str,
    task: str,
    seconds: int,
    args: tuple = (),
    kwargs: dict | None = None
) -> None:
    """Create or update a RedBeat schedule entry.
    
    Args:
        name: Unique name for the schedule entry
        task: Task name to execute (must match @celery_app.task name)
        seconds: Interval in seconds between executions
        args: Positional arguments to pass to the task
        kwargs: Keyword arguments to pass to the task
    """
    entry = RedBeatSchedulerEntry(
        name=name,
        task=task,
        schedule=interval(run_every=seconds),
        args=args,
        kwargs=kwargs or {},
        app=celery_app,
    )
    entry.save()
    logger.info(
        "redbeat.entry_saved",
        name=name,
        task=task,
        every_seconds=seconds,
        args=args
    )


def update_schedule_interval(name: str, seconds: int) -> None:
    """Update the interval of an existing schedule entry.
    
    Args:
        name: Name of the existing schedule entry
        seconds: New interval in seconds
        
    Raises:
        KeyError: If the schedule entry doesn't exist
    """
    key = f'redbeat:{name}'
    entry = RedBeatSchedulerEntry.from_key(key, app=celery_app)
    entry.schedule = interval(run_every=seconds)
    entry.save()
    logger.info("redbeat.entry_updated", name=name, every_seconds=seconds)


def delete_entry(name: str) -> None:
    """Delete a RedBeat schedule entry.
    
    Args:
        name: Name of the schedule entry to delete
    """
    key = f'redbeat:{name}'
    entry = RedBeatSchedulerEntry.from_key(key, app=celery_app)
    entry.delete()
    logger.info("redbeat.entry_deleted", name=name)


def list_entries() -> list[dict]:
    """List all RedBeat schedule entries.
    
    Returns:
        List of schedule entry dictionaries with name, task, and schedule info
    """
    from redis import Redis
    from .config import CeleryConfig
    
    # Connect to RedBeat's Redis DB
    redis_url = CeleryConfig.redbeat_redis_url
    client = Redis.from_url(redis_url)
    
    entries = []
    # RedBeat stores entries with prefix 'redbeat:'
    for key in client.scan_iter(match='redbeat:*'):
        key_str = key.decode() if isinstance(key, bytes) else key
        if key_str.endswith(':lock') or key_str == 'redbeat::statics':
            continue
        try:
            entry = RedBeatSchedulerEntry.from_key(key_str, app=celery_app)
            entries.append({
                'name': entry.name,
                'task': entry.task,
                'schedule': str(entry.schedule),
                'args': entry.args,
                'kwargs': entry.kwargs,
            })
        except Exception:
            continue
    return entries
