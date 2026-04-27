# SmartPort Galicia - NGSI-LD Seed Data

## Overview

This directory contains the NGSI-LD seed data generation system for SmartPort Galicia. It creates a realistic, multi-port dataset based on 8 real Galician ports with proper NGSI-LD structure.

## Generated Entities (211 total)

### Static Infrastructure (40 entities)
- **8 Port** entities (8 Galician ports)
- **8 PortAuthority** entities
- **8 SeaportFacilities** entities
- **10 MasterVessel** entities (shipping registry)
- **6 Catalogs of **BoatPlacesPricing** (4 categories per 8 ports = 32)

### Dynamic/Semi-Dynamic (141 entities)
- **71 Berth** entities (6-15 per port, varying statuses)
- **10 Vessel** entities (instances with position)
- **10 BoatAuthorized** entities (authorization records)
- **32 BoatPlacesAvailable** entities (occupancy by category)
- **11 Device** entities (sensors)

### Observations (30 entities)
- **6 AirQualityObserved** entities
- **5 WeatherObserved** entities

## Scripts

### 1. `validate_payloads.py`
Validates NGSI-LD compliance of all generated entities.

```bash
python3 backend/scripts/validate_payloads.py
```

**Output:** Validates 12 sample entities for NGSI-LD correctness
- Checks @context presence
- Validates URN format (urn:ngsi-ld:*)
- Verifies Property/Relationship/GeoProperty types
- **All payloads must be VALID before loading**

### 2. `generate_seed_json.py`
Generates all 211 entities and saves to JSON file.

```bash
# Generate and save
python3 backend/scripts/generate_seed_json.py --pretty

# Output file: data/seed/galicia_entities.json (217 KB)
```

**Output:**
```json
{
  "statistics": {
    "Port": 8,
    "PortAuthority": 8,
    "SeaportFacilities": 8,
    "Berth": 71,
    "MasterVessel": 10,
    "Vessel": 10,
    "BoatAuthorized": 10,
    "BoatPlacesAvailable": 32,
    "BoatPlacesPricing": 32,
    "Device": 11,
    "AirQualityObserved": 6,
    "WeatherObserved": 5
  },
  "entities": [...]
}
```

### 3. `load_seed.py`
Loads entities to Orion-LD context broker.

```bash
# Dry-run (preview only)
python3 backend/scripts/load_seed.py --dry-run

# Load with upsert (safe, default)
python3 backend/scripts/load_seed.py --upsert

# Custom Orion URL
python3 backend/scripts/load_seed.py --orion-url http://localhost:1026

# Custom FIWARE Service
python3 backend/scripts/load_seed.py --service smartport --service-path /galicia
```

