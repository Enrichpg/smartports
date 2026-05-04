# SmartPort Galicia — System Architecture

**Version:** 1.4 (Iteración 10 - Synthetic Maritime Ecosystem)
**Date:** 2026-05-04
**Status:** Active with Real-Time Layer + Synthetic Data Generation
**Scope:** Multipurpose Galician port network (11+ ports, expandable to 128+)

---

## Executive Summary

**SmartPort Galicia** is a distributed, real-time operational platform for managing a multipurpose Galician port network. It combines:

- **Real-time context layer** (Orion-LD) for live operational state
- **Time-series persistence** (QuantumLeap + TimescaleDB) for historical analytics
- **Operational backend** (FastAPI) for business logic and API
- **Frontend visualization** (Leaflet, Chart.js, Three.js) for dashboards and immersive views
- **Machine Learning** (Prophet, scikit-learn) for forecasting and recommendations
- **Intelligent assistance** (Ollama LLM) for conversational queries

The architecture is designed for **real-time first**, **multipurpose scalability**, and **FIWARE/NGSI-LD compliance** from day one.

---

## 1. Architectural Layers

### Layer Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 0: External Sources                                      │
│  - Sensors (air quality, weather, device status)               │
│  - AIS/MMSI feeds (vessel positions)                           │
│  - Simulators (dev/test data generation)                       │
│  - User inputs (dashboards, web forms)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Message Broker & IoT Ingestion                        │
│  - Mosquitto MQTT (pub/sub for sensors)                        │
│  - IoT Agent JSON (transform MQTT → NGSI-LD)                   │
│  - REST API (alternative ingestion for non-MQTT sources)       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: Context Broker & Time-Series                          │
│  - Orion-LD (NGSI-LD context, current state)                   │
│  - QuantumLeap (time-series subscriptions)                      │
│  - TimescaleDB (persistent time-series storage)                │
│  - MongoDB (flexible document storage if needed)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: Operational Backend                                   │
│  - FastAPI server (REST API, WebSocket, business logic)        │
│  - Domain services (berth management, port calls, etc.)        │
│  - Integrations (Orion queries, QL queries, alerts)            │
│  - Synthetic Maritime Ecosystem generator (4500 vessels)        │
│  - Simulation engine (state machines, observations)            │
│  - Redis (caching, session store, Celery queue)                │
│  - PostgreSQL (operational DB, transactional integrity)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Intelligence, Simulation & ML                         │
│  - Celery workers (async ML + simulation tasks)                │
│  - Simulation tick task (5-min intervals: vessel state + obs)  │
│  - Prophet (occupancy forecasting, Prophet models)             │
│  - scikit-learn (berth recommendation engine)                   │
│  - Ollama (local LLM for chat interface)                        │
│  - Redis (task queue, simulation scheduling)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: Presentation & Visualization                          │
│  - Frontend (HTML, CSS, JavaScript)                            │
│  - Leaflet (geospatial maps)                                   │
│  - Chart.js (analytics charts)                                 │
│  - Three.js (3D visualization)                                 │
│  - Grafana (analytical dashboards)                             │
│  - WebSocket client (real-time sync)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: Infrastructure & DevOps                               │
│  - Docker & Docker Compose (containerization, orchestration)   │
│  - Nginx (reverse proxy, SSL/TLS, rate limiting)               │
│  - Volumes (persistent storage for databases)                  │
│  - Networks (bridge networking, service discovery)             │
│  - Health checks (liveness, readiness, startup probes)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Service Architecture

### 2.1 Service Topology

```
12 Core Services (Docker Compose):

1. mosquitto        - MQTT broker for IoT sensors
2. iot-agent        - IoT Agent JSON (MQTT → NGSI-LD)
3. orion-ld         - Orion-LD context broker (NGSI-LD)
4. quantumleap      - QuantumLeap time-series manager
5. timescaledb      - TimescaleDB (time-series storage)
6. mongodb          - MongoDB (document store)
7. postgres         - PostgreSQL (operational DB)
8. redis            - Redis (cache, task queue)
9. backend          - FastAPI server (business logic, API)
10. celery-worker   - Celery worker (async ML tasks)
11. nginx           - Nginx reverse proxy
12. grafana         - Grafana (analytical dashboards)

Optional:
13. prometheus      - Prometheus metrics scraper
14. ollama          - Ollama LLM runtime
```

### 2.2 Service Responsibilities

| Service | Role | Primary Functions | Internal Ports |
|---------|------|-------------------|----------------|
| **mosquitto** | Message Broker | MQTT pub/sub for sensors, topic routing | 1883 (MQTT), 8883 (TLS) |
| **iot-agent** | IoT Data Transformation | Parse MQTT payloads, transform to NGSI-LD, post to Orion | 4041 (HTTP) |
| **orion-ld** | Context Broker | Store/retrieve NGSI-LD entities, subscriptions, queries | 1026 (HTTP API) |
| **quantumleap** | Time-Series Manager | Subscribe to Orion changes, persist to TimescaleDB, query endpoint | 8668 (HTTP) |
| **timescaledb** | Time-Series DB | Store measurements, observations, time-series data with TimescaleDB extension | 5432 (PostgreSQL) |
| **mongodb** | Document Store | Flexible document storage (metadata, configs, logs) | 27017 |
| **postgres** | Operational DB | Transactional data (operations, users, sessions), referential integrity | 5432 |
| **redis** | Cache & Queue | Session cache, task queue for Celery, temporary data | 6379 |
| **backend** | Core API & Logic | REST API, domain services, WebSocket, Orion/QL integration, alert engine, synthetic data generation | 8000 (HTTP), 8001 (WS) |
| **celery-worker** | Async Processing | ML forecasting, recommendations, background jobs, simulation tick (5-min interval: vessel state + observations) | N/A (broker-based) |
| **nginx** | Reverse Proxy | SSL/TLS termination, rate limiting, request routing, WebSocket upgrade | 80 (HTTP), 443 (HTTPS) |
| **grafana** | Analytics & Dashboards | QL/TS queries, historical analytics, embedded in frontend | 3000 (HTTP) |
| **prometheus** (optional) | Metrics | Scrape metrics from services, alerting infrastructure | 9090 (HTTP) |
| **ollama** (optional) | LLM Runtime | Local Llama model inference, tool calling | 11434 (HTTP) |

---

## 3. Real-Time Data Flow

### 3.1 Complete Real-Time Flow Diagram

