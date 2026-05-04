"""
Realtime Events Task - Generates and broadcasts simulated/real port events.
Runs periodically via Celery to emit berth updates, vessel movements, sensor readings, etc.

This task:
- Polls Orion-LD for recent changes
- Generates simulated sensor readings
- Emits WebSocket events to connected clients
- Is designed to be non-blocking and graceful on errors
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Optional

from celery import shared_task
from realtime.ws_manager import get_manager
from realtime.models import RealtimeEvent, EventScope, EntityReference

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='smartport.broadcast_occupancy_update')
def broadcast_occupancy_update(self, port_id: str = "galicia-a-coruna"):
    """
    Emit occupancy update event for a port.
    
    Simulates: berth occupancy changes, trending analysis
    """
    import asyncio
    
    async def emit():
        try:
            # Simulate occupancy data
            total_berths = 15
            occupied = random.randint(5, 12)
            reserved = random.randint(1, 3)
            free = total_berths - occupied - reserved
            occupancy_pct = (occupied / total_berths) * 100
            
            # Trending logic (simple)
            prev_occ = random.uniform(60, 85)
            if occupancy_pct > prev_occ:
                trending = "increasing"
            elif occupancy_pct < prev_occ:
                trending = "decreasing"
            else:
                trending = "stable"
            
            event = RealtimeEvent(
                event="occupancy.changed",
                scope=EventScope(port_id=port_id),
                entity=EntityReference(type="Port", id=f"urn:ngsi-ld:Port:{port_id}"),
                payload={
                    "total_berths": total_berths,
                    "occupied_berths": occupied,
                    "reserved_berths": reserved,
                    "free_berths": free,
                    "occupancy_percentage": round(occupancy_pct, 1),
                    "trending": trending,
                },
                source="simulator",
                severity="info"
            )
            
            manager = get_manager()
            sent, failed = await manager.broadcast_event(event)
            logger.info(f"[TASK] Occupancy update for {port_id}: sent={sent}, failed={failed}")
        
        except Exception as e:
            logger.error(f"[TASK] Error broadcasting occupancy: {type(e).__name__}: {e}")
    
    # Run async task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(emit())
    finally:
        loop.close()


@shared_task(bind=True, name='smartport.broadcast_berth_update')
def broadcast_berth_update(self, port_id: str = "galicia-a-coruna", berth_index: int = 0):
    """
    Emit berth status update event.
    
    Simulates: berth state transitions (free -> reserved -> occupied -> free)
    """
    import asyncio
    
    async def emit():
        try:
            statuses = ["free", "reserved", "occupied", "free"]
            status = random.choice(statuses)
            
            berth_id = f"urn:ngsi-ld:Berth:{port_id}:berth-{berth_index:03d}"
            
            payload = {
                "berth_id": berth_id,
                "status": status,
                "previous_status": random.choice(statuses),
                "occupancy_percentage": 100 if status == "occupied" else 0,
            }
            
            # Add vessel info if occupied
            if status == "occupied":
                payload.update({
                    "vessel_id": "urn:ngsi-ld:Vessel:IMO-1234567",
                    "vessel_name": f"Vessel-{random.randint(1000, 9999)}",
                    "arrival_time": datetime.utcnow().isoformat() + "Z",
                    "estimated_departure": (datetime.utcnow() + timedelta(hours=6)).isoformat() + "Z",
                    "operations": ["loading"],
                })
            
            event = RealtimeEvent(
                event="berth.updated",
                scope=EventScope(port_id=port_id, berth_id=berth_id),
                entity=EntityReference(type="Berth", id=berth_id),
                payload=payload,
                source="simulator",
                severity="info"
            )
            
            manager = get_manager()
            sent, failed = await manager.broadcast_event(event)
            logger.info(f"[TASK] Berth update {berth_id}: status={status}, sent={sent}")
        
        except Exception as e:
            logger.error(f"[TASK] Error broadcasting berth update: {type(e).__name__}: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(emit())
    finally:
        loop.close()


@shared_task(bind=True, name='smartport.broadcast_sensor_reading')
def broadcast_sensor_reading(
    self,
    sensor_type: str = "temperature",
    port_id: str = "galicia-a-coruna"
):
    """
    Emit sensor reading event (weather, air quality, etc).
    
    Simulates: continuous sensor data updates
    """
    import asyncio
    
    async def emit():
        try:
            sensor_ranges = {
                "temperature": {"min": 5, "max": 25, "unit": "°C"},
                "wind": {"min": 0, "max": 40, "unit": "m/s"},
                "pressure": {"min": 980, "max": 1040, "unit": "hPa"},
                "humidity": {"min": 40, "max": 95, "unit": "%"},
            }
            
            config = sensor_ranges.get(sensor_type, sensor_ranges["temperature"])
            value = round(random.uniform(config["min"], config["max"]), 1)
            
            sensor_id = f"urn:ngsi-ld:Device:{sensor_type.lower()}-sensor-01"
            
            event = RealtimeEvent(
                event="sensor_reading",
                scope=EventScope(port_id=port_id),
                entity=EntityReference(type="Device", id=sensor_id),
                payload={
                    "sensor_id": sensor_id,
                    "sensor_type": sensor_type,
                    "value": value,
                    "unit": config["unit"],
                    "location": {"lat": 43.3, "lon": -8.4},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                source="simulator",
                severity="info"
            )
            
            manager = get_manager()
            await manager.broadcast_event(event)
            logger.debug(f"[TASK] Sensor reading: {sensor_type}={value} {config['unit']}")
        
        except Exception as e:
            logger.error(f"[TASK] Error broadcasting sensor: {type(e).__name__}: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(emit())
    finally:
        loop.close()


@shared_task(bind=True, name='smartport.broadcast_alert')
def broadcast_alert(
    self,
    alert_type: str = "weather_warning",
    port_id: str = "galicia-a-coruna"
):
    """
    Emit alert event (warnings, incidents, etc).
    
    Simulates: system alerts and notifications
    """
    import asyncio
    
    async def emit():
        try:
            # Randomly decide whether to emit (80% chance not to, to be sparse)
            if random.random() > 0.2:
                logger.debug("[TASK] Alert skipped (random)")
                return
            
            alert_descriptions = {
                "weather_warning": "High wind warning - speeds may exceed safe limits",
                "berth_unavailable": "Berth maintenance scheduled",
                "system_warning": "Database connection slow",
                "security_incident": "Unauthorized access attempt detected",
            }
            
            alert_id = f"urn:ngsi-ld:Alert:alert-{random.randint(1000, 9999)}"
            severity_level = random.choice(["warning", "critical"])
            
            event = RealtimeEvent(
                event="alert.triggered",
                scope=EventScope(port_id=port_id),
                entity=EntityReference(type="Alert", id=alert_id),
                payload={
                    "alert_id": alert_id,
                    "alert_type": alert_type,
                    "severity": severity_level,
                    "description": alert_descriptions.get(alert_type, "Unknown alert"),
                    "entity_id": f"urn:ngsi-ld:Berth:{port_id}:berth-001",
                    "recommended_action": "Check system status",
                    "triggered_at": datetime.utcnow().isoformat() + "Z",
                },
                source="simulator",
                severity=severity_level,
            )
            
            manager = get_manager()
            await manager.broadcast_event(event)
            logger.info(f"[TASK] Alert: {alert_type} ({severity_level})")
        
        except Exception as e:
            logger.error(f"[TASK] Error broadcasting alert: {type(e).__name__}: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(emit())
    finally:
        loop.close()


@shared_task(bind=True, name='smartport.emit_demo_events')
def emit_demo_events(self):
    """
    Orchestrating task that emits various events periodically.
    
    This task is called by Celery Beat at regular intervals to simulate
    a live port operation with changing conditions.
    """
    logger.info("[TASK] Starting demo event emission cycle")
    
    try:
        port_id = "galicia-a-coruna"
        
        # Emit occupancy update
        broadcast_occupancy_update.apply_async(args=[port_id])
        
        # Emit 1-3 random berth updates
        for _ in range(random.randint(1, 3)):
            berth_idx = random.randint(0, 14)
            broadcast_berth_update.apply_async(args=[port_id, berth_idx])
        
        # Emit sensor readings
        for sensor_type in ["temperature", "wind", "humidity"]:
            if random.random() > 0.3:  # 70% chance
                broadcast_sensor_reading.apply_async(args=[sensor_type, port_id])
        
        # Emit occasional alert
        if random.random() > 0.7:  # 30% chance
            alert_type = random.choice(["weather_warning", "system_warning"])
            broadcast_alert.apply_async(args=[alert_type, port_id])
        
        logger.info("[TASK] Demo event emission cycle complete")
        return {"status": "success", "message": "Events emitted"}
    
    except Exception as e:
        logger.error(f"[TASK] Error in event emission: {type(e).__name__}: {e}")
        return {"status": "error", "message": str(e)}
