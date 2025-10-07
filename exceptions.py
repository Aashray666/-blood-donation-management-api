"""
Custom exception classes for the Blood Donation Management API.
Provides structured error handling with detailed error information.
"""

from typing import Optional, Dict, Any
from fastapi import status


class BloodDonationAPIError(Exception):
    """Base exception class for all Blood Donation API errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            http_status_code: HTTP status code for the error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.http_status_code = http_status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(BloodDonationAPIError):
    """Exception raised for data validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        validation_details = details or {}
        if field:
            validation_details["field"] = field
        if value is not None:
            validation_details["invalid_value"] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=validation_details,
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class NotFoundError(BloodDonationAPIError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if resource_id is not None:
            message = f"{resource_type} with ID {resource_id} not found"
            resource_details = {"resource_type": resource_type, "resource_id": str(resource_id)}
        else:
            message = f"{resource_type} not found"
            resource_details = {"resource_type": resource_type}
        
        if details:
            resource_details.update(details)
        
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=resource_details,
            http_status_code=status.HTTP_404_NOT_FOUND
        )


class DuplicateResourceError(BloodDonationAPIError):
    """Exception raised when attempting to create a duplicate resource."""
    
    def __init__(
        self,
        resource_type: str,
        field: str,
        value: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} with {field} '{value}' already exists"
        duplicate_details = {
            "resource_type": resource_type,
            "duplicate_field": field,
            "duplicate_value": str(value)
        }
        
        if details:
            duplicate_details.update(details)
        
        super().__init__(
            message=message,
            error_code="DUPLICATE_RESOURCE",
            details=duplicate_details,
            http_status_code=status.HTTP_409_CONFLICT
        )


class BusinessLogicError(BloodDonationAPIError):
    """Exception raised for business logic violations."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        business_details = details or {}
        if operation:
            business_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=business_details,
            http_status_code=status.HTTP_400_BAD_REQUEST
        )


class DatabaseError(BloodDonationAPIError):
    """Exception raised for database operation errors."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        db_details = details or {}
        if operation:
            db_details["operation"] = operation
        if table:
            db_details["table"] = table
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=db_details,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalServiceError(BloodDonationAPIError):
    """Exception raised for external service integration errors."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        service_details = details or {}
        if service:
            service_details["service"] = service
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=service_details,
            http_status_code=status.HTTP_502_BAD_GATEWAY
        )


class AuthenticationError(BloodDonationAPIError):
    """Exception raised for authentication failures."""
    
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details or {},
            http_status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(BloodDonationAPIError):
    """Exception raised for authorization failures."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        auth_details = details or {}
        if resource:
            auth_details["resource"] = resource
        if action:
            auth_details["action"] = action
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=auth_details,
            http_status_code=status.HTTP_403_FORBIDDEN
        )


class RateLimitError(BloodDonationAPIError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        rate_details = details or {}
        if limit:
            rate_details["limit"] = limit
        if window:
            rate_details["window"] = window
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=rate_details,
            http_status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ConfigurationError(BloodDonationAPIError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        config_details = details or {}
        if config_key:
            config_details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=config_details,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Convenience functions for common error scenarios
def donor_not_found(donor_id: int) -> NotFoundError:
    """Create a NotFoundError for a donor."""
    return NotFoundError("Donor", donor_id)


def blood_request_not_found(request_id: int) -> NotFoundError:
    """Create a NotFoundError for a blood request."""
    return NotFoundError("Blood Request", request_id)


def duplicate_donor(field: str, value: Any) -> DuplicateResourceError:
    """Create a DuplicateResourceError for a donor."""
    return DuplicateResourceError("Donor", field, value)


def duplicate_blood_request(field: str, value: Any) -> DuplicateResourceError:
    """Create a DuplicateResourceError for a blood request."""
    return DuplicateResourceError("Blood Request", field, value)


def invalid_blood_group(blood_group: str) -> ValidationError:
    """Create a ValidationError for invalid blood group."""
    return ValidationError(
        message=f"Invalid blood group: {blood_group}. Must be one of: A+, A-, B+, B-, AB+, AB-, O+, O-",
        field="blood_group",
        value=blood_group,
        details={"valid_values": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]}
    )


def invalid_urgency_level(urgency: str) -> ValidationError:
    """Create a ValidationError for invalid urgency level."""
    return ValidationError(
        message=f"Invalid urgency level: {urgency}. Must be one of: Low, Medium, High, Critical",
        field="urgency",
        value=urgency,
        details={"valid_values": ["Low", "Medium", "High", "Critical"]}
    )


def invalid_status(status_value: str) -> ValidationError:
    """Create a ValidationError for invalid status."""
    return ValidationError(
        message=f"Invalid status: {status_value}. Must be one of: Active, Fulfilled",
        field="status",
        value=status_value,
        details={"valid_values": ["Active", "Fulfilled"]}
    )