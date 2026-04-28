# SmartPort Galicia Operations Center

**An intelligent, real-time operational management platform for the Galician port network.**

---

## 🎯 Quick Overview

**SmartPort Galicia** is a FIWARE-based, NGSI-LD-compliant platform for managing multiple Galician ports as a unified system. It combines real-time operational control, historical analytics, machine learning forecasting, and intelligent decision support.

**Status:** Iteration 2 Complete - Realtime Infrastructure Active  
**Version:** 1.1  
**Last Updated:** 2026-04-28

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### � **NEW: Realtime Infrastructure & Operational Robustness (Iteration 2)**
- ✅ **WebSocket Real-Time Events** - Live event streaming to connected clients
  - Event types: berth updates, port calls, alerts, availability changes
  - Subscription filtering by port, entity type, and event
  - Graceful connection lifecycle management
- ✅ **PostgreSQL Audit Trail** - Immutable operational history
  - Logs all critical operations (berth changes, port calls, authorization failures)
  - JSONB state snapshots, correlation ID tracking
  - REST API for audit queries and compliance
- ✅ **Redis Caching** - Reduced latency and load
  - Selective caching: port summaries, availability, active alerts
  - Event-driven invalidation, TTL management
  - Graceful fallback if Redis unavailable
- ✅ **Celery Background Tasks** - Async processing without blocking
  - Alert checking, availability recalculation, cache warming
  - Task orchestration after domain operations
  - Scheduled jobs for periodic analysis

### 🔴 **Real Data Integration**
- ✅ **AEMET OpenData** - Spanish meteorological service (JWT authenticated)
- ✅ **MeteoGalicia** - Galician regional weather & oceanographic forecasts
- ✅ **Puertos del Estado** - Official port authority sea conditions (waves, wind, currents)
- ✅ **Open-Meteo Marine API** - Free offshore marine weather (wave data, forecasts)
- ✅ Intelligent fallback to realistic simulators when APIs unavailable
- ✅ Full data provenance tracking (source, confidence level, timestamp)
- ✅ 8 periodic ingestion tasks (4 real APIs + 4 simulator fallbacks)

### Core Operational
- ✅ Real-time multipurpose port network visualization (11+ Galician ports)
- ✅ Berth availability & occupancy management
- ✅ Port call lifecycle management (expected → active → completed)
- ✅ Operation logging (cargo handling, services, maintenance)
- ✅ Vessel authorization & compliance tracking
- ✅ Environmental monitoring (air quality, weather, alerts)

### Intelligence
- ✅ ML-powered occupancy forecasting (Prophet)
- ✅ Smart berth recommendations (Random Forest)
- ✅ Intelligent alerting (rule-based thresholds)
- ✅ Conversational AI assistant (Ollama LLM)

### Analytics
- ✅ Real-time dashboards (Leaflet maps, Chart.js)
- ✅ Historical analytics (QuantumLeap/TimescaleDB)
- ✅ Embedded Grafana dashboards
- ✅ KPIs: occupancy, dwell time, revenue

### Immersive
- ✅ 3D port visualization (Three.js)
- ✅ Geospatial mapping (OpenStreetMap)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Context Broker** | Orion-LD (NGSI-LD v1.6) |
| **Time-Series** | QuantumLeap + TimescaleDB |
| **Message Broker** | Mosquitto MQTT |
| **Backend** | FastAPI (Python 3.10+) |
| **Database** | PostgreSQL + MongoDB |
| **Cache & Queue** | Redis + Celery |
| **ML** | Prophet, scikit-learn |
| **LLM** | Ollama (Llama 2) |
| **Frontend** | HTML/CSS/JS + Leaflet + Three.js |
| **Visualization** | Chart.js + Grafana |
| **Infrastructure** | Docker Compose, Nginx |

---

## 🏗️ Architecture

**6 Main Layers:**

```
┌──────────────────────────────────────────┐
│ Presentation (Leaflet, Charts, 3D)       │
├──────────────────────────────────────────┤
│ FastAPI Backend (REST, WebSocket, Logic) │
├──────────────────────────────────────────┤
│ Context (Orion-LD) + Time-Series (QL)    │
├──────────────────────────────────────────┤
│ Message Broker (MQTT) + IoT Agent        │
├──────────────────────────────────────────┤
│ Databases (PostgreSQL, TimescaleDB, Mongo)
├──────────────────────────────────────────┤
│ Infrastructure (Docker Compose, Nginx)   │
└──────────────────────────────────────────┘
```

