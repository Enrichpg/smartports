"""
Event bus for the realtime system.
Decouples event publication from WebSocket management and provides extensibility
for future integrations (e.g., message queues, external systems).
"""

import logging
import asyncio
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from uuid import uuid4

from .models import RealtimeEvent, EventScope, EntityReference
from .ws_manager import get_manager

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for publishing domain events.
    Handles:
    - Event publication
    - WebSocket broadcasting
    - Event tracking and audit hooks
    - Extensibility for external systems
    """
    
    def __init__(self):
        self._subscribers: List[Callable[[RealtimeEvent], None]] = []
        self._audit_hooks: List[Callable[[RealtimeEvent], None]] = []
        self._task_hooks: List[Callable[[RealtimeEvent], None]] = []
        self.event_count = 0
    
    def subscribe_audit(self, callback: Callable[[RealtimeEvent], None]) -> None:
        """Register a callback to be invoked for audit logging."""
        self._audit_hooks.append(callback)
        logger.debug(f"Audit hook registered (total: {len(self._audit_hooks)})")
    
    def subscribe_tasks(self, callback: Callable[[RealtimeEvent], None]) -> None:
        """Register a callback to trigger background tasks on events."""
        self._task_hooks.append(callback)
        logger.debug(f"Task hook registered (total: {len(self._task_hooks)})")
    
    async def publish(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        payload: Dict[str, Any],
        port_id: Optional[str] = None,
        berth_id: Optional[str] = None,
        portcall_id: Optional[str] = None,
        vessel_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        severity: str = "info",
        source: str = "backend",
    ) -> RealtimeEvent:
        """
        Publish a domain event.
        Automatically triggers WebSocket broadcasting and registered hooks.
        """
        
        # Build event
        event = RealtimeEvent(
            event=event_type,
            entity=EntityReference(type=entity_type, id=entity_id),
            scope=EventScope(
                port_id=port_id,
                berth_id=berth_id,
                portcall_id=portcall_id,
                vessel_id=vessel_id,
            ),
            payload=payload,
            correlation_id=correlation_id or str(uuid4()),
            severity=severity,
            source=source,
        )
        
        self.event_count += 1
        logger.info(
            f"Event published: {event_type} | entity: {entity_id} | port: {port_id} "
            f"| severity: {severity}"
        )
        
        # WebSocket broadcast (async, non-blocking)
        try:
            manager = get_manager()
            asyncio.create_task(manager.broadcast_event(event))
        except Exception as e:
            logger.error(f"Error broadcasting event to WebSocket: {e}")
        
        # Audit hooks (async)
        for hook in self._audit_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    asyncio.create_task(hook(event))
                else:
                    hook(event)
            except Exception as e:
                logger.error(f"Error in audit hook: {e}")
        
        # Task hooks (async)
        for hook in self._task_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    asyncio.create_task(hook(event))
                else:
                    hook(event)
            except Exception as e:
                logger.error(f"Error in task hook: {e}")
        
        return event
    
    async def publish_berth_updated(
        self,
        berth_id: str,
        port_id: str,
        status: str,
        previous_status: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish a berth.updated event."""
        return await self.publish(
            event_type="berth.updated",
            entity_type="Berth",
            entity_id=berth_id,
            port_id=port_id,
            berth_id=berth_id,
            payload={
                "status": status,
                "previous_status": previous_status,
            },
            correlation_id=correlation_id,
        )
    
    async def publish_portcall_created(
        self,
        portcall_id: str,
        port_id: str,
        vessel_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish a portcall.created event."""
        return await self.publish(
            event_type="portcall.created",
            entity_type="PortCall",
            entity_id=portcall_id,
            port_id=port_id,
            portcall_id=portcall_id,
            vessel_id=vessel_id,
            payload=payload,
            correlation_id=correlation_id,
        )
    
    async def publish_portcall_updated(
        self,
        portcall_id: str,
        port_id: str,
        vessel_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish a portcall.updated event."""
        return await self.publish(
            event_type="portcall.updated",
            entity_type="PortCall",
            entity_id=portcall_id,
            port_id=port_id,
            portcall_id=portcall_id,
            vessel_id=vessel_id,
            payload=payload,
            correlation_id=correlation_id,
        )
    
    async def publish_portcall_closed(
        self,
        portcall_id: str,
        port_id: str,
        vessel_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish a portcall.closed event."""
        return await self.publish(
            event_type="portcall.closed",
            entity_type="PortCall",
            entity_id=portcall_id,
            port_id=port_id,
            portcall_id=portcall_id,
            vessel_id=vessel_id,
            payload=payload,
            correlation_id=correlation_id,
            severity="warning",
        )
    
    async def publish_alert_created(
        self,
        alert_id: str,
        port_id: str,
        alert_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        severity: str = "warning",
    ) -> RealtimeEvent:
        """Helper to publish an alert.created event."""
        return await self.publish(
            event_type="alert.created",
            entity_type="Alert",
            entity_id=alert_id,
            port_id=port_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=severity,
        )
    
    async def publish_alert_updated(
        self,
        alert_id: str,
        port_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        severity: str = "warning",
    ) -> RealtimeEvent:
        """Helper to publish an alert.updated event."""
        return await self.publish(
            event_type="alert.updated",
            entity_type="Alert",
            entity_id=alert_id,
            port_id=port_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=severity,
        )
    
    async def publish_availability_updated(
        self,
        port_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish an availability.updated event."""
        return await self.publish(
            event_type="availability.updated",
            entity_type="Availability",
            entity_id=f"urn:ngsi-ld:Availability:{port_id}",
            port_id=port_id,
            payload=payload,
            correlation_id=correlation_id,
        )
    
    async def publish_port_summary_updated(
        self,
        port_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish a port.summary.updated event."""
        return await self.publish(
            event_type="port.summary.updated",
            entity_type="Port",
            entity_id=port_id,
            port_id=port_id,
            payload=payload,
            correlation_id=correlation_id,
        )
    
    async def publish_authorization_validation_failed(
        self,
        vessel_id: str,
        port_id: Optional[str] = None,
        reason: str = "Unknown",
        correlation_id: Optional[str] = None,
    ) -> RealtimeEvent:
        """Helper to publish an authorization.validation.failed event."""
        return await self.publish(
            event_type="authorization.validation.failed",
            entity_type="Vessel",
            entity_id=vessel_id,
            port_id=port_id,
            vessel_id=vessel_id,
            payload={"reason": reason},
            correlation_id=correlation_id,
            severity="error",
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the event bus."""
        return {
            "total_events_published": self.event_count,
            "audit_hooks": len(self._audit_hooks),
            "task_hooks": len(self._task_hooks),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global instance
_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus instance."""
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance
