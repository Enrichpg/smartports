# PortCall Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PortCallStatus(str, Enum):
    """PortCall lifecycle states"""
    SCHEDULED = "scheduled"
    EXPECTED = "expected"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PortCallCreateRequest(BaseModel):
    """Request to create a new PortCall"""
    vessel_id: str = Field(..., description="Vessel ID")
    port_id: str = Field(..., description="Port ID")
    berth_id: Optional[str] = Field(None, description="Assigned berth ID (optional at creation)")
    estimated_arrival: datetime = Field(..., description="Estimated arrival time")
    estimated_departure: Optional[datetime] = Field(None, description="Estimated departure time")
    purpose: Optional[str] = Field(None, description="Purpose of visit (e.g., load, unload, repair)")
    cargo_type: Optional[str] = Field(None, description="Cargo type if relevant")
    status: PortCallStatus = Field(default=PortCallStatus.SCHEDULED, description="Initial status")

    class Config:
        json_schema_extra = {
            "example": {
                "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "estimated_arrival": "2026-04-30T08:00:00",
                "estimated_departure": "2026-05-02T18:00:00",
                "purpose": "load",
                "cargo_type": "containers",
                "status": "scheduled"
            }
        }


class PortCallResponse(BaseModel):
    """PortCall entity response"""
    id: str = Field(..., description="PortCall URN ID")
    vessel_id: str = Field(..., description="Vessel ID")
    vessel_name: Optional[str] = Field(None, description="Vessel name")
    port_id: str = Field(..., description="Port ID")
    port_name: Optional[str] = Field(None, description="Port name")
    berth_id: Optional[str] = Field(None, description="Assigned berth ID")
    berth_name: Optional[str] = Field(None, description="Berth name")
    status: PortCallStatus = Field(..., description="Current status")
    estimated_arrival: datetime = Field(..., description="Estimated arrival")
    estimated_departure: Optional[datetime] = Field(None, description="Estimated departure")
    actual_arrival: Optional[datetime] = Field(None, description="Actual arrival timestamp")
    actual_departure: Optional[datetime] = Field(None, description="Actual departure timestamp")
    purpose: Optional[str] = Field(None, description="Visit purpose")
    cargo_type: Optional[str] = Field(None, description="Cargo type")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:PortCall:Galicia:corA_20260430_imo9876543",
                "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "vessel_name": "MSC Example",
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "port_name": "Puerto de A Coruña",
                "berth_id": "urn:smartdatamodels:Berth:CorA:berth_A1",
                "berth_name": "A1",
                "status": "active",
                "estimated_arrival": "2026-04-30T08:00:00",
                "estimated_departure": "2026-05-02T18:00:00",
                "actual_arrival": "2026-04-30T08:15:00",
                "actual_departure": None,
                "purpose": "load",
                "cargo_type": "containers",
                "created_at": "2026-04-28T10:00:00",
                "updated_at": "2026-04-30T08:15:00"
            }
        }


class PortCallStatusChangeRequest(BaseModel):
    """Request to change PortCall status"""
    new_status: PortCallStatus = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Reason for change")
    operator_id: str = Field(..., description="Operator ID")

    class Config:
        json_schema_extra = {
            "example": {
                "new_status": "active",
                "reason": "Vessel arrived on schedule",
                "operator_id": "urn:smartdatamodels:PortAuthority:CorA:operator_001"
            }
        }


class PortCallCloseRequest(BaseModel):
    """Request to close a PortCall"""
    actual_departure: datetime = Field(..., description="Actual departure time")
    notes: Optional[str] = Field(None, description="Closing notes")
    operator_id: str = Field(..., description="Operator ID")

    class Config:
        json_schema_extra = {
            "example": {
                "actual_departure": "2026-05-02T18:30:00",
                "notes": "Completed successfully",
                "operator_id": "urn:smartdatamodels:PortAuthority:CorA:operator_001"
            }
        }


class PortCallListResponse(BaseModel):
    """PortCall list with pagination"""
    total: int = Field(..., description="Total PortCalls")
    limit: int = Field(..., description="Limit")
    offset: int = Field(..., description="Offset")
    portcalls: List[PortCallResponse] = Field(..., description="PortCall list")
