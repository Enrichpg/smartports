# SmartPort Galicia — Backend Implementation Guide

**Version:** 1.0  
**Date:** 2026-04-28  
**Status:** Operational  

---

## Overview

The SmartPort backend is a **domain business API** built on FastAPI that exposes operational intelligence over Orion-LD. It manages:

✅ Port and facility inventory  
✅ Berth lifecycle with state machines  
✅ Real-time availability calculation  
✅ Vessel authorization and validation  
✅ Port call management (visit lifecycle)  
✅ Operational alerts and monitoring  

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file with critical settings:

```env
# Server
ENVIRONMENT=development
DEBUG=true
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Orion-LD
ORION_BASE_URL=http://localhost:1026
FIWARE_SERVICE=smartports
FIWARE_SERVICE_PATH=/Galicia

# Database (if needed)
DATABASE_URL=postgresql://user:pass@localhost/smartports
```

### 3. Run Backend

```bash
# Development (with auto-reload)
python main.py

# With uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## Project Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration management
├── requirements.txt           # Dependencies
│
├── api/
│   ├── __init__.py
│   ├── health.py              # Health check endpoints
│   ├── v1.py                  # API v1 router
│   └── routes/                # Domain-specific routes
│       ├── __init__.py
│       ├── ports.py           # Port endpoints
│       ├── berths.py          # Berth endpoints
│       ├── availability.py    # Availability endpoints
│       ├── vessels.py         # Vessel & authorization endpoints
│       ├── portcalls.py       # PortCall endpoints
│       └── alerts.py          # Alert endpoints
│
├── schemas/                   # Pydantic data models
│   ├── __init__.py
│   ├── common.py              # Common schemas & base classes
│   ├── port.py                # Port schemas
│   ├── berth.py               # Berth schemas
│   ├── availability.py        # Availability schemas
│   ├── vessel.py              # Vessel schemas
│   ├── authorization.py       # Authorization schemas
│   ├── portcall.py            # PortCall schemas
│   └── alert.py               # Alert schemas
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── orion_ld_client.py     # Orion-LD HTTP client
│   ├── port_service.py        # Port operations
│   ├── berth_service.py       # Berth management (state machines)
│   ├── availability_service.py # Availability calculation
│   ├── vessel_service.py      # Vessel queries
│   ├── authorization_service.py # Authorization validation
│   ├── portcall_service.py    # PortCall lifecycle
│   └── alert_service.py       # Alert generation
│
└── tests/                     # Unit tests
    ├── conftest.py            # Pytest fixtures
    ├── test_domain_logic.py   # State machines, validation logic
    └── test_*.py              # Per-service tests
```

---

## Architecture Layers

```
                          Browser / Dashboard
                                 ↓
                    ┌───────────────────────┐
                    │   REST API (FastAPI)  │
                    │   :8000/api/v1        │
                    └───────────────────────┘
                                 ↓
    ┌─────────────────────────────────────────────────────────┐
    │          API Routes Layer                              │
    │  /ports  /berths  /availability  /vessels  /portcalls │
    │  /authorizations  /alerts                             │
    └─────────────────────────────────────────────────────────┘
                                 ↓
    ┌─────────────────────────────────────────────────────────┐
    │        Domain Services (Business Logic)                │
    │  • PortService                                         │
    │  • BerthService (state machine)                       │
    │  • AvailabilityService (recalculation)                │
    │  • VesselService                                      │
    │  • AuthorizationService (validation)                  │
    │  • PortCallService (lifecycle management)             │
    │  • AlertService (rule-based alerts)                   │
    └─────────────────────────────────────────────────────────┘
                                 ↓
    ┌─────────────────────────────────────────────────────────┐
    │       Orion-LD Client (NGSI-LD Operations)             │
    │  query_entities()  get_entity()  create_entity()      │
    │  update_entity()   upsert_entity()  delete_entity()   │
    └─────────────────────────────────────────────────────────┘
                                 ↓
                    ┌───────────────────────┐
                    │   Orion-LD (Port 1026)│
                    │   NGSI-LD Context    │
                    │   Broker             │
                    └───────────────────────┘
```

---

## Service Layer Details

### 1. OrionLDClient (`services/orion_ld_client.py`)

Low-level HTTP client for Orion-LD interactions.

**Key Methods:**
```python
query_entities()          # Query by type, ID, or filter
get_entity()              # Get single entity by ID
create_entity()           # Create new entity
update_entity()           # Update entity attributes (PATCH)
upsert_entity()           # Create or update
delete_entity()           # Delete entity
query_by_type()           # Query all of specific type
query_by_relationship()   # Relationship traversal
health_check()            # Connection test
```

### 2. PortService (`services/port_service.py`)

Port management and operational queries.

**Operations:**
- `get_all_ports()` - List all ports
- `get_port_by_id()` - Fetch specific port
- `get_port_summary()` - Generate KPIs (occupancy, alerts, etc.)

### 3. BerthService (`services/berth_service.py`)

Berth lifecycle with state machine validation.

**State Machine:**
```
free ←→ reserved ←→ occupied ←→ outOfService
  ↑                  ↓
  └──────────────────┘
```

