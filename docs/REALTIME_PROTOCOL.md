# SmartPort Real-Time Protocol v1.0

## Overview

The SmartPort real-time system provides live event streaming via WebSocket, enabling instant updates across the operation center dashboard, 2D/3D visualizations, and monitoring systems.

**Endpoint:** `ws://localhost/api/v1/realtime/ws`

## Message Format

All messages follow this structure:

```json
{
  "type": "event|heartbeat|ping|pong|subscribe|subscription_confirmed|unsubscribe|unsubscribed",
  "timestamp": "2026-05-04T10:00:00.000000Z",
  "data": { /* event-specific data */ }
}
```

## Message Types

### 1. Event Messages (Server → Client)

**Type:** `event`

**Description:** Broadcast events from the backend when entities change.

**Schema:**
```json
{
  "type": "event",
  "timestamp": "2026-05-04T10:00:00.000000Z",
  "data": {
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "event": "berth.updated|vessel.arrived|alert.triggered|occupancy.changed",
    "timestamp": "2026-05-04T10:00:00.000000Z",
    "correlation_id": "req-12345",
    "scope": {
      "port_id": "galicia-a-coruna",
      "berth_id": "urn:ngsi-ld:Berth:galicia-a-coruna:berth-001",
      "portcall_id": null,
      "vessel_id": null
    },
    "entity": {
      "type": "Berth|Vessel|Device|PortCall|Alert",
      "id": "urn:ngsi-ld:Berth:galicia-a-coruna:berth-001"
    },
    "payload": {
      /* Event-specific data - see below */
    },
    "source": "backend|simulator|external_api",
    "severity": "info|warning|error"
  }
}
```

### 2. Event Subtypes (Payload Variations)

#### 2.1 berth.updated
```json
{
  "payload": {
    "berth_id": "urn:ngsi-ld:Berth:galicia-a-coruna:berth-001",
    "status": "free|reserved|occupied|unavailable",
    "previous_status": "free",
    "occupancy_percentage": 100,
    "vessel_id": "urn:ngsi-ld:Vessel:IMO-1234567",
    "vessel_name": "Maersk Seatrade",
    "arrival_time": "2026-05-04T10:00:00Z",
    "estimated_departure": "2026-05-05T14:00:00Z",
    "operations": ["loading", "unloading"]
  }
}
```

#### 2.2 vessel.arrived
```json
{
  "payload": {
    "vessel_id": "urn:ngsi-ld:Vessel:IMO-1234567",
    "vessel_name": "Maersk Seatrade",
    "imo": "1234567",
    "mmsi": "219000000",
    "vessel_type": "Container Ship",
    "length_m": 200,
    "beam_m": 30,
    "draft_m": 10,
    "port_id": "galicia-a-coruna",
    "arrival_time": "2026-05-04T10:00:00Z",
    "flag": "DK"
  }
}
```

#### 2.3 alert.triggered
```json
{
  "payload": {
    "alert_id": "urn:ngsi-ld:Alert:alert-001",
    "alert_type": "berth_unavailable|weather_warning|system_warning|security_incident",
    "severity": "info|warning|critical",
    "description": "High wind warning",
    "entity_id": "urn:ngsi-ld:Berth:galicia-a-coruna:berth-001",
    "recommended_action": "Suspend operations",
    "triggered_at": "2026-05-04T10:00:00Z"
  }
}
```

#### 2.4 occupancy.changed
```json
{
  "payload": {
    "port_id": "galicia-a-coruna",
    "total_berths": 15,
    "occupied_berths": 8,
    "reserved_berths": 3,
    "free_berths": 4,
    "occupancy_percentage": 73.3,
    "trending": "increasing|stable|decreasing"
  }
}
```

#### 2.5 sensor_reading
```json
{
  "payload": {
    "sensor_id": "urn:ngsi-ld:Device:weather-01",
    "sensor_type": "temperature|wind|pressure|humidity",
    "value": 15.5,
    "unit": "°C|m/s|hPa|%",
    "location": { "lat": 43.3, "lon": -8.4 },
    "timestamp": "2026-05-04T10:00:00Z"
  }
}
```

### 3. Heartbeat Messages (Server → Client)

**Type:** `heartbeat`

**Description:** Sent by server every 30 seconds to keep connection alive.

```json
{
  "type": "heartbeat",
  "timestamp": "2026-05-04T10:00:00.000000Z",
  "data": { "timestamp": "2026-05-04T10:00:00.000000Z" }
}
```

### 4. Ping/Pong (Client ↔ Server)

**Client → Server:**
```json
{ "type": "ping", "timestamp": "2026-05-04T10:00:00Z" }
```

**Server → Client:**
```json
{ "type": "pong", "timestamp": "2026-05-04T10:00:00Z", "data": { "timestamp": "..." } }
```

### 5. Subscription Management (Client → Server)

#### 5.1 Subscribe to Events

```json
{
  "type": "subscribe",
  "data": {
    "event_types": ["berth.updated", "alert.triggered"],
    "port_ids": ["galicia-a-coruna"],
    "entity_types": ["Berth", "Alert"]
  }
}
```

