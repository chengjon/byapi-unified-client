"""
Custom exceptions for the Byapi Stock API Client.

This module defines the exception hierarchy used throughout the Byapi client library.
All exceptions inherit from ByapiError for easy catching of library-specific errors.
"""

from typing import Optional


class ByapiError(Exception):
    """Base exception for all Byapi client errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize Byapi error.

        Args:
            message: Human-readable error message
            error_code: API error code or error type identifier
            status_code: HTTP status code (if applicable)
            cause: Original exception that caused this error (for debugging)
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.cause = cause
        super().__init__(message)


class AuthenticationError(ByapiError):
    """
    Raised when API authentication fails.

    Common causes:
    - Invalid or expired license key
    - Missing license key
    - License key has insufficient permissions
    - License key is rate limited or blocked
    """

    pass


class DataError(ByapiError):
    """
    Raised when API response data is invalid or unparseable.

    Common causes:
    - Invalid JSON in API response
    - Missing required fields in response
    - Type mismatch in response fields
    - Corrupted data transmission
    """

    pass


class NotFoundError(ByapiError):
    """
    Raised when requested resource doesn't exist.

    Common causes:
    - Invalid stock code
    - Delisted stock
    - Non-existent company data
    - No announcements for given period
    """

    pass


class RateLimitError(ByapiError):
    """
    Raised when API rate limit is exceeded.

    Common causes:
    - Too many requests in short period
    - License key quota exhausted
    - Concurrent request limits exceeded

    Note: The client will automatically retry on rate limit errors with exponential backoff.
    This exception is raised only if retries are exhausted.
    """

    pass


class NetworkError(ByapiError):
    """
    Raised when network communication fails.

    Common causes:
    - Connection timeout
    - DNS resolution failure
    - Server unavailable (5xx errors)
    - Network unreachable
    - TLS/SSL errors
    """

    pass
