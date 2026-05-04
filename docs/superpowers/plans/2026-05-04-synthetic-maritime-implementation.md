# Synthetic Maritime Ecosystem Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar un sistema completo de generación de datos sintéticos masivos (4500 buques, 320 atraques, 180 sensores) con simulación dinámica continua para los puertos gallegos.

**Architecture:** Módulo generators/ aislado que genera entidades NGSI-LD reutilizando builders/services existentes. Simulación continua mediante Celery task que actualiza estados y genera observaciones. Endpoint REST para regeneración en vivo.

**Tech Stack:** FastAPI, Orion-LD, PostgreSQL, Redis, Celery, NGSI-LD, pytest

---

## Implementation Phases

### Phase 1: Core Generators (Tasks 1-6)
- Module structure, config, port profiles, vessel/berth/sensor factories

### Phase 2: Simulation & Validation (Tasks 7-9)
- Historical initialization, data validation, orchestrator

### Phase 3: Backend Integration (Tasks 10-12)
- Simulation engine, Celery tasks, admin endpoint

### Phase 4: Finalization (Tasks 13-15)
- Integration with load_seed, tests, documentation

---

## Task 1: Create generators module structure

- [ ] **Step 1: Create `backend/generators/__init__.py`**

```python
"""Synthetic maritime data generation for Galician ports."""

__version__ = "1.0.0"

from .port_profiles import load_port_profiles
from .vessel_factory import VesselFactory
from .berth_generator import BerthGenerator
from .sensor_factory import SensorFactory
from .scenario_config import ScenarioConfig
from .simulation_initializer import SimulationInitializer
from .synthetic_data_generator import SyntheticDataGenerator
from .data_validator import DataValidator

__all__ = [
    "load_port_profiles",
    "VesselFactory",
    "BerthGenerator",
    "SensorFactory",
    "ScenarioConfig",
    "SimulationInitializer",
    "SyntheticDataGenerator",
    "DataValidator",
]
```

- [ ] **Step 2: Commit**

```bash
git add backend/generators/__init__.py
git commit -m "feat: initialize generators module structure"
```

---

## Task 2: Implement ScenarioConfig

**Files:** `backend/generators/scenario_config.py`, `tests/generators/test_scenario_config.py`

- [ ] **Step 1: Create test file with scenario tests**

```python
# tests/generators/test_scenario_config.py
import pytest
from backend.generators.scenario_config import ScenarioConfig


def test_scenario_config_xlarge():
    config = ScenarioConfig(volume="xlarge", seed=42)
    assert config.num_vessels == 4500
    assert config.num_berths == 320
    assert config.num_sensors == 180


def test_invalid_volume_raises_error():
    with pytest.raises(ValueError):
        ScenarioConfig(volume="invalid")
```

- [ ] **Step 2: Run pytest (expect failure)**

```bash
pytest tests/generators/test_scenario_config.py -v
```

- [ ] **Step 3: Implement ScenarioConfig**

