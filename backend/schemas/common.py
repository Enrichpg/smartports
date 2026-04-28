# SmartPort Common Schemas
# Base NGSI-LD and common response patterns

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


class NGSILDEntityResponse(BaseModel):
    """
    Base NGSI-LD entity response.
    All domain entities should extend this.
    """
    id: str = Field(..., description="NGSI-LD entity ID (URN)")
    type: str = Field(..., description="NGSI-LD entity type")
    context: Optional[Dict[str, Any]] = Field(
        None, alias="@context", description="NGSI-LD @context"
    )

    class Config:
        populate_by_name = True


class GeoLocation(BaseModel):
    """GeoJSON representation of coordinates"""
    type: str = Field(default="Point", description="GeoJSON type")
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class GeoProperty(BaseModel):
    """NGSI-LD GeoProperty"""
    type: str = Field(default="GeoProperty", description="Property type")
    value: GeoLocation = Field(..., description="GeoJSON value")


class ObservedProperty(BaseModel):
    """NGSI-LD Property with observedAt timestamp"""
    type: str = Field(default="Property", description="Property type")
    value: Any = Field(..., description="Property value")
    observedAt: str = Field(..., description="ISO 8601 timestamp")


class NGSIRelationship(BaseModel):
    """NGSI-LD Relationship"""
    type: str = Field(default="Relationship", description="Relationship type")
    object: str = Field(..., description="Related entity ID (URN)")


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error description")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="Request path")


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    limit: int = Field(default=20, ge=1, le=100, description="Max items")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class FilterParams(BaseModel):
    """Common filter parameters"""
    search: Optional[str] = Field(None, description="Free-text search")
    status: Optional[str] = Field(None, description="Filter by status")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="Sort order")
