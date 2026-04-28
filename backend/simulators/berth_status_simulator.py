# Berth Status Simulator
# Generate realistic berth occupancy and status data

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List


class BerthStatusSimulator:
    """
    Simulate berth status and occupancy with coherence rules.
    
    - Different berths have different average occupancy
    - Occupancy varies by time of day
    - Transitions between states are realistic
    """
    
    def __init__(self, port_code: str, num_berths: int = 5):
        self.port_code = port_code
        self.num_berths = num_berths
        self.berth_states = {}  # Track current state of each berth
        self._initialize_berths()
    
    def _initialize_berths(self):
        """Initialize berth states"""
        for i in range(self.num_berths):
            self.berth_states[f"berth_{i+1}"] = {
                "status": random.choice(["free", "occupied", "maintenance"]),
                "occupied_since": datetime.utcnow() - timedelta(hours=random.randint(0, 48)),
                "occupant": None,
            }
    
    def get_berth_status(self, berth_id: str) -> Dict[str, Any]:
        """
        Get current status of a specific berth.
        Maintains state continuity while allowing for state transitions.
        """
        if berth_id not in self.berth_states:
            berth_id = f"berth_{random.randint(1, self.num_berths)}"
        
        state = self.berth_states[berth_id]
        
        # Small chance of state transition
        if random.random() < 0.1:  # 10% chance per query
            self._transition_berth_state(berth_id)
        
        status = state["status"]
        occupied = status == "occupied"
        
        return {
            "berth_id": berth_id,
            "port_code": self.port_code,
            "status": status,
            "occupied": occupied,
            "occupied_since": state["occupied_since"].isoformat() if occupied else None,
            "occupant_vessel_id": state["occupant"],
            "data_source": "simulator",
            "confidence": 0.3,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def _transition_berth_state(self, berth_id: str):
        """Update berth state with realistic transitions"""
        state = self.berth_states[berth_id]
        current_status = state["status"]
        
        if current_status == "free":
            # Free berth might get occupied
            if random.random() < 0.4:
                state["status"] = "occupied"
                state["occupied_since"] = datetime.utcnow()
                state["occupant"] = f"vessel_{random.randint(1000, 9999)}"
        
        elif current_status == "occupied":
            # Occupied berth might become free
            elapsed = datetime.utcnow() - state["occupied_since"]
            if elapsed > timedelta(hours=12) and random.random() < 0.3:
                state["status"] = "free"
                state["occupied_since"] = None
                state["occupant"] = None
        
        elif current_status == "maintenance":
            # Maintenance might end
            if random.random() < 0.05:
                state["status"] = "free"
    
    def get_all_berth_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all berths at this port"""
        return [self.get_berth_status(berth_id) for berth_id in self.berth_states.keys()]
    
    def get_port_occupancy_rate(self) -> float:
        """Calculate current occupancy rate for the port"""
        occupied = sum(
            1 for state in self.berth_states.values() 
            if state["status"] == "occupied"
        )
        return occupied / self.num_berths if self.num_berths > 0 else 0
