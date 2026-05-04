
from backend.generators.port_profiles import load_port_profiles, PortProfile

def test_load_port_profiles_returns_8_ports():
    ports = load_port_profiles()
    assert len(ports) == 8
    assert all(isinstance(p, PortProfile) for p in ports)

def test_a_coruna_port():
    ports = load_port_profiles()
    a_coruna = next(p for p in ports if p.key == "a-coruna")
    assert a_coruna.name == "Puerto de A Coruña"
    assert a_coruna.berth_count_est == 50
    assert a_coruna.vessel_count_est == 700

def test_all_ports_have_valid_coordinates():
    ports = load_port_profiles()
    for port in ports:
        lon, lat = port.coordinates
        assert -10 < lon < -7
        assert 42 < lat < 44
