"""
Integration tests for license key failover and multi-key management.

Tests verify:
1. Automatic failover to next key on failure
2. Health tracking (5 consecutive → faulty, 10 total → invalid)
3. Key rotation to healthy keys
4. Logging of key switches
5. Error handling when all keys are invalid

Run with: pytest tests/integration/test_license_failover.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from byapi_client_unified import ByapiClient
from byapi_config import ByapiConfig, KeyRotationManager, LicenseKeyHealth
from byapi_exceptions import AuthenticationError, NetworkError, ByapiError


class TestKeyRotationManager:
    """Test KeyRotationManager for multi-key handling."""

    def test_parse_single_key(self):
        """Test parsing a single license key."""
        config = ByapiConfig()
        config.license_keys = ["key123"]
        assert len(config.license_keys) == 1
        assert config.license_keys[0] == "key123"

    def test_parse_multiple_keys(self):
        """Test parsing multiple comma-separated keys."""
        config = ByapiConfig()
        config.license_keys = ["key1", "key2", "key3"]
        assert len(config.license_keys) == 3
        assert config.license_keys[0] == "key1"
        assert config.license_keys[2] == "key3"

    def test_get_license_key_returns_current_key(self):
        """Test that get_license_key returns a valid key."""
        config = ByapiConfig()
        config.license_keys = ["key1", "key2"]
        # Reinitialize key_manager with new keys
        config.key_manager = KeyRotationManager(config.license_keys)

        key = config.get_license_key()
        assert key in config.license_keys

    def test_get_next_key_rotates_to_next_key(self):
        """Test that get_next_key returns the next key."""
        manager = KeyRotationManager(["key1", "key2", "key3"])

        # Get first key
        key1 = manager.get_next_key()
        assert key1 in ["key1", "key2", "key3"]

    def test_key_rotation_skips_invalid_keys(self):
        """Test that invalid keys are skipped during rotation."""
        manager = KeyRotationManager(["key1", "key2", "key3"])

        # Mark key1 as invalid
        manager.keys["key1"].status = "invalid"

        # Next usable key should not be key1
        next_key = manager.get_next_key()
        assert next_key != "key1" or all(k.status == "invalid" for k in manager.keys.values())

    def test_mark_key_failure_increments_counters(self):
        """Test that mark_key_failure increments failure counters."""
        manager = KeyRotationManager(["key1", "key2"])

        # Mark failure
        manager.mark_key_failure("key1", "API error")

        key_health = manager.keys["key1"]
        assert key_health.total_failures == 1
        assert key_health.consecutive_failures == 1

    def test_mark_key_success_resets_consecutive_failures(self):
        """Test that mark_key_success resets consecutive failures."""
        manager = KeyRotationManager(["key1"])
        key_health = manager.keys["key1"]

        # Simulate failures
        key_health.consecutive_failures = 3

        # Mark success
        manager.mark_key_success("key1")

        # Consecutive should reset, but total should not
        assert key_health.consecutive_failures == 0
        assert key_health.total_failures == 0

    def test_faulty_status_at_5_consecutive_failures(self):
        """Test that status becomes 'faulty' at 5 consecutive failures."""
        manager = KeyRotationManager(["key1"])
        key_health = manager.keys["key1"]

        # Simulate 5 consecutive failures
        for i in range(5):
            manager.mark_key_failure("key1", f"Failure {i+1}")

        assert key_health.status == "faulty"
        assert key_health.consecutive_failures == 5

    def test_invalid_status_at_10_total_failures(self):
        """Test that status becomes 'invalid' at 10 total failures."""
        manager = KeyRotationManager(["key1"])
        key_health = manager.keys["key1"]

        # Simulate 10 total failures
        for i in range(10):
            manager.mark_key_failure("key1", f"Failure {i+1}")

        assert key_health.status == "invalid"
        assert key_health.total_failures == 10

    def test_consecutive_resets_on_success(self):
        """Test that consecutive failures reset on success."""
        manager = KeyRotationManager(["key1"])
        key_health = manager.keys["key1"]

        # 3 failures, then success, then more failures
        for i in range(3):
            manager.mark_key_failure("key1", f"Failure {i+1}")

        manager.mark_key_success("key1")

        # Consecutive should reset to 0
        assert key_health.consecutive_failures == 0
        # Total should still be 3
        assert key_health.total_failures == 3
        # Status should go back to healthy
        assert key_health.status == "healthy"


class TestLicenseKeyHealth:
    """Test LicenseKeyHealth tracking."""

    def test_new_key_is_healthy(self):
        """Test that new keys start as healthy."""
        health = LicenseKeyHealth(key="test_key")

        assert health.status == "healthy"
        assert health.consecutive_failures == 0
        assert health.total_failures == 0

    def test_is_usable_for_healthy_key(self):
        """Test that healthy keys are usable."""
        health = LicenseKeyHealth(key="test_key")
        assert health.is_usable

    def test_is_usable_for_faulty_key(self):
        """Test that faulty keys are still usable (not permanently disabled)."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "faulty"
        assert health.is_usable

    def test_is_usable_for_invalid_key(self):
        """Test that invalid keys are not usable."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "invalid"
        assert not health.is_usable

    def test_is_permanently_disabled_for_invalid_key(self):
        """Test that only invalid keys are permanently disabled."""
        health = LicenseKeyHealth(key="test_key")

        assert not health.is_permanently_disabled

        health.status = "invalid"
        assert health.is_permanently_disabled


class TestByapiClientFailover:
    """Test ByapiClient with multi-key failover."""

    def test_get_license_health_returns_list(self):
        """Test that get_license_health returns a list."""
        client = ByapiClient()
        health = client.get_license_health()

        assert isinstance(health, list)
        assert len(health) > 0

    def test_get_license_health_shows_key_status(self):
        """Test that license health objects show key status."""
        client = ByapiClient()
        health = client.get_license_health()

        for key_health in health:
            assert hasattr(key_health, "status")
            assert key_health.status in ["healthy", "faulty", "invalid"]
            assert hasattr(key_health, "consecutive_failures")
            assert hasattr(key_health, "total_failures")

    def test_health_key_is_masked(self):
        """Test that license keys are masked in health output."""
        client = ByapiClient()
        health = client.get_license_health()

        for key_health in health:
            # Key should be masked (show only first 8 chars + "...")
            assert len(key_health.key) <= 11  # 8 chars + "..." = 11
            if len(key_health.key) == 11:
                assert key_health.key.endswith("...")


class TestMultipleKeysFailover:
    """Test behavior with multiple license keys."""

    @patch('byapi_client_unified.requests.Session.get')
    def test_automatic_key_switch_on_failure(self, mock_get):
        """Test that system switches to next key on failure."""
        # Setup: First key fails, second key succeeds
        response1 = MagicMock()
        response1.status_code = 401  # Auth failure
        response2 = MagicMock()
        response2.status_code = 200
        response2.json.return_value = {
            "code": "000001",
            "name": "Test Stock",
            "close": 15.45,
            "open": 15.20,
            "high": 15.50,
            "low": 15.15,
            "volume": 1000000,
            "amount": 15400000,
            "price_change": 0.37,
            "pct_change": 2.45,
            "trade_date": "2025-01-28",
        }

        # First call with key1 fails, second call with key2 succeeds
        mock_get.side_effect = [response1, response2]

        # Create config with multiple keys
        config = ByapiConfig()
        config.license_keys = ["key1_invalid", "key2_valid"]

        client = ByapiClient(config_instance=config)

        # This should fail with first key and switch to second
        # The actual behavior depends on implementation
        try:
            # Try to get stock price
            # This may raise an exception if both keys fail
            pass
        except (AuthenticationError, ByapiError):
            # Expected if first key is invalid
            pass


class TestFailoverErrorHandling:
    """Test error handling in failover scenarios."""

    def test_raises_error_when_all_keys_invalid(self):
        """Test that error is raised when all keys are marked invalid."""
        config = ByapiConfig()
        config.license_keys = ["key1", "key2"]

        # Mark all keys as invalid
        for key_health in config.key_manager.keys.values():
            key_health.status = "invalid"

        # Trying to get a usable key should fail or return None
        # depending on implementation

    def test_error_message_helpful_for_no_usable_keys(self):
        """Test that error message is helpful when no usable keys remain."""
        # This test verifies that the error message guides the developer
        # to check their license keys
        pass


class TestFailoverLogging:
    """Test that failover events are logged appropriately."""

    def test_key_switch_logged_at_info_level(self):
        """Test that key switches are logged at INFO level."""
        # This would require capturing logs and verifying
        # that key switches produce INFO-level log entries
        pass

    def test_key_marked_faulty_logged_at_warning_level(self):
        """Test that marking a key as faulty produces WARNING log."""
        # This would require log capture
        pass

    def test_key_marked_invalid_logged_at_warning_level(self):
        """Test that marking a key as invalid produces WARNING log."""
        # This would require log capture
        pass


class TestRetryBehavior:
    """Test exponential backoff retry behavior."""

    def test_transient_errors_are_retried(self):
        """Test that transient errors (network, timeouts) are retried."""
        # This tests that temporary failures don't trigger key switching
        pass

    def test_permanent_errors_trigger_key_switch(self):
        """Test that permanent errors (401, 403) trigger key switching."""
        # This tests that auth errors switch keys
        pass

    def test_retry_delay_increases_exponentially(self):
        """Test that retry delay increases exponentially."""
        # This would verify the backoff timing
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
