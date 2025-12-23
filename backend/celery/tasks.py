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


@celery_app.task(name="data.collect_for_source", bind=True)
def collect_data_for_source(self, source_id: int) -> dict:
    """Task to collect data from a specific source.
    
    This is a stub implementation that simulates data collection.
    In a real implementation, this would call the appropriate parser
    based on the source configuration.
    
    Args:
        source_id: ID of the data source to collect from
        
    Returns:
        Dictionary with collection results
    """
    logger.info("task.collect_data.start", task=self.name, source_id=source_id)
    
    # TODO: Implement actual data collection logic
    # For now, this is a stub that simulates successful collection
    import time
    time.sleep(2)  # Simulate work
    
    result = {
        "source_id": source_id,
        "status": "success",
        "records_collected": 0,  # Placeholder
        "message": "Data collection completed (stub implementation)"
    }
    
    logger.info("task.collect_data.done", task=self.name, **result)
    return result
