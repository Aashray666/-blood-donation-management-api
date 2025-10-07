"""
Global exception handlers for the Blood Donation Management API.
Provides consistent error response formatting across all endpoints.
"""

import logging
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError as PydanticValidationError

from exceptions import BloodDonationAPIError

logger = logging.getLogger(__name__)


async def blood_donation_api_exception_handler(
    request: Request, 
    exc: BloodDonationAPIError
) -> JSONResponse:
    """
    Handle custom BloodDonationAPIError exceptions.
    
    Args:
        request: FastAPI request object
        exc: BloodDonationAPIError exception
        
    Returns:
        JSONResponse with structured error information
    """
    logger.error(
        f"BloodDonationAPIError occurred: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.http_status_code,
        content=exc.to_dict()
    )


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """
    Handle FastAPI HTTPException exceptions.
    
    Args:
        request: FastAPI request object
        exc: HTTPException
        
    Returns:
        JSONResponse with structured error information
    """
    logger.warning(
        f"HTTPException occurred: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = {
        "error": "HTTP_ERROR",
        "message": exc.detail,
        "details": {
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def starlette_http_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle Starlette HTTPException exceptions.
    
    Args:
        request: FastAPI request object
        exc: StarletteHTTPException
        
    Returns:
        JSONResponse with structured error information
    """
    logger.warning(
        f"StarletteHTTPException occurred: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = {
        "error": "HTTP_ERROR",
        "message": exc.detail,
        "details": {
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI RequestValidationError exceptions.
    
    Args:
        request: FastAPI request object
        exc: RequestValidationError
        
    Returns:
        JSONResponse with structured validation error information
    """
    logger.warning(
        f"Validation error occurred: {exc.errors()}",
        extra={
            "validation_errors": exc.errors(),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    error_response = {
        "error": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": {
            "validation_errors": formatted_errors,
            "error_count": len(formatted_errors)
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def pydantic_validation_exception_handler(
    request: Request, 
    exc: PydanticValidationError
) -> JSONResponse:
    """
    Handle Pydantic ValidationError exceptions.
    
    Args:
        request: FastAPI request object
        exc: PydanticValidationError
        
    Returns:
        JSONResponse with structured validation error information
    """
    logger.warning(
        f"Pydantic validation error occurred: {exc.errors()}",
        extra={
            "validation_errors": exc.errors(),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    error_response = {
        "error": "VALIDATION_ERROR",
        "message": "Data validation failed",
        "details": {
            "validation_errors": formatted_errors,
            "error_count": len(formatted_errors)
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def generic_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """
    Handle all other unhandled exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception
        
    Returns:
        JSONResponse with generic error information
    """
    logger.error(
        f"Unhandled exception occurred: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    error_response = {
        "error": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred. Please try again later.",
        "details": {
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Custom exception handlers
    app.add_exception_handler(BloodDonationAPIError, blood_donation_api_exception_handler)
    
    # FastAPI built-in exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered successfully")


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        details: Additional error details
        status_code: HTTP status code
        
    Returns:
        JSONResponse with structured error information
    """
    error_response = {
        "error": error_code,
        "message": message,
        "details": details or {}
    }
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


def format_validation_errors(errors: list) -> Dict[str, Any]:
    """
    Format validation errors for consistent response structure.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Formatted error details dictionary
    """
    formatted_errors = []
    
    for error in errors:
        if isinstance(error, dict):
            field_path = " -> ".join(str(loc) for loc in error.get("loc", []))
            formatted_errors.append({
                "field": field_path,
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "unknown"),
                "input": error.get("input")
            })
        else:
            formatted_errors.append({
                "field": "unknown",
                "message": str(error),
                "type": "unknown",
                "input": None
            })
    
    return {
        "validation_errors": formatted_errors,
        "error_count": len(formatted_errors)
    }