**Server Response:**
```json
{
  "type": "subscription_confirmed",
  "data": {
    "filter": {
      "event_types": ["berth.updated", "alert.triggered"],
      "port_ids": ["galicia-a-coruna"],
      "entity_types": ["Berth", "Alert"]
    }
  }
}
```

#### 5.2 Unsubscribe from All

```json
{ "type": "unsubscribe" }
```

**Server Response:**
```json
{
  "type": "unsubscribed",
  "data": { "message": "Unsubscribed from all events" }
}
```

## Subscription Filters

If no filter is provided, client receives **all events**.

| Filter | Type | Example | Behavior |
|--------|------|---------|----------|
| `event_types` | `List[str] \| null` | `["berth.updated"]` | Match events by type; `null` = all |
| `port_ids` | `List[str] \| null` | `["galicia-a-coruna"]` | Match by port; `null` = all ports |
| `entity_types` | `List[str] \| null` | `["Berth", "Vessel"]` | Match by entity type; `null` = all |

## Connection Lifecycle

1. **Connect:** Client connects to WebSocket endpoint
   ```
   Client → Server: (WebSocket UPGRADE)
   Server → Client: (Connection accepted)
   ```

2. **Optional Subscribe:** Client specifies what to receive
   ```
   Client → Server: { "type": "subscribe", "data": {...} }
   Server → Client: { "type": "subscription_confirmed", ... }
   ```

3. **Event Stream:** Server broadcasts matching events
   ```
   Server → Client: { "type": "event", "data": {...} }
   Server → Client: { "type": "event", "data": {...} }
   ```

4. **Keepalive:** Heartbeats keep connection alive
   ```
   Server → Client: { "type": "heartbeat", ... }
   Client → Server: (optional ping)
   Server → Client: { "type": "pong", ... }
   ```

5. **Disconnect:** Client or server closes
   ```
   Client → Server: (WebSocket CLOSE)
   OR
   Server → Client: (WebSocket CLOSE)
   ```

## Error Handling

If a message cannot be parsed or processed:
- Server logs the error and continues
- Client is not notified (no error messages in v1)
- Connection remains open

For critical errors (e.g., protocol violations):
- Server closes the WebSocket
- Client reconnects automatically with exponential backoff

## Frontend Integration

### URL Construction

```javascript
const WS_URL = (window.location.protocol === 'https:' ? 'wss:' : 'ws:')
  + '//' + window.location.host + '/api/v1/realtime/ws';
```

### Usage Example

```javascript
import { wsManager } from './services/websocket.js';

// Connect
wsManager.connect();

// Subscribe to berth updates for a port
wsManager.send({
  type: 'subscribe',
  data: {
    event_types: ['berth.updated'],
    port_ids: ['galicia-a-coruna']
  }
});

// Listen for events
wsManager.subscribe('berth.updated', (eventData) => {
  console.log('Berth updated:', eventData);
  updateMapLayer(eventData);
});

// Listen for connection state
wsManager.subscribe('connected', () => {
  console.log('Connected to real-time events');
});

wsManager.subscribe('disconnected', () => {
  console.log('Disconnected, will retry...');
});
```

## Backend Integration

### Emitting Events

```python
from realtime.models import RealtimeEvent, EventScope, EntityReference
from realtime.ws_manager import get_manager

event = RealtimeEvent(
    event="berth.updated",
    scope=EventScope(
        port_id="galicia-a-coruna",
        berth_id="urn:ngsi-ld:Berth:galicia-a-coruna:berth-001"
    ),
    entity=EntityReference(
        type="Berth",
        id="urn:ngsi-ld:Berth:galicia-a-coruna:berth-001"
    ),
    payload={
        "status": "occupied",
        "vessel_name": "Maersk Seatrade"
    },
    source="backend",
    severity="info"
)

manager = get_manager()
await manager.broadcast_event(event)
```

## Performance Considerations

- **Message Rate:** Server aims for <100ms delivery latency
- **Connection Limit:** Nginx configured for 1024 connections/worker
- **Buffering:** No client-side buffering if WebSocket disconnected (use REST for snapshot)
- **Bandwidth:** Estimated ~1KB/event; ~100 events/min at full capacity

## Monitoring

### Health Endpoint

```
GET /api/v1/realtime/health
```

**Response:**
```json
{
  "component": "websocket_manager",
  "active_connections": 25,
  "total_messages": 1543,
  "total_errors": 2,
  "status": "healthy",
  "timestamp": "2026-05-04T10:00:00Z"
}
```

### Connections Count

```
GET /api/v1/realtime/connections
```

**Response:**
```json
{
  "active_connections": 25,
  "timestamp": "2026-05-04T10:00:00Z"
}
```

## Debugging

Enable debug logging in frontend:

```javascript
window.ENV.DEBUG = true;
// Look for [WebSocket] prefixed logs
```

Check backend logs:
```bash
docker logs smartports_backend | grep "\[WS\]"
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-04 | Initial release |

