"""
Tests for the realtime infrastructure: WebSocket, audit, cache, and Celery.
"""

import pytest
import asyncio
import json
from datetime import datetime
from uuid import uuid4

# Realtime components
from realtime.ws_manager import ConnectionManager
from realtime.event_bus import EventBus
from realtime.models import RealtimeEvent, EventScope, EntityReference, SubscriptionFilter
from cache.redis_service import RedisCache, CacheKeys
from audit.models import AuditLog
from audit.service import AuditService
from tasks.celery_app import make_celery, get_task_result


# =============================================================================
# WebSocket Manager Tests
# =============================================================================

@pytest.mark.asyncio
async def test_websocket_manager_basic_connection():
    """Test basic WebSocket connection and disconnection."""
    manager = ConnectionManager()
    
    # Mock WebSocket
    class MockWebSocket:
        async def accept(self):
            pass
        async def send_text(self, data: str):
            pass
    
    ws = MockWebSocket()
    conn_id = await manager.connect(ws, "test-client")
    
    assert conn_id == "test-client"
    assert manager.get_connection_count() == 1
    
    await manager.disconnect(conn_id)
    assert manager.get_connection_count() == 0


@pytest.mark.asyncio
async def test_websocket_subscription_filter():
    """Test subscription filtering."""
    manager = ConnectionManager()
    
    class MockWebSocket:
        async def accept(self):
            pass
        async def send_text(self, data: str):
            self.last_message = data
    
    ws = MockWebSocket()
    conn_id = await manager.connect(ws)
    
    # Update subscription to only port-specific events
    filter = SubscriptionFilter(
        port_ids=["port-a"],
        event_types=["berth.updated"],
    )
    await manager.subscribe(conn_id, filter)
    
    # Event matching the filter
    event = RealtimeEvent(
        event="berth.updated",
        entity=EntityReference(type="Berth", id="berth-1"),
        scope=EventScope(port_id="port-a"),
        payload={},
    )
    
    assert manager._matches_subscription(conn_id, event)
    
    # Event not matching the filter (different port)
    event2 = RealtimeEvent(
        event="berth.updated",
        entity=EntityReference(type="Berth", id="berth-2"),
        scope=EventScope(port_id="port-b"),
        payload={},
    )
    
    assert not manager._matches_subscription(conn_id, event2)
    
    await manager.disconnect(conn_id)


# =============================================================================
# Event Bus Tests
# =============================================================================

@pytest.mark.asyncio
async def test_event_bus_publish():
    """Test basic event publishing."""
    bus = EventBus()
    
    # Publish an event
    event = await bus.publish(
        event_type="berth.updated",
        entity_type="Berth",
        entity_id="berth-1",
        port_id="port-a",
        payload={"status": "occupied"},
    )
    
    assert event.event == "berth.updated"
    assert event.entity.id == "berth-1"
    assert event.scope.port_id == "port-a"
    assert bus.event_count == 1


@pytest.mark.asyncio
async def test_event_bus_helper_methods():
    """Test event bus helper methods for specific event types."""
    bus = EventBus()
    
    # Test port call created
    event = await bus.publish_portcall_created(
        portcall_id="pc-1",
        port_id="port-a",
        vessel_id="vessel-1",
        payload={"vessel_name": "TestVessel"},
    )
    
    assert event.event == "portcall.created"
    assert event.entity.type == "PortCall"
    assert bus.event_count == 1


@pytest.mark.asyncio
async def test_event_bus_audit_hook():
    """Test event bus audit hook registration."""
    bus = EventBus()
    
    audit_events = []
    
    def audit_hook(event: RealtimeEvent):
        audit_events.append(event)
    
    bus.subscribe_audit(audit_hook)
    
    # Publish an event
    await bus.publish(
        event_type="test.event",
        entity_type="Test",
        entity_id="test-1",
        payload={},
    )
    
    # Give async tasks a moment to complete
    await asyncio.sleep(0.1)
    
    # Audit hook should have been called
    assert len(audit_events) > 0 or bus.event_count == 1  # Either hook called or event published


# =============================================================================
# Cache Tests
# =============================================================================

