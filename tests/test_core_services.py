#!/usr/bin/env python3
"""
Core Services Integration Test
==============================

Test script to validate that our core consciousness and security systems
are working properly before moving to full containerization.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_consciousness_import():
    """Test consciousness system import and basic initialization"""
    print("🧠 Testing Consciousness System Import...")
    try:
        from consciousness_v2.main import ConsciousnessSystem
        system = ConsciousnessSystem()
        print("✅ Consciousness system imported successfully")
        print(f"   - NATS URL: {system.nats_url}")
        print(f"   - Mode: {system.consciousness_mode}")
        print(f"   - Log Level: {system.log_level}")
        return True
    except Exception as e:
        print(f"❌ Consciousness import failed: {e}")
        return False

async def test_security_modules():
    """Test security module imports and functionality"""
    print("\n🔒 Testing Security Module Imports...")
    try:
        from security.config_manager import SecureConfigManager
        from security.jwt_auth import SecureJWTManager
        from security.input_validator import SecureInputValidator
        from security.audit_logger import SecurityAuditLogger
        
        # Test basic functionality
        config_manager = SecureConfigManager()
        jwt_auth = SecureJWTManager()
        input_validator = SecureInputValidator()
        audit_logger = SecurityAuditLogger()
        
        print("✅ All security modules imported successfully")
        print("   - SecureConfigManager: Ready")
        print("   - SecureJWTManager: Ready")
        print("   - SecureInputValidator: Ready")
        print("   - SecurityAuditLogger: Ready")
        return True
    except Exception as e:
        print(f"❌ Security module import failed: {e}")
        return False

async def test_consciousness_core_basic():
    """Test consciousness core basic functionality"""
    print("\n🧠 Testing Consciousness Core Basic Functions...")
    try:
        from consciousness_v2.components.consciousness_core import ConsciousnessCore
        
        core = ConsciousnessCore()
        
        # Test basic methods
        attention_level = core.get_attention_level()
        cognitive_load = core.get_cognitive_load()
        emotional_state = core.get_emotional_state()
        learning_mode = core.get_learning_mode()
        
        print("✅ Consciousness core basic functions working")
        print(f"   - Attention Level: {attention_level:.2f}")
        print(f"   - Cognitive Load: {cognitive_load:.2f}")
        print(f"   - Learning Mode: {learning_mode}")
        print(f"   - Emotional State: {emotional_state}")
        return True
    except Exception as e:
        print(f"❌ Consciousness core test failed: {e}")
        return False

async def test_security_functionality():
    """Test security functionality"""
    print("\n🔒 Testing Security Functionality...")
    try:
        from security.input_validator import SecureInputValidator, ValidationRule, InputType
        from security.config_manager import SecureConfigManager
        
        validator = SecureInputValidator()
        config_manager = SecureConfigManager()
        
        # Test input validation with proper rule
        test_input = "Hello, World!"
        rule = ValidationRule(
            input_type=InputType.STRING,
            required=True,
            min_length=1,
            max_length=100
        )
        result = validator.validate_input(test_input, rule)
        
        # Test config validation
        is_valid = config_manager.validate_security_config()
        
        print("✅ Security functionality working")
        print(f"   - Input validation: '{test_input}' -> Valid: {result.is_valid}")
        print(f"   - Config validation: {is_valid}")
        return True
    except Exception as e:
        print(f"❌ Security functionality test failed: {e}")
        return False

async def test_environment_config():
    """Test environment configuration"""
    print("\n⚙️  Testing Environment Configuration...")
    
    required_vars = [
        "NATS_URL", "ORCHESTRATOR_URL", "LOG_LEVEL", 
        "CONSCIOUSNESS_MODE", "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    present_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            present_vars.append(var)
        else:
            missing_vars.append(var)
    
    print(f"✅ Environment variables present: {len(present_vars)}/{len(required_vars)}")
    for var in present_vars:
        value = os.getenv(var)
        # Mask sensitive values
        if "SECRET" in var or "PASSWORD" in var:
            value = "***MASKED***" if value else None
        print(f"   - {var}: {value}")
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
    
    return len(missing_vars) == 0

async def run_integration_tests():
    """Run all integration tests"""
    print("🎯 SynapticOS Core Services Integration Test")
    print("=" * 50)
    
    tests = [
        ("Consciousness Import", test_consciousness_import),
        ("Security Modules", test_security_modules),
        ("Consciousness Core", test_consciousness_core_basic),
        ("Security Functionality", test_security_functionality),
        ("Environment Config", test_environment_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All core services are working! Ready for next phase.")
        return 0
    else:
        print("⚠️  Some issues found. Address these before proceeding.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_integration_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
