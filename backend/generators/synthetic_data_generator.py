
import logging
from typing import List, Dict, Any
from .port_profiles import load_port_profiles
from .vessel_factory import VesselFactory
from .berth_generator import BerthGenerator
from .sensor_factory import SensorFactory
from .data_validator import DataValidator

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    def __init__(self, config):
        self.config = config
        self.ports = load_port_profiles()
        self.validator = DataValidator()
    
    def generate_all(self) -> List[Dict[str, Any]]:
        logger.info("Generating all synthetic entities...")
        entities = []
        
        # Ports
        entities.extend(self._generate_ports())
        
        # Berths
        berths = BerthGenerator(self.ports, self.config).generate_all_berths()
        entities.extend(berths)
        logger.info(f"Generated {len(berths)} berths")
        
        # Vessels
        vessel_factory = VesselFactory(self.config)
        vessels = vessel_factory.generate_all_vessels()
        entities.extend(vessels)
        logger.info(f"Generated {len(vessels)} vessels")
        
        # Sensors
        sensors = SensorFactory(self.ports, self.config).generate_all_sensors()
        entities.extend(sensors)
        logger.info(f"Generated {len(sensors)} sensors")
        
        # Validate
        result = self.validator.validate_entities(entities)
        if not result["valid"]:
            logger.warning(f"Validation errors: {result['errors']}")
        else:
            logger.info("Dataset validation passed")
        
        logger.info(f"Total entities: {len(entities)}")
        return entities
    
    def _generate_ports(self) -> List[Dict[str, Any]]:
        ports_list = []
        for port in self.ports:
            port_id = f"urn:ngsi-ld:Port:galicia-{port.key}"
            entity = {
                "id": port_id,
                "type": "Port",
                "name": {"type": "Property", "value": port.name},
                "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": port.coordinates}},
                "description": {"type": "Property", "value": f"Port of {port.municipality}, Galicia"},
            }
            ports_list.append(entity)
        return ports_list
