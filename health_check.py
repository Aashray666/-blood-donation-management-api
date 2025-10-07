"""
Health check and monitoring endpoints for the Blood Donation Management API.
Provides comprehensive system health monitoring and diagnostics.
"""

import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from database.connection import get_database_connection
from logging_config import get_logger

logger = get_logger("health_check")

# Health check router
router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """Health status response model."""
    status: str
    timestamp: str
    service: str
    version: str
    uptime_seconds: float
    checks: Dict[str, Any]


class DetailedHealthStatus(BaseModel):
    """Detailed health status response model."""
    status: str
    timestamp: str
    service: str
    version: str
    uptime_seconds: float
    system_info: Dict[str, Any]
    database_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    checks: Dict[str, Any]


# Store application start time for uptime calculation
_start_time = time.time()


def get_uptime() -> float:
    """
    Get application uptime in seconds.
    
    Returns:
        Uptime in seconds
    """
    return time.time() - _start_time


async def check_database_health() -> Dict[str, Any]:
    """
    Check database connectivity and basic operations.
    
    Returns:
        Database health information
    """
    try:
        start_time = time.time()
        
        # Import the async context manager
        from database.connection import get_db_session
        
        # Test database connection
        async with get_db_session() as conn:
            # Test basic query
            cursor = await conn.execute("SELECT 1")
            result = await cursor.fetchone()
            
            # Check if tables exist
            cursor = await conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('donors', 'blood_requests')
            """)
            tables_result = await cursor.fetchall()
            tables = [row[0] for row in tables_result]
            
            # Get database file size
            db_path = Path("blood_donation.db")
            db_size = db_path.stat().st_size if db_path.exists() else 0
            
            # Get record counts
            donor_count = 0
            request_count = 0
            
            if "donors" in tables:
                cursor = await conn.execute("SELECT COUNT(*) FROM donors")
                result = await cursor.fetchone()
                donor_count = result[0] if result else 0
            
            if "blood_requests" in tables:
                cursor = await conn.execute("SELECT COUNT(*) FROM blood_requests")
                result = await cursor.fetchone()
                request_count = result[0] if result else 0
        
        response_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time * 1000, 2),
            "database_size_bytes": db_size,
            "tables_present": tables,
            "donor_count": donor_count,
            "request_count": request_count,
            "connection_test": "passed"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection_test": "failed"
        }


def get_system_info() -> Dict[str, Any]:
    """
    Get system information and resource usage.
    
    Returns:
        System information dictionary
    """
    try:
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Process information
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total_bytes": memory.total,
                "available_bytes": memory.available,
                "used_bytes": memory.used,
                "usage_percent": memory.percent
            },
            "disk": {
                "total_bytes": disk.total,
                "free_bytes": disk.free,
                "used_bytes": disk.used,
                "usage_percent": (disk.used / disk.total) * 100
            },
            "process": {
                "memory_rss_bytes": process_memory.rss,
                "memory_vms_bytes": process_memory.vms,
                "pid": process.pid,
                "cpu_percent": process.cpu_percent()
            }
        }
        
    except Exception as e:
        logger.warning(f"Failed to get system info: {str(e)}")
        return {
            "error": str(e),
            "status": "unavailable"
        }


def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics and statistics.
    
    Returns:
        Performance metrics dictionary
    """
    try:
        # This is a simplified version - in a real application,
        # you might collect these metrics from a monitoring system
        return {
            "uptime_seconds": get_uptime(),
            "requests_processed": "N/A",  # Would be tracked by middleware
            "average_response_time_ms": "N/A",  # Would be calculated from logs
            "error_rate_percent": "N/A",  # Would be calculated from logs
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.warning(f"Failed to get performance metrics: {str(e)}")
        return {
            "error": str(e),
            "status": "unavailable"
        }


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status information
    """
    try:
        # Perform basic checks
        db_health = await check_database_health()
        
        # Determine overall status
        overall_status = "healthy" if db_health["status"] == "healthy" else "unhealthy"
        
        health_data = HealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            service="blood-donation-api",
            version="1.0.0",
            uptime_seconds=get_uptime(),
            checks={
                "database": db_health
            }
        )
        
        # Log health check
        logger.info(
            f"Health check performed: {overall_status}",
            extra={
                "status": overall_status,
                "uptime": get_uptime(),
                "database_status": db_health["status"]
            }
        )
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/health/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check():
    """
    Detailed health check endpoint with comprehensive system information.
    
    Returns:
        Detailed health status information
    """
    try:
        # Perform all checks
        db_health = await check_database_health()
        system_info = get_system_info()
        performance_metrics = get_performance_metrics()
        
        # Determine overall status
        overall_status = "healthy" if db_health["status"] == "healthy" else "unhealthy"
        
        # Check for system resource warnings
        if "memory" in system_info and system_info["memory"].get("usage_percent", 0) > 90:
            overall_status = "degraded"
        
        if "cpu" in system_info and system_info["cpu"].get("usage_percent", 0) > 90:
            overall_status = "degraded"
        
        health_data = DetailedHealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            service="blood-donation-api",
            version="1.0.0",
            uptime_seconds=get_uptime(),
            system_info=system_info,
            database_info=db_health,
            performance_metrics=performance_metrics,
            checks={
                "database": db_health,
                "system_resources": "healthy" if overall_status != "unhealthy" else "warning"
            }
        )
        
        # Log detailed health check
        logger.info(
            f"Detailed health check performed: {overall_status}",
            extra={
                "status": overall_status,
                "uptime": get_uptime(),
                "database_status": db_health["status"],
                "memory_usage": system_info.get("memory", {}).get("usage_percent"),
                "cpu_usage": system_info.get("cpu", {}).get("usage_percent")
            }
        )
        
        return health_data
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detailed health check failed"
        )


@router.get("/health/database")
async def database_health_check():
    """
    Database-specific health check endpoint.
    
    Returns:
        Database health information
    """
    try:
        db_health = await check_database_health()
        
        if db_health["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is unhealthy"
            )
        
        return db_health
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database health check failed"
        )


@router.get("/health/system")
async def system_health_check():
    """
    System-specific health check endpoint.
    
    Returns:
        System health information
    """
    try:
        system_info = get_system_info()
        
        # Check for critical resource usage
        memory_usage = system_info.get("memory", {}).get("usage_percent", 0)
        cpu_usage = system_info.get("cpu", {}).get("usage_percent", 0)
        disk_usage = system_info.get("disk", {}).get("usage_percent", 0)
        
        status_info = {
            "status": "healthy",
            "system_info": system_info,
            "warnings": []
        }
        
        if memory_usage > 90:
            status_info["warnings"].append("High memory usage")
            status_info["status"] = "warning"
        
        if cpu_usage > 90:
            status_info["warnings"].append("High CPU usage")
            status_info["status"] = "warning"
        
        if disk_usage > 90:
            status_info["warnings"].append("High disk usage")
            status_info["status"] = "warning"
        
        return status_info
        
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System health check failed"
        )


@router.get("/metrics")
async def get_metrics():
    """
    Get application metrics in a format suitable for monitoring systems.
    
    Returns:
        Application metrics
    """
    try:
        db_health = await check_database_health()
        system_info = get_system_info()
        performance_metrics = get_performance_metrics()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": get_uptime(),
            "database": {
                "healthy": db_health["status"] == "healthy",
                "response_time_ms": db_health.get("response_time_ms", 0),
                "donor_count": db_health.get("donor_count", 0),
                "request_count": db_health.get("request_count", 0)
            },
            "system": {
                "memory_usage_percent": system_info.get("memory", {}).get("usage_percent", 0),
                "cpu_usage_percent": system_info.get("cpu", {}).get("usage_percent", 0),
                "disk_usage_percent": system_info.get("disk", {}).get("usage_percent", 0)
            },
            "performance": performance_metrics
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics collection failed"
        )