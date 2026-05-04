
from backend.generators.sensor_factory import SensorFactory
from backend.generators.port_profiles import load_port_profiles
from backend.generators.scenario_config import ScenarioConfig

def test_sensor_factory_initialization():
    ports = load_port_profiles()
    config = ScenarioConfig(volume="xlarge")
    factory = SensorFactory(ports, config)
    assert len(factory.ports) == 8

def test_generate_all_sensors():
    ports = load_port_profiles()
    config = ScenarioConfig(volume="xlarge")
    factory = SensorFactory(ports, config)
    sensors = factory.generate_all_sensors()
    assert len(sensors) <= 180
    assert all(s["type"] == "Device" for s in sensors)
