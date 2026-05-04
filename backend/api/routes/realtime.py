"""
Real-time WebSocket endpoint and management.
Handles WebSocket connections, subscriptions, and event streaming.

Endpoints:
- /api/v1/realtime/ws: WebSocket streaming
- /api/v1/realtime/health: WebSocket server health
- /api/v1/realtime/connections: Active connection count
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import asyncio

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
    - Connect and receive all events by default
    - Subscribe to specific event types/ports
    - Send ping for keepalive (optional, automatic heartbeats available)
    - Send heartbeat messages
    
    Usage:
    1. Connect: ws://localhost:8000/api/v1/realtime/ws?client_id=my-client
    2. Subscribe (optional): {"type": "subscribe", "data": {"event_types": ["berth.updated"], "port_ids": ["galicia-a-coruna"]}}
    3. Receive events as they happen
    
    Event format:
    {
        "type": "event",
        "timestamp": "2026-05-04T10:00:00Z",
        "data": {
            "event_id": "uuid",
            "event": "berth.updated",
            "timestamp": "2026-05-04T10:00:00Z",
            "scope": {"port_id": "galicia-a-coruna", ...},
            "entity": {"type": "Berth", "id": "..."},
            "payload": {...},
            "source": "backend",
            "severity": "info"
        }
    }
    
    Heartbeat format (sent by server):
    {
        "type": "heartbeat",
        "timestamp": "2026-05-04T10:00:00Z",
        "data": {"timestamp": "2026-05-04T10:00:00Z"}
    }
    """
    
    manager = get_manager()
    conn_id = await manager.connect(websocket, client_id)
    logger.info(f"[WS] WebSocket endpoint: Client connected: {conn_id}")
    
    # Create heartbeat task for this connection
    heartbeat_task = None
    
    try:
        # Schedule periodic heartbeat
        async def send_heartbeat():
            """Send heartbeats every 30 seconds"""
            while True:
                await asyncio.sleep(30)
                try:
                    # Just ensure connection is alive
                    if manager.active_connections.get(conn_id):
                        logger.debug(f"[WS] Heartbeat tick for {conn_id}")
                except Exception as e:
                    logger.debug(f"[WS] Heartbeat error for {conn_id}: {e}")
                    break
        
        heartbeat_task = asyncio.create_task(send_heartbeat())
        
        # Main message loop
        while True:
            # Wait for incoming message from client
            data = await websocket.receive_text()
            
            # Process the message
            await manager.handle_client_message(conn_id, data)
    
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected normally: {conn_id}")
        await manager.disconnect(conn_id)
    
    except Exception as e:
        logger.error(f"[WS] WebSocket error for {conn_id}: {type(e).__name__}: {e}")
        await manager.disconnect(conn_id)
    
    finally:
        # Clean up heartbeat task
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"[WS] Endpoint cleanup complete for {conn_id}")


@router.get("/health", name="WebSocket Health Check")
async def websocket_health():
    """Get health status of WebSocket server."""
    manager = get_manager()
    health = await manager.get_health()
    return {
        "component": "websocket_manager",
        "endpoint": "/api/v1/realtime/ws",
        **health,
    }


@router.get("/connections", name="Active Connections Count")
async def get_connections_count():
    """Get the number of active WebSocket connections."""
    manager = get_manager()
    return {
        "active_connections": manager.get_connection_count(),
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    }
