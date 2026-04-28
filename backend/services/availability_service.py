# Availability Service
# Business logic for berth availability management and recalculation

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from .orion_ld_client import orion_client
from schemas.availability import BoatPlacesAvailableResponse, AvailabilitySummaryResponse
from schemas.berth import BerthStatus

logger = logging.getLogger(__name__)


class AvailabilityService:
    """Business logic for availability operations"""

    async def get_port_availability(self, port_id: str) -> AvailabilitySummaryResponse:
        """Get availability summary for a port"""
        try:
            # Get all berths in port
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", limit=1000
            )
            port_berths = [
                b for b in berth_entities
                if b.get("relatedTo", {}).get("object") == port_id
            ]

            # Group by category
            by_category = defaultdict(lambda: {"total": 0, "available": 0, "berths": []})

            for berth in port_berths:
                category = berth.get("category", {}).get("value", "unknown")
                status = berth.get("status", {}).get("value", "free")
                by_category[category]["total"] += 1
                by_category[category]["berths"].append(berth)

                if status == BerthStatus.FREE.value:
                    by_category[category]["available"] += 1

            # Build response
            availability_responses = []
            total_available = 0
            total_berths = 0

            port_name = await self._get_port_name(port_id)

            for category, data in by_category.items():
                total_berths += data["total"]
                total_available += data["available"]

                avg_depth = self._calculate_average_depth(data["berths"])

                availability_responses.append(
                    BoatPlacesAvailableResponse(
                        id=f"urn:smartdatamodels:BoatPlacesAvailable:{port_id.split(':')[-1]}:{category}",
                        port_id=port_id,
                        port_name=port_name,
                        category=category,
                        availability_count=data["available"],
                        total_berths_in_category=data["total"],
                        average_depth=avg_depth,
                        last_updated=datetime.utcnow(),
                    )
                )

            availability_rate = (
                (total_available / total_berths * 100) if total_berths > 0 else 0
            )

            return AvailabilitySummaryResponse(
                port_id=port_id,
                port_name=port_name,
                total_available_berths=total_available,
                total_berths=total_berths,
                availability_rate=availability_rate,
                by_category=availability_responses,
                last_recalculated=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Error getting availability for port {port_id}: {e}")
            raise

    async def recalculate_port_availability(self, port_id: str) -> AvailabilitySummaryResponse:
        """
        Recalculate availability and update BoatPlacesAvailable entities in Orion-LD.
        This is the master function that synchronizes availability state.
        """
        try:
            availability = await self.get_port_availability(port_id)

            # Update or create BoatPlacesAvailable entities for each category
            for category_availability in availability.by_category:
                entity_data = {
                    "id": category_availability.id,
                    "type": "BoatPlacesAvailable",
                    "portId": {
                        "type": "Relationship",
                        "object": port_id,
                    },
                    "category": {
                        "type": "Property",
                        "value": category_availability.category,
                    },
                    "availabilityCount": {
                        "type": "Property",
                        "value": category_availability.availability_count,
                        "observedAt": datetime.utcnow().isoformat(),
                    },
                    "totalBerthsInCategory": {
                        "type": "Property",
                        "value": category_availability.total_berths_in_category,
                    },
                    "lastUpdated": {
                        "type": "Property",
                        "value": datetime.utcnow().isoformat(),
                        "observedAt": datetime.utcnow().isoformat(),
                    },
                }

                if category_availability.average_depth:
                    entity_data["averageDepth"] = {
                        "type": "Property",
                        "value": category_availability.average_depth,
                    }

                try:
                    await orion_client.upsert_entity(entity_data)
                except Exception as e:
                    logger.warning(
                        f"Failed to upsert BoatPlacesAvailable entity: {e}"
                    )

            logger.info(f"Recalculated availability for port {port_id}")
            return availability

        except Exception as e:
            logger.error(f"Error recalculating availability for port {port_id}: {e}")
            raise

    async def get_facility_availability(self, facility_id: str) -> AvailabilitySummaryResponse:
        """Get availability for a specific facility"""
        try:
            # Get all berths in facility
            berth_entities = await orion_client.query_entities(
                entity_type="Berth", limit=1000
            )
            facility_berths = [
                b for b in berth_entities
                if b.get("partOf", {}).get("object") == facility_id
            ]

            # Group by category
            by_category = defaultdict(lambda: {"total": 0, "available": 0, "berths": []})

            for berth in facility_berths:
                category = berth.get("category", {}).get("value", "unknown")
                status = berth.get("status", {}).get("value", "free")
                by_category[category]["total"] += 1
                by_category[category]["berths"].append(berth)

                if status == BerthStatus.FREE.value:
                    by_category[category]["available"] += 1

            # Build response
            availability_responses = []
            total_available = 0
            total_berths = 0

            facility_name = await self._get_facility_name(facility_id)

            for category, data in by_category.items():
                total_berths += data["total"]
                total_available += data["available"]

                avg_depth = self._calculate_average_depth(data["berths"])

                availability_responses.append(
                    BoatPlacesAvailableResponse(
                        id=f"urn:smartdatamodels:BoatPlacesAvailable:{facility_id.split(':')[-1]}:{category}",
                        port_id=facility_id,
                        port_name=facility_name,
                        category=category,
                        availability_count=data["available"],
                        total_berths_in_category=data["total"],
                        average_depth=avg_depth,
                        last_updated=datetime.utcnow(),
                    )
                )

            availability_rate = (
                (total_available / total_berths * 100) if total_berths > 0 else 0
            )

            return AvailabilitySummaryResponse(
                port_id=facility_id,
                port_name=facility_name,
                total_available_berths=total_available,
                total_berths=total_berths,
                availability_rate=availability_rate,
                by_category=availability_responses,
                last_recalculated=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Error getting availability for facility {facility_id}: {e}")
            raise

    def _calculate_average_depth(self, berths: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average depth of berths"""
        depths = [
            b.get("depth", {}).get("value")
            for b in berths
            if b.get("depth", {}).get("value") is not None
        ]
        return sum(depths) / len(depths) if depths else None

    async def _get_port_name(self, port_id: str) -> str:
        """Get port name"""
        try:
            port = await orion_client.get_entity(port_id)
            return port.get("name", {}).get("value", "Unknown")
        except:
            return "Unknown"

    async def _get_facility_name(self, facility_id: str) -> str:
        """Get facility name"""
        try:
            facility = await orion_client.get_entity(facility_id)
            return facility.get("name", {}).get("value", "Unknown")
        except:
            return "Unknown"


# Singleton instance
availability_service = AvailabilityService()
