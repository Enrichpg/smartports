# SmartPort Galicia — Backend Data Model Implementation

**Version:** 2.0  
**Date:** 2026-04-28  
**Status:** Operational  
**Scope:** Domain business layer with state machines and validation

---

## Executive Summary

This document describes the **operational data model** as implemented in the SmartPort backend. The backend exposes a clean REST API over the NGSI-LD context layer (Orion-LD), implementing business rules, state machines, and domain validations.

### Key Design Decisions

- **Orion-LD as source of truth:** All entities stored in Orion-LD, exposed via domain API
- **State machines:** Explicit validation for Berth and PortCall transitions
- **Authorization validation:** Mandatory checks with insurance support
- **Availability management:** Automatic recalculation from berth states
- **Alert generation:** Rule-based detection of port operational issues

---

## 1. State Machines

### 1.1 Berth State Machine

Berth operational states and valid transitions:

```
STATES:
- free       → Available for assignment
- reserved   → Tentatively assigned, not occupied
- occupied   → Currently occupied by a vessel
- outOfService → Unavailable (maintenance, inspection, etc.)

VALID TRANSITIONS:
┌─────────────────────────────────────────────────────┐
│                  State Diagram                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│   free ───→ reserved                                │
│    ↑         ↓                                      │
│    │         occupied ─────┐                        │
│    │         ↑             │                        │
│    └─────────┴─────────────┘                        │
│                             ↓                       │
│              outOfService ──→ free                  │
│                                                     │
└─────────────────────────────────────────────────────┘

Transitions:
  free          → reserved, occupied, outOfService
  reserved      → free, occupied, outOfService
  occupied      → free, outOfService
  outOfService  → free
  (Terminal: no transitions unless explicitly freed)
```

**Implementation:** [BerthService.VALID_TRANSITIONS](backend/services/berth_service.py)

**Example Flow:**
1. New berth created → `free`
2. Vessel assignment request → `reserved`
3. Vessel arrives and moors → `occupied`
4. Vessel departs → `free` (handled by PortCall closure)
5. Maintenance needed → `outOfService` (requires authorization)
6. Maintenance complete → `free`

---

### 1.2 PortCall State Machine

PortCall lifecycle states:

```
STATES:
- scheduled  → Planned visit (reservation)
- expected   → Arrival imminent (ETA confirmed)
- active     → Vessel currently at port
- completed  → Visit finished successfully
- cancelled  → Visit cancelled

VALID TRANSITIONS:
┌──────────────────────────────────────────────────┐
│          PortCall Lifecycle                      │
├──────────────────────────────────────────────────┤
│                                                  │
│   scheduled ──→ expected                         │
│       ↓ ┌────┬──────────┐                        │
│       │ │    │          │                        │
│  cancelled expected →  active → completed       │
│       ↑ │    │          │                        │
│       │ └────┴──────────┘                        │
│       └──────────────────────────────────────────│
│                                                  │
└──────────────────────────────────────────────────┘

Transitions:
  scheduled → expected, cancelled
  expected  → active, cancelled
  active    → completed, cancelled
  completed → (terminal)
  cancelled → (terminal)
```

**Implementation:** [PortCallService.VALID_TRANSITIONS](backend/services/portcall_service.py)

**Example Flow:**
1. Booking created → `scheduled`
2. Vessel departure confirmed → `expected`
3. Vessel arrives at pilot station → `active` (marks actual arrival)
4. Berth is freed on departure → `completed` (marks actual departure)

**Special Handling:**
- Status change to `active` automatically records `actualArrival` timestamp
- `close_portcall()` operation transitions to `completed` and records `actualDeparture`
- Berth is automatically freed when PortCall is closed

---

## 2. Authorization System

### 2.1 Authorization Status

Vessel authorization states:

```
Status Values:
- authorized      → Valid and active
- expired         → Authorization date has passed
- revoked         → Explicitly revoked by authority
- pending         → Application under review
- unauthorized    → No valid authorization exists
```

### 2.2 Validation Rules

**Authorization Validation Checks:**

1. **Existence:** Authorization record must exist
2. **Status:** Must not be `revoked`
3. **Expiration:** Current date must be before `expirationDate`
4. **Insurance:** If checked, `insuranceValid` must be `true` and `insuranceExpiration` must be future
5. **Port-Specific:** If checking for specific port, must not be port-restricted