**Full details:** See [docs/architecture.md](docs/architecture.md)

---

## 🚀 Quick Start

### 🔴 **NEW: Real APIs Integration Complete!**

SmartPort now includes **4 real-time API integrations** with your AEMET credentials pre-configured:

- 🌡️ **AEMET** (Spanish meteorology) - Every 30 min
- 🌊 **Puertos del Estado** (Sea conditions) - Every 15 min
- 🌍 **MeteoGalicia** (Regional weather) - Every 30 min
- 🌀 **Open-Meteo** (Marine forecasts) - Every 30 min

**👉 See [QUICKSTART_REAL_APIS.md](QUICKSTART_REAL_APIS.md) for complete startup instructions with real data!**

---

### Prerequisites

- Docker & Docker Compose (v20.10+)
- Git
- Python 3.10+ (for local development)
- 4+ GB RAM, 20 GB disk space recommended

### 1. Clone Repository

```bash
git clone https://github.com/your-org/SmartPorts.git
cd SmartPorts
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values (IMPORTANT: change secrets for production)
# nano .env
# Key variables:
#   - SECRET_KEY: Change to a strong random value
#   - POSTGRES_PASSWORD, TIMESCALE_PASSWORD, MONGO_ROOT_PASSWORD
#   - REDIS_PASSWORD, GRAFANA_PASSWORD
#   - PUBLIC_BASE_URL: Set to your domain
```

### 3. Start Infrastructure Stack

```bash
# Build and start all services (first run ~5-10 minutes)
docker-compose up -d

# Verify all services are healthy
docker-compose ps

# Check health status
curl http://localhost/health
```

### 4. Access Services

Once running, access SmartPort components at:

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Frontend (Web UI)** | http://localhost | N/A |
| **API Docs (Swagger)** | http://localhost/api/v1/docs | N/A |
| **Grafana Dashboards** | http://localhost/grafana | admin / admin123 |
| **Prometheus Metrics** | http://localhost/prometheus | N/A |
| **Orion-LD API** | http://localhost/ngsi-ld/v1/ | N/A |
| **QuantumLeap API** | http://localhost/ql/v2/ | N/A |

### 5. Service Verification

```bash
# Check all services are running
docker-compose ps

# Test backend health endpoint
curl http://localhost/health

# Test Orion-LD context broker
curl http://localhost/ngsi-ld/v1/entities?limit=1

# Test QuantumLeap version
curl http://localhost/ql/v2/version

# Test MQTT broker (publish test message)
docker exec smartports_mosquitto mosquitto_pub -h localhost -t test -m "Hello SmartPort"

# View backend logs
docker-compose logs -f backend

# View all service logs
docker-compose logs -f
```

### 6. Stopping Services

```bash
# Stop all running containers (preserves volumes)
docker-compose down

# Stop and remove all data (careful!)
docker-compose down -v

# Restart a specific service
docker-compose restart backend
```

### 7. First Run - Load Seed Data (Recommended)

SmartPort includes 211 pre-generated NGSI-LD entities covering 8 Galician ports:

```bash
# Step 1: Validate seed payloads (verify NGSI-LD compliance)
python3 backend/scripts/validate_payloads.py
# Expected: ✓ ALL PAYLOADS VALID

# Step 2: Generate seed JSON file
python3 backend/scripts/generate_seed_json.py --pretty
# Creates: data/seed/galicia_entities.json (217 KB)

# Step 3: Preview what will be loaded (dry-run)
python3 backend/scripts/load_seed.py --dry-run
# Shows: 211 entities ready to load

# Step 4: Load to Orion-LD (upsert mode - safe)
python3 backend/scripts/load_seed.py --upsert
# Result: 211 entities created in Orion-LD

# Step 5: Verify data was loaded
curl -H "FIWARE-Service: smartport" \
     -H "FIWARE-ServicePath: /galicia" \
     http://localhost:1026/ngsi-ld/v1/entities?type=Port
# Lists: All 8 Galician ports
```

