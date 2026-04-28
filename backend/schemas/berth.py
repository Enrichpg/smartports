# Berth Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BerthStatus(str, Enum):
    """Berth operational states"""
    FREE = "free"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    OUT_OF_SERVICE = "outOfService"


class BerthResponse(BaseModel):
    """Berth entity response"""
    id: str = Field(..., description="Berth URN ID")
    name: str = Field(..., description="Berth name/identifier")
    port_id: str = Field(..., description="Parent port ID")
    facility_id: Optional[str] = Field(None, description="Parent facility ID")
    berth_type: str = Field(
        ..., description="Berth type (e.g., container, general, oil, passenger)"
    )
    status: BerthStatus = Field(..., description="Current berth status")
    depth: Optional[float] = Field(None, description="Water depth in meters")
    length: Optional[float] = Field(None, description="Berth length in meters")
    draft_limit: Optional[float] = Field(None, description="Max draft allowed in meters")
    category: Optional[str] = Field(None, description="Berth category/zone")
    active_portcall_id: Optional[str] = Field(None, description="Active PortCall if occupied")
    last_status_change: datetime = Field(..., description="Last status change timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:Berth:CorA:berth_A1",
                "name": "A1",
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "facility_id": "urn:smartdatamodels:SeaportFacilities:CorA:general_dock",
                "berth_type": "general_cargo",
                "status": "occupied",
                "depth": 12.5,
                "length": 200.0,
                "draft_limit": 11.0,
                "category": "general",
                "active_portcall_id": "urn:smartdatamodels:PortCall:Galicia:corA_20260428_imo9876543",
                "last_status_change": "2026-04-28T10:00:00"
            }
        }


class BerthDetailResponse(BaseModel):
    """Berth detail with additional context"""
    berth: BerthResponse
    port_name: str = Field(..., description="Port name for context")
    facility_name: Optional[str] = Field(None, description="Facility name")
    current_vessel: Optional[dict] = Field(None, description="Current vessel info if occupied")
    can_accommodate_size: Optional[dict] = Field(
        None, description="Max size vessel this berth can accommodate"
    )


class BerthListResponse(BaseModel):
    """Berth list with pagination"""
    total: int = Field(..., description="Total berths")
    limit: int = Field(..., description="Limit")
    offset: int = Field(..., description="Offset")
    berths: List[BerthResponse] = Field(..., description="Berth list")


class BerthStateChangeRequest(BaseModel):
    """Request to change berth status"""
    new_status: BerthStatus = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Reason for status change")
    operator_id: str = Field(..., description="Operator performing change")

    class Config:
        json_schema_extra = {
            "example": {
                "new_status": "outOfService",
                "reason": "Maintenance scheduled",
                "operator_id": "urn:smartdatamodels:PortAuthority:CorA:operator_001"
            }
        }
