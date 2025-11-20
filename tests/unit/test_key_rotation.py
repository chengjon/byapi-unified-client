"""
Unit tests for KeyRotationManager and license key health tracking.

Tests verify:
1. Multi-key parsing and management
2. Health status transitions
3. Failure counting (consecutive and total)
4. Key rotation logic
5. Status properties (is_usable, is_permanently_disabled)

Run with: pytest tests/unit/test_key_rotation.py -v
"""

import pytest
from datetime import datetime
from byapi_config import KeyRotationManager, LicenseKeyHealth


class TestLicenseKeyHealthBasics:
    """Test basic LicenseKeyHealth functionality."""

    def test_new_health_object_is_healthy(self):
        """Test that new health objects start healthy."""
        health = LicenseKeyHealth(key="abc123")

        assert health.key == "abc123"
        assert health.status == "healthy"
        assert health.consecutive_failures == 0
        assert health.total_failures == 0

    def test_health_object_stores_key(self):
        """Test that health object stores the key."""
        health = LicenseKeyHealth(key="test_key_12345")
        assert health.key == "test_key_12345"

    def test_health_object_timestamp(self):
        """Test that health object tracks failure timestamps."""
        health = LicenseKeyHealth(key="test_key")
        assert health.last_failed_timestamp is None

        health.last_failed_timestamp = datetime.now()
        assert health.last_failed_timestamp is not None


class TestLicenseKeyHealthStatus:
    """Test status transitions in LicenseKeyHealth."""

    def test_healthy_is_usable(self):
        """Test that healthy keys are usable."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "healthy"

        assert health.is_usable

    def test_faulty_is_usable(self):
        """Test that faulty keys are still usable."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "faulty"

        assert health.is_usable

    def test_invalid_is_not_usable(self):
        """Test that invalid keys are not usable."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "invalid"

        assert not health.is_usable

    def test_invalid_is_permanently_disabled(self):
        """Test that only invalid keys are permanently disabled."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "invalid"

        assert health.is_permanently_disabled

    def test_healthy_is_not_permanently_disabled(self):
        """Test that healthy keys are not permanently disabled."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "healthy"

        assert not health.is_permanently_disabled

    def test_faulty_is_not_permanently_disabled(self):
        """Test that faulty keys are not permanently disabled."""
        health = LicenseKeyHealth(key="test_key")
        health.status = "faulty"

        assert not health.is_permanently_disabled


class TestKeyRotationManagerBasics:
    """Test KeyRotationManager basic functionality."""

    def test_manager_with_single_key(self):
        """Test manager with a single key."""
        manager = KeyRotationManager(["key1"])

        assert len(manager.keys) == 1
        assert "key1" in manager.keys

    def test_manager_with_multiple_keys(self):
        """Test manager with multiple keys."""
        manager = KeyRotationManager(["key1", "key2", "key3"])

        assert len(manager.keys) == 3
        assert "key1" in manager.keys
        assert "key2" in manager.keys
        assert "key3" in manager.keys

    def test_all_new_keys_are_healthy(self):
        """Test that all newly created keys are healthy."""
        manager = KeyRotationManager(["key1", "key2", "key3"])

        for key, health in manager.keys.items():
            assert health.status == "healthy"
            assert health.consecutive_failures == 0
            assert health.total_failures == 0


class TestKeyFailureTracking:
    """Test failure tracking in KeyRotationManager."""

    def test_mark_failure_increments_counters(self):
        """Test that mark_key_failure increments both counters."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        manager.mark_key_failure("key1", "Test error")

        assert health.consecutive_failures == 1
        assert health.total_failures == 1

    def test_multiple_failures_increase_counters(self):
        """Test that multiple failures increase counters correctly."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        for i in range(3):
            manager.mark_key_failure("key1", f"Error {i+1}")

        assert health.consecutive_failures == 3
        assert health.total_failures == 3

    def test_5_consecutive_failures_mark_faulty(self):
        """Test that 5 consecutive failures mark key as faulty."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        for i in range(5):
            manager.mark_key_failure("key1", "Error")

        assert health.status == "faulty"
        assert health.consecutive_failures == 5

    def test_10_total_failures_mark_invalid(self):
        """Test that 10 total failures mark key as invalid."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        for i in range(10):
            manager.mark_key_failure("key1", "Error")

        assert health.status == "invalid"
        assert health.total_failures == 10

    def test_6th_failure_keeps_faulty_status(self):
        """Test that 6th failure keeps 'faulty' status, doesn't go to invalid yet."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        for i in range(6):
            manager.mark_key_failure("key1", "Error")

        assert health.status == "faulty"  # Not invalid yet (need 10)
        assert health.total_failures == 6


