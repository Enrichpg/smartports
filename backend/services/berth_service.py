# Berth Service
# Business logic for berth management and state transitions

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from .orion_ld_client import orion_client
from schemas.berth import BerthResponse, BerthStatus

logger = logging.getLogger(__name__)


class BerthStateError(Exception):
    """Raised when berth state transition is invalid"""
    pass


class BerthConflictError(Exception):
    """Raised when berth assignment conflicts exist"""
    pass


class BerthService:
    """Business logic for berth operations"""

    # Valid state transitions
    VALID_TRANSITIONS = {
        BerthStatus.FREE: [BerthStatus.RESERVED, BerthStatus.OCCUPIED, BerthStatus.OUT_OF_SERVICE],
        BerthStatus.RESERVED: [BerthStatus.FREE, BerthStatus.OCCUPIED, BerthStatus.OUT_OF_SERVICE],
        BerthStatus.OCCUPIED: [BerthStatus.FREE, BerthStatus.OUT_OF_SERVICE],
        BerthStatus.OUT_OF_SERVICE: [BerthStatus.FREE],
    }

    async def get_berths_by_port(
        self, port_id: str, limit: int = 100, offset: int = 0
    ) -> tuple[List[BerthResponse], int]:
        """Get all berths in a port"""
        try:
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", limit=1000
            )
            # Filter by port
            port_berths = [
                b for b in berth_entities
                if b.get("relatedTo", {}).get("object") == port_id
            ]
            total = len(port_berths)
            berths_data = port_berths[offset : offset + limit]
            berths = [self._entity_to_berth_response(b) for b in berths_data]
            return berths, total
        except Exception as e:
            logger.error(f"Error fetching berths for port {port_id}: {e}")
            raise

    async def get_berth_by_id(self, berth_id: str) -> BerthResponse:
        """Get a specific berth by ID"""
        try:
            entity = await orion_client.get_entity(berth_id)
            return self._entity_to_berth_response(entity)
        except Exception as e:
            logger.error(f"Error fetching berth {berth_id}: {e}")
            raise

    async def change_berth_status(
        self,
        berth_id: str,
        new_status: BerthStatus,
        reason: Optional[str] = None,
    ) -> BerthResponse:
        """
        Change berth status with validation.
        Implements state machine to ensure valid transitions.
        """
        try:
            # Get current berth
            berth_entity = await orion_client.get_entity(berth_id)
            current_status_str = berth_entity.get("status", {}).get("value", "free").lower()

            try:
                current_status = BerthStatus(current_status_str)
            except ValueError:
                current_status = BerthStatus.FREE

            # Validate transition
            if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
                raise BerthStateError(
                    f"Cannot transition from {current_status} to {new_status}"
                )

            # Additional validation for occupied status
            if new_status == BerthStatus.OCCUPIED:
                # Check if there's already an active PortCall
                portcalls = await orion_client.query_entities(
                    entity_type="PortCall", filters=f"status=active"
                )
                for pc in portcalls:
                    if pc.get("berth_id", {}).get("object") == berth_id:
                        raise BerthConflictError(
                            f"Berth {berth_id} already has active PortCall"
                        )

            # Update status in Orion-LD
            update_data = {
                "status": {"type": "Property", "value": new_status.value},
                "lastStatusChange": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                    "observedAt": datetime.utcnow().isoformat(),
                },
            }

            if reason:
                update_data["statusReason"] = {"type": "Property", "value": reason}

            await orion_client.update_entity(berth_id, update_data)

            # Return updated berth
            updated_entity = await orion_client.get_entity(berth_id)
            return self._entity_to_berth_response(updated_entity)

        except BerthStateError:
            raise
        except BerthConflictError:
            raise
        except Exception as e:
            logger.error(f"Error changing berth {berth_id} status: {e}")
            raise

    async def get_berths_by_facility(
        self, facility_id: str, limit: int = 100, offset: int = 0
    ) -> tuple[List[BerthResponse], int]:
        """Get all berths in a facility"""
        try:
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", limit=1000
            )
            # Filter by facility
            facility_berths = [
                b for b in berth_entities
                if b.get("partOf", {}).get("object") == facility_id
            ]
            total = len(facility_berths)
            berths_data = facility_berths[offset : offset + limit]
            berths = [self._entity_to_berth_response(b) for b in berths_data]
            return berths, total
        except Exception as e:
            logger.error(f"Error fetching berths for facility {facility_id}: {e}")
            raise

    async def get_available_berths(self, port_id: str) -> List[BerthResponse]:
        """Get available (free) berths in a port"""
        try:
            berths, _ = await self.get_berths_by_port(port_id, limit=1000)
            return [b for b in berths if b.status == BerthStatus.FREE]
        except Exception as e:
            logger.error(f"Error fetching available berths for port {port_id}: {e}")
            raise

    def _entity_to_berth_response(self, entity: Dict[str, Any]) -> BerthResponse:
        """Convert Orion-LD entity to BerthResponse schema"""
        status_str = entity.get("status", {}).get("value", "free").lower()
        try:
            status = BerthStatus(status_str)
        except ValueError:
            status = BerthStatus.FREE

        return BerthResponse(
            id=entity.get("id", ""),
            name=entity.get("name", {}).get("value", ""),
            port_id=entity.get("relatedTo", {}).get("object", ""),
            facility_id=entity.get("partOf", {}).get("object"),
            berth_type=entity.get("berthType", {}).get("value", "unknown"),
            status=status,
            depth=entity.get("depth", {}).get("value"),
            length=entity.get("length", {}).get("value"),
            draft_limit=entity.get("draftLimit", {}).get("value"),
            category=entity.get("category", {}).get("value"),
            active_portcall_id=entity.get("activePortCall", {}).get("object"),
            last_status_change=datetime.fromisoformat(
                entity.get("lastStatusChange", {}).get("value", datetime.utcnow().isoformat())
            ),
        )


# Singleton instance
berth_service = BerthService()
