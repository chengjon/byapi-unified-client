"""
Configuration management for the Byapi Stock API Client.

This module handles:
- Loading environment variables from .env file
- Managing license key configuration
- License key health tracking and rotation
- Client configuration settings
"""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class LicenseKeyHealth:
    """Tracks the health status of a single license key."""

    key: str
    consecutive_failures: int = 0
    total_failures: int = 0
    status: str = "healthy"  # healthy | faulty | invalid
    last_failed_timestamp: Optional[datetime] = None
    last_failed_reason: Optional[str] = None

    def mark_failure(self, reason: str) -> str:
        """
        Record a failure, update status, return new status.

        Args:
            reason: Description of why the request failed

        Returns:
            New status: "healthy", "faulty", or "invalid"
        """
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failed_timestamp = datetime.now()
        self.last_failed_reason = reason

        if self.total_failures >= 10:
            self.status = "invalid"
            logger.warning(
                f"License key {self._mask_key()} permanently disabled "
                f"after {self.total_failures} total failures"
            )
        elif self.consecutive_failures >= 5:
            self.status = "faulty"
            logger.warning(
                f"License key {self._mask_key()} marked faulty "
                f"after {self.consecutive_failures} consecutive failures"
            )

        return self.status

    def mark_success(self) -> None:
        """Reset consecutive counter on successful API call."""
        # Invalid keys don't recover automatically - they stay invalid for the session
        if self.status == "invalid":
            return

        if self.consecutive_failures > 0:
            logger.debug(
                f"License key {self._mask_key()} recovered after "
                f"{self.consecutive_failures} consecutive failures"
            )
        self.consecutive_failures = 0
        self.status = "healthy"

    @property
    def is_usable(self) -> bool:
        """Returns True if key can be used for API calls."""
        return self.status in ["healthy", "faulty"]

    @property
    def is_permanently_disabled(self) -> bool:
        """Returns True if key should never be used again this session."""
        return self.status == "invalid"

    def _mask_key(self) -> str:
        """Return masked version of key for logging (first 8 chars + ...)."""
        if len(self.key) > 8:
            return f"{self.key[:8]}..."
        return "***"


class KeyRotationManager:
    """
    Manages license key lifecycle and automatic failover.

    Features:
    - Tracks health of each key (consecutive and total failures)
    - Automatic status transitions (healthy → faulty → invalid)
    - Rotates to next healthy key on failure
    - Session-scoped state (resets on process restart)
    """

    def __init__(self, license_keys: List[str]):
        """
        Initialize key rotation manager.

        Args:
            license_keys: List of license keys (comma-separated from env)
        """
        # keys is now a dict mapping key string to LicenseKeyHealth
        self.keys = {
            key.strip(): LicenseKeyHealth(key=key.strip())
            for key in license_keys
            if key.strip()
        }
        # For iteration order, keep a list of key strings
        self._key_list = list(self.keys.keys())
        self.current_index = 0

        logger.info(f"KeyRotationManager initialized with {len(self.keys)} key(s)")

    def get_next_key(self) -> str:
        """
        Get next usable license key.

        Prefers healthy keys over faulty, but will use faulty if no healthy keys remain.
        As a last resort, will return an invalid key if all keys are invalid.

        Returns:
            A license key (healthy, faulty, or invalid as last resort)

        Raises:
            ByapiError: If no keys are configured at all
        """
        from byapi_exceptions import ByapiError

        if not self.keys:
            raise ByapiError("No license keys configured")

        # First, try to find a healthy key
        healthy_keys = [k for k in self._key_list if self.keys[k].status == "healthy"]
        if healthy_keys:
            # Round-robin through healthy keys
            key = healthy_keys[self.current_index % len(healthy_keys)]
            self.current_index = (self.current_index + 1) % len(self._key_list)
            return key

        # No healthy keys, try faulty (still usable)
        faulty_keys = [k for k in self._key_list if self.keys[k].status == "faulty"]
        if faulty_keys:
            key = faulty_keys[self.current_index % len(faulty_keys)]
            self.current_index = (self.current_index + 1) % len(self._key_list)
            return key

        # No healthy or faulty keys, return an invalid key as last resort
        # This allows the caller to attempt the request and get proper error handling
        invalid_keys = [k for k in self._key_list if self.keys[k].status == "invalid"]
        if invalid_keys:
            key = invalid_keys[self.current_index % len(invalid_keys)]
            self.current_index = (self.current_index + 1) % len(self._key_list)
            logger.warning(
                f"All available keys are invalid. Returning {key[:8]}... as last resort."
            )
            return key

        # This should never happen if keys are initialized
        raise ByapiError("No license keys available")

    def mark_key_failure(self, key: str, reason: str) -> str:
        """
        Mark key as failed and return new status.

        Args:
            key: The license key that failed
            reason: Reason for failure

        Returns:
            New status: "healthy", "faulty", or "invalid"
        """
        if key not in self.keys:
            logger.warning(f"Unknown key marked as failed: {key[:8]}...")
            return "unknown"

        health = self.keys[key]
        new_status = health.mark_failure(reason)

        if new_status == "faulty":
            logger.warning(f"Switching from {health.key[:8]}... to next key")
            self.current_index = (self.current_index + 1) % len(self.keys)

        return new_status

    def mark_key_success(self, key: str) -> None:
        """
        Mark key as successful.

        Args:
            key: The license key that succeeded
        """
        if key not in self.keys:
            return

        self.keys[key].mark_success()

    def get_health_status(self, mask_keys: bool = True) -> List[LicenseKeyHealth]:
        """
        Get health status of all keys.

        Args:
            mask_keys: If True, mask the key values for privacy (default True)

        Returns:
            List of LicenseKeyHealth objects for each key
        """
        health_list = list(self.keys.values())

        if mask_keys:
            # Create copies with masked keys
            masked_health = []
            for health in health_list:
                # Create a copy with masked key
                masked = LicenseKeyHealth(
                    key=health._mask_key(),
                    consecutive_failures=health.consecutive_failures,
                    total_failures=health.total_failures,
                    status=health.status,
                    last_failed_timestamp=health.last_failed_timestamp,
                    last_failed_reason=health.last_failed_reason,
                )
                masked_health.append(masked)
            return masked_health

        return health_list


