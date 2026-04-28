# SmartPorts Data Architecture - Complete Flow

## 📊 Real-Time Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL REAL DATA SOURCES                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  🌡️  AEMET OpenData          🌍 MeteoGalicia WCS/WMS                  │
│  Spanish Meteorology          Galician Regional                       │
│  JWT: [configured]            Free / No Auth                          │
│  Update: 30 min               Update: 30 min                          │
│  Stations: Vigo/Ferrol/Coruña  Regional + Coastal                    │
│                                                                       │
│  🌊 Puertos del Estado        🌀 Open-Meteo Marine                    │
│  Spain Port Authority          Free Marine Weather API                │
│  Buoys: Real-time             Free / No Auth                          │
│  Update: 15 min               Update: 30 min                          │
│  Waves/Wind/Current/Tide      Wave/Swell/Forecast                    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │         CONNECTOR LAYER (API-Specific Fetch)               │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  AEMETConnector      MeteoGaliciaConnector                 │
        │  └─ Fetch from API   └─ WCS/WMS query                    │
        │  └─ Parse JSON       └─ XML parsing                      │
        │  └─ Error handling   └─ Retry logic                      │
        │                                                            │
        │  PuertosEstadoConnector  OpenMeteoConnector               │
        │  └─ Measurement nets      └─ Async fetch                 │
        │  └─ Real-time stream      └─ Pandas DataFrame             │
        │  └─ Historical API        └─ Cache + Retry               │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │       TRANSFORMER LAYER (to NGSI-LD v1.6)                  │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  WeatherTransformer          OceanTransformer             │
        │  ├─ from_aemet()             ├─ from_puertos_estado()     │
        │  ├─ from_generic()           ├─ from_generic()           │
        │  ├─ NGSI properties          ├─ NGSI properties          │
        │  │  └─ temperature           │  └─ wave_height           │
        │  │  └─ humidity              │  └─ wave_period           │
        │  │  └─ pressure              │  └─ water_temperature     │
        │  │  └─ wind_speed            │  └─ wind_direction        │
        │  │  └─ precipitation         │  └─ tide_level            │
        │  └─ @context v1.6            └─ @context v1.6            │
        │  └─ observedAt timestamp     └─ observedAt timestamp     │
        │  └─ dataProvider             └─ dataProvider             │
        │  └─ sourceConfidence         └─ sourceConfidence         │
        │                                                            │
        │  AvailabilityTransformer                                   │
        │  ├─ berth_status()                                         │
        │  ├─ boat_places_available()                                │
        │  ├─ vessel_status()                                        │
        │  └─ NGSI GeoProperty for positions                         │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │      CELERY PERIODIC TASKS (Scheduled Ingestion)           │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  Every 30 min:               Every 15 min:                 │
        │  • ingest_weather_aemet      • ingest_sea_conditions      │
        │  • ingest_weather_meteogalicia                             │
        │  • ingest_marine_weather     Every 5 min:                 │
        │                              • ingest_berth_status        │
        │                              • ingest_availability        │
        │                                                            │
        │  Every 1 min:               Every 1 hour:                  │
        │  • ingest_vessel_data        • ingest_air_quality         │
        │                                                            │
        │  All tasks:                                                │
        │  ├─ Instantiate connector/simulator                        │
        │  ├─ Fetch data                                             │
        │  ├─ Transform to NGSI-LD                                   │
        │  ├─ Publish to Orion                                       │
        │  ├─ Error handling + logging                               │
        │  └─ Return status dict                                     │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │         ORION-LD (NGSI-LD Context Broker)                  │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  Update/Upsert Entities:                                   │
        │  ├─ WeatherObserved (3 ports × 2 sources)                  │
        │  ├─ SeaConditionObserved (3+ sources per port)             │
        │  ├─ Berth (71 entities)                                    │
        │  ├─ BoatPlacesAvailable (32 entities)                      │
        │  ├─ Vessel (10+ instances)                                 │
        │  └─ AirQualityObserved (port-level)                        │
        │                                                            │
        │  Backend: MongoDB                                          │
        │  REST API: /ngsi-ld/v1/entities                            │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │         QUANTUMLEAP Subscriptions                          │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  Automatic temporal subscriptions:                         │
        │  ├─ WeatherObserved → TimescaleDB (historical)             │
        │  ├─ SeaConditionObserved → TimescaleDB                     │
        │  ├─ Berth → TimescaleDB                                    │
        │  ├─ BoatPlacesAvailable → TimescaleDB                      │
        │  ├─ Vessel → TimescaleDB                                   │
        │  └─ AirQualityObserved → TimescaleDB                       │
        │                                                            │
        │  Backend: PostgreSQL + TimescaleDB extension               │
        │  REST API: /ql/v2/entities                                 │
        │  Purpose: 7-day historical retention, analytics            │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │              FASTAPI Backend Exposure                      │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  GET /api/v1/sources/status                                │
        │  └─ All data sources + status + frequency                  │
        │                                                            │
        │  GET /api/v1/ports/{port_id}/live/weather                  │
        │  └─ Latest weather + source + confidence                   │
        │                                                            │
        │  GET /api/v1/ports/{port_id}/live/ocean                    │
        │  └─ Latest sea conditions (multi-source)                   │
        │                                                            │
        │  GET /api/v1/ports/{port_id}/live/operations               │
        │  └─ Berths + vessels + occupancy rate                      │
        │                                                            │
        │  GET /api/v1/ports/{port_id}/history/weather               │
        │  └─ 7-day historical weather (QuantumLeap)                 │
        │                                                            │
        │  GET /api/v1/berths, /api/v1/vessels                       │
        │  └─ Query all entities of type                             │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
                                ↓↓↓
        ┌───────────────────────────────────────────────────────────┐
        │           Frontend / Application Layer                     │
        ├───────────────────────────────────────────────────────────┤
        │                                                            │
        │  HTML/CSS/JS Dashboard                                     │
        │  ├─ Leaflet maps (real-time vessel tracking)               │
        │  ├─ Chart.js (weather trends)                              │
        │  ├─ Three.js (3D port visualization)                       │
        │  ├─ Grafana (embedded dashboards)                          │
        │  └─ Real-time updates via WebSocket/MQTT                   │
        │                                                            │
        │  Mobile Apps (future)                                      │
        │  ML/Analytics (Prophet, scikit-learn)                      │
        │  Decision Support (Ollama LLM)                             │
        │                                                            │
        └───────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Sequence (Single Update Cycle)

