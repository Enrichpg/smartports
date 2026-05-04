
import random
from typing import List, Dict, Any

class SensorFactory:
    def __init__(self, ports, config):
        self.ports = ports
        self.config = config
        self.sensor_counter = 0
    
    def generate_sensor(self, port, sensor_type: str) -> Dict[str, Any]:
        self.sensor_counter += 1
        sensor_id = f"urn:ngsi-ld:Device:galicia-{sensor_type.lower()}-{port.key}-{self.sensor_counter}"
        
        return {
            "id": sensor_id,
            "type": "Device",
            "name": {"type": "Property", "value": f"Sensor-{sensor_type}-{self.sensor_counter}"},
            "type_sensor": {"type": "Property", "value": sensor_type},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [port.coordinates[0] + random.uniform(-0.005, 0.005), port.coordinates[1] + random.uniform(-0.005, 0.005)]}},
            "status": {"type": "Property", "value": "operational"},
            "port": {"type": "Relationship", "object": f"urn:ngsi-ld:Port:galicia-{port.key}"},
        }
    
    def generate_all_sensors(self) -> List[Dict[str, Any]]:
        sensors = []
        for port in self.ports:
            for _ in range(random.randint(1, 3)):
                sensors.append(self.generate_sensor(port, "AirQualityDevice"))
            for _ in range(random.randint(1, 3)):
                sensors.append(self.generate_sensor(port, "WeatherDevice"))
        return sensors[:self.config.num_sensors]