**Seed Coverage:**
- 8 Ports (A Coruña, Vigo, Ferrol, Marín, Vilagarcía, Ribeira, Burela, Baiona)
- 71 Berths (6-15 per port)
- 10 Master Vessels (static registry)
- 10 Vessel Instances (active ships)
- 10 BoatAuthorized entities
- 32 BoatPlacesAvailable entities (4 categories × 8 ports)
- 32 BoatPlacesPricing entities
- 11 Devices (air quality & weather sensors)
- 6 AirQualityObserved measurements
- 5 WeatherObserved measurements

📚 **More details:** See [data/seed/README.md](data/seed/README.md)

---

## 📁 Project Structure

```
SmartPorts/
├── agents/
│   └── AGENTS.md                  ← Development rules & governance
├── docs/
│   ├── PRD.md                     ← Product requirements  
│   ├── data_model.md              ← NGSI-LD 15 entity types
│   └── architecture.md            ← System design & data flows
├── backend/                       ← FastAPI backend (Python)
│   ├── main.py                    ← Application entry point
│   ├── config.py                  ← Settings from .env
│   ├── api/
│   │   ├── health.py              ← Health check endpoints
│   │   └── v1.py                  ← API v1 routes
│   ├── services/
│   │   ├── orion.py               ← Orion-LD integration
│   │   └── quantumleap.py         ← QuantumLeap integration
│   ├── models/                    ← Pydantic schemas (TBD)
│   ├── tasks/
│   │   └── celery.py              ← Async task definitions
│   ├── requirements.txt            ← Python dependencies
│   └── Dockerfile                 ← Container image
├── frontend/                      ← Web UI (HTML/CSS/JS)
│   ├── index.html                 ← Main page with dashboards
│   ├── css/
│   │   └── style.css              ← Application styles
│   └── js/
│       └── app.js                 ← Frontend logic
├── nginx/
│   └── nginx.conf                 ← Reverse proxy config
├── mosquitto/
│   └── mosquitto.conf             ← MQTT broker config
├── prometheus/
│   └── prometheus.yml             ← Metrics scrape config
├── grafana/
│   └── provisioning/
│       └── datasources/           ← TimescaleDB & Prometheus datasources
├── docker-compose.yml             ← Container orchestration (13 services)
├── .env.example                   ← Environment template
├── .gitignore                     ← Git ignore rules
├── README.md                      ← This file
└── data/
    └── seed/                      ← Sample data (future)
```

**Implementation Status:**
- ✅ Infrastructure stack (13 services, fully operational)
- ✅ Backend scaffolding (FastAPI, services, tasks)
- ✅ Frontend template (dashboard UI ready)
- ✅ FIWARE integration (Orion, QuantumLeap services)
- ✅ Environment & configuration
- 🔄 ML pipelines (Prophet, scikit-learn)
- 🔄 Advanced features (WebSocket, 3D visualization)

---

## 🏛️ Infrastructure Overview

### Deployed Services (Docker Compose)

The complete stack includes **13 containerized services**:

#### Layer 1: IoT & MQTT
- **mosquitto** (1883, 9001): MQTT broker for sensor ingestion
- **iot-agent** (4041): IoT Agent JSON (MQTT → NGSI-LD)

#### Layer 2: FIWARE Context
- **orion-ld** (1026): Orion-LD context broker
- **quantumleap** (8668): Time-series manager + TimescaleDB persistence

#### Layer 3: Databases
- **postgresql** (5432): Operational DB
- **timescaledb** (5433): Time-series storage
- **mongodb** (27017): Document store
- **redis** (6379): Cache & task queue

#### Layer 4: Backend & Workers
- **backend** (8000): FastAPI REST + WebSocket
- **celery-worker**: Async tasks (ML, forecasting)

#### Layer 5: Presentation
- **nginx**: Reverse proxy (80/443)
- **grafana** (3000): Dashboards
- **prometheus** (9090): Metrics

### Complete Data Flow

```
Sensors → MQTT → Mosquitto → IoT Agent → Orion-LD ↔ PostgreSQL
                                            ↓
                                        QuantumLeap → TimescaleDB
                                            ↓
                                         Backend ↔ Redis
                                            ↓
                                    Nginx (Reverse Proxy)
                                       ↙        ↘
                                   Frontend   Grafana/Prometheus
```

### Persistent Volumes

- `mongodb_data`, `mongodb_config`
- `postgres_data`, `timescaledb_data`, `redis_data`
- `mosquitto_data`, `mosquitto_logs`
- `grafana_storage`, `prometheus_data`, `nginx_cache`

