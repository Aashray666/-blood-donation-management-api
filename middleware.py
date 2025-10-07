"""
Middleware for the Blood Donation Management API.
Provides request/response logging, timing, and monitoring capabilities.
"""

import time
import uuid
import logging
from typing import Callable, Dict, Any
from datetime import datetime
import json

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from logging_config import get_logger, RequestLoggingContext

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: list = None
    ):
        """
        Initialize the request logging middleware.
        
        Args:
            app: ASGI application
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
            exclude_paths: List of paths to exclude from logging
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and response.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint
            
        Returns:
            Response object
        """
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        await self._log_request(request, request_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add timing and request ID headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            await self._log_response(request, response, request_id, process_time)
            
            return response
            
        except Exception as exc:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log exception
            logger.error(
                f"Request processing failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc)
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise exc
    
    async def _log_request(self, request: Request, request_id: str) -> None:
        """
        Log incoming request details.
        
        Args:
            request: FastAPI request object
            request_id: Unique request identifier
        """
        # Collect request information
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log request body if enabled
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON for better logging
                    try:
                        request_info["body"] = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_info["body"] = body.decode(errors="replace")
            except Exception as e:
                request_info["body_error"] = str(e)
        
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra=request_info
        )
    
    async def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        process_time: float
    ) -> None:
        """
        Log outgoing response details.
        
        Args:
            request: FastAPI request object
            response: FastAPI response object
            request_id: Unique request identifier
            process_time: Request processing time in seconds
        """
        # Collect response information
        response_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "process_time": process_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log response body if enabled and it's a JSON response
        if (self.log_response_body and 
            isinstance(response, JSONResponse) and 
            hasattr(response, 'body')):
            try:
                if response.body:
                    body_str = response.body.decode()
                    response_info["body"] = json.loads(body_str)
            except Exception as e:
                response_info["body_error"] = str(e)
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = "error"
        elif response.status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"
        
        getattr(logger, log_level)(
            f"Outgoing response: {request.method} {request.url.path} - {response.status_code}",
            extra=response_info
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded headers (for reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance metrics."""
    
    def __init__(
        self,
        app: ASGIApp,
        slow_request_threshold: float = 1.0,
        exclude_paths: list = None
    ):
        """
        Initialize the performance monitoring middleware.
        
        Args:
            app: ASGI application
            slow_request_threshold: Threshold in seconds for slow request logging
            exclude_paths: List of paths to exclude from monitoring
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
        self.performance_logger = get_logger("performance")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor request performance.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint
            
        Returns:
            Response object
        """
        # Skip monitoring for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log performance metrics
        performance_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add request ID if available
        if hasattr(request.state, "request_id"):
            performance_data["request_id"] = request.state.request_id
        
        # Log slow requests with warning level
        if process_time > self.slow_request_threshold:
            self.performance_logger.warning(
                f"Slow request detected: {request.method} {request.url.path} took {process_time:.3f}s",
                extra=performance_data
            )
        else:
            self.performance_logger.info(
                f"Request performance: {request.method} {request.url.path} - {process_time:.3f}s",
                extra=performance_data
            )
        
        return response


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware for health check functionality."""
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the health check middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
        self.health_logger = get_logger("health")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle health check requests.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint
            
        Returns:
            Response object
        """
        # Process request normally
        response = await call_next(request)
        
        # Log health check requests
        if request.url.path == "/health":
            self.health_logger.info(
                f"Health check request: {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "client_ip": self._get_client_ip(request),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        if request.client:
            return request.client.host
        return "unknown"


def register_middleware(app) -> None:
    """
    Register all middleware with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add middleware in reverse order (last added is executed first)
    
    # Health check middleware
    app.add_middleware(HealthCheckMiddleware)
    
    # Performance monitoring middleware
    app.add_middleware(
        PerformanceMonitoringMiddleware,
        slow_request_threshold=1.0  # Log requests taking more than 1 second
    )
    
    # Request logging middleware
    app.add_middleware(
        RequestLoggingMiddleware,
        log_request_body=False,  # Set to True for debugging
        log_response_body=False,  # Set to True for debugging
        exclude_paths=["/health", "/docs", "/redoc", "/openapi.json", "/static"]
    )
    
    logger.info("Middleware registered successfully")


# Utility functions for request context
def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request ID or 'unknown' if not available
    """
    return getattr(request.state, "request_id", "unknown")


def log_with_request_context(
    request: Request,
    level: str,
    message: str,
    **kwargs
) -> None:
    """
    Log a message with request context.
    
    Args:
        request: FastAPI request object
        level: Log level (info, warning, error, etc.)
        message: Log message
        **kwargs: Additional log data
    """
    request_logger = get_logger("request_context")
    
    log_data = {
        "request_id": get_request_id(request),
        "method": request.method,
        "path": request.url.path,
        **kwargs
    }
    
    getattr(request_logger, level.lower())(message, extra=log_data)