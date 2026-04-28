# SmartPorts Real APIs Quick Start Guide

**Date:** April 28, 2026  
**Status:** ✅ Ready to Use

---

## 🚀 You're Ready to Use Real Data!

SmartPorts now has **5 real APIs integrated** with your **AEMET credentials pre-configured**:

### ✅ Real APIs Active

1. **AEMET OpenData** (Spanish meteorological service)
   - Your JWT API key: Already configured in `.env`
   - Updates: Every 30 minutes
   - Provides: Temperature, humidity, pressure, wind, precipitation

2. **MeteoGalicia** (Galician regional weather)
   - Free (no auth needed)
   - Updates: Every 30 minutes
   - Provides: Regional weather + oceanographic context

3. **Puertos del Estado** (Spain's Port Authority)
   - Free (no auth needed)
   - Updates: Every 15 minutes
   - Provides: Wave height, direction, period, water temp

4. **Open-Meteo Marine** (Free marine weather)
   - Free (no auth needed)
   - Updates: Every 30 minutes
   - Provides: Wave data, forecasts, offshore conditions

5. **Open-Meteo Air Quality** (Free air quality data) ✨ NEW
   - Free (no auth needed)
   - Updates: Every 1 hour
   - Provides: PM10, PM2.5, NO2, O3, SO2, CO, AQI, UV Index

---

## 🎯 Starting the System

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Celery Beat (Scheduler)
```bash
# Terminal 1
cd backend
celery -A tasks.celery beat --loglevel=info
```

Expected output:
```
celery beat v5.3.4 (sun) running...
LocalTime -> 2026-04-28 14:30:00
Version -> celery 5.3.4
...
Scheduler: celery.beat.PersistentScheduler
db -> celery-beat-schedule
Loaded 8 scheduled tasks
```

### Step 3: Start Celery Worker (Executor)
```bash
# Terminal 2
cd backend
celery -A tasks.celery worker --loglevel=info
```

Expected output:
```
celery worker ready.
pool: solo (max concurrency: 1)
[Tasks]
  * ingest_air_quality
  * ingest_availability
  * ingest_berth_status
  * ingest_marine_weather_openmeteo
  * ingest_sea_conditions
  * ingest_vessel_data
  * ingest_weather_aemet
  * ingest_weather_meteogalicia
```

### Step 4: Start FastAPI Backend
```bash
# Terminal 3
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 5: Verify Data Flow

```bash
# Check API status and data sources
curl http://localhost:8000/api/v1/sources/status

# Get live weather (Vigo port)
curl http://localhost:8000/api/v1/ports/80003/live/weather

# Get live oceanographic data
curl http://localhost:8000/api/v1/ports/80003/live/ocean

# Get operational data (berths, vessels)
curl http://localhost:8000/api/v1/ports/80003/live/operations
```

### Step 6: Setup Historical Persistence (Optional)

```bash
# Create QuantumLeap subscriptions for historical storage
python backend/scripts/setup_quantumleap_subscriptions.py
```

---

## 📋 Data Ingestion Schedule

All tasks run automatically via Celery Beat:

| Task | First Run | Frequency | Source |
|---|---|---|---|
| AEMET Weather | Now | Every 30 min | Real API ✅ |
| MeteoGalicia | Now | Every 30 min | Real API ✅ |
| Puertos del Estado | Now | Every 15 min | Real API ✅ |
| Open-Meteo Marine | Now | Every 30 min | Real API ✅ |
| Open-Meteo Air Quality | Now | Every 1 hour | Real API ✅ |
| Berth Status | Now | Every 5 min | Simulator |
| Availability | Now | Every 5 min | Simulator |
| Vessel Data | Now | Every 1 min | Simulator |

---

## 🔍 What Happens on Each Cycle

### AEMET (Every 30 min)
```
1. Fetch from: https://opendata.aemet.es/opendata
   Stations: Vigo (35012), Ferrol (15023), Coruña (15001)
   
2. Transform to NGSI-LD WeatherObserved
   - temperature
   - humidity
   - pressure
   - wind_speed
   - wind_direction
   - precipitation

3. Publish to Orion-LD
4. Subscribe → QuantumLeap → Historical storage
5. Available via: GET /api/v1/ports/{port_id}/live/weather
```

### Open-Meteo Marine (Every 30 min)
```
1. Fetch from: https://marine-api.open-meteo.com/v1/marine
   Locations: Vigo Offshore, Ferrol Offshore, Coruña Offshore, Atlantic
   
2. Transform to NGSI-LD SeaConditionObserved
   - significant_wave_height
   - wave_direction
   - wave_period
   - wind_wave_height
   - swell_wave_height
   - 7-day forecast

3. Publish to Orion-LD
4. Available via: GET /api/v1/ports/{port_id}/live/ocean
```

### Open-Meteo Air Quality (Every 1 hour)
```
1. Fetch from: https://air-quality-api.open-meteo.com/v1/air-quality
   Locations: Vigo, Ferrol, Coruña, Pontevedra, Lugo
   
2. Transform to NGSI-LD AirQualityObserved
   - pm10 (coarse particulates)
   - pm2_5 (fine particulates)
   - nitrogen_dioxide (NO2)
   - ozone (O3)
   - sulphur_dioxide (SO2)
   - carbon_monoxide (CO)
   - uv_index
   - AQI (calculated from PM2.5)
   - AQI level (Good, Fair, Moderate, Unhealthy, Hazardous, etc.)

3. Publish to Orion-LD
4. Available via: GET /api/v1/ports/{port_id}/live/air-quality (future endpoint)
```

---

## 📊 Example Responses

### GET `/api/v1/sources/status`
```json
{
  "timestamp": "2026-04-28T14:35:00Z",
  "sources": {
    "AEMET": {
      "type": "real",
      "status": "enabled",
      "api_key": "configured",
      "update_frequency": "1800s",
      "entities": ["WeatherObserved"]
    },
    "MeteoGalicia": {
      "type": "real",
      "status": "enabled",
      "update_frequency": "1800s",
      "entities": ["WeatherObserved", "SeaConditionObserved"]
    },
    "Puertos_del_Estado": {
      "type": "real",
      "status": "enabled",
      "update_frequency": "900s",
      "entities": ["SeaConditionObserved"]
    },
    "OpenMeteo_Marine": {
      "type": "real",
      "status": "enabled",
      "update_frequency": "1800s",
      "entities": ["SeaConditionObserved"]
    },
    "OpenMeteo_AirQuality": {
      "type": "real",
      "status": "enabled",
      "update_frequency": "3600s",
      "entities": ["AirQualityObserved"]
    }
  }
}
```

### GET `/api/v1/ports/80003/live/weather`
```json
{
  "port_id": "80003",
  "timestamp": "2026-04-28T14:30:00Z",
  "weather": {
    "temperature": 16.5,
    "humidity": 0.75,
    "pressure": 1013.2,
    "wind_speed": 8.2,
    "wind_direction": 240,
    "precipitation": 0.0
  },
  "source": "AEMET",
  "confidence": 0.95
}
```

### GET `/api/v1/ports/80003/live/ocean`
```json
{
  "port_id": "80003",
  "timestamp": "2026-04-28T14:30:00Z",
  "conditions": {
    "significant_wave_height": 1.2,
    "water_temperature": 14.8,
    "wind_speed": 8.2,
    "tide_level": 0.5
  },
  "source": "OpenMeteo",
  "data_types": ["wave_height", "wave_period", "wind_waves", "swell"]
}
```

### GET `/api/v1/ports/80003/live/air-quality` (Future Endpoint)
```json
{
  "port_id": "80003",
  "timestamp": "2026-04-28T14:30:00Z",
  "air_quality": {
    "aqi": 42,
    "aqi_level": "Good",
    "pm2_5": 8.5,
    "pm10": 15.2,
    "nitrogen_dioxide": 12.3,
    "ozone": 65.4,
    "sulphur_dioxide": 2.1,
    "carbon_monoxide": 0.3,
    "uv_index": 3.2
  },
  "source": "OpenMeteo",
  "confidence": 0.85,
  "location": "Vigo"
}
```

---

## 🔐 Your AEMET API Key

✅ **Status:** Active and configured  
📧 **Email:** enrique.pardo.ab@gmail.com  
⏰ **Issued:** April 28, 2026  
🔑 **Token:** Pre-configured in `backend/.env`

**Verify it's working:**
```bash
# This will show if AEMET is successfully fetching data
curl http://localhost:8000/api/v1/ports/80003/live/weather | jq '.source'
# Expected output: "AEMET"
```

---

## ⚠️ Important Notes

1. **AEMET API Key:** Valid JWT token, expires when AEMET revokes it
2. **No Rate Limits:** Open-Meteo allows unlimited free requests
3. **Data Origin:** Every entity includes `dataProvider` field for auditing
4. **Fallback:** If real APIs fail, simulators provide plausible synthetic data
5. **Historical:** Data automatically persists to QuantumLeap (configurable)

---

## 🐛 Troubleshooting

### Tasks not running
```bash
# Check Celery Beat logs for errors
# Terminal 1: Look for "Scheduler" messages

# Check if tasks are registered
celery -A tasks.celery inspect active
```

### AEMET API failing
```bash
# Check if API key is valid
curl -H "api_key: <your_key>" https://opendata.aemet.es/opendata/api/observacion/convencional/datos/35012

# Check backend logs for AEMET errors
# Terminal 3: Look for "AEMET" messages
```

### No data in Orion
```bash
# Check if Orion is running
curl http://orion-ld:1026/ngsi-ld/v1/entities

# Check backend error logs for publisher errors
```

---

## 📚 Documentation

- **Full API Guide:** [docs/REAL_APIS_INGESTION.md](docs/REAL_APIS_INGESTION.md)
- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **Data Model:** [docs/data_model.md](docs/data_model.md)

---

## ✨ What's Next?

1. ✅ Real APIs are flowing data
2. ⏭️ Frontend will consume via `/api/v1/ports/{id}/live/*` endpoints
3. ⏭️ ML will use historical data from QuantumLeap
4. ⏭️ Alerts will trigger on real data thresholds

**The system is now:**
- ✅ Collecting real weather data (AEMET, MeteoGalicia)
- ✅ Collecting real oceanographic data (Puertos del Estado, Open-Meteo Marine)
- ✅ Collecting real air quality data (Open-Meteo Air Quality) ✨ NEW
- ✅ Publishing to Orion-LD
- ✅ Persisting history to QuantumLeap
- ✅ Exposing via REST API
- ✅ Ready for frontend integration

**Enjoy your real-time operational platform!** 🎉