```
SENSORS / SIMULATORS (Layer 0)
├─ Air quality sensor
├─ Weather station
├─ AIS feed (vessel positions)
├─ Port gate (berth occupancy)
└─ Operational input (port calls, operations)
         ↓↓↓
    MQTT Topic
    (devices/*, portcalls/*, operations/*)
         ↓
MOSQUITTO MQTT BROKER (Layer 1)
    (topic routing, message buffering)
         ↓↓
IoT Agent JSON (Layer 1)
    Receives MQTT → Transforms to NGSI-LD
    Example:
      {"deviceId": "sensor_01", "temp": 16.5}
      ↓ transform
      {
        "id": "urn:smartdatamodels:AirQualityObserved:CorA:...",
        "type": "AirQualityObserved",
        "temperature": {"value": 16.5, "observedAt": "2026-04-27T10:15:32Z"}
      }
         ↓↓
ORION-LD Context Broker (Layer 2)
    - Receives POST /ngsi-ld/v1/entities from IoT Agent
    - Updates current state (overwrite or merge)
    - Triggers subscriptions (if any)
    - Stores entity graph in-memory + disk
         ↓↓↓ [Subscription]
QUANTUMLEAP (Layer 2)
    - Subscribed to Orion entity updates
    - Receives notification
    - Extracts time-series relevant attributes
    - Writes to TimescaleDB (batch or streaming)
         ↓↓↓
TIMESCALEDB (Layer 2)
    - Stores time-series (measurements, observations)
    - Hypertables for: AirQualityObserved, WeatherObserved, Berth occupancy
    - Retention policy: 3 years
    - Available for QL queries, historical analytics, Grafana
         ↓↓↓ [Event]
BACKEND FastAPI (Layer 3)
    - Polls or subscribes to Orion changes (depending on pattern)
    - Evaluates business rules:
      * Berth occupancy status changes
      * Environmental threshold breaches
      * Port call state transitions
      * Authorization compliance
    - Generates alerts (if thresholds breached)
    - Publishes updates to Redis
    - Broadcasts to WebSocket connections
         ↓↓
REDIS (Layer 3)
    - Stores:
      * Cache: recent entity states
      * Queue: Celery tasks (ML forecasting, recommendations)
      * Pub/Sub: alert messages for WebSocket broadcast
         ↓↓ [WebSocket Pub/Sub]
FRONTEND WebSocket Client (Layer 5)
    - Maintains persistent WebSocket connection to backend
    - Receives real-time updates:
      * Berth status changes
      * New alerts
      * Operational events
      * Vessel position updates
    - Updates UI components without page reload
    - Displays on: Map, table grids, alert banner, dashboard widgets
         ↓↓↓ [Interactive Query]
USER Dashboard (Layer 5)
    - Sees real-time data updated in <2s from sensor
    - Clicks on entity for details (backend queries Orion/QL)
    - Uses chat interface (sends query to backend LLM service)
         ↓↓↓ [LLM Query]
OLLAMA LLM (Layer 4)
    - Receives natural language query
    - Parses intent
    - Calls backend tools:
      * GET /api/ports/occupancy
      * GET /api/vessels?portId=...
      * GET /api/forecasts/occupancy
    - Composes answer in user's language
    - Returns to chat widget
         ↓↓↓ [Forecast Generation - Async]
CELERY WORKER (Layer 4)
    - Scheduled task: Daily occupancy forecasting
    - Queries QL/TimescaleDB for historical 90-day occupancy
    - Trains Prophet model per port
    - Publishes forecast as BoatPlacesAvailable NGSI-LD entity to Orion
    - Updates QuantumLeap, propagates to frontend
```

### 3.2 Latency Budget

| Hop | Component | Typical Latency | Budget |
|-----|-----------|-----------------|--------|
| 1 | Sensor → MQTT publish | <100ms | <100ms |
| 2 | MQTT → IoT Agent parse | <50ms | <50ms |
| 3 | IoT Agent → Orion POST | <200ms | <300ms |
| 4 | Orion → QuantumLeap (subscription) | <100ms | <100ms |
| 5 | QL → TimescaleDB write | <200ms | <200ms |
| 6 | Backend poll Orion OR receive QL webhook | <100ms | <100ms |
| 7 | Backend business logic | <100ms | <100ms |
| 8 | Backend → Redis pub/sub | <10ms | <10ms |
| 9 | Backend → WebSocket broadcast | <50ms | <50ms |
| 10 | WebSocket → Browser receive | <100ms | <100ms |
| 11 | Browser → UI render | <500ms | <500ms |
| | **Total: Sensor to UI** | ~1.5s | **<5s target** ✓ |

---

## 4. Synchronization & Consistency Patterns

### 4.1 Source of Truth

| Data Type | Source of Truth | Consistency Model |
|-----------|-----------------|-------------------|
| **Current State** | Orion-LD (NGSI-LD entities) | Eventual (updates propagate via subscriptions) |
| **Time-Series** | TimescaleDB (via QL subscriptions) | Eventually consistent (async writes) |
| **Operational DB** | PostgreSQL (transactions) | Strong consistency (ACID) |
| **Cache** | Redis (TTL-based) | Eventual (TTL or manual invalidation) |

### 4.2 Update Patterns

**Pattern A: Direct Orion Update** (for infrastructure/configuration)
```
Backend API receives update request
  ↓
Validates input (Pydantic)
  ↓
PUT /ngsi-ld/v1/entities/{id}/attrs to Orion
  ↓
Orion persists, notifies subscribers
  ↓
QuantumLeap receives notification (if time-series relevant)
  ↓
QL writes to TimescaleDB
  ↓
Backend receives QL confirmation / polls Orion
  ↓
Broadcasts via WebSocket
```

**Pattern B: Sensor-Driven Update** (for observations)
```
Sensor publishes to MQTT
  ↓
IoT Agent transforms to NGSI-LD
  ↓
IoT Agent POSTs to Orion
  ↓
Orion updates entity (overwrites or merges observedAt attributes)
  ↓
Orion notifies QuantumLeap (subscription)
  ↓
QL writes to TimescaleDB
  ↓
Backend polls / hooks into Orion → broadcasts WebSocket
  ↓
Frontend updates chart/map
```

**Pattern C: Rule-Driven Alert** (for business logic)
```
Observation arrives (Pattern B)
  ↓
Backend evaluates threshold rules:
  - IF AirQualityObserved.pm25 > 75 THEN create Alert
  ↓
Backend POSTs new Alert entity to Orion
  ↓
Orion stores Alert
  ↓
Backend broadcasts Alert via WebSocket
  ↓
Frontend displays alert banner
  ↓
Alert stored in TimescaleDB via QL (for history)
```

---

## 5. Services & Technologies in Detail

### 5.1 FIWARE Core Services

#### Mosquitto (MQTT Broker)

```yaml
Service: mosquitto
Image: eclipse-mosquitto:latest
Port: 1883 (unsecured), 8883 (TLS)
Purpose: Message broker for IoT sensor data

Topics:
  devices/{deviceId}/temperature
  devices/{deviceId}/airquality
  devices/{deviceId}/position
  portcalls/+/state
  operations/+/status

Config: /config/mosquitto.conf
  - Max connections: 1000
  - Persistence: enabled (disk-backed)
  - Default username: mqtt_user (from .env)
```

#### IoT Agent JSON

```yaml
Service: iot-agent-json
Image: fiware/iotagent-json:latest
Port: 4041
Purpose: Transform MQTT payloads to NGSI-LD

Flow:
  1. Subscribe to MQTT topics
  2. Parse JSON payload from MQTT message
  3. Translate to NGSI-LD entity structure
  4. POST to Orion-LD at configured endpoint
  
Config:
  - Orion endpoint: http://orion-ld:1026
  - MQTT broker: mosquitto:1883
  - Service: smartport
  - Subservice: /galicia
```

#### Real APIs Integration Layer (NEW - Apr 28, 2026)

**Priority:** API-First architecture with Fallback to Simulation

```yaml
Purpose: Integrate real official data sources with realistic simulator fallback

Architecture:
  1. Connectors (API-specific)
     - AEMET Connector: Spanish meteorological service
     - MeteoGalicia Connector: Galician regional weather/ocean data
     - Puertos del Estado Connector: Spanish Port Authority sea conditions
  
  2. Transformers (NGSI-LD conversion)
     - WeatherTransformer: AEMET/MeteoGalicia → WeatherObserved
     - OceanTransformer: Puertos del Estado → SeaConditionObserved
     - AvailabilityTransformer: Simulators → Berth, BoatPlacesAvailable
  
  3. Simulators (Fallback when APIs unavailable)
     - BerthStatusSimulator: Coherent berth occupancy
     - AvailabilitySimulator: Boat places availability
     - VesselSimulator: Realistic vessel positions/status
     - AirQualitySimulator: Plausible air quality data
  
  4. Celery Beat Schedule (Periodic ingestion)
     - ingest_weather_aemet: Every 30 min (real API)
     - ingest_weather_meteogalicia: Every 30 min (real API)
     - ingest_sea_conditions: Every 15 min (real API)
     - ingest_berth_status: Every 5 min (simulator)
     - ingest_availability: Every 5 min (simulator)
     - ingest_vessel_data: Every 1 min (simulator)
     - ingest_air_quality: Every 1 hour (simulator)

Data Provenance:
  - Every entity includes dataProvider and source fields
  - Confidence scores indicate data quality (0-1 scale)
  - "simulator" marked for synthetic data
  - "AEMET", "MeteoGalicia", "Puertos_del_Estado" for real APIs

Files Created:
  - backend/connectors/ (AEMET, MeteoGalicia, PuertosDelEstado)
  - backend/services/transformers/ (Weather, Ocean, Availability)
  - backend/simulators/ (Berth, Availability, Vessel, AirQuality)
  - backend/generators/ (NEW: Synthetic maritime ecosystem, 8 modules)
  - backend/services/simulation_engine.py (NEW: State machine simulation)
  - backend/tasks/simulation_tasks.py (NEW: Celery periodic tick task)
  - backend/tasks/ingest_tasks.py (Celery task definitions)
  - backend/scripts/setup_quantumleap_subscriptions.py (Historical setup)
  - docs/REAL_APIS_INGESTION.md (Comprehensive guide)
  - docs/SYNTHETIC_DATA_ECOSYSTEM.md (NEW: Synthetic data specification)

Configuration (.env):
  - AEMET_API_KEY: API key for AEMET OpenData
  - ENABLE_REAL_DATA_INGESTION: true/false
  - ENABLE_FALLBACK_SIMULATORS: true/false
  - WEATHER_UPDATE_FREQUENCY: 1800 (30 min)
  - OCEAN_CONDITIONS_UPDATE_FREQUENCY: 900 (15 min)
  - BERTH_STATUS_UPDATE_FREQUENCY: 300 (5 min)
```

#### Orion-LD (Context Broker)

```yaml
Service: orion-ld
Image: fiware/orion-ld:latest
Port: 1026
Purpose: NGSI-LD context broker, current state store

Capabilities:
  - CRUD on NGSI-LD entities
  - Subscriptions (notify on entity changes)
  - Queries (GET entities, filter by attributes)
  - Batch operations (bulk create/update)

Persistence:
  - MongoDB backend (for entity storage)
  - In-memory cache for hot entities
  - Subscription event log

API Endpoints:
  - GET /ngsi-ld/v1/entities
  - GET /ngsi-ld/v1/entities/{id}
  - POST /ngsi-ld/v1/entities
  - PUT /ngsi-ld/v1/entities/{id}/attrs
  - POST /ngsi-ld/v1/subscriptions
  - GET /ngsi-ld/v1/subscriptions
```

#### QuantumLeap (Time-Series Manager)

```yaml
Service: quantumleap
Image: smartsdk/quantumleap:latest
Port: 8668
Purpose: Subscribe to Orion changes, persist time-series to TimescaleDB

Flow:
  1. Backend creates subscription in Orion
     - Notification endpoint: http://quantumleap:8668/v2/notify
     - Type: PortCall, Berth, AirQualityObserved, WeatherObserved
  2. When entity changes, Orion notifies QL
  3. QL extracts time-series attributes
  4. QL writes to TimescaleDB (INSERT with timestamp)

Query Endpoints:
  - GET /v2/entities/{entity_id}/attrs/{attr_name}
  - GET /v2/entities?type=AirQualityObserved&fromDate=...&toDate=...
  - Supports time-series aggregations (avg, min, max, sum)

Time Partitioning:
  - Hypertables per entity type
  - Chunks: 1 day (configurable)
  - Compression: enabled (after 7 days)
```

#### TimescaleDB (Time-Series Database)

```yaml
Service: timescaledb
Image: timescale/timescaledb-ha:latest (or pg_timescaledb extension)
Port: 5432 (PostgreSQL protocol)
Purpose: Persistent storage of time-series data

Hypertables:
  - air_quality_observed (refDeviceId, observedAt, pm25, pm10, no2, so2, co, temperature, humidity)
  - weather_observed (refDeviceId, observedAt, temperature, humidity, wind_speed, wind_direction, visibility, precipitation)
  - berth_occupancy (refBerthId, observedAt, occupancyStatus, occupiedBy)
  - vessel_position (refVesselId, observedAt, position (PostGIS), course, speed, eta)
  - operation_events (refOperationId, createdAt, startTime, endTime, quantityHandled)

Features:
  - Automatic data compression (after 7 days)
  - Retention policies (3 years for operational data)
  - Continuous aggregates (hourly, daily rollups for fast dashboards)
  - PostGIS extension (geographic queries)
  - pg_cron (scheduled maintenance)

User: quantumleap_user (for QL writes)
User: analytics_user (for Grafana/backend reads)
```

#### MongoDB (Document Store)

```yaml
Service: mongodb
Image: mongo:7.0
Port: 27017
Purpose: Store Orion entities, flexible document storage

Collections:
  - entities (Orion entity documents)
  - subscriptions (Orion subscription definitions)
  - metadata (port configurations, tariffs, catalogs)
  - logs (audit logs, debug traces)

Persistence:
  - WiredTiger engine (default)
  - Volume mount for data durability
```

### 5.2 Operational Backend

#### FastAPI Server

```yaml
Service: backend
Image: smartport/backend:latest (custom Dockerfile)
Port: 8000 (REST API), 8001 (WebSocket)
Purpose: Core operational logic, API, WebSocket server

Architecture:
  - Pydantic models (request/response validation)
  - SQLAlchemy ORM (PostgreSQL ORM layer)
  - httpx async client (Orion/QL integration)
  - starlette.websockets (real-time sync)
  - logging (structured logs to stdout)

Key Modules:
  backend/
  ├── app/
  │   ├── main.py (FastAPI app initialization)
  │   ├── core/
  │   │   ├── config.py (settings from .env)
  │   │   ├── security.py (JWT, RBAC)
  │   │   └── logger.py (logging config)
  │   ├── models/
  │   │   ├── entities.py (Pydantic schemas for NGSI-LD)
  │   │   ├── database.py (SQLAlchemy models)
  │   │   └── requests.py (API request models)
  │   ├── services/
  │   │   ├── orion.py (Orion-LD integration, CRUD on entities)
  │   │   ├── quantumleap.py (QL time-series queries)
  │   │   ├── port_service.py (port operations, KPIs)
  │   │   ├── berth_service.py (berth availability, recommendation)
  │   │   ├── portcall_service.py (port call lifecycle)
  │   │   ├── alert_service.py (threshold rules, alert generation)
  │   │   └── ml_service.py (forecast/recommendation requests)
  │   ├── api/
  │   │   ├── routes.py (main routes)
  │   │   ├── ports.py (GET /ports, /ports/{id}, /ports/{id}/occupancy)
  │   │   ├── berths.py (GET /berths, POST /berths/recommend)
  │   │   ├── portcalls.py (GET /portcalls, POST /portcalls, PUT /portcalls/{id}/state)
  │   │   ├── operations.py (GET /operations, POST /operations)
  │   │   ├── vessels.py (GET /vessels, GET /vessels/{id}/position)
  │   │   ├── alerts.py (GET /alerts, POST /alerts/acknowledge)
  │   │   ├── analytics.py (GET /analytics/occupancy, /analytics/dwell-time)
  │   │   └── health.py (GET /health, /ready)
  │   └── websocket/
  │       └── manager.py (WebSocket connection pool, broadcast)
  └── tests/
      ├── test_services.py (unit tests)
      ├── test_api.py (integration tests)
      └── test_orion.py (Orion integration tests)

Endpoints (RESTful):
  GET /health                 → Service health
  GET /ports                  → List all ports
  GET /ports/{portId}         → Port details + KPIs
  GET /ports/{portId}/occupancy   → Current occupancy QL query
  GET /berths?portId=...      → List berths (with availability)
  POST /berths/recommend      → ML berth recommendation
  POST /portcalls             → Create new port call
  GET /portcalls              → List port calls
  PUT /portcalls/{id}/state   → Transition port call state
  POST /operations            → Log operational event
  GET /alerts?severity=...    → List alerts
  POST /alerts/{id}/acknowledge  → Mark alert resolved
  GET /analytics/occupancy    → Historical occupancy trend (QL query)
  GET /forecasts/occupancy    → 7-day occupancy forecast (from Redis or Orion)

WebSocket Endpoint:
  WS /ws                      → Connect for real-time updates
  Messages:
    {"type": "berth_status", "berth": "CorA:A1", "status": "occupied"}
    {"type": "alert", "severity": "critical", "description": "..."}
    {"type": "vessel_position", "vessel": "imo9876543", "position": [-8.389, 43.371]}
    {"type": "operation_update", "operationId": "...", "status": "completed"}
```