```python
# backend/generators/scenario_config.py
from typing import Dict, Any, Optional
import random


class ScenarioConfig:
    """Configuration for synthetic data generation scenarios."""
    
    SCENARIOS = {
        "small": {"num_vessels": 300, "num_berths": 50, "num_sensors": 40},
        "medium": {"num_vessels": 1500, "num_berths": 150, "num_sensors": 80},
        "large": {"num_vessels": 2500, "num_berths": 180, "num_sensors": 100},
        "xlarge": {"num_vessels": 4500, "num_berths": 320, "num_sensors": 180},
    }
    
    VESSEL_ARCHETYPES = {
        "fishing": {"ratio": 0.35, "speed_knots_min": 8, "speed_knots_max": 14},
        "merchant": {"ratio": 0.25, "speed_knots_min": 12, "speed_knots_max": 18},
        "auxiliary": {"ratio": 0.20, "speed_knots_min": 6, "speed_knots_max": 12},
        "oceanic": {"ratio": 0.15, "speed_knots_min": 14, "speed_knots_max": 20},
        "recreational": {"ratio": 0.05, "speed_knots_min": 4, "speed_knots_max": 10},
    }
    
    def __init__(self, volume: str = "xlarge", historical_days: Optional[int] = None, seed: int = 42):
        if volume not in self.SCENARIOS:
            raise ValueError(f"Invalid volume '{volume}'")
        
        self.volume = volume
        self.seed = seed
        scenario = self.SCENARIOS[volume]
        self.num_vessels = scenario["num_vessels"]
        self.num_berths = scenario["num_berths"]
        self.num_sensors = scenario["num_sensors"]
        self.historical_days = historical_days or scenario.get("historical_days", 90)
        self.vessel_archetypes = self.VESSEL_ARCHETYPES.copy()
        self.time_acceleration = 24
        self.tick_interval_minutes = 5
        self.days_per_tick = 2
        random.seed(self.seed)
```

- [ ] **Step 4: Run pytest (expect pass)**

```bash
pytest tests/generators/test_scenario_config.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/generators/scenario_config.py tests/generators/test_scenario_config.py
git commit -m "feat: implement scenario configuration"
```

---

## Task 3: Implement PortProfiles

**Files:** `backend/generators/port_profiles.py`, `tests/generators/test_port_profiles.py`

- [ ] **Step 1: Write tests**

```python
# tests/generators/test_port_profiles.py
from backend.generators.port_profiles import load_port_profiles, PortProfile


def test_load_port_profiles_returns_8_ports():
    ports = load_port_profiles()
    assert len(ports) == 8
    assert all(isinstance(p, PortProfile) for p in ports)


def test_a_coruna_port_properties():
    ports = load_port_profiles()
    a_coruna = next(p for p in ports if p.key == "a-coruna")
    assert a_coruna.name == "Puerto de A Coruña"
    assert a_coruna.berth_count_est == 50
```

- [ ] **Step 2: Implement PortProfiles**

```python
# backend/generators/port_profiles.py
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class PortProfile:
    key: str
    name: str
    coordinates: Tuple[float, float]
    municipality: str
    port_type: str
    authority_name: str
    berth_count_est: int
    vessel_count_est: int


def load_port_profiles() -> List[PortProfile]:
    ports = [
        PortProfile(
            key="a-coruna",
            name="Puerto de A Coruña",
            coordinates=[-8.3936, 43.3613],
            municipality="A Coruña",
            port_type="commercial",
            authority_name="Autoridad Portuaria de A Coruña",
            berth_count_est=50,
            vessel_count_est=700,
        ),
        PortProfile(
            key="vigo",
            name="Puerto de Vigo",
            coordinates=[-8.7670, 42.2362],
            municipality="Vigo",
            port_type="commercial_fishing",
            authority_name="Autoridad Portuaria de Vigo",
            berth_count_est=60,
            vessel_count_est=800,
        ),
        PortProfile(
            key="ferrol",
            name="Puerto de Ferrol",
            coordinates=[-8.2444, 43.4667],
            municipality="Ferrol",
            port_type="naval_commercial",
            authority_name="Autoridad Portuaria de Ferrol-San Cibrao",
            berth_count_est=45,
            vessel_count_est=550,
        ),
        PortProfile(
            key="marin",
            name="Puerto de Marín",
            coordinates=[-8.7033, 42.3967],
            municipality="Marín",
            port_type="mixed",
            authority_name="Autoridad Portuaria de Marín",
            berth_count_est=25,
            vessel_count_est=300,
        ),
        PortProfile(
            key="vilagarcia",
            name="Puerto de Vilagarcía de Arousa",
            coordinates=[-8.7681, 42.6153],
            municipality="Vilagarcía de Arousa",
            port_type="commercial_fishing",
            authority_name="Autoridad Portuaria de Vilagarcía",
            berth_count_est=35,
            vessel_count_est=450,
        ),
        PortProfile(
            key="ribeira",
            name="Puerto de Ribeira",
            coordinates=[-9.2717, 42.5544],
            municipality="Ribeira",
            port_type="fishing",
            authority_name="Autoridad Portuaria de Ribeira",
            berth_count_est=30,
            vessel_count_est=550,
        ),
        PortProfile(
            key="burela",
            name="Puerto de Burela",
            coordinates=[-7.5817, 43.3283],
            municipality="Burela",
            port_type="fishing",
            authority_name="Autoridad Portuaria de Burela",
            berth_count_est=20,
            vessel_count_est=400,
        ),
        PortProfile(
            key="baiona",
            name="Puerto de Baiona",
            coordinates=[-8.8350, 42.1205],
            municipality="Baiona",
            port_type="recreational",
            authority_name="Autoridad Portuaria de Baiona",
            berth_count_est=15,
            vessel_count_est=250,
        ),
    ]
    return ports
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/generators/test_port_profiles.py -v
git add backend/generators/port_profiles.py tests/generators/test_port_profiles.py
git commit -m "feat: implement port profiles for 8 Galician ports"
```

