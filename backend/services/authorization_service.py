# Authorization Service
# Business logic for vessel authorization validation and management

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from .orion_ld_client import orion_client
from schemas.authorization import (
    AuthorizationResponse,
    AuthorizationStatus,
    AuthorizationValidationResponse,
)

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """Raised when authorization check fails"""
    pass


class AuthorizationService:
    """Business logic for authorization operations"""

    async def get_vessel_authorization(
        self, vessel_id: str, port_id: Optional[str] = None
    ) -> AuthorizationResponse:
        """Get authorization for a vessel (optionally port-specific)"""
        try:
            # Query BoatAuthorized entities
            filters = f"vesselId=={vessel_id}"
            if port_id:
                filters += f" AND portId=={port_id}"

            auth_entities = await orion_client.query_entities(
                entity_type="BoatAuthorized", filters=filters, limit=1
            )

            if not auth_entities:
                raise ValueError(f"No authorization found for vessel {vessel_id}")

            return self._entity_to_authorization_response(auth_entities[0])
        except Exception as e:
            logger.error(f"Error fetching authorization for vessel {vessel_id}: {e}")
            raise

    async def validate_vessel_authorization(
        self,
        vessel_id: str,
        port_id: Optional[str] = None,
        check_insurance: bool = True,
    ) -> AuthorizationValidationResponse:
        """
        Validate if a vessel is authorized to operate.
        Checks:
        - Authorization exists
        - Authorization not expired
        - Authorization not revoked
        - Insurance valid (if check_insurance=True)
        """
        try:
            # Get authorization
            auth_entities = await orion_client.query_entities(
                entity_type="BoatAuthorized",
                filters=f"vesselId=={vessel_id}",
                limit=1,
            )

            if not auth_entities:
                return AuthorizationValidationResponse(
                    is_authorized=False,
                    vessel_id=vessel_id,
                    vessel_name=None,
                    status=AuthorizationStatus.UNAUTHORIZED,
                    reason="No authorization found",
                )

            auth_entity = auth_entities[0]
            auth_status_str = auth_entity.get("status", {}).get("value", "authorized")

            try:
                auth_status = AuthorizationStatus(auth_status_str)
            except ValueError:
                auth_status = AuthorizationStatus.UNAUTHORIZED

            # Check if revoked
            if auth_status == AuthorizationStatus.REVOKED:
                return AuthorizationValidationResponse(
                    is_authorized=False,
                    vessel_id=vessel_id,
                    vessel_name=auth_entity.get("vesselName", {}).get("value"),
                    status=auth_status,
                    reason="Authorization has been revoked",
                )

            # Check expiration
            expiration_str = auth_entity.get("expirationDate", {}).get("value")
            if expiration_str:
                try:
                    expiration = datetime.fromisoformat(
                        expiration_str.replace("Z", "+00:00")
                    )
                    if datetime.utcnow() > expiration:
                        return AuthorizationValidationResponse(
                            is_authorized=False,
                            vessel_id=vessel_id,
                            vessel_name=auth_entity.get("vesselName", {}).get("value"),
                            status=AuthorizationStatus.EXPIRED,
                            reason=f"Authorization expired on {expiration_str}",
                            details={"expiration_date": expiration_str},
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse expiration date: {e}")

            # Check insurance if requested
            if check_insurance:
                insurance_valid = auth_entity.get("insuranceValid", {}).get("value", True)
                insurance_expiration_str = (
                    auth_entity.get("insuranceExpiration", {}).get("value")
                )

                if not insurance_valid:
                    return AuthorizationValidationResponse(
                        is_authorized=False,
                        vessel_id=vessel_id,
                        vessel_name=auth_entity.get("vesselName", {}).get("value"),
                        status=AuthorizationStatus.PENDING,
                        reason="Insurance is not valid",
                    )

                if insurance_expiration_str:
                    try:
                        insurance_expiration = datetime.fromisoformat(
                            insurance_expiration_str.replace("Z", "+00:00")
                        )
                        if datetime.utcnow() > insurance_expiration:
                            return AuthorizationValidationResponse(
                                is_authorized=False,
                                vessel_id=vessel_id,
                                vessel_name=auth_entity.get("vesselName", {}).get("value"),
                                status=AuthorizationStatus.PENDING,
                                reason=f"Insurance expired on {insurance_expiration_str}",
                                details={"insurance_expiration": insurance_expiration_str},
                            )
                    except Exception as e:
                        logger.warning(f"Failed to parse insurance expiration date: {e}")

            # All checks passed
            return AuthorizationValidationResponse(
                is_authorized=True,
                vessel_id=vessel_id,
                vessel_name=auth_entity.get("vesselName", {}).get("value"),
                status=AuthorizationStatus.AUTHORIZED,
                reason=None,
                details={
                    "expiration_date": expiration_str,
                    "insurance_valid": insurance_valid if check_insurance else None,
                },
            )

        except Exception as e:
            logger.error(f"Error validating authorization for vessel {vessel_id}: {e}")
            return AuthorizationValidationResponse(
                is_authorized=False,
                vessel_id=vessel_id,
                vessel_name=None,
                status=AuthorizationStatus.UNAUTHORIZED,
                reason=f"Authorization check failed: {str(e)}",
            )

    async def get_all_authorizations(
        self, limit: int = 100, offset: int = 0
    ) -> tuple[List[AuthorizationResponse], int]:
        """Get all authorizations"""
        try:
            entities = await orion_client.query_by_type("BoatAuthorized")
            total = len(entities)
            auth_data = entities[offset : offset + limit]
            authorizations = [self._entity_to_authorization_response(a) for a in auth_data]
            return authorizations, total
        except Exception as e:
            logger.error(f"Error fetching authorizations: {e}")
            raise

    def _entity_to_authorization_response(
        self, entity: Dict[str, Any]
    ) -> AuthorizationResponse:
        """Convert Orion-LD entity to AuthorizationResponse schema"""
        status_str = entity.get("status", {}).get("value", "authorized")
        try:
            status = AuthorizationStatus(status_str)
        except ValueError:
            status = AuthorizationStatus.UNAUTHORIZED

        issued_date_str = entity.get("issuedDate", {}).get("value")
        expiration_date_str = entity.get("expirationDate", {}).get("value")
        insurance_expiration_str = entity.get("insuranceExpiration", {}).get("value")

        return AuthorizationResponse(
            id=entity.get("id", ""),
            vessel_id=entity.get("vesselId", {}).get("object", ""),
            vessel_name=entity.get("vesselName", {}).get("value"),
            imo_number=entity.get("imoNumber", {}).get("value"),
            status=status,
            issued_date=datetime.fromisoformat(issued_date_str.replace("Z", "+00:00"))
            if issued_date_str
            else datetime.utcnow(),
            expiration_date=datetime.fromisoformat(expiration_date_str.replace("Z", "+00:00"))
            if expiration_date_str
            else None,
            port_id=entity.get("portId", {}).get("object"),
            certificate_number=entity.get("certificateNumber", {}).get("value"),
            issuing_authority=entity.get("issuingAuthority", {}).get("value"),
            restrictions=entity.get("restrictions", {}).get("value"),
            insurance_valid=entity.get("insuranceValid", {}).get("value", True),
            insurance_expiration=datetime.fromisoformat(
                insurance_expiration_str.replace("Z", "+00:00")
            )
            if insurance_expiration_str
            else None,
        )


# Singleton instance
authorization_service = AuthorizationService()
