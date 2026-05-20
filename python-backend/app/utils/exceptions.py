from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class SkillTradeException(Exception):
    """Base exception class for SkillTrade application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(SkillTradeException):
    """Authentication related errors"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR",
            details=details
        )


class AuthorizationError(SkillTradeException):
    """Authorization related errors"""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHZ_ERROR",
            details=details
        )


class ValidationError(SkillTradeException):
    """Validation related errors"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(SkillTradeException):
    """Resource not found errors"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class ConflictError(SkillTradeException):
    """Conflict errors (e.g., duplicate resources)"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details=details
        )


class RateLimitError(SkillTradeException):
    """Rate limiting errors"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT",
            details=details
        )


class DatabaseError(SkillTradeException):
    """Database related errors"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(SkillTradeException):
    """External service integration errors"""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if details is None:
            details = {}
        
        if service_name:
            details["service_name"] = service_name
        
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class FileUploadError(SkillTradeException):
    """File upload related errors"""
    
    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR",
            details=details
        )


class WebSocketError(SkillTradeException):
    """WebSocket related errors"""
    
    def __init__(
        self,
        message: str = "WebSocket error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="WEBSOCKET_ERROR",
            details=details
        )


class BusinessLogicError(SkillTradeException):
    """Business logic validation errors"""
    
    def __init__(
        self,
        message: str = "Business logic error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


# Custom exception factory functions
def create_user_not_found_error(user_id: str) -> NotFoundError:
    """Create a user not found error"""
    return NotFoundError(
        message="User not found",
        resource_type="User",
        resource_id=user_id
    )


def create_swap_not_found_error(swap_id: str) -> NotFoundError:
    """Create a swap request not found error"""
    return NotFoundError(
        message="Swap request not found",
        resource_type="SwapRequest",
        resource_id=swap_id
    )


def create_message_not_found_error(message_id: str) -> NotFoundError:
    """Create a message not found error"""
    return NotFoundError(
        message="Message not found",
        resource_type="Message",
        resource_id=message_id
    )


def create_review_not_found_error(review_id: str) -> NotFoundError:
    """Create a review not found error"""
    return NotFoundError(
        message="Review not found",
        resource_type="Review",
        resource_id=review_id
    )


def create_email_already_exists_error(email: str) -> ConflictError:
    """Create an email already exists error"""
    return ConflictError(
        message="Email already registered",
        details={"email": email}
    )


def create_invalid_swap_status_error(current_status: str, requested_status: str) -> BusinessLogicError:
    """Create an invalid swap status transition error"""
    return BusinessLogicError(
        message=f"Cannot transition swap from {current_status} to {requested_status}",
        details={
            "current_status": current_status,
            "requested_status": requested_status
        }
    )


def create_skill_not_found_error(skill_name: str) -> NotFoundError:
    """Create a skill not found error"""
    return NotFoundError(
        message="Skill not found",
        resource_type="Skill",
        resource_id=skill_name
    )


def create_location_required_error() -> ValidationError:
    """Create a location required error"""
    return ValidationError(
        message="Location is required for this operation",
        details={"required_field": "location"}
    )


def create_invalid_coordinates_error() -> ValidationError:
    """Create an invalid coordinates error"""
    return ValidationError(
        message="Invalid geographic coordinates",
        details={
            "format": "[longitude, latitude]",
            "longitude_range": "[-180, 180]",
            "latitude_range": "[-90, 90]"
        }
    )


def create_file_too_large_error(max_size: int) -> FileUploadError:
    """Create a file too large error"""
    return FileUploadError(
        message=f"File size exceeds maximum allowed size",
        details={"max_size_bytes": max_size}
    )


def create_invalid_file_type_error(allowed_types: list) -> FileUploadError:
    """Create an invalid file type error"""
    return FileUploadError(
        message="File type not allowed",
        details={"allowed_types": allowed_types}
    )


def create_unauthorized_swap_access_error(swap_id: str, user_id: str) -> AuthorizationError:
    """Create an unauthorized swap access error"""
    return AuthorizationError(
        message="Access denied to swap request",
        details={
            "swap_id": swap_id,
            "user_id": user_id,
            "reason": "User is not a participant in this swap"
        }
    )


def create_swap_already_exists_error(sender_id: str, receiver_id: str) -> ConflictError:
    """Create a swap already exists error"""
    return ConflictError(
        message="Active swap request already exists between these users",
        details={
            "sender_id": sender_id,
            "receiver_id": receiver_id
        }
    )


def create_review_already_exists_error(swap_id: str, user_id: str) -> ConflictError:
    """Create a review already exists error"""
    return ConflictError(
        message="Review already exists for this swap",
        details={
            "swap_id": swap_id,
            "user_id": user_id
        }
    )


def create_swap_not_completed_error(swap_id: str) -> BusinessLogicError:
    """Create a swap not completed error"""
    return BusinessLogicError(
        message="Swap must be completed before reviewing",
        details={"swap_id": swap_id}
    )