---

## Task 4-6: Implement Vessel, Berth, Sensor Factories

*Follow same TDD pattern as Tasks 2-3 for:*
- `backend/generators/vessel_factory.py` → generates 4500 vessels
- `backend/generators/berth_generator.py` → generates 320 berths
- `backend/generators/sensor_factory.py` → generates 180 sensors

Each factory follows TDD: write test → run fail → implement → pass → commit

---

## Task 7: Implement SimulationInitializer

- [ ] **Create `backend/generators/simulation_initializer.py`**

```python
# backend/generators/simulation_initializer.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random


class SimulationInitializer:
    def __init__(self, ports, config, vessel_factory):
        self.ports = ports
        self.config = config
        self.vessel_factory = vessel_factory
    
    def create_historical_movement(self) -> List[Dict[str, Any]]:
        """Create 90 days of historical movement data."""
        updates = []
        now = datetime.utcnow()
        
        for day_offset in range(self.config.historical_days):
            timestamp = now - timedelta(days=self.config.historical_days - day_offset)
            
            for _ in range(50):  # 50 updates per day
                update = {
                    "timestamp": timestamp.isoformat() + "Z",
                    "vessel_id": f"urn:ngsi-ld:Vessel:galicia-fishing-{random.randint(1, 1000)}",
                    "state": random.choice(["DOCKED", "MOVING", "ANCHORED"]),
                    "location": [random.uniform(-10, -7), random.uniform(42, 44)],
                }
                updates.append(update)
        
        return updates
```

---

## Task 8: Implement DataValidator

- [ ] **Create `backend/generators/data_validator.py`**

```python
# backend/generators/data_validator.py
from typing import List, Dict, Any


class DataValidator:
    def __init__(self):
        self.errors = []
    
    def validate_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.errors = []
        self._check_duplicate_ids(entities)
        self._check_references(entities)
        self._check_coordinates(entities)
        
        return {"valid": len(self.errors) == 0, "errors": self.errors}
    
    def _check_duplicate_ids(self, entities):
        ids = [e.get("id") for e in entities]
        seen = set()
        for entity_id in ids:
            if entity_id in seen:
                self.errors.append(f"Duplicate ID: {entity_id}")
            else:
                seen.add(entity_id)
    
    def _check_references(self, entities):
        entity_ids = {e.get("id") for e in entities}
        for entity in entities:
            for key, value in entity.items():
                if isinstance(value, dict) and value.get("type") == "Relationship":
                    ref_id = value.get("object")
                    if ref_id and ref_id not in entity_ids:
                        self.errors.append(f"Invalid reference: {ref_id}")
    
    def _check_coordinates(self, entities):
        galicia_bounds = {"lon_min": -10, "lon_max": -7, "lat_min": 42, "lat_max": 44}
        
        for entity in entities:
            location = entity.get("location")
            if location and location.get("type") == "GeoProperty":
                coords = location.get("value", {}).get("coordinates", [])
                if len(coords) >= 2:
                    lon, lat = coords[0], coords[1]
                    if not (galicia_bounds["lon_min"] < lon < galicia_bounds["lon_max"]):
                        self.errors.append(f"Invalid longitude: {lon}")
                    if not (galicia_bounds["lat_min"] < lat < galicia_bounds["lat_max"]):
                        self.errors.append(f"Invalid latitude: {lat}")
```

---

## Task 9: Implement SyntheticDataGenerator (Orchestrator)

- [ ] **Create `backend/generators/synthetic_data_generator.py`**

```python
# backend/generators/synthetic_data_generator.py
import logging
from typing import List, Dict, Any

from backend.generators.scenario_config import ScenarioConfig
from backend.generators.port_profiles import load_port_profiles
from backend.generators.vessel_factory import VesselFactory
from backend.generators.berth_generator import BerthGenerator
from backend.generators.sensor_factory import SensorFactory
from backend.generators.data_validator import DataValidator


logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    def __init__(self, config: ScenarioConfig):
        self.config = config
        self.ports = load_port_profiles()
        self.validator = DataValidator()
    
    def generate_all(self) -> List[Dict[str, Any]]:
        logger.info("Generating all synthetic entities...")
        
        entities = []
        
        # Generate ports
        entities.extend(self._generate_ports())
        
        # Generate berths
        berths = BerthGenerator(self.ports, self.config).generate_all_berths()
        entities.extend(berths)
        
        # Generate vessels
        vessel_factory = VesselFactory(self.config)
        vessels = vessel_factory.generate_all_vessels()
        entities.extend(vessels)
        
        # Generate sensors
        sensors = SensorFactory(self.ports, self.config).generate_all_sensors()
        entities.extend(sensors)
        
        # Validate
        result = self.validator.validate_entities(entities)
        if not result["valid"]:
            logger.warning(f"Validation errors: {result['errors']}")
        
        logger.info(f"Total entities: {len(entities)}")
        return entities
    
    def _generate_ports(self) -> List[Dict[str, Any]]:
        from backend.services.ngsi_builders import PortBuilder
        
        ports_list = []
        for port in self.ports:
            port_id = f"urn:ngsi-ld:Port:galicia-{port.key}"
            authority_id = f"urn:ngsi-ld:PortAuthority:autoridad-{port.key}"
            
            entity = PortBuilder.build(
                port_id=port_id,
                name=port.name,
                coordinates=port.coordinates,
                description=f"Port of {port.municipality}, Galicia",
                port_type="SeaPort",
                authority_id=authority_id,
            )
            ports_list.append(entity)
        
        return ports_list
```

---

## Task 10: Implement SimulationEngine

- [ ] **Create `backend/services/simulation_engine.py`**

