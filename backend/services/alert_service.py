# Alert Service
# Business logic for operational alert generation and management

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from .orion_ld_client import orion_client
from .authorization_service import authorization_service
from schemas.alert import AlertResponse, AlertType, AlertSeverity

logger = logging.getLogger(__name__)


class AlertService:
    """Business logic for alert operations"""

    async def check_port_alerts(
        self,
        port_id: str,
        check_authorizations: bool = True,
        check_occupancy: bool = True,
        check_conflicts: bool = True,
    ) -> List[AlertResponse]:
        """
        Check and generate alerts for a port.
        Checks:
        - Vessel authorization status
        - Occupancy levels
        - Berth conflicts
        """
        alerts = []

        try:
            if check_authorizations:
                auth_alerts = await self._check_authorization_alerts(port_id)
                alerts.extend(auth_alerts)

            if check_occupancy:
                occupancy_alerts = await self._check_occupancy_alerts(port_id)
                alerts.extend(occupancy_alerts)

            if check_conflicts:
                conflict_alerts = await self._check_berth_conflicts(port_id)
                alerts.extend(conflict_alerts)

            return alerts
        except Exception as e:
            logger.error(f"Error checking alerts for port {port_id}: {e}")
            raise

    async def _check_authorization_alerts(self, port_id: str) -> List[AlertResponse]:
        """Check for authorization-related alerts"""
        alerts = []

        try:
            # Get active PortCalls in this port
            portcalls = await orion_client.query_entities(
                entity_type="PortCall",
                filters=f"portId=={port_id} AND status==active",
                limit=1000,
            )

            for portcall in portcalls:
                vessel_id = portcall.get("vesselId", {}).get("object")
                if not vessel_id:
                    continue

                # Validate authorization
                auth_response = await authorization_service.validate_vessel_authorization(
                    vessel_id, port_id=port_id, check_insurance=True
                )

                if not auth_response.is_authorized:
                    alert = await self._create_alert(
                        port_id=port_id,
                        entity_id=vessel_id,
                        entity_type="Vessel",
                        alert_type=AlertType.AUTHORIZATION_FAILED,
                        severity=AlertSeverity.CRITICAL,
                        title=f"Vessel Authorization Failed: {auth_response.vessel_name}",
                        description=auth_response.reason or "Authorization validation failed",
                    )
                    alerts.append(alert)

                # Check for expired insurance
                if (
                    not auth_response.details.get("insurance_valid")
                    if auth_response.details
                    else False
                ):
                    alert = await self._create_alert(
                        port_id=port_id,
                        entity_id=vessel_id,
                        entity_type="Vessel",
                        alert_type=AlertType.INSURANCE_EXPIRED,
                        severity=AlertSeverity.WARNING,
                        title=f"Vessel Insurance Expired: {auth_response.vessel_name}",
                        description="Vessel insurance has expired",
                    )
                    alerts.append(alert)

            return alerts
        except Exception as e:
            logger.error(f"Error checking authorization alerts: {e}")
            return []

    async def _check_occupancy_alerts(self, port_id: str) -> List[AlertResponse]:
        """Check for occupancy-related alerts"""
        alerts = []

        try:
            # Get all berths in port
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", limit=1000
            )
            port_berths = [
                b for b in berth_entities
                if b.get("relatedTo", {}).get("object") == port_id
            ]

            total_berths = len(port_berths)
            occupied_berths = sum(
                1
                for b in port_berths
                if b.get("status", {}).get("value", "").lower() == "occupied"
            )

            occupancy_rate = (occupied_berths / total_berths * 100) if total_berths > 0 else 0

            # Generate alerts based on occupancy
            if occupancy_rate >= 90:
                alert = await self._create_alert(
                    port_id=port_id,
                    entity_id=port_id,
                    entity_type="Port",
                    alert_type=AlertType.OCCUPANCY_FULL,
                    severity=AlertSeverity.CRITICAL,
                    title="Port at Full Capacity",
                    description=f"Port occupancy at {occupancy_rate:.1f}% (all berths occupied)",
                )
                alerts.append(alert)
            elif occupancy_rate >= 75:
                alert = await self._create_alert(
                    port_id=port_id,
                    entity_id=port_id,
                    entity_type="Port",
                    alert_type=AlertType.OCCUPANCY_HIGH,
                    severity=AlertSeverity.WARNING,
                    title="High Port Occupancy",
                    description=f"Port occupancy at {occupancy_rate:.1f}%",
                )
                alerts.append(alert)

            return alerts
        except Exception as e:
            logger.error(f"Error checking occupancy alerts: {e}")
            return []

    async def _check_berth_conflicts(self, port_id: str) -> List[AlertResponse]:
        """Check for berth assignment conflicts"""
        alerts = []

        try:
            # Get all berths in port with active PortCalls
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", limit=1000
            )
            port_berths = [
                b for b in berth_entities
                if b.get("relatedTo", {}).get("object") == port_id
            ]

            # Check for multiple PortCalls on same berth
            portcalls = await orion_client.query_entities(
                entity_type="PortCall",
                filters=f"portId=={port_id} AND status==active",
                limit=1000,
            )

            berth_assignments = {}
            for pc in portcalls:
                berth_id = pc.get("berthId", {}).get("object")
                if berth_id:
                    if berth_id not in berth_assignments:
                        berth_assignments[berth_id] = []
                    berth_assignments[berth_id].append(pc.get("id"))

            for berth_id, portcall_ids in berth_assignments.items():
                if len(portcall_ids) > 1:
                    alert = await self._create_alert(
                        port_id=port_id,
                        entity_id=berth_id,
                        entity_type="Berth",
                        alert_type=AlertType.BERTH_CONFLICT,
                        severity=AlertSeverity.CRITICAL,
                        title=f"Berth Conflict Detected: {berth_id}",
                        description=f"Berth assigned to {len(portcall_ids)} active PortCalls",
                    )
                    alerts.append(alert)

            return alerts
        except Exception as e:
            logger.error(f"Error checking berth conflicts: {e}")
            return []

    async def get_port_alerts(
        self, port_id: str, active_only: bool = True, limit: int = 100, offset: int = 0
    ) -> tuple[List[AlertResponse], int]:
        """Get alerts for a port"""
        try:
            filters = f"portId=={port_id}"
            if active_only:
                filters += " AND isActive==true"

            entities = await orion_client.query_entities(
                entity_type="Alert", filters=filters, limit=1000
            )

            total = len(entities)
            alerts_data = entities[offset : offset + limit]
            alerts = [self._entity_to_alert_response(a) for a in alerts_data]
            return alerts, total
        except Exception as e:
            logger.error(f"Error fetching alerts for port {port_id}: {e}")
            raise

    async def get_all_alerts(
        self, active_only: bool = True, limit: int = 100, offset: int = 0
    ) -> tuple[List[AlertResponse], int]:
        """Get all alerts"""
        try:
            if active_only:
                filters = "isActive==true"
                entities = await orion_client.query_entities(
                    entity_type="Alert", filters=filters, limit=1000
                )
            else:
                entities = await orion_client.query_by_type("Alert")

            total = len(entities)
            alerts_data = entities[offset : offset + limit]
            alerts = [self._entity_to_alert_response(a) for a in alerts_data]
            return alerts, total
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            raise

    async def acknowledge_alert(self, alert_id: str, operator_id: str) -> AlertResponse:
        """Acknowledge an alert"""
        try:
            update_data = {
                "acknowledgedAt": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                },
                "acknowledgedBy": {"type": "Property", "value": operator_id},
            }

            await orion_client.update_entity(alert_id, update_data)
            entity = await orion_client.get_entity(alert_id)
            return self._entity_to_alert_response(entity)
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            raise

    async def resolve_alert(self, alert_id: str) -> AlertResponse:
        """Resolve an alert"""
        try:
            update_data = {
                "isActive": {"type": "Property", "value": False},
                "resolvedAt": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                },
            }

            await orion_client.update_entity(alert_id, update_data)
            entity = await orion_client.get_entity(alert_id)
            return self._entity_to_alert_response(entity)
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            raise

    async def _create_alert(
        self,
        port_id: str,
        entity_id: str,
        entity_type: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
    ) -> AlertResponse:
        """Create and store an alert"""
        try:
            alert_id = f"urn:smartdatamodels:Alert:{port_id.split(':')[-1]}:{str(uuid.uuid4())[:8]}"

            entity_data = {
                "id": alert_id,
                "type": "Alert",
                "@context": [
                    "https://www.w3.org/2019/wot/json-schema",
                    "https://smartdatamodels.org/context.jsonld",
                ],
                "portId": {"type": "Relationship", "object": port_id},
                "entityId": {"type": "Property", "value": entity_id},
                "entityType": {"type": "Property", "value": entity_type},
                "alertType": {"type": "Property", "value": alert_type.value},
                "severity": {"type": "Property", "value": severity.value},
                "title": {"type": "Property", "value": title},
                "description": {"type": "Property", "value": description},
                "isActive": {"type": "Property", "value": True},
                "createdAt": {
                    "type": "Property",
                    "value": datetime.utcnow().isoformat(),
                },
            }

            await orion_client.upsert_entity(entity_data)
            entity = await orion_client.get_entity(alert_id)
            return self._entity_to_alert_response(entity)
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            # Return in-memory alert even if storage fails
            return AlertResponse(
                id=f"temp_alert_{str(uuid.uuid4())[:8]}",
                port_id=port_id,
                entity_id=entity_id,
                entity_type=entity_type,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                is_active=True,
                created_at=datetime.utcnow(),
            )

    def _entity_to_alert_response(self, entity: Dict[str, Any]) -> AlertResponse:
        """Convert Orion-LD entity to AlertResponse schema"""
        alert_type_str = entity.get("alertType", {}).get("value", "operational")
        severity_str = entity.get("severity", {}).get("value", "warning")

        try:
            alert_type = AlertType(alert_type_str)
        except ValueError:
            alert_type = AlertType.OPERATIONAL

        try:
            severity = AlertSeverity(severity_str)
        except ValueError:
            severity = AlertSeverity.WARNING

        created_at_str = entity.get("createdAt", {}).get("value")
        acknowledged_at_str = entity.get("acknowledgedAt", {}).get("value")
        resolved_at_str = entity.get("resolvedAt", {}).get("value")

        return AlertResponse(
            id=entity.get("id", ""),
            port_id=entity.get("portId", {}).get("object", ""),
            port_name=entity.get("portName", {}).get("value"),
            entity_id=entity.get("entityId", {}).get("value"),
            entity_type=entity.get("entityType", {}).get("value"),
            alert_type=alert_type,
            severity=severity,
            title=entity.get("title", {}).get("value", ""),
            description=entity.get("description", {}).get("value", ""),
            is_active=entity.get("isActive", {}).get("value", True),
            created_at=datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            if created_at_str
            else datetime.utcnow(),
            acknowledged_at=datetime.fromisoformat(acknowledged_at_str.replace("Z", "+00:00"))
            if acknowledged_at_str
            else None,
            acknowledged_by=entity.get("acknowledgedBy", {}).get("value"),
            resolved_at=datetime.fromisoformat(resolved_at_str.replace("Z", "+00:00"))
            if resolved_at_str
            else None,
        )


# Singleton instance
alert_service = AlertService()
