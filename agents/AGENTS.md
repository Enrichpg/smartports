# SmartPort Galicia Operations Center — AGENTS.md

**Version:** 1.0  
**Last Updated:** 2026-04-27  
**Status:** Active  
**Authority:** Project Lead  

---

## 📋 Purpose

This document defines the **operational rules and constraints** for any AI agent, developer, or contributor working on the SmartPort Galicia Operations Center repository. It ensures coherence, technical rigor, NGSI-LD compliance, and traceability across all development iterations.

**This is not optional.** These rules are binding for every contribution.

---

## 🎯 Project Overview

### What is SmartPort Galicia Operations Center?

**SmartPort Galicia Operations Center** is an **intelligent, real-time operational management platform** for multiple Galician ports modeled as a unified, multipurpose regional network—not isolated ports.

**Core Identity:**
- **Scope:** Galician port system (minimum 11 ports, expandable to 128+)
- **Nature:** Real-time operational platform with business logic (not just visualization)
- **Foundation:** FIWARE + NGSI-LD v1.6 + Official Smart Data Models
- **Data Flow:** Sensors/simulators → MQTT → IoT Agent → Orion-LD → QuantumLeap → Backend → Frontend → WebSocket
- **Stack:** FastAPI, PostgreSQL, TimescaleDB, MongoDB, Redis, Ollama, Leaflet, Three.js, Grafana

### What SmartPort Does

```
Real-Time Multipurpose Operations Center
├─ Port network visualization (map + KPIs)
├─ Berth management (state, occupancy, availability)
├─ Port call lifecycle (expected → active → completed)
├─ Vessel tracking (position, status, authorization)
├─ Environmental monitoring (sensors, air quality, weather)
├─ Operational alerting (rules-based, threshold-triggered)
├─ Historical analytics (occupancy, dwell time, revenue trends)
├─ ML-based forecasting (occupancy prediction)
├─ ML-based recommendation (optimal berth assignment)
├─ Local LLM assistant (natural language queries on live data)
└─ Immersive 3D visualization (ports, vessels, sensors)
```

### Why It Matters

The Galician port system is complex, distributed, and time-critical. Operations require:
- **Real-time situational awareness** across multiple ports
- **Intelligent resource allocation** (berths, services)
- **Predictive capacity** (occupancy, congestion)
- **Compliance and safety** (authorizations, environmental monitoring)
- **Data-driven decision making** (analytics, recommendations)

SmartPort provides this as a unified platform via FIWARE, reusing official Smart Data Models and ensuring NGSI-LD compliance at every layer.

---

## 🔷 Technical Foundation Rules

### 1. NGSI-LD is Non-Negotiable

**Every data model in this project must be NGSI-LD v1.6 compliant.**

Rules:
- ✅ **All payloads include @context** (global or local)
- ✅ **Relationships use NGSI-LD Relationship type** with `object` field
- ✅ **Dynamic attributes include observedAt** timestamp
- ✅ **Geospatial data use GeoProperty** (not plain Property)
- ✅ **Temporal data include datetime in ISO 8601 format**
- ❌ NGSIv2 only in exceptional, documented cases

**Reference:** [NGSI-LD Spec](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf)

### 2. Smart Data Models are Authoritative

**Reuse official Smart Data Models.** Do not invent local models if an official one exists.

**Sources:**
- Portal: https://smartdatamodels.org
- GitHub Org: https://github.com/smart-data-models
- Catalog: https://smart-data-models.github.io/data-models/
- dataModel.Ports: https://github.com/smart-data-models/dataModel.Ports
- dataModel.MarineTransport: https://github.com/smart-data-models/dataModel.MarineTransport

**Mandatory entities in this project:**
- Port, PortAuthority, Vessel, MasterVessel, PortCall, Berth, Operation (from MarineTransport)
- SeaportFacilities, BoatAuthorized, BoatPlacesAvailable, BoatPlacesPricing (from Ports)
- Device, AirQualityObserved, WeatherObserved, Alert (transversal)

When documenting entities, **link to official repository/subject** wherever possible.

### 3. Configuration Never Hardc0ded

**All secrets, URLs, credentials, API keys, and environment-specific values go in `.env`.**

Rules:
- ✅ Use `config.py` + `pydantic.BaseSettings` or `python-dotenv`
- ✅ Reference `.env.example` for every variable
- ✅ Never commit `.env`
- ❌ No hardcoded URLs, API keys, db passwords, or service endpoints

### 4. Logging Over Printing

**Use Python `logging` module for all output.**

Rules:
- ✅ Import `logging` and configure in `config.py`
- ✅ Use `logger.info()`, `logger.warning()`, `logger.error()`, `logger.debug()`
- ✅ Include context (request IDs, entity IDs) in log messages
- ❌ Never use `print()` in production code

### 5. Error Handling is Mandatory

**Every external integration (Orion, QuantumLeap, MQTT, DB) must have try-except-log-retry logic.**

Rules:
- ✅ Catch specific exceptions
- ✅ Log errors with context and stack trace
- ✅ Implement retry logic for transient failures
- ✅ Return meaningful HTTP status codes (4xx, 5xx)
- ✅ Validate data before sending to Orion
- ❌ Never swallow exceptions silently