**Operations:**
- `get_berths_by_port()` - List port's berths
- `get_berth_by_id()` - Fetch berth details
- `change_berth_status()` - State transition with validation
- `get_available_berths()` - Free berths only

**Validations:**
- Prevents invalid transitions
- Checks for conflicts (multiple PortCalls)
- Updates Orion-LD state

### 4. AvailabilityService (`services/availability_service.py`)

Berth availability calculation and management.

**Operations:**
- `get_port_availability()` - Compute availability from berth states
- `recalculate_port_availability()` - Update BoatPlacesAvailable entities
- `get_facility_availability()` - Facility-level availability

**Formula:**
```
For each category in port:
  available = count(berths with status='free')
  total = count(berths)
  rate = (available / total) * 100
```

### 5. VesselService (`services/vessel_service.py`)

Vessel registry queries.

**Operations:**
- `get_all_vessels()` - List all vessels
- `get_vessel_by_id()` - Fetch vessel
- `get_vessel_by_imo()` - Lookup by IMO number
- `get_vessels_by_type()` - Filter by type

### 6. AuthorizationService (`services/authorization_service.py`)

**Critical:** Authorization validation with insurance checks.

**Operations:**
- `get_vessel_authorization()` - Get authorization record
- `validate_vessel_authorization()` - **Validation logic**
- `get_all_authorizations()` - List authorizations

**Validation Checks:**
1. Authorization exists
2. Status not `revoked`
3. Date not expired (`expirationDate` > now)
4. Insurance valid (if `check_insurance=True`)
5. Insurance not expired

### 7. PortCallService (`services/portcall_service.py`)

**Critical:** PortCall lifecycle management.

**State Machine:**
```
scheduled → expected → active → completed
   ↓          ↓          ↓
   └──────────┴──────────→ cancelled
```

**Operations:**
- `create_portcall()` - Create visit (validates authorization, berth)
- `get_portcall_by_id()` - Fetch PortCall
- `get_active_portcalls()` - Get active visits
- `change_portcall_status()` - State transition
- `close_portcall()` - End visit (frees berth, records departure)

**Critical Checks:**
- Vessel must be authorized
- Insurance must be valid
- Berth must be available (if assigned)
- State transitions must be valid

### 8. AlertService (`services/alert_service.py`)

Rule-based operational alert generation.

**Alert Types:**
- `authorization_failed` - CRITICAL
- `authorization_expired` - CRITICAL
- `insurance_expired` - WARNING
- `berth_conflict` - CRITICAL
- `occupancy_high` (≥75%) - WARNING
- `occupancy_full` (≥90%) - CRITICAL
- `berth_out_of_service` - ERROR

**Operations:**
- `check_port_alerts()` - Generate alerts for port
- `get_port_alerts()` - Query port alerts
- `acknowledge_alert()` - Mark as seen
- `resolve_alert()` - Mark as resolved

---

## Key Business Rules

### Authorization Rules
❌ Cannot create PortCall for unauthorized vessel  
❌ Cannot use expired authorization  
❌ Cannot use revoked authorization  
❌ Cannot proceed if insurance expired  

### Berth Rules
❌ Cannot transition to invalid state  
❌ Cannot assign occupied berth  
❌ Cannot assign out-of-service berth  
✅ Closing PortCall automatically frees berth  

### PortCall Rules
❌ Cannot change status to invalid transition  
❌ Cannot change status without authorization  
✅ Transition to ACTIVE records actual arrival  
✅ Closing records actual departure  

### Availability Rules
✅ Calculated from current berth states  
✅ Grouped by berth category  
✅ Includes average depth per category  
✅ Recalculated after berth state changes  

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/ports` | List ports |
| GET | `/api/v1/ports/{port_id}` | Get port details |
| GET | `/api/v1/ports/{port_id}/summary` | Get KPIs |
| GET | `/api/v1/berths` | List berths (filtered) |
| GET | `/api/v1/berths/{berth_id}` | Get berth details |
| PATCH | `/api/v1/berths/{berth_id}/status` | Change status |
| GET | `/api/v1/availability/ports/{port_id}` | Get availability |
| POST | `/api/v1/availability/recalculate/{port_id}` | Recalculate |
| GET | `/api/v1/vessels` | List vessels |
| GET | `/api/v1/vessels/{vessel_id}` | Get vessel |
| GET | `/api/v1/authorizations/{vessel_id}` | Get authorization |
| POST | `/api/v1/authorizations/validate` | **Validate authorization** |
| GET | `/api/v1/portcalls` | List PortCalls |
| POST | `/api/v1/portcalls` | **Create PortCall** |
| PATCH | `/api/v1/portcalls/{portcall_id}/status` | Change status |
| POST | `/api/v1/portcalls/{portcall_id}/close` | Close visit |
| GET | `/api/v1/alerts` | List alerts |
| POST | `/api/v1/alerts` | Check/generate alerts |

---

## Testing

### Run Tests

```bash
cd backend
pytest tests/ -v

# Specific test class
pytest tests/test_domain_logic.py::TestBerthStateTransitions -v

