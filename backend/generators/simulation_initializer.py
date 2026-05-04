
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

class SimulationInitializer:
    def __init__(self, ports, config, vessel_factory):
        self.ports = ports
        self.config = config
        self.vessel_factory = vessel_factory
    
    def create_historical_movement(self) -> List[Dict[str, Any]]:
        updates = []
        now = datetime.utcnow()
        for day_offset in range(self.config.historical_days):
            timestamp = now - timedelta(days=self.config.historical_days - day_offset)
            for _ in range(50):
                update = {
                    "timestamp": timestamp.isoformat() + "Z",
                    "vessel_id": f"urn:ngsi-ld:Vessel:galicia-fishing-{random.randint(1, 1000)}",
                    "state": random.choice(["DOCKED", "MOVING", "ANCHORED"]),
                    "location": [random.uniform(-10, -7), random.uniform(42, 44)],
                }
                updates.append(update)
        return updates
