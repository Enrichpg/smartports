# SmartPort Galicia — Backend API Reference

**Version:** 1.0  
**Date:** 2026-04-28  
**Status:** Operational  
**Base URL:** `http://localhost:8000/api/v1`

---

## Table of Contents

1. [Ports API](#ports-api)
2. [Berths API](#berths-api)
3. [Availability API](#availability-api)
4. [Vessels & Authorizations API](#vessels--authorizations-api)
5. [PortCalls API](#portcalls-api)
6. [Alerts API](#alerts-api)
7. [Error Handling](#error-handling)
8. [Authentication & Security](#authentication--security)

---

## Ports API

### GET /ports

List all ports in the Galician network.

**Query Parameters:**
- `limit` (int, default=20): Max items per page (1-100)
- `offset` (int, default=0): Pagination offset

**Response (200 OK):**
```json
{
  "ports": [
    {
      "id": "urn:smartdatamodels:Port:Galicia:CorA",
      "name": "Puerto de A Coruña",
      "country": "ES",
      "location": {
        "type": "GeoProperty",
        "value": {
          "type": "Point",
          "coordinates": [-8.384, 43.371]
        }
      },
      "url": "https://www.puertocoruna.es",
      "imo": "ESCOR"
    }
  ],
  "total": 11,
  "limit": 20,
  "offset": 0
}
```

**Error Responses:**
- `500 Internal Server Error`: Failed to fetch ports

---

### GET /ports/{port_id}

Get detailed information about a specific port.

**Path Parameters:**
- `port_id` (string): Port URN ID

**Response (200 OK):**
```json
{
  "id": "urn:smartdatamodels:Port:Galicia:CorA",
  "name": "Puerto de A Coruña",
  "country": "ES",
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.384, 43.371]
    }
  },
  "url": "https://www.puertocoruna.es",
  "imo": "ESCOR",
  "dbpedia": "https://dbpedia.org/resource/Port_of_A_Coru%C3%B1a",
  "description": "Port of A Coruña"
}
```

**Error Responses:**
- `404 Not Found`: Port not found

---

### GET /ports/{port_id}/summary

Get operational summary of a port with KPIs.

**Path Parameters:**
- `port_id` (string): Port URN ID

**Response (200 OK):**
```json
{
  "id": "urn:smartdatamodels:Port:Galicia:CorA",
  "name": "Puerto de A Coruña",
  "total_berths": 5,
  "berths_free": 2,
  "berths_occupied": 2,
  "berths_reserved": 1,
  "berths_out_of_service": 0,
  "occupancy_rate": 40.0,
  "active_vessels": 2,
  "active_alerts": 1,
  "last_updated": "2026-04-28T12:00:00"
}
```

**Usage Examples:**
- Dashboard real-time KPI updates
- Occupancy rate trending
- Alert threshold detection

---

## Berths API

### GET /berths

List berths with optional filtering.

**Query Parameters:**
- `port_id` (string, optional): Filter by port ID
- `facility_id` (string, optional): Filter by facility ID
- `limit` (int): Max items (default 20)
- `offset` (int): Pagination offset (default 0)

**Response (200 OK):**
```json
{
  "berths": [
    {
      "id": "urn:smartdatamodels:Berth:CorA:berth_A1",
      "name": "A1",
      "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
      "facility_id": "urn:smartdatamodels:SeaportFacilities:CorA:general_dock",
      "berth_type": "general_cargo",
      "status": "occupied",
      "depth": 12.5,
      "length": 200.0,
      "draft_limit": 11.0,
      "category": "general",
      "active_portcall_id": "urn:smartdatamodels:PortCall:Galicia:...",
      "last_status_change": "2026-04-28T10:00:00"
    }
  ],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

**Error Responses:**
- `400 Bad Request`: Must specify port_id or facility_id
- `500 Internal Server Error`: Failed to fetch berths

---

### GET /berths/{berth_id}

Get detailed information about a berth.

**Path Parameters:**
- `berth_id` (string): Berth URN ID

**Response (200 OK):**
```json
{
  "berth": {
    "id": "urn:smartdatamodels:Berth:CorA:berth_A1",
    "name": "A1",
    "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
    "status": "occupied",
    "depth": 12.5,
    "length": 200.0,
    "draft_limit": 11.0,
    "category": "general",
    "active_portcall_id": "urn:smartdatamodels:PortCall:Galicia:...",
    "last_status_change": "2026-04-28T10:00:00"
  },
  "port_name": "Puerto de A Coruña",
  "facility_name": "General Dock",
  "current_vessel": {
    "status": "occupied"
  },
  "can_accommodate_size": null
}
```

---

### PATCH /berths/{berth_id}/status

Change berth operational status with state machine validation.

**Path Parameters:**
- `berth_id` (string): Berth URN ID

**Request Body:**
```json
{
  "new_status": "outOfService",
  "reason": "Scheduled maintenance",
  "operator_id": "urn:smartdatamodels:PortAuthority:CorA:operator_001"
}
```

**Valid Status Values:**
- `free`: Available for assignment
- `reserved`: Reserved but not yet occupied
- `occupied`: Currently occupied
- `outOfService`: Unavailable (maintenance, inspection, etc.)

**Response (200 OK):**
```json
{
  "id": "urn:smartdatamodels:Berth:CorA:berth_A1",
  "name": "A1",
  "status": "outOfService",
  "last_status_change": "2026-04-28T12:30:00"
}
```

**Error Responses:**
- `409 Conflict`: Invalid state transition or berth conflict
- `404 Not Found`: Berth not found

---

## Availability API

### GET /availability/ports/{port_id}

Get availability summary for a port.

**Path Parameters:**
- `port_id` (string): Port URN ID

**Response (200 OK):**
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
      "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
      "port_name": "Puerto de A Coruña",
      "category": "general_cargo",
      "availability_count": 2,
      "total_berths_in_category": 3,
      "average_depth": 12.3,
      "last_updated": "2026-04-28T12:00:00"
    }
  ],
  "last_recalculated": "2026-04-28T12:00:00"
}
```

---

### GET /availability/facilities/{facility_id}

Get availability summary for a specific facility.

**Path Parameters:**
- `facility_id` (string): Facility URN ID

**Response (200 OK):** Same structure as `/availability/ports/{port_id}`

---

### POST /availability/recalculate/{port_id}

Recalculate and update availability for a port.

**Path Parameters:**
- `port_id` (string): Port URN ID

**Query Parameters:**
- `force` (bool, default=false): Skip recent cache check

**Response (200 OK):** Updated availability summary

---

## Vessels & Authorizations API

### GET /vessels

List all registered vessels.

**Query Parameters:**
- `limit` (int): Max items (default 20)
- `offset` (int): Pagination offset

**Response (200 OK):**
```json
{
  "vessels": [
    {
      "id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
      "imo_number": "9876543",
      "mmsi": "224999999",
      "name": "MSC Example",
      "vessel_type": "container_ship",
      "length": 398.0,
      "width": 54.0,
      "draft": 15.5,
      "gross_tonnage": 98000,
      "deadweight_tonnage": 121000,
      "nationality": "IT",
      "operator": "Mediterranean Shipping Company",
      "status": "active"
    }
  ],
  "total": 500,
  "limit": 20,
  "offset": 0
}
```

---

### GET /vessels/{vessel_id}

Get details of a specific vessel.

**Path Parameters:**
- `vessel_id` (string): Vessel URN ID

**Response (200 OK):** Individual Vessel entity

---

### GET /vessels/imo/{imo_number}

Get vessel by IMO number.

**Path Parameters:**
- `imo_number` (string): IMO registration number

**Response (200 OK):** Individual Vessel entity

---

### GET /authorizations/{vessel_id}

Get authorization record for a vessel.

**Path Parameters:**
- `vessel_id` (string): Vessel URN ID

**Query Parameters:**
- `port_id` (string, optional): Port ID for port-specific authorization

**Response (200 OK):**
```json
{
  "id": "urn:smartdatamodels:BoatAuthorized:Galicia:imo9876543",
  "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
  "vessel_name": "MSC Example",
  "imo_number": "9876543",
  "status": "authorized",
  "issued_date": "2025-01-01T00:00:00",
  "expiration_date": "2027-12-31T23:59:59",
  "port_id": null,
  "certificate_number": "AUTH-2025-001",
  "issuing_authority": "Autoridad Portuaria de Galicia",
  "restrictions": null,
  "insurance_valid": true,
  "insurance_expiration": "2027-06-30T23:59:59"
}
```

---

### POST /authorizations/validate

Validate if a vessel is authorized to operate.

**Request Body:**
```json
{
  "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
  "imo_number": "9876543",
  "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
  "check_insurance": true
}
```

**Response (200 OK):**
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

**Response (200 OK - Not Authorized):**
```json
{
  "is_authorized": false,
  "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
  "vessel_name": "MSC Example",
  "status": "expired",
  "reason": "Authorization expired on 2026-04-15T00:00:00Z",
  "details": {
    "expiration_date": "2026-04-15T00:00:00Z"
  }
}
```

---

## PortCalls API

### GET /portcalls

List PortCalls with optional filtering.

**Query Parameters:**
- `port_id` (string, optional): Filter by port
- `active_only` (bool): Show only active PortCalls
- `limit` (int): Max items
- `offset` (int): Pagination offset

**Response (200 OK):**
```json
{
  "portcalls": [
    {
      "id": "urn:smartdatamodels:PortCall:Galicia:corA_20260430_imo9876543_abc123de",
      "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
      "vessel_name": "MSC Example",
      "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
      "port_name": "Puerto de A Coruña",
      "berth_id": "urn:smartdatamodels:Berth:CorA:berth_A1",
      "berth_name": "A1",
      "status": "active",
      "estimated_arrival": "2026-04-30T08:00:00",
      "estimated_departure": "2026-05-02T18:00:00",
      "actual_arrival": "2026-04-30T08:15:00",
      "actual_departure": null,
      "purpose": "load",
      "cargo_type": "containers",
      "created_at": "2026-04-28T10:00:00",
      "updated_at": "2026-04-30T08:15:00"
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

---

### POST /portcalls

Create a new PortCall (vessel visit).

**Request Body:**
```json
{
  "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
  "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
  "estimated_arrival": "2026-04-30T08:00:00",
  "estimated_departure": "2026-05-02T18:00:00",
  "berth_id": "urn:smartdatamodels:Berth:CorA:berth_A1",
  "purpose": "load",
  "cargo_type": "containers",
  "status": "scheduled"
}
```

**Response (201 Created):**
```json
{
  "id": "urn:smartdatamodels:PortCall:Galicia:corA_20260430_imo9876543_abc123de",
  "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
  "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
  "status": "scheduled",
  "estimated_arrival": "2026-04-30T08:00:00",
  "created_at": "2026-04-28T10:00:00",
  "updated_at": "2026-04-28T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Vessel not authorized, berth unavailable, etc.
- `500 Internal Server Error`: Failed to create PortCall

**Validation Checks:**
- Vessel authorization required
- Insurance must be valid
- Berth must be available (if specified)

---

### PATCH /portcalls/{portcall_id}/status

Change PortCall status with state machine validation.

**Path Parameters:**
- `portcall_id` (string): PortCall URN ID

**Request Body:**
```json
{
  "new_status": "active",
  "reason": "Vessel arrived on schedule",
  "operator_id": "urn:smartdatamodels:PortAuthority:CorA:operator_001"
}
```

**Valid Status Values:**
- `scheduled` → `expected`, `cancelled`
- `expected` → `active`, `cancelled`
- `active` → `completed`, `cancelled`
- `completed` (terminal)
- `cancelled` (terminal)

**Response (200 OK):** Updated PortCall entity

**Error Responses:**
- `409 Conflict`: Invalid state transition

---

### POST /portcalls/{portcall_id}/close

Close a PortCall (mark as completed and free berth).

**Path Parameters:**
- `portcall_id` (string): PortCall URN ID

**Request Body:**
```json
{
  "actual_departure": "2026-05-02T18:30:00",
  "notes": "Completed successfully",
  "operator_id": "urn:smartdatamodels:PortAuthority:CorA:operator_001"
}
```

**Response (200 OK):**
```json
{
  "id": "urn:smartdatamodels:PortCall:Galicia:corA_20260430_imo9876543_abc123de",
  "status": "completed",
  "actual_departure": "2026-05-02T18:30:00",
  "updated_at": "2026-05-02T18:30:00"
}
```

**Side Effects:**
- Berth is freed (status → `free`)
- PortCall status → `completed`

---

## Alerts API

### GET /alerts

List alerts with optional filtering.

**Query Parameters:**
- `port_id` (string, optional): Filter by port
- `active_only` (bool): Show only active alerts (default true)
- `limit` (int): Max items
- `offset` (int): Pagination offset

**Response (200 OK):**
```json
{
  "alerts": [
    {
      "id": "urn:smartdatamodels:Alert:CorA:alert_001",
      "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
      "port_name": "Puerto de A Coruña",
      "entity_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
      "entity_type": "Vessel",
      "alert_type": "authorization_expired",
      "severity": "critical",
      "title": "Vessel Authorization Expired",
      "description": "Vessel MSC Example authorization expired on 2026-04-15",
      "is_active": true,
      "created_at": "2026-04-28T10:00:00",
      "acknowledged_at": "2026-04-28T10:05:00",
      "acknowledged_by": "operator_001",
      "resolved_at": null
    }
  ],
  "total": 45,
  "active": 12,
  "limit": 20,
  "offset": 0
}
```

---

### POST /alerts

Check and generate alerts for a port.

**Request Body:**
```json
{
  "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
  "check_authorizations": true,
  "check_occupancy": true,
  "check_conflicts": true,
  "severity_threshold": "warning"
}
```

**Response (200 OK):** List of generated alerts

**Checks Performed:**
- Vessel authorization validation
- Occupancy level monitoring
- Berth assignment conflicts

---

### PATCH /alerts/{alert_id}/acknowledge

Acknowledge an alert.

**Path Parameters:**
- `alert_id` (string): Alert URN ID

**Query Parameters:**
- `operator_id` (string): Operator ID

**Response (200 OK):** Updated alert with acknowledgement

---

### PATCH /alerts/{alert_id}/resolve

Resolve an alert.

**Path Parameters:**
- `alert_id` (string): Alert URN ID

**Response (200 OK):** Updated alert with resolved status

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Port not found",
  "status_code": 404,
  "timestamp": "2026-04-28T12:00:00",
  "path": "/api/v1/ports/invalid_id"
}
```

### Error Status Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 | Bad Request | Invalid parameters, validation failure |
| 404 | Not Found | Entity doesn't exist |
| 409 | Conflict | State transition invalid, berth conflict |
| 500 | Internal Server Error | Server-side error, Orion-LD unavailable |
| 503 | Service Unavailable | External service down |

---

## Authentication & Security

### Current Implementation

- **No authentication** in development/test
- **Allowed hosts** configured via environment variables
- **CORS** enabled for cross-origin requests

### Production Recommendations

1. Implement JWT authentication
2. Add rate limiting
3. Enable HTTPS/TLS
4. Restrict allowed origins
5. Add request signing for Orion-LD calls
6. Implement audit logging

---

## OpenAPI Documentation

Interactive API documentation available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