# With coverage
pytest --cov=services tests/
```

### Test Coverage

**Implemented Tests:**
✅ Berth state transitions (6 tests)  
✅ PortCall state transitions (5 tests)  
✅ Authorization validation (3 tests)  
✅ Availability calculation (4 tests)  
✅ Alert generation (3 tests)  
✅ PortCall ID generation (2 tests)  

**Total:** 23 tests for critical business logic

### Test Fixtures

Fixtures in `tests/conftest.py`:
- `mock_orion_client`
- `sample_port_entity`
- `sample_berth_entity`
- `sample_vessel_entity`
- `sample_authorization_entity`
- `sample_portcall_entity`
- `sample_alert_entity`

---

## Development Workflow

### 1. Adding a New Endpoint

```python
# 1. Create schema in schemas/
# 2. Implement service method in services/
# 3. Create route in api/routes/domain.py
# 4. Add tests in tests/

# Example: New endpoint for facility info
# File: backend/api/routes/facilities.py
@router.get("/facilities/{facility_id}")
async def get_facility(facility_id: str):
    facility = await facility_service.get_facility_by_id(facility_id)
    return facility
```

### 2. Adding Business Logic

```python
# File: backend/services/custom_service.py
class CustomService:
    async def do_something(self, entity_id: str):
        # Validate input
        if not entity_id:
            raise ValueError("entity_id required")
        
        # Query Orion-LD
        entity = await orion_client.get_entity(entity_id)
        
        # Apply business logic
        result = self._apply_rule(entity)
        
        # Update Orion-LD if needed
        await orion_client.update_entity(entity_id, result)
        
        return result
```

### 3. Error Handling

```python
# Use domain-specific exceptions
class BerthStateError(Exception):
    """Raised for invalid berth state transition"""
    pass

class AuthorizationError(Exception):
    """Raised for authorization failures"""
    pass

# In routes, convert to HTTP responses
try:
    berth = await berth_service.change_berth_status(berth_id, new_status)
except BerthStateError as e:
    raise HTTPException(status_code=409, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

---

## Environment Variables

### Required

```env
ORION_BASE_URL          # Orion-LD URL (http://localhost:1026)
FIWARE_SERVICE          # Service name (smartports)
FIWARE_SERVICE_PATH     # Service path (/Galicia)
```

### Optional

```env
ENVIRONMENT             # development, production
DEBUG                   # true, false
LOG_LEVEL              # INFO, DEBUG, WARNING, ERROR
DATABASE_URL           # PostgreSQL connection
REDIS_URL              # Redis connection
CELERY_BROKER_URL      # Celery broker
ENABLE_PROMETHEUS      # Enable Prometheus metrics
```

---

## Troubleshooting

### Orion-LD Connection Failed

```
Error: Orion-LD request failed: Connection refused
```

**Solution:**
```bash
# Check Orion-LD is running
docker ps | grep orion

# Verify URL in .env
cat .env | grep ORION_BASE_URL

# Test connection
curl http://localhost:1026/ngsi-ld/v1/entities?limit=1
```

### Authorization Validation Always Fails

```
Response: is_authorized=false, reason="No authorization found"
```

**Solution:**
1. Verify BoatAuthorized entity exists in Orion-LD
2. Check vessel_id matches in BoatAuthorized
3. Verify expirationDate is in future
4. Check insuranceValid is true

### Tests Failing

```bash
# Run with verbose output
pytest -vv tests/test_domain_logic.py

# Show print statements
pytest -s tests/test_domain_logic.py

# Run single test
pytest tests/test_domain_logic.py::TestBerthStateTransitions::test_valid_transition_free_to_occupied -vv
```

---

## Production Deployment

### Security Checklist

- [ ] Set `DEBUG=false`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/TLS
- [ ] Restrict `ALLOWED_HOSTS`
- [ ] Add authentication (JWT)
- [ ] Add rate limiting
- [ ] Enable CORS for specific origins only
- [ ] Setup audit logging
- [ ] Configure Prometheus monitoring

### Performance Optimization

- [ ] Enable Redis caching
- [ ] Add query result caching
- [ ] Implement pagination properly
- [ ] Use connection pooling
- [ ] Setup load balancing
- [ ] Monitor Orion-LD query performance
- [ ] Consider denormalization for hot paths

---

## Next Steps

1. **Frontend Integration:** Use API endpoints for dashboard
2. **ML Integration:** Feed historical data to forecasting models
3. **Real-time Updates:** Add WebSocket support for live updates
4. **Audit Trail:** Store all operations in PostgreSQL
5. **Advanced Alerts:** Integrate with notification system
6. **Analytics:** Build on QuantumLeap time-series data

---

## Documentation

- [API Reference](./API_REFERENCE.md) - Full endpoint documentation
- [Data Model](./data_model_backend.md) - Entity definitions and state machines
- [Architecture](./architecture.md) - System architecture overview
- [PRD](./PRD.md) - Project requirements

---

## Support

For issues or questions:
1. Check relevant test files for usage examples
2. Review service implementations for business logic
3. Consult API_REFERENCE.md for endpoint details
4. Check Orion-LD logs for entity issues

