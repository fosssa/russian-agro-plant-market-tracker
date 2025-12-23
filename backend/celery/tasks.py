"""Celery tasks for the agro backend.

This module contains task definitions for periodic data collection
and processing operations.
"""
import structlog
from .celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="demo.add", bind=True)
def add(self, x: int, y: int) -> int:
    """Demo task: adds two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
    """
    logger.info("task.start", task=self.name, args=(x, y))
    result = x + y
    logger.info("task.done", task=self.name, result=result)
    return result


@celery_app.task(name="demo.ping", bind=True)
def ping(self) -> str:
    """Demo task: health check ping.
    
    Returns:
        'pong' string
    """
    logger.info("task.ping", task=self.name, status="ok")
    return "pong"
