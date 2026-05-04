
from typing import List, Dict, Any

class DataValidator:
    def __init__(self):
        self.errors = []
    
    def validate_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.errors = []
        self._check_duplicate_ids(entities)
        self._check_references(entities)
        self._check_coordinates(entities)
        return {"valid": len(self.errors) == 0, "errors": self.errors}
    
    def _check_duplicate_ids(self, entities):
        ids = [e.get("id") for e in entities]
        seen = set()
        for entity_id in ids:
            if entity_id in seen:
                self.errors.append(f"Duplicate ID: {entity_id}")
            else:
                seen.add(entity_id)
    
    def _check_references(self, entities):
        entity_ids = {e.get("id") for e in entities}
        for entity in entities:
            for key, value in entity.items():
                if isinstance(value, dict) and value.get("type") == "Relationship":
                    ref_id = value.get("object")
                    if ref_id and ref_id not in entity_ids:
                        self.errors.append(f"Invalid reference: {ref_id}")
    
    def _check_coordinates(self, entities):
        galicia_bounds = {"lon_min": -10, "lon_max": -7, "lat_min": 42, "lat_max": 44}
        for entity in entities:
            location = entity.get("location")
            if location and location.get("type") == "GeoProperty":
                coords = location.get("value", {}).get("coordinates", [])
                if len(coords) >= 2:
                    lon, lat = coords[0], coords[1]
                    if not (galicia_bounds["lon_min"] < lon < galicia_bounds["lon_max"]):
                        self.errors.append(f"Invalid longitude: {lon}")
                    if not (galicia_bounds["lat_min"] < lat < galicia_bounds["lat_max"]):
                        self.errors.append(f"Invalid latitude: {lat}")
