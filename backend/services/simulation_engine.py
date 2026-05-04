import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import random


logger = logging.getLogger(__name__)


class SimulationEngine:
    """Engine for maritime simulation state transitions and observations."""

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
        """Advance simulation time with acceleration."""
        real_advancement_hours = delta_hours / self.time_acceleration
        return current_time + timedelta(hours=real_advancement_hours)

    def update_vessel_state(self, vessel: Dict[str, Any], archetype: str) -> Dict[str, Any]:
        """Update vessel state based on archetype transition rules."""
        current_state = vessel.get("state", {}).get("value", "DOCKED")
        valid_states = self.state_transitions.get(archetype, ["DOCKED", "MOVING"])

        if random.random() < 0.3:
            idx = valid_states.index(current_state) if current_state in valid_states else 0
            next_state = valid_states[(idx + 1) % len(valid_states)]
            vessel["state"]["value"] = next_state

        return vessel

    def generate_air_quality_observation(self, sensor_id: str) -> Dict[str, Any]:
        """Generate realistic air quality observation."""
        now = datetime.utcnow()
        sensor_key = sensor_id.split(":")[-1]
        return {
            "id": f"urn:ngsi-ld:AirQualityObserved:{sensor_key}-{int(now.timestamp())}",
            "type": "AirQualityObserved",
            "PM2_5": {"type": "Property", "value": round(random.uniform(15, 40), 1)},
            "PM10": {"type": "Property", "value": round(random.uniform(25, 60), 1)},
            "NO2": {"type": "Property", "value": round(random.uniform(40, 80), 1)},
            "O3": {"type": "Property", "value": round(random.uniform(30, 80), 1)},
            "CO": {"type": "Property", "value": round(random.uniform(0.3, 1.0), 2)},
            "SO2": {"type": "Property", "value": round(random.uniform(5, 20), 1)},
            "observedAt": now.isoformat() + "Z"
        }

    def generate_weather_observation(self, sensor_id: str) -> Dict[str, Any]:
        """Generate realistic weather observation."""
        now = datetime.utcnow()
        sensor_key = sensor_id.split(":")[-1]
        return {
            "id": f"urn:ngsi-ld:WeatherObserved:{sensor_key}-{int(now.timestamp())}",
            "type": "WeatherObserved",
            "temperature": {"type": "Property", "value": round(random.uniform(8, 22), 1)},
            "relativeHumidity": {"type": "Property", "value": round(random.uniform(60, 95), 1)},
            "atmPressure": {"type": "Property", "value": round(random.uniform(1000, 1020), 1)},
            "windSpeed": {"type": "Property", "value": round(random.uniform(2, 15), 1)},
            "windDirection": {"type": "Property", "value": round(random.uniform(0, 360), 0)},
            "observedAt": now.isoformat() + "Z"
        }