```
T+0:00  Beat Scheduler triggers "ingest_weather_aemet" task

T+0:05  Task executes:
        1. AEMETConnector().get_weather_data("35012")
           └─ HTTP GET to AEMET OpenData API
           └─ Returns: {"temperatura": 16.5, "humedad": 75, ...}
        
        2. WeatherTransformer.from_aemet(normalized_data)
           └─ Creates NGSI-LD entity:
           {
             "@context": "https://www.w3.org/ns/json-ld#v1.6",
             "id": "urn:ngsi-ld:WeatherObserved:aemet-35012",
             "type": "WeatherObserved",
             "temperature": {
               "type": "Property",
               "value": 16.5,
               "unitCode": "CEL",
               "observedAt": "2026-04-28T14:30:00Z"
             },
             "dataProvider": {
               "type": "Property",
               "value": "AEMET"
             },
             "sourceConfidence": {
               "type": "Property",
               "value": 0.95
             }
           }
        
        3. OrionService().update_entity(ngsi_entity)
           └─ HTTP PATCH to Orion-LD /ngsi-ld/v1/entities/
           └─ Upsert mode (create if not exist, update if exists)

T+0:10  QuantumLeap detects entity update:
        1. QuantumLeap subscription triggers
        2. Inserts entity attributes into TimescaleDB
        3. Historical record created with timestamp
        4. 7-day retention policy applied

T+0:15  Frontend requests live weather:
        1. GET /api/v1/ports/80003/live/weather
        2. FastAPI queries Orion-LD
        3. Returns latest weather + source (AEMET) + confidence (0.95)

T+30:00 Beat Scheduler triggers again
        └─ Cycle repeats (usually ~2-3 new records per source per port)
```

---

## 📊 Data Source Priority & Fallback

```
┌─────────────────────────────────────────────────────────────────┐
│                  INTELLIGENT DATA SELECTION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  For WeatherObserved (Temperature, Humidity, Pressure, Wind):   │
│  ┌─ Priority 1: AEMET (Real API, 95% confidence)                │
│  ├─ Priority 2: MeteoGalicia (Real API, 90% confidence)         │
│  └─ Priority 3: Simulator (Fallback, 50% confidence)            │
│                                                                  │
│  For SeaConditionObserved (Waves, Currents, Tide):             │
│  ┌─ Priority 1: Puertos del Estado (Official, 95% confidence)   │
│  ├─ Priority 2: Open-Meteo (Free API, 90% confidence)           │
│  ├─ Priority 3: MeteoGalicia (Regional, 85% confidence)         │
│  └─ Priority 4: Simulator (Fallback, 30% confidence)            │
│                                                                  │
│  For Berth/Availability (Occupancy, Places):                   │
│  ┌─ Priority 1: Real API (if available - future integration)    │
│  └─ Priority 2: Simulator (Coherent, realistic, 30% confidence) │
│                                                                  │
│  For Vessel Positions (Location, Speed, Course):                │
│  ┌─ Priority 1: AIS API (if available - future integration)     │
│  ├─ Priority 2: GPS tracking (if available - future)            │
│  └─ Priority 3: Simulator (Coherent movements, 40% confidence)  │
│                                                                  │
│  Backend Selection Logic:                                        │
│  When frontend requests data:                                    │
│  1. Query Orion-LD for entity                                    │
│  2. Return highest confidence source                             │
│  3. If multiple sources available, aggregate with weighted avg   │
│  4. If no sources available, return simulator with lower score   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Data Provenance Tracking

```
Every NGSI-LD entity includes:

dataProvider (Property):
  "AEMET" | "MeteoGalicia" | "Puertos_del_Estado" | "OpenMeteo" | "simulator"

sourceConfidence (Property):
  0.95  ← Real official API
  0.90  ← Real free API
  0.85  ← Real regional data
  0.30-0.50 ← Simulated (fallback)

Example query to find all high-confidence data:
  GET /ngsi-ld/v1/entities?q=sourceConfidence>0.8
  
Example query to find specific source:
  GET /ngsi-ld/v1/entities?q=dataProvider=="AEMET"
```

---

## ⚙️ Configuration Summary

```
REAL_APIS_ENABLED = true
FALLBACK_SIMULATORS_ENABLED = true

AEMET_API_KEY = eyJhbGciOiJIUzI1NiJ9... (JWT token)
AEMET_BASE_URL = https://opendata.aemet.es/opendata
WEATHER_UPDATE_FREQUENCY = 1800s (30 min)

METEOGALICIA_BASE_URL = http://forecast.cirrus.uvigo.es/thredds/wcs
WEATHER_UPDATE_FREQUENCY = 1800s

PUERTOS_ESTADO_BASE_URL = https://www.puertos.es
OCEAN_CONDITIONS_UPDATE_FREQUENCY = 900s (15 min)

OPENMETEO_BASE_URL = https://marine-api.open-meteo.com/v1/marine
OPENMETEO_CACHE_TTL = 3600s
MARINE_WEATHER_UPDATE_FREQUENCY = 1800s (30 min)

CELERY_BROKER_URL = redis://redis:6379/0
CELERY_BACKEND = redis://redis:6379/0

ORION_URL = http://orion-ld:1026
QUANTUMLEAP_URL = http://quantumleap:8668

POSTGRES_DB = smartports
TIMESCALE_DB = smartports_timescale
MONGODB = mongodb://mongo:27017
```

---

## 📈 Expected Performance

```
Update Cycles per Day:

AEMET Weather:          48 updates/day (30 min intervals)
MeteoGalicia:           48 updates/day (30 min intervals)
Puertos del Estado:     96 updates/day (15 min intervals)
Open-Meteo Marine:      48 updates/day (30 min intervals)

Berth Status:          288 updates/day (5 min intervals)
Availability:          288 updates/day (5 min intervals)
Vessel Data:         1,440 updates/day (1 min intervals)
Air Quality:            24 updates/day (1 hour intervals)

Total:               2,280 data points per day
                    ~1.6 points per minute average
                    
Entities in Orion-LD: ~150-200 active entities
Historical records in TimescaleDB: ~50,000 in first week

Storage:
  Orion-LD (MongoDB): ~50 MB (entity documents)
  TimescaleDB: ~200 MB per week (7-day retention)
  Redis Cache: ~10 MB (active task state)
```

---

## 🚀 Production Deployment Considerations

```
✅ Ready for Production:
   - Real API credentials (AEMET JWT token)
   - Error handling on all connectors
   - Automatic retry with exponential backoff
   - Data provenance tracking
   - Fallback to simulators if API fails
   - Health checks on all endpoints
   - Comprehensive logging
   - Docker-based infrastructure
   - HTTPS support (Nginx reverse proxy)

⏱️  Future Enhancements:
   - Additional AIS/GPS APIs for vessel tracking
   - Port Authority integration for berth/vessel data
   - Real-time alerts on threshold violations
   - ML forecasting integrated with real weather
   - Blockchain audit trail for high-value operations
   - GraphQL API layer
```

---

**Status:** ✅ Complete and operational with real Spanish meteorological data flowing into SmartPorts
