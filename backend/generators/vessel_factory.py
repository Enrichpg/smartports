
import random
from typing import List, Dict, Any
from datetime import datetime

class VesselFactory:
    def __init__(self, config):
        self.config = config
        self.vessel_counter = 0
    
    def generate_vessel(self, archetype: str, port_key: str = None, state: str = None) -> Dict[str, Any]:
        self.vessel_counter += 1
        vessel_id = f"urn:ngsi-ld:Vessel:galicia-{archetype}-{self.vessel_counter}"
        now = datetime.utcnow().isoformat() + "Z"
        
        return {
            "id": vessel_id,
            "type": "Vessel",
            "name": {"type": "Property", "value": f"Vessel-{self.vessel_counter}"},
            "state": {"type": "Property", "value": state or random.choice(["DOCKED", "MOVING", "ANCHORED"])},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [random.uniform(-10, -7), random.uniform(42, 44)]}},
            "last_updated": {"type": "Property", "value": now},
        }
    
    def generate_all_vessels(self) -> List[Dict[str, Any]]:
        vessels = []
        counts = self.config.get_vessel_count_by_archetype()
        for archetype, count in counts.items():
            for _ in range(count):
                vessels.append(self.generate_vessel(archetype))
        return vessels