**Implementation:** [AuthorizationService.validate_vessel_authorization()](backend/services/authorization_service.py)

**Example Validation Response:**

```json
{
  "is_authorized": true,
  "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
  "vessel_name": "MSC Example",
  "status": "authorized",
  "reason": null,
  "details": {
    "expiration_date": "2027-12-31T23:59:59Z",
    "insurance_valid": true,
    "insurance_expiration": "2027-06-30T23:59:59Z"
  }
}
```

---

## 3. Availability Management

### 3.1 Availability Calculation

Availability is **computed from current berth states**:

**Formula:**
```
For each port:
  by_category = group berths by category
  for category in categories:
    available_count = count(berths with status='free')
    total_in_category = count(berths)
    availability_rate = (available_count / total_in_category) * 100
    
  total_availability = sum(available_count) / sum(total_in_category) * 100
```

### 3.2 Recalculation Trigger

Availability is recalculated:
1. **On demand:** GET `/api/v1/availability/ports/{port_id}`
2. **After berth state change:** PATCH `/api/v1/berths/{berth_id}/status`
3. **Explicit recalculation:** POST `/api/v1/availability/recalculate/{port_id}`

### 3.3 BoatPlacesAvailable Entity

Stores availability summary by category:

**Attributes:**
- `portId` → Relationship to Port
- `category` → Berth category (general, container, tanker, etc.)
- `availabilityCount` → Number of free berths
- `totalBerthsInCategory` → Total berths in category
- `averageDepth` → Average depth of free berths
- `lastUpdated` → Timestamp of last calculation

**Example Response:**

```json
{
  "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
  "port_name": "Puerto de A Coruña",
  "total_available_berths": 3,
  "total_berths": 8,
  "availability_rate": 37.5,
  "by_category": [
    {
      "id": "urn:smartdatamodels:BoatPlacesAvailable:CorA:general",
      "category": "general_cargo",
      "availability_count": 2,
      "total_berths_in_category": 3,
      "average_depth": 12.3
    },
    {
      "id": "urn:smartdatamodels:BoatPlacesAvailable:CorA:container",
      "category": "container",
      "availability_count": 1,
      "total_berths_in_category": 2,
      "average_depth": 14.1
    }
  ],
  "last_recalculated": "2026-04-28T12:00:00"
}
```

---

## 4. Alert Types and Triggers

### 4.1 Alert Types

| Alert Type | Severity | Trigger |
|------------|----------|---------|
| `authorization_failed` | CRITICAL | PortCall creation blocked due to failed authorization |
| `authorization_expired` | CRITICAL | Vessel authorization expired |
| `insurance_expired` | WARNING | Insurance validity check failed |
| `berth_conflict` | CRITICAL | Multiple PortCalls assigned to same berth |
| `occupancy_high` | WARNING | Port occupancy ≥ 75% |
| `occupancy_full` | CRITICAL | Port occupancy ≥ 90% (or all berths occupied) |
| `berth_out_of_service` | ERROR | Berth status → outOfService |
| `vessel_not_found` | ERROR | Referenced vessel doesn't exist |
| `invalid_vessel_size` | WARNING | Vessel exceeds berth capacity |
| `operational` | INFO | General operational notification |

### 4.2 Alert Lifecycle

```
Alert States:
- Active
- Acknowledged (acknowledgedAt, acknowledgedBy set)
- Resolved (resolvedAt set, isActive=false)

Operations:
- Create: Triggered by check_port_alerts()
- Acknowledge: PATCH /{alert_id}/acknowledge
- Resolve: PATCH /{alert_id}/resolve
- Query: GET /alerts, GET /ports/{port_id}/alerts
```

**Implementation:** [AlertService](backend/services/alert_service.py)

---

## 5. Domain Entities & API Contracts

### 5.1 Port Entity

**Endpoints:**
- `GET /api/v1/ports` - List all ports
- `GET /api/v1/ports/{port_id}` - Get port details
- `GET /api/v1/ports/{port_id}/summary` - Get operational summary with KPIs

**Response Model:** [PortResponse](backend/schemas/port.py)

### 5.2 Berth Entity

**Endpoints:**
- `GET /api/v1/berths?port_id={port_id}` - List berths by port
- `GET /api/v1/berths/{berth_id}` - Get berth details
- `PATCH /api/v1/berths/{berth_id}/status` - Change berth status