### 6. Testing is Part of Development

**No code merges without tests.**

Rules:
- ✅ Unit tests for services and domain logic
- ✅ Integration tests for Orion, QuantumLeap interactions
- ✅ Use `pytest` for backend
- ✅ Run tests before committing: `pytest --cov`
- ✅ Maintain >80% code coverage on backend services

### 7. Documentation is Code

**Every technical decision, architecture change, or entity modification must be reflected in live documentation.**

Rules:
- ✅ Code = Documentation in sync
- ✅ If you add a service, update `architecture.md`
- ✅ If you change a model, update `data_model.md`
- ✅ If you add a feature, update `PRD.md`
- ✅ Update `README.md` if setup/deployment changes
- ❌ Never close a PR or commit without doc review

---

## 🏗️ Mandatory Documentation Files

These files are the **source of truth** for the project. Keep them current.

| File | Purpose | Owner |
|------|---------|-------|
| **docs/PRD.md** | Product requirements, features, use cases | Product decisions |
| **docs/data_model.md** | NGSI-LD entity definitions, examples, relationships | Data modeling |
| **docs/architecture.md** | System architecture, services, data flows, decisions | System design |
| **README.md** | Installation, quickstart, troubleshooting | Onboarding |
| **agents/AGENTS.md** | This file — development rules and obligations | Governance |

---

## ⚙️ The Critical Closure Rule

### ⭐ MANDATORY AT THE END OF EVERY CONVERSATION OR ITERATION

**This is the single most important rule in this document.**

At the **end of each development iteration, conversation loop, or feature implementation**, the agent **MUST**:

1. **Review** all code changes made in the session
2. **Check** if any of these triggered documentation updates:
   - ✓ New or modified NGSI-LD entities → update `docs/data_model.md`
   - ✓ New services or architectural changes → update `docs/architecture.md`
   - ✓ New features, use cases, or requirements → update `docs/PRD.md`
   - ✓ Installation or deployment changes → update `README.md`

3. **Update** documentation **immediately** (within same conversation)

4. **Stage and commit** all changes:
   ```bash
   git add .
   git commit -m "docs: update after [FEATURE/COMPONENT]"
   ```

5. **Push to remote** (if permissions allow):
   ```bash
   git push origin main
   ```

### Why This Rule Exists

- **Traceability:** Every feature is documented in real-time
- **Onboarding:** New contributors see current state, not stale docs
- **Consistency:** Code + documentation stay in sync
- **Auditability:** Commit history reflects all decisions
- **Maintenance:** No technical debt from undocumented changes

### Example Closure Workflow

```
Session: Implement Berth availability feature

1. Code changes:
   - backend/services/berth_service.py (new 200 LOC)
   - backend/routes/berth_routes.py (new endpoints)
   - tests/test_berth_service.py (new tests)

2. Documentation checks:
   ✓ New entity BoatPlacesAvailable touched?
     → YES → Update data_model.md (add/modify entity section)
   ✓ New service layer?
     → YES → Update architecture.md (add service, update flow)
   ✓ New API routes?
     → YES → Update PRD.md (add functional requirement)

3. Commit & Push:
   git add .
   git commit -m "feat: berth availability service with real-time occupancy"
   git push origin main

4. Close session only after git push succeeds
```

---

## 📐 Entity Management Rules

### Creating or Modifying Entities

If you touch any NGSI-LD entity:

1. **Before coding:** Check Smart Data Models official definition
2. **During coding:** Use correct NGSI-LD structure (Relationship, observedAt, @context)
3. **After coding:** Add/update `docs/data_model.md` with:
   - Entity name, source repo, official link
   - Attribute table (name, NGSI type, NGSI data type, static/dynamic, description)
   - Example JSON-LD payload
   - Related entities and relationships

4. **Validation:** Validate payload against official schemas where available

### Example: New Attribute on Vessel Entity

```
Code change: Add 'lastAISUpdate' timestamp to Vessel

Documentation update: data_model.md

Find Vessel section → add row to attributes table:
| lastAISUpdate | DateTime | date-time | Dynamic | Last update from AIS source (observedAt required) |

Update example payload to show new attribute with observedAt

Update README/troubleshooting if relevant

Commit: "docs: add lastAISUpdate to Vessel in data_model.md"
```

---

## 🔌 Integration Rules

### Orion-LD Integration

**Every interaction with Orion must:**
- ✅ Include `@context` in payloads
- ✅ Use correct NGSI-LD v1.6 syntax
- ✅ Handle HTTP 4xx, 5xx responses
- ✅ Log request/response bodies for debugging
- ✅ Implement timeout (recommend 5-10s)
- ✅ Retry transient failures (503, 504, timeout)

### QuantumLeap Integration

**Every query to QL must:**
- ✅ Specify entity type and ID
- ✅ Handle time-series responses correctly
- ✅ Expect ISO 8601 timestamps
- ✅ Validate that TimescaleDB data exists before querying
- ✅ Log query timing for performance monitoring

