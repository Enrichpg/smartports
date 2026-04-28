# Real APIs Ingestion Architecture - SmartPorts

**Version:** 1.0  
**Date:** April 28, 2026  
**Status:** Implementation In Progress

## 📋 Overview

SmartPorts implements an **API-first architecture** with **intelligent fallback** to simulation. This document describes the data ingestion pipeline that prioritizes real official data sources while gracefully degrading to synthetic data when APIs are unavailable or lack sufficient granularity.

## 🎯 Principle: API-First with Simulation Fallback

```
Priority Order:
1. Real official APIs
2. Derived data from real sources + business rules
3. Realistic simulators (fallback only)
```

**Result:** A credible, auditable system where data origin is always documented.

---

## 🌍 Real API Sources

### 1. AEMET OpenData (Spanish Meteorological Service)

**Type:** Official REST API  
**Authentication:** API Key  
**Update Frequency:** 30 minutes (configurable)  
**Coverage:** Spain-wide, including Galicia  

**What We Ingest:**
- Temperature (°C)
- Relative Humidity (%)
- Atmospheric Pressure (hPa)
- Wind Speed (m/s) and Direction (degrees)
- Precipitation (mm)
- Alerts and warnings

**NGSI-LD Entity:** `WeatherObserved`  
**Galician Stations:**
- Vigo (35012) → Port 80003
- Ferrol (15023) → Port 80001
- Coruña (15001) → Port 80004

**Configuration:**
```bash
AEMET_API_KEY=your_key_here
AEMET_BASE_URL=https://opendata.aemet.es/opendata
WEATHER_UPDATE_FREQUENCY=1800  # 30 minutes
```

**Task:** `ingest_weather_aemet` (Celery Beat, 30min interval)

---

### 2. MeteoGalicia (Galician Meteorological Authority)

**Type:** WMS/WCS Web Services  
**Authentication:** None (free, public)  
**Update Frequency:** 30 minutes (configurable)  
**Coverage:** Galicia + Iberian Peninsula, coastal focus  

**What We Ingest:**
- Regional meteorological observations
- Coastal data
- Marine forecasts
- Oceanographic context

**NGSI-LD Entity:** `WeatherObserved`, `SeaConditionObserved`

**Services:**
- WMS (Web Map Service): `http://forecast.cirrus.uvigo.es/thredds/wms`
- WCS (Web Coverage Service): `http://forecast.cirrus.uvigo.es/thredds/wcs`

**Configuration:**
```bash
METEOGALICIA_BASE_URL=http://forecast.cirrus.uvigo.es/thredds/wcs
METEOGALICIA_WMS_URL=http://forecast.cirrus.uvigo.es/thredds/wms
WEATHER_UPDATE_FREQUENCY=1800
```

**Task:** `ingest_weather_meteogalicia` (Celery Beat, 30min interval)

---

### 3. Puertos del Estado (Spain's Port Authority)

**Type:** Measurement Networks (Real-time)  
**Authentication:** Public data  
**Update Frequency:** 15 minutes (configurable)  
**Coverage:** Galician ports, coastal regions  

**What We Ingest:**
- Wave conditions (significant wave height, peak period, direction)
- Wind speed and direction at sea
- Water temperature
- Salinity
- Sea level / Tide
- Currents
- Real-time, historical, and forecast data

**NGSI-LD Entity:** `SeaConditionObserved`

**Main Buoys/Stations:**
- Rias Bajas Network
- Atlantic Offshore
- Cape Ortegal

**Configuration:**
```bash
PUERTOS_ESTADO_BASE_URL=https://www.puertos.es
OCEAN_CONDITIONS_UPDATE_FREQUENCY=900  # 15 minutes
```

**Task:** `ingest_sea_conditions` (Celery Beat, 15min interval)

---

### 4. Open-Meteo Marine Weather API (NEW - Apr 28, 2026)

**Type:** Free, open-source API  
**Authentication:** None (completely free, public)  
**Update Frequency:** 30 minutes (cache-friendly, configurable)  
**Coverage:** Global coverage, including Galician waters  

**Why Open-Meteo?**
- No API key required (unlike many commercial APIs)
- Excellent marine weather data specifically designed for offshore operations
- Free tier with no rate limits
- Well-documented and actively maintained
- Complementary to Puertos del Estado (offshore vs. port-specific)

**What We Ingest:**
- Wave height (significant, wind waves, swell)
- Wave direction and period
- Wind speed and direction at sea
- Sea surface temperature (where available)
- Wave forecast data (hourly, up to 7 days)

**NGSI-LD Entity:** `SeaConditionObserved`

