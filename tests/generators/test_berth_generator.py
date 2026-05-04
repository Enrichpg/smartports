
from backend.generators.berth_generator import BerthGenerator
from backend.generators.port_profiles import load_port_profiles
from backend.generators.scenario_config import ScenarioConfig

def test_berth_generator_initialization():
    ports = load_port_profiles()
    config = ScenarioConfig(volume="xlarge")
    generator = BerthGenerator(ports, config)
    assert len(generator.ports) == 8

def test_generate_all_berths():
    ports = load_port_profiles()
    config = ScenarioConfig(volume="xlarge")
    generator = BerthGenerator(ports, config)
    berths = generator.generate_all_berths()
    assert len(berths) <= 320
    assert all(b["type"] == "Berth" for b in berths)