### MQTT (IoT Agent)

**Every sensor/simulator publishing to MQTT must:**
- ✅ Use documented topic naming convention: `devices/{deviceId}/{sensor}`
- ✅ Publish valid JSON
- ✅ Include timestamp if possible
- ✅ Match IoT Agent JSON payload schema

### FastAPI Routes

**Every route must:**
- ✅ Have input validation (Pydantic models)
- ✅ Return typed responses
- ✅ Include HTTP status codes (200, 201, 400, 404, 500, etc.)
- ✅ Include docstrings with description, parameters, returns
- ✅ Log request start/end with duration
- ✅ Handle errors gracefully with meaningful messages

---

## 🌍 Multipurpose Galicia Context Rules

### Scope is Multipurpose, Not Single-Port

**Every feature must work for multiple ports simultaneously.**

Rules:
- ✅ Query operations support filtering by `portId`
- ✅ Dashboards show aggregated views across ports
- ✅ Alerts respect port-specific thresholds
- ✅ Forecasting trains per-port or global with port dimension
- ✅ No hardcoded port IDs in code (use configuration)

### Real-Time Requirements

**The system is real-time first.**

Rules:
- ✅ Data updates propagate within seconds
- ✅ WebSocket connections broadcast changes to frontend
- ✅ Sensors emit data continuously (not batch)
- ✅ Dashboards reflect state within 5-10 seconds of change
- ✅ No 1-hour ETL batches unless explicitly for historical analytics

### Geospatial Context

**All ports and facilities have geographic data.**

Rules:
- ✅ Use GeoProperty for locations
- ✅ Support geographic queries (within radius, bounding box)
- ✅ Store coordinates in WGS84 (lat/long)
- ✅ Map visualization uses Leaflet + OpenStreetMap

---

## 🛠️ Development Workflow

### Starting a Feature

```
1. Create branch: git checkout -b feature/[name]
2. Add to docs/PRD.md if new requirement
3. Implement feature respecting all rules above
4. Write tests (pytest coverage >80%)
5. Update data_model.md if entities changed
6. Update architecture.md if services changed
7. Create PR with description linking PRD/architecture
```

### Code Review Checklist

Before merging, verify:
- ✅ NGSI-LD compliance (if entities touched)
- ✅ Tests pass: `pytest --cov`
- ✅ No hardcoded secrets
- ✅ Logging present (no print statements)
- ✅ Error handling present
- ✅ Documentation updated (PRD, data_model, architecture, README)
- ✅ No contradict between code and docs
- ✅ Commit messages are clear and reference issues

### Deployment Checklist

Before production push:
- ✅ All tests pass
- ✅ docker-compose up validates
- ✅ All environment variables documented in .env.example
- ✅ Health checks working
- ✅ Metrics/logs configured
- ✅ No TODOs or FIXMEs in critical paths

---

## 📊 Continuous Integration & Deployment

**GitHub/GitLab Actions expected (future):**
- ✅ Run pytest on every push
- ✅ Check code style (black, flake8, isort)
- ✅ Validate docker-compose.yml
- ✅ Build and push Docker images
- ✅ Deploy to staging on main branch

---

## 🚫 Anti-Patterns (Never Do These)

| Anti-Pattern | Why Forbidden | Alternative |
|--------------|---------------|-------------|
| Hardcoding URLs | Breaks in different envs | Use .env + config.py |
| Using NGSIv2 | Not future-proof | Always use NGSI-LD |
| print() for logging | No context, no levels | Use logging module |
| Bare exceptions | Masks real errors | Catch specific exceptions |
| Ignoring Orion errors | Silent failures | Log + retry + alert |
| Undocumented entities | Loss of traceability | Always document in data_model.md |
| Single-port design | Not scalable | Design for multipurpose from start |
| Static seed data | Not realistic | Simulate live data flows |
| No tests | Technical debt | Minimum 80% coverage |
| Outdated docs | Confusion | Update docs same session |

---

## 🎓 Learning Resources

### FIWARE
- https://www.fiware.org
- https://fiware-tutorials.readthedocs.io

### NGSI-LD
- Spec: https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf
- Introduction: https://ngsi-ld-tutorials.readthedocs.io

### Smart Data Models
- Portal: https://smartdatamodels.org
- GitHub: https://github.com/smart-data-models
- Ports: https://github.com/smart-data-models/dataModel.Ports

### Galician Ports
- Portos de Galicia: https://portosdegalicia.gal
- Puertos del Estado: https://www.puertos.es
- Law: https://www.boe.es/buscar/act.php?id=BOE-A-2018-1750

---

## 📞 Questions / Clarifications

If ambiguity arises:
1. Consult `docs/architecture.md` for system design
2. Consult `docs/PRD.md` for feature scope
3. Consult `docs/data_model.md` for entity structure
4. Check Smart Data Models official repo
5. Document decision in code/docs for future reference

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-27 | Initial comprehensive governance document |

---

**Last Review:** 2026-04-27  
**Next Review:** After Phase 1 completion  
**Status:** ACTIVE - Binding for all contributors
