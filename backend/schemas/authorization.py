# Authorization Domain Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AuthorizationStatus(str, Enum):
    """Authorization status states"""
    AUTHORIZED = "authorized"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    UNAUTHORIZED = "unauthorized"


class AuthorizationResponse(BaseModel):
    """BoatAuthorized entity response"""
    id: str = Field(..., description="Authorization URN ID")
    vessel_id: str = Field(..., description="Vessel ID")
    vessel_name: Optional[str] = Field(None, description="Vessel name")
    imo_number: Optional[str] = Field(None, description="Vessel IMO number")
    status: AuthorizationStatus = Field(..., description="Authorization status")
    issued_date: datetime = Field(..., description="Issue date")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")
    port_id: Optional[str] = Field(None, description="Port ID if port-specific")
    certificate_number: Optional[str] = Field(None, description="Certificate identifier")
    issuing_authority: Optional[str] = Field(None, description="Issuing authority")
    restrictions: Optional[str] = Field(None, description="Any restrictions/notes")
    insurance_valid: bool = Field(default=True, description="Insurance validity")
    insurance_expiration: Optional[datetime] = Field(None, description="Insurance expiration")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:smartdatamodels:BoatAuthorized:Galicia:imo9876543",
                "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "vessel_name": "MSC Example",
                "imo_number": "9876543",
                "status": "authorized",
                "issued_date": "2025-01-01T00:00:00",
                "expiration_date": "2027-12-31T23:59:59",
                "port_id": None,
                "certificate_number": "AUTH-2025-001",
                "issuing_authority": "Autoridad Portuaria de Galicia",
                "insurance_valid": True,
                "insurance_expiration": "2027-06-30T23:59:59"
            }
        }


class AuthorizationValidationRequest(BaseModel):
    """Request to validate vessel authorization"""
    vessel_id: str = Field(..., description="Vessel ID to validate")
    imo_number: Optional[str] = Field(None, description="IMO number (alternative identifier)")
    port_id: Optional[str] = Field(None, description="Port ID (for port-specific checks)")
    check_insurance: bool = Field(default=True, description="Also validate insurance")

    class Config:
        json_schema_extra = {
            "example": {
                "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "port_id": "urn:smartdatamodels:Port:Galicia:CorA",
                "check_insurance": True
            }
        }


class AuthorizationValidationResponse(BaseModel):
    """Response from authorization validation"""
    is_authorized: bool = Field(..., description="Authorization valid")
    vessel_id: str = Field(..., description="Vessel ID")
    vessel_name: Optional[str] = Field(None, description="Vessel name")
    status: AuthorizationStatus = Field(..., description="Authorization status")
    reason: Optional[str] = Field(None, description="Reason if not authorized")
    details: Optional[dict] = Field(None, description="Additional details")

    class Config:
        json_schema_extra = {
            "example": {
                "is_authorized": True,
                "vessel_id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
                "vessel_name": "MSC Example",
                "status": "authorized",
                "reason": None,
                "details": {
                    "expiration_date": "2027-12-31T23:59:59",
                    "insurance_valid": True
                }
            }
        }
