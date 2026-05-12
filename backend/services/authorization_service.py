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

    async def _find_auth_entity(self, vessel_id: str, port_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find BoatAuthorized entity for a vessel by scanning all authorizations."""
        all_auths = await orion_client.query_by_type("BoatAuthorized")
        for auth in all_auths:
            ref_vessel = auth.get("refVessel", {}).get("object", "")
            if ref_vessel == vessel_id:
                if port_id:
                    authorized_port = auth.get("authorizedPort", {}).get("value", "")
                    if port_id not in authorized_port and authorized_port not in port_id:
                        continue
                return auth
        return None

    async def get_vessel_authorization(
        self, vessel_id: str, port_id: Optional[str] = None
    ) -> AuthorizationResponse:
        """Get authorization for a vessel (optionally port-specific)"""
        try:
            auth_entity = await self._find_auth_entity(vessel_id, port_id)
            if not auth_entity:
                raise ValueError(f"No authorization found for vessel {vessel_id}")
            return self._entity_to_authorization_response(auth_entity)
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
        """
        try:
            auth_entity = await self._find_auth_entity(vessel_id, port_id)

            if not auth_entity:
                return AuthorizationValidationResponse(
                    is_authorized=False,
                    vessel_id=vessel_id,
                    vessel_name=None,
                    status=AuthorizationStatus.UNAUTHORIZED,
                    reason="No authorization found",
                )

            # BoatAuthorized uses "status" if present, default to authorized
            auth_status_str = auth_entity.get("status", {}).get("value", "authorized")

            try:
                auth_status = AuthorizationStatus(auth_status_str)
            except ValueError:
                auth_status = AuthorizationStatus.AUTHORIZED

            # Check expiration via validUntil
            expiration_str = auth_entity.get("validUntil", {}).get("value")
            if expiration_str:
                try:
                    expiration = datetime.fromisoformat(
                        expiration_str.replace("Z", "+00:00")
                    )
                    if datetime.utcnow().replace(tzinfo=expiration.tzinfo) > expiration:
                        return AuthorizationValidationResponse(
                            is_authorized=False,
                            vessel_id=vessel_id,
                            vessel_name=None,
                            status=AuthorizationStatus.EXPIRED,
                            reason=f"Authorization expired on {expiration_str}",
                            details={"expiration_date": expiration_str},
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse expiration date: {e}")

            # All checks passed
            return AuthorizationValidationResponse(
                is_authorized=True,
                vessel_id=vessel_id,
                vessel_name=None,
                status=AuthorizationStatus.AUTHORIZED,
                reason=None,
                details={"expiration_date": expiration_str},
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
            status = AuthorizationStatus.AUTHORIZED

        issued_date_str = entity.get("validFrom", {}).get("value")
        expiration_date_str = entity.get("validUntil", {}).get("value")

        return AuthorizationResponse(
            id=entity.get("id", ""),
            vessel_id=entity.get("refVessel", {}).get("object", ""),
            vessel_name=None,
            imo_number=None,
            status=status,
            issued_date=datetime.fromisoformat(issued_date_str.replace("Z", "+00:00"))
            if issued_date_str
            else datetime.utcnow(),
            expiration_date=datetime.fromisoformat(expiration_date_str.replace("Z", "+00:00"))
            if expiration_date_str
            else None,
            port_id=entity.get("authorizedPort", {}).get("value"),
            certificate_number=None,
            issuing_authority=None,
            restrictions=None,
            insurance_valid=True,
            insurance_expiration=None,
        )


# Singleton instance
authorization_service = AuthorizationService()
