"""
Logging configuration for the Blood Donation Management API.
Provides structured logging with different levels and formatters.
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Dict, Any
import json
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON formatted log string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.
        
        Args:
            record: LogRecord to format
            
        Returns:
            Colored formatted log string
        """
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the message
        formatted_message = (
            f"{color}[{timestamp}] {record.levelname:8} "
            f"{record.name}:{record.lineno} - {record.getMessage()}{reset}"
        )
        
        # Add exception information if present
        if record.exc_info:
            formatted_message += f"\n{self.formatException(record.exc_info)}"
        
        return formatted_message


def get_logging_config(
    log_level: str = "INFO",
    log_file: str = "logs/blood_donation_api.log",
    enable_json_logging: bool = False,
    enable_console_logging: bool = True
) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        enable_json_logging: Whether to enable JSON formatted file logging
        enable_console_logging: Whether to enable console logging
        
    Returns:
        Logging configuration dictionary
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d in %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": JSONFormatter
            },
            "colored": {
                "()": ColoredFormatter
            }
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json" if enable_json_logging else "detailed",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json" if enable_json_logging else "detailed",
                "filename": log_file.replace(".log", "_errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["file", "error_file"],
                "propagate": False
            },
            "blood_donation_api": {
                "level": log_level,
                "handlers": ["file", "error_file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["file", "error_file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    # Add console handler if enabled
    if enable_console_logging:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        }
        
        # Add console handler to all loggers
        for logger_config in config["loggers"].values():
            if "console" not in logger_config["handlers"]:
                logger_config["handlers"].append("console")
    
    return config


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    enable_json_logging: bool = None,
    enable_console_logging: bool = None
) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (defaults to environment variable or INFO)
        log_file: Path to log file (defaults to logs/blood_donation_api.log)
        enable_json_logging: Whether to enable JSON logging (defaults to environment variable or False)
        enable_console_logging: Whether to enable console logging (defaults to environment variable or True)
    """
    # Get configuration from environment variables or use defaults
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = log_file or os.getenv("LOG_FILE", "logs/blood_donation_api.log")
    enable_json_logging = (
        enable_json_logging 
        if enable_json_logging is not None 
        else os.getenv("ENABLE_JSON_LOGGING", "false").lower() == "true"
    )
    enable_console_logging = (
        enable_console_logging 
        if enable_console_logging is not None 
        else os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true"
    )
    
    # Get logging configuration
    config = get_logging_config(
        log_level=log_level,
        log_file=log_file,
        enable_json_logging=enable_json_logging,
        enable_console_logging=enable_console_logging
    )
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log configuration info
    logger = logging.getLogger("blood_donation_api.logging")
    logger.info(
        "Logging configured successfully",
        extra={
            "log_level": log_level,
            "log_file": log_file,
            "json_logging": enable_json_logging,
            "console_logging": enable_console_logging
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"blood_donation_api.{name}")


# Context manager for request logging
class RequestLoggingContext:
    """Context manager for request-specific logging."""
    
    def __init__(self, request_id: str, method: str, path: str):
        """
        Initialize request logging context.
        
        Args:
            request_id: Unique request identifier
            method: HTTP method
            path: Request path
        """
        self.request_id = request_id
        self.method = method
        self.path = path
        self.start_time = None
        self.logger = get_logger("request")
    
    def __enter__(self):
        """Enter the context manager."""
        self.start_time = datetime.utcnow()
        self.logger.info(
            f"Request started: {self.method} {self.path}",
            extra={
                "request_id": self.request_id,
                "method": self.method,
                "path": self.path,
                "start_time": self.start_time.isoformat()
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                f"Request completed: {self.method} {self.path}",
                extra={
                    "request_id": self.request_id,
                    "method": self.method,
                    "path": self.path,
                    "duration_seconds": duration,
                    "end_time": end_time.isoformat()
                }
            )
        else:
            self.logger.error(
                f"Request failed: {self.method} {self.path}",
                extra={
                    "request_id": self.request_id,
                    "method": self.method,
                    "path": self.path,
                    "duration_seconds": duration,
                    "end_time": end_time.isoformat(),
                    "exception_type": exc_type.__name__ if exc_type else None,
                    "exception_message": str(exc_val) if exc_val else None
                },
                exc_info=(exc_type, exc_val, exc_tb)
            )
    
    def log_info(self, message: str, **kwargs):
        """Log an info message with request context."""
        self.logger.info(
            message,
            extra={
                "request_id": self.request_id,
                "method": self.method,
                "path": self.path,
                **kwargs
            }
        )
    
    def log_warning(self, message: str, **kwargs):
        """Log a warning message with request context."""
        self.logger.warning(
            message,
            extra={
                "request_id": self.request_id,
                "method": self.method,
                "path": self.path,
                **kwargs
            }
        )
    
    def log_error(self, message: str, **kwargs):
        """Log an error message with request context."""
        self.logger.error(
            message,
            extra={
                "request_id": self.request_id,
                "method": self.method,
                "path": self.path,
                **kwargs
            }
        )