# Alert Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types"""
    AUTHORIZATION_FAILED = "authorization_failed"
    AUTHORIZATION_EXPIRED = "authorization_expired"
    BERTH_CONFLICT = "berth_conflict"
    OCCUPANCY_HIGH = "occupancy_high"
    OCCUPANCY_FULL = "occupancy_full"
    BERTH_OUT_OF_SERVICE = "berth_out_of_service"
    VESSEL_NOT_FOUND = "vessel_not_found"
    INSURANCE_EXPIRED = "insurance_expired"
    INVALID_VESSEL_SIZE = "invalid_vessel_size"
    OPERATIONAL = "operational"


class AlertResponse(BaseModel):
    """Alert entity response"""
    id: str = Field(..., description="Alert URN ID")
    port_id: str = Field(..., description="Port ID")
    port_name: Optional[str] = Field(None, description="Port name")
    entity_id: Optional[str] = Field(None, description="Related entity ID (Berth, Vessel, PortCall)")
    entity_type: Optional[str] = Field(None, description="Related entity type")
    alert_type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Severity level")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    is_active: bool = Field(default=True, description="Whether alert is still active")
    created_at: datetime = Field(..., description="Creation timestamp")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgement timestamp")
    acknowledged_by: Optional[str] = Field(None, description="Operator who acknowledged")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:Alert:CorA:alert_001",
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "port_name": "Puerto de A Coruña",
                "entity_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "entity_type": "Vessel",
                "alert_type": "authorization_expired",
                "severity": "critical",
                "title": "Vessel Authorization Expired",
                "description": "Vessel MSC Example (IMO 9876543) authorization expired on 2026-04-15",
                "is_active": True,
                "created_at": "2026-04-28T10:00:00",
                "acknowledged_at": "2026-04-28T10:05:00",
                "acknowledged_by": "operator_001",
                "resolved_at": None
            }
        }


class AlertListResponse(BaseModel):
    """Alert list with pagination"""
    total: int = Field(..., description="Total alerts")
    active: int = Field(..., description="Active alerts count")
    limit: int = Field(..., description="Limit")
    offset: int = Field(..., description="Offset")
    alerts: List[AlertResponse] = Field(..., description="Alert list")


class CheckAlertsRequest(BaseModel):
    """Request to check and generate alerts for a port"""
    port_id: str = Field(..., description="Port ID")
    check_authorizations: bool = Field(default=True, description="Check vessel authorizations")
    check_occupancy: bool = Field(default=True, description="Check occupancy levels")
    check_conflicts: bool = Field(default=True, description="Check berth conflicts")
    severity_threshold: AlertSeverity = Field(
        default=AlertSeverity.WARNING, description="Minimum severity to report"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "check_authorizations": True,
                "check_occupancy": True,
                "check_conflicts": True,
                "severity_threshold": "warning"
            }
        }