**Response Model:** [BerthResponse](backend/schemas/berth.py)

**Status Change Validation:**
- Validates state transition
- Checks for berth conflicts
- Updates Orion-LD entity

### 5.3 PortCall Entity

**Endpoints:**
- `GET /api/v1/portcalls` - List all PortCalls
- `POST /api/v1/portcalls` - Create new PortCall
- `PATCH /api/v1/portcalls/{portcall_id}/status` - Change status
- `POST /api/v1/portcalls/{portcall_id}/close` - Close visit

**Response Model:** [PortCallResponse](backend/schemas/portcall.py)

**Creation Validation:**
- Validates vessel authorization
- Checks insurance validity
- Validates berth availability (if specified)

### 5.4 Authorization Entity

**Endpoints:**
- `GET /api/v1/authorizations/{vessel_id}` - Get authorization
- `POST /api/v1/authorizations/validate` - Validate authorization

**Response Models:** [AuthorizationResponse](backend/schemas/authorization.py)

### 5.5 Vessel Entity

**Endpoints:**
- `GET /api/v1/vessels` - List all vessels
- `GET /api/v1/vessels/{vessel_id}` - Get vessel details
- `GET /api/v1/vessels/imo/{imo_number}` - Lookup by IMO

**Response Model:** [VesselResponse](backend/schemas/vessel.py)

### 5.6 Availability Entity

**Endpoints:**
- `GET /api/v1/availability/ports/{port_id}` - Get port availability
- `POST /api/v1/availability/recalculate/{port_id}` - Recalculate availability

**Response Model:** [AvailabilitySummaryResponse](backend/schemas/availability.py)

### 5.7 Alert Entity

**Endpoints:**
- `GET /api/v1/alerts` - List alerts
- `POST /api/v1/alerts` - Check and generate alerts
- `PATCH /api/v1/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `PATCH /api/v1/alerts/{alert_id}/resolve` - Resolve alert

**Response Model:** [AlertResponse](backend/schemas/alert.py)

---

## 6. Business Rules Enforced

### 6.1 Berth Management Rules

✅ Cannot transition from occupied → reserved  
✅ Cannot assign occupied berth to new PortCall  
✅ Cannot mark berth occupied without valid PortCall  
✅ Closing PortCall automatically frees berth  

### 6.2 PortCall Lifecycle Rules

✅ Cannot create PortCall for unauthorized vessel  
✅ Cannot activate PortCall if authorization expired  
✅ Cannot activate PortCall if insurance invalid  
✅ Cannot transition from active → expected  
✅ Cannot assign unavailable berth  

### 6.3 Authorization Rules

✅ Expired authorization blocks PortCall creation  
✅ Revoked authorization always fails validation  
✅ Insurance expiration checked on validation  
✅ Port-specific restrictions enforced  

### 6.4 Availability Rules

✅ Recalculation uses current berth states  
✅ Available count = berths with status='free'  
✅ Category grouping by berth.category attribute  
✅ Occupancy rate = (occupied+reserved) / total  

---

## 7. Service Layer Architecture

```
API Routes Layer
    ↓
[Domain Services]
    - PortService
    - BerthService
    - AvailabilityService
    - VesselService
    - AuthorizationService
    - PortCallService
    - AlertService
    ↓
[Orion-LD Client]
    - NGSI-LD queries/updates
    - Entity creation/deletion
    - Relationship management
    ↓
Orion-LD Context Broker
```

Each service:
1. Enforces business logic
2. Validates state transitions
3. Manages Orion-LD entities
4. Returns consistent schemas

---

## 8. Implementation Status

**Completed:**
- ✅ State machines (Berth, PortCall)
- ✅ Authorization validation system
- ✅ Availability calculation engine
- ✅ Alert generation framework
- ✅ All domain services (7 services)
- ✅ REST API endpoints (all routes)
- ✅ Pydantic schemas (100% coverage)
- ✅ Unit tests (critical paths)

**In Progress:**
- 🔄 Integration tests
- 🔄 Performance optimization

**Future:**
- 🔜 PostgreSQL audit trail
- 🔜 WebSocket real-time updates
- 🔜 Celery background tasks for alerts
- 🔜 Cache layer (Redis)

