# Vessel Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VesselResponse(BaseModel):
    """Vessel entity response"""
    id: str = Field(..., description="Vessel URN ID (MasterVessel reference)")
    imo_number: str = Field(..., description="IMO number (unique identifier)")
    mmsi: Optional[str] = Field(None, description="MMSI (Maritime Mobile Service Identity)")
    name: str = Field(..., description="Vessel name")
    vessel_type: str = Field(..., description="Vessel type (e.g., container, tanker, general)")
    length: Optional[float] = Field(None, description="Vessel length in meters")
    width: Optional[float] = Field(None, description="Vessel beam/width in meters")
    draft: Optional[float] = Field(None, description="Vessel draft in meters")
    gross_tonnage: Optional[float] = Field(None, description="Gross tonnage")
    deadweight_tonnage: Optional[float] = Field(None, description="Deadweight tonnage")
    nationality: Optional[str] = Field(None, description="Country of origin")
    operator: Optional[str] = Field(None, description="Vessel operator/owner")
    status: Optional[str] = Field(None, description="Current status")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "imo_number": "9876543",
                "mmsi": "224999999",
                "name": "MSC Example",
                "vessel_type": "container_ship",
                "length": 398.0,
                "width": 54.0,
                "draft": 15.5,
                "gross_tonnage": 98000,
                "deadweight_tonnage": 121000,
                "nationality": "IT",
                "operator": "Mediterranean Shipping Company",
                "status": "active"
            }
        }


class VesselListResponse(BaseModel):
    """Vessel list with pagination"""
    total: int = Field(..., description="Total vessels")
    limit: int = Field(..., description="Limit")
    offset: int = Field(..., description="Offset")
    vessels: List[VesselResponse] = Field(..., description="Vessel list")
