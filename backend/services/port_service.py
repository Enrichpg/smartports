# Port Service
# Business logic for port operations and queries

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from .orion_ld_client import orion_client
from schemas.port import PortResponse, PortSummaryResponse

logger = logging.getLogger(__name__)


class PortService:
    """Business logic for port operations"""

    async def get_all_ports(self, limit: int = 100, offset: int = 0) -> tuple[List[PortResponse], int]:
        """Get all ports with pagination"""
        try:
            entities = await orion_client.query_by_type("Port")
            total = len(entities)
            ports_data = entities[offset : offset + limit]
            ports = [self._entity_to_port_response(p) for p in ports_data]
            return ports, total
        except Exception as e:
            logger.error(f"Error fetching ports: {e}")
            raise

    async def get_port_by_id(self, port_id: str) -> PortResponse:
        """Get a specific port by ID"""
        try:
            entity = await orion_client.get_entity(port_id)
            return self._entity_to_port_response(entity)
        except Exception as e:
            logger.error(f"Error fetching port {port_id}: {e}")
            raise

    async def get_port_summary(self, port_id: str) -> PortSummaryResponse:
        """Get operational summary for a port with KPIs"""
        try:
            # Get port info
            port_entity = await orion_client.get_entity(port_id)
            _nk = "name" if "name" in port_entity else "https://uri.etsi.org/ngsi-ld/name"
            port_name = port_entity.get(_nk, {}).get("value", "Unknown")

            # Get all berths in this port
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", filters=f"relatedTo({port_id})"
            )

            # Count berths by status
            berths_free = 0
            berths_occupied = 0
            berths_reserved = 0
            berths_out_of_service = 0

            for berth in berth_entities:
                status = berth.get("status", {}).get("value", "").lower()
                if status == "free":
                    berths_free += 1
                elif status == "occupied":
                    berths_occupied += 1
                elif status == "reserved":
                    berths_reserved += 1
                elif status == "outofservice":
                    berths_out_of_service += 1

            total_berths = len(berth_entities)
            occupancy_rate = (
                ((berths_occupied + berths_reserved) / total_berths * 100)
                if total_berths > 0
                else 0
            )

            # Get active PortCalls
            portcalls = await orion_client.query_entities(
                entity_type="PortCall", filters=f"hasRelationship(hasPort,{port_id})"
            )
            active_vessels = sum(
                1 for pc in portcalls if pc.get("status", {}).get("value") == "active"
            )

            # Get active alerts
            alerts = await orion_client.query_entities(
                entity_type="Alert", filters=f"relatedTo({port_id})"
            )
            active_alerts = sum(
                1 for a in alerts if a.get("is_active", {}).get("value", True)
            )

            return PortSummaryResponse(
                id=port_id,
                name=port_name,
                total_berths=total_berths,
                berths_free=berths_free,
                berths_occupied=berths_occupied,
                berths_reserved=berths_reserved,
                berths_out_of_service=berths_out_of_service,
                occupancy_rate=occupancy_rate,
                active_vessels=active_vessels,
                active_alerts=active_alerts,
                last_updated=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Error generating port summary for {port_id}: {e}")
            raise

    def _entity_to_port_response(self, entity: Dict[str, Any]) -> PortResponse:
        """Convert Orion-LD entity to PortResponse schema"""
        # Orion-LD may return NGSI-LD core terms as full URIs
        _name_key = "name" if "name" in entity else "https://uri.etsi.org/ngsi-ld/name"
        return PortResponse(
            id=entity.get("id", ""),
            name=entity.get(_name_key, {}).get("value", ""),
            country=entity.get("country", {}).get("value", "ES"),
            location=entity.get("location"),
            url=entity.get("url", {}).get("value"),
            dbpedia=entity.get("dbpedia", {}).get("value"),
            imo=entity.get("imo", {}).get("value"),
            description=entity.get("description", {}).get("value"),
        )


# Singleton instance
port_service = PortService()