---

## ⚙️ Configuration

### Environment Variables

See [.env.example](.env.example) for all available variables with descriptions.

**Quick start (.env):**
```bash
# Copy the template
cp .env.example .env

# For development, the defaults are acceptable
# For production, CHANGE THESE:
SECRET_KEY=<generate_secure_random_key>
POSTGRES_PASSWORD=<strong_password>
TIMESCALE_PASSWORD=<strong_password>
MONGO_ROOT_PASSWORD=<strong_password>
REDIS_PASSWORD=<strong_password>
GRAFANA_PASSWORD=<admin_password>
ENVIRONMENT=production
DEBUG=false
```

### Service Ports (Internal Network)

| Service | Port | Access |
|---------|------|--------|
| **Nginx (Frontend)** | 80 → 443 | External |
| **Backend API** | 8000 | Internal |
| **Orion-LD** | 1026 | Internal |
| **QuantumLeap** | 8668 | Internal |
| **Grafana** | 3000 | Internal (via Nginx) |
| **Prometheus** | 9090 | Internal (via Nginx) |
| **Mosquitto (MQTT)** | 1883, 9001 | Internal |
| **PostgreSQL** | 5432 | Internal |
| **TimescaleDB** | 5433 | Internal |
| **MongoDB** | 27017 | Internal |
| **Redis** | 6379 | Internal |

**Public endpoints (via Nginx reverse proxy):**
- `http://localhost/` → Frontend
- `http://localhost/api/v1/` → Backend API
- `http://localhost/api/v1/docs` → Swagger API docs
- `http://localhost/api/ws` → WebSocket
- `http://localhost/grafana/` → Grafana dashboards
- `http://localhost/prometheus/` → Prometheus metrics
- `http://localhost/ngsi-ld/` → Orion-LD API
- `http://localhost/ql/` → QuantumLeap API

---

## 👨‍💻 Development

### Local Setup

```bash
# Create Python virtual environment
python3.10 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r backend/requirements.txt

# Run tests
pytest backend/tests/ --cov=backend/app --cov-report=html

# Start backend (development mode)
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Code Style

```bash
# Format code
black backend/

# Lint
flake8 backend/ --max-line-length=100

# Type check
mypy backend/

# Sort imports
isort backend/
```

### Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test
pytest backend/tests/test_services.py::test_berth_occupancy -v

# Coverage report
pytest backend/tests/ --cov=backend/app --cov-report=html
open htmlcov/index.html
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes, test locally

# Commit (with meaningful message)
git add .
git commit -m "feat: add berth recommendation service"

# Push and create PR
git push origin feature/your-feature

# After PR review, merge to main
git checkout main
git pull origin main
git merge feature/your-feature
git push origin main
```

**Important:** See [agents/AGENTS.md](agents/AGENTS.md) for mandatory documentation updates after each feature.

---

## 🐳 Deployment

### Docker Compose (Development/Testing)

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Stop services
docker-compose -f docker/docker-compose.yml down

# Clean up (including volumes)
docker-compose -f docker/docker-compose.yml down -v

# Rebuild containers
docker-compose -f docker/docker-compose.yml build --no-cache
```

### Production Deployment (Future)

Kubernetes manifests (Helm charts) coming in Phase 2.

For now:
1. Use docker-compose on a production VM
2. Mount volumes to persistent storage
3. Configure SSL certificates (Let's Encrypt)
4. Set up backup cron jobs
5. Monitor with Prometheus + AlertManager

---

## 📚 Documentation

### Core Documents

| Document | Purpose |
|----------|---------|
| [docs/PRD.md](docs/PRD.md) | Product requirements & features |
| [docs/data_model.md](docs/data_model.md) | NGSI-LD entity definitions & examples |
| [docs/architecture.md](docs/architecture.md) | System design, services, data flows |
| [agents/AGENTS.md](agents/AGENTS.md) | Development rules & governance |
| [README.md](README.md) | This file (quick start) |

### Generated Documentation

```bash
# API documentation (auto-generated from FastAPI)
# Access at: http://localhost:8000/docs (Swagger UI)
# Access at: http://localhost:8000/redoc (ReDoc)

# Data model diagrams (in data_model.md)
# ER diagram generation: future enhancement