#### PostgreSQL (Operational DB)

```yaml
Service: postgres
Image: postgres:15
Port: 5432
Purpose: Transactional database for operational data (non-time-series)

Schema:
  - users (operators, managers, admins)
  - sessions (active user sessions, JWT tokens)
  - authorization_rules (threshold configurations per port)
  - tariff_overrides (temporary pricing changes)
  - audit_log (who did what, when)

Connection Pool:
  - Max connections: 20
  - Min idle: 2
  - Timeout: 30s

Backups:
  - Daily at 02:00 UTC
  - Retention: 30 days
  - Backup path: /backups/postgres/
```

#### Redis (Cache & Queue)

```yaml
Service: redis
Image: redis:7.0
Port: 6379
Purpose: Cache, session store, Celery task queue

Data Structures:
  - Strings: user sessions, entity caches
  - Hashes: entity snapshots
  - Lists: Celery task queue
  - Pub/Sub: real-time alert broadcasts

TTLs:
  - Session: 24 hours
  - Entity cache: 5 minutes
  - Forecast cache: 1 hour

Task Queue (Celery):
  - Queue name: celery
  - Task types: forecast_occupancy, recommend_berth, send_alert_notification
```

### 5.3 Machine Learning & Intelligence

#### Celery Workers

```yaml
Service: celery-worker
Image: smartport/backend:latest
Command: celery -A app.tasks worker --loglevel=info
Purpose: Asynchronous ML tasks

Tasks:
  1. forecast_occupancy(port_id, days=7)
     - Queries QL for 90-day occupancy history
     - Trains Prophet model
     - Generates 7-day forecast
     - Posts BoatPlacesAvailable.forecast7Day to Orion
     - Scheduled: Daily at 06:00 UTC

  2. recommend_berth(vessel_id, port_id, services=[...])
     - Queries Orion for available Berths
     - Loads pre-trained Random Forest model
     - Scores berths on: availability, service match, vessel fit, efficiency
     - Returns ranked list
     - Triggered on: Operator request via API

Execution:
  - Broker: Redis (redis://redis:6379/0)
  - Backend: redis
  - Concurrency: 4 workers per instance
```

#### Ollama LLM

```yaml
Service: ollama
Image: ollama/ollama:latest
Port: 11434
GPU: Optional (NVIDIA GPU mount if available)
Model: Llama 2 (7B or 13B variant, loaded on startup)
Purpose: Natural language understanding, tool calling

Chat Endpoint:
  POST /api/chat
  Request: {"model": "llama2", "messages": [{"role": "user", "content": "..."}]}
  
Tool Calling:
  The LLM can call backend functions registered as tools:
    - get_port_occupancy(port_id)
    - get_berth_availability(port_id, type=...)
    - get_forecast_occupancy(port_id)
    - get_vessel_position(vessel_id)
    - query_alerts(severity=...)
  
  Example query → response chain:
    User: "¿Qué puertos tienen la ocupación más alta?"
    → LLM: Call get_port_occupancy() for all ports
    → Backend returns: {"CorA": 92, "Vigo": 78, "Ferrol": 65}
    → LLM: "Vigo tiene la ocupación más alta: 92%"
```

### 5.4 Visualization & Frontend

#### Leaflet Map

```html
<!-- Frontend hosted by Nginx -->
<!-- Leaflet with OpenStreetMap tiles -->

<div id="map"></div>
<script>
  const map = L.map('map').setView([43.0, -8.5], 8);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  // Ports as markers
  // Berths as polygons with occupancy color
  // Vessels as animated icons (updated via WebSocket)
  // Sensors as layer toggles
  // Click → drill into detailed view
</script>
```

#### Dashboard Components

```
Frontend views (via HTML/CSS/JavaScript):
  1. Global Port Network Map
     - All 11 ports visible
     - Real-time KPI badges (occupancy %, alerts)
     - Click port → detail view
  
  2. Port Detail Dashboard
     - Port info (authority, address, contact)
     - Berth grid (occupancy status, ETA/ETD)
     - Active vessels list
     - Active operations
     - Environmental conditions (air quality, weather)
     - Recent alerts (latest 10)
  
  3. Occupancy Chart (Chart.js)
     - X: time (hourly, daily, weekly)
     - Y: occupancy %
     - 7-day forecast (dashed line with CI)
     - Compare across ports
  
  4. 3D Port Visualization (Three.js)
     - 3D model of port layout
     - Berths as interactive boxes
     - Vessels with correct dimensions
     - Sensors as points
     - Click → details
  
  5. LLM Chat Widget
     - Text input box
     - Chat history
     - Tool calling (backend responds)
  
  6. Embedded Grafana
     - Historical analytics from QL/TimescaleDB
     - Pre-built dashboards for different roles
     - Custom dashboard builder
  
  All views update via WebSocket in real-time (<2s)
```

#### Grafana Dashboards

```yaml
Service: grafana
Image: grafana/grafana:latest
Port: 3000
Purpose: Historical analytics, KPIs, real-time monitoring

Data Source:
  - QuantumLeap (time-series queries)
  - TimescaleDB (direct SQL queries for advanced analytics)

Pre-built Dashboards:
  1. Operations Dashboard (for port managers)
     - Occupancy trend (7 days)
     - Dwell time statistics (min, avg, max)
     - Operational volume (cargo tonnage)
     - Revenue KPI
     - Comparison: this port vs. others
  
  2. Environmental Dashboard
     - Air quality index over time
     - Weather trends
     - Alert history
  
  3. System Health Dashboard
     - API response times
     - Celery task success rate
     - Database connections
     - Disk usage
     - Error rates
```

### 5.5 Reverse Proxy & TLS

#### Nginx Configuration

```yaml
Service: nginx
Image: nginx:alpine
Port: 80 (HTTP → 443 redirect), 443 (HTTPS)
Purpose: Reverse proxy, SSL/TLS termination, rate limiting, static file serving

Config (/config/nginx.conf):
  - SSL certificate (from Let's Encrypt or self-signed)
  - Rate limiting: 100 req/min per IP
  - CORS headers (if applicable)
  - WebSocket upgrade (Connection: upgrade, Upgrade: websocket)
  - Caching headers (static files: 1 day, API: no-cache)
  - Compression (gzip on)

Upstream Services:
  - backend: http://backend:8000 (REST API)
  - grafana: http://grafana:3000 (analytics dashboards)
  - orion-ld: http://orion-ld:1026 (context broker, optional expose)

Routes:
  /api/*                    → backend:8000 (REST API)
  /api/v1/realtime/ws       → backend:8000 (WebSocket upgrade)
  /ngsi-ld/*                → orion-ld:1026 (context broker, optional)
  /ql/*                     → quantumleap:8668 (time-series API, optional)
  /grafana/*                → grafana:3000
  /prometheus/*             → prometheus:9090
  /iot/*                    → iot-agent-json:4041
  /health                   → backend:8000/health
  / (static assets)         → nginx file serving (frontend)
```

### 5.6 Prometheus (Optional Monitoring)

```yaml
Service: prometheus
Image: prom/prometheus:latest
Port: 9090
Purpose: Metrics scraping, alerting infrastructure

Targets:
  - Backend FastAPI (http://backend:8000/metrics)
  - Orion-LD (http://orion-ld:1026/metrics, if available)
  - TimescaleDB (via postgres_exporter, optional)
  - Redis (via redis_exporter, optional)

Metrics Collected:
  - http_requests_total
  - http_request_duration_seconds
  - database_connection_count
  - celery_task_duration_seconds
  - cache_hit_ratio
  - orion_entity_count (custom metric)

Alerts:
  - High error rate (>5%)
  - Service unavailable
  - Database connection pool exhausted
  - Celery task backlog growing
```

### 5.7 Realtime Infrastructure (Iteration 2)

This section describes the realtime infrastructure added in Iteration 2 for live event streaming, audit logging, caching, and async task processing.

#### WebSocket Server

```yaml
Endpoint: /api/v1/realtime/ws
Protocol: WebSocket (upgraded from HTTP)
Purpose: Real-time event streaming to clients

Features:
  - Multiple concurrent connections (1000+ supported)
  - Subscription filtering (by port, entity type, event)
  - Automatic reconnection support
  - Message type routing (event, ping/pong, subscribe/unsubscribe)
  - Connection lifecycle management

Message Format (Event):
  {
    "type": "event",
    "data": {
      "event": "berth.updated",
      "timestamp": "2026-04-28T14:00:00Z",
      "entity": {"type": "Berth", "id": "urn:ngsi-ld:Berth:coruna:berth-001"},
      "scope": {"port_id": "urn:ngsi-ld:Port:coruna"},
      "payload": {"status": "occupied", "previous_status": "reserved"}
    }
  }

Event Types Supported:
  - berth.updated
  - portcall.created, portcall.updated, portcall.closed
  - alert.created, alert.updated
  - availability.updated
  - port.summary.updated
  - authorization.validation.failed
```

#### Audit Logging (PostgreSQL)

```yaml
Database: postgres (same as operational DB)
Tables:
  - audit_log: Main audit trail for all operations
  - task_execution_log: Background task execution history
  - authentication_log: Authorization check history

Features:
  - Structured JSONB snapshots (before/after state)
  - Correlation ID linking (trace related events)
  - Port-scoped queries
  - Timestamp UTC, TTL-based retention (90 days default)
  - Actor tracking (who/what triggered action)

REST Endpoints:
  GET /api/v1/admin/audit - Query audit logs with filters
  GET /api/v1/admin/audit/{entity_type}/{entity_id} - Entity history
  GET /api/v1/admin/audit/port/{port_id} - Port operations history

Use Cases:
  - Compliance & regulatory audits
  - Operational troubleshooting
  - Security incident investigation
  - Change tracking (who modified what, when)
```

#### Redis Cache Layer

```yaml
Service: redis
Database Allocation:
  - DB 0: General cache (port summaries, availability, alerts)
  - DB 1: Celery broker queue
  - DB 2: Celery result backend

Cache Keys & TTLs:
  - port:summary:{port_id} (600s) - Port overview, KPIs
  - port:availability:{port_id} (600s) - Berth availability by category
  - port:alerts:active:{port_id} (300s) - Active alerts for port
  - dashboard:galicia:overview (600s) - Global KPI aggregates
  - port:berths:{port_id} (600s) - Berth list and status

Invalidation Strategy:
  - Event-driven: On entity change, invalidate related caches
  - Pattern-based: Delete all keys matching port:* when port summary changes
  - TTL-based: Automatic expiration

REST Endpoints:
  GET /api/v1/admin/cache/health - Cache memory, connection status
  DELETE /api/v1/admin/cache/invalidate?pattern=port:* - Manual invalidation
  POST /api/v1/admin/cache/warm/{key_type}/{resource_id} - Pre-populate cache

Graceful Degradation:
  - If Redis unavailable, backend continues operating
  - Cache requests return None, services fall back to DB queries
  - No user-facing errors; transparently slower
```

#### Celery Background Tasks

```yaml
Broker: Redis (DB 1)
Result Backend: Redis (DB 2)
Worker Image: Same as backend (backend service with Celery command override)

Task Categories:

1. Domain Tasks (domain_tasks.py):
   - recalculate_port_availability(port_id)
   - check_port_alerts(port_id)
   - refresh_port_summary_cache(port_id)
   - broadcast_port_summary_update(port_id)
   - orchestrate_berth_status_change(port_id, berth_id)
   - orchestrate_portcall_lifecycle(portcall_id, event_type)

2. Cache Tasks (cache_tasks.py):
   - warm_cache_key(key, ttl, data)
   - invalidate_cache_pattern(pattern)
   - periodic_cache_maintenance()

3. Alert Tasks (alert_tasks.py):
   - analyze_port_conditions(port_id)
   - check_vessel_authorization_issues(port_id)
   - check_berth_utilization(port_id)
   - generate_operational_report(port_id, period_hours)
   - cleanup_expired_alerts()

4. Ingest Tasks (existing):
   - ingest_weather_data(port_id)
   - ingest_air_quality_data(port_id)

Execution Model:
  - Sync endpoint: Validates & persists critical data (berth status, port call creation)
  - Async orchestration: Launches task chain after successful operation
  - Correlation ID: Links original request to all downstream tasks

Example Flow (Berth Status Change):
  1. PATCH /api/v1/berths/{berth_id}/status (sync, returns 200)
     - Validates authorization
     - Updates berth status in DB
     - Emits event via WebSocket
  2. Event triggers Celery task chain (async):
     - recalculate_port_availability(port_id) 
     - check_port_alerts(port_id)
     - refresh_port_summary_cache(port_id)
     - broadcast_port_summary_update(port_id)
  3. Each task can log to audit_log and emit derived events
  4. Frontend receives updates via WebSocket as tasks complete

Task Timeouts:
  - Hard limit: 30 minutes (1800s)
  - Soft limit: 25 minutes (1500s)
  - Retry: 3 attempts with exponential backoff

REST Endpoints:
  GET /api/v1/admin/tasks/{task_id} - Check task status
  POST /api/v1/admin/tasks/check-alerts/{port_id} - Manual alert check
  POST /api/v1/admin/tasks/recalculate-availability/{port_id} - Manual recalc

Configuration (.env):
  CELERY_BROKER_URL=redis://...:6379/1
  CELERY_RESULT_BACKEND=redis://...:6379/2
  CELERY_CONCURRENCY=4 (number of worker processes)
  CELERY_WORKER_LOG_LEVEL=info
```

