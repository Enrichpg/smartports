# Vessel State Simulator
# Generate realistic vessel tracking and status data

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List


class VesselSimulator:
    """
    Simulate vessel positions, speeds, and status.
    
    Maintains coherence:
    - Vessels transit between ports over hours/days
    - Speed is realistic for maritime context
    - Status transitions are coherent
    """
    
    def __init__(self, port_code: str):
        self.port_code = port_code
        self.vessels = self._initialize_vessels()
        self.update_interval = timedelta(seconds=30)
        self.last_update = datetime.utcnow()
    
    def _initialize_vessels(self) -> Dict[str, Dict[str, Any]]:
        """Create initial fleet"""
        vessels = {}
        num_vessels = random.randint(3, 8)
        
        for i in range(num_vessels):
            mmsi = 200000000 + random.randint(1000000, 9999999)
            vessels[f"vessel_{i+1}"] = {
                "mmsi": mmsi,
                "status": random.choice(["moored", "at_anchor", "transiting"]),
                "latitude": 42.5 + random.uniform(-0.5, 0.5),
                "longitude": -8.5 + random.uniform(-0.5, 0.5),
                "speed": random.uniform(0, 15),  # knots
                "course": random.uniform(0, 360),  # degrees
                "current_berth": f"berth_{random.randint(1, 5)}" if random.random() < 0.3 else None,
                "ets": (datetime.utcnow() + timedelta(hours=random.randint(1, 72))).isoformat(),
            }
        
        return vessels
    
    def get_vessel_status(self, vessel_id: str) -> Dict[str, Any]:
        """Get current status and position of a vessel"""
        
        if vessel_id not in self.vessels:
            vessel_id = random.choice(list(self.vessels.keys()))
        
        vessel = self.vessels[vessel_id]
        self._update_vessel_state(vessel_id)
        
        return {
            "vessel_id": vessel_id,
            "mmsi": vessel["mmsi"],
            "port_code": self.port_code,
            "status": vessel["status"],
            "latitude": vessel["latitude"],
            "longitude": vessel["longitude"],
            "speed": vessel["speed"],
            "course": vessel["course"],
            "current_berth": vessel["current_berth"],
            "ets": vessel["ets"],  # Estimated time of arrival/departure
            "data_source": "simulator",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def _update_vessel_state(self, vessel_id: str):
        """Update vessel position and state based on elapsed time"""
        vessel = self.vessels[vessel_id]
        now = datetime.utcnow()
        
        # Small chance of state change
        if random.random() < 0.15:  # 15% chance
            self._transition_vessel_state(vessel)
        
        # Update position if transiting
        if vessel["status"] == "transiting":
            # Simulate movement (very simplified)
            elapsed_minutes = (now - self.last_update).total_seconds() / 60
            movement_scale = (vessel["speed"] / 60) / 100  # Rough scale
            vessel["latitude"] += random.uniform(-movement_scale, movement_scale)
            vessel["longitude"] += random.uniform(-movement_scale, movement_scale)
    
    def _transition_vessel_state(self, vessel: Dict[str, Any]):
        """Update vessel state with realistic transitions"""
        current_status = vessel["status"]
        
        if current_status == "transiting":
            # Transiting vessel might arrive and moor
            if random.random() < 0.3:
                vessel["status"] = "moored"
                vessel["speed"] = 0
                vessel["current_berth"] = f"berth_{random.randint(1, 5)}"
        
        elif current_status == "moored":
            # Moored vessel might depart
            if random.random() < 0.2:
                vessel["status"] = "transiting"
                vessel["speed"] = random.uniform(5, 15)
                vessel["current_berth"] = None
                vessel["ets"] = (datetime.utcnow() + timedelta(hours=random.randint(6, 48))).isoformat()
        
        elif current_status == "at_anchor":
            # At anchor might transition to moored or transiting
            if random.random() < 0.25:
                vessel["status"] = random.choice(["moored", "transiting"])
                if vessel["status"] == "transiting":
                    vessel["speed"] = random.uniform(5, 15)
    
    def get_all_vessels(self) -> List[Dict[str, Any]]:
        """Get status of all vessels in the simulation"""
        return [self.get_vessel_status(v_id) for v_id in self.vessels.keys()]
    
    def get_vessel_count_by_status(self) -> Dict[str, int]:
        """Count vessels by status"""
        counts = {}
        for vessel in self.vessels.values():
            status = vessel["status"]
            counts[status] = counts.get(status, 0) + 1
        return counts
