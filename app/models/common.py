"""Common schemas for API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """Pagination metadata."""

    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Current offset")
    has_more: bool = Field(..., description="Whether there are more items")


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""

    field: str = Field(..., description="Field name that caused the error")
    message: str = Field(..., description="Error message")


class ErrorInfo(BaseModel):
    """Error information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Validation error details")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorInfo


# Helper functions for creating error responses
def create_error_response(
    code: str, message: str, details: Optional[List[Dict[str, str]]] = None
) -> ErrorResponse:
    """Create a standard error response."""
    error_details = None
    if details:
        error_details = [ErrorDetail(**detail) for detail in details]

    return ErrorResponse(error=ErrorInfo(code=code, message=message, details=error_details))


def validation_error_response(details: List[Dict[str, str]]) -> ErrorResponse:
    """Create a validation error response."""
    return create_error_response(code="VALIDATION_ERROR", message="Validation failed", details=details)


def unauthorized_error_response(message: str = "Authentication required") -> ErrorResponse:
    """Create an unauthorized error response."""
    return create_error_response(code="UNAUTHORIZED", message=message)


def not_found_error_response(message: str = "Resource not found") -> ErrorResponse:
    """Create a not found error response."""
    return create_error_response(code="NOT_FOUND", message=message)


def conflict_error_response(message: str) -> ErrorResponse:
    """Create a conflict error response."""
    return create_error_response(code="CONFLICT", message=message)


class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    data: List[Any] = Field(..., description="List of items")
    pagination: Pagination = Field(..., description="Pagination metadata")


def create_paginated_response(
    data: List[Any], total: int, limit: int, offset: int
) -> Dict[str, Any]:
    """Create a paginated response."""
    has_more = offset + len(data) < total
    return {
        "items": data,  # Use 'items' for compatibility with tests
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }
