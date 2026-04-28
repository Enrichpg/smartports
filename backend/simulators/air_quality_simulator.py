# Air Quality Simulator
# Generate realistic air quality observations when API data is unavailable

import random
from datetime import datetime
from typing import Dict, Any


class AirQualitySimulator:
    """
    Simulate air quality measurements.
    
    Generates realistic AQI (Air Quality Index) and pollutant levels
    with time-of-day patterns (worse during peak hours).
    """
    
    # Pollutants tracked
    POLLUTANTS = ["NO2", "O3", "PM2.5", "PM10", "SO2", "CO"]
    
    # AQI categories
    AQI_LEVELS = {
        0: {"range": (0, 50), "category": "Good", "color": "green"},
        1: {"range": (51, 100), "category": "Fair", "color": "yellow"},
        2: {"range": (101, 150), "category": "Moderate", "color": "orange"},
        3: {"range": (151, 200), "category": "Poor", "color": "red"},
        4: {"range": (201, 300), "category": "Very Poor", "color": "purple"},
        5: {"range": (301, 500), "category": "Hazardous", "color": "maroon"},
    }
    
    def __init__(self, port_code: str, location_name: str = ""):
        self.port_code = port_code
        self.location_name = location_name
        self.base_aqi = random.randint(30, 80)  # Base AQI for this location
    
    def get_air_quality(self) -> Dict[str, Any]:
        """
        Get current air quality observations.
        
        Returns:
            AirQualityObserved NGSI-LD compatible data
        """
        
        # Simulate time-of-day effect
        now = datetime.utcnow()
        hour = now.hour
        
        # Higher AQI during peak hours (6-20)
        time_factor = 1.5 if 6 <= hour <= 20 else 0.7
        aqi = int(self.base_aqi * time_factor + random.randint(-10, 10))
        aqi = max(0, min(500, aqi))  # Clamp to 0-500
        
        # Get AQI level
        aqi_level = self._get_aqi_level(aqi)
        
        # Generate pollutant concentrations
        pollutants = self._generate_pollutants(aqi)
        
        return {
            "port_code": self.port_code,
            "location_name": self.location_name,
            "timestamp": datetime.utcnow().isoformat(),
            "aqi": aqi,
            "aqi_level": aqi_level["category"],
            "aqi_color": aqi_level["color"],
            "pollutants": pollutants,
            "dominant_pollutant": max(pollutants, key=pollutants.get),
            "data_source": "simulator",
            "confidence": 0.2,  # Low confidence for simulated data
        }
    
    def _get_aqi_level(self, aqi: int) -> Dict[str, str]:
        """Get AQI category for a given AQI value"""
        for level in self.AQI_LEVELS.values():
            if level["range"][0] <= aqi <= level["range"][1]:
                return level
        return self.AQI_LEVELS[5]  # Default to hazardous
    
    def _generate_pollutants(self, aqi: int) -> Dict[str, float]:
        """Generate realistic pollutant concentrations based on AQI"""
        
        # Base concentrations (µg/m³ for particulates, ppb for gases)
        base_concentrations = {
            "NO2": 15,
            "O3": 30,
            "PM2.5": 10,
            "PM10": 20,
            "SO2": 5,
            "CO": 200,
        }
        
        # Scale by AQI / 100
        aqi_factor = aqi / 100.0
        
        pollutants = {}
        for pollutant, base in base_concentrations.items():
            # Add random variation
            noise = random.uniform(0.8, 1.2)
            concentration = base * aqi_factor * noise
            pollutants[pollutant] = round(concentration, 2)
        
        return pollutants
    
    def get_forecast(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """
        Generate air quality forecast for next N hours.
        
        Args:
            hours_ahead: Hours to forecast
            
        Returns:
            Forecast data with hourly predictions
        """
        
        forecast = []
        base_aqi = self.base_aqi
        
        for hour in range(hours_ahead):
            # Simulate AQI variation over time
            tomorrow_hour = (datetime.utcnow().hour + hour) % 24
            time_factor = 1.5 if 6 <= tomorrow_hour <= 20 else 0.7
            predicted_aqi = int(base_aqi * time_factor + random.randint(-15, 15))
            predicted_aqi = max(0, min(500, predicted_aqi))
            
            forecast.append({
                "hour_ahead": hour,
                "predicted_aqi": predicted_aqi,
                "predicted_level": self._get_aqi_level(predicted_aqi)["category"],
            })
        
        return {
            "port_code": self.port_code,
            "forecast_generated_at": datetime.utcnow().isoformat(),
            "forecast_hours": hours_ahead,
            "forecast": forecast,
        }
