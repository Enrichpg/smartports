
from backend.generators.vessel_factory import VesselFactory
from backend.generators.scenario_config import ScenarioConfig

def test_vessel_factory_initialization():
    config = ScenarioConfig(volume="xlarge", seed=42)
    factory = VesselFactory(config)
    assert factory.config == config

def test_generate_vessel():
    config = ScenarioConfig(volume="xlarge", seed=42)
    factory = VesselFactory(config)
    vessel = factory.generate_vessel(archetype="fishing")
    assert vessel["type"] == "Vessel"
    assert "id" in vessel
    assert vessel["id"].startswith("urn:ngsi-ld:Vessel:galicia-fishing-")

def test_generate_all_vessels():
    config = ScenarioConfig(volume="small", seed=42)
    factory = VesselFactory(config)
    vessels = factory.generate_all_vessels()
    assert len(vessels) == 300
