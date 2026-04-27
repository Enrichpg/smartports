# SmartPort Galicia — Data Model (NGSI-LD)

**Version:** 1.0  
**Date:** 2026-04-27  
**Standard:** NGSI-LD v1.6  
**Status:** Active

---

## Executive Summary

The SmartPort Galicia data model defines **15 NGSI-LD entities** organized into three groups:

1. **Infrastructure (Static):** Port, PortAuthority, SeaportFacilities, MasterVessel, BoatAuthorized, BoatPlacesPricing
2. **Operations (Dynamic):** Berth, Vessel, PortCall, Operation, BoatPlacesAvailable
3. **Observations & Alerts (Dynamic):** Device, AirQualityObserved, WeatherObserved, Alert

All entities follow:
- **Official Smart Data Models** from https://smartdatamodels.org
- **NGSI-LD v1.6 standards** from https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf
- **Multipurpose Galician scope** (11+ ports as unified system)
- **Real-time first design** (dynamic entities updated continuously)

---

## 0. Global NGSI-LD Conventions

### 0.1 URN Naming Convention

All entity IDs follow this URN format:

```
urn:smartdatamodels:<entityType>:<namespace>:<uniqueId>
```

**Examples:**
```
urn:smartdatamodels:Port:Galicia:CorA
urn:smartdatamodels:Berth:CorA:berth_A1
urn:smartdatamodels:Vessel:ImoRegistry:9876543
urn:smartdatamodels:PortCall:Galicia:corA_20260427_imo9876543
```

### 0.2 Required Global @Context

Every entity payload MUST include @context. Preferred approach: embed globally:

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ]
}
```

### 0.3 Static vs Dynamic Attributes

**Static Attributes:**
- Do NOT include `observedAt`
- Set once, rarely change
- Example: `Port.name`, `Berth.dimensions`, `MasterVessel.imoNumber`

**Dynamic Attributes:**
- MUST include `observedAt` (ISO 8601 timestamp)
- Updated frequently (seconds to minutes)
- Example: `Berth.occupancyStatus`, `Vessel.position`, `AirQualityObserved.pm25`

### 0.4 NGSI-LD Relationship Format

All relationships use NGSI-LD `Relationship` type with `object` field:

```json
{
  "hasPortCall": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:PortCall:Galicia:corA_20260427_imo9876543"
  }
}
```

---

## 1. Infrastructure Entities (Static Layer)

### 1.1 Port

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/Port  
**Role:** Represents a Galician port (geographic, administrative, operational unit)

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier (urn:smartdatamodels:Port:Galicia:CorA) |
| type | N/A | Text | Static | "Port" |
| name | Property | Text | Static | Port name (e.g., "A Coruña", "Vigo") |
| location | GeoProperty | Point | Static | Geographic coordinates (WGS84 lat/long) |
| address | Property | Address Object | Static | Full address including country |
| portAuthority | Relationship | URN | Static | Reference to PortAuthority entity |
| hasSeaportFacilities | Relationship | URN[] | Static | List of SeaportFacilities in port |
| description | Property | Text | Static | Operational description |
| timezone | Property | Text | Static | Timezone (e.g., "Europe/Madrid") |
| website | Property | URL | Static | Official website |
| contactPoint | Property | Object | Static | {name, email, phone, role} |
| operatingStatus | Property | Text | Static | "operational" \| "maintenance" \| "closed" |
| lastModified | DateTime | ISO 8601 | Static | Last modification timestamp |

**Example JSON-LD Payload:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Port:Galicia:CorA",
  "type": "Port",
  "name": {
    "type": "Property",
    "value": "Puerto de A Coruña"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3886, 43.3708]
    }
  },
  "address": {
    "type": "Property",
    "value": {
      "streetAddress": "Avda. Marina Española",
      "addressLocality": "A Coruña",
      "addressRegion": "Galicia",
      "postalCode": "15001",
      "addressCountry": "ES"
    }
  },
  "portAuthority": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:PortAuthority:Galicia:CorA"
  },
  "hasSeaportFacilities": {
    "type": "Relationship",
    "value": [
      "urn:smartdatamodels:SeaportFacilities:CorA:dock_A",
      "urn:smartdatamodels:SeaportFacilities:CorA:dock_B"
    ]
  },
  "timezone": {
    "type": "Property",
    "value": "Europe/Madrid"
  },
  "operatingStatus": {
    "type": "Property",
    "value": "operational"
  }
}
```

---