**Operations:**
- `--dry-run`: Preview entities without loading
- `--upsert`: Create or update entities safely (recommended)
- `--orion-url`: Orion-LD base URL (default: http://localhost:1026)
- `--service`: FIWARE-Service header (default: smartport)
- `--service-path`: FIWARE-ServicePath header (default: /galicia)

## Covered Galician Ports

The seed covers these 8 real Galician ports:

1. **A Coruña** - 12 berths, 250 capacity (Main northwest port)
2. **Vigo** - 15 berths, 300 capacity (Major commercial)
3. **Ferrol** - 10 berths, 200 capacity (Naval+commercial)
4. **Marín** - 6 berths, 100 capacity (Pontevedra Ría)
5. **Vilagarcía de Arousa** - 8 berths, 150 capacity (Fishing+commercial)
6. **Ribeira** - 7 berths, 120 capacity (Fishing port)
7. **Burela** - 5 berths, 80 capacity (Lugo fishing)
8. **Baiona** - 8 berths, 100 capacity (Recreational+historic)

**Total: 71 berths across 8 ports**

## Data Quality

### Static Data
- Real GPS coordinates (WGS84)
- Real port names and authorities
- Real contact information
- Realistic capacity values

### Dynamic Data
- 10 realistic vessels (General Cargo, Container, Tanker, Fishing)
- IMO/MMSI numbers follow real patterns
- Vessel characteristics: length, beam, tonnage
- Berth statuses: free, occupied, maintenance, reserved
- Initial occupancy: ~66% occupied, ~33% available

### Pricing Categories (ISO 8666 boat length)
- **Category A:** 0-7m, €45/day
- **Category B:** 7-12m, €75/day
- **Category C:** 12-18m, €120/day
- **Category D:** 18-25m, €180/day

### Sensors
- 11 devices total across ports
- Air Quality sensors: PM2.5, PM10, NO2, CO
- Weather stations: Temperature, Humidity, Wind, Pressure

### Observations
- Realistic values (plausible environmental data)
- ISO 8601 timestamps with UTC
- `observedAt` field for all dynamic measurements

## NGSI-LD Compliance

All entities follow:
- **NGSI-LD v1.6** specification
- **Smart Data Models** (dataModel.Ports, dataModel.MarineTransport)
- **URN Format:** `urn:ngsi-ld:<type>:<namespace>:<id>`
- **@context:** Includes SmartDataModels context
- **Relationships:** Use Relationship type with object field
- **GeoProperty:** All locations use proper GeoJSON
- **observedAt:** Dynamic attributes include timestamp

## URN Examples

### Port
```
urn:ngsi-ld:Port:galicia-a-coruna
urn:ngsi-ld:Port:galicia-vigo
```

### Berth
```
urn:ngsi-ld:Berth:galicia-a-coruna-001
urn:ngsi-ld:Berth:galicia-vigo-001
```

### Vessel
```
urn:ngsi-ld:Vessel:mmsi-224123456
urn:ngsi-ld:MasterVessel:imo-9876543
```

### Device
```
urn:ngsi-ld:Device:galicia-a-coruna-air-01
urn:ngsi-ld:Device:galicia-vigo-weather-01
```

### Observations
```
urn:ngsi-ld:AirQualityObserved:galicia-a-coruna-air-01-<timestamp>
urn:ngsi-ld:WeatherObserved:galicia-vigo-weather-01-<timestamp>
```

## Static vs Dynamic Distinction

### Static Attributes (No `observedAt`)
- Port names, descriptions
- Vessel IMO/MMSI, dimensions
- Pricing categories and rates
- Device names and types

### Dynamic Attributes (`observedAt` included)
- Berth status (free/occupied/maintenance)
- Available boat places
- Vessel position (GPS)
- Air quality measurements (PM25, PM10)
- Weather measurements (temperature, wind, etc.)

## Usage Workflow

### Step 1: Validate
```bash
python3 backend/scripts/validate_payloads.py
```
✓ All 12 sample entities must be VALID

### Step 2: Generate JSON
```bash
python3 backend/scripts/generate_seed_json.py --pretty
```
✓ Creates `data/seed/galicia_entities.json`

### Step 3: Test (Dry-Run)
```bash
python3 backend/scripts/load_seed.py --dry-run
```
✓ Shows what would be loaded

### Step 4: Load to Orion-LD
```bash
python3 backend/scripts/load_seed.py --upsert
```
✓ Loads 211 entities to Orion-LD

### Step 5: Verify in Orion
```bash
# Query all ports
curl -H "FIWARE-Service: smartport" \
     -H "FIWARE-ServicePath: /galicia" \
     http://localhost:1026/ngsi-ld/v1/entities?type=Port

# Query a specific port
curl -H "FIWARE-Service: smartport" \
     -H "FIWARE-ServicePath: /galicia" \
     http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Port:galicia-a-coruna
```

## Code Structure

```
backend/
├── services/
│   ├── ngsi_builders.py          # Entity builders (PortBuilder, VesselBuilder, etc.)
│   └── orion_service.py          # Orion-LD client (create, update, upsert, query)
├── scripts/
│   ├── validate_payloads.py      # NGSI-LD compliance validator
│   ├── generate_seed_json.py     # JSON generation script
│   └── load_seed.py              # Orion-LD loader

data/
├── catalogs/
│   └── galicia_ports.py          # Port, vessel, sensor catalog data
└── seed/
    └── galicia_entities.json     # Generated 211 entities (output)
```

## Future Extensions

### Next Phase
- Real-time MQTT data simulation
- PortCall events for individual port operations
- Time-series data in QuantumLeap
- Predictive models for occupancy
- Historical data archival

### Current Limitations (by design)
- No MQTT continuous updates yet
- No PortCall events (preparation for next phase)
- Observations are static seed (will be replaced by sensors)
- No historical time-series data yet

## Troubleshooting

### Issue: "Cannot connect to Orion-LD"
```bash
# Verify Orion is running
curl http://localhost:1026/version

# If not running, start with docker-compose
docker-compose -f docker/docker-compose.yml up -d orion
```

### Issue: "Validation fails with 'Invalid @context'"
- Ensure all entities include NGSI_CONTEXT
- Check for missing @context in builders

### Issue: "Upsert shows 400 Bad Request"
- Verify JSON-LD structure (use validate_payloads.py first)
- Check FIWARE-Service header is included
- Ensure URN format is correct (urn:ngsi-ld:*)

## Related Documentation

- **data_model.md** - Full NGSI-LD entity specifications
- **architecture.md** - System architecture and data flow
- **PRD.md** - Product requirements and features

## Generated By

This seed data was automatically generated for SmartPort Galicia Operations Center v1.0 (April 27, 2026) using the NGSI-LD builders and SmartDataModels compliance framework.

---

**Last Updated:** 2026-04-27  
**Version:** 1.0  
**Status:** Production Ready