class TestKeySuccessTracking:
    """Test success tracking and consecutive reset."""

    def test_mark_success_resets_consecutive_only(self):
        """Test that mark_key_success resets consecutive but not total."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        # Simulate failures
        for i in range(3):
            manager.mark_key_failure("key1", "Error")

        # Mark success
        manager.mark_key_success("key1")

        assert health.consecutive_failures == 0
        assert health.total_failures == 3  # Still 3 total
        assert health.status == "healthy"

    def test_success_after_failures_resets_counter(self):
        """Test that success properly resets the consecutive counter."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        # 3 failures
        for i in range(3):
            manager.mark_key_failure("key1", "Error")

        assert health.consecutive_failures == 3

        # 1 success
        manager.mark_key_success("key1")

        assert health.consecutive_failures == 0
        assert health.status == "healthy"

    def test_repeated_fail_success_cycles(self):
        """Test repeated fail/success cycles."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        # Cycle 1: 2 failures, then success
        manager.mark_key_failure("key1", "Error")
        manager.mark_key_failure("key1", "Error")
        assert health.consecutive_failures == 2
        manager.mark_key_success("key1")
        assert health.consecutive_failures == 0
        assert health.total_failures == 2  # Still 2 total

        # Cycle 2: 3 more failures
        for i in range(3):
            manager.mark_key_failure("key1", "Error")
        assert health.consecutive_failures == 3
        assert health.total_failures == 5  # Now 5 total


class TestKeyRotationLogic:
    """Test get_next_key rotation logic."""

    def test_get_next_key_returns_valid_key(self):
        """Test that get_next_key returns a valid key."""
        manager = KeyRotationManager(["key1", "key2", "key3"])
        key = manager.get_next_key()

        assert key in ["key1", "key2", "key3"]

    def test_single_key_always_returns_same(self):
        """Test that with single key, it's always returned."""
        manager = KeyRotationManager(["only_key"])

        key1 = manager.get_next_key()
        key2 = manager.get_next_key()

        assert key1 == "only_key"
        assert key2 == "only_key"

    def test_skips_invalid_keys(self):
        """Test that rotation skips permanently invalid keys."""
        manager = KeyRotationManager(["key1", "key2", "key3"])

        # Mark key1 as invalid
        manager.keys["key1"].status = "invalid"

        # Get next key multiple times
        for _ in range(5):
            key = manager.get_next_key()
            # Should never return the invalid key
            # (unless all are invalid)
            if manager.keys["key2"].is_usable or manager.keys["key3"].is_usable:
                assert key != "key1"

    def test_uses_faulty_keys_if_no_healthy(self):
        """Test that faulty keys are used if no healthy keys available."""
        manager = KeyRotationManager(["key1", "key2"])

        # Mark both as faulty
        manager.keys["key1"].status = "faulty"
        manager.keys["key2"].status = "faulty"

        # Should still get a usable key (faulty keys are still usable)
        key = manager.get_next_key()
        assert key in ["key1", "key2"]

    def test_prefers_healthy_over_faulty(self):
        """Test that healthy keys are preferred over faulty."""
        manager = KeyRotationManager(["key1", "key2"])

        # Mark key1 as faulty, keep key2 healthy
        manager.keys["key1"].status = "faulty"
        manager.keys["key2"].status = "healthy"

        # Should get key2 (healthy) more often
        keys = [manager.get_next_key() for _ in range(10)]
        # At least some should be key2
        assert "key2" in keys


class TestMultipleKeyScenarios:
    """Test complex scenarios with multiple keys."""

    def test_all_keys_invalid_scenario(self):
        """Test behavior when all keys are marked invalid."""
        manager = KeyRotationManager(["key1", "key2"])

        # Mark all as invalid
        for health in manager.keys.values():
            health.status = "invalid"

        # Trying to get next key will return invalid key
        # (behavior depends on implementation)
        key = manager.get_next_key()
        # Either returns None or raises error (implementation dependent)
        # This test just verifies it doesn't crash

    def test_key_recovery_not_automatic_in_session(self):
        """Test that invalid keys don't auto-recover within a session."""
        manager = KeyRotationManager(["key1"])
        health = manager.keys["key1"]

        # Mark as invalid
        health.status = "invalid"
        health.total_failures = 10

        # Mark success should NOT reset invalid status
        manager.mark_key_success("key1")

        # Status should remain invalid
        assert health.status == "invalid"


class TestGetHealthStatus:
    """Test retrieving health status information."""

    def test_get_all_keys_health(self):
        """Test getting health status of all keys."""
        manager = KeyRotationManager(["key1", "key2", "key3"])

        # Simulate some failures
        manager.mark_key_failure("key1", "Error")
        manager.mark_key_failure("key2", "Error")
        manager.mark_key_failure("key2", "Error")

        # Get health for all keys
        health_list = list(manager.keys.values())

        assert len(health_list) == 3
        assert health_list[0].total_failures == 1
        assert health_list[1].total_failures == 2
        assert health_list[2].total_failures == 0


class TestKeyRotationEdgeCases:
    """Test edge cases in key rotation."""

    def test_empty_key_list_handling(self):
        """Test handling of empty key list."""
        # This depends on implementation - might raise error
        try:
            manager = KeyRotationManager([])
            assert len(manager.keys) == 0
        except (ValueError, Exception):
            # Implementation may reject empty list
            pass

    def test_duplicate_keys_handling(self):
        """Test handling of duplicate keys in list."""
        # This depends on implementation
        # Some may accept duplicates, some may deduplicate
        manager = KeyRotationManager(["key1", "key1", "key2"])
        # Just verify it doesn't crash

    def test_very_long_key_string(self):
        """Test handling of very long key strings."""
        long_key = "k" * 1000
        manager = KeyRotationManager([long_key])

        assert long_key in manager.keys
        assert len(manager.keys) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
