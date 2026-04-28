"""
Celery task definitions and configuration.
Background jobs for non-critical or expensive operations.
"""

import logging
from celery import Celery, Task
from celery.result import AsyncResult
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SmartPortTask(Task):
    """Base task class with custom error handling."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {self.name} retrying after error: {exc}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} failed permanently: {exc}")


def make_celery(
    broker_url: str = "redis://localhost:6379/1",
    result_backend: str = "redis://localhost:6379/2",
    app_name: str = "smartports",
) -> Celery:
    """Create and configure a Celery application."""
    
    celery_app = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend,
    )
    
    # Configuration
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # Hard time limit: 30 minutes
        task_soft_time_limit=25 * 60,  # Soft time limit: 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    
    # Set the base task class
    celery_app.Task = SmartPortTask
    
    logger.info(f"Celery app configured: {app_name}")
    logger.info(f"  Broker: {broker_url}")
    logger.info(f"  Backend: {result_backend}")
    
    return celery_app


# This will be initialized in main.py
celery_app: Optional[Celery] = None


def get_celery() -> Optional[Celery]:
    """Get the global Celery app instance."""
    return celery_app


def set_celery(app: Celery) -> None:
    """Set the global Celery app instance."""
    global celery_app
    celery_app = app


def get_task_result(task_id: str) -> Dict[str, Any]:
    """Get the result of a task by ID."""
    if not celery_app:
        return {"status": "unknown", "error": "Celery not initialized"}
    
    try:
        result = AsyncResult(task_id, app=celery_app)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
        }
    except Exception as e:
        logger.error(f"Error getting task result for {task_id}: {e}")
        return {"status": "error", "error": str(e)}
