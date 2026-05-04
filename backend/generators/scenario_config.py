import random
from typing import Dict, Any, Optional


class ScenarioConfig:
    """Configuration for synthetic data generation scenarios."""
    
    SCENARIOS = {
        "small": {"num_vessels": 300, "num_berths": 50, "num_sensors": 40, "historical_days": 30},
        "medium": {"num_vessels": 1500, "num_berths": 150, "num_sensors": 80, "historical_days": 60},
        "large": {"num_vessels": 2500, "num_berths": 180, "num_sensors": 100, "historical_days": 90},
        "xlarge": {"num_vessels": 4500, "num_berths": 320, "num_sensors": 180, "historical_days": 90},
    }
    
    VESSEL_ARCHETYPES = {
        "fishing": {"ratio": 0.35},
        "merchant": {"ratio": 0.25},
        "auxiliary": {"ratio": 0.20},
        "oceanic": {"ratio": 0.15},
        "recreational": {"ratio": 0.05},
    }
    
    def __init__(self, volume: str = "xlarge", historical_days: Optional[int] = None, seed: int = 42):
        if volume not in self.SCENARIOS:
            raise ValueError(f"Invalid volume '{volume}'")
        self.volume = volume
        self.seed = seed
        scenario = self.SCENARIOS[volume]
        self.num_vessels = scenario["num_vessels"]
        self.num_berths = scenario["num_berths"]
        self.num_sensors = scenario["num_sensors"]
        self.historical_days = historical_days or scenario["historical_days"]
        self.vessel_archetypes = self.VESSEL_ARCHETYPES.copy()
        self.time_acceleration = 24
        self.tick_interval_minutes = 5
        self.days_per_tick = 2
        random.seed(self.seed)
    
    def get_vessel_count_by_archetype(self) -> Dict[str, int]:
        """Get number of vessels per archetype based on ratios."""
        counts = {}
        remaining = self.num_vessels
        
        archetypes_sorted = sorted(self.vessel_archetypes.items(), key=lambda x: x[1]["ratio"], reverse=True)
        
        for i, (archetype, config) in enumerate(archetypes_sorted):
            if i == len(archetypes_sorted) - 1:
                counts[archetype] = remaining
            else:
                count = int(self.num_vessels * config["ratio"])
                counts[archetype] = count
                remaining -= count
        
        return counts
    
    def __repr__(self) -> str:
        return f"ScenarioConfig(volume={self.volume}, vessels={self.num_vessels}, berths={self.num_berths}, sensors={self.num_sensors})"
