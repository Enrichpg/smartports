"""
Celery tasks package - Import all task modules
"""

# Import all task modules to register them with Celery
from . import ingest_tasks  # noqa: F401
from . import domain_tasks  # noqa: F401
from . import cache_tasks  # noqa: F401
from . import alert_tasks  # noqa: F401
from . import realtime_events_task  # noqa: F401
