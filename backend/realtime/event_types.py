"""
Event type definitions for the realtime system.
Centralizes all event types to avoid magic strings.
"""

from enum import Enum
from typing import Literal


class EventType(str, Enum):
    """All event types supported by the realtime system"""
    
    # Berth events
    BERTH_UPDATED = "berth.updated"
    
    # Port call events
    PORTCALL_CREATED = "portcall.created"
    PORTCALL_UPDATED = "portcall.updated"
    PORTCALL_CLOSED = "portcall.closed"
    
    # Alert events
    ALERT_CREATED = "alert.created"
    ALERT_UPDATED = "alert.updated"
    
    # Availability events
    AVAILABILITY_UPDATED = "availability.updated"
    
    # Port summary events
    PORT_SUMMARY_UPDATED = "port.summary.updated"
    
    # Authorization events
    AUTHORIZATION_VALIDATION_FAILED = "authorization.validation.failed"
    
    # System events
    SYSTEM_HEALTH_CHECK = "system.health.check"


class EventScope(str, Enum):
    """Scope/channel for event delivery"""
    
    GLOBAL = "global"
    PORT = "port"
    BERTH = "berth"
    PORTCALL = "portcall"
    VESSEL = "vessel"


# Typing helpers for event payloads
EventTypeStr = Literal[
    "berth.updated",
    "portcall.created",
    "portcall.updated",
    "portcall.closed",
    "alert.created",
    "alert.updated",
    "availability.updated",
    "port.summary.updated",
    "authorization.validation.failed",
    "system.health.check",
]