# Architecture diagrams (Mermaid, in architecture.md)
# View in GitHub/Markdown editor or render locally
```

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check Docker daemon
docker ps

# View container logs
docker-compose -f docker/docker-compose.yml logs backend

# Check disk space
df -h

# Rebuild container
docker-compose -f docker/docker-compose.yml build --no-cache backend
```

### Database Connection Errors

```bash
# Verify database is running
docker-compose -f docker/docker-compose.yml ps timescaledb

# Check connection from backend
docker-compose -f docker/docker-compose.yml exec backend psql -h timescaledb -U smartport_user

# Check logs
docker-compose -f docker/docker-compose.yml logs timescaledb
```

### Orion-LD Not Responding

```bash
# Check Orion status
curl -i http://localhost:1026/version

# Check MongoDB is running
docker-compose -f docker/docker-compose.yml ps mongodb

# Restart Orion
docker-compose -f docker/docker-compose.yml restart orion-ld
```

### MQTT Connection Issues

```bash
# Test MQTT broker
docker exec mosquitto mosquitto_sub -h localhost -t test

# Check Mosquitto logs
docker-compose -f docker/docker-compose.yml logs mosquitto

# Verify IoT Agent is subscribed
docker-compose -f docker/docker-compose.yml logs iot-agent-json
```

### WebSocket Connection Drops

```bash
# Check backend logs
docker-compose -f docker/docker-compose.yml logs backend | grep websocket

# Verify Nginx is forwarding WS
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost/ws

# Restart backend
docker-compose -f docker/docker-compose.yml restart backend
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Monitor database connections
docker-compose -f docker/docker-compose.yml exec timescaledb \
  psql -U smartport_user -c "SELECT count(*) FROM pg_stat_activity;"

# Check Celery task queue
docker-compose -f docker/docker-compose.yml exec backend \
  celery -A app.tasks inspect active

# Monitor Redis
docker-compose -f docker/docker-compose.yml exec redis redis-cli info stats
```

### Data Not Appearing in Orion

```bash
# Check if MQTT messages are being published
docker-compose -f docker/docker-compose.yml exec mosquitto \
  mosquitto_sub -h localhost -t "devices/+" &

# Check IoT Agent logs for transformation errors
docker-compose -f docker/docker-compose.yml logs iot-agent-json

# Verify subscription from QL to Orion
curl -s http://localhost:1026/ngsi-ld/v1/subscriptions | jq .
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused: 1026` | Orion-LD not running | `docker-compose up -d orion-ld` |
| `MQTT: Connection refused` | Mosquitto not running | `docker-compose up -d mosquitto` |
| `permission denied` | Docker daemon access issue | Add user to docker group: `sudo usermod -aG docker $USER` |
| `Bind for 0.0.0.0:80 failed` | Port already in use | Change NGINX_HTTP_PORT in .env |
| `No such image` | Image not built | `docker-compose build` |

---

## 📊 Key Metrics & Monitoring

### Health Checks

```bash
# Overall system health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/health/db

# Orion-LD status
curl http://localhost:1026/version

# QuantumLeap status
curl http://localhost:8668/version

# Metrics (Prometheus format)
curl http://localhost:8000/metrics
```

### Sample Queries

```bash
# List all ports
curl http://localhost:8000/api/ports

# Get port details
curl http://localhost:8000/api/ports/CorA

# Get occupancy
curl http://localhost:8000/api/ports/CorA/occupancy

# List active alerts
curl http://localhost:8000/api/alerts?severity=critical

# Get forecast
curl http://localhost:8000/api/forecasts/occupancy?portId=CorA&days=7
```

---

## 📞 Support & Contributing

- **Issues:** Create a GitHub issue with detailed reproduction steps
- **Discussions:** Use GitHub Discussions for questions
- **PRs:** Follow development guidelines in [agents/AGENTS.md](agents/AGENTS.md)
- **Documentation:** Update docs with every significant change

---

## 📜 License

[To be defined]

---

## 🔗 References

- **FIWARE:** https://www.fiware.org
- **NGSI-LD Spec:** https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf
- **Smart Data Models:** https://smartdatamodels.org
- **Galician Ports Authority:** https://portosdegalicia.gal
- **Puertos del Estado:** https://www.puertos.es

---

**Last Updated:** 2026-04-27  
**Maintained By:** SmartPort Team  
**Status:** Production-Ready Foundation
