
import pytest
from backend.generators.scenario_config import ScenarioConfig

def test_scenario_config_xlarge():
    config = ScenarioConfig(volume="xlarge", seed=42)
    assert config.num_vessels == 4500
    assert config.num_berths == 320
    assert config.num_sensors == 180

def test_scenario_config_large():
    config = ScenarioConfig(volume="large")
    assert config.num_vessels == 2500
    assert config.num_berths == 180

def test_invalid_volume_raises_error():
    with pytest.raises(ValueError):
        ScenarioConfig(volume="invalid")

def test_vessel_archetype_ratios():
    config = ScenarioConfig(volume="xlarge")
    total_ratio = sum(arch["ratio"] for arch in config.vessel_archetypes.values())
    assert abs(total_ratio - 1.0) < 0.001
