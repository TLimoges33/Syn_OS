#!/usr/bin/env python3
"""
Security Implementation Test Script
Tests all security components to ensure they're working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_config_manager():
    """Test the configuration manager"""
    print("🔧 Testing Configuration Manager...")
    try:
        sys.path.append('src')
        from security.config_manager import SecureConfigManager
        
        config = SecureConfigManager()
        print("  ✅ Configuration manager initialized successfully")
        
        # Test configuration validation
        if config.validate_security_config():
            print("  ✅ Security configuration validation successful")
        else:
            print("  ❌ Security configuration validation failed")
            return False
            
        return True
    except Exception as e:
        print(f"  ❌ Configuration manager test failed: {e}")
        return False

def test_jwt_auth():
    """Test JWT authentication"""
    print("🔐 Testing JWT Authentication...")
    try:
        sys.path.append('src')
        from security.jwt_auth import SecureJWTManager
        
        jwt_manager = SecureJWTManager()
        print("  ✅ JWT manager initialized successfully")
        
        # Test token generation and validation
        token = jwt_manager.create_access_token("test_user_id", "test_user", ["admin"])
        
        if token:
            print("  ✅ JWT token generation successful")
            
            # Test token validation
            decoded = jwt_manager.verify_token(token)
            if decoded and decoded.username == "test_user":
                print("  ✅ JWT token validation successful")
                return True
            else:
                print("  ❌ JWT token validation failed")
                return False
        else:
            print("  ❌ JWT token generation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ JWT authentication test failed: {e}")
        return False

def test_input_validator():
    """Test input validation"""
    print("🛡️ Testing Input Validator...")
    try:
        sys.path.append('src')
        from security.input_validator import SecureInputValidator, ValidationRule, InputType
        
        validator = SecureInputValidator()
        print("  ✅ Input validator initialized successfully")
        
        # Test SQL injection detection
        malicious_input = "'; DROP TABLE users; --"
        sql_rule = ValidationRule(input_type=InputType.SQL_SAFE, required=True)
        result = validator.validate_input(malicious_input, sql_rule)
        if not result.is_valid:
            print("  ✅ SQL injection detection working")
        else:
            print("  ❌ SQL injection detection failed")
            return False
            
        # Test XSS detection
        xss_input = "<script>alert('xss')</script>"
        html_rule = ValidationRule(input_type=InputType.HTML_SAFE, required=True)
        result = validator.validate_input(xss_input, html_rule)
        if not result.is_valid:
            print("  ✅ XSS detection working")
        else:
            print("  ❌ XSS detection failed")
            return False
            
        # Test email validation
        valid_email = "test@gmail.com"
        email_rule = ValidationRule(input_type=InputType.EMAIL, required=True)
        result = validator.validate_input(valid_email, email_rule)
        if result.is_valid:
            print("  ✅ Email validation working")
        else:
            print("  ❌ Email validation failed")
            return False
            
        return True
    except Exception as e:
        print(f"  ❌ Input validator test failed: {e}")
        return False

def test_audit_logger():
    """Test audit logging"""
    print("📝 Testing Audit Logger...")
    try:
        sys.path.append('src')
        from security.audit_logger import SecurityAuditLogger, SecurityEventType, SecurityLevel
        
        logger = SecurityAuditLogger()
        print("  ✅ Audit logger initialized successfully")
        
        # Test security event logging
        logger.log_security_event(
            event_type=SecurityEventType.SYSTEM_STARTUP,
            severity=SecurityLevel.LOW,
            user_id="test_user",
            ip_address="127.0.0.1",
            details={"test": "data"}
        )
        print("  ✅ Security event logging successful")
        
        return True
    except Exception as e:
        print(f"  ❌ Audit logger test failed: {e}")
        return False

def main():
    """Run all security tests"""
    print("🔒 Syn_OS Security Implementation Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration Manager", test_config_manager),
        ("JWT Authentication", test_jwt_auth),
        ("Input Validator", test_input_validator),
        ("Audit Logger", test_audit_logger)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"  ✅ {test_name} PASSED")
        else:
            print(f"  ❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Security Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SECURITY TESTS PASSED! System is secure and ready.")
        return 0
    else:
        print("⚠️  Some security tests failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())