**Galician Monitoring Locations:**
- Vigo Offshore (42.2°N, 8.8°W) → Port 80003
- Ferrol Offshore (43.5°N, 8.3°W) → Port 80001
- Coruña Offshore (43.4°N, 8.2°W) → Port 80004
- Atlantic Reference Point (42.5°N, 9.5°W) → Offshore

**API Endpoint:**
```
https://marine-api.open-meteo.com/v1/marine
```

**Configuration:**
```bash
OPENMETEO_BASE_URL=https://marine-api.open-meteo.com/v1/marine
OPENMETEO_CACHE_TTL=3600  # Cache for 1 hour (API-friendly)
MARINE_WEATHER_UPDATE_FREQUENCY=1800  # 30 minutes
```

**Example Request:**
```python
import openmeteo_requests

client = openmeteo_requests.Client()
url = "https://marine-api.open-meteo.com/v1/marine"
params = {
    "latitude": 42.2,
    "longitude": -8.8,
    "hourly": "wave_height,wave_direction,wave_period",
    "forecast_days": 7,
    "timezone": "UTC"
}
responses = client.weather_api(url, params=params)
```

**Task:** `ingest_marine_weather_openmeteo` (Celery Beat, 30min interval)

**Integration Notes:**
- Open-Meteo data complements Puertos del Estado (offshore vs port buoys)
- Provides forecasts when Puertos del Estado gives real-time observations
- Zero cost and no authentication makes it ideal as primary offshore source
- Data marked as "OpenMeteo" source in NGSI-LD entities
- Ideal for vessel route planning and weather-sensitive operations

---

### 5. Open-Meteo Air Quality API (NEW - Apr 28, 2026)

**Type:** Free, open-source API  
**Authentication:** None (completely free, public)  
**Update Frequency:** 1 hour (configurable)  
**Coverage:** Global coverage, including Galician cities  

**Why Open-Meteo Air Quality?**
- No API key required
- Real-time air quality measurements for 13 different pollutants
- 5-day forecasts included
- Free tier with no rate limits
- Well-documented API
- Complements official sources (when available)

**What We Ingest:**
- PM10 (coarse particulate matter, 10µm)
- PM2.5 (fine particulate matter, 2.5µm)
- NO2 (nitrogen dioxide)
- O3 (ozone)
- SO2 (sulfur dioxide)
- CO (carbon monoxide)
- AQI (Air Quality Index calculated from PM2.5)
- UV Index

**NGSI-LD Entity:** `AirQualityObserved`

**Galician Monitoring Locations:**
- Vigo (42.23°N, 8.72°W)
- Ferrol (43.47°N, 8.25°W)
- Coruña (43.37°N, 8.39°W)
- Pontevedra (42.43°N, 8.64°W)
- Lugo (43.13°N, 8.55°W)

**API Endpoint:**
```
https://air-quality-api.open-meteo.com/v1/air-quality
```

**Configuration:**
```bash
OPENMETEO_AIR_QUALITY_BASE_URL=https://air-quality-api.open-meteo.com/v1/air-quality
OPENMETEO_CACHE_TTL=3600  # Cache for 1 hour
AIR_QUALITY_UPDATE_FREQUENCY=3600  # 1 hour
```

**Example Request:**
```python
import openmeteo_requests
import pandas as pd

client = openmeteo_requests.Client()
url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
    "latitude": 42.2,
    "longitude": -8.7,
    "hourly": ["pm10", "pm2_5", "nitrogen_dioxide", "ozone"],
    "forecast_days": 5,
    "timezone": "UTC"
}
responses = client.weather_api(url, params=params)
response = responses[0]

# Extract hourly data as DataFrame
hourly = response.Hourly()
hourly_data = {"date": pd.date_range(...)}
for idx, var_name in enumerate(["pm10", "pm2_5", ...]):
    hourly_data[var_name] = hourly.Variables(idx).ValuesAsNumpy()

df = pd.DataFrame(data=hourly_data)
```

**Task:** `ingest_air_quality` (Celery Beat, 1hour interval)

**Integration Notes:**
- Real-time air quality measurements from multiple pollutants
- AQI automatically calculated from PM2.5 using EPA formula
- Provides early warning for poor air quality conditions
- Complements environmental monitoring systems
- Data marked as "OpenMeteo" source with 85% confidence
- Can be used to trigger environmental alerts
- Integrated with environmental monitoring dashboard

---

## 🤖 Fallback Simulators (When APIs Insufficient)

When real APIs don't provide direct data (e.g., exact berth occupancy), we use **realistic simulators** that:
- Generate coherent, plausible data
- Respect real-world constraints
- Mark themselves as "simulator" source
- Never contradict real meteorological data

### Simulator Data Types

