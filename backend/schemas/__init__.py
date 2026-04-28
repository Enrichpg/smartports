# SmartPort Domain Schemas
# Pydantic models for NGSI-LD entities and API contracts

from .port import PortResponse, PortSummaryResponse, PortListResponse
from .berth import (
    BerthResponse, BerthStateChangeRequest, BerthListResponse, BerthDetailResponse
)
from .availability import (
    BoatPlacesAvailableResponse, AvailabilitySummaryResponse, RecalculateAvailabilityRequest
)
from .vessel import VesselResponse, VesselListResponse
from .authorization import (
    AuthorizationResponse, AuthorizationValidationRequest, AuthorizationValidationResponse
)
from .portcall import (
    PortCallCreateRequest, PortCallResponse, PortCallStatusChangeRequest, 
    PortCallCloseRequest, PortCallListResponse
)
from .alert import AlertResponse, AlertListResponse, CheckAlertsRequest
from .common import NGSILDEntityResponse, ErrorResponse

__all__ = [
    # Port
    "PortResponse",
    "PortSummaryResponse",
    "PortListResponse",
    # Berth
    "BerthResponse",
    "BerthStateChangeRequest",
    "BerthListResponse",
    "BerthDetailResponse",
    # Availability
    "BoatPlacesAvailableResponse",
    "AvailabilitySummaryResponse",
    "RecalculateAvailabilityRequest",
    # Vessel
    "VesselResponse",
    "VesselListResponse",
    # Authorization
    "AuthorizationResponse",
    "AuthorizationValidationRequest",
    "AuthorizationValidationResponse",
    # PortCall
    "PortCallCreateRequest",
    "PortCallResponse",
    "PortCallStatusChangeRequest",
    "PortCallCloseRequest",
    "PortCallListResponse",
    # Alert
    "AlertResponse",
    "AlertListResponse",
    "CheckAlertsRequest",
    # Common
    "NGSILDEntityResponse",
    "ErrorResponse",
]
