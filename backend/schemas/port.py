# Port Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .common import NGSILDEntityResponse, GeoProperty


class PortResponse(BaseModel):
    """Port entity response (NGSI-LD)"""
    id: str = Field(..., description="Port URN ID")
    name: str = Field(..., description="Port name")
    country: str = Field(..., description="Country code (ES for Spain)")
    location: Optional[GeoProperty] = Field(None, description="Port geographic location")
    url: Optional[str] = Field(None, description="Port official website")
    dbpedia: Optional[str] = Field(None, description="DBpedia reference")
    imo: Optional[str] = Field(None, description="IMO port number")
    description: Optional[str] = Field(None, description="Port description")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:Port:Galicia:CorA",
                "name": "Puerto de A Coruña",
                "country": "ES",
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [-8.384, 43.371]
                    }
                },
                "imo": "ESCOR"
            }
        }


class PortSummaryResponse(BaseModel):
    """Port operational summary with KPIs"""
    id: str = Field(..., description="Port ID")
    name: str = Field(..., description="Port name")
    total_berths: int = Field(..., description="Total berths in port")
    berths_free: int = Field(..., description="Free berths")
    berths_occupied: int = Field(..., description="Occupied berths")
    berths_reserved: int = Field(..., description="Reserved berths")
    berths_out_of_service: int = Field(..., description="Out of service berths")
    occupancy_rate: float = Field(..., ge=0, le=100, description="Occupancy percentage")
    active_vessels: int = Field(..., description="Active vessel visits (PortCalls)")
    active_alerts: int = Field(..., description="Active alerts count")
    last_updated: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:Port:Galicia:CorA",
                "name": "Puerto de A Coruña",
                "total_berths": 5,
                "berths_free": 2,
                "berths_occupied": 2,
                "berths_reserved": 1,
                "berths_out_of_service": 0,
                "occupancy_rate": 40.0,
                "active_vessels": 2,
                "active_alerts": 1,
                "last_updated": "2026-04-28T12:00:00"
            }
        }


class PortListResponse(BaseModel):
    """Port list with pagination"""
    total: int = Field(..., description="Total ports")
    limit: int = Field(..., description="Limit")
    offset: int = Field(..., description="Offset")
    ports: List[PortResponse] = Field(..., description="Port list")
