"""
Pydantic models for realtime events.
Defines the structure of events flowing through the system.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4


class EventScope(BaseModel):
    """Identifies the scope/channel for this event"""
    port_id: Optional[str] = None
    berth_id: Optional[str] = None
    portcall_id: Optional[str] = None
    vessel_id: Optional[str] = None


class EntityReference(BaseModel):
    """References the entity that triggered the event"""
    type: str  # e.g. "Berth", "PortCall", "Alert"
    id: str    # NGSI-LD entity URN


class RealtimeEvent(BaseModel):
    """
    Standard event envelope for all realtime events.
    Ensures consistency across the system.
    """
    
    # Event metadata
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event: str = Field(..., description="Event type name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp")
    correlation_id: Optional[str] = None  # For tracing through async operations
    
    # Scope and entity
    scope: EventScope = Field(..., description="Delivery scope")
    entity: EntityReference = Field(..., description="Entity that triggered event")
    
    # Payload
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    
    # Metadata
    source: str = "backend"  # e.g., "backend", "simulator", "external_api"
    severity: str = "info"  # info, warning, error
    
    def dict(self, **kwargs):
        """Override to ensure timestamp is ISO format"""
        d = super().dict(**kwargs)
        if isinstance(d['timestamp'], datetime):
            d['timestamp'] = d['timestamp'].isoformat() + 'Z'
        if d.get('event_id'):
            d['event_id'] = str(d['event_id'])
        return d
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "event": "berth.updated",
                "timestamp": "2026-04-28T14:00:00Z",
                "correlation_id": "req-12345",
                "scope": {
                    "port_id": "urn:ngsi-ld:Port:coruna",
                    "berth_id": "urn:ngsi-ld:Berth:coruna:berth-001"
                },
                "entity": {
                    "type": "Berth",
                    "id": "urn:ngsi-ld:Berth:coruna:berth-001"
                },
                "payload": {
                    "status": "occupied",
                    "previous_status": "reserved"
                },
                "source": "backend",
                "severity": "info"
            }
        }


class WebSocketMessage(BaseModel):
    """Message format for WebSocket communication"""
    
    type: str  # "event", "ping", "pong", "subscribe", "unsubscribe"
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionFilter(BaseModel):
    """Filter for event subscription"""
    
    event_types: Optional[List[str]] = None  # If None, subscribe to all
    port_ids: Optional[List[str]] = None     # If None, all ports
    entity_types: Optional[List[str]] = None # If None, all entities
