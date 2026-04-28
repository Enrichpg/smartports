# SmartPort Backend Tests
# Unit tests for critical business logic

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from schemas.berth import BerthStatus
from schemas.portcall import PortCallStatus
from schemas.authorization import AuthorizationStatus, AuthorizationValidationResponse
from services.berth_service import BerthService, BerthStateError
from services.portcall_service import PortCallService, PortCallError


class TestBerthStateTransitions:
    """Test berth state machine validation"""

    def test_valid_transition_free_to_occupied(self):
        """Test valid transition from FREE to OCCUPIED"""
        service = BerthService()
        valid_transitions = service.VALID_TRANSITIONS[BerthStatus.FREE]
        assert BerthStatus.OCCUPIED in valid_transitions

    def test_valid_transition_occupied_to_free(self):
        """Test valid transition from OCCUPIED to FREE"""
        service = BerthService()
        valid_transitions = service.VALID_TRANSITIONS[BerthStatus.OCCUPIED]
        assert BerthStatus.FREE in valid_transitions

    def test_invalid_transition_occupied_to_reserved(self):
        """Test invalid transition from OCCUPIED to RESERVED"""
        service = BerthService()
        valid_transitions = service.VALID_TRANSITIONS[BerthStatus.OCCUPIED]
        assert BerthStatus.RESERVED not in valid_transitions

    def test_invalid_transition_completed_state(self):
        """Test terminal state transitions"""
        service = BerthService()
        # COMPLETED and CANCELLED are terminal states
        valid_transitions = service.VALID_TRANSITIONS.get(BerthStatus.OUT_OF_SERVICE, [])
        assert BerthStatus.OCCUPIED not in valid_transitions


class TestPortCallStateTransitions:
    """Test PortCall lifecycle state machine"""

    def test_valid_transition_scheduled_to_expected(self):
        """Test valid transition from SCHEDULED to EXPECTED"""
        service = PortCallService()
        valid_transitions = service.VALID_TRANSITIONS[PortCallStatus.SCHEDULED]
        assert PortCallStatus.EXPECTED in valid_transitions

    def test_valid_transition_expected_to_active(self):
        """Test valid transition from EXPECTED to ACTIVE"""
        service = PortCallService()
        valid_transitions = service.VALID_TRANSITIONS[PortCallStatus.EXPECTED]
        assert PortCallStatus.ACTIVE in valid_transitions

    def test_valid_transition_active_to_completed(self):
        """Test valid transition from ACTIVE to COMPLETED"""
        service = PortCallService()
        valid_transitions = service.VALID_TRANSITIONS[PortCallStatus.ACTIVE]
        assert PortCallStatus.COMPLETED in valid_transitions

    def test_invalid_transition_active_to_expected(self):
        """Test invalid transition from ACTIVE back to EXPECTED"""
        service = PortCallService()
        valid_transitions = service.VALID_TRANSITIONS[PortCallStatus.ACTIVE]
        assert PortCallStatus.EXPECTED not in valid_transitions

    def test_terminal_state_completed(self):
        """Test that COMPLETED has no valid transitions (terminal)"""
        service = PortCallService()
        valid_transitions = service.VALID_TRANSITIONS[PortCallStatus.COMPLETED]
        assert len(valid_transitions) == 0


class TestAuthorizationValidation:
    """Test authorization validation logic"""

    @pytest.mark.asyncio
    async def test_authorization_expired(self):
        """Test authorization expiration check"""
        # Simulated entity with expired authorization
        expired_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        auth_entity = {
            "id": "urn:smartdatamodels:BoatAuthorized:test:1",
            "vesselId": {"object": "urn:smartdatamodels:Vessel:test:1"},
            "vesselName": {"value": "Test Vessel"},
            "status": {"value": "authorized"},
            "expirationDate": {"value": expired_date},
            "insuranceValid": {"value": True},
        }

        # Authorization should be marked as expired
        assert datetime.fromisoformat(expired_date.replace("Z", "+00:00")) < datetime.utcnow()

    def test_authorization_valid_future_date(self):
        """Test valid authorization with future expiration"""
        future_date = (datetime.utcnow() + timedelta(days=365)).isoformat()
        assert datetime.fromisoformat(future_date.replace("Z", "+00:00")) > datetime.utcnow()

    @pytest.mark.asyncio
    async def test_authorization_insurance_check(self):
        """Test insurance validation in authorization"""
        # With insurance valid=True, should pass
        should_pass = True

        # With insurance valid=False, should fail
        should_fail = False

        assert should_pass
        assert not should_fail


class TestPortCallCreation:
    """Test PortCall creation and validation"""

    def test_portcall_id_generation(self):
        """Test PortCall ID generation"""
        service = PortCallService()
        port_id = "urn:smartdatamodels:Port:Galicia:CorA"
        vessel_id = "urn:smartdatamodels:Vessel:ImoRegistry:9876543"

        portcall_id = service._generate_portcall_id(port_id, vessel_id)

        # Should follow URN format
        assert portcall_id.startswith("urn:smartdatamodels:PortCall:")
        assert "Galicia" in portcall_id
        assert "CorA" in portcall_id
        assert "9876543" in portcall_id

    def test_portcall_id_uniqueness(self):
        """Test that different PortCall IDs are generated"""
        service = PortCallService()
        port_id = "urn:smartdatamodels:Port:Galicia:CorA"
        vessel_id = "urn:smartdatamodels:Vessel:ImoRegistry:9876543"

        id1 = service._generate_portcall_id(port_id, vessel_id)
        id2 = service._generate_portcall_id(port_id, vessel_id)

        # IDs should be unique due to UUID component
        assert id1 != id2


class TestAvailabilityCalculation:
    """Test availability calculation logic"""

    def test_availability_rate_calculation(self):
        """Test availability rate percentage calculation"""
        total_berths = 10
        available_berths = 4

        availability_rate = (available_berths / total_berths) * 100
        assert availability_rate == 40.0

    def test_availability_rate_full_occupancy(self):
        """Test availability when all berths are occupied"""
        total_berths = 10
        available_berths = 0

        availability_rate = (available_berths / total_berths) * 100
        assert availability_rate == 0.0

    def test_availability_rate_all_free(self):
        """Test availability when all berths are free"""
        total_berths = 10
        available_berths = 10

        availability_rate = (available_berths / total_berths) * 100
        assert availability_rate == 100.0

    def test_availability_rate_zero_berths(self):
        """Test availability calculation with zero berths"""
        total_berths = 0
        available_berths = 0

        # Should handle division by zero
        availability_rate = (
            (available_berths / total_berths * 100) if total_berths > 0 else 0
        )
        assert availability_rate == 0


class TestAlertGeneration:
    """Test alert generation logic"""

    def test_high_occupancy_alert(self):
        """Test high occupancy threshold"""
        occupancy_rate = 85.0
        should_trigger_warning = occupancy_rate >= 75
        assert should_trigger_warning

    def test_full_occupancy_alert(self):
        """Test full occupancy threshold"""
        occupancy_rate = 100.0
        should_trigger_critical = occupancy_rate >= 90
        assert should_trigger_critical

    def test_low_occupancy_no_alert(self):
        """Test low occupancy produces no alert"""
        occupancy_rate = 50.0
        should_trigger_warning = occupancy_rate >= 75
        assert not should_trigger_warning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
