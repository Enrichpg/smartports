# Boat Places Availability Simulator
# Generate realistic availability data for different mooring types

import random
from datetime import datetime
from typing import Dict, Any


class AvailabilitySimulator:
    """
    Simulate boat places availability with realistic patterns.
    
    Different port types have different occupancy patterns:
    - Commercial berths: higher occupancy, more stable
    - Moorings: medium occupancy
    - Anchorage: more variable
    """
    
    def __init__(self, port_code: str):
        self.port_code = port_code
        self.places = {
            "berth": {"total": 15, "occupied": random.randint(8, 13)},
            "mooring": {"total": 30, "occupied": random.randint(10, 25)},
            "anchorage": {"total": 50, "occupied": random.randint(15, 45)},
        }
    
    def get_available_places(self, place_type: str) -> Dict[str, Any]:
        """
        Get current availability for a specific place type.
        
        Args:
            place_type: "berth", "mooring", or "anchorage"
            
        Returns:
            Availability data with occupancy rate
        """
        if place_type not in self.places:
            place_type = list(self.places.keys())[0]
        
        info = self.places[place_type]
        
        # Small fluctuation
        if random.random() < 0.2:  # 20% chance per query
            change = random.randint(-2, 2)
            info["occupied"] = max(0, min(info["total"], info["occupied"] + change))
        
        available = info["total"] - info["occupied"]
        occupancy_rate = info["occupied"] / info["total"]
        
        return {
            "port_code": self.port_code,
            "place_type": place_type,
            "available_places": available,
            "total_places": info["total"],
            "occupied_places": info["occupied"],
            "occupancy_rate": occupancy_rate,
            "data_source": "simulator",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_all_availability(self) -> Dict[str, Dict[str, Any]]:
        """Get availability for all place types at this port"""
        return {
            place_type: self.get_available_places(place_type)
            for place_type in self.places.keys()
        }
    
    def get_port_occupancy(self) -> float:
        """Calculate overall port occupancy rate"""
        total_occupied = sum(info["occupied"] for info in self.places.values())
        total_places = sum(info["total"] for info in self.places.values())
        return total_occupied / total_places if total_places > 0 else 0
