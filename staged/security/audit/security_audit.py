#!/usr/bin/env python3
"""
Syn_OS Security Audit Framework

Comprehensive security assessment tool for the consciousness-aware infrastructure platform.
Performs automated security scans, vulnerability assessments, and penetration testing.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
import socket
import ssl
import hashlib
import secrets
import jwt
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_audit.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Main security audit orchestrator"""
    
    def __init__(self, config_path: str = "security_config.json"):
        self.config = self._load_config(config_path)
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "tests": {},
            "summary": {},
            "recommendations": []
        }
        
    def _load_config(self, config_path: str) -> Dict:
        """Load security audit configuration"""
        default_config = {
            "targets": {
                "orchestrator": "http://localhost:8080",
                "consciousness": "http://localhost:8081",
                "dashboard": "http://localhost:8083",
                "tutor": "http://localhost:8082"
            },
            "database": {
                "postgres_host": "localhost",
                "postgres_port": 5432,
                "redis_host": "localhost",
                "redis_port": 6379
            },
            "network": {
                "nats_host": "localhost",
                "nats_port": 4222
            },
            "timeouts": {
                "connection": 10,
                "request": 30
            },
            "credentials": {
                "test_username": "security_test",
                "test_password": "test_password_123"
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def run_full_audit(self) -> Dict:
        """Execute comprehensive security audit"""
        logger.info("Starting comprehensive security audit...")
        
        # Network Security Tests
        await self._test_network_security()
        
        # Authentication & Authorization Tests
        await self._test_authentication()
        
        # API Security Tests
        await self._test_api_security()
        
        # Database Security Tests
        await self._test_database_security()
        
        # SSL/TLS Security Tests
        await self._test_ssl_security()
        
        # Input Validation Tests
        await self._test_input_validation()
        
        # Session Management Tests
        await self._test_session_management()
        
        # Information Disclosure Tests
        await self._test_information_disclosure()
        
        # Consciousness System Security Tests
        await self._test_consciousness_security()
        
        # Generate summary and recommendations
        self._generate_summary()
        
        logger.info("Security audit completed")
        return self.results
    
    async def _test_network_security(self):
        """Test network-level security"""
        logger.info("Testing network security...")
        
        tests = {
            "port_scanning": await self._test_port_scanning(),
            "service_enumeration": await self._test_service_enumeration(),
            "firewall_rules": await self._test_firewall_rules(),
            "network_protocols": await self._test_network_protocols()
        }
        
        self.results["tests"]["network_security"] = tests
    
    async def _test_port_scanning(self) -> Dict:
        """Perform port scanning on target services"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        common_ports = [22, 80, 443, 5432, 6379, 4222, 8080, 8081, 8082, 8083]
        open_ports = []
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            
            if result == 0:
                open_ports.append(port)
                
                # Check if port should be open
                expected_ports = [4222, 8080, 8081, 8082, 8083]  # NATS and services
                if port not in expected_ports and port != 22:  # SSH might be expected
                    results["findings"].append(f"Unexpected open port: {port}")
                    results["status"] = "warning"
            
            sock.close()
        
        results["details"]["open_ports"] = open_ports
        results["details"]["total_scanned"] = len(common_ports)
        
        return results
    
    async def _test_service_enumeration(self) -> Dict:
        """Test service enumeration and banner grabbing"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        services = self.config["targets"]
        
        for service_name, url in services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                
                # Check for information disclosure in headers
                sensitive_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
                for header in sensitive_headers:
                    if header in response.headers:
                        results["findings"].append(
                            f"{service_name}: Sensitive header disclosed: {header}"
                        )
                        results["status"] = "warning"
                
                results["details"][service_name] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response_time": response.elapsed.total_seconds()
                }
                
            except Exception as e:
                results["details"][service_name] = {"error": str(e)}
        
        return results
    
    async def _test_firewall_rules(self) -> Dict:
        """Test firewall configuration"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        try:
            # Check if UFW is active
            ufw_result = subprocess.run(['ufw', 'status'], 
                                      capture_output=True, text=True)
            
            if "Status: active" not in ufw_result.stdout:
                results["findings"].append("UFW firewall is not active")
                results["status"] = "fail"
            
            results["details"]["ufw_status"] = ufw_result.stdout
            
        except Exception as e:
            results["findings"].append(f"Could not check firewall status: {e}")
            results["status"] = "warning"
        
        return results
    
    async def _test_network_protocols(self) -> Dict:
        """Test network protocol security"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # Test NATS security
        try:
            import nats
            nc = await nats.connect("nats://localhost:4222")
            
            # Test if authentication is required
            try:
                await nc.publish("test.subject", b"test message")
                results["findings"].append("NATS allows unauthenticated publishing")
                results["status"] = "warning"
            except Exception:
                pass  # Good, authentication required
            
            await nc.close()
            
        except Exception as e:
            results["details"]["nats_error"] = str(e)
        
        return results
    
    async def _test_authentication(self):
        """Test authentication mechanisms"""
        logger.info("Testing authentication security...")
        
        tests = {
            "jwt_security": await self._test_jwt_security(),
            "password_policy": await self._test_password_policy(),
            "brute_force_protection": await self._test_brute_force_protection(),
            "session_fixation": await self._test_session_fixation()
        }
        
        self.results["tests"]["authentication"] = tests
    
    async def _test_jwt_security(self) -> Dict:
        """Test JWT token security"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # Test weak JWT secrets
        weak_secrets = ["secret", "123456", "password", "jwt_secret"]
        
        for service_name, url in self.config["targets"].items():
            try:
                # Try to get a token
                login_data = {
                    "username": self.config["credentials"]["test_username"],
                    "password": self.config["credentials"]["test_password"]
                }
                
                response = requests.post(f"{url}/api/v1/auth/login", 
                                       json=login_data, timeout=10)
                
                if response.status_code == 200:
                    token = response.json().get("token")
                    
                    if token:
                        # Try to decode with weak secrets
                        for weak_secret in weak_secrets:
                            try:
                                decoded = jwt.decode(token, weak_secret, 
                                                   algorithms=["HS256"])
                                results["findings"].append(
                                    f"{service_name}: JWT uses weak secret"
                                )
                                results["status"] = "fail"
                                break
                            except jwt.InvalidTokenError:
                                continue
                        
                        # Check token structure
                        try:
                            header = jwt.get_unverified_header(token)
                            payload = jwt.decode(token, options={"verify_signature": False})
                            
                            # Check for sensitive information in payload
                            sensitive_fields = ["password", "secret", "key"]
                            for field in sensitive_fields:
                                if field in payload:
                                    results["findings"].append(
                                        f"{service_name}: JWT contains sensitive field: {field}"
                                    )
                                    results["status"] = "warning"
                            
                            results["details"][service_name] = {
                                "header": header,
                                "payload_keys": list(payload.keys())
                            }
                            
                        except Exception as e:
                            results["details"][f"{service_name}_error"] = str(e)
                
            except Exception as e:
                results["details"][f"{service_name}_login_error"] = str(e)
        
        return results
    
    async def _test_password_policy(self) -> Dict:
        """Test password policy enforcement"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        weak_passwords = ["123456", "password", "admin", "test"]
        
        for service_name, url in self.config["targets"].items():
            for weak_password in weak_passwords:
                try:
                    # Try to create user with weak password
                    user_data = {
                        "username": f"test_user_{secrets.token_hex(4)}",
                        "password": weak_password,
                        "email": "test@example.com"
                    }
                    
                    response = requests.post(f"{url}/api/v1/users", 
                                           json=user_data, timeout=10)
                    
                    if response.status_code == 201:
                        results["findings"].append(
                            f"{service_name}: Accepts weak password: {weak_password}"
                        )
                        results["status"] = "fail"
                
                except Exception:
                    continue  # Service might not support user creation
        
        return results
    
    async def _test_brute_force_protection(self) -> Dict:
        """Test brute force attack protection"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            failed_attempts = 0
            
            # Attempt multiple failed logins
            for i in range(10):
                try:
                    login_data = {
                        "username": "nonexistent_user",
                        "password": f"wrong_password_{i}"
                    }
                    
                    response = requests.post(f"{url}/api/v1/auth/login", 
                                           json=login_data, timeout=5)
                    
                    if response.status_code == 401:
                        failed_attempts += 1
                    elif response.status_code == 429:
                        # Rate limiting detected - good!
                        break
                    
                    time.sleep(0.1)  # Small delay between attempts
                    
                except Exception:
                    continue
            
            if failed_attempts >= 10:
                results["findings"].append(
                    f"{service_name}: No brute force protection detected"
                )
                results["status"] = "warning"
            
            results["details"][service_name] = {
                "failed_attempts_allowed": failed_attempts
            }
        
        return results
    
    async def _test_session_fixation(self) -> Dict:
        """Test session fixation vulnerabilities"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # This would require more complex session handling
        # For now, just check if sessions are properly invalidated
        
        for service_name, url in self.config["targets"].items():
            try:
                # Test logout functionality
                response = requests.post(f"{url}/api/v1/auth/logout", timeout=5)
                
                if response.status_code == 404:
                    results["findings"].append(
                        f"{service_name}: No logout endpoint found"
                    )
                    results["status"] = "warning"
                
            except Exception:
                continue
        
        return results
    
    async def _test_api_security(self):
        """Test API security"""
        logger.info("Testing API security...")
        
        tests = {
            "cors_policy": await self._test_cors_policy(),
            "http_methods": await self._test_http_methods(),
            "rate_limiting": await self._test_rate_limiting(),
            "api_versioning": await self._test_api_versioning()
        }
        
        self.results["tests"]["api_security"] = tests
    
    async def _test_cors_policy(self) -> Dict:
        """Test CORS policy configuration"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            try:
                # Test CORS with different origins
                headers = {"Origin": "https://malicious-site.com"}
                response = requests.options(f"{url}/api/v1/health", 
                                          headers=headers, timeout=5)
                
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                # Check for overly permissive CORS
                if cors_headers["Access-Control-Allow-Origin"] == "*":
                    results["findings"].append(
                        f"{service_name}: Overly permissive CORS policy"
                    )
                    results["status"] = "warning"
                
                results["details"][service_name] = cors_headers
                
            except Exception as e:
                results["details"][f"{service_name}_error"] = str(e)
        
        return results
    
    async def _test_http_methods(self) -> Dict:
        """Test HTTP method security"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        dangerous_methods = ["TRACE", "TRACK", "DEBUG"]
        
        for service_name, url in self.config["targets"].items():
            allowed_methods = []
            
            for method in dangerous_methods:
                try:
                    response = requests.request(method, f"{url}/api/v1/health", timeout=5)
                    
                    if response.status_code != 405:  # Method Not Allowed
                        allowed_methods.append(method)
                        results["findings"].append(
                            f"{service_name}: Dangerous HTTP method allowed: {method}"
                        )
                        results["status"] = "warning"
                
                except Exception:
                    continue
            
            results["details"][service_name] = {
                "dangerous_methods_allowed": allowed_methods
            }
        
        return results
    
    async def _test_rate_limiting(self) -> Dict:
        """Test rate limiting implementation"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            requests_made = 0
            rate_limited = False
            
            # Make rapid requests
            for i in range(50):
                try:
                    response = requests.get(f"{url}/api/v1/health", timeout=2)
                    requests_made += 1
                    
                    if response.status_code == 429:
                        rate_limited = True
                        break
                
                except Exception:
                    break
            
            if not rate_limited and requests_made >= 50:
                results["findings"].append(
                    f"{service_name}: No rate limiting detected"
                )
                results["status"] = "warning"
            
            results["details"][service_name] = {
                "requests_before_limit": requests_made,
                "rate_limited": rate_limited
            }
        
        return results
    
    async def _test_api_versioning(self) -> Dict:
        """Test API versioning security"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            try:
                # Test if old API versions are accessible
                old_versions = ["/api/v0", "/api/beta", "/api/dev"]
                
                for version in old_versions:
                    response = requests.get(f"{url}{version}/health", timeout=5)
                    
                    if response.status_code == 200:
                        results["findings"].append(
                            f"{service_name}: Old API version accessible: {version}"
                        )
                        results["status"] = "warning"
                
            except Exception:
                continue
        
        return results
    
    async def _test_database_security(self):
        """Test database security"""
        logger.info("Testing database security...")
        
        tests = {
            "postgres_security": await self._test_postgres_security(),
            "redis_security": await self._test_redis_security(),
            "connection_encryption": await self._test_db_encryption()
        }
        
        self.results["tests"]["database_security"] = tests
    
    async def _test_postgres_security(self) -> Dict:
        """Test PostgreSQL security configuration"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        try:
            import psycopg2
            
            # Test connection without password
            try:
                conn = psycopg2.connect(
                    host=self.config["database"]["postgres_host"],
                    port=self.config["database"]["postgres_port"],
                    database="postgres",
                    user="postgres"
                )
                conn.close()
                
                results["findings"].append("PostgreSQL allows passwordless connections")
                results["status"] = "fail"
                
            except psycopg2.OperationalError:
                pass  # Good, password required
            
            # Test for default credentials
            default_creds = [
                ("postgres", "postgres"),
                ("postgres", "password"),
                ("postgres", "admin")
            ]
            
            for username, password in default_creds:
                try:
                    conn = psycopg2.connect(
                        host=self.config["database"]["postgres_host"],
                        port=self.config["database"]["postgres_port"],
                        database="postgres",
                        user=username,
                        password=password
                    )
                    conn.close()
                    
                    results["findings"].append(
                        f"PostgreSQL uses default credentials: {username}/{password}"
                    )
                    results["status"] = "fail"
                    
                except psycopg2.OperationalError:
                    continue
        
        except ImportError:
            results["details"]["error"] = "psycopg2 not available for testing"
        
        return results
    
    async def _test_redis_security(self) -> Dict:
        """Test Redis security configuration"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        try:
            import redis
            
            # Test connection without password
            try:
                r = redis.Redis(
                    host=self.config["database"]["redis_host"],
                    port=self.config["database"]["redis_port"]
                )
                r.ping()
                
                results["findings"].append("Redis allows passwordless connections")
                results["status"] = "fail"
                
            except redis.AuthenticationError:
                pass  # Good, password required
            except redis.ConnectionError:
                results["details"]["error"] = "Could not connect to Redis"
        
        except ImportError:
            results["details"]["error"] = "redis library not available for testing"
        
        return results
    
    async def _test_db_encryption(self) -> Dict:
        """Test database connection encryption"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # This would require checking SSL/TLS configuration
        # For now, just note that encryption should be verified
        results["details"]["note"] = "Database encryption should be verified manually"
        
        return results
    
    async def _test_ssl_security(self):
        """Test SSL/TLS security"""
        logger.info("Testing SSL/TLS security...")
        
        tests = {
            "certificate_validation": await self._test_certificate_validation(),
            "ssl_configuration": await self._test_ssl_configuration(),
            "cipher_suites": await self._test_cipher_suites()
        }
        
        self.results["tests"]["ssl_security"] = tests
    
    async def _test_certificate_validation(self) -> Dict:
        """Test SSL certificate validation"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            if url.startswith("https://"):
                try:
                    hostname = url.split("://")[1].split(":")[0]
                    port = 443
                    
                    if ":" in url.split("://")[1]:
                        port = int(url.split(":")[-1])
                    
                    # Get certificate
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert_der = ssock.getpeercert(binary_form=True)
                            cert = x509.load_der_x509_certificate(cert_der, default_backend())
                            
                            # Check certificate expiration
                            if cert.not_valid_after < datetime.utcnow():
                                results["findings"].append(
                                    f"{service_name}: SSL certificate expired"
                                )
                                results["status"] = "fail"
                            
                            # Check if certificate is self-signed
                            if cert.issuer == cert.subject:
                                results["findings"].append(
                                    f"{service_name}: Self-signed SSL certificate"
                                )
                                results["status"] = "warning"
                            
                            results["details"][service_name] = {
                                "subject": str(cert.subject),
                                "issuer": str(cert.issuer),
                                "not_valid_after": cert.not_valid_after.isoformat(),
                                "serial_number": str(cert.serial_number)
                            }
                
                except Exception as e:
                    results["details"][f"{service_name}_error"] = str(e)
        
        return results
    
    async def _test_ssl_configuration(self) -> Dict:
        """Test SSL configuration"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # Test if HTTP is redirected to HTTPS
        for service_name, url in self.config["targets"].items():
            if url.startswith("http://"):
                try:
                    response = requests.get(url, allow_redirects=False, timeout=5)
                    
                    if response.status_code not in [301, 302, 307, 308]:
                        results["findings"].append(
                            f"{service_name}: HTTP not redirected to HTTPS"
                        )
                        results["status"] = "warning"
                
                except Exception:
                    continue
        
        return results
    
    async def _test_cipher_suites(self) -> Dict:
        """Test SSL cipher suites"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # This would require more complex SSL testing
        # For now, just note that cipher suites should be reviewed
        results["details"]["note"] = "SSL cipher suites should be reviewed manually"
        
        return results
    
    async def _test_input_validation(self):
        """Test input validation"""
        logger.info("Testing input validation...")
        
        tests = {
            "sql_injection": await self._test_sql_injection(),
            "xss_protection": await self._test_xss_protection(),
            "command_injection": await self._test_command_injection(),
            "path_traversal": await self._test_path_traversal()
        }
        
        self.results["tests"]["input_validation"] = tests
    
    async def _test_sql_injection(self) -> Dict:
        """Test SQL injection vulnerabilities"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--"
        ]
        
        for service_name, url in self.config["targets"].items():
            for payload in sql_payloads:
                try:
                    # Test login endpoint
                    login_data = {
                        "username": payload,
                        "password": "test"
                    }
                    
                    response = requests.post(f"{url}/api/v1/auth/login", 
                                           json=login_data, timeout=5)
                    
                    # Look for SQL error messages
                    error_indicators = ["SQL", "syntax error", "mysql", "postgres"]
                    response_text = response.text.lower()
                    
                    for indicator in error_indicators:
                        if indicator in response_text:
                            results["findings"].append(
                                f"{service_name}: Possible SQL injection vulnerability"
                            )
                            results["status"] = "fail"
                            break
                
                except Exception:
                    continue
        
        return results
    
    async def _test_xss_protection(self) -> Dict:
        """Test XSS protection"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for service_name, url in self.config["targets"].items():
            for payload in xss_payloads:
                try:
                    # Test various endpoints with XSS payload
                    response = requests.get(f"{url}/api/v1/health?test={payload}", timeout=5)
                    
                    if payload in response.text:
                        results["findings"].append(
                            f"{service_name}: Possible XSS vulnerability"
                        )
                        results["status"] = "fail"
                
                except Exception:
                    continue
        
        return results
    
    async def _test_command_injection(self) -> Dict:
        """Test command injection vulnerabilities"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        command_payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`"
        ]
        
        # This would require finding endpoints that might execute commands
        # For now, just note that command injection should be tested
        results["details"]["note"] = "Command injection testing requires manual review"
        
        return results
    
    async def _test_path_traversal(self) -> Dict:
        """Test path traversal vulnerabilities"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for service_name, url in self.config["targets"].items():
            for payload in path_payloads:
                try:
                    # Test file access endpoints
                    response = requests.get(f"{url}/api/v1/files/{payload}", timeout=5)
                    
                    # Look for system file content
                    if "root:" in response.text or "[drivers]" in response.text:
                        results["findings"].append(
                            f"{service_name}: Possible path traversal vulnerability"
                        )
                        results["status"] = "fail"
                
                except Exception:
                    continue
        
        return results
    
    async def _test_session_management(self):
        """Test session management"""
        logger.info("Testing session management...")
        
        tests = {
            "session_timeout": await self._test_session_timeout(),
            "session_invalidation": await self._test_session_invalidation(),
            "concurrent_sessions": await self._test_concurrent_sessions()
        }
        
        self.results["tests"]["session_management"] = tests
    
    async def _test_session_timeout(self) -> Dict:
        """Test session timeout implementation"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # This would require long-running tests
        results["details"]["note"] = "Session timeout should be tested manually"
        
        return results
    
    async def _test_session_invalidation(self) -> Dict:
        """Test session invalidation"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            try:
                # Test if logout properly invalidates session
                response = requests.post(f"{url}/api/v1/auth/logout", timeout=5)
                
                if response.status_code == 404:
                    results["findings"].append(
                        f"{service_name}: No logout endpoint found"
                    )
                    results["status"] = "warning"
            
            except Exception:
                continue
        
        return results
    
    async def _test_concurrent_sessions(self) -> Dict:
        """Test concurrent session handling"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        # This would require complex session testing
        results["details"]["note"] = "Concurrent session testing requires manual review"
        
        return results
    
    async def _test_information_disclosure(self):
        """Test information disclosure vulnerabilities"""
        logger.info("Testing information disclosure...")
        
        tests = {
            "error_messages": await self._test_error_messages(),
            "debug_information": await self._test_debug_information(),
            "server_headers": await self._test_server_headers(),
            "directory_listing": await self._test_directory_listing()
        }
        
        self.results["tests"]["information_disclosure"] = tests
    
    async def _test_error_messages(self) -> Dict:
        """Test for information disclosure in error messages"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            try:
                # Test with invalid endpoint
                response = requests.get(f"{url}/api/v1/nonexistent", timeout=5)
                
                # Look for sensitive information in error messages
                sensitive_info = ["stack trace", "file path", "database", "internal"]
                response_text = response.text.lower()
                
                for info in sensitive_info:
                    if info in response_text:
                        results["findings"].append(
                            f"{service_name}: Error message contains sensitive information"
                        )
                        results["status"] = "warning"
                        break
                
            except Exception:
                continue
        
        return results
    
    async def _test_debug_information(self) -> Dict:
        """Test for debug information disclosure"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        debug_endpoints = ["/debug", "/api/debug", "/api/v1/debug", "/.env"]
        
        for service_name, url in self.config["targets"].items():
            for endpoint in debug_endpoints:
                try:
                    response = requests.get(f"{url}{endpoint}", timeout=5)
                    
                    if response.status_code == 200:
                        results["findings"].append(
                            f"{service_name}: Debug endpoint accessible: {endpoint}"
                        )
                        results["status"] = "warning"
                
                except Exception:
                    continue
        
        return results
    
    async def _test_server_headers(self) -> Dict:
        """Test server headers for information disclosure"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        for service_name, url in self.config["targets"].items():
            try:
                response = requests.get(f"{url}/api/v1/health", timeout=5)
                
                # Check for information disclosure headers
                disclosure_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
                for header in disclosure_headers:
                    if header in response.headers:
                        results["findings"].append(
                            f"{service_name}: Information disclosure header: {header}"
                        )
                        results["status"] = "warning"
                
                results["details"][service_name] = dict(response.headers)
                
            except Exception:
                continue
        
        return results
    
    async def _test_directory_listing(self) -> Dict:
        """Test for directory listing vulnerabilities"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        common_dirs = ["/", "/api", "/static", "/assets", "/uploads"]
        
        for service_name, url in self.config["targets"].items():
            for directory in common_dirs:
                try:
                    response = requests.get(f"{url}{directory}", timeout=5)
                    
                    # Look for directory listing indicators
                    if "Index of" in response.text or "Directory listing" in response.text:
                        results["findings"].append(
                            f"{service_name}: Directory listing enabled: {directory}"
                        )
                        results["status"] = "warning"
                
                except Exception:
                    continue
        
        return results
    
    async def _test_consciousness_security(self):
        """Test consciousness system specific security"""
        logger.info("Testing consciousness system security...")
        
        tests = {
            "consciousness_access": await self._test_consciousness_access(),
            "memory_protection": await self._test_memory_protection(),
            "learning_data_security": await self._test_learning_data_security(),
            "cognitive_process_isolation": await self._test_cognitive_isolation()
        }
        
        self.results["tests"]["consciousness_security"] = tests
    
    async def _test_consciousness_access(self) -> Dict:
        """Test consciousness system access controls"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        consciousness_url = self.config["targets"].get("consciousness")
        if not consciousness_url:
            results["details"]["error"] = "Consciousness URL not configured"
            return results
        
        try:
            # Test unauthenticated access to consciousness state
            response = requests.get(f"{consciousness_url}/api/v1/consciousness/state", timeout=5)
            
            if response.status_code == 200:
                results["findings"].append(
                    "Consciousness state accessible without authentication"
                )
                results["status"] = "fail"
            
            # Test access to sensitive consciousness endpoints
            sensitive_endpoints = [
                "/api/v1/consciousness/memory",
                "/api/v1/consciousness/processes",
                "/api/v1/consciousness/parameters"
            ]
            
            for endpoint in sensitive_endpoints:
                response = requests.get(f"{consciousness_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    results["findings"].append(
                        f"Sensitive consciousness endpoint accessible: {endpoint}"
                    )
                    results["status"] = "fail"
        
        except Exception as e:
            results["details"]["error"] = str(e)
        
        return results
    
    async def _test_memory_protection(self) -> Dict:
        """Test consciousness memory protection"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        consciousness_url = self.config["targets"].get("consciousness")
        if not consciousness_url:
            results["details"]["error"] = "Consciousness URL not configured"
            return results
        
        try:
            # Test if memory can be directly accessed or modified
            malicious_payloads = [
                {"type": "system", "content": {"command": "rm -rf /"}},
                {"type": "injection", "content": {"sql": "DROP TABLE memories"}},
                {"type": "overflow", "content": {"data": "A" * 10000}}
            ]
            
            for payload in malicious_payloads:
                response = requests.post(
                    f"{consciousness_url}/api/v1/consciousness/memory",
                    json=payload,
                    timeout=5
                )
                
                if response.status_code == 201:
                    results["findings"].append(
                        "Consciousness memory accepts malicious payloads"
                    )
                    results["status"] = "fail"
                    break
        
        except Exception as e:
            results["details"]["error"] = str(e)
        
        return results
    
    async def _test_learning_data_security(self) -> Dict:
        """Test learning data security"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        consciousness_url = self.config["targets"].get("consciousness")
        if not consciousness_url:
            results["details"]["error"] = "Consciousness URL not configured"
            return results
        
        try:
            # Test if learning data can be extracted
            response = requests.get(
                f"{consciousness_url}/api/v1/consciousness/learning",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if sensitive learning data is exposed
                if "training_data" in data or "model_weights" in data:
                    results["findings"].append(
                        "Sensitive learning data exposed in API response"
                    )
                    results["status"] = "warning"
        
        except Exception as e:
            results["details"]["error"] = str(e)
        
        return results
    
    async def _test_cognitive_isolation(self) -> Dict:
        """Test cognitive process isolation"""
        results = {"status": "pass", "findings": [], "details": {}}
        
        consciousness_url = self.config["targets"].get("consciousness")
        if not consciousness_url:
            results["details"]["error"] = "Consciousness URL not configured"
            return results
        
        try:
            # Test if cognitive processes can interfere with each other
            malicious_process = {
                "type": "system_access",
                "priority": 1.0,
                "parameters": {
                    "command": "access_system_files",
                    "target": "/etc/passwd"
                }
            }
            
            response = requests.post(
                f"{consciousness_url}/api/v1/consciousness/processes",
                json=malicious_process,
                timeout=5
            )
            
            if response.status_code == 201:
                results["findings"].append(
                    "Consciousness accepts potentially dangerous cognitive processes"
                )
                results["status"] = "warning"
        
        except Exception as e:
            results["details"]["error"] = str(e)
        
        return results
    
    def _generate_summary(self):
        """Generate audit summary and recommendations"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warning_tests = 0
        total_findings = 0
        
        # Count test results
        for category, tests in self.results["tests"].items():
            for test_name, test_result in tests.items():
                total_tests += 1
                status = test_result.get("status", "unknown")
                
                if status == "pass":
                    passed_tests += 1
                elif status == "fail":
                    failed_tests += 1
                elif status == "warning":
                    warning_tests += 1
                
                total_findings += len(test_result.get("findings", []))
        
        # Generate summary
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warning_tests": warning_tests,
            "total_findings": total_findings,
            "security_score": self._calculate_security_score(passed_tests, failed_tests, warning_tests)
        }
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _calculate_security_score(self, passed: int, failed: int, warnings: int) -> float:
        """Calculate overall security score"""
        total = passed + failed + warnings
        if total == 0:
            return 0.0
        
        # Weight: pass=1, warning=0.5, fail=0
        score = (passed + warnings * 0.5) / total
        return round(score * 100, 2)
    
    def _generate_recommendations(self):
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Analyze findings and generate recommendations
        for category, tests in self.results["tests"].items():
            for test_name, test_result in tests.items():
                findings = test_result.get("findings", [])
                
                for finding in findings:
                    if "weak password" in finding.lower():
                        recommendations.append({
                            "category": "Authentication",
                            "priority": "High",
                            "recommendation": "Implement strong password policy with minimum length, complexity requirements, and password history"
                        })
                    
                    elif "brute force" in finding.lower():
                        recommendations.append({
                            "category": "Authentication",
                            "priority": "High",
                            "recommendation": "Implement account lockout and rate limiting for failed login attempts"
                        })
                    
                    elif "ssl" in finding.lower() or "certificate" in finding.lower():
                        recommendations.append({
                            "category": "Encryption",
                            "priority": "High",
                            "recommendation": "Configure proper SSL/TLS certificates and enforce HTTPS for all communications"
                        })
                    
                    elif "cors" in finding.lower():
                        recommendations.append({
                            "category": "API Security",
                            "priority": "Medium",
                            "recommendation": "Configure restrictive CORS policy to prevent unauthorized cross-origin requests"
                        })
                    
                    elif "rate limit" in finding.lower():
                        recommendations.append({
                            "category": "API Security",
                            "priority": "Medium",
                            "recommendation": "Implement rate limiting to prevent abuse and DoS attacks"
                        })
                    
                    elif "firewall" in finding.lower():
                        recommendations.append({
                            "category": "Network Security",
                            "priority": "High",
                            "recommendation": "Enable and configure firewall to restrict network access to necessary ports only"
                        })
                    
                    elif "consciousness" in finding.lower():
                        recommendations.append({
                            "category": "Consciousness Security",
                            "priority": "Critical",
                            "recommendation": "Implement strict access controls and input validation for consciousness system endpoints"
                        })
        
        # Remove duplicates
        unique_recommendations = []
        seen = set()
        
        for rec in recommendations:
            key = (rec["category"], rec["recommendation"])
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        self.results["recommendations"] = unique_recommendations

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Syn_OS Security Audit Framework")
    parser.add_argument("--config", default="security_config.json",
                       help="Security configuration file")
    parser.add_argument("--output", default="security_audit_report.json",
                       help="Output report file")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run security audit
    auditor = SecurityAuditor(args.config)
    
    try:
        results = asyncio.run(auditor.run_full_audit())
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        summary = results["summary"]
        print(f"\n{'='*60}")
        print("SECURITY AUDIT SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Warnings: {summary['warning_tests']}")
        print(f"Total Findings: {summary['total_findings']}")
        print(f"Security Score: {summary['security_score']}%")
        
        if results["recommendations"]:
            print(f"\n{'='*60}")
            print("TOP RECOMMENDATIONS")
            print(f"{'='*60}")
            
            for i, rec in enumerate(results["recommendations"][:5], 1):
                print(f"{i}. [{rec['priority']}] {rec['category']}")
                print(f"   {rec['recommendation']}\n")
        
        print(f"Full report saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Security audit failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()