### 1.2 PortAuthority

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/PortAuthority  
**Role:** Administrative entity managing one or more ports

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "PortAuthority" |
| name | Property | Text | Static | Authority name (e.g., "Autoridad Portuaria de A Coruña") |
| manages | Relationship | URN[] | Static | List of ports managed |
| address | Property | Address Object | Static | Registered address |
| contactPoint | Property | Object | Static | {name, email, phone, role} |
| website | Property | URL | Static | Official website |
| registrationNumber | Property | Text | Static | Administrative registration |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:PortAuthority:Galicia:CorA",
  "type": "PortAuthority",
  "name": {
    "type": "Property",
    "value": "Autoridad Portuaria de A Coruña"
  },
  "manages": {
    "type": "Relationship",
    "value": ["urn:smartdatamodels:Port:Galicia:CorA"]
  },
  "address": {
    "type": "Property",
    "value": {
      "streetAddress": "Avda. Marina Española 25",
      "addressLocality": "A Coruña",
      "postalCode": "15001",
      "addressCountry": "ES"
    }
  }
}
```

---

### 1.3 SeaportFacilities

**Source:** dataModel.Ports  
**Official Link:** https://github.com/smart-data-models/dataModel.Ports/blob/master/SeaportFacilities  
**Role:** Grouping of berths and services within a port (dock, terminal, zone)

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "SeaportFacilities" |
| name | Property | Text | Static | Facility name (e.g., "Dock A", "Terminal 1") |
| location | GeoProperty | Point/Polygon | Static | Geographic boundaries |
| port | Relationship | URN | Static | Reference to parent Port |
| hasBerths | Relationship | URN[] | Static | List of Berths in facility |
| hasAvailability | Relationship | URN[] | Static | List of BoatPlacesAvailable |
| facilitiesType | Property | Text[] | Static | ["dock", "terminal", "anchorage", "mooring"] |
| servicesOffered | Property | Text[] | Static | ["cargo_handling", "bunkering", "repairs", etc.] |
| cranes | Property | Integer | Static | Number of cranes available |
| storageCapacity | Property | Object | Static | {unit: "tons", value: 5000} |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:SeaportFacilities:CorA:dock_A",
  "type": "SeaportFacilities",
  "name": {
    "type": "Property",
    "value": "Dock A - Terminal Carga General"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Polygon",
      "coordinates": [[[-8.389, 43.371], [-8.388, 43.371], [-8.388, 43.372], [-8.389, 43.372], [-8.389, 43.371]]]
    }
  },
  "port": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Port:Galicia:CorA"
  },
  "hasBerths": {
    "type": "Relationship",
    "value": [
      "urn:smartdatamodels:Berth:CorA:A1",
      "urn:smartdatamodels:Berth:CorA:A2"
    ]
  },
  "servicesOffered": {
    "type": "Property",
    "value": ["cargo_handling", "bunkering", "repairs"]
  },
  "cranes": {
    "type": "Property",
    "value": 4
  }
}
```

---

### 1.4 MasterVessel

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/Vessel  
**Role:** Static catalog of vessel characteristics (reference for active Vessel entities)

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier (IMO-based) |
| type | N/A | Text | Static | "Vessel" (with subType="MasterVessel") |
| imoNumber | Property | Text | Static | IMO number (unique international identifier) |
| mmsi | Property | Text | Static | MMSI (Maritime Mobile Service Identity) |
| name | Property | Text | Static | Vessel name |
| vesselType | Property | Text | Static | "cargo", "container", "tanker", "passenger", etc. |
| length | Property | Quantity | Static | Length overall (meters) |
| breadth | Property | Quantity | Static | Beam width (meters) |
| draft | Property | Quantity | Static | Maximum draft (meters) |
| grossTonnage | Property | Quantity | Static | GT (gross tonnage) |
| deadweightTonnage | Property | Quantity | Static | DWT (carrying capacity) |
| flag | Property | Text | Static | Country of registry |
| operator | Property | Text | Static | Ship operator/owner |
| yearOfBuilt | Property | Integer | Static | Construction year |
| engineType | Property | Text | Static | Propulsion type |
| certificateExpiry | Property | DateTime | Static | Latest relevant certification expiry |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Vessel:IMORegistry:9876543",
  "type": "Vessel",
  "subType": "MasterVessel",
  "imoNumber": {
    "type": "Property",
    "value": "9876543"
  },
  "name": {
    "type": "Property",
    "value": "OCEAN TRADER"
  },
  "vesselType": {
    "type": "Property",
    "value": "cargo"
  },
  "length": {
    "type": "Property",
    "value": {
      "value": 189.5,
      "unitCode": "MTR"
    }
  },
  "breadth": {
    "type": "Property",
    "value": {
      "value": 32.2,
      "unitCode": "MTR"
    }
  },
  "draft": {
    "type": "Property",
    "value": {
      "value": 10.5,
      "unitCode": "MTR"
    }
  },
  "grossTonnage": {
    "type": "Property",
    "value": {
      "value": 38000,
      "unitCode": "TNE"
    }
  },
  "deadweightTonnage": {
    "type": "Property",
    "value": {
      "value": 56000,
      "unitCode": "TNE"
    }
  },
  "flag": {
    "type": "Property",
    "value": "MT"
  }
}
```

---

### 1.5 BoatAuthorized

**Source:** dataModel.Ports  
**Official Link:** https://github.com/smart-data-models/dataModel.Ports/blob/master/BoatAuthorized  
**Role:** Authorization and compliance status of a vessel to operate in Galician ports

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "BoatAuthorized" |
| refVessel | Relationship | URN | Static | Reference to MasterVessel |
| insuranceCompany | Property | Text | Static | Insurance provider |
| insurancePolicyNumber | Property | Text | Static | Policy identifier |
| insuranceExpiry | Property | DateTime | Static | Policy expiration date |
| certificatesHeld | Property | Text[] | Static | List of certifications (SOLAS, ISPS, etc.) |
| certificateExpiry | Property | DateTime | Static | Earliest certificate expiration |
| portAuthority | Relationship | URN | Static | Issuing authority |
| authorizedPorts | Relationship | URN[] | Static | List of ports where authorized |
| restrictions | Property | Text[] | Static | Any operational restrictions |
| approvalDate | Property | DateTime | Static | Authorization issuance date |
| authorizationStatus | Property | Text | Static | "authorized" \| "suspended" \| "revoked" \| "expired" |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:BoatAuthorized:Galicia:imo9876543",
  "type": "BoatAuthorized",
  "refVessel": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Vessel:IMORegistry:9876543"
  },
  "insuranceCompany": {
    "type": "Property",
    "value": "Lloyd's Register"
  },
  "insurancePolicyNumber": {
    "type": "Property",
    "value": "LR-POL-2026-001234"
  },
  "insuranceExpiry": {
    "type": "Property",
    "value": "2027-03-15T23:59:59Z"
  },
  "certificatesHeld": {
    "type": "Property",
    "value": ["SOLAS", "ISPS", "MLC", "BALLAST"]
  },
  "authorizedPorts": {
    "type": "Relationship",
    "value": [
      "urn:smartdatamodels:Port:Galicia:CorA",
      "urn:smartdatamodels:Port:Galicia:Vigo",
      "urn:smartdatamodels:Port:Galicia:Ferrol"
    ]
  },
  "authorizationStatus": {
    "type": "Property",
    "value": "authorized"
  }
}
```

