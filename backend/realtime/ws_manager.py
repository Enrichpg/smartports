"""
WebSocket connection manager.
Handles multiple concurrent WebSocket connections, subscriptions, and broadcasting.
"""

import logging
import asyncio
import json
from typing import Dict, Set, Optional, Callable, Awaitable
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from .models import RealtimeEvent, SubscriptionFilter, WebSocketMessage
from .event_types import EventType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts events to subscribed clients.
    Thread-safe for async operations.
    """
    
    def __init__(self):
        # {connection_id: {"websocket": WebSocket, "subscriptions": SubscriptionFilter}}
        self.active_connections: Dict[str, Dict] = {}
        self.connection_counter = 0
        self._lock = asyncio.Lock()
    
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
            }
            
            logger.info(f"WebSocket connected: {conn_id} (total: {len(self.active_connections)})")
        
        return conn_id
    
    async def disconnect(self, conn_id: str) -> None:
        """Unregister and clean up a WebSocket connection."""
        async with self._lock:
            if conn_id in self.active_connections:
                del self.active_connections[conn_id]
                logger.info(f"WebSocket disconnected: {conn_id} (total: {len(self.active_connections)})")
    
    async def subscribe(self, conn_id: str, filter: SubscriptionFilter) -> None:
        """Update subscription filters for a connection."""
        async with self._lock:
            if conn_id in self.active_connections:
                self.active_connections[conn_id]["subscriptions"] = filter
                logger.debug(f"Subscription updated for {conn_id}: {filter}")
    
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
    
    async def broadcast_event(self, event: RealtimeEvent) -> None:
        """
        Broadcast an event to all connected clients whose subscriptions match.
        Handles disconnections gracefully.
        """
        if not self.active_connections:
            logger.debug(f"No active connections to broadcast {event.event}")
            return
        
        message = WebSocketMessage(
            type="event",
            data=event.dict()
        )
        
        message_json = json.dumps(message.dict())
        disconnected = []
        
        async with self._lock:
            connections_snapshot = list(self.active_connections.items())
        
        for conn_id, conn_data in connections_snapshot:
            # Check if subscription matches
            if not self._matches_subscription(conn_id, event):
                continue
            
            try:
                await conn_data["websocket"].send_text(message_json)
                conn_data["last_heartbeat"] = datetime.utcnow()
                logger.debug(f"Event {event.event} sent to {conn_id}")
            except Exception as e:
                logger.warning(f"Failed to send event to {conn_id}: {e}")
                disconnected.append(conn_id)
        
        # Clean up disconnected clients
        for conn_id in disconnected:
            await self.disconnect(conn_id)
    
    async def broadcast_to_scope(
        self,
        event: RealtimeEvent,
        scope_key: str = "port_id"
    ) -> None:
        """
        Broadcast to specific scope (e.g., all clients watching a specific port).
        Default scope_key is port_id.
        """
        await self.broadcast_event(event)
    
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
            return True
        except Exception as e:
            logger.warning(f"Failed to send message to {conn_id}: {e}")
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
            
            if msg_type == "ping":
                pong = WebSocketMessage(type="pong")
                await self.send_to_connection(conn_id, pong)
            
            elif msg_type == "subscribe":
                # Client can subscribe to specific channels
                filter_data = data.get("data", {})
                filter = SubscriptionFilter(**filter_data) if filter_data else SubscriptionFilter()
                await self.subscribe(conn_id, filter)
                
                # Confirm subscription
                confirm = WebSocketMessage(
                    type="subscription_confirmed",
                    data={"filter": filter.dict()}
                )
                await self.send_to_connection(conn_id, confirm)
            
            elif msg_type == "command" and on_command:
                # Forward commands to handler if provided
                await on_command(conn_id, data.get("data", {}))
            
            logger.debug(f"Processed {msg_type} message from {conn_id}")
        
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from {conn_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {conn_id}: {e}")
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    async def get_health(self) -> Dict:
        """Get health information about the WebSocket manager."""
        return {
            "active_connections": len(self.active_connections),
            "status": "healthy" if len(self.active_connections) >= 0 else "degraded",
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
