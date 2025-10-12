"""Custom HTTP exceptions with standardized error responses."""

from typing import Any

from fastapi import HTTPException, status


class StandardHTTPException(HTTPException):
    """Base class for standardized HTTP exceptions."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize standard HTTP exception.

        Args:
            status_code: HTTP status code
            error_code: Internal error code for client handling
            message: Human-readable error message
            details: Additional error details (optional)
        """
        detail: dict[str, Any] = {
            "error_code": error_code,
            "message": message,
        }
        if details:
            detail["details"] = details

        super().__init__(status_code=status_code, detail=detail)


# Authentication Errors
class UnauthorizedError(StandardHTTPException):
    """401 Unauthorized error."""

    def __init__(
        self, message: str = "Not authenticated", details: dict[str, Any] | None = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            message=message,
            details=details,
        )


class InvalidCredentialsError(StandardHTTPException):
    """401 Invalid credentials error."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
            message=message,
        )


class ForbiddenError(StandardHTTPException):
    """403 Forbidden error."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            message=message,
            details=details,
        )


# Resource Errors
class NotFoundError(StandardHTTPException):
    """404 Not Found error."""

    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        details = None
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
            details = {"resource": resource, "identifier": identifier}

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
            details=details,
        )


class ConflictError(StandardHTTPException):
    """409 Conflict error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            details=details,
        )


class AlreadyExistsError(ConflictError):
    """409 Resource already exists error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} already exists",
            details={"resource": resource, "identifier": identifier},
        )


# Validation Errors
class ValidationError(StandardHTTPException):
    """422 Validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


# Business Logic Errors
class BusinessRuleError(StandardHTTPException):
    """400 Business rule violation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_RULE_VIOLATION",
            message=message,
            details=details,
        )


# External Service Errors
class ExternalServiceError(StandardHTTPException):
    """502 External service error."""

    def __init__(self, service: str, message: str | None = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            message=message or f"Error communicating with {service}",
            details={"service": service},
        )


# Rate Limiting
class RateLimitExceededError(StandardHTTPException):
    """429 Rate limit exceeded error."""

    def __init__(self, retry_after: int | None = None):
        details = {"retry_after": retry_after} if retry_after else None
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded. Please try again later.",
            details=details,
        )
