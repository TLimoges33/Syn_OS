#!/usr/bin/env python3
"""
Security Integration Test Suite
==============================

Tests the unified security layer integration between Rust kernel security
and Python consciousness-aware security system.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Import our security integration components
try:
    from .security_integration_bridge import (
        SecurityIntegrationBridge, SecurityEvent, SecurityContext, 
        SecurityLevel, Capability, SecurityOperation
    )
    from ..consciousness_v2.core.consciousness_bus import ConsciousnessBus
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Security integration components not available: {e}")
    COMPONENTS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('synapticos.security.integration_test')


class MockKernelSecurityClient:
    """Mock kernel security client for testing"""
    
    def __init__(self, bridge_port: int = 8950):
        self.bridge_port = bridge_port
        self.reader = None
        self.writer = None
        self.responses_received = []
    
    async def connect(self) -> bool:
        """Connect to security integration bridge"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                'localhost', self.bridge_port
            )
            logger.info("Mock kernel security client connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from bridge"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        logger.info("Mock kernel security client disconnected")
    
    async def send_security_event(self, event_data: Dict[str, Any]) -> None:
        """Send security event to bridge"""
        try:
            import struct
            message_json = json.dumps(event_data)
            message_data = message_json.encode('utf-8')
            
            length_prefix = struct.pack('!I', len(message_data))
            self.writer.write(length_prefix + message_data)
            await self.writer.drain()
            
            logger.info(f"Sent security event: {event_data.get('operation_type')}")
            
        except Exception as e:
            logger.error(f"Failed to send security event: {e}")
    
    async def receive_response(self, timeout: float = 5.0) -> Dict[str, Any]:
        """Receive response from bridge"""
        try:
            import struct
            
            # Wait for response with timeout
            length_data = await asyncio.wait_for(
                self.reader.readexactly(4), timeout=timeout
            )
            message_length = struct.unpack('!I', length_data)[0]
            
            message_data = await asyncio.wait_for(
                self.reader.readexactly(message_length), timeout=timeout
            )
            
            message = json.loads(message_data.decode('utf-8'))
            self.responses_received.append(message)
            
            logger.info(f"Received response: {message.get('response_type', 'unknown')}")
            return message
            
        except asyncio.TimeoutError:
            logger.warning("Response timeout")
            return {}
        except Exception as e:
            logger.error(f"Failed to receive response: {e}")
            return {}


async def test_security_bridge_initialization():
    """Test security bridge initialization"""
    logger.info("=== Testing Security Bridge Initialization ===")
    
    if not COMPONENTS_AVAILABLE:
        logger.warning("Components not available - skipping test")
        return False
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create security integration bridge
    bridge = SecurityIntegrationBridge(consciousness_bus, security_port=8951)
    
    # Initialize bridge
    success = await bridge.initialize()
    assert success, "Security bridge should initialize successfully"
    
    # Check status
    status = await bridge.get_security_status()
    assert status['bridge_status'] == 'active', "Bridge should be active"
    assert status['consciousness_available'], "Consciousness should be available"
    
    logger.info("✅ Security bridge initialization test passed")
    
    # Clean up
    await bridge.stop()
    await consciousness_bus.stop()
    
    return True


async def test_security_context_creation():
    """Test security context creation and validation"""
    logger.info("=== Testing Security Context Creation ===")
    
    if not COMPONENTS_AVAILABLE:
        logger.warning("Components not available - skipping test")
        return False
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create security integration bridge
    bridge = SecurityIntegrationBridge(consciousness_bus, security_port=8952)
    await bridge.initialize()
    
    try:
        # Test different security contexts
        contexts = [
            {
                'user_id': 1000,
                'process_id': 1234,
                'capabilities': [Capability.READ_MEMORY, Capability.EXECUTE_CODE]
            },
            {
                'user_id': 0,  # root
                'process_id': 1,
                'capabilities': [Capability.ADMIN_ACCESS, Capability.SYSTEM_CALL]
            },
            {
                'user_id': 1001,
                'process_id': 5678,
                'capabilities': [Capability.NETWORK_ACCESS, Capability.FILESYSTEM_ACCESS]
            }
        ]
        
        created_contexts = []
        
        for ctx_data in contexts:
            context = await bridge.create_security_context(
                ctx_data['user_id'],
                ctx_data['process_id'],
                ctx_data['capabilities']
            )
            
            created_contexts.append(context)
            
            # Validate the context
            assert context.user_id == ctx_data['user_id'], "User ID should match"
            assert context.process_id == ctx_data['process_id'], "Process ID should match"
            assert context.security_level is not None, "Security level should be assigned"
            
            logger.info(f"Created context for user {context.user_id}: level {context.security_level.name}")
        
        # Test context validation
        for context in created_contexts:
            for cap in context.capabilities:
                valid = await bridge.validate_operation(
                    context, SecurityOperation.AUTHORIZATION, cap
                )
                assert valid, f"Should be authorized for own capabilities"
        
        logger.info("✅ Security context creation test passed")
        
    finally:
        await bridge.stop()
        await consciousness_bus.stop()
    
    return True


async def test_threat_detection_flow():
    """Test threat detection and response flow"""
    logger.info("=== Testing Threat Detection Flow ===")
    
    if not COMPONENTS_AVAILABLE:
        logger.warning("Components not available - skipping test")
        return False
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create security integration bridge
    bridge = SecurityIntegrationBridge(consciousness_bus, security_port=8953)
    await bridge.initialize()
    
    try:
        # Create security context
        context = await bridge.create_security_context(
            user_id=1002,
            process_id=9999,
            capabilities=[Capability.READ_MEMORY, Capability.EXECUTE_CODE]
        )
        
        # Create high-severity threat event
        threat_event = SecurityEvent(
            event_id="test_threat_001",
            event_type=SecurityOperation.THREAT_DETECTION,
            timestamp=datetime.now(),
            source_component="test_kernel",
            security_context=context,
            data={
                'threat_type': 'buffer_overflow_attempt',
                'confidence': '0.95',
                'evidence': 'Stack canary corruption detected',
                'memory_address': '0x7fff12345678'
            },
            severity=4,  # Critical
            requires_response=True
        )
        
        # Handle the threat event
        response = await bridge.handle_security_event(threat_event)
        
        # Verify response
        assert response is not None, "Should receive threat response"
        assert response.original_event_id == threat_event.event_id, "Response should match event"
        assert len(response.actions) > 0, "Should have security actions"
        
        # Check if isolation action is included for critical threat
        isolation_actions = [a for a in response.actions if 'isolate' in a.get('type', '')]
        assert len(isolation_actions) > 0, "Should include isolation action for critical threat"
        
        logger.info("✅ Threat detection flow test passed")
        
    finally:
        await bridge.stop()
        await consciousness_bus.stop()
    
    return True


async def test_educational_security_demo():
    """Test educational security demonstrations"""
    logger.info("=== Testing Educational Security Demo ===")
    
    if not COMPONENTS_AVAILABLE:
        logger.warning("Components not available - skipping test")
        return False
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create security integration bridge
    bridge = SecurityIntegrationBridge(consciousness_bus, security_port=8954)
    await bridge.initialize()
    
    try:
        # Create security context for student
        context = await bridge.create_security_context(
            user_id=2000,  # Student user
            process_id=1111,
            capabilities=[Capability.READ_MEMORY, Capability.EXECUTE_CODE]
        )
        
        # Test different educational concepts
        concepts = [
            "privilege_escalation",
            "isolation_domains", 
            "threat_detection"
        ]
        
        for concept in concepts:
            demo_result = await bridge.demonstrate_security_concept(concept, context)
            
            assert 'concept' in demo_result, "Demo should include concept"
            assert 'educational_content' in demo_result, "Demo should include educational content"
            assert demo_result['concept'] == concept, "Concept should match"
            
            logger.info(f"Educational demo completed: {concept}")
        
        # Check statistics
        status = await bridge.get_security_status()
        assert status['statistics']['educational_demos'] >= len(concepts), "Should track educational demos"
        
        logger.info("✅ Educational security demo test passed")
        
    finally:
        await bridge.stop()
        await consciousness_bus.stop()
    
    return True


async def test_policy_enforcement():
    """Test security policy enforcement"""
    logger.info("=== Testing Security Policy Enforcement ===")
    
    if not COMPONENTS_AVAILABLE:
        logger.warning("Components not available - skipping test")
        return False
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create security integration bridge
    bridge = SecurityIntegrationBridge(consciousness_bus, security_port=8955)
    await bridge.initialize()
    
    try:
        # Create restricted security context
        context = await bridge.create_security_context(
            user_id=3000,
            process_id=2222,
            capabilities=[Capability.READ_MEMORY]  # Limited capabilities
        )
        
        # Test authorized operation
        authorized = await bridge.validate_operation(
            context, SecurityOperation.AUTHORIZATION, Capability.READ_MEMORY
        )
        assert authorized, "Should authorize allowed capability"
        
        # Test unauthorized operation
        unauthorized = await bridge.validate_operation(
            context, SecurityOperation.AUTHORIZATION, Capability.ADMIN_ACCESS
        )
        assert not unauthorized, "Should deny unauthorized capability"
        
        # Check policy violation statistics
        status = await bridge.get_security_status()
        assert status['statistics']['policy_violations'] >= 1, "Should track policy violations"
        
        logger.info("✅ Security policy enforcement test passed")
        
    finally:
        await bridge.stop()
        await consciousness_bus.stop()
    
    return True


async def test_consciousness_integration():
    """Test consciousness system integration"""
    logger.info("=== Testing Consciousness Integration ===")
    
    if not COMPONENTS_AVAILABLE:
        logger.warning("Components not available - skipping test")
        return False
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create security integration bridge
    bridge = SecurityIntegrationBridge(consciousness_bus, security_port=8956)
    await bridge.initialize()
    
    try:
        # Create security context
        context = await bridge.create_security_context(
            user_id=4000,
            process_id=3333,
            capabilities=[Capability.NETWORK_ACCESS]
        )
        
        # Create security event that triggers consciousness analysis
        security_event = SecurityEvent(
            event_id="test_consciousness_001",
            event_type=SecurityOperation.THREAT_DETECTION,
            timestamp=datetime.now(),
            source_component="test_component",
            security_context=context,
            data={
                'suspicious_activity': 'unusual_network_pattern',
                'pattern_analysis': 'potential_data_exfiltration',
                'confidence': '0.75'
            },
            severity=3,  # High severity
            requires_response=True
        )
        
        # Handle event - should trigger consciousness analysis
        response = await bridge.handle_security_event(security_event)
        
        # Verify consciousness involvement
        status = await bridge.get_security_status()
        assert status['statistics']['consciousness_decisions'] >= 1, "Should involve consciousness"
        
        # Wait for event processing
        await asyncio.sleep(2.0)
        
        logger.info("✅ Consciousness integration test passed")
        
    finally:
        await bridge.stop()
        await consciousness_bus.stop()
    
    return True


async def run_all_security_integration_tests():
    """Run all security integration tests"""
    logger.info("🔒 Starting Security Integration Test Suite")
    logger.info("=" * 60)
    
    test_functions = [
        test_security_bridge_initialization,
        test_security_context_creation,
        test_threat_detection_flow,
        test_educational_security_demo,
        test_policy_enforcement,
        test_consciousness_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            success = await test_func()
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Test {test_func.__name__} failed: {e}")
            failed += 1
        
        # Small delay between tests
        await asyncio.sleep(1.0)
    
    logger.info("=" * 60)
    logger.info(f"🔒 Security Integration Tests Complete: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All security integration tests passed! Security layer is working.")
    else:
        logger.error(f"⚠️  {failed} security tests failed. Check logs for details.")
    
    return failed == 0


if __name__ == "__main__":
    # Run the security integration tests
    success = asyncio.run(run_all_security_integration_tests())
    exit(0 if success else 1)