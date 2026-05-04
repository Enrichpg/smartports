
import random
from typing import List, Dict, Any

class BerthGenerator:
    def __init__(self, ports, config):
        self.ports = ports
        self.config = config
        self.berth_counter = 0
    
    def generate_berth_for_port(self, port) -> Dict[str, Any]:
        self.berth_counter += 1
        berth_id = f"urn:ngsi-ld:Berth:galicia-{port.key}-{self.berth_counter}"
        
        return {
            "id": berth_id,
            "type": "Berth",
            "name": {"type": "Property", "value": f"Berth-{self.berth_counter}"},
            "length": {"type": "Property", "value": round(random.uniform(50, 300), 1)},
            "draft": {"type": "Property", "value": round(random.uniform(4, 14), 1)},
            "state": {"type": "Property", "value": random.choice(["available", "occupied", "maintenance"])},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [port.coordinates[0] + random.uniform(-0.01, 0.01), port.coordinates[1] + random.uniform(-0.01, 0.01)]}},
            "port": {"type": "Relationship", "object": f"urn:ngsi-ld:Port:galicia-{port.key}"},
        }
    
    def generate_all_berths(self) -> List[Dict[str, Any]]:
        berths = []
        total_est = sum(p.berth_count_est for p in self.ports)
        for port in self.ports:
            ratio = port.berth_count_est / total_est
            count = max(1, int(self.config.num_berths * ratio))
            for _ in range(count):
                berths.append(self.generate_berth_for_port(port))
        return berths[:self.config.num_berths]
