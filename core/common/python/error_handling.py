#!/usr/bin/env python3
"""
Syn_OS Standardized Error Handling Framework
Provides unified error handling, logging, and recovery patterns across the system
"""

import json
import logging
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import wraps

class ErrorSeverity(Enum):
    """Standardized error severity levels"""
    CRITICAL = "CRITICAL"    # System failure, requires immediate action
    HIGH = "HIGH"           # Service degradation, user impact
    MEDIUM = "MEDIUM"       # Functionality impaired, workaround available
    LOW = "LOW"             # Minor issues, no user impact
    INFO = "INFO"           # Informational, no action required

class ErrorCategory(Enum):
    """Standardized error categories"""
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"
    FILESYSTEM = "FILESYSTEM"
    CONFIGURATION = "CONFIGURATION"
    CONSCIOUSNESS = "CONSCIOUSNESS"
    INTEGRATION = "INTEGRATION"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    SYSTEM = "SYSTEM"

class SynOSError(Exception):
    """Base class for all Syn_OS errors with standardized structure"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code or f"{category.value}_{severity.value}"
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now().isoformat()
        self.traceback_info = traceback.format_exc() if original_exception else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to structured dictionary for logging/serialization"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "context": self.context,
            "traceback": self.traceback_info,
            "original_exception": str(self.original_exception) if self.original_exception else None
        }
    
    def to_json(self) -> str:
        """Convert error to JSON string for structured logging"""
        return json.dumps(self.to_dict(), indent=2, default=str)

# Specific error types
class AuthenticationError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.AUTHENTICATION, **kwargs)

class AuthorizationError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.AUTHORIZATION, **kwargs)

class ValidationError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.VALIDATION, **kwargs)

class NetworkError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.NETWORK, **kwargs)

class DatabaseError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.DATABASE, **kwargs)

class FilesystemError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.FILESYSTEM, **kwargs)

class ConfigurationError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.CONFIGURATION, **kwargs)

class ConsciousnessError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.CONSCIOUSNESS, **kwargs)

class IntegrationError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.INTEGRATION, **kwargs)

class SecurityError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.SECURITY, **kwargs)

class PerformanceError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.PERFORMANCE, **kwargs)

class SystemError(SynOSError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.SYSTEM, **kwargs)

class ErrorHandler:
    """Centralized error handling and logging service"""
    
    def __init__(self, service_name: str, log_file: Optional[str] = None):
        self.service_name = service_name
        self.setup_logging(log_file)
        self.error_stats = {category.value: 0 for category in ErrorCategory}
        
    def setup_logging(self, log_file: Optional[str] = None):
        """Setup structured logging with standardized format"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("${PROJECT_ROOT}/logs/errors")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        if not log_file:
            log_file = logs_dir / f"{self.service_name}_errors.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger(f"syn_os.{self.service_name}")
    
    def handle_error(
        self,
        error: Union[SynOSError, Exception],
        context: Optional[Dict[str, Any]] = None,
        raise_after_log: bool = True
    ) -> Optional[SynOSError]:
        """Handle and log errors with standardized format"""
        
        # Convert generic exceptions to SynOSError
        if not isinstance(error, SynOSError):
            syn_error = SynOSError(
                message=str(error),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                context=context,
                original_exception=error
            )
        else:
            if context:
                syn_error.context.update(context)
            syn_error = error
        
        # Update error statistics
        self.error_stats[syn_error.category.value] += 1
        
        # Log error with appropriate level
        log_level = self._get_log_level(syn_error.severity)
        self.logger.log(log_level, f"[{syn_error.error_code}] {syn_error.to_json()}")
        
        # Send alerts for critical errors
        if syn_error.severity == ErrorSeverity.CRITICAL:
            self._send_critical_alert(syn_error)
        
        if raise_after_log:
            raise syn_error
        
        return syn_error
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """Map error severity to logging level"""
        severity_mapping = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.INFO: logging.DEBUG
        }
        return severity_mapping.get(severity, logging.WARNING)
    
    def _send_critical_alert(self, error: SynOSError):
        """Send alerts for critical errors (implement based on infrastructure)"""
        # This would integrate with alerting systems like PagerDuty, Slack, etc.
        # For now, log as critical and write to special alert file
        alert_file = Path("${PROJECT_ROOT}/logs/errors/critical_alerts.log")
        alert_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(alert_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} - CRITICAL ALERT: {error.to_json()}\n")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring and reporting"""
        total_errors = sum(self.error_stats.values())
        return {
            "service": self.service_name,
            "total_errors": total_errors,
            "errors_by_category": self.error_stats,
            "timestamp": datetime.now().isoformat()
        }

def error_handler_decorator(handler: ErrorHandler):
    """Decorator for automatic error handling in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200],  # Truncate long args
                    "kwargs": str(kwargs)[:200]
                }
                handler.handle_error(e, context=context)
        return wrapper
    return decorator

def safe_execute(
    func,
    default_return=None,
    error_handler: Optional[ErrorHandler] = None,
    context: Optional[Dict[str, Any]] = None
):
    """Execute function safely with error handling and default return"""
    try:
        return func()
    except Exception as e:
        if error_handler:
            error_handler.handle_error(e, context=context, raise_after_log=False)
        else:
            logging.error(f"Safe execution failed: {e}")
        return default_return

# Global error handler instance
_global_error_handler = None

def get_global_error_handler() -> ErrorHandler:
    """Get or create global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler("syn_os_global")
    return _global_error_handler

def log_error(error: Union[str, Exception], **kwargs):
    """Convenience function for quick error logging"""
    handler = get_global_error_handler()
    if isinstance(error, str):
        error = SynOSError(error, ErrorCategory.SYSTEM, **kwargs)
    handler.handle_error(error, raise_after_log=False)

# Example usage and testing
if __name__ == "__main__":
    # Initialize error handler
    handler = ErrorHandler("test_service")
    
    # Test different error types
    try:
        raise ValidationError(
            "Invalid input format",
            severity=ErrorSeverity.HIGH,
            context={"input": "invalid_data", "expected": "json"}
        )
    except SynOSError as e:
        handler.handle_error(e, raise_after_log=False)
    
    # Test decorator
    @error_handler_decorator(handler)
    def test_function():
        raise ValueError("Test error for decorator")
    
    try:
        test_function()
    except:
        pass  # Error already handled by decorator
    
    # Print statistics
    print("Error Statistics:", handler.get_error_statistics())
