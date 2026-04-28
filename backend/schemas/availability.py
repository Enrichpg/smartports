# Availability Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class BoatPlacesAvailableResponse(BaseModel):
    """BoatPlacesAvailable entity (available berths count by category)"""
    id: str = Field(..., description="Entity ID")
    port_id: str = Field(..., description="Port ID")
    port_name: Optional[str] = Field(None, description="Port name")
    category: str = Field(..., description="Berth category (e.g., general, container)")
    availability_count: int = Field(..., ge=0, description="Number of available berths")
    total_berths_in_category: int = Field(..., ge=0, description="Total berths in category")
    average_depth: Optional[float] = Field(None, description="Average depth of available berths")
    prices: Optional[Dict[str, float]] = Field(None, description="Pricing by duration")
    last_updated: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:BoatPlacesAvailable:CorA:general",
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "port_name": "Puerto de A Coruña",
                "category": "general_cargo",
                "availability_count": 2,
                "total_berths_in_category": 3,
                "average_depth": 12.3,
                "prices": {
                    "hourly": 150.0,
                    "daily": 1200.0
                },
                "last_updated": "2026-04-28T12:00:00"
            }
        }


class AvailabilitySummaryResponse(BaseModel):
    """Availability summary for a port or facility"""
    port_id: str = Field(..., description="Port ID")
    port_name: Optional[str] = Field(None, description="Port name")
    total_available_berths: int = Field(..., ge=0, description="Total free berths")
    total_berths: int = Field(..., ge=0, description="Total berths")
    availability_rate: float = Field(..., ge=0, le=100, description="Availability percentage")
    by_category: List[BoatPlacesAvailableResponse] = Field(
        ..., description="Availability by berth category"
    )
    last_recalculated: datetime = Field(..., description="Last recalculation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "port_name": "Puerto de A Coruña",
                "total_available_berths": 3,
                "total_berths": 8,
                "availability_rate": 37.5,
                "by_category": [
                    {
                        "id": "urn:smartdatamodels:BoatPlacesAvailable:CorA:general",
                        "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                        "category": "general_cargo",
                        "availability_count": 2,
                        "total_berths_in_category": 3
                    }
                ],
                "last_recalculated": "2026-04-28T12:00:00"
            }
        }


class RecalculateAvailabilityRequest(BaseModel):
    """Request to recalculate availability for a port"""
    port_id: str = Field(..., description="Port ID")
    force: bool = Field(default=False, description="Force recalculation even if recent")
