#!/usr/bin/env python3
"""
Emergency Input Sanitization Framework
Critical security fix for CVSS 9.1 command injection vulnerabilities
"""

import re
import html
import logging
import ipaddress
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse, quote
import json
import base64


class InputSanitizer:
    """
    Emergency input sanitization framework to prevent injection attacks
    Implements comprehensive input validation and sanitization
    """
    
    def __init__(self):
        """Initialize input sanitizer with security patterns"""
        self.logger = logging.getLogger(__name__)
        
        # Dangerous patterns that should be blocked
        self.dangerous_patterns = [
            # Command injection patterns
            r'[;&|`$(){}[\]<>]',
            r'\.\./',
            r'\\x[0-9a-fA-F]{2}',
            r'%[0-9a-fA-F]{2}',
            
            # SQL injection patterns
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'[\'";]',
            
            # Script injection patterns
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            
            # Path traversal patterns
            r'\.\.[\\/]',
            r'[\\/]etc[\\/]',
            r'[\\/]proc[\\/]',
            r'[\\/]sys[\\/]'
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
        
        # Allowed characters for different input types
        self.allowed_chars = {
            'alphanumeric': r'^[a-zA-Z0-9]+$',
            'alphanumeric_space': r'^[a-zA-Z0-9\s]+$',
            'filename': r'^[a-zA-Z0-9._-]+$',
            'ip_address': r'^[0-9.]+$',
            'hostname': r'^[a-zA-Z0-9.-]+$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'url': r'^https?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?$'
        }
    
    def sanitize_command_input(self, input_str: str) -> Dict[str, Any]:
        """
        CRITICAL: Sanitize command input to prevent injection attacks
        Returns validation result and sanitized input
        """
        try:
            if not isinstance(input_str, str):
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Input must be a string',
                    'risk_level': 'HIGH'
                }
            
            # Check for dangerous patterns
            for pattern in self.compiled_patterns:
                if pattern.search(input_str):
                    self.logger.warning(f"Dangerous pattern detected in input: {input_str[:50]}...")
                    return {
                        'valid': False,
                        'sanitized': '',
                        'reason': f'Dangerous pattern detected: {pattern.pattern}',
                        'risk_level': 'CRITICAL'
                    }
            
            # Length validation
            if len(input_str) > 1000:
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Input too long (max 1000 characters)',
                    'risk_level': 'MEDIUM'
                }
            
            # Basic sanitization
            sanitized = input_str.strip()
            sanitized = re.sub(r'\s+', ' ', sanitized)  # Normalize whitespace
            
            return {
                'valid': True,
                'sanitized': sanitized,
                'reason': 'Input passed validation',
                'risk_level': 'LOW'
            }
            
        except Exception as e:
            self.logger.error(f"Error sanitizing command input: {e}")
            return {
                'valid': False,
                'sanitized': '',
                'reason': f'Sanitization error: {str(e)}',
                'risk_level': 'HIGH'
            }
    
    def validate_ip_address(self, ip_str: str) -> Dict[str, Any]:
        """Validate IP address input"""
        try:
            # Try to parse as IP address
            ip_obj = ipaddress.ip_address(ip_str.strip())
            
            # Check for private/reserved ranges
            if ip_obj.is_private:
                risk_level = 'LOW'
            elif ip_obj.is_reserved or ip_obj.is_multicast:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'MEDIUM'  # Public IP
            
            return {
                'valid': True,
                'sanitized': str(ip_obj),
                'reason': 'Valid IP address',
                'risk_level': risk_level,
                'ip_type': 'IPv4' if ip_obj.version == 4 else 'IPv6'
            }
            
        except ValueError as e:
            return {
                'valid': False,
                'sanitized': '',
                'reason': f'Invalid IP address: {str(e)}',
                'risk_level': 'HIGH'
            }
    
    def validate_hostname(self, hostname: str) -> Dict[str, Any]:
        """Validate hostname input"""
        try:
            hostname = hostname.strip().lower()
            
            # Length check
            if len(hostname) > 253:
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Hostname too long',
                    'risk_level': 'MEDIUM'
                }
            
            # Pattern check
            if not re.match(self.allowed_chars['hostname'], hostname):
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Invalid hostname characters',
                    'risk_level': 'HIGH'
                }
            
            # Check for dangerous domains
            dangerous_domains = ['.gov', '.mil', '.bank', '.hospital']
            if any(domain in hostname for domain in dangerous_domains):
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Restricted domain detected',
                    'risk_level': 'CRITICAL'
                }
            
            return {
                'valid': True,
                'sanitized': hostname,
                'reason': 'Valid hostname',
                'risk_level': 'LOW'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'sanitized': '',
                'reason': f'Hostname validation error: {str(e)}',
                'risk_level': 'HIGH'
            }
    
    def sanitize_file_path(self, file_path: str) -> Dict[str, Any]:
        """Sanitize file path to prevent directory traversal"""
        try:
            if not isinstance(file_path, str):
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'File path must be a string',
                    'risk_level': 'HIGH'
                }
            
            # Check for path traversal attempts
            if '..' in file_path or file_path.startswith('/'):
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Path traversal attempt detected',
                    'risk_level': 'CRITICAL'
                }
            
            # Normalize path
            import os.path
            normalized = os.path.normpath(file_path)
            
            # Check for dangerous paths
            dangerous_paths = ['/etc/', '/proc/', '/sys/', '/dev/', '/root/']
            if any(dangerous in normalized.lower() for dangerous in dangerous_paths):
                return {
                    'valid': False,
                    'sanitized': '',
                    'reason': 'Access to system directory denied',
                    'risk_level': 'CRITICAL'
                }
            
            return {
                'valid': True,
                'sanitized': normalized,
                'reason': 'Valid file path',
                'risk_level': 'LOW'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'sanitized': '',
                'reason': f'File path validation error: {str(e)}',
                'risk_level': 'HIGH'
            }
    
    def sanitize_json_input(self, json_str: str) -> Dict[str, Any]:
        """Sanitize JSON input"""
        try:
            # Parse JSON to validate structure
            parsed = json.loads(json_str)
            
            # Re-serialize to ensure clean JSON
            sanitized = json.dumps(parsed, separators=(',', ':'))
            
            return {
                'valid': True,
                'sanitized': sanitized,
                'parsed': parsed,
                'reason': 'Valid JSON',
                'risk_level': 'LOW'
            }
            
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'sanitized': '',
                'reason': f'Invalid JSON: {str(e)}',
                'risk_level': 'MEDIUM'
            }
    
    def sanitize_html_input(self, html_str: str) -> Dict[str, Any]:
        """Sanitize HTML input to prevent XSS"""
        try:
            # HTML escape dangerous characters
            sanitized = html.escape(html_str)
            
            # Remove script tags and event handlers
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            
            return {
                'valid': True,
                'sanitized': sanitized,
                'reason': 'HTML sanitized',
                'risk_level': 'LOW'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'sanitized': '',
                'reason': f'HTML sanitization error: {str(e)}',
                'risk_level': 'HIGH'
            }
    
    def validate_security_tool_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for security tools"""
        try:
            sanitized_params = {}
            validation_results = []
            
            for key, value in params.items():
                if key == 'target':
                    # Validate target (IP or hostname)
                    if '.' in str(value) and str(value).replace('.', '').isdigit():
                        result = self.validate_ip_address(str(value))
                    else:
                        result = self.validate_hostname(str(value))
                    
                    if not result['valid']:
                        return {
                            'valid': False,
                            'reason': f"Invalid target: {result['reason']}",
                            'risk_level': result['risk_level']
                        }
                    
                    sanitized_params[key] = result['sanitized']
                    validation_results.append(result)
                
                elif key in ['port', 'timeout', 'threads']:
                    # Validate numeric parameters
                    try:
                        num_value = int(value)
                        if num_value < 1 or num_value > 65535:
                            return {
                                'valid': False,
                                'reason': f"Invalid {key}: must be between 1 and 65535",
                                'risk_level': 'MEDIUM'
                            }
                        sanitized_params[key] = num_value
                    except ValueError:
                        return {
                            'valid': False,
                            'reason': f"Invalid {key}: must be a number",
                            'risk_level': 'MEDIUM'
                        }
                
                elif key == 'output_file':
                    # Validate output file path
                    result = self.sanitize_file_path(str(value))
                    if not result['valid']:
                        return {
                            'valid': False,
                            'reason': f"Invalid output file: {result['reason']}",
                            'risk_level': result['risk_level']
                        }
                    sanitized_params[key] = result['sanitized']
                
                else:
                    # Generic string sanitization
                    result = self.sanitize_command_input(str(value))
                    if not result['valid']:
                        return {
                            'valid': False,
                            'reason': f"Invalid {key}: {result['reason']}",
                            'risk_level': result['risk_level']
                        }
                    sanitized_params[key] = result['sanitized']
            
            return {
                'valid': True,
                'sanitized_params': sanitized_params,
                'reason': 'All parameters validated',
                'risk_level': 'LOW'
            }
            
        except Exception as e:
            self.logger.error(f"Error validating security tool params: {e}")
            return {
                'valid': False,
                'reason': f'Parameter validation error: {str(e)}',
                'risk_level': 'HIGH'
            }


# Global sanitizer instance
input_sanitizer = InputSanitizer()


def sanitize_input(input_data: Any, input_type: str = 'command') -> Dict[str, Any]:
    """
    Global input sanitization function
    
    Args:
        input_data: Data to sanitize
        input_type: Type of input ('command', 'ip', 'hostname', 'file_path', 'json', 'html')
    
    Returns:
        Dict with validation results
    """
    if input_type == 'command':
        return input_sanitizer.sanitize_command_input(str(input_data))
    elif input_type == 'ip':
        return input_sanitizer.validate_ip_address(str(input_data))
    elif input_type == 'hostname':
        return input_sanitizer.validate_hostname(str(input_data))
    elif input_type == 'file_path':
        return input_sanitizer.sanitize_file_path(str(input_data))
    elif input_type == 'json':
        return input_sanitizer.sanitize_json_input(str(input_data))
    elif input_type == 'html':
        return input_sanitizer.sanitize_html_input(str(input_data))
    else:
        return input_sanitizer.sanitize_command_input(str(input_data))


# Emergency security decorator
def secure_input(input_type: str = 'command'):
    """
    Decorator to automatically sanitize function inputs
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Sanitize all string arguments
            sanitized_args = []
            for arg in args:
                if isinstance(arg, str):
                    result = sanitize_input(arg, input_type)
                    if not result['valid']:
                        raise ValueError(f"Input validation failed: {result['reason']}")
                    sanitized_args.append(result['sanitized'])
                else:
                    sanitized_args.append(arg)
            
            # Sanitize keyword arguments
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    result = sanitize_input(value, input_type)
                    if not result['valid']:
                        raise ValueError(f"Input validation failed for {key}: {result['reason']}")
                    sanitized_kwargs[key] = result['sanitized']
                else:
                    sanitized_kwargs[key] = value
            
            return func(*sanitized_args, **sanitized_kwargs)
        return wrapper
    return decorator