---

### 1.6 BoatPlacesPricing

**Source:** dataModel.Ports  
**Official Link:** https://github.com/smart-data-models/dataModel.Ports/blob/master/BoatPlacesPricing  
**Role:** Tariff structure for berth/mooring usage

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "BoatPlacesPricing" |
| refBoatPlacesAvailable | Relationship | URN | Static | Reference to BoatPlacesAvailable |
| currency | Property | Text | Static | Currency code (EUR, USD, etc.) |
| pricePerMeter | Property | Quantity | Static | Price per meter of vessel length |
| pricePerTon | Property | Quantity | Static | Price per ton of vessel weight |
| pricePerDay | Property | Quantity | Static | Base daily rate |
| minimumStay | Property | Quantity | Static | Minimum stay period (hours) |
| discountMultiday | Property | Number | Static | Discount factor for multi-day stays (0-1) |
| specialServices | Property | Object[] | Static | [{service: "bunkering", price: 1500, unit: "unit"}] |
| effectiveFrom | Property | DateTime | Static | Tariff start date |
| effectiveTo | Property | DateTime | Static | Tariff end date (null = ongoing) |
| tariffType | Property | Text | Static | "scheduled", "spot", "contract" |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:BoatPlacesPricing:CorA:dock_A_pricing",
  "type": "BoatPlacesPricing",
  "refBoatPlacesAvailable": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:BoatPlacesAvailable:CorA:dock_A"
  },
  "currency": {
    "type": "Property",
    "value": "EUR"
  },
  "pricePerMeter": {
    "type": "Property",
    "value": {
      "value": 25.50,
      "unitCode": "EUR/MTR/DAY"
    }
  },
  "pricePerDay": {
    "type": "Property",
    "value": {
      "value": 5000,
      "unitCode": "EUR/DAY"
    }
  },
  "effectiveFrom": {
    "type": "Property",
    "value": "2026-01-01T00:00:00Z"
  },
  "tariffType": {
    "type": "Property",
    "value": "scheduled"
  }
}
```

---

## 2. Operations Entities (Dynamic Layer)

### 2.1 Berth

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/Berth  
**Role:** Individual mooring point / berth, updated in real-time

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "Berth" |
| name | Property | Text | Static | Berth name/number |
| location | GeoProperty | Point | Static | Berth coordinates |
| seaportFacilities | Relationship | URN | Static | Parent facility |
| length | Property | Quantity | Static | Berth length (meters) |
| width | Property | Quantity | Static | Berth width (meters) |
| maxDraft | Property | Quantity | Static | Maximum draft allowed (meters) |
| occupancyStatus | Property | Text | **Dynamic** | "free" \| "occupied" \| "reserved" \| "maintenance" |
| occupiedBy | Relationship | URN | **Dynamic** | Current PortCall ID (if occupied) |
| expectedArrival | Property | DateTime | **Dynamic** | Expected arrival of next vessel |
| expectedDeparture | Property | DateTime | **Dynamic** | Expected departure of current vessel |
| availableFrom | Property | DateTime | **Dynamic** | When berth becomes available (observedAt required) |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Status observation timestamp |
| hasAlert | Relationship | URN[] | **Dynamic** | Active alerts on this berth |
| pricing | Relationship | URN | Static | Reference to BoatPlacesPricing |

**Example (Dynamic Update):**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Berth:CorA:A1",
  "type": "Berth",
  "name": {
    "type": "Property",
    "value": "Atraque A1"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.389, 43.371]
    }
  },
  "seaportFacilities": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:SeaportFacilities:CorA:dock_A"
  },
  "length": {
    "type": "Property",
    "value": {
      "value": 250,
      "unitCode": "MTR"
    }
  },
  "maxDraft": {
    "type": "Property",
    "value": {
      "value": 12.5,
      "unitCode": "MTR"
    }
  },
  "occupancyStatus": {
    "type": "Property",
    "value": "occupied",
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "occupiedBy": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:PortCall:Galicia:corA_20260427_imo9876543"
  },
  "expectedDeparture": {
    "type": "Property",
    "value": "2026-04-28T18:00:00Z",
    "observedAt": "2026-04-27T10:15:32Z"
  }
}
```

