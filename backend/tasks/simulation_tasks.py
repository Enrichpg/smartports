"""Celery tasks for synthetic maritime simulation."""

import logging
from datetime import datetime
from backend.tasks.celery_app import get_celery
from backend.services.simulation_engine import SimulationEngine
from backend.services.orion_service import OrionService


logger = logging.getLogger(__name__)


def register_simulation_tasks():
    """Register periodic simulation tasks."""
    app = get_celery()
    if not app:
        logger.warning("Celery app not initialized, simulation tasks not registered")
        return

    # Schedule periodic simulation tick every 5 minutes
    app.conf.beat_schedule = getattr(app.conf, 'beat_schedule', {})
    app.conf.beat_schedule.update({
        'tick-simulation': {
            'task': 'backend.tasks.simulation_tasks.tick_simulation',
            'schedule': 300.0,  # 5 minutes in seconds
            'options': {'queue': 'default'},
        },
    })
    logger.info("Simulation tasks registered with Celery Beat")


@get_celery().task(bind=True, name="backend.tasks.simulation_tasks.tick_simulation", queue="default")
def tick_simulation(self):
    """Periodic task: update vessel states and generate observations."""
    try:
        logger.info("Starting simulation tick...")
        engine = SimulationEngine()
        orion = OrionService()

        # Get and update vessels (up to 5000)
        vessels = orion.get_entities(entity_type="Vessel", limit=5000)
        updated_count = 0

        if vessels:
            for vessel in vessels:
                # Extract archetype from vessel ID: urn:ngsi-ld:Vessel:galicia-{archetype}-{num}
                try:
                    parts = vessel.get("id", "").split("-")
                    archetype = parts[2] if len(parts) > 2 else "fishing"
                except Exception:
                    archetype = "fishing"

                updated_vessel = engine.update_vessel_state(vessel, archetype)
                try:
                    orion.upsert_entity(updated_vessel)
                    updated_count += 1
                except Exception as e:
                    logger.warning(f"Failed to update vessel {vessel.get('id')}: {e}")

        # Generate observations from sensors (up to 200)
        sensors = orion.get_entities(entity_type="Device", limit=200)
        observation_count = 0

        if sensors:
            for sensor in sensors:
                sensor_type = sensor.get("type_sensor", {}).get("value", "WeatherDevice")
                try:
                    if "Air" in sensor_type:
                        obs = engine.generate_air_quality_observation(sensor["id"])
                    else:
                        obs = engine.generate_weather_observation(sensor["id"])
                    orion.create_entity(obs)
                    observation_count += 1
                except Exception as e:
                    logger.warning(f"Failed to create observation for sensor {sensor.get('id')}: {e}")

        result = {
            "status": "completed",
            "vessels_updated": updated_count,
            "observations_created": observation_count,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        logger.info(f"Tick complete: {updated_count} vessels, {observation_count} observations")
        return result

    except Exception as e:
        logger.error(f"Error in simulation tick: {e}", exc_info=True)
        raise
