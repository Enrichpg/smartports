# PortCall Service
# Business logic for PortCall lifecycle management

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from .orion_ld_client import orion_client
from .authorization_service import authorization_service
from .berth_service import berth_service, BerthStateError, BerthConflictError
from schemas.portcall import PortCallResponse, PortCallStatus

logger = logging.getLogger(__name__)


class PortCallError(Exception):
    """Raised when PortCall operation fails"""
    pass


class PortCallService:
    """Business logic for PortCall operations"""

    # Valid state transitions
    VALID_TRANSITIONS = {
        PortCallStatus.SCHEDULED: [PortCallStatus.EXPECTED, PortCallStatus.CANCELLED],
        PortCallStatus.EXPECTED: [PortCallStatus.ACTIVE, PortCallStatus.CANCELLED],
        PortCallStatus.ACTIVE: [PortCallStatus.COMPLETED, PortCallStatus.CANCELLED],
        PortCallStatus.COMPLETED: [],  # Terminal state
        PortCallStatus.CANCELLED: [],  # Terminal state
    }

    async def create_portcall(
        self,
        vessel_id: str,
        port_id: str,
        estimated_arrival: datetime,
        estimated_departure: Optional[datetime] = None,
        berth_id: Optional[str] = None,
        purpose: Optional[str] = None,
        cargo_type: Optional[str] = None,
    ) -> PortCallResponse:
        """
        Create a new PortCall with validation.
        Validates:
        - Vessel authorization
        - Berth availability (if specified)
        """
        try:
            # Validate vessel authorization
            auth_response = await authorization_service.validate_vessel_authorization(
                vessel_id, port_id=port_id, check_insurance=True
            )

            if not auth_response.is_authorized:
                raise PortCallError(
                    f"Vessel {vessel_id} is not authorized: {auth_response.reason}"
                )

            # Generate PortCall ID
            portcall_id = self._generate_portcall_id(port_id, vessel_id)

            # Prepare entity data
            entity_data = {
                "id": portcall_id,
                "type": "PortCall",
                "@context": [
                    "https://www.w3.org/2019/wot/json-schema",
                    "https://smartdatamodels.org/context.jsonld",
                ],
                "vesselId": {"type": "Relationship", "object": vessel_id},
                "portId": {"type": "Relationship", "object": port_id},
                "status": {"type": "Property", "value": PortCallStatus.SCHEDULED.value},
                "estimatedArrival": {
                    "type": "Property",
                    "value": estimated_arrival.isoformat(),
                },
                "createdAt": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                },
                "updatedAt": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                },
            }

            # Optional fields
            if estimated_departure:
                entity_data["estimatedDeparture"] = {
                    "type": "Property",
                    "value": estimated_departure.isoformat(),
                }

            if berth_id:
                # Validate berth availability
                try:
                    berth = await berth_service.get_berth_by_id(berth_id)
                    if berth.status.value != "free":
                        raise PortCallError(
                            f"Berth {berth_id} is not available (status: {berth.status})"
                        )
                    entity_data["berthId"] = {"type": "Relationship", "object": berth_id}
                except Exception as e:
                    raise PortCallError(f"Invalid berth: {str(e)}")

            if purpose:
                entity_data["purpose"] = {"type": "Property", "value": purpose}

            if cargo_type:
                entity_data["cargoType"] = {"type": "Property", "value": cargo_type}

            # Create in Orion-LD
            await orion_client.create_entity(entity_data)

            # Return created PortCall
            return await self.get_portcall_by_id(portcall_id)

        except PortCallError:
            raise
        except Exception as e:
            logger.error(f"Error creating PortCall: {e}")
            raise PortCallError(f"Failed to create PortCall: {str(e)}")

    async def get_portcall_by_id(self, portcall_id: str) -> PortCallResponse:
        """Get a PortCall by ID"""
        try:
            entity = await orion_client.get_entity(portcall_id)
            return self._entity_to_portcall_response(entity)
        except Exception as e:
            logger.error(f"Error fetching PortCall {portcall_id}: {e}")
            raise

    async def get_all_portcalls(
        self, limit: int = 100, offset: int = 0
    ) -> tuple[List[PortCallResponse], int]:
        """Get all PortCalls"""
        try:
            entities = await orion_client.query_by_type("PortCall")
            total = len(entities)
            portcalls_data = entities[offset : offset + limit]
            portcalls = [self._entity_to_portcall_response(p) for p in portcalls_data]
            return portcalls, total
        except Exception as e:
            logger.error(f"Error fetching PortCalls: {e}")
            raise

    async def get_portcalls_by_port(
        self, port_id: str, limit: int = 100, offset: int = 0
    ) -> tuple[List[PortCallResponse], int]:
        """Get PortCalls for a specific port"""
        try:
            entities = await orion_client.query_entities(
                entity_type="PortCall",
                filters=f"portId=={port_id}",
                limit=1000,
            )
            total = len(entities)
            portcalls_data = entities[offset : offset + limit]
            portcalls = [self._entity_to_portcall_response(p) for p in portcalls_data]
            return portcalls, total
        except Exception as e:
            logger.error(f"Error fetching PortCalls for port {port_id}: {e}")
            raise

    async def get_active_portcalls(
        self, port_id: Optional[str] = None
    ) -> List[PortCallResponse]:
        """Get active PortCalls (status=active)"""
        try:
            filters = "status==active"
            if port_id:
                filters += f" AND portId=={port_id}"

            entities = await orion_client.query_entities(
                entity_type="PortCall", filters=filters, limit=1000
            )
            return [self._entity_to_portcall_response(p) for p in entities]
        except Exception as e:
            logger.error(f"Error fetching active PortCalls: {e}")
            raise

    async def change_portcall_status(
        self,
        portcall_id: str,
        new_status: PortCallStatus,
        reason: Optional[str] = None,
    ) -> PortCallResponse:
        """
        Change PortCall status with state machine validation.
        Handles berth assignment on transition to ACTIVE.
        """
        try:
            # Get current PortCall
            portcall_entity = await orion_client.get_entity(portcall_id)
            current_status_str = (
                portcall_entity.get("status", {}).get("value", "scheduled").lower()
            )

            try:
                current_status = PortCallStatus(current_status_str)
            except ValueError:
                current_status = PortCallStatus.SCHEDULED

            # Validate transition
            if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
                raise PortCallError(
                    f"Cannot transition PortCall from {current_status} to {new_status}"
                )

            # Special handling for ACTIVE status
            if new_status == PortCallStatus.ACTIVE:
                # Mark actual arrival
                update_data = {
                    "status": {"type": "Property", "value": new_status.value},
                    "actualArrival": {
                        "type": "Property",
                        "value": datetime.utcnow().isoformat(),
                    },
                    "updatedAt": {
                        "type": "Property",
                        "value": datetime.utcnow().isoformat(),
                    },
                }

                # Try to assign berth if not already assigned
                berth_id = portcall_entity.get("berthId", {}).get("object")
                if not berth_id:
                    # Auto-assign first available berth (optional logic)
                    logger.info(f"PortCall {portcall_id} activated without berth assignment")
            else:
                # Standard status update
                update_data = {
                    "status": {"type": "Property", "value": new_status.value},
                    "updatedAt": {
                        "type": "Property",
                        "value": datetime.utcnow().isoformat(),
                    },
                }

            if reason:
                update_data["statusReason"] = {"type": "Property", "value": reason}

            await orion_client.update_entity(portcall_id, update_data)

            # Return updated PortCall
            return await self.get_portcall_by_id(portcall_id)

        except PortCallError:
            raise
        except Exception as e:
            logger.error(f"Error changing PortCall {portcall_id} status: {e}")
            raise PortCallError(f"Failed to change PortCall status: {str(e)}")

    async def close_portcall(
        self,
        portcall_id: str,
        actual_departure: datetime,
        notes: Optional[str] = None,
    ) -> PortCallResponse:
        """
        Close a PortCall (mark as completed and free the berth).
        """
        try:
            # Get PortCall
            portcall_entity = await orion_client.get_entity(portcall_id)

            # Free the berth if assigned
            berth_id = portcall_entity.get("berthId", {}).get("object")
            if berth_id:
                try:
                    await berth_service.change_berth_status(
                        berth_id, "free", reason="PortCall closed"
                    )
                except Exception as e:
                    logger.warning(f"Failed to free berth {berth_id}: {e}")

            # Update PortCall to completed
            update_data = {
                "status": {"type": "Property", "value": PortCallStatus.COMPLETED.value},
                "actualDeparture": {
                    "type": "Property",
                    "value": actual_departure.isoformat(),
                },
                "updatedAt": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                },
            }

            if notes:
                update_data["closingNotes"] = {"type": "Property", "value": notes}

            await orion_client.update_entity(portcall_id, update_data)

            return await self.get_portcall_by_id(portcall_id)

        except Exception as e:
            logger.error(f"Error closing PortCall {portcall_id}: {e}")
            raise PortCallError(f"Failed to close PortCall: {str(e)}")

    def _generate_portcall_id(self, port_id: str, vessel_id: str) -> str:
        """Generate unique PortCall ID"""
        port_code = port_id.split(":")[-1]
        vessel_code = vessel_id.split(":")[-1]
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        return f"urn:smartdatamodels:PortCall:Galicia:{port_code}_{timestamp}_{vessel_code}_{unique_id}"

    def _entity_to_portcall_response(self, entity: Dict[str, Any]) -> PortCallResponse:
        """Convert Orion-LD entity to PortCallResponse schema"""
        status_str = entity.get("status", {}).get("value", "scheduled").lower()
        try:
            status = PortCallStatus(status_str)
        except ValueError:
            status = PortCallStatus.SCHEDULED

        estimated_arrival_str = entity.get("estimatedArrival", {}).get("value")
        estimated_departure_str = entity.get("estimatedDeparture", {}).get("value")
        actual_arrival_str = entity.get("actualArrival", {}).get("value")
        actual_departure_str = entity.get("actualDeparture", {}).get("value")
        created_at_str = entity.get("createdAt", {}).get("value", datetime.utcnow().isoformat())
        updated_at_str = entity.get("updatedAt", {}).get("value", datetime.utcnow().isoformat())

        return PortCallResponse(
            id=entity.get("id", ""),
            vessel_id=entity.get("vesselId", {}).get("object", ""),
            vessel_name=entity.get("vesselName", {}).get("value"),
            port_id=entity.get("portId", {}).get("object", ""),
            port_name=entity.get("portName", {}).get("value"),
            berth_id=entity.get("berthId", {}).get("object"),
            berth_name=entity.get("berthName", {}).get("value"),
            status=status,
            estimated_arrival=datetime.fromisoformat(
                estimated_arrival_str.replace("Z", "+00:00")
            )
            if estimated_arrival_str
            else datetime.utcnow(),
            estimated_departure=datetime.fromisoformat(
                estimated_departure_str.replace("Z", "+00:00")
            )
            if estimated_departure_str
            else None,
            actual_arrival=datetime.fromisoformat(
                actual_arrival_str.replace("Z", "+00:00")
            )
            if actual_arrival_str
            else None,
            actual_departure=datetime.fromisoformat(
                actual_departure_str.replace("Z", "+00:00")
            )
            if actual_departure_str
            else None,
            purpose=entity.get("purpose", {}).get("value"),
            cargo_type=entity.get("cargoType", {}).get("value"),
            created_at=datetime.fromisoformat(
                created_at_str.replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                updated_at_str.replace("Z", "+00:00")
            ),
        )


# Singleton instance
portcall_service = PortCallService()