---

### 2.2 Vessel (Active Instance)

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/Vessel  
**Role:** Real-time state of a vessel currently at or approaching a port

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier (IMO-based but with context) |
| type | N/A | Text | Static | "Vessel" |
| masterVessel | Relationship | URN | Static | Reference to MasterVessel catalog |
| name | Property | Text | Static | Vessel name |
| position | GeoProperty | Point | **Dynamic** | Current GPS position (lat/long) |
| lastAISUpdate | Property | DateTime | **Dynamic** | Timestamp of last AIS reception |
| course | Property | Number | **Dynamic** | Course over ground (degrees, 0-360) |
| speed | Property | Quantity | **Dynamic** | Speed over ground (knots) |
| status | Property | Text | **Dynamic** | "transit" \| "maneuvering" \| "anchored" \| "moored" \| "underway" |
| eta | Property | DateTime | **Dynamic** | Estimated time of arrival (observedAt required) |
| etd | Property | DateTime | **Dynamic** | Estimated time of departure |
| currentPort | Relationship | URN | **Dynamic** | Port currently at or approaching |
| currentBerth | Relationship | URN | **Dynamic** | Berth currently at (if moored) |
| draft | Property | Quantity | **Dynamic** | Current draft (may vary due to cargo) |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Position/status observation timestamp |
| refAuthorized | Relationship | URN | Static | Reference to BoatAuthorized |

**Example (Real-Time):**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Vessel:AIS:imo9876543_corA_20260427",
  "type": "Vessel",
  "masterVessel": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Vessel:IMORegistry:9876543"
  },
  "name": {
    "type": "Property",
    "value": "OCEAN TRADER"
  },
  "position": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.395, 43.368]
    },
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "course": {
    "type": "Property",
    "value": 045,
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "speed": {
    "type": "Property",
    "value": {
      "value": 8.5,
      "unitCode": "KNT"
    },
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "status": {
    "type": "Property",
    "value": "moored",
    "observedAt": "2026-04-27T09:30:00Z"
  },
  "eta": {
    "type": "Property",
    "value": "2026-04-27T11:00:00Z",
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "currentPort": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Port:Galicia:CorA"
  },
  "currentBerth": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Berth:CorA:A1"
  },
  "refAuthorized": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:BoatAuthorized:Galicia:imo9876543"
  }
}
```

---

### 2.3 PortCall

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/PortCall  
**Role:** Complete visit of a vessel to a port, with lifecycle state

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "PortCall" |
| refVessel | Relationship | URN | Static | Reference to Vessel |
| refPort | Relationship | URN | Static | Reference to Port |
| refBerth | Relationship | URN | **Dynamic** | Assigned berth (changes if reassigned) |
| etaPort | Property | DateTime | Static | Expected arrival at port (initial) |
| ataPort | Property | DateTime | **Dynamic** | Actual arrival (once arrived) |
| etd | Property | DateTime | **Dynamic** | Expected departure |
| atd | Property | DateTime | **Dynamic** | Actual departure (once departed) |
| state | Property | Text | **Dynamic** | "expected" \| "active" \| "operations" \| "completed" |
| servicesRequested | Property | Text[] | Static | ["cargo_loading", "bunkering", "repairs"] |
| cargoType | Property | Text | Static | Type of cargo (e.g., "general cargo", "containers") |
| cargoVolume | Property | Quantity | Static | Volume or tonnage |
| hasOperations | Relationship | URN[] | **Dynamic** | List of Operation entities |
| hasAlert | Relationship | URN[] | **Dynamic** | Active alerts on this port call |
| observedAt | DateTime | ISO 8601 | **Dynamic** | State update timestamp |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:PortCall:Galicia:corA_20260427_imo9876543",
  "type": "PortCall",
  "refVessel": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Vessel:AIS:imo9876543_corA_20260427"
  },
  "refPort": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Port:Galicia:CorA"
  },
  "refBerth": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Berth:CorA:A1"
  },
  "etaPort": {
    "type": "Property",
    "value": "2026-04-27T12:00:00Z"
  },
  "ataPort": {
    "type": "Property",
    "value": "2026-04-27T11:45:00Z",
    "observedAt": "2026-04-27T11:45:00Z"
  },
  "etd": {
    "type": "Property",
    "value": "2026-04-28T18:00:00Z",
    "observedAt": "2026-04-27T12:00:00Z"
  },
  "state": {
    "type": "Property",
    "value": "active",
    "observedAt": "2026-04-27T11:45:00Z"
  },
  "servicesRequested": {
    "type": "Property",
    "value": ["cargo_unloading", "bunkering"]
  },
  "cargoType": {
    "type": "Property",
    "value": "general cargo"
  },
  "cargoVolume": {
    "type": "Property",
    "value": {
      "value": 12000,
      "unitCode": "TNE"
    }
  },
  "hasOperations": {
    "type": "Relationship",
    "value": [
      "urn:smartdatamodels:Operation:corA_20260427_imo9876543_op1"
    ]
  }
}
```