#### Event Bus (Internal Pub/Sub)

```yaml
Purpose: Decouple event publication from WebSocket, audit, and task execution

Components:
  - Publisher: Services create events via event_bus.publish(...)
  - Subscribers:
    * WebSocket manager (broadcasts to connected clients)
    * Audit service (logs to PostgreSQL)
    * Celery orchestrator (triggers background tasks)

Event Publishing API:
  await event_bus.publish(
    event_type="berth.updated",
    entity_type="Berth",
    entity_id="berth-1",
    port_id="port-a",
    payload={"status": "occupied"},
    correlation_id="req-123"
  )

  # Or use typed helpers:
  await event_bus.publish_berth_updated(berth_id, port_id, status)
  await event_bus.publish_portcall_created(portcall_id, port_id, vessel_id, payload)
  await event_bus.publish_alert_created(alert_id, port_id, alert_type, payload)
  # ... etc

Hook Registration:
  event_bus.subscribe_audit(audit_callback)      # Receives all events for logging
  event_bus.subscribe_tasks(task_orchestrator)   # Receives events for task triggering

Benefits:
  - Separation of concerns (event publication ≠ broadcast/audit/tasks)
  - Easy to extend (add new hooks without touching publishing code)
  - Non-blocking (hooks run async, don't block the request)
  - Testable (can mock publishers/subscribers independently)
```

#### Integration with Existing Services

All domain services (berth_service.py, portcall_service.py, alert_service.py, etc.) integrate with realtime infrastructure as follows:

```python
# Example: berth_service.py

async def update_berth_status(berth_id: str, status: str):
    # 1. Validate and persist
    berth = await db.update_berth(berth_id, status)
    
    # 2. Emit event
    await event_bus.publish_berth_updated(
        berth_id=berth_id,
        port_id=berth.port_id,
        status=status,
        previous_status=berth.previous_status,
        correlation_id=context_id,  # Trace back to original request
    )
    
    # 3. Audit is logged automatically by event_bus
    # 4. WebSocket clients receive update automatically
    # 5. Celery tasks triggered automatically (recalc, alerts, etc.)
    
    return berth
```

---

## 6. Data Flow Diagrams

### 6.1 Port Call Lifecycle with Real-Time Updates

```
T0: Port Call Created (via API or external system)
   Backend POST /portcalls
   → Create PortCall entity in Orion
   → QL subscription triggered (PortCall created)
   → Backend broadcasts via WebSocket: "new_portcall"
   → Dashboard adds row to table, marks with "expected" status
   
T1: Vessel Arrives (AIS position update)
   Sensor publishes: {"deviceId": "ais", "vesselId": "9876543", "lat": 43.371, "lon": -8.389}
   → MQTT → IoT Agent → Orion (Vessel entity position updated)
   → QL stores position to TimescaleDB
   → Backend detects arrival → transitions PortCall.state to "active"
   → Backend creates/updates Berth.occupancyStatus = "occupied"
   → WebSocket broadcast: occupancy status changed
   → Dashboard highlights port/berth as occupied, shows ETA/ETD
   
T2-T3: Operations Logged (cargo unloading)
   Operator submits operation via mobile form
   → Backend POST /operations
   → Create Operation entity in Orion
   → QL stores operation events to TimescaleDB
   → WebSocket broadcast: operation_started
   → Dashboard updates operations list, shows cargo tonnage
   
T4: Vessel Departs (AIS movement away)
   Sensor publishes: vessel position outside port boundaries
   → Backend detects departure
   → Transitions PortCall.state to "completed"
   → Updates Berth.occupancyStatus = "free"
   → Calculates dwell time = departure - arrival
   → WebSocket broadcast: berth now free, dwell time calculated
   → Dashboard removes from active, adds to history
   
T5+: Historical Analysis
   QL stores all observations
   Analyst queries: "Show me occupancy trend for CorA this month"
   → Backend queries QL with time range
   → QL returns aggregated hourly occupancy
   → Grafana renders chart
   → ML: forecast next month's occupancy (Celery task scheduled daily)
```

### 6.2 Alert Generation & Propagation

```
Sensor triggers threshold:
  Air quality sensor measures PM2.5 = 42.5 µg/m³
  Threshold config: IF pm25 > 35 THEN alert("warning")
  
T0: Measurement arrives
  MQTT → IoT Agent → Orion (AirQualityObserved.pm25 = 42.5)
  
T1: Backend evaluates rules
  Orion notifies QL (QL stores to TimescaleDB)
  Backend polls Orion OR receives webhook from QL
  Backend loads rules: SELECT * FROM authorization_rules WHERE metric = "pm25" AND port = "CorA"
  Backend logic: IF 42.5 > 35 THEN create Alert
  
T2: Alert created
  Backend POSTs new Alert entity to Orion
  Alert ID: urn:smartdatamodels:Alert:CorA:alert_20260427_101500
  Alert fields:
    - alertType: "environmental"
    - severity: "warning"
    - description: "PM2.5 exceeds threshold"
    - refEntity: Port:Galicia:CorA
    - refDevice: Device:CorA:aq_sensor_01
    - status: "active"
  
T3: QL stores Alert
  Orion notifies QL (subscription to Alert type)
  QL writes Alert to TimescaleDB
  
T4: Broadcast to frontend
  Backend publishes to Redis channel: alerts
  WebSocket listener receives and broadcasts to all connected clients
  Frontend receives: {"type": "alert", "severity": "warning", "description": "..."}
  
T5: UI updates
  Alert banner appears (red/yellow background)
  Alert list table gets new row
  User clicks alert → sees details, acknowledges
  Backend updates Alert.status = "acknowledged"
  Alert removed from active list (moved to history)
```

---

## 7. Deployment Architecture

### 7.1 Docker Compose Orchestration

```yaml
# docker-compose.yml
# 12 services, all defined in one compose file

Services:
  - mosquitto
  - iot-agent-json
  - orion-ld
  - quantumleap
  - timescaledb
  - mongodb
  - postgres
  - redis
  - backend
  - celery-worker
  - nginx
  - grafana
  (optional: prometheus, ollama)

Networks:
  - default (docker bridge)
  
Volumes:
  - mosquitto_data
  - orion_data
  - quantumleap_data
  - timescaledb_data
  - mongodb_data
  - postgres_data
  - redis_data
  - nginx_config
  - grafana_data
  - ollama_models (optional)

Environment:
  - All services read from .env file
  - No hardcoded secrets
  - Development & production variants
```

### 7.2 Health Checks

```yaml
# All services include healthchecks in docker-compose.yml

Backend (FastAPI):
  test: curl -f http://localhost:8000/health
  interval: 10s
  timeout: 5s
  retries: 3

Orion-LD:
  test: curl -f http://localhost:1026/version
  interval: 10s
  timeout: 5s

QuantumLeap:
  test: curl -f http://localhost:8668/version
  interval: 15s
  timeout: 5s

PostgreSQL:
  test: pg_isready -U postgres
  interval: 10s
  timeout: 5s

Redis:
  test: redis-cli ping
  interval: 10s
  timeout: 5s

Mosquitto:
  test: mosquitto_sub -h localhost -t test | head -n 1 || false
  interval: 10s
  timeout: 5s
```

