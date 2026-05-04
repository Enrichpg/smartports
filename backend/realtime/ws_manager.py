"""
WebSocket connection manager.
Handles multiple concurrent WebSocket connections, subscriptions, and broadcasting.
"""

import logging
import asyncio
import json
from typing import Dict, Optional, Callable, Awaitable
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta

from .models import RealtimeEvent, SubscriptionFilter, WebSocketMessage
from .event_types import EventType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts events to subscribed clients.
    Thread-safe for async operations.
    
    Features:
    - Multiple concurrent connections with subscriptions
    - Event filtering per connection
    - Automatic heartbeat/ping-pong
    - Graceful disconnection handling
    - Connection cleanup on error
    """
    
    def __init__(self, heartbeat_interval: int = 30):
        # {connection_id: {"websocket": WebSocket, "subscriptions": SubscriptionFilter, ...}}
        self.active_connections: Dict[str, Dict] = {}
        self.connection_counter = 0
        self._lock = asyncio.Lock()
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_task = None
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """
        Accept and register a new WebSocket connection.
        Returns the connection ID.
        """
        await websocket.accept()
        
        async with self._lock:
            self.connection_counter += 1
            conn_id = client_id or f"conn-{self.connection_counter}"
            
            self.active_connections[conn_id] = {
                "websocket": websocket,
                "subscriptions": SubscriptionFilter(),  # Subscribe to everything by default
                "created_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow(),
                "message_count": 0,
                "error_count": 0,
            }
            
            logger.info(
                f"[WS] Connected: {conn_id} "
                f"(total: {len(self.active_connections)} active)"
            )
        
        return conn_id
    
    async def disconnect(self, conn_id: str) -> None:
        """Unregister and clean up a WebSocket connection."""
        async with self._lock:
            if conn_id in self.active_connections:
                conn_data = self.active_connections[conn_id]
                del self.active_connections[conn_id]
                logger.info(
                    f"[WS] Disconnected: {conn_id} "
                    f"(messages: {conn_data['message_count']}, "
                    f"errors: {conn_data['error_count']}, "
                    f"remaining: {len(self.active_connections)})"
                )
    
    async def subscribe(self, conn_id: str, filter: SubscriptionFilter) -> None:
        """Update subscription filters for a connection."""
        async with self._lock:
            if conn_id in self.active_connections:
                self.active_connections[conn_id]["subscriptions"] = filter
                logger.debug(
                    f"[WS] Subscription updated for {conn_id}: "
                    f"events={filter.event_types}, ports={filter.port_ids}"
                )
    
    def _matches_subscription(self, conn_id: str, event: RealtimeEvent) -> bool:
        """Check if a connection's subscription matches the event."""
        conn_data = self.active_connections.get(conn_id)
        if not conn_data:
            return False
        
        filter = conn_data["subscriptions"]
        
        # Check event type filter
        if filter.event_types and event.event not in filter.event_types:
            return False
        
        # Check port filter
        if filter.port_ids and event.scope.port_id not in filter.port_ids:
            return False
        
        # Check entity type filter
        if filter.entity_types and event.entity.type not in filter.entity_types:
            return False
        
        return True
    
    async def broadcast_event(self, event: RealtimeEvent) -> tuple[int, int]:
        """
        Broadcast an event to all connected clients whose subscriptions match.
        Handles disconnections gracefully.
        
        Returns: (sent_count, failed_count)
        """
        if not self.active_connections:
            logger.debug(f"[WS] No active connections for event: {event.event}")
            return (0, 0)
        
        message = WebSocketMessage(
            type="event",
            data=event.dict()
        )
        
        message_json = json.dumps(message.dict())
        disconnected = []
        sent_count = 0
        failed_count = 0
        
        async with self._lock:
            connections_snapshot = list(self.active_connections.items())
        
        for conn_id, conn_data in connections_snapshot:
            # Check if subscription matches
            if not self._matches_subscription(conn_id, event):
                continue
            
            try:
                await conn_data["websocket"].send_text(message_json)
                conn_data["last_heartbeat"] = datetime.utcnow()
                conn_data["message_count"] += 1
                sent_count += 1
                logger.debug(
                    f"[WS] Event '{event.event}' sent to {conn_id}"
                )
            except Exception as e:
                logger.warning(
                    f"[WS] Failed to send event to {conn_id}: {type(e).__name__}: {e}"
                )
                conn_data["error_count"] += 1
                failed_count += 1
                disconnected.append(conn_id)
        
        # Clean up disconnected clients
        for conn_id in disconnected:
            await self.disconnect(conn_id)
        
        if sent_count > 0 or failed_count > 0:
            logger.info(
                f"[WS] Broadcast '{event.event}': "
                f"sent={sent_count}, failed={failed_count}"
            )
        
        return (sent_count, failed_count)
    
    async def send_to_connection(self, conn_id: str, message: WebSocketMessage) -> bool:
        """
        Send a specific message to a single connection.
        Returns True if successful, False if connection not found or failed.
        """
        async with self._lock:
            conn_data = self.active_connections.get(conn_id)
        
        if not conn_data:
            return False
        
        try:
            message_json = json.dumps(message.dict())
            await conn_data["websocket"].send_text(message_json)
            conn_data["message_count"] += 1
            return True
        except Exception as e:
            logger.warning(f"[WS] Failed to send message to {conn_id}: {e}")
            conn_data["error_count"] += 1
            await self.disconnect(conn_id)
            return False
    
    async def handle_client_message(
        self,
        conn_id: str,
        message: str,
        on_command: Optional[Callable[[str, Dict], Awaitable[None]]] = None
    ) -> None:
        """
        Process incoming message from a client.
        Can be extended to handle client commands/subscriptions.
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            logger.debug(f"[WS] Message from {conn_id}: type={msg_type}")
            
            if msg_type == "heartbeat":
                # Client heartbeat, just acknowledge
                pass
            
            elif msg_type == "ping":
                pong = WebSocketMessage(type="pong", data={"timestamp": datetime.utcnow().isoformat()})
                await self.send_to_connection(conn_id, pong)
            
            elif msg_type == "subscribe":
                # Client can subscribe to specific channels
                filter_data = data.get("data", {})
                filter = SubscriptionFilter(**filter_data) if filter_data else SubscriptionFilter()
                await self.subscribe(conn_id, filter)
                
                # Confirm subscription
                confirm = WebSocketMessage(
                    type="subscription_confirmed",
                    data={
                        "filter": {
                            "event_types": filter.event_types,
                            "port_ids": filter.port_ids,
                            "entity_types": filter.entity_types,
                        }
                    }
                )
                await self.send_to_connection(conn_id, confirm)
            
            elif msg_type == "unsubscribe":
                # Clear subscriptions
                await self.subscribe(conn_id, SubscriptionFilter())
                confirm = WebSocketMessage(
                    type="unsubscribed",
                    data={"message": "Unsubscribed from all events"}
                )
                await self.send_to_connection(conn_id, confirm)
            
            elif msg_type == "command" and on_command:
                # Forward commands to handler if provided
                await on_command(conn_id, data.get("data", {}))
            
            else:
                logger.debug(f"[WS] Unknown message type from {conn_id}: {msg_type}")
        
        except json.JSONDecodeError:
            logger.warning(f"[WS] Invalid JSON from {conn_id}: {message[:100]}")
        except Exception as e:
            logger.error(f"[WS] Error handling message from {conn_id}: {type(e).__name__}: {e}")
    
    async def broadcast_heartbeat(self) -> None:
        """Send heartbeat to all connected clients."""
        heartbeat = WebSocketMessage(
            type="heartbeat",
            data={"timestamp": datetime.utcnow().isoformat()}
        )
        
        async with self._lock:
            connections_snapshot = list(self.active_connections.items())
        
        disconnected = []
        for conn_id, conn_data in connections_snapshot:
            try:
                message_json = json.dumps(heartbeat.dict())
                await conn_data["websocket"].send_text(message_json)
                logger.debug(f"[WS] Heartbeat sent to {conn_id}")
            except Exception as e:
                logger.warning(f"[WS] Heartbeat failed for {conn_id}: {e}")
                disconnected.append(conn_id)
        
        for conn_id in disconnected:
            await self.disconnect(conn_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    async def get_health(self) -> Dict:
        """Get health information about the WebSocket manager."""
        async with self._lock:
            total_connections = len(self.active_connections)
            total_messages = sum(
                conn_data.get("message_count", 0)
                for conn_data in self.active_connections.values()
            )
            total_errors = sum(
                conn_data.get("error_count", 0)
                for conn_data in self.active_connections.values()
            )
        
        return {
            "active_connections": total_connections,
            "total_messages": total_messages,
            "total_errors": total_errors,
            "status": "healthy" if total_connections >= 0 else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
_manager_instance: Optional[ConnectionManager] = None


def get_manager() -> ConnectionManager:
    """Get or create the global connection manager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ConnectionManager()
    return _manager_instance
