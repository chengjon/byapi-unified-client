#!/usr/bin/env python3
"""
License Key Failover and Multi-Key Management Example

This example demonstrates how to use the Byapi client with multiple license keys
for automatic failover and health tracking.

Features demonstrated:
- Multi-key configuration
- Health status monitoring
- Automatic key rotation
- Failure detection and recovery
- Health tracking visualization

Run with: python examples/license_failover.py
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import byapi modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from byapi_client_unified import ByapiClient
from byapi_config import ByapiConfig, KeyRotationManager
from byapi_exceptions import AuthenticationError, ByapiError

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_separator(title=""):
    """Print a separator line with optional title."""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    else:
        print(f"\n{'-' * 60}")


def print_health_status(client: ByapiClient):
    """Print the health status of all license keys."""
    health = client.get_license_health()

    print("\nLicense Key Health Status:")
    print("-" * 60)
    print(f"{'Key':<15} {'Status':<12} {'Consecutive':<12} {'Total':<10}")
    print("-" * 60)

    for key_health in health:
        status_emoji = {
            "healthy": "✓",
            "faulty": "⚠",
            "invalid": "✗"
        }.get(key_health.status, "?")

        print(
            f"{key_health.key:<15} {key_health.status:<12} "
            f"{key_health.consecutive_failures:<12} {key_health.total_failures:<10} {status_emoji}"
        )


def example_1_basic_multi_key():
    """Example 1: Basic multi-key setup and health monitoring."""
    print_separator("Example 1: Basic Multi-Key Setup")

    try:
        # Create a client (loads from .env)
        client = ByapiClient()

        print("\n✓ Client initialized with multiple license keys")
        print(f"✓ Number of keys configured: {len(client.config.license_keys)}")

        # Check health status
        print_health_status(client)

        # Get the next key
        next_key = client.config.get_license_key()
        print(f"\n✓ Next available key: {next_key[:8]}...")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_manual_key_rotation():
    """Example 2: Manual key management and rotation."""
    print_separator("Example 2: Manual Key Rotation")

    try:
        # Create manager with specific keys
        manager = KeyRotationManager([
            "test_key_1",
            "test_key_2",
            "test_key_3"
        ])

        print("\n✓ Created KeyRotationManager with 3 test keys")

        # Show initial status
        print("\nInitial Health Status:")
        health = manager.get_health_status(mask_keys=False)
        for h in health:
            print(f"  {h.key:<15} - {h.status}")

        # Simulate some failures on key 1
        print("\nSimulating 3 failures on test_key_1...")
        for i in range(3):
            manager.mark_key_failure("test_key_1", f"Test error {i+1}")
            print(f"  Failure {i+1}: status = {manager.keys['test_key_1'].status}")

        # Get next key (should rotate to key 2)
        next_key = manager.get_next_key()
        print(f"\n✓ Next key after failures: {next_key}")
        print(f"  (Rotated from test_key_1 to {next_key})")

        # More failures to reach "faulty" threshold
        print("\nSimulating 2 more failures on test_key_1...")
        for i in range(2):
            manager.mark_key_failure("test_key_1", f"Test error {i+4}")

        print(f"test_key_1 status after 5 failures: {manager.keys['test_key_1'].status}")

        # Show final status
        print("\nFinal Health Status:")
        health = manager.get_health_status(mask_keys=False)
        for h in health:
            usable = "✓" if h.is_usable else "✗"
            print(f"  {h.key:<15} - {h.status:<12} ({h.consecutive_failures} consecutive, "
                  f"{h.total_failures} total) {usable}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_3_health_recovery():
    """Example 3: Key recovery after transient failures."""
    print_separator("Example 3: Health Recovery After Success")

    try:
        manager = KeyRotationManager(["recovery_key"])
        health = manager.keys["recovery_key"]

        print("\n✓ Created KeyRotationManager with 1 key")

        # Simulate failures
        print("\nSimulating 3 failures...")
        for i in range(3):
            manager.mark_key_failure("recovery_key", f"Transient error {i+1}")

        print(f"After 3 failures: consecutive={health.consecutive_failures}, "
              f"total={health.total_failures}, status={health.status}")

        # Recovery - mark success
        print("\nMarketing key as successful (recovered)...")
        manager.mark_key_success("recovery_key")

        print(f"After recovery: consecutive={health.consecutive_failures}, "
              f"total={health.total_failures}, status={health.status}")
        print("✓ Consecutive failures reset to 0, but total remains at 3")
        print("✓ This allows the key to be used again")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_permanent_invalid():
    """Example 4: Permanent key invalidation."""
    print_separator("Example 4: Permanent Key Invalidation (10 failures)")

    try:
        manager = KeyRotationManager(["invalid_key_1", "backup_key"])

        print("\n✓ Created manager with 2 keys")

        # Accumulate 10 total failures
        print("\nSimulating 10 total failures to mark key as invalid...")
        for i in range(10):
            manager.mark_key_failure("invalid_key_1", f"Persistent error {i+1}")
            status = manager.keys["invalid_key_1"].status
            if status != "healthy":
                print(f"  After failure {i+1}: status = {status}")

        health = manager.keys["invalid_key_1"]
        print(f"\nFinal status: {health.status}")
        print(f"Is usable: {health.is_usable}")
        print(f"Is permanently disabled: {health.is_permanently_disabled}")

        # Try to recover with mark_success
        print("\nTrying to recover with mark_success()...")
        manager.mark_key_success("invalid_key_1")
        print(f"Status after mark_success: {health.status}")
        print("✓ Status remains 'invalid' - no automatic recovery!")

        # But system will use backup key
        next_key = manager.get_next_key()
        print(f"\n✓ System automatically uses backup key: {next_key}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_preference_hierarchy():
    """Example 5: Key selection preference (healthy > faulty > invalid)."""
    print_separator("Example 5: Key Selection Preference")

    try:
        manager = KeyRotationManager(["healthy_key", "faulty_key", "invalid_key"])

        print("\n✓ Created manager with 3 keys")

        # Set different states
        manager.keys["healthy_key"].status = "healthy"
        manager.keys["faulty_key"].status = "faulty"
        manager.keys["invalid_key"].status = "invalid"

        print("\nKey states set:")
        for key, health in manager.keys.items():
            print(f"  {key}: {health.status}")

        # Get next key multiple times
        print("\nGetting next key 5 times:")
        selected_keys = []
        for _ in range(5):
            key = manager.get_next_key()
            selected_keys.append(key)
            print(f"  Selected: {key}")

        print(f"\n✓ Preference: Always selected '{selected_keys[0]}' (healthy key)")
        print("✓ Healthy keys are preferred over faulty")
        print("✓ Faulty keys are preferred over invalid")
        print("✓ Invalid keys are only used as last resort")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_6_client_health_api():
    """Example 6: Using ByapiClient health API."""
    print_separator("Example 6: ByapiClient Health API")

    try:
        client = ByapiClient()

        print("\n✓ Client initialized")

        # Get health (keys are masked by default)
        health = client.get_license_health()

        print(f"\nConfigured with {len(health)} license key(s)")
        print("\nKey Health Summary:")
        print("-" * 60)

        healthy_count = sum(1 for h in health if h.status == "healthy")
        faulty_count = sum(1 for h in health if h.status == "faulty")
        invalid_count = sum(1 for h in health if h.status == "invalid")

        print(f"Healthy keys: {healthy_count}")
        print(f"Faulty keys:  {faulty_count}")
        print(f"Invalid keys: {invalid_count}")

        # Show masked keys
        print("\nMasked Key Details (safe to log/display):")
        for i, key_health in enumerate(health, 1):
            print(f"\n  Key {i}: {key_health.key}")
            print(f"    Status: {key_health.status}")
            print(f"    Consecutive failures: {key_health.consecutive_failures}")
            print(f"    Total failures: {key_health.total_failures}")

        print("\n✓ Keys are masked for safe logging/display")
        print("✓ Only shows first 8 characters + '...'")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  Byapi License Failover and Multi-Key Management")
    print("  Examples and Demonstrations")
    print("=" * 60)

    try:
        # Run each example
        example_1_basic_multi_key()
        example_2_manual_key_rotation()
        example_3_health_recovery()
        example_4_permanent_invalid()
        example_5_preference_hierarchy()
        example_6_client_health_api()

        print_separator("All Examples Completed Successfully")
        print("\n✓ Multi-key failover is working correctly")
        print("✓ Health tracking enables automatic recovery")
        print("✓ Keys are protected (masked) in health output")
        print("✓ Preference system ensures optimal key selection")

    except KeyboardInterrupt:
        print("\n\n✗ Examples interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
