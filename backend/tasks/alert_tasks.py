"""
Alert-related background tasks.
Wired to alert_service for rule evaluation, generation and cleanup.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

from .celery_app import celery_app

logger = logging.getLogger(__name__)

ALL_PORTS = [
    "urn:ngsi-ld:Port:galicia-a-coruna",
    "urn:ngsi-ld:Port:galicia-vigo",
    "urn:ngsi-ld:Port:galicia-marin",
    "urn:ngsi-ld:Port:galicia-ferrol",
    "urn:ngsi-ld:Port:galicia-vilagarcia",
    "urn:ngsi-ld:Port:galicia-ribeira",
    "urn:ngsi-ld:Port:galicia-celeiro",
    "urn:ngsi-ld:Port:galicia-burela",
]


def _run_async(coro):
    """Execute an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(bind=True, name="tasks.analyze_port_conditions")
def analyze_port_conditions(self, port_id: str) -> Dict[str, Any]:
    """Full alert sweep for a single port: auth, occupancy, conflicts, weather, ETA."""
    logger.info(f"[Task] Analyzing port conditions: {port_id}")
    try:
        from services.alert_service import alert_service
        alerts = _run_async(alert_service.check_port_alerts(
            port_id,
            check_authorizations=True,
            check_occupancy=True,
            check_conflicts=True,
            check_weather=True,
            check_eta=True,
        ))
        logger.info(f"[Task] {port_id}: {len(alerts)} alerts generated")
        return {
            "status": "success",
            "port_id": port_id,
            "alerts_generated": len(alerts),
            "alert_ids": [a.id for a in alerts],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error analyzing port conditions for {port_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.check_all_ports_alerts")
def check_all_ports_alerts(self) -> Dict[str, Any]:
    """Periodic sweep across all Galician ports."""
    logger.info("[Task] Sweeping alerts for all ports")
    results = {}
    for port_id in ALL_PORTS:
        try:
            from services.alert_service import alert_service
            alerts = _run_async(alert_service.check_port_alerts(port_id))
            results[port_id] = len(alerts)
        except Exception as e:
            logger.error(f"Alert sweep failed for {port_id}: {e}")
            results[port_id] = -1
    total = sum(v for v in results.values() if v >= 0)
    logger.info(f"[Task] Alert sweep complete: {total} alerts across {len(ALL_PORTS)} ports")
    return {
        "status": "success",
        "total_alerts": total,
        "by_port": results,
        "timestamp": datetime.utcnow().isoformat(),
    }


@celery_app.task(bind=True, name="tasks.check_vessel_authorization_issues")
def check_vessel_authorization_issues(self, port_id: str) -> Dict[str, Any]:
    """Check vessel authorization issues for a port."""
    logger.info(f"[Task] Checking vessel authorization issues for port: {port_id}")
    try:
        from services.alert_service import alert_service
        alerts = _run_async(alert_service.check_port_alerts(
            port_id,
            check_authorizations=True,
            check_occupancy=False,
            check_conflicts=False,
            check_weather=False,
            check_eta=False,
        ))
        return {
            "status": "success",
            "port_id": port_id,
            "issues_found": len(alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error checking vessel authorizations for {port_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.check_berth_utilization")
def check_berth_utilization(self, port_id: str) -> Dict[str, Any]:
    """Check berth occupancy and generate alerts."""
    logger.info(f"[Task] Checking berth utilization: {port_id}")
    try:
        from services.alert_service import alert_service
        alerts = _run_async(alert_service.check_port_alerts(
            port_id,
            check_authorizations=False,
            check_occupancy=True,
            check_conflicts=True,
            check_weather=False,
            check_eta=False,
        ))
        return {
            "status": "success",
            "port_id": port_id,
            "alerts_generated": len(alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error checking berth utilization for {port_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.check_weather_alerts")
def check_weather_alerts(self, port_id: str) -> Dict[str, Any]:
    """Check weather conditions and generate alerts."""
    logger.info(f"[Task] Checking weather alerts: {port_id}")
    try:
        from services.alert_service import alert_service
        alerts = _run_async(alert_service.check_port_alerts(
            port_id,
            check_authorizations=False,
            check_occupancy=False,
            check_conflicts=False,
            check_weather=True,
            check_eta=False,
        ))
        return {
            "status": "success",
            "port_id": port_id,
            "alerts_generated": len(alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error checking weather alerts for {port_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.generate_operational_report")
def generate_operational_report(self, port_id: str, period_hours: int = 24) -> Dict[str, Any]:
    """Generate an operational alert summary for a port."""
    logger.info(f"[Task] Generating operational report for {port_id} (last {period_hours}h)")
    try:
        from services.alert_service import alert_service
        alerts, total = _run_async(alert_service.get_port_alerts(
            port_id, active_only=False, limit=1000
        ))
        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        for a in alerts:
            by_type[a.alert_type.value] = by_type.get(a.alert_type.value, 0) + 1
            by_severity[a.severity.value] = by_severity.get(a.severity.value, 0) + 1

        return {
            "status": "success",
            "port_id": port_id,
            "period_hours": period_hours,
            "total_alerts": total,
            "active_alerts": sum(1 for a in alerts if a.is_active),
            "by_type": by_type,
            "by_severity": by_severity,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error generating operational report for {port_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.cleanup_expired_alerts")
def cleanup_expired_alerts(self) -> Dict[str, Any]:
    """Resolve alerts older than 24 h that are still marked active."""
    logger.info("[Task] Cleaning up expired alerts")
    try:
        from services.alert_service import alert_service
        from services.orion_ld_client import orion_client

        alerts, total = _run_async(alert_service.get_all_alerts(active_only=True, limit=1000))
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        cleaned = 0
        for alert in alerts:
            try:
                created = alert.created_at
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created < cutoff:
                    _run_async(alert_service.resolve_alert(alert.id))
                    cleaned += 1
            except Exception as inner_e:
                logger.warning(f"Could not resolve alert {alert.id}: {inner_e}")

        logger.info(f"[Task] Cleaned up {cleaned} expired alerts")
        return {
            "status": "success",
            "alerts_cleaned": cleaned,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error cleaning up alerts: {e}")
        raise
