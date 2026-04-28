"""
Real-time WebSocket endpoint and management.
Handles WebSocket connections, subscriptions, and event streaming.
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from realtime.ws_manager import get_manager
from realtime.models import SubscriptionFilter

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["realtime"],
    prefix="/realtime",
)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time event streaming.
    
    Client can:
    - Subscribe to events with filters
    - Receive events matching their subscription
    - Send ping/pong for keepalive
    
    Usage:
    1. Connect: ws://localhost:8000/api/v1/realtime/ws
    2. Subscribe: {"type": "subscribe", "data": {"event_types": ["berth.updated"], "port_ids": ["port-id"]}}
    3. Receive events as they happen
    
    Event format:
    {
        "type": "event",
        "data": {
            "event": "berth.updated",
            "timestamp": "2026-04-28T14:00:00Z",
            "entity": {"type": "Berth", "id": "..."},
            ...
        }
    }
    """
    
    manager = get_manager()
    conn_id = await manager.connect(websocket, client_id)
    logger.info(f"WebSocket connected: {conn_id}")
    
    try:
        while True:
            # Wait for incoming message from client
            data = await websocket.receive_text()
            
            # Process the message
            await manager.handle_client_message(conn_id, data)
    
    except WebSocketDisconnect:
        await manager.disconnect(conn_id)
        logger.info(f"WebSocket disconnected: {conn_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for {conn_id}: {e}")
        await manager.disconnect(conn_id)


@router.get("/health", name="WebSocket Health Check")
async def websocket_health():
    """Get health status of WebSocket server."""
    manager = get_manager()
    health = await manager.get_health()
    return {
        "component": "websocket_manager",
        **health,
    }


@router.get("/connections", name="Active Connections Count")
async def get_connections_count():
    """Get the number of active WebSocket connections."""
    manager = get_manager()
    return {
        "active_connections": manager.get_connection_count(),
    }