---

## 8. Configuration Management

### 8.1 Environment Variables (.env file)

```bash
# .env.example (all non-secret template vars)

# FIWARE Services
ORION_HOST=orion-ld
ORION_PORT=1026
ORION_SERVICE=smartport
ORION_SUBSERVICE=/galicia

QUANTUMLEAP_HOST=quantumleap
QUANTUMLEAP_PORT=8668

IOT_AGENT_HOST=iot-agent-json
IOT_AGENT_PORT=4041

MOSQUITTO_HOST=mosquitto
MOSQUITTO_PORT=1883
MOSQUITTO_USER=mqtt_user
MOSQUITTO_PASSWORD=<SET_IN_PRODUCTION>

# Databases
POSTGRES_USER=smartport_user
POSTGRES_PASSWORD=<SET_IN_PRODUCTION>
POSTGRES_DB=smartport
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

TIMESCALEDB_HOST=timescaledb
TIMESCALEDB_PORT=5432
TIMESCALEDB_USER=quantumleap_user
TIMESCALEDB_PASSWORD=<SET_IN_PRODUCTION>

MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USER=orion_user
MONGODB_PASSWORD=<SET_IN_PRODUCTION>

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<SET_IN_PRODUCTION>

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DEBUG=false (true only in dev)
BACKEND_LOG_LEVEL=INFO
JWT_SECRET_KEY=<SET_IN_PRODUCTION>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Machine Learning
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
PROPHET_FORECAST_DAYS=7
PROPHET_RETRAIN_SCHEDULE="0 6 * * *" (daily at 6 AM UTC)

# Ollama (optional LLM)
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=llama2:13b

# Grafana
GRAFANA_ADMIN_PASSWORD=<SET_IN_PRODUCTION>
GRAFANA_HOST=grafana
GRAFANA_PORT=3000

# Nginx
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
NGINX_SSL_CERT_PATH=/etc/nginx/certs/cert.pem
NGINX_SSL_KEY_PATH=/etc/nginx/certs/key.pem

# Application Settings
SITE_NAME=SmartPort Galicia Operations Center
SITE_URL=https://smartport.galicia.example.com
CORS_ORIGINS=["https://smartport.galicia.example.com"]

# Ports (Galician ports to populate)
PILOT_PORTS=CorA,Vigo,Ferrol,Marin,Vilagarcia,Ribeira,Burela,Celeiro,Cangas,Baiona,Viveiro
```

### 8.2 Configuration Layers

```python
# backend/app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # FIWARE
    orion_host: str = "orion-ld"
    orion_port: int = 1026
    
    # Databases
    postgres_url: str = "postgresql://..."
    redis_url: str = "redis://..."
    
    # Backend
    debug: bool = False
    api_title: str = "SmartPort Galicia API"
    
    # Security
    jwt_secret_key: str  # Required from .env
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 9. Architectural Decisions & Rationale

### Decision 1: Orion-LD as Single Source of Truth for Current State

**Decision:** Current operational state (live Berths, Vessels, PortCalls, Alerts) lives in Orion-LD, not a traditional RDBMS.

**Rationale:**
- ✓ NGSI-LD compliance from day 1
- ✓ Graph-like relationships native (Relationship type)
- ✓ Subscriptions enable real-time propagation
- ✓ Loose schema allows flexible attributes
- ✓ Integration with FIWARE ecosystem

**Trade-off:**
- ✗ Eventual consistency (not ACID)
- ✗ Querying less powerful than SQL (no complex JOINs)
- *Mitigation:* Use PostgreSQL for transactional operations (users, sessions), QL for time-series queries

### Decision 2: Async Time-Series via QL Subscriptions

**Decision:** Use QuantumLeap subscriptions (not polling) to persist observations to TimescaleDB.

**Rationale:**
- ✓ Real-time push model (low latency)
- ✓ Scales with sensor count
- ✓ Decouples Orion from DB write load
- ✓ Native FIWARE pattern

**Trade-off:**
- ✗ Requires subscription setup
- *Mitigation:* Subscription manager in backend setup phase

### Decision 3: FastAPI as Operational Backend

**Decision:** Single FastAPI server (not separate backend + API layer) for simplicity and performance.

**Rationale:**
- ✓ Async-native (handles WebSocket + MQTT → Orion concurrency)
- ✓ Pydantic validation built-in
- ✓ OpenAPI docs auto-generated
- ✓ Light enough for multipurpose model
- ✓ Easy to scale horizontally

**Trade-off:**
- ✗ Single point of failure (mitigation: run multiple instances behind load balancer)

### Decision 4: WebSocket for Real-Time Frontend Updates

**Decision:** WebSocket connections for pushing updates to UI (not polling).

**Rationale:**
- ✓ Low latency (<200ms)
- ✓ Scales to 100+ concurrent users
- ✓ Bi-directional (UI can send commands too)
- ✓ Reduces server load vs. polling

**Trade-off:**
- ✗ Stateful connections (need connection pool, reconnection logic)
- *Mitigation:* Starlette WebSocketManager (built-in)

### Decision 5: Celery + Redis for Async ML Tasks

**Decision:** Separate Celery workers for ML (forecast, recommendation), not inline in request handler.

**Rationale:**
- ✓ Long-running tasks don't block API
- ✓ Scalable: add workers as needed
- ✓ Retryable (if worker fails, task retried)
- ✓ Scheduled tasks (daily forecast)

**Trade-off:**
- ✗ Complexity: task coordination, monitoring
- *Mitigation:* Flower dashboard for monitoring

### Decision 6: Embedded Ollama LLM (Not Cloud API)

**Decision:** Run Ollama locally (Llama 2 7B) instead of calling OpenAI/Anthropic APIs.

**Rationale:**
- ✓ No API costs
- ✓ Data privacy (queries stay local)
- ✓ No external dependency (works offline)
- ✓ Customizable prompts for domain knowledge

**Trade-off:**
- ✗ Lower quality than GPT-4 (Llama 2 is good but not best-in-class)
- ✗ Requires GPU for fast inference (~2s response time on CPU)
- *Mitigation:* Tool calling (LLM retrieves data from backend, doesn't hallucinate)

### Decision 7: Nginx Reverse Proxy (Not API Gateway)

**Decision:** Use Nginx (not Kong, AWS ALB, etc.) for simplicity.

**Rationale:**
- ✓ Lightweight, fast
- ✓ WebSocket upgrade built-in
- ✓ Rate limiting simple
- ✓ SSL/TLS termination standard
- ✓ Easy configuration

**Trade-off:**
- ✗ No built-in auth policies (handled by backend)
- *Mitigation:* OK for internal ports, restrict network access

### Decision 8: TimescaleDB (Not Pure PostgreSQL or InfluxDB)

**Decision:** Use TimescaleDB (PostgreSQL extension) for time-series.

**Rationale:**
- ✓ Native PostgreSQL (no new language/client)
- ✓ Advanced time-series features (hypertables, compression, continuous aggregates)
- ✓ SQL queries (familiar for developers)
- ✓ Geographic queries via PostGIS
- ✓ Grafana native support

**Trade-off:**
- ✗ Not as specialized as InfluxDB/Prometheus
- *Mitigation:* Good enough for SmartPort use case

---

## 10. High Availability & Disaster Recovery

### 10.1 Service Redundancy (Future)

```
Current (Phase 1):
  - Single instance deployment
  - Local volumes (no replication)
  