```python
# backend/services/simulation_engine.py
from datetime import datetime, timedelta
from typing import Dict, Any
import random
import logging


logger = logging.getLogger(__name__)


class SimulationEngine:
    def __init__(self):
        self.time_acceleration = 24
        self.tick_interval_minutes = 5
        self.days_per_tick = 2
        self.state_transitions = {
            "fishing": ["DOCKED", "LEAVING_PORT", "FISHING", "RETURNING"],
            "merchant": ["DOCKED", "LEAVING_PORT", "MOVING", "APPROACHING_PORT"],
            "auxiliary": ["DOCKED", "IN_HARBOR_TRANSIT", "MANEUVERING"],
            "oceanic": ["OPEN_SEA", "APPROACHING_PORT", "DOCKED"],
            "recreational": ["DOCKED", "IN_HARBOR_TRANSIT"],
        }
    
    def advance_time(self, current_time: datetime, delta_hours: int = 48) -> datetime:
        real_advancement_hours = delta_hours / self.time_acceleration
        return current_time + timedelta(hours=real_advancement_hours)
    
    def update_vessel_state(self, vessel: Dict[str, Any], archetype: str) -> Dict[str, Any]:
        current_state = vessel.get("state", {}).get("value", "DOCKED")
        valid_states = self.state_transitions.get(archetype, ["DOCKED", "MOVING"])
        
        if random.random() < 0.3:
            idx = valid_states.index(current_state) if current_state in valid_states else 0
            next_state = valid_states[(idx + 1) % len(valid_states)]
            vessel["state"]["value"] = next_state
        
        return vessel
    
    def generate_air_quality_observation(self, sensor_id: str) -> Dict[str, Any]:
        now = datetime.utcnow()
        return {
            "id": f"urn:ngsi-ld:AirQualityObserved:{sensor_id.split(':')[-1]}-{int(now.timestamp())}",
            "type": "AirQualityObserved",
            "PM2_5": {"type": "Property", "value": round(random.uniform(15, 40), 1)},
            "PM10": {"type": "Property", "value": round(random.uniform(25, 60), 1)},
            "NO2": {"type": "Property", "value": round(random.uniform(40, 80), 1)},
            "observedAt": now.isoformat() + "Z"
        }
    
    def generate_weather_observation(self, sensor_id: str) -> Dict[str, Any]:
        now = datetime.utcnow()
        return {
            "id": f"urn:ngsi-ld:WeatherObserved:{sensor_id.split(':')[-1]}-{int(now.timestamp())}",
            "type": "WeatherObserved",
            "temperature": {"type": "Property", "value": round(random.uniform(8, 22), 1)},
            "relativeHumidity": {"type": "Property", "value": round(random.uniform(60, 95), 1)},
            "windSpeed": {"type": "Property", "value": round(random.uniform(2, 15), 1)},
            "observedAt": now.isoformat() + "Z"
        }
```

---

## Task 11: Implement Celery Simulation Tasks

- [ ] **Create `backend/tasks/simulation_tasks.py`**

```python
# backend/tasks/simulation_tasks.py
import logging
from datetime import datetime
from backend.tasks.celery_app import app
from backend.services.simulation_engine import SimulationEngine
from backend.services.orion_service import OrionService


logger = logging.getLogger(__name__)


@app.task(bind=True, name="tasks.tick_simulation")
def tick_simulation(self):
    try:
        logger.info("Starting simulation tick...")
        engine = SimulationEngine()
        orion = OrionService()
        
        # Get and update vessels
        vessels = orion.get_entities(entity_type="Vessel", limit=5000)
        updated_count = 0
        for vessel in vessels:
            archetype = vessel["id"].split("-")[2]
            updated_vessel = engine.update_vessel_state(vessel, archetype)
            orion.upsert_entity(updated_vessel)
            updated_count += 1
        
        # Generate observations
        sensors = orion.get_entities(entity_type="Device", limit=200)
        observation_count = 0
        for sensor in sensors:
            sensor_type = sensor.get("type_sensor", {}).get("value", "")
            obs = engine.generate_air_quality_observation(sensor["id"]) if "Air" in sensor_type else engine.generate_weather_observation(sensor["id"])
            orion.create_entity(obs)
            observation_count += 1
        
        logger.info(f"Tick complete: {updated_count} vessels, {observation_count} observations")
        return {"status": "completed", "vessels_updated": updated_count, "observations_created": observation_count}
    
    except Exception as e:
        logger.error(f"Error in simulation tick: {e}", exc_info=True)
        raise
```

- [ ] **Register in `backend/tasks/celery_app.py`:**

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'tick-simulation': {
        'task': 'tasks.tick_simulation',
        'schedule': crontab(minute='*/5'),
    },
}
```

---

## Task 12: Implement Admin Endpoint

- [ ] **Create `backend/api/routes/admin.py`**

```python
# backend/api/routes/admin.py
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/synthetic", tags=["admin"])


