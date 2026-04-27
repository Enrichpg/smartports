# SmartPort Galicia Operations Center

**An intelligent, real-time operational management platform for the Galician port network.**

---

## 🎯 Quick Overview

**SmartPort Galicia** is a FIWARE-based, NGSI-LD-compliant platform for managing multiple Galician ports as a unified system. It combines real-time operational control, historical analytics, machine learning forecasting, and intelligent decision support.

**Status:** Foundation Complete (Phase 1)  
**Version:** 1.0  
**Last Updated:** 2026-04-27

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

### Prerequisites

- Docker & Docker Compose (v20.10+)
- Git
- Python 3.10+ (for local development)
- 4+ GB RAM, 20 GB disk space

### 1. Clone Repository

```bash
git clone https://github.com/Enrichpg/smartports
cd SmartPorts
```

### 2. Configure Environment

```bash
# Copy example configuration
cp config/.env.example .env

# Edit .env with your values (especially secrets)
nano .env
```

**Key variables to set:**
- `MQTT_USER`, `MQTT_PASSWORD`
- `POSTGRES_PASSWORD`, `TIMESCALEDB_PASSWORD`
- `JWT_SECRET_KEY`
- `GRAFANA_ADMIN_PASSWORD`

### 3. Start Services

```bash
# Start all services (first time ~5 min)
docker-compose -f docker/docker-compose.yml up -d

# Check service status
docker-compose -f docker/docker-compose.yml ps

# View logs (all services)
docker-compose -f docker/docker-compose.yml logs -f

# View specific service logs
docker-compose -f docker/docker-compose.yml logs -f backend
```

### 4. Verify Installation

```bash
# Test backend health
curl http://localhost:8000/health

# Test Orion-LD
curl http://localhost:1026/version

# Test MQTT
docker exec mosquitto mosquitto_sub -h localhost -t test &
docker exec mosquitto mosquitto_pub -h localhost -t test -m "Hello"

# Access dashboards
# - Frontend: http://localhost:80
# - Grafana: http://localhost:3000 (admin/set_in_.env)
# - API Docs: http://localhost:8000/docs
```

### 5. Load Sample Data (Optional)

```bash
# Populate 11 Galician ports with seed data
python backend/scripts/load_seed_data.py

# Check entities in Orion
curl http://localhost:1026/ngsi-ld/v1/entities?type=Port
```

---

## 📁 Project Structure

```
SmartPorts/
├── agents/
│   └── AGENTS.md              ← Development rules & obligations
├── docs/
│   ├── PRD.md                 ← Product requirements
│   ├── data_model.md          ← NGSI-LD 15 entities
│   ├── architecture.md        ← System design & services
│   ├── APPLICATION.md         ← Vision & features (when created)
│   └── README.md              ← This file
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py      ← Settings from .env
│   │   │   ├── security.py    ← JWT, RBAC
│   │   │   └── logger.py      ← Logging config
│   │   ├── models/
│   │   │   ├── entities.py    ← Pydantic schemas
│   │   │   ├── database.py    ← SQLAlchemy models
│   │   │   └── requests.py    ← API models
│   │   ├── services/
│   │   │   ├── orion.py       ← Orion-LD integration
│   │   │   ├── quantumleap.py ← Time-series queries
│   │   │   ├── port_service.py
│   │   │   ├── berth_service.py
│   │   │   ├── portcall_service.py
│   │   │   ├── alert_service.py
│   │   │   └── ml_service.py
│   │   ├── api/
│   │   │   ├── routes.py      ← Main routes
│   │   │   ├── ports.py       ← Port endpoints
│   │   │   ├── berths.py      ← Berth endpoints
│   │   │   ├── portcalls.py   ← Port call endpoints
│   │   │   ├── operations.py  ← Operation endpoints
│   │   │   ├── vessels.py     ← Vessel endpoints
│   │   │   ├── alerts.py      ← Alert endpoints
│   │   │   ├── analytics.py   ← Analytics endpoints
│   │   │   ├── health.py      ← Health/status endpoints
│   │   │   └── llm.py         ← LLM chat endpoints
│   │   ├── websocket/
│   │   │   └── manager.py     ← WebSocket pool & broadcast
│   │   └── tasks/
│   │       ├── __init__.py    ← Celery config
│   │       ├── forecast.py    ← Prophet forecasting
│   │       └── recommend.py   ← Berth recommendation
│   ├── Dockerfile
│   ├── requirements.txt
│   └── scripts/
│       └── load_seed_data.py  ← Populate initial data
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   │   ├── app.js             ← Main app logic
│   │   ├── map.js             ← Leaflet integration
│   │   ├── websocket.js       ← WebSocket client
│   │   ├── charts.js          ← Chart.js integration
│   │   ├── 3d.js              ← Three.js integration
│   │   └── llm-chat.js        ← LLM chat widget
│   └── assets/
├── docker/
│   └── docker-compose.yml     ← Full orchestration
├── config/
│   ├── .env.example           ← Environment template
│   ├── nginx.conf             ← Nginx reverse proxy config
│   ├── mosquitto.conf         ← MQTT broker config
│   ├── prometheus.yml         ← Prometheus scrape config
│   └── grafana/
│       └── dashboards/        ← Pre-built dashboards
├── data/
│   └── seed/
│       └── ports.json         ← Sample port data
├── .gitignore
└── README.md                  ← This file
```

---

## ⚙️ Configuration

### Environment Variables

See [config/.env.example](config/.env.example) for all available variables.

**Critical variables for production:**
```bash
# FIWARE
ORION_HOST=orion-ld
ORION_PORT=1026

# Security
JWT_SECRET_KEY=<random_secret_key_128_chars_minimum>
JWT_ALGORITHM=HS256

# Databases
POSTGRES_PASSWORD=<strong_password>
TIMESCALEDB_PASSWORD=<strong_password>
MONGODB_PASSWORD=<strong_password>
REDIS_PASSWORD=<strong_password>
MQTT_PASSWORD=<strong_password>

# Machine Learning
PROPHET_FORECAST_DAYS=7

# LLM
OLLAMA_MODEL=llama2:13b

# Application
SITE_URL=https://smartport.your-domain.com
```

### Ports & Services

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Nginx (HTTP) | 80 | HTTP | Redirect to HTTPS |
| Nginx (HTTPS) | 443 | HTTPS | Reverse proxy, static files |
| FastAPI | 8000 | HTTP | REST API (internal) |
| WebSocket | 8001 | WS | Real-time updates (internal) |
| Orion-LD | 1026 | HTTP | Context broker (internal) |
| QuantumLeap | 8668 | HTTP | Time-series (internal) |
| Grafana | 3000 | HTTP | Analytics dashboards (internal) |
| Mosquitto | 1883 | MQTT | Message broker (internal) |
| PostgreSQL | 5432 | TCP | Operational DB (internal) |
| TimescaleDB | 5432 | TCP | Time-series DB (internal) |
| MongoDB | 27017 | TCP | Document store (internal) |
| Redis | 6379 | TCP | Cache & queue (internal) |

**External access (via Nginx):**
- `https://smartport.your-domain.com/` → Frontend
- `https://smartport.your-domain.com/api/` → API
- `https://smartport.your-domain.com/ws` → WebSocket
- `https://smartport.your-domain.com/grafana/` → Grafana

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