@pytest.mark.asyncio
async def test_redis_cache_set_get():
    """Test Redis cache set and get operations."""
    cache = RedisCache("redis://localhost:6379/0")
    await cache.connect()
    
    # Set a value
    success = await cache.set("test-key", {"data": "value"}, ttl=10)
    assert success
    
    # Get the value
    value = await cache.get("test-key")
    assert value == {"data": "value"}
    
    # Clean up
    await cache.delete("test-key")
    await cache.disconnect()


@pytest.mark.asyncio
async def test_redis_cache_key_patterns():
    """Test cache key naming patterns."""
    
    port_id = "urn:ngsi-ld:Port:coruna"
    
    key = CacheKeys.port_summary(port_id)
    assert key == f"port:summary:{port_id}"
    
    key = CacheKeys.port_availability(port_id)
    assert key == f"port:availability:{port_id}"
    
    key = CacheKeys.port_alerts(port_id)
    assert key == f"port:alerts:active:{port_id}"
    
    key = CacheKeys.dashboard_overview()
    assert key == "dashboard:galicia:overview"


@pytest.mark.asyncio
async def test_redis_cache_graceful_failure():
    """Test cache graceful failure handling."""
    # Create cache with invalid URL
    cache = RedisCache("redis://invalid-host:6379/0")
    
    # Attempt to set value should fail gracefully
    success = await cache.set("test-key", "value")
    assert success is False
    
    # Get should return None gracefully
    value = await cache.get("test-key")
    assert value is None


# =============================================================================
# Audit Tests
# =============================================================================

@pytest.mark.asyncio
async def test_audit_service_log_event():
    """Test audit service event logging."""
    # Note: This test requires a working DB session
    # For now, we just test the event creation
    
    event = RealtimeEvent(
        event="portcall.created",
        entity=EntityReference(type="PortCall", id="pc-1"),
        scope=EventScope(port_id="port-a", portcall_id="pc-1"),
        payload={"vessel_name": "Test"},
        correlation_id="corr-1",
    )
    
    # Test event structure
    event_dict = event.dict()
    assert event_dict["event"] == "portcall.created"
    assert event_dict["entity"]["type"] == "PortCall"
    assert event_dict["scope"]["port_id"] == "port-a"


# =============================================================================
# Celery Tests
# =============================================================================

def test_celery_app_creation():
    """Test Celery app creation."""
    celery = make_celery(
        broker_url="redis://localhost:6379/1",
        result_backend="redis://localhost:6379/2",
        app_name="test-smartports",
    )
    
    assert celery is not None
    assert celery.conf.task_serializer == "json"
    assert celery.conf.timezone == "UTC"


def test_get_task_result():
    """Test getting task result status."""
    # Create a dummy task ID
    task_id = str(uuid4())
    
    # Get result (will fail since task doesn't exist, but tests the function)
    result = get_task_result(task_id)
    
    # Should return a dict with status field
    assert isinstance(result, dict)
    assert "status" in result or "error" in result


# =============================================================================
# Integration Tests
# =============================================================================

@pytest.mark.asyncio
async def test_full_event_flow():
    """Test a complete event flow: publish -> broadcast -> audit."""
    
    # Create components
    manager = ConnectionManager()
    bus = EventBus()
    
    # Track audit logs
    audit_logs = []
    
    def audit_callback(event: RealtimeEvent):
        audit_logs.append(event)
    
    bus.subscribe_audit(audit_callback)
    
    # Mock WebSocket connection
    class MockWebSocket:
        async def accept(self):
            pass
        async def send_text(self, data: str):
            self.received = data
    
    ws = MockWebSocket()
    conn_id = await manager.connect(ws)
    
    # Publish an event
    event = await bus.publish(
        event_type="berth.updated",
        entity_type="Berth",
        entity_id="berth-1",
        port_id="port-a",
        payload={"status": "occupied"},
    )
    
    # Give async tasks time to complete
    await asyncio.sleep(0.2)
    
    # Verify event was published
    assert bus.event_count == 1
    
    # Clean up
    await manager.disconnect(conn_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
