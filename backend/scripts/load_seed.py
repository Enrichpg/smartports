"""
SmartPort Galicia - Seed Data Loader
Generates NGSI-LD entities and loads them into Orion-LD

Usage:
    python load_seed.py --dry-run              # Preview without loading
    python load_seed.py --upsert               # Load with upsert (safe)
    python load_seed.py --clean-first          # Delete existing first (careful!)
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Ensure /app (backend root) is in sys.path when running inside the container
# or the repo root's backend/ dir when running locally.
_APP_ROOT = Path(__file__).resolve().parent.parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from services.ngsi_builders import (
    PortBuilder, PortAuthorityBuilder, SeaportFacilitiesBuilder,
    BerthBuilder, VesselBuilder, MasterVesselBuilder, BoatAuthorizedBuilder,
    BoatPlacesAvailableBuilder, BoatPlacesPricingBuilder, DeviceBuilder,
    AirQualityObservedBuilder, WeatherObservedBuilder, AlertBuilder
)
from services.orion_service import OrionService
from data.catalogs.galicia_ports import (
    GALICIAN_PORTS, PRICING_CATEGORIES, MASTER_VESSELS, VESSEL_INSTANCES,
    AUTHORIZED_BOATS, SENSOR_DEVICES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SeedGenerator:
    """Generates NGSI-LD seed data for Galician ports"""
    
    def __init__(self, orion_service: OrionService):
        self.orion = orion_service
        self.entities: List[Dict[str, Any]] = []
        self.stats = {
            "Port": 0,
            "PortAuthority": 0,
            "SeaportFacilities": 0,
            "Berth": 0,
            "MasterVessel": 0,
            "Vessel": 0,
            "BoatAuthorized": 0,
            "BoatPlacesAvailable": 0,
            "BoatPlacesPricing": 0,
            "Device": 0,
            "AirQualityObserved": 0,
            "WeatherObserved": 0
        }
    
    def generate_ports(self):
        """Generate Port entities"""
        logger.info("Generating Port entities...")
        
        for port_key, port_data in GALICIAN_PORTS.items():
            port_id = f"urn:ngsi-ld:Port:galicia-{port_key}"
            authority_id = f"urn:ngsi-ld:PortAuthority:autoridad-{port_key}"
            facility_id = f"urn:ngsi-ld:SeaportFacilities:galicia-{port_key}-main"
            
            port_entity = PortBuilder.build(
                port_id=port_id,
                name=port_data["name"],
                coordinates=port_data["coordinates"],
                description=port_data["description"],
                port_type=port_data["port_type"],
                authority_id=authority_id,
                facility_id=facility_id
            )
            
            self.entities.append(port_entity)
            self.stats["Port"] += 1
            logger.info(f"Generated Port: {port_data['name']}")
    
    def generate_authorities(self):
        """Generate PortAuthority entities"""
        logger.info("Generating PortAuthority entities...")
        
        for port_key, port_data in GALICIAN_PORTS.items():
            auth_id = f"urn:ngsi-ld:PortAuthority:autoridad-{port_key}"
            
            authority_entity = PortAuthorityBuilder.build(
                auth_id=auth_id,
                name=port_data["authority_name"],
                contact_email=port_data["authority_contact"],
                contact_phone=port_data["authority_phone"],
                website=port_data["authority_website"]
            )
            
            self.entities.append(authority_entity)
            self.stats["PortAuthority"] += 1
            logger.info(f"Generated PortAuthority: {port_data['authority_name']}")
    
    def generate_facilities(self):
        """Generate SeaportFacilities entities"""
        logger.info("Generating SeaportFacilities entities...")
        
        for port_key, port_data in GALICIAN_PORTS.items():
            port_id = f"urn:ngsi-ld:Port:galicia-{port_key}"
            facility_id = f"urn:ngsi-ld:SeaportFacilities:galicia-{port_key}-main"
            
            facility_entity = SeaportFacilitiesBuilder.build(
                facility_id=facility_id,
                name=port_data["main_facility"],
                description=f"Main seaport facility for {port_data['name']}",
                capacity=port_data["facility_capacity"],
                port_id=port_id
            )
            
            self.entities.append(facility_entity)
            self.stats["SeaportFacilities"] += 1
            logger.info(f"Generated SeaportFacilities: {port_data['main_facility']}")
    
    def generate_berths(self):
        """Generate Berth entities for each port"""
        logger.info("Generating Berth entities...")
        
        berth_statuses = ["free", "occupied", "maintenance", "reserved"]
        
        for port_key, port_data in GALICIAN_PORTS.items():
            facility_id = f"urn:ngsi-ld:SeaportFacilities:galicia-{port_key}-main"
            
            # Generate berths for each port
            for berth_num in range(1, port_data["num_berths"] + 1):
                berth_id = f"urn:ngsi-ld:Berth:galicia-{port_key}-{berth_num:03d}"
                berth_name = f"{port_data['name']} - Berth {berth_num}"
                
                # Assign status: most free, some occupied or reserved
                status = berth_statuses[berth_num % len(berth_statuses)]
                
                berth_entity = BerthBuilder.build(
                    berth_id=berth_id,
                    name=berth_name,
                    status=status,
                    facility_id=facility_id,
                    dimensions={
                        "length": 150.0 + (berth_num * 5),
                        "width": 25.0,
                        "depth": 10.0
                    }
                )
                
                self.entities.append(berth_entity)
                self.stats["Berth"] += 1
        
        logger.info(f"Generated {self.stats['Berth']} Berth entities")
    
    def generate_master_vessels(self):
        """Generate MasterVessel entities (static registry)"""
        logger.info("Generating MasterVessel entities...")
        
        for vessel in MASTER_VESSELS:
            master_id = f"urn:ngsi-ld:MasterVessel:imo-{vessel['imo']}"
            
            master_entity = MasterVesselBuilder.build(
                master_id=master_id,
                imo=vessel["imo"],
                name=vessel["name"],
                ship_type=vessel["ship_type"],
                length=vessel["length"],
                beam=vessel["beam"],
                depth=vessel["depth"],
                gross_tonnage=vessel["gross_tonnage"],
                net_tonnage=vessel["net_tonnage"],
                year_built=vessel["year_built"],
                flag_state=vessel["flag_state"]
            )
            
            self.entities.append(master_entity)
            self.stats["MasterVessel"] += 1
        
        logger.info(f"Generated {self.stats['MasterVessel']} MasterVessel entities")
    
    def generate_vessels(self):
        """Generate Vessel entities (instances with dynamic position)"""
        logger.info("Generating Vessel entities...")
        
        now = datetime.utcnow().isoformat() + "Z"
        
        for vessel in VESSEL_INSTANCES:
            vessel_id = f"urn:ngsi-ld:Vessel:mmsi-{vessel['mmsi']}"
            port_key = vessel["current_port"]
            port_data = GALICIAN_PORTS[port_key]
            
            vessel_entity = VesselBuilder.build(
                vessel_id=vessel_id,
                name=vessel["name"],
                mmsi=vessel["mmsi"],
                imo=vessel["imo"],
                vessel_type=vessel["vessel_type"],
                length=next(v["length"] for v in MASTER_VESSELS if v["imo"] == vessel["imo"]),
                beam=next(v["beam"] for v in MASTER_VESSELS if v["imo"] == vessel["imo"]),
                draught=next(v["depth"] for v in MASTER_VESSELS if v["imo"] == vessel["imo"]),
                position=port_data["coordinates"],
                position_timestamp=now
            )
            
            self.entities.append(vessel_entity)
            self.stats["Vessel"] += 1
        
        logger.info(f"Generated {self.stats['Vessel']} Vessel entities")
    
    def generate_authorized_boats(self):
        """Generate BoatAuthorized entities"""
        logger.info("Generating BoatAuthorized entities...")
        
        now = datetime.utcnow().isoformat() + "Z"
        valid_until = "2027-12-31T23:59:59Z"
        
        for auth_boat in AUTHORIZED_BOATS:
            auth_id = f"urn:ngsi-ld:BoatAuthorized:es-{auth_boat['es_code']}"
            vessel_id = f"urn:ngsi-ld:Vessel:mmsi-{auth_boat['mmsi']}"
            
            boat_auth_entity = BoatAuthorizedBuilder.build(
                auth_id=auth_id,
                vessel_id=vessel_id,
                authorized_port=auth_boat["authorized_port"],
                valid_from=now,
                valid_until=valid_until,
                authorization_type=auth_boat["authorization_type"]
            )
            
            self.entities.append(boat_auth_entity)
            self.stats["BoatAuthorized"] += 1
        
        logger.info(f"Generated {self.stats['BoatAuthorized']} BoatAuthorized entities")
    
    def generate_boat_availability(self):
        """Generate BoatPlacesAvailable entities"""
        logger.info("Generating BoatPlacesAvailable entities...")
        
        for port_key, port_data in GALICIAN_PORTS.items():
            facility_id = f"urn:ngsi-ld:SeaportFacilities:galicia-{port_key}-main"
            
            for category in PRICING_CATEGORIES.keys():
                avail_id = f"urn:ngsi-ld:BoatPlacesAvailable:galicia-{port_key}-{category}"
                
                # Calculate available places based on facility capacity and category
                total = max(10, port_data["facility_capacity"] // 4)
                available = total - (total // 3)  # 2/3 available, 1/3 occupied
                
                avail_entity = BoatPlacesAvailableBuilder.build(
                    availability_id=avail_id,
                    facility_id=facility_id,
                    category=category,
                    total_places=total,
                    available_places=available
                )
                
                self.entities.append(avail_entity)
                self.stats["BoatPlacesAvailable"] += 1
        
        logger.info(f"Generated {self.stats['BoatPlacesAvailable']} BoatPlacesAvailable entities")
    
    def generate_pricing(self):
        """Generate BoatPlacesPricing entities"""
        logger.info("Generating BoatPlacesPricing entities...")
        
        for port_key, port_data in GALICIAN_PORTS.items():
            facility_id = f"urn:ngsi-ld:SeaportFacilities:galicia-{port_key}-main"
            
            for category, price_data in PRICING_CATEGORIES.items():
                pricing_id = f"urn:ngsi-ld:BoatPlacesPricing:galicia-{port_key}-cat-{category}"
                
                pricing_entity = BoatPlacesPricingBuilder.build(
                    pricing_id=pricing_id,
                    facility_id=facility_id,
                    category=category,
                    price_per_day=price_data["price_per_day"],
                    currency="EUR",
                    iso8266_length_min=price_data["iso8266_length_min"],
                    iso8266_length_max=price_data["iso8266_length_max"]
                )
                
                self.entities.append(pricing_entity)
                self.stats["BoatPlacesPricing"] += 1
        
        logger.info(f"Generated {self.stats['BoatPlacesPricing']} BoatPlacesPricing entities")
    
    def generate_devices(self):
        """Generate Device entities (sensors)"""
        logger.info("Generating Device entities...")
        
        device_counter = {}
        
        for port_key, devices in SENSOR_DEVICES.items():
            device_counter[port_key] = 1
            
            for device in devices:
                device_id = f"urn:ngsi-ld:Device:galicia-{port_key}-{device['device_type'][:3].lower()}-{device_counter[port_key]:02d}"
                port_id = f"urn:ngsi-ld:Port:galicia-{port_key}"
                
                device_entity = DeviceBuilder.build(
                    device_id=device_id,
                    name=device["name"],
                    device_type=device["device_type"],
                    location=device["coordinates"],
                    port_ref=port_id
                )
                
                self.entities.append(device_entity)
                self.stats["Device"] += 1
                device_counter[port_key] += 1
        
        logger.info(f"Generated {self.stats['Device']} Device entities")
    
    def generate_observations(self):
        """Generate AirQualityObserved and WeatherObserved entities"""
        logger.info("Generating observation entities...")
        
        now = datetime.utcnow().isoformat() + "Z"
        
        for port_key, devices in SENSOR_DEVICES.items():
            port_data = GALICIAN_PORTS[port_key]
            coords = port_data["coordinates"]
            
            for idx, device in enumerate(devices):
                device_id = f"urn:ngsi-ld:Device:galicia-{port_key}-{device['device_type'][:3].lower()}-{idx+1:02d}"
                
                if "AirQuality" in device["device_type"]:
                    obs_id = f"urn:ngsi-ld:AirQualityObserved:galicia-{port_key}-air-{idx+1}"
                    
                    air_obs = AirQualityObservedBuilder.build(
                        obs_id=obs_id,
                        device_id=device_id,
                        location=coords,
                        observed_at=now,
                        pm25=15.5 + (idx * 2),
                        pm10=25.0 + (idx * 3),
                        no2=35.0 + (idx * 1),
                        co=0.5 + (idx * 0.1)
                    )
                    
                    self.entities.append(air_obs)
                    self.stats["AirQualityObserved"] += 1
                
                if "Weather" in device["device_type"]:
                    obs_id = f"urn:ngsi-ld:WeatherObserved:galicia-{port_key}-weather-{idx+1}"
                    
                    weather_obs = WeatherObservedBuilder.build(
                        obs_id=obs_id,
                        device_id=device_id,
                        location=coords,
                        observed_at=now,
                        temperature=18.5 + (idx * 0.5),
                        relative_humidity=65.0 + (idx * 2),
                        wind_speed=12.0 + (idx * 1.5),
                        wind_direction=180.0 + (idx * 10),
                        atmospheric_pressure=1013.25
                    )
                    
                    self.entities.append(weather_obs)
                    self.stats["WeatherObserved"] += 1
        
        logger.info(f"Generated {self.stats['AirQualityObserved']} AirQualityObserved and {self.stats['WeatherObserved']} WeatherObserved entities")
    
    def generate_all(self):
        """Generate all seed entities"""
        logger.info("=" * 80)
        logger.info("Starting NGSI-LD Seed Data Generation for Galician Ports")
        logger.info("=" * 80)
        
        self.generate_ports()
        self.generate_authorities()
        self.generate_facilities()
        self.generate_berths()
        self.generate_master_vessels()
        self.generate_vessels()
        self.generate_authorized_boats()
        self.generate_boat_availability()
        self.generate_pricing()
        self.generate_devices()
        self.generate_observations()
        
        logger.info("=" * 80)
        logger.info("Seed Generation Complete")
        logger.info("=" * 80)
        for entity_type, count in self.stats.items():
            logger.info(f"  {entity_type:25} {count:4} entities")
        logger.info(f"  {'TOTAL':25} {sum(self.stats.values()):4} entities")
        logger.info("=" * 80)
        
        return self.entities
    
    async def load_to_orion(self, dry_run: bool = False, upsert: bool = False):
        """Load generated entities to Orion-LD"""
        logger.info("=" * 80)
        logger.info(f"Loading entities to Orion-LD (dry_run={dry_run}, upsert={upsert})")
        logger.info("=" * 80)
        
        if not self.entities:
            logger.warning("No entities generated. Run generate_all() first.")
            return
        
        if dry_run:
            logger.info("[DRY-RUN] Would load the following entities:")
            for entity in self.entities[:5]:
                logger.info(f"  - {entity.get('id')} (type: {entity.get('type')})")
            if len(self.entities) > 5:
                logger.info(f"  ... and {len(self.entities) - 5} more")
            return
        
        result = await self.orion.batch_upsert_entities(
            self.entities,
            dry_run=False
        )
        
        logger.info("=" * 80)
        logger.info(f"Orion-LD Load Result:")
        logger.info(f"  Total:      {result['total']}")
        logger.info(f"  Successful: {result['successful']}")
        logger.info(f"  Failed:     {result['failed']}")
        logger.info("=" * 80)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Load NGSI-LD seed data for SmartPort Galicia to Orion-LD"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview entities without loading"
    )
    parser.add_argument(
        "--upsert",
        action="store_true",
        default=True,
        help="Use upsert mode (safe, default)"
    )
    parser.add_argument(
        "--orion-url",
        default="http://localhost:1026",
        help="Orion-LD base URL"
    )
    parser.add_argument(
        "--service",
        default="smartport",
        help="FIWARE Service name"
    )
    parser.add_argument(
        "--service-path",
        default="/galicia",
        help="FIWARE ServicePath"
    )
    
    args = parser.parse_args()
    
    # Initialize Orion service
    orion = OrionService(
        base_url=args.orion_url,
        fiware_service=args.service,
        fiware_service_path=args.service_path
    )
    
    # Generate and load seed
    generator = SeedGenerator(orion)
    generator.generate_all()
    
    await generator.load_to_orion(
        dry_run=args.dry_run,
        upsert=args.upsert
    )


if __name__ == "__main__":
    asyncio.run(main())