---

### 2.4 Operation

**Source:** dataModel.MarineTransport  
**Official Link:** https://github.com/smart-data-models/dataModel.MarineTransport/blob/master/Operation  
**Role:** Specific operational activity during a port call (cargo handling, service, etc.)

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "Operation" |
| refPortCall | Relationship | URN | Static | Reference to PortCall |
| refBerth | Relationship | URN | Static | Berth where operation occurs |
| operationType | Property | Text | Static | "cargo_load" \| "cargo_unload" \| "bunkering" \| "repairs" \| "inspection" \| "maintenance" |
| startTime | Property | DateTime | **Dynamic** | Actual start (observedAt required) |
| endTime | Property | DateTime | **Dynamic** | Actual end (observedAt required) |
| duration | Property | Quantity | **Dynamic** | Duration in hours |
| plannedDuration | Property | Quantity | Static | Initially planned duration |
| quantityHandled | Property | Quantity | Static | Amount (tons, containers, barrels, etc.) |
| unit | Property | Text | Static | Unit of quantity |
| hasDevice | Relationship | URN[] | Static | Sensors/cranes involved |
| status | Property | Text | **Dynamic** | "planned" \| "in_progress" \| "completed" \| "delayed" \| "cancelled" |
| personnel | Property | Integer | Static | Number of personnel involved |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Status update timestamp |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Operation:corA_20260427_imo9876543_op1",
  "type": "Operation",
  "refPortCall": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:PortCall:Galicia:corA_20260427_imo9876543"
  },
  "refBerth": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Berth:CorA:A1"
  },
  "operationType": {
    "type": "Property",
    "value": "cargo_unload"
  },
  "startTime": {
    "type": "Property",
    "value": "2026-04-27T12:30:00Z",
    "observedAt": "2026-04-27T12:30:00Z"
  },
  "endTime": {
    "type": "Property",
    "value": "2026-04-28T16:15:00Z",
    "observedAt": "2026-04-28T16:15:00Z"
  },
  "quantityHandled": {
    "type": "Property",
    "value": {
      "value": 5600,
      "unitCode": "TNE"
    }
  },
  "status": {
    "type": "Property",
    "value": "completed",
    "observedAt": "2026-04-28T16:15:00Z"
  },
  "hasDevice": {
    "type": "Relationship",
    "value": [
      "urn:smartdatamodels:Device:CorA:crane_01",
      "urn:smartdatamodels:Device:CorA:crane_02"
    ]
  }
}
```

---

### 2.5 BoatPlacesAvailable

**Source:** dataModel.Ports  
**Official Link:** https://github.com/smart-data-models/dataModel.Ports/blob/master/BoatPlacesAvailable  
**Role:** Real-time and forecast availability of berths/mooring spaces

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "BoatPlacesAvailable" |
| refSeaportFacilities | Relationship | URN | Static | Reference to facility |
| totalPlaces | Property | Integer | Static | Total berths/moorings available |
| occupiedPlaces | Property | Integer | **Dynamic** | Currently occupied places |
| availablePlaces | Property | Integer | **Dynamic** | Currently free places |
| reservedPlaces | Property | Integer | **Dynamic** | Currently reserved (not yet arrived) |
| occupiedPercentage | Property | Number | **Dynamic** | Occupancy % (0-100) |
| forecast7Day | Property | Object[] | **Dynamic** | [{day: "2026-04-28", occupancyPercent: 75.5}] |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Observation timestamp |
| pricing | Relationship | URN | Static | Reference to BoatPlacesPricing |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:BoatPlacesAvailable:CorA:dock_A",
  "type": "BoatPlacesAvailable",
  "refSeaportFacilities": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:SeaportFacilities:CorA:dock_A"
  },
  "totalPlaces": {
    "type": "Property",
    "value": 8
  },
  "occupiedPlaces": {
    "type": "Property",
    "value": 6,
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "availablePlaces": {
    "type": "Property",
    "value": 2,
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "occupiedPercentage": {
    "type": "Property",
    "value": 75,
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "forecast7Day": {
    "type": "Property",
    "value": [
      {"day": "2026-04-27", "occupancyPercent": 75},
      {"day": "2026-04-28", "occupancyPercent": 85},
      {"day": "2026-04-29", "occupancyPercent": 62}
    ],
    "observedAt": "2026-04-27T06:00:00Z"
  }
}
```

---

## 3. Observations & Alerts (Dynamic Layer)

### 3.1 Device