Future (Phase 2+):
  - Backend: run 2+ instances behind load balancer
  - Orion-LD: deploy with MongoDB replica set
  - QuantumLeap: multi-instance with shared QL backend
  - TimescaleDB: streaming replication to standby
  - Redis: sentinel-managed primary + replica
  - Nginx: keepalived + virtual IP (active-passive)
```

### 10.2 Backup & Recovery

```
Backups:
  - Database backups: Daily at 02:00 UTC
    * pg_dump for PostgreSQL (1 hour retention)
    * mongodump for MongoDB (1 hour retention)
    * Compressed and uploaded to cloud storage (weekly + monthly archives)
  
  - Configuration backups: Versioned in Git
  
  - Docker images: Tagged by date, pushed to registry

Recovery:
  - RTO (Recovery Time Objective): 4 hours
  - RPO (Recovery Point Objective): 1 hour
  - Procedure: Documented in runbooks/DISASTER_RECOVERY.md
```

---

## 11. Performance Targets

### 11.1 Benchmarks

| Metric | Target | Current* | Status |
|--------|--------|---------|--------|
| API response time (p95) | <500ms | TBD | Baseline needed |
| Real-time latency (sensor to UI) | <5s | TBD | To validate |
| WebSocket throughput | 1000 msg/s | TBD | Load test needed |
| Forecast generation time | <5 min | TBD | To measure |
| ML recommendation latency | <2s | TBD | To measure |
| LLM chat response | <3s | TBD | To measure |
| Database query (QL 1M points) | <10s | TBD | To tune |

*To be measured during Phase 2-3

### 11.2 Scaling Roadmap

```
Phase 1 (Single instance):
  - 11 ports
  - 1000+ berths
  - 100+ concurrent users
  - 1000 sensors
  - 10k daily port calls
  
Phase 2 (Horizontal scaling):
  - Backend: 3 instances
  - Worker: 2 instances
  - Databases: Replicated
  - Nginx: HA
  
Phase 3 (Kubernetes):
  - HPA (Horizontal Pod Autoscaling)
  - Multiple replicas per service
  - Geographic distribution
```

---

## 12. Monitoring & Observability

### 12.1 Logging Strategy

```
All services output structured logs to stdout (JSON format):

{
  "timestamp": "2026-04-27T10:15:32Z",
  "level": "INFO",
  "service": "backend",
  "component": "berth_service",
  "message": "Berth occupancy updated",
  "context": {
    "berth_id": "urn:smartdatamodels:Berth:CorA:A1",
    "status": "occupied",
    "port_id": "CorA"
  },
  "duration_ms": 45
}

Aggregation (future):
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Fluent-bit or Filebeat as forwarder
  - Retention: 30 days
```

### 12.2 Metrics (Prometheus format)

```
Key metrics exposed by backend at GET /metrics:

# HELP smartport_api_requests_total Total API requests
# TYPE smartport_api_requests_total counter
smartport_api_requests_total{method="GET",path="/ports",status="200"} 1542

# HELP smartport_api_request_duration_seconds API request duration
# TYPE smartport_api_request_duration_seconds histogram
smartport_api_request_duration_seconds_bucket{path="/ports",le="0.5"} 1200

# HELP smartport_orion_query_duration_seconds Orion query latency
# TYPE smartport_orion_query_duration_seconds histogram
smartport_orion_query_duration_seconds_bucket{entity_type="Berth",le="0.1"} 89

# HELP smartport_entities_in_orion Current entity count
# TYPE smartport_entities_in_orion gauge
smartport_entities_in_orion{type="Berth",port="CorA"} 256
smartport_entities_in_orion{type="Vessel",port="CorA"} 45

# HELP smartport_websocket_connections Active WebSocket connections
# TYPE smartport_websocket_connections gauge
smartport_websocket_connections 87

# HELP smartport_celery_task_duration_seconds ML task execution time
# TYPE smartport_celery_task_duration_seconds histogram
smartport_celery_task_duration_seconds_bucket{task="forecast_occupancy",le="5"} 45
```

### 12.3 Alerting (Prometheus AlertManager + Grafana)

```
Alert Rules:

  - name: HighAPIErrorRate
    expr: rate(smartport_api_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "API error rate >5%"
  
  - name: OrionContextBrokerDown
    expr: up{job="orion-ld"} == 0
    for: 1m
    annotations:
      summary: "Orion-LD is down"
  
  - name: QuantumLeapLag
    expr: (time() - smartport_quantumleap_last_notification_timestamp) > 300
    for: 5m
    annotations:
      summary: "QL hasn't received notification in 5+ minutes"
  
  - name: TimescaleDBConnectionPoolExhausted
    expr: smartport_timescaledb_connections >= 20
    for: 1m
    annotations:
      summary: "DB connection pool exhausted"
  
  - name: CeleryTaskBacklogGrowing
    expr: rate(smartport_celery_tasks_waiting[5m]) > 10
    for: 10m
    annotations:
      summary: "Celery queue backlog growing (>10 tasks/sec)"
```

---

## 13. Architectural Constraints & Trade-Offs

### 13.1 Constraints

1. **NGSI-LD Compliance**: All data models must follow NGSI-LD v1.6 (no NGSIv2)
2. **Multipurpose Design**: Architecture must scale to 11+ ports without redesign
3. **Real-Time First**: All updates propagate within 5 seconds (sensor to UI)
4. **Open Standards**: Reuse Smart Data Models, FIWARE components, no proprietary APIs
5. **Data Privacy**: No personal data in operational DB, GDPR-compliant

### 13.2 Key Trade-Offs

| Aspect | Choice | Benefit | Cost |
|--------|--------|---------|------|
| Context store | Orion-LD | NGSI-LD native, pub/sub | Eventual consistency |
| Time-series | TimescaleDB | PostgreSQL + advanced TS features | Not as specialized as InfluxDB |
| Backend | FastAPI | Async-native, lightweight | Operational complexity vs. Django |
| LLM | Ollama local | Data privacy, no costs | Lower quality than cloud APIs |
| Frontend | Vanilla JS | No build step, lightweight | Less abstractions, more code |
| Monitoring | Prometheus | Standard, lightweight | Limited dashboard vs. DataDog |

---

## 14. Future Enhancements

### 14.1 Planned Improvements

- **Kubernetes Migration**: Move from docker-compose to K8s (Helm charts)
- **Advanced Auth**: OAuth2 + OIDC (Active Directory integration)
- **Geographic Redundancy**: Multi-region deployment (Galicia + backup region)
- **Advanced ML**: Reinforcement learning for optimal berth allocation
- **Mobile App**: Native iOS/Android app (sync via same WebSocket)
- **Integration APIs**: 3rd-party vessel tracking APIs (Pole Star, MarineTraffic)
- **Blockchain**: Immutable audit trail of critical operations (optional)

### 14.2 Performance Optimizations

- **Caching Layer**: Varnish or Redis for frontend static assets
- **CDN**: CloudFront/Cloudflare for geographic distribution
- **Database Indexing**: Analyze slow queries, add strategic indexes
- **Query Optimization**: Materialized views in TimescaleDB for common analytics
- **Compression**: WebSocket message compression, gzip on APIs

---

## 15. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-27 | Initial architecture document |
| 1.1 | 2026-04-28 | Added section 5.7: Realtime Infrastructure (WebSocket, audit, cache, Celery) |
| 1.2 | 2026-04-28 | Fixed duplicate section number (5.4→5.7), corrected nginx config notes, updated status |

---

**Next Review:** After Phase 2 backend implementation  
**Maintainer:** SmartPort Architecture Team  
**Status:** ACTIVE — Binding for all development
