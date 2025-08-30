#!/usr/bin/env python3
"""
Comprehensive Input Validation System for Syn_OS
Prevents injection attacks, XSS, and other input-based vulnerabilities
"""

import re
import html
import logging
import ipaddress
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import bleach
from urllib.parse import urlparse
try:
    import email_validator
except ImportError:
    email_validator = None

logger = logging.getLogger('synapticos.security.input_validator')


class ValidationError(Exception):
    """Input validation error"""
    pass


class InputType(Enum):
    """Types of input validation"""
    STRING = "string"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"
    USERNAME = "username"
    PASSWORD = "password"
    FILENAME = "filename"
    SQL_SAFE = "sql_safe"
    HTML_SAFE = "html_safe"
    JSON = "json"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    UUID = "uuid"
    CONSCIOUSNESS_LEVEL = "consciousness_level"
    API_KEY = "api_key"


@dataclass
class ValidationRule:
    """Input validation rule"""
    input_type: InputType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable] = None
    sanitize: bool = True


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_value: Any = None
    error_message: Optional[str] = None
    security_risk: Optional[str] = None


class SecureInputValidator:
    """Comprehensive input validation and sanitization"""
    
    def __init__(self):
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(;|\|\||&&)",
            r"(\bxp_cmdshell\b|\bsp_executesql\b)"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        self.command_injection_patterns = [
            r"[;&|`$(){}[\]\\]",
            r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ping|wget|curl|nc|telnet|ssh|ftp)\b",
            r"(\.\.\/|\.\.\\)",
            r"(/etc/passwd|/etc/shadow|/proc/)",
            r"(\$\(|\`)"
        ]
        
        # Safe HTML tags and attributes for content sanitization
        self.allowed_html_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'a', 'img'
        ]
        
        self.allowed_html_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            '*': ['class']
        }
    
    def validate_input(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate input according to rule"""
        try:
            # Check if required
            if rule.required and (value is None or value == ""):
                return ValidationResult(
                    is_valid=False,
                    error_message="This field is required"
                )
            
            # If not required and empty, return valid
            if not rule.required and (value is None or value == ""):
                return ValidationResult(is_valid=True, sanitized_value=value)
            
            # Convert to string for most validations
            str_value = str(value) if value is not None else ""
            
            # Type-specific validation
            if rule.input_type == InputType.STRING:
                return self._validate_string(str_value, rule)
            elif rule.input_type == InputType.EMAIL:
                return self._validate_email(str_value, rule)
            elif rule.input_type == InputType.URL:
                return self._validate_url(str_value, rule)
            elif rule.input_type == InputType.IP_ADDRESS:
                return self._validate_ip_address(str_value, rule)
            elif rule.input_type == InputType.USERNAME:
                return self._validate_username(str_value, rule)
            elif rule.input_type == InputType.PASSWORD:
                return self._validate_password(str_value, rule)
            elif rule.input_type == InputType.FILENAME:
                return self._validate_filename(str_value, rule)
            elif rule.input_type == InputType.SQL_SAFE:
                return self._validate_sql_safe(str_value, rule)
            elif rule.input_type == InputType.HTML_SAFE:
                return self._validate_html_safe(str_value, rule)
            elif rule.input_type == InputType.JSON:
                return self._validate_json(str_value, rule)
            elif rule.input_type == InputType.INTEGER:
                return self._validate_integer(value, rule)
            elif rule.input_type == InputType.FLOAT:
                return self._validate_float(value, rule)
            elif rule.input_type == InputType.BOOLEAN:
                return self._validate_boolean(value, rule)
            elif rule.input_type == InputType.UUID:
                return self._validate_uuid(str_value, rule)
            elif rule.input_type == InputType.CONSCIOUSNESS_LEVEL:
                return self._validate_consciousness_level(value, rule)
            elif rule.input_type == InputType.API_KEY:
                return self._validate_api_key(str_value, rule)
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unknown validation type: {rule.input_type}"
                )
                
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error_message="Validation failed",
                security_risk="Validation exception"
            )
    
    def _validate_string(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate string input"""
        # Length validation
        if rule.min_length and len(value) < rule.min_length:
            return ValidationResult(
                is_valid=False,
                error_message=f"Minimum length is {rule.min_length} characters"
            )
        
        if rule.max_length and len(value) > rule.max_length:
            return ValidationResult(
                is_valid=False,
                error_message=f"Maximum length is {rule.max_length} characters"
            )
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, value):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid format"
            )
        
        # Allowed values validation
        if rule.allowed_values and value not in rule.allowed_values:
            return ValidationResult(
                is_valid=False,
                error_message="Value not allowed"
            )
        
        # Security checks
        security_risk = self._check_security_risks(value)
        if security_risk:
            return ValidationResult(
                is_valid=False,
                error_message="Input contains potentially dangerous content",
                security_risk=security_risk
            )
        
        # Sanitization
        sanitized_value = self._sanitize_string(value) if rule.sanitize else value
        
        # Custom validation
        if rule.custom_validator:
            try:
                if not rule.custom_validator(sanitized_value):
                    return ValidationResult(
                        is_valid=False,
                        error_message="Custom validation failed"
                    )
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Custom validation error: {e}"
                )
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized_value)
    
    def _validate_email(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate email address"""
        if email_validator:
            try:
                # Use email-validator library for comprehensive validation
                valid_email = email_validator.validate_email(value)
                sanitized_value = valid_email.email if rule.sanitize else value
                
                return ValidationResult(is_valid=True, sanitized_value=sanitized_value)
            except email_validator.EmailNotValidError as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid email address: {str(e)}"
                )
        else:
            # Fallback email validation using regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid email address format"
                )
            
            sanitized_value = value.lower() if rule.sanitize else value
            return ValidationResult(is_valid=True, sanitized_value=sanitized_value)
    
    def _validate_url(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate URL"""
        try:
            parsed = urlparse(value)
            
            # Check for valid scheme
            if parsed.scheme not in ['http', 'https', 'ftp', 'ftps']:
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid URL scheme"
                )
            
            # Check for valid netloc
            if not parsed.netloc:
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid URL format"
                )
            
            # Security checks for dangerous URLs
            if any(danger in value.lower() for danger in ['javascript:', 'data:', 'vbscript:']):
                return ValidationResult(
                    is_valid=False,
                    error_message="Potentially dangerous URL",
                    security_risk="Dangerous URL scheme"
                )
            
            sanitized_value = value if rule.sanitize else value
            return ValidationResult(is_valid=True, sanitized_value=sanitized_value)
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message="Invalid URL format"
            )
    
    def _validate_ip_address(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate IP address"""
        try:
            # Try IPv4 first, then IPv6
            ip = ipaddress.ip_address(value)
            
            # Check for private/reserved addresses if needed
            if hasattr(ip, 'is_private') and ip.is_private:
                logger.info(f"Private IP address detected: {value}")
            
            return ValidationResult(is_valid=True, sanitized_value=str(ip))
            
        except ValueError:
            return ValidationResult(
                is_valid=False,
                error_message="Invalid IP address format"
            )
    
    def _validate_username(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate username"""
        # Username pattern: alphanumeric, underscore, hyphen, dot
        username_pattern = r'^[a-zA-Z0-9._-]+$'
        
        if not re.match(username_pattern, value):
            return ValidationResult(
                is_valid=False,
                error_message="Username can only contain letters, numbers, dots, underscores, and hyphens"
            )
        
        # Length checks
        if len(value) < 3:
            return ValidationResult(
                is_valid=False,
                error_message="Username must be at least 3 characters long"
            )
        
        if len(value) > 50:
            return ValidationResult(
                is_valid=False,
                error_message="Username cannot exceed 50 characters"
            )
        
        # Reserved usernames
        reserved_usernames = [
            'admin', 'administrator', 'root', 'system', 'api', 'test', 'guest',
            'null', 'undefined', 'anonymous', 'public', 'private'
        ]
        
        if value.lower() in reserved_usernames:
            return ValidationResult(
                is_valid=False,
                error_message="Username is reserved"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=value.lower())
    
    def _validate_password(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate password strength"""
        errors = []
        
        # Length check
        if len(value) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(value) > 128:
            errors.append("Password cannot exceed 128 characters")
        
        # Complexity checks
        if not re.search(r'[a-z]', value):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', value):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', value):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("Password must contain at least one special character")
        
        # Common password check
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', '1234567890'
        ]
        
        if value.lower() in common_passwords:
            errors.append("Password is too common")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                error_message="; ".join(errors)
            )
        
        # Don't sanitize passwords - return as-is
        return ValidationResult(is_valid=True, sanitized_value=value)
    
    def _validate_filename(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate filename for security"""
        # Dangerous filename patterns
        dangerous_patterns = [
            r'\.\./',  # Directory traversal
            r'\.\.\\',  # Windows directory traversal
            r'^/',     # Absolute path
            r'^[A-Za-z]:',  # Windows drive letter
            r'\x00',   # Null byte
            r'[<>:"|?*]',  # Windows invalid characters
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value):
                return ValidationResult(
                    is_valid=False,
                    error_message="Filename contains dangerous characters",
                    security_risk="Path traversal attempt"
                )
        
        # Reserved Windows filenames
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
            'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
            'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        if value.upper().split('.')[0] in reserved_names:
            return ValidationResult(
                is_valid=False,
                error_message="Filename is reserved"
            )
        
        # Length check
        if len(value) > 255:
            return ValidationResult(
                is_valid=False,
                error_message="Filename too long"
            )
        
        # Sanitize filename
        sanitized = re.sub(r'[^\w\-_\.]', '_', value) if rule.sanitize else value
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    def _validate_sql_safe(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate input is safe from SQL injection"""
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    error_message="Input contains potentially dangerous SQL content",
                    security_risk="SQL injection attempt"
                )
        
        # Sanitize by escaping single quotes
        sanitized = value.replace("'", "''") if rule.sanitize else value
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    def _validate_html_safe(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate and sanitize HTML content"""
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    error_message="Input contains potentially dangerous HTML content",
                    security_risk="XSS attempt"
                )
        
        if rule.sanitize:
            # Use bleach to sanitize HTML
            sanitized = bleach.clean(
                value,
                tags=self.allowed_html_tags,
                attributes=self.allowed_html_attributes,
                strip=True
            )
        else:
            sanitized = value
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    def _validate_json(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate JSON format"""
        import json
        try:
            parsed = json.loads(value)
            
            # Check for dangerous content in JSON
            json_str = json.dumps(parsed)
            security_risk = self._check_security_risks(json_str)
            if security_risk:
                return ValidationResult(
                    is_valid=False,
                    error_message="JSON contains potentially dangerous content",
                    security_risk=security_risk
                )
            
            return ValidationResult(is_valid=True, sanitized_value=json_str)
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid JSON format: {str(e)}"
            )
    
    def _validate_integer(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate integer value"""
        try:
            int_value = int(value)
            
            if rule.min_value is not None and int_value < rule.min_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Value must be at least {rule.min_value}"
                )
            
            if rule.max_value is not None and int_value > rule.max_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Value must be at most {rule.max_value}"
                )
            
            return ValidationResult(is_valid=True, sanitized_value=int_value)
            
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid integer value"
            )
    
    def _validate_float(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate float value"""
        try:
            float_value = float(value)
            
            if rule.min_value is not None and float_value < rule.min_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Value must be at least {rule.min_value}"
                )
            
            if rule.max_value is not None and float_value > rule.max_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Value must be at most {rule.max_value}"
                )
            
            return ValidationResult(is_valid=True, sanitized_value=float_value)
            
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid number value"
            )
    
    def _validate_boolean(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate boolean value"""
        if isinstance(value, bool):
            return ValidationResult(is_valid=True, sanitized_value=value)
        
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return ValidationResult(is_valid=True, sanitized_value=True)
            elif value.lower() in ['false', '0', 'no', 'off']:
                return ValidationResult(is_valid=True, sanitized_value=False)
        
        return ValidationResult(
            is_valid=False,
            error_message="Invalid boolean value"
        )
    
    def _validate_uuid(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate UUID format"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, value.lower()):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid UUID format"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=value.lower())
    
    def _validate_consciousness_level(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate consciousness level (0.0 to 1.0)"""
        try:
            level = float(value)
            
            if not (0.0 <= level <= 1.0):
                return ValidationResult(
                    is_valid=False,
                    error_message="Consciousness level must be between 0.0 and 1.0"
                )
            
            return ValidationResult(is_valid=True, sanitized_value=level)
            
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid consciousness level value"
            )
    
    def _validate_api_key(self, value: str, rule: ValidationRule) -> ValidationResult:
        """Validate API key format"""
        # API key should be alphanumeric with specific length
        if not re.match(r'^[A-Za-z0-9_-]+$', value):
            return ValidationResult(
                is_valid=False,
                error_message="API key contains invalid characters"
            )
        
        if len(value) < 16:
            return ValidationResult(
                is_valid=False,
                error_message="API key too short"
            )
        
        if len(value) > 128:
            return ValidationResult(
                is_valid=False,
                error_message="API key too long"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=value)
    
    def _check_security_risks(self, value: str) -> Optional[str]:
        """Check for various security risks in input"""
        # SQL injection check
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return "SQL injection attempt"
        
        # XSS check
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return "XSS attempt"
        
        # Command injection check
        for pattern in self.command_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return "Command injection attempt"
        
        return None
    
    def _sanitize_string(self, value: str) -> str:
        """Basic string sanitization"""
        # HTML escape
        sanitized = html.escape(value)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def validate_dict(self, data: Dict[str, Any], rules: Dict[str, ValidationRule]) -> Dict[str, ValidationResult]:
        """Validate a dictionary of inputs"""
        results = {}
        
        for field_name, rule in rules.items():
            value = data.get(field_name)
            results[field_name] = self.validate_input(value, rule)
        
        return results
    
    def is_dict_valid(self, validation_results: Dict[str, ValidationResult]) -> bool:
        """Check if all validation results are valid"""
        return all(result.is_valid for result in validation_results.values())
    
    def get_sanitized_dict(self, validation_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Get sanitized values from validation results"""
        return {
            field: result.sanitized_value
            for field, result in validation_results.items()
            if result.is_valid and result.sanitized_value is not None
        }


# Global validator instance
input_validator = SecureInputValidator()


def get_validator() -> SecureInputValidator:
    """Get the global input validator instance"""
    return input_validator


# Common validation rules
COMMON_RULES = {
    'username': ValidationRule(
        input_type=InputType.USERNAME,
        required=True,
        min_length=3,
        max_length=50
    ),
    'password': ValidationRule(
        input_type=InputType.PASSWORD,
        required=True,
        min_length=8,
        max_length=128
    ),
    'email': ValidationRule(
        input_type=InputType.EMAIL,
        required=True,
        max_length=254
    ),
    'consciousness_level': ValidationRule(
        input_type=InputType.CONSCIOUSNESS_LEVEL,
        required=True,
        min_value=0.0,
        max_value=1.0
    ),
    'api_key': ValidationRule(
        input_type=InputType.API_KEY,
        required=True,
        min_length=16,
        max_length=128
    )
}


if __name__ == "__main__":
    # Test the validation system
    validator = SecureInputValidator()
    
    # Test various inputs
    test_cases = [
        ("valid_username", ValidationRule(InputType.USERNAME), True),
        ("user@example.com", ValidationRule(InputType.EMAIL), True),
        ("' OR '1'='1' --", ValidationRule(InputType.SQL_SAFE), False),
        ("<script>alert('xss')</script>", ValidationRule(InputType.HTML_SAFE), False),
        ("0.75", ValidationRule(InputType.CONSCIOUSNESS_LEVEL), True),
        ("2.5", ValidationRule(InputType.CONSCIOUSNESS_LEVEL), False),
    ]
    
    for value, rule, expected_valid in test_cases:
        result = validator.validate_input(value, rule)
        status = "✅" if result.is_valid == expected_valid else "❌"
        print(f"{status} {value}: {result.is_valid} (expected: {expected_valid})")
        if not result.is_valid:
            print(f"   Error: {result.error_message}")
            if result.security_risk:
                print(f"   Security Risk: {result.security_risk}")