**Source:** NGSI-LD Core ontology + Smart Data Models  
**Official Link:** https://github.com/smart-data-models/dataModel.Device  
**Role:** IoT sensor or actuator deployed in a port

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "Device" |
| name | Property | Text | Static | Device name/label |
| location | GeoProperty | Point | Static | Installation location |
| refSeaportFacilities | Relationship | URN | Static | Deployed at facility |
| deviceType | Property | Text | Static | "air_quality_sensor", "weather_station", "crane", "gate", etc. |
| manufacturer | Property | Text | Static | Device manufacturer |
| model | Property | Text | Static | Device model |
| serialNumber | Property | Text | Static | Serial number |
| operatingStatus | Property | Text | **Dynamic** | "active" \| "inactive" \| "error" \| "maintenance" |
| lastCalibration | Property | DateTime | **Dynamic** | Last calibration date |
| batteryLevel | Property | Number | **Dynamic** | Battery % (if applicable) |
| signalStrength | Property | Number | **Dynamic** | Signal strength (dBm) |
| lastCommunication | Property | DateTime | **Dynamic** | Last message received |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Status timestamp |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Device:CorA:aq_sensor_01",
  "type": "Device",
  "name": {
    "type": "Property",
    "value": "Air Quality Sensor - Dock A"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3893, 43.3712]
    }
  },
  "deviceType": {
    "type": "Property",
    "value": "air_quality_sensor"
  },
  "manufacturer": {
    "type": "Property",
    "value": "FLIR"
  },
  "operatingStatus": {
    "type": "Property",
    "value": "active",
    "observedAt": "2026-04-27T10:15:32Z"
  },
  "lastCommunication": {
    "type": "Property",
    "value": "2026-04-27T10:15:30Z"
  }
}
```

---

### 3.2 AirQualityObserved

**Source:** Smart Data Models  
**Official Link:** https://github.com/smart-data-models/dataModel.Environment/tree/master/AirQualityObserved  
**Role:** Real-time air quality measurements at a port

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "AirQualityObserved" |
| location | GeoProperty | Point | Static | Measurement location |
| refDevice | Relationship | URN | Static | Sensor that made measurement |
| refPort | Relationship | URN | Static | Associated port |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Measurement timestamp (REQUIRED) |
| pm25 | Property | Quantity | **Dynamic** | PM2.5 (µg/m³) |
| pm10 | Property | Quantity | **Dynamic** | PM10 (µg/m³) |
| no2 | Property | Quantity | **Dynamic** | NO₂ (µg/m³) |
| so2 | Property | Quantity | **Dynamic** | SO₂ (µg/m³) |
| co | Property | Quantity | **Dynamic** | CO (mg/m³) |
| o3 | Property | Quantity | **Dynamic** | O₃ (µg/m³) |
| temperature | Property | Quantity | **Dynamic** | Air temperature (°C) |
| humidity | Property | Number | **Dynamic** | Relative humidity (%) |
| aqi | Property | Number | **Dynamic** | Air Quality Index (0-500) |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:AirQualityObserved:CorA:dock_A_20260427_101532",
  "type": "AirQualityObserved",
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3893, 43.3712]
    }
  },
  "refDevice": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Device:CorA:aq_sensor_01"
  },
  "refPort": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Port:Galicia:CorA"
  },
  "observedAt": "2026-04-27T10:15:32Z",
  "pm25": {
    "type": "Property",
    "value": {
      "value": 42.5,
      "unitCode": "UGM3"
    }
  },
  "pm10": {
    "type": "Property",
    "value": {
      "value": 65.3,
      "unitCode": "UGM3"
    }
  },
  "no2": {
    "type": "Property",
    "value": {
      "value": 28.1,
      "unitCode": "UGM3"
    }
  },
  "temperature": {
    "type": "Property",
    "value": {
      "value": 16.5,
      "unitCode": "CEL"
    }
  },
  "humidity": {
    "type": "Property",
    "value": 72.5
  },
  "aqi": {
    "type": "Property",
    "value": 145
  }
}
```

---

### 3.3 WeatherObserved

