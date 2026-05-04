
from backend.generators.synthetic_data_generator import SyntheticDataGenerator
from backend.generators.scenario_config import ScenarioConfig

def test_synthetic_data_generator_init():
    config = ScenarioConfig(volume="xlarge")
    generator = SyntheticDataGenerator(config)
    assert generator.config == config

def test_generate_all_creates_entities():
    config = ScenarioConfig(volume="small", seed=42)
    generator = SyntheticDataGenerator(config)
    entities = generator.generate_all()
    assert len(entities) > 0
    types = [e.get("type") for e in entities]
    assert "Port" in types
    assert "Berth" in types
    assert "Vessel" in types
    assert "Device" in types
