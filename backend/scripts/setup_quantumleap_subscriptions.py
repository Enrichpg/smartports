#!/usr/bin/env python3
# Script to create Orion-LD subscriptions to QuantumLeap
# Enables time series persistence for historical analysis

import httpx
import json
import logging
from typing import Dict, Any, List
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Manage Orion-LD subscriptions for QuantumLeap"""
    
    def __init__(self):
        self.orion_url = settings.orion_base_url
        self.quantumleap_url = settings.quantumleap_base_url
        self.service = settings.fiware_service
        self.service_path = settings.fiware_service_path
        self.headers = {
            "Content-Type": "application/ld+json",
            "FIWARE-Service": self.service,
            "FIWARE-ServicePath": self.service_path,
        }
    
    def create_subscription(
        self,
        subscription_id: str,
        entity_type: str,
        watched_attributes: List[str],
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a subscription to send entity updates to QuantumLeap.
        
        Args:
            subscription_id: Unique subscription identifier
            entity_type: NGSI-LD entity type (e.g., "WeatherObserved")
            watched_attributes: List of attributes to watch
            description: Human-readable description
            
        Returns:
            Response from Orion
        """
        
        payload = {
            "@context": [
                "https://smartdatamodels.org/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ],
            "id": f"urn:ngsi-ld:Subscription:{subscription_id}",
            "type": "Subscription",
            "description": description or f"Subscription to stream {entity_type} to QuantumLeap",
            "entities": [
                {
                    "type": entity_type
                }
            ],
            "watchedAttributes": watched_attributes,
            "notification": {
                "attributes": watched_attributes,
                "format": "normalized",
                "endpoint": {
                    "uri": f"{self.quantumleap_url}/v2/notify",
                    "accept": "application/json"
                }
            }
        }
        
        try:
            response = httpx.post(
                f"{self.orion_url}/ngsi-ld/v1/subscriptions",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"✅ Subscription created: {subscription_id}")
            return {
                "status": "created",
                "subscription_id": subscription_id,
                "entity_type": entity_type
            }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to create subscription {subscription_id}: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                logger.error(f"   Error: {error_detail}")
            except:
                logger.error(f"   Response: {e.response.text}")
            
            return {
                "status": "failed",
                "subscription_id": subscription_id,
                "error": str(e)
            }
        
        except Exception as e:
            logger.error(f"❌ Unexpected error creating subscription {subscription_id}: {str(e)}")
            return {
                "status": "error",
                "subscription_id": subscription_id,
                "error": str(e)
            }
    
    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """List all active subscriptions"""
        try:
            response = httpx.get(
                f"{self.orion_url}/ngsi-ld/v1/subscriptions",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            subscriptions = response.json()
            logger.info(f"Found {len(subscriptions)} active subscriptions")
            return subscriptions
        
        except Exception as e:
            logger.error(f"Failed to list subscriptions: {str(e)}")
            return []
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription by ID"""
        try:
            response = httpx.delete(
                f"{self.orion_url}/ngsi-ld/v1/subscriptions/{subscription_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"✅ Subscription deleted: {subscription_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete subscription: {str(e)}")
            return False


def setup_all_subscriptions() -> List[Dict[str, Any]]:
    """
    Set up all default subscriptions for SmartPorts entities.
    Idempotent - can be run multiple times safely.
    """
    
    manager = SubscriptionManager()
    
    # Define subscriptions for each entity type that should have historical data
    subscriptions = [
        {
            "id": "weather-observed-historical",
            "entity_type": "WeatherObserved",
            "attributes": [
                "temperature",
                "relativeHumidity",
                "atmosphericPressure",
                "windSpeed",
                "windDirection",
                "precipitation"
            ],
            "description": "Stream weather observations to QuantumLeap for historical analysis"
        },
        {
            "id": "sea-condition-historical",
            "entity_type": "SeaConditionObserved",
            "attributes": [
                "significantWaveHeight",
                "waterTemperature",
                "windSpeed",
                "tideLevel"
            ],
            "description": "Stream sea conditions to QuantumLeap"
        },
        {
            "id": "berth-status-historical",
            "entity_type": "Berth",
            "attributes": [
                "status",
                "occupied"
            ],
            "description": "Track berth occupancy history"
        },
        {
            "id": "availability-historical",
            "entity_type": "BoatPlacesAvailable",
            "attributes": [
                "availablePlaces",
                "occupancyRate"
            ],
            "description": "Track boat places availability history"
        },
        {
            "id": "vessel-historical",
            "entity_type": "Vessel",
            "attributes": [
                "status",
                "location",
                "speed"
            ],
            "description": "Track vessel positions and status"
        },
        {
            "id": "air-quality-historical",
            "entity_type": "AirQualityObserved",
            "attributes": [
                "aqi",
                "dominantPollutant"
            ],
            "description": "Track air quality observations"
        },
    ]
    
    results = []
    
    logger.info("=" * 70)
    logger.info("Setting up Orion-LD → QuantumLeap Subscriptions")
    logger.info("=" * 70)
    logger.info(f"Orion URL: {manager.orion_url}")
    logger.info(f"QuantumLeap URL: {manager.quantumleap_url}")
    logger.info(f"FIWARE Service: {manager.service}")
    logger.info(f"FIWARE Service Path: {manager.service_path}")
    logger.info("")
    
    for sub_config in subscriptions:
        logger.info(f"Creating subscription: {sub_config['id']}")
        result = manager.create_subscription(
            subscription_id=sub_config["id"],
            entity_type=sub_config["entity_type"],
            watched_attributes=sub_config["attributes"],
            description=sub_config["description"]
        )
        results.append(result)
        logger.info("")
    
    # Summary
    logger.info("=" * 70)
    successful = sum(1 for r in results if r["status"] in ["created", "already_exists"])
    logger.info(f"✅ SUMMARY: {successful}/{len(results)} subscriptions ready")
    logger.info("=" * 70)
    
    return results


if __name__ == "__main__":
    results = setup_all_subscriptions()
    
    # Print results as JSON
    print("\n")
    print(json.dumps(results, indent=2))
