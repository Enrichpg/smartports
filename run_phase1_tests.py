#!/usr/bin/env python3
"""
Phase 1: Core Generators Test Suite
Verifies all 8 generator modules are working correctly.
"""
import sys
import traceback

def run_tests():
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: port_profiles
    print("\n[1/8] Testing port_profiles...")
    try:
        from backend.generators.port_profiles import load_port_profiles
        ports = load_port_profiles()
        assert len(ports) == 8, f"Expected 8 ports, got {len(ports)}"
        assert ports[0].key == "a-coruna", "First port should be a-coruna"
        assert ports[0].berth_count_est == 50, "A Coruña berth count should be 50"
        print("  ✓ port_profiles PASS")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ port_profiles FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 2: scenario_config
    print("\n[2/8] Testing scenario_config...")
    try:
        from backend.generators.scenario_config import ScenarioConfig
        config = ScenarioConfig("xlarge")
        assert config.num_vessels == 4500, f"Expected 4500 vessels, got {config.num_vessels}"
        assert config.num_berths == 320, f"Expected 320 berths, got {config.num_berths}"
        
        vessel_counts = config.get_vessel_count_by_archetype()
        total = sum(vessel_counts.values())
        assert total == 4500, f"Archetype vessel counts sum to {total}, not 4500"
        assert 'fishing' in vessel_counts, "Missing fishing archetype"
        print(f"  ✓ scenario_config PASS (vessel distribution: {vessel_counts})")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ scenario_config FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 3: vessel_factory
    print("\n[3/8] Testing vessel_factory...")
    try:
        from backend.generators.vessel_factory import VesselFactory
        from backend.generators.scenario_config import ScenarioConfig
        
        config = ScenarioConfig("small")
        factory = VesselFactory(config)
        vessel = factory.generate_vessel('fishing', 'a-coruna', 'DOCKED')
        
        assert vessel['id'].startswith('urn:ngsi-ld:Vessel:'), "Invalid vessel ID format"
        assert vessel['type'] == 'Vessel', "Vessel type should be Vessel"
        assert vessel['state']['value'] == 'DOCKED', "Vessel state should be DOCKED"
        assert 'location' in vessel, "Vessel should have location"
        print("  ✓ vessel_factory PASS")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ vessel_factory FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 4: berth_generator
    print("\n[4/8] Testing berth_generator...")
    try:
        from backend.generators.berth_generator import BerthGenerator
        from backend.generators.port_profiles import load_port_profiles
        from backend.generators.scenario_config import ScenarioConfig
        
        config = ScenarioConfig("small")
        ports = load_port_profiles()
        gen = BerthGenerator(ports, config)
        berth = gen.generate_berth_for_port(ports[0])
        
        assert berth['id'].startswith('urn:ngsi-ld:Berth:'), "Invalid berth ID format"
        assert berth['type'] == 'Berth', "Berth type should be Berth"
        assert 'length' in berth, "Berth should have length"
        print("  ✓ berth_generator PASS")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ berth_generator FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 5: sensor_factory
    print("\n[5/8] Testing sensor_factory...")
    try:
        from backend.generators.sensor_factory import SensorFactory
        from backend.generators.port_profiles import load_port_profiles
        from backend.generators.scenario_config import ScenarioConfig
        
        config = ScenarioConfig("small")
        ports = load_port_profiles()
        factory = SensorFactory(ports, config)
        sensor = factory.generate_sensor(ports[0], 'AirQualityDevice')
        
        assert sensor['id'].startswith('urn:ngsi-ld:Device:'), "Invalid device ID format"
        assert sensor['type'] == 'Device', "Device type should be Device"
        assert 'location' in sensor, "Device should have location"
        print("  ✓ sensor_factory PASS")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ sensor_factory FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 6: simulation_initializer
    print("\n[6/8] Testing simulation_initializer...")
    try:
        from backend.generators.simulation_initializer import SimulationInitializer
        from backend.generators.port_profiles import load_port_profiles
        from backend.generators.scenario_config import ScenarioConfig
        from backend.generators.vessel_factory import VesselFactory
        
        config = ScenarioConfig("small")
        ports = load_port_profiles()
        vessel_factory = VesselFactory(config)
        init = SimulationInitializer(ports, config, vessel_factory)
        movements = init.create_historical_movement()
        
        assert len(movements) > 0, "Historical movement should have entries"
        first_move = movements[0]
        assert 'timestamp' in first_move, "Movement should have timestamp"
        assert 'state' in first_move, "Movement should have state"
        print(f"  ✓ simulation_initializer PASS ({len(movements)} historical entries)")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ simulation_initializer FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 7: data_validator
    print("\n[7/8] Testing data_validator...")
    try:
        from backend.generators.data_validator import DataValidator
        from backend.generators.synthetic_data_generator import SyntheticDataGenerator
        from backend.generators.scenario_config import ScenarioConfig
        
        # Generate small dataset for validation test
        config = ScenarioConfig("small")
        gen = SyntheticDataGenerator(config)
        entities = gen.generate_all()
        
        validator = DataValidator()
        result = validator.validate_entities(entities)
        
        # Small dataset should validate successfully
        assert result['valid'], f"Validation failed: {result.get('errors', [])}"
        print(f"  ✓ data_validator PASS ({len(entities)} entities validated)")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ data_validator FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Test 8: synthetic_data_generator
    print("\n[8/8] Testing synthetic_data_generator...")
    try:
        from backend.generators.synthetic_data_generator import SyntheticDataGenerator
        from backend.generators.scenario_config import ScenarioConfig
        
        config = ScenarioConfig("medium")
        gen = SyntheticDataGenerator(config)
        entities = gen.generate_all()
        
        assert len(entities) > 0, "Generator should produce entities"
        
        # Count entity types
        port_count = sum(1 for e in entities if e['type'] == 'Port')
        berth_count = sum(1 for e in entities if e['type'] == 'Berth')
        vessel_count = sum(1 for e in entities if e['type'] == 'Vessel')
        device_count = sum(1 for e in entities if e['type'] == 'Device')
        
        print(f"  ✓ synthetic_data_generator PASS")
        print(f"    - Ports: {port_count}")
        print(f"    - Berths: {berth_count}")
        print(f"    - Vessels: {vessel_count}")
        print(f"    - Devices: {device_count}")
        print(f"    - Total: {len(entities)}")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ synthetic_data_generator FAIL: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"Phase 1 Test Results: {tests_passed} PASS, {tests_failed} FAIL")
    print("="*60)
    
    return 0 if tests_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(run_tests())