class RegenerateSyntheticDataRequest(BaseModel):
    volume: str = "xlarge"
    historical_days: int = 90
    seed: Optional[int] = None
    purge_first: bool = False


@router.post("/regenerate")
async def regenerate_synthetic_data(request: RegenerateSyntheticDataRequest):
    try:
        from backend.generators.synthetic_data_generator import SyntheticDataGenerator
        from backend.generators.scenario_config import ScenarioConfig
        from backend.services.orion_service import OrionService
        
        logger.info(f"Regenerating synthetic data: volume={request.volume}")
        
        config = ScenarioConfig(volume=request.volume, historical_days=request.historical_days, seed=request.seed or 42)
        generator = SyntheticDataGenerator(config)
        entities = generator.generate_all()
        
        orion = OrionService()
        for entity in entities:
            orion.upsert_entity(entity)
        
        logger.info(f"Loaded {len(entities)} entities")
        
        return {
            "status": "completed",
            "message": f"Successfully regenerated {len(entities)} entities",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error regenerating: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

- [ ] **Register in `backend/main.py`:**

```python
from backend.api.routes import admin

app.include_router(admin.router, prefix="/api/v1")
```

---

## Task 13: Integrate with load_seed.py

- [ ] **Modify `backend/scripts/load_seed.py`:**

```python
parser.add_argument("--synthetic-xlarge", action="store_true")
parser.add_argument("--synthetic-volume", choices=["small", "medium", "large", "xlarge"], default="xlarge")

if args.synthetic_xlarge or args.synthetic_volume:
    from backend.generators.synthetic_data_generator import SyntheticDataGenerator
    from backend.generators.scenario_config import ScenarioConfig
    
    logger.info(f"Generating synthetic data (volume={args.synthetic_volume})...")
    config = ScenarioConfig(volume=args.synthetic_volume, historical_days=90)
    generator = SyntheticDataGenerator(config)
    entities = generator.generate_all()
    
    logger.info(f"Loading {len(entities)} entities to Orion-LD...")
    for entity in entities:
        orion.upsert_entity(entity)
```

---

## Task 14: Run All Tests

- [ ] **Step 1: Run all generator tests**

```bash
pytest tests/generators/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 2: Run simulation engine tests**

```bash
pytest tests/services/test_simulation_engine.py -v
```

Expected: All tests PASS

- [ ] **Step 3: Test load_seed integration**

```bash
python backend/scripts/load_seed.py --synthetic-xlarge --dry-run
```

Expected: No errors, shows entity counts

---

## Task 15: Final Commit and Documentation

- [ ] **Step 1: Commit all remaining changes**

```bash
git add -A
git commit -m "feat: complete synthetic maritime data ecosystem implementation

- 4500 realistic vessels with archetype-based behavior
- 320 heterogeneous berths across 8 ports
- 180 IoT sensors with environmental observations
- 90-day historical data for ML training
- Simulation engine with state machines
- Celery periodic task for continuous updates
- Admin endpoint for dynamic regeneration
- Full test coverage and validation"
```

- [ ] **Step 2: Update README**

Add to README.md:

```markdown
## Synthetic Data Generation

Generate xlarge maritime ecosystem:

```bash
docker compose up -d
python backend/scripts/load_seed.py --synthetic-xlarge
```

Or regenerate:
```bash
curl -X POST http://localhost:8000/api/v1/admin/synthetic/regenerate \
  -H "Content-Type: application/json" \
  -d '{"volume":"xlarge","historical_days":90}'
```

Scenarios: small (300), medium (1500), large (2500), xlarge (4500) vessels
```

- [ ] **Step 3: Final verification**

```bash
pytest tests/generators tests/services/test_simulation_engine.py -v --cov=backend.generators --cov-report=term-missing
```

Expected: >80% coverage, all tests passing

**Implementation Complete ✓**