**Source:** Smart Data Models  
**Official Link:** https://github.com/smart-data-models/dataModel.Weather/tree/master/WeatherObserved  
**Role:** Meteorological observations at port locations

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "WeatherObserved" |
| location | GeoProperty | Point | Static | Measurement location |
| refDevice | Relationship | URN | Static | Weather station device |
| refPort | Relationship | URN | Static | Associated port |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Measurement timestamp (REQUIRED) |
| temperature | Property | Quantity | **Dynamic** | Air temperature (°C) |
| relativeHumidity | Property | Number | **Dynamic** | Relative humidity (%) |
| atmosphericPressure | Property | Quantity | **Dynamic** | Atmospheric pressure (hPa) |
| windDirection | Property | Number | **Dynamic** | Wind direction (degrees 0-360) |
| windSpeed | Property | Quantity | **Dynamic** | Wind speed (m/s) |
| windGust | Property | Quantity | **Dynamic** | Wind gust speed (m/s) |
| visibility | Property | Quantity | **Dynamic** | Visibility (meters) |
| precipitation | Property | Quantity | **Dynamic** | Precipitation (mm) |
| weatherCondition | Property | Text | **Dynamic** | "clear" \| "rain" \| "fog" \| "snow" \| "clouds" \| "thunderstorm" |
| waveHeight | Property | Quantity | **Dynamic** | Sea wave height (meters) |
| seaState | Property | Text | **Dynamic** | "calm" \| "slight" \| "moderate" \| "rough" \| "high" |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:WeatherObserved:CorA:station_01_20260427_101532",
  "type": "WeatherObserved",
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3886, 43.3708]
    }
  },
  "refDevice": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Device:CorA:weather_station_01"
  },
  "refPort": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Port:Galicia:CorA"
  },
  "observedAt": "2026-04-27T10:15:32Z",
  "temperature": {
    "type": "Property",
    "value": {
      "value": 16.2,
      "unitCode": "CEL"
    }
  },
  "relativeHumidity": {
    "type": "Property",
    "value": 68
  },
  "windDirection": {
    "type": "Property",
    "value": 245
  },
  "windSpeed": {
    "type": "Property",
    "value": {
      "value": 12.5,
      "unitCode": "MTS"
    }
  },
  "visibility": {
    "type": "Property",
    "value": {
      "value": 8500,
      "unitCode": "MTR"
    }
  },
  "weatherCondition": {
    "type": "Property",
    "value": "clouds"
  },
  "waveHeight": {
    "type": "Property",
    "value": {
      "value": 1.8,
      "unitCode": "MTR"
    }
  },
  "seaState": {
    "type": "Property",
    "value": "slight"
  }
}
```

---

### 3.4 Alert

**Source:** NGSI-LD Core + Smart Data Models adaptations  
**Official Link:** https://github.com/smart-data-models/dataModel.Alert  
**Role:** System-generated alert for operational, environmental, or administrative issues

**Attributes:**

| Attribute | NGSI Type | Data Type | Static/Dynamic | Description |
|-----------|-----------|-----------|----------------|-------------|
| id | N/A | URN | Static | Unique identifier |
| type | N/A | Text | Static | "Alert" |
| alertType | Property | Text | Static | "operational" \| "environmental" \| "administrative" \| "safety" |
| severity | Property | Text | **Dynamic** | "info" \| "warning" \| "critical" |
| description | Property | Text | **Dynamic** | Human-readable alert description |
| refEntity | Relationship | URN | Static | Entity triggering alert (Port, Berth, Vessel, PortCall, etc.) |
| refDevice | Relationship | URN | Static | Sensor that triggered alert (if applicable) |
| threshold | Property | Object | Static | {parameter: "pm25", limit: 75, unit: "µg/m³"} |
| actualValue | Property | Quantity | **Dynamic** | Value that triggered threshold |
| createdAt | Property | DateTime | **Dynamic** | When alert was generated |
| resolvedAt | Property | DateTime | **Dynamic** | When alert was resolved (null if active) |
| status | Property | Text | **Dynamic** | "active" \| "acknowledged" \| "resolved" \| "expired" |
| acknowledgmentComment | Property | Text | **Dynamic** | Resolution comment |
| observedAt | DateTime | ISO 8601 | **Dynamic** | Status timestamp |

**Example:**

```json
{
  "@context": "https://smartdatamodels.org/context.jsonld",
  "id": "urn:smartdatamodels:Alert:CorA:alert_20260427_101500",
  "type": "Alert",
  "alertType": {
    "type": "Property",
    "value": "environmental"
  },
  "severity": {
    "type": "Property",
    "value": "warning",
    "observedAt": "2026-04-27T10:15:00Z"
  },
  "description": {
    "type": "Property",
    "value": "PM2.5 concentration exceeds threshold (42.5 µg/m³ > 35 µg/m³)"
  },
  "refEntity": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Port:Galicia:CorA"
  },
  "refDevice": {
    "type": "Relationship",
    "object": "urn:smartdatamodels:Device:CorA:aq_sensor_01"
  },
  "threshold": {
    "type": "Property",
    "value": {
      "parameter": "pm25",
      "limit": 35,
      "unit": "µg/m³"
    }
  },
  "actualValue": {
    "type": "Property",
    "value": {
      "value": 42.5,
      "unitCode": "UGM3"
    }
  },
  "createdAt": {
    "type": "Property",
    "value": "2026-04-27T10:15:00Z"
  },
  "status": {
    "type": "Property",
    "value": "active",
    "observedAt": "2026-04-27T10:15:00Z"
  }
}
```

---

## 4. Entity Relationships & Graph

### 4.1 Relationship Map

```
Port
├─ manages (Relationship)
│   └─ PortAuthority
├─ hasFacilities (Relationship)
│   └─ SeaportFacilities
│       ├─ hasBerths (Relationship)
│       │   └─ Berth
│       │       ├─ occupiedBy (Relationship) → PortCall
│       │       ├─ hasAlert (Relationship) → Alert
│       │       └─ pricing (Relationship) → BoatPlacesPricing
│       └─ hasAvailability (Relationship)
│           └─ BoatPlacesAvailable
│               └─ pricing (Relationship) → BoatPlacesPricing

Vessel (Active)
├─ masterVessel (Relationship) → MasterVessel
├─ refAuthorized (Relationship) → BoatAuthorized
├─ currentPort (Relationship) → Port
└─ currentBerth (Relationship) → Berth

PortCall
├─ refVessel (Relationship) → Vessel
├─ refPort (Relationship) → Port
├─ refBerth (Relationship) → Berth
├─ hasOperations (Relationship) → Operation[]
└─ hasAlert (Relationship) → Alert[]

Operation
├─ refPortCall (Relationship) → PortCall
├─ refBerth (Relationship) → Berth
└─ hasDevice (Relationship) → Device[]

Device
├─ location (GeoProperty)
└─ observes / measures
    ├─ AirQualityObserved
    └─ WeatherObserved

