import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.config.settings import settings


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_string: Custom log format string
    """
    # Default format
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_specific_loggers()


def configure_specific_loggers() -> None:
    """Configure logging for specific modules"""
    
    # Database logging
    db_logger = logging.getLogger("motor")
    db_logger.setLevel(logging.WARNING)
    
    # Beanie logging
    beanie_logger = logging.getLogger("beanie")
    beanie_logger.setLevel(logging.INFO)
    
    # FastAPI logging
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # UVicorn logging
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # HTTP client logging
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {str(e)}")
            raise
    
    return wrapper


def log_async_function_call(func):
    """Decorator to log async function calls"""
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} returned successfully")
            return result
        except Exception as e:
            logger.error(f"Async {func.__name__} failed with error: {str(e)}")
            raise
    
    return wrapper


class RequestLogger:
    """Utility class for logging HTTP requests"""
    
    def __init__(self, logger_name: str = "requests"):
        self.logger = get_logger(logger_name)
    
    def log_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        user_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Log HTTP request information"""
        
        log_data = {
            "method": method,
            "url": url,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if status_code:
            log_data["status_code"] = status_code
        
        if duration:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        if user_id:
            log_data["user_id"] = user_id
        
        if error:
            log_data["error"] = error
            self.logger.error(f"Request failed: {log_data}")
        else:
            self.logger.info(f"Request: {log_data}")
    
    def log_database_operation(
        self,
        operation: str,
        collection: str,
        duration: Optional[float] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Log database operation information"""
        
        log_data = {
            "operation": operation,
            "collection": collection,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if duration:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        if user_id:
            log_data["user_id"] = user_id
        
        if error:
            log_data["error"] = error
            self.logger.error(f"Database operation failed: {log_data}")
        else:
            self.logger.debug(f"Database operation: {log_data}")


class SecurityLogger:
    """Utility class for logging security-related events"""
    
    def __init__(self, logger_name: str = "security"):
        self.logger = get_logger(logger_name)
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Log login attempt"""
        
        log_data = {
            "event": "login_attempt",
            "email": email,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if ip_address:
            log_data["ip_address"] = ip_address
        
        if user_agent:
            log_data["user_agent"] = user_agent
        
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(f"Login successful: {log_data}")
        else:
            self.logger.warning(f"Login failed: {log_data}")
    
    def log_registration_attempt(
        self,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Log registration attempt"""
        
        log_data = {
            "event": "registration_attempt",
            "email": email,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if ip_address:
            log_data["ip_address"] = ip_address
        
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(f"Registration successful: {log_data}")
        else:
            self.logger.warning(f"Registration failed: {log_data}")
    
    def log_token_validation(
        self,
        token_valid: bool,
        user_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Log JWT token validation"""
        
        log_data = {
            "event": "token_validation",
            "valid": token_valid,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if user_id:
            log_data["user_id"] = user_id
        
        if error:
            log_data["error"] = error
        
        if token_valid:
            self.logger.debug(f"Token valid: {log_data}")
        else:
            self.logger.warning(f"Token invalid: {log_data}")
    
    def log_suspicious_activity(
        self,
        activity: str,
        details: dict,
        severity: str = "warning"
    ) -> None:
        """Log suspicious security activity"""
        
        log_data = {
            "event": "suspicious_activity",
            "activity": activity,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if severity == "critical":
            self.logger.critical(f"Suspicious activity: {log_data}")
        elif severity == "error":
            self.logger.error(f"Suspicious activity: {log_data}")
        else:
            self.logger.warning(f"Suspicious activity: {log_data}")


# Global logger instances
request_logger = RequestLogger()
security_logger = SecurityLogger()