class ByapiConfig:
    """
    Main configuration class for Byapi client.

    Loads settings from environment variables with sensible defaults.
    """

    def __init__(self):
        """Initialize configuration from environment variables."""
        # License key(s) - required
        licence_str = os.getenv("BYAPI_LICENCE", "")
        if not licence_str:
            raise ValueError(
                "BYAPI_LICENCE environment variable not set. "
                "Please create a .env file with: BYAPI_LICENCE=your-key-here"
            )

        self.license_keys = [k.strip() for k in licence_str.split(",") if k.strip()]
        if not self.license_keys:
            raise ValueError("No valid license keys found in BYAPI_LICENCE")

        # Base URL - default to HTTP but can be overridden
        self.base_url = os.getenv(
            "BYAPI_BASE_URL", "http://api.biyingapi.com"
        )

        # HTTPS variant
        self.https_base_url = os.getenv(
            "BYAPI_HTTPS_BASE_URL", "https://api.biyingapi.com"
        )

        # Request timeout in seconds
        self.timeout = int(os.getenv("BYAPI_TIMEOUT", "30"))

        # Logging level
        self.log_level = os.getenv("BYAPI_LOG_LEVEL", "INFO")

        # Retry configuration
        self.max_retries = int(os.getenv("BYAPI_MAX_RETRIES", "5"))
        self.retry_base_delay = float(os.getenv("BYAPI_RETRY_BASE_DELAY", "0.1"))
        self.retry_max_delay = float(os.getenv("BYAPI_RETRY_MAX_DELAY", "30"))

        # License key health thresholds
        self.consecutive_failure_threshold = int(
            os.getenv("BYAPI_CONSECUTIVE_FAILURES", "5")
        )
        self.total_failure_threshold = int(
            os.getenv("BYAPI_TOTAL_FAILURES", "10")
        )

        # Initialize key rotation manager
        self.key_manager = KeyRotationManager(self.license_keys)

        logger.info(
            f"ByapiConfig initialized: "
            f"url={self.base_url}, "
            f"timeout={self.timeout}s, "
            f"keys={len(self.license_keys)}"
        )

    def get_license_key(self) -> str:
        """Get the next usable license key."""
        return self.key_manager.get_next_key()

    def get_license_health(self, mask_keys: bool = True) -> List[LicenseKeyHealth]:
        """
        Get health status of all license keys.

        Args:
            mask_keys: If True, mask the key values for privacy (default True)

        Returns:
            List of LicenseKeyHealth objects for each key
        """
        return self.key_manager.get_health_status(mask_keys=mask_keys)

    @staticmethod
    def get_config() -> "ByapiConfig":
        """
        Get or create singleton configuration instance.

        Returns:
            ByapiConfig instance
        """
        if not hasattr(ByapiConfig, "_instance"):
            ByapiConfig._instance = ByapiConfig()
        return ByapiConfig._instance


# Create global config instance
config = ByapiConfig.get_config()
