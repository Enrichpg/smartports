
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class PortProfile:
    key: str
    name: str
    coordinates: Tuple[float, float]
    municipality: str
    port_type: str
    authority_name: str
    berth_count_est: int
    vessel_count_est: int

def load_port_profiles() -> List[PortProfile]:
    return [
        PortProfile("a-coruna", "Puerto de A Coruña", [-8.3936, 43.3613], "A Coruña", "commercial", "Autoridad Portuaria de A Coruña", 50, 700),
        PortProfile("vigo", "Puerto de Vigo", [-8.7670, 42.2362], "Vigo", "commercial_fishing", "Autoridad Portuaria de Vigo", 60, 800),
        PortProfile("ferrol", "Puerto de Ferrol", [-8.2444, 43.4667], "Ferrol", "naval_commercial", "Autoridad Portuaria de Ferrol-San Cibrao", 45, 550),
        PortProfile("marin", "Puerto de Marín", [-8.7033, 42.3967], "Marín", "mixed", "Autoridad Portuaria de Marín", 25, 300),
        PortProfile("vilagarcia", "Puerto de Vilagarcía de Arousa", [-8.7681, 42.6153], "Vilagarcía de Arousa", "commercial_fishing", "Autoridad Portuaria de Vilagarcía", 35, 450),
        PortProfile("ribeira", "Puerto de Ribeira", [-9.2717, 42.5544], "Ribeira", "fishing", "Autoridad Portuaria de Ribeira", 30, 550),
        PortProfile("burela", "Puerto de Burela", [-7.5817, 43.3283], "Burela", "fishing", "Autoridad Portuaria de Burela", 20, 400),
        PortProfile("baiona", "Puerto de Baiona", [-8.8350, 42.1205], "Baiona", "recreational", "Autoridad Portuaria de Baiona", 15, 250),
    ]