Alert
├─ refEntity (Relationship) → [Port | Berth | PortCall | Vessel | Device]
└─ refDevice (Relationship) → Device
```

### 4.2 Static vs Dynamic Summary

**Predominantly Static (Create once, rarely update):**
- Port
- PortAuthority
- SeaportFacilities
- MasterVessel
- BoatAuthorized
- BoatPlacesPricing

**Predominantly Dynamic (Updated continuously or frequently):**
- Berth (occupancy status, ETA/ETD)
- Vessel (position, speed, course, ETA, ETD)
- PortCall (state transitions, ETA/ETD, operations)
- Operation (timing, status)
- BoatPlacesAvailable (occupancy, forecast)
- Device (operating status, battery, signals)
- AirQualityObserved (measurements, observedAt required)
- WeatherObserved (measurements, observedAt required)
- Alert (severity, status, resolution)

---

## 5. Data Quality & Validation Rules

### 5.1 Mandatory Fields by Entity Type

**All Entities:**
- ✅ id (URN format)
- ✅ type (entity type string)
- ✅ @context (explicitly included)

**Dynamic Attributes:**
- ✅ observedAt (ISO 8601 timestamp)
- ✅ Must be set when publishing updates

**Relationships:**
- ✅ Must use NGSI-LD Relationship type
- ✅ Must include object field with target entity URN
- ✅ Cannot be null

### 5.2 Validation Constraints

| Entity | Field | Constraint | Example |
|--------|-------|-----------|---------|
| Port | location | Valid WGS84 | [-8.3886, 43.3708] |
| Berth | maxDraft | Positive number | 12.5 |
| Vessel | speed | 0-30 knots typical | 8.5 |
| PortCall | state | Enum: expected, active, operations, completed | "active" |
| Device | operatingStatus | Enum | "active" \| "error" \| "maintenance" |
| AirQualityObserved | pm25 | Non-negative | 42.5 |
| WeatherObserved | windDirection | 0-360 degrees | 245 |
| Alert | severity | Enum | "info" \| "warning" \| "critical" |

---

## 6. Temporal & Real-Time Considerations

### 6.1 observedAt Precision

- **Sensors:** Timestamp at source (ms precision where possible)
- **Derived entities:** Timestamp when computed (Berth occupancy from PortCall state)
- **Forecasts:** Timestamp of forecast generation, not prediction time

### 6.2 Historical Data Retention

- **Dynamic entities:** Keep 3 years (via QuantumLeap/TimescaleDB)
- **Static entities:** Keep indefinitely
- **Observations:** Keep 1 year in QuantumLeap, 3 years in analytical warehouse

### 6.3 Real-Time Update Frequency

| Entity | Typical Update Frequency | Reason |
|--------|-------------------------|--------|
| Vessel position | Every 30-60s | AIS reception cycle |
| Berth occupancy | Real-time (on PortCall change) | Operational decision |
| BoatPlacesAvailable | Every 5 minutes | Forecast refresh |
| AirQualityObserved | Every 10-15 minutes | Sensor polling |
| WeatherObserved | Every 5-10 minutes | Station polling |
| Alert | Real-time (event-driven) | Threshold breach |

---

## 7. Naming & ID Conventions

### 7.1 Entity ID Format

```
urn:smartdatamodels:<EntityType>:<Namespace>:<UniqueID>
```

**Examples:**
```
Port: urn:smartdatamodels:Port:Galicia:CorA
Berth: urn:smartdatamodels:Berth:CorA:A1
Vessel (Master): urn:smartdatamodels:Vessel:IMORegistry:9876543
Vessel (Active): urn:smartdatamodels:Vessel:AIS:imo9876543_corA_20260427
PortCall: urn:smartdatamodels:PortCall:Galicia:corA_20260427_imo9876543
Operation: urn:smartdatamodels:Operation:corA_20260427_imo9876543_op1
Device: urn:smartdatamodels:Device:CorA:aq_sensor_01
AirQualityObserved: urn:smartdatamodels:AirQualityObserved:CorA:dock_A_20260427_101532
Alert: urn:smartdatamodels:Alert:CorA:alert_20260427_101500
```

### 7.2 Namespace Conventions

- **Geographic:** Port codes (CorA = A Coruña, Vigo, Ferrol, etc.)
- **Registry:** IMORegistry, AIS, LocalCatalog
- **System:** Galicia (region-level)

---

## 8. Compliance & Standards References

### 8.1 Smart Data Models Compliance

All entities derive from or align with:
- https://github.com/smart-data-models/dataModel.MarineTransport
- https://github.com/smart-data-models/dataModel.Ports
- https://github.com/smart-data-models/dataModel.Device
- https://github.com/smart-data-models/dataModel.Environment

### 8.2 NGSI-LD v1.6 Compliance

- https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf
- All payloads include @context
- Relationships use correct NGSI-LD type
- GeoProperty for spatial data
- DateTime in ISO 8601 format
- observedAt on dynamic attributes

### 8.3 W3C Linked Data Standards

- JSON-LD: https://www.w3.org/TR/json-ld11/
- RDF/OWL optional but supported

---

## 9. Version History & Evolution

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-27 | Initial 15-entity model with NGSI-LD compliance |

---

**Next Review:** After Phase 2 backend implementation  
**Maintainer:** SmartPort Data Architecture Team  
**Status:** ACTIVE
