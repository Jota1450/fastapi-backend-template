"""
Standard API Response Model and Helper Functions

All API responses follow a consistent format with success, data, and message fields.
"""

from typing import Any, Optional

from pydantic import BaseModel
from sqlmodel import SQLModel


class StandardResponse(SQLModel):
    """
    Standard response model for all API endpoints.
    
    Attributes:
        success: Indicates if the operation was successful
        data: Response data (can be None)
        message: Descriptive message (optional)
    """
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200,
) -> tuple[StandardResponse, int]:
    """
    Create a successful response.
    
    Args:
        data: The response data
        message: Optional success message
        status_code: HTTP status code (default: 200)
    
    Returns:
        Tuple of (StandardResponse, status_code) for use with FastAPI Response
    """
    return StandardResponse(success=True, data=data, message=message), status_code


def error_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 400,
) -> tuple[StandardResponse, int]:
    """
    Create an error response.
    
    Args:
        message: Error message (required)
        data: Optional error data
        status_code: HTTP status code (default: 400)
    
    Returns:
        Tuple of (StandardResponse, status_code) for use with FastAPI Response
    """
    return StandardResponse(success=False, data=data, message=message), status_code