| Entity Type | Data Source | Update Freq | Confidence |
|---|---|---|---|
| `Berth` status/occupancy | Simulator | 5 min | 0.3 |
| `BoatPlacesAvailable` | Simulator | 5 min | 0.3 |
| `Vessel` positions/status | Simulator | 1 min | 0.4 |

**Tasks:**
- `ingest_berth_status` (5min interval)
- `ingest_availability` (5min interval)
- `ingest_vessel_data` (1min interval)

---

## 🔄 Data Transformation Pipeline

```
External API
    ↓
Connector (API-specific)
    ↓
Normalization (common format)
    ↓
Transformer (to NGSI-LD)
    ↓
Orion-LD (publish/upsert)
    ↓
QuantumLeap (historical storage)
    ↓
Backend API (consume)
```

### Example: AEMET → NGSI-LD

```python
# 1. Fetch from AEMET
weather_raw = await aemet_connector.get_weather_data("35012")

# 2. Normalize
normalized = {
    "temperature": 16.5,
    "humidity": 75,
    "wind_speed": 8.2,
    # ... other fields
}

# 3. Transform to NGSI-LD
ngsi_entity = WeatherTransformer.from_aemet(
    normalized,
    location_id="35012",
    port_code="80003"
)

# 4. Publish to Orion
orion.update_entity(ngsi_entity)

# 5. QuantumLeap subscribes and persists
```

---

## 📊 Data Origin Traceability

Every entity includes source metadata:

```json
{
  "id": "urn:ngsi-ld:WeatherObserved:aemet-35012",
  "type": "WeatherObserved",
  "temperature": { "value": 16.5 },
  "dataProvider": {
    "type": "Property",
    "value": "AEMET"
  },
  "source": {
    "type": "Property",
    "value": "AEMET OpenData"
  },
  "sourceConfidence": {
    "type": "Property",
    "value": 0.95  # 0-1 scale
  }
}
```

**Data Source Values:**
- `"AEMET"` - Real data from AEMET OpenData
- `"MeteoGalicia"` - Real data from MeteoGalicia services
- `"Puertos_del_Estado"` - Real data from Port Authority
- `"simulator"` - Synthetic realistic data
- `"derived"` - Computed from other data + rules

---

## ⏱️ Celery Beat Schedule

Update frequencies (configurable via environment variables):

```python
WEATHER_UPDATE_FREQUENCY=1800          # 30 min (AEMET, MeteoGalicia)
OCEAN_CONDITIONS_UPDATE_FREQUENCY=900  # 15 min (Puertos del Estado)
BERTH_STATUS_UPDATE_FREQUENCY=300      # 5 min (Berth simulators)
AIR_QUALITY_UPDATE_FREQUENCY=3600      # 1 hour
```

### Active Schedules

| Task | Frequency | Queue | Purpose |
|---|---|---|---|
| `ingest_weather_aemet` | 30 min | `real_data` | Real weather (official) |
| `ingest_weather_meteogalicia` | 30 min | `real_data` | Regional weather (Galicia) |
| `ingest_sea_conditions` | 15 min | `real_data` | Ocean conditions (buoys) |
| `ingest_marine_weather_openmeteo` | 30 min | `real_data` | Marine weather (offshore) |
| `ingest_air_quality` | 1 hour | `real_data` | Air quality (real API) |
| `ingest_berth_status` | 5 min | `operational` | Berth occupancy (simulator) |
| `ingest_availability` | 5 min | `operational` | Boat places (simulator) |
| `ingest_vessel_data` | 1 min | `operational` | Vessel positions (simulator) |

---

## 🗄️ Orion-LD → QuantumLeap Subscriptions

Subscriptions automatically persist relevant entities to QuantumLeap for historical analysis:

```python
# Setup subscriptions
python backend/scripts/setup_quantumleap_subscriptions.py
```

**Persistent Entities:**
- `WeatherObserved` - All meteorological attributes
- `SeaConditionObserved` - Ocean conditions
- `Berth` - Status and occupancy
- `BoatPlacesAvailable` - Availability metrics
- `Vessel` - Position and status
- `AirQualityObserved` - Air quality metrics

---

## 🔗 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL REAL DATA SOURCES                   │
├─────────────────────────────────────────────────────────────────┤
│  AEMET         MeteoGalicia        Puertos del Estado           │
│  Weather API   WMS/WCS Services    Real-time Buoys             │
└────────────┬──────────────┬─────────────────────────┬──────────┘
             │              │                         │
             ↓              ↓                         ↓
       ┌──────────────────────────────────────────────────┐
       │          CONNECTOR LAYER (API-specific)          │
       │    - Handle auth, timeouts, retries, errors     │
       └──────────────┬──────────────────────────────────┘
                      ↓
       ┌──────────────────────────────────────────────────┐
       │      TRANSFORMER LAYER (NGSI-LD format)         │
       │    - Normalize and convert to entities           │
       └──────────────┬──────────────────────────────────┘
                      ↓
       ┌──────────────────────────────────────────────────┐
       │           ORION-LD (Context Broker)              │
       │        Publish/Update NGSI-LD Entities           │
       └──────────────┬──────────────────────────────────┘
                      ↓
       ┌──────────────────────────────────────────────────┐
       │      QUANTUMLEAP (Time Series Database)          │
       │     Subscribed updates → Historical Storage      │
       └──────────────┬──────────────────────────────────┘
                      ↓
       ┌──────────────────────────────────────────────────┐
       │         BACKEND API (Data Exposure)              │
       │   GET /ports/{id}/live/weather                   │
       │   GET /ports/{id}/history/weather                │
       │   GET /sources/status                            │
       └──────────────┬──────────────────────────────────┘
                      ↓
                 FRONTEND (React/Leaflet)

┌─────────────────────────────────────────────────────────────────┐
│              FALLBACK: Simulators (When APIs fail)               │
│  - Berth Status Simulator                                       │
│  - Availability Simulator                                       │
│  - Vessel State Simulator                                       │
│  - Air Quality Simulator                                        │
│  → Mark as "simulator" source for transparency                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Running the Ingestion Pipeline

### 1. Start Celery Worker

```bash
# Terminal 1: Start Celery Beat (scheduler)
celery -A backend.tasks.celery beat --loglevel=info

# Terminal 2: Start Celery Worker (task executor)
celery -A backend.tasks.celery worker --loglevel=info
```

### 2. Setup QuantumLeap Subscriptions

```bash
# One-time setup to enable historical storage
python backend/scripts/setup_quantumleap_subscriptions.py
```

### 3. Verify Data Flow

```bash
# Check API status
curl http://localhost:8000/api/v1/sources/status

# Get live weather for a port
curl http://localhost:8000/api/v1/ports/80003/live/weather

# Get operational data
curl http://localhost:8000/api/v1/ports/80003/live/operations
```

---

## 🛠️ Configuration

### Environment Variables (`.env`)

```bash
# AEMET Configuration
AEMET_API_KEY=your_api_key_here
AEMET_BASE_URL=https://opendata.aemet.es/opendata

# MeteoGalicia Configuration
METEOGALICIA_BASE_URL=http://forecast.cirrus.uvigo.es/thredds/wcs
METEOGALICIA_WMS_URL=http://forecast.cirrus.uvigo.es/thredds/wms

# Puertos del Estado Configuration
PUERTOS_ESTADO_BASE_URL=https://www.puertos.es

# Ingestion Settings
ENABLE_REAL_DATA_INGESTION=true
ENABLE_FALLBACK_SIMULATORS=true

# Update Frequencies (in seconds)
WEATHER_UPDATE_FREQUENCY=1800       # 30 minutes
AIR_QUALITY_UPDATE_FREQUENCY=3600   # 1 hour
OCEAN_CONDITIONS_UPDATE_FREQUENCY=900  # 15 minutes
BERTH_STATUS_UPDATE_FREQUENCY=300   # 5 minutes

# Request Configuration
API_REQUEST_TIMEOUT=30
API_MAX_RETRIES=3
```

---

## ✅ Validation Checklist

- [x] Connectors created (AEMET, MeteoGalicia, Puertos del Estado)
- [x] Transformers to NGSI-LD implemented
- [x] Celery tasks for ingestion defined
- [x] Celery Beat schedule configured
- [x] QuantumLeap subscriptions setup script
- [x] Backend API endpoints for data exposure
- [x] Simulators with fallback support
- [x] Data source traceability metadata
- [ ] End-to-end testing (pending)
- [ ] Production deployment validation (pending)

---

## 📝 Notes

1. **Real APIs are prioritized.** Simulators fill gaps only when real data unavailable.
2. **Data origin is auditable.** Every entity includes source metadata.
3. **Graceful degradation.** System continues operating if APIs fail temporarily.
4. **Modular design.** Each connector/simulator is independent and replaceable.
5. **Time series storage.** QuantumLeap provides historical context for analytics.

---

## 🔗 References

- AEMET OpenData: https://opendata.aemet.es/
- MeteoGalicia THREDDS: http://forecast.cirrus.uvigo.es/thredds/
- Puertos del Estado: https://www.puertos.es/
- NGSI-LD Spec: https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf
- Smart Data Models: https://smartdatamodels.org/
