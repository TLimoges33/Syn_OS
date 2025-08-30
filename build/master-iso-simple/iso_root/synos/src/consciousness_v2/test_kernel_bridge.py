#!/usr/bin/env python3
"""
Consciousness-Kernel Bridge Integration Test
==========================================

This test verifies the bidirectional communication between the 
consciousness system and the kernel through the bridge.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any

from .bridges.kernel_bridge import KernelBridge, KernelEventType, ConsciousnessResponseType
from .core.consciousness_bus import ConsciousnessBus
from .core.event_types import EventType, EventPriority, create_security_event
from .core.data_models import create_default_consciousness_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('synapticos.kernel_bridge_test')


class MockKernelClient:
    """Mock kernel client for testing"""
    
    def __init__(self, bridge_port: int = 8900):
        self.bridge_port = bridge_port
        self.reader = None
        self.writer = None
        self.messages_received = []
    
    async def connect(self) -> bool:
        """Connect to bridge"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                'localhost', self.bridge_port
            )
            logger.info("Mock kernel client connected to bridge")
            return True
        except Exception as e:
            logger.error(f"Failed to connect mock kernel client: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from bridge"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        logger.info("Mock kernel client disconnected")
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message to bridge"""
        try:
            # Serialize message
            message_json = json.dumps(message)
            message_data = message_json.encode('utf-8')
            
            # Send length prefix + data
            import struct
            length_prefix = struct.pack('!I', len(message_data))
            self.writer.write(length_prefix + message_data)
            await self.writer.drain()
            
            logger.info(f"Sent message: {message.get('event_type')}")
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive message from bridge"""
        try:
            # Read length prefix
            import struct
            length_data = await self.reader.readexactly(4)
            message_length = struct.unpack('!I', length_data)[0]
            
            # Read message data
            message_data = await self.reader.readexactly(message_length)
            message_json = message_data.decode('utf-8')
            message = json.loads(message_json)
            
            self.messages_received.append(message)
            logger.info(f"Received message: {message.get('type', 'unknown')}")
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return {}
    
    async def listen_for_responses(self, duration: float = 5.0) -> None:
        """Listen for responses from bridge"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Check if data is available
                if self.reader.at_eof():
                    break
                
                # Try to receive message with timeout
                try:
                    message = await asyncio.wait_for(self.receive_message(), timeout=1.0)
                    if message:
                        logger.info(f"Response received: {message.get('response_type', 'unknown')}")
                except asyncio.TimeoutError:
                    continue
                    
            except Exception as e:
                logger.error(f"Error listening for responses: {e}")
                break


async def test_bridge_initialization():
    """Test bridge initialization"""
    logger.info("=== Testing Bridge Initialization ===")
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create bridge
    bridge = KernelBridge(consciousness_bus)
    
    # Initialize and start bridge
    success = await bridge.start()
    assert success, "Bridge should start successfully"
    
    # Check status
    status = await bridge.get_bridge_status()
    assert status['is_running'], "Bridge should be running"
    assert status['component_id'] == 'kernel_bridge', "Component ID should be correct"
    
    logger.info("✅ Bridge initialization test passed")
    
    # Clean up
    await bridge.stop()
    await consciousness_bus.stop()


async def test_security_event_flow():
    """Test security event communication"""
    logger.info("=== Testing Security Event Flow ===")
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create bridge
    bridge = KernelBridge(consciousness_bus, bridge_port=8901)
    await bridge.start()
    
    # Create mock kernel client
    mock_kernel = MockKernelClient(bridge_port=8901)
    
    try:
        # Connect mock kernel
        connected = await mock_kernel.connect()
        assert connected, "Mock kernel should connect"
        
        # Wait for welcome message
        welcome = await mock_kernel.receive_message()
        assert welcome.get('type') == 'connection_established', "Should receive welcome"
        
        # Send security alert from "kernel"
        security_alert = {
            'id': 'test_security_001',
            'event_type': 'security_alert',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'alert_type': 'unauthorized_access',
                'severity': '8',
                'details': 'Suspicious process attempting privilege escalation',
                'process_id': '1234'
            },
            'priority': 1,
            'requires_response': True
        }
        
        await mock_kernel.send_message(security_alert)
        
        # Wait for processing
        await asyncio.sleep(2.0)
        
        # Listen for response
        await mock_kernel.listen_for_responses(duration=3.0)
        
        # Check if response was received
        assert len(mock_kernel.messages_received) >= 2, "Should receive welcome + response"
        
        logger.info("✅ Security event flow test passed")
        
    finally:
        await mock_kernel.disconnect()
        await bridge.stop()
        await consciousness_bus.stop()


async def test_memory_pressure_handling():
    """Test memory pressure event handling"""
    logger.info("=== Testing Memory Pressure Handling ===")
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create bridge
    bridge = KernelBridge(consciousness_bus, bridge_port=8902)
    await bridge.start()
    
    # Create mock kernel client
    mock_kernel = MockKernelClient(bridge_port=8902)
    
    try:
        # Connect mock kernel
        await mock_kernel.connect()
        
        # Wait for welcome message
        await mock_kernel.receive_message()
        
        # Send memory pressure alert
        memory_alert = {
            'id': 'test_memory_001',
            'event_type': 'memory_pressure',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'available_memory': '52428800',  # 50MB
                'total_memory': '1073741824',   # 1GB
                'fragmentation': '0.75',
                'pressure_level': 'high'
            },
            'priority': 2,
            'requires_response': True
        }
        
        await mock_kernel.send_message(memory_alert)
        
        # Wait for processing and response
        await asyncio.sleep(2.0)
        await mock_kernel.listen_for_responses(duration=3.0)
        
        # Verify response received
        responses = [msg for msg in mock_kernel.messages_received 
                    if msg.get('response_type') == 'memory_optimization']
        
        assert len(responses) > 0, "Should receive memory optimization response"
        
        logger.info("✅ Memory pressure handling test passed")
        
    finally:
        await mock_kernel.disconnect()
        await bridge.stop()
        await consciousness_bus.stop()


async def test_educational_request_handling():
    """Test educational request handling"""
    logger.info("=== Testing Educational Request Handling ===")
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create bridge
    bridge = KernelBridge(consciousness_bus, bridge_port=8903)
    await bridge.start()
    
    # Create mock kernel client
    mock_kernel = MockKernelClient(bridge_port=8903)
    
    try:
        # Connect mock kernel
        await mock_kernel.connect()
        
        # Wait for welcome message
        await mock_kernel.receive_message()
        
        # Send educational request
        edu_request = {
            'id': 'test_edu_001',
            'event_type': 'educational_request',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'topic': 'buffer_overflow',
                'level': 'intermediate',
                'user_context': 'cybersecurity_student',
                'privilege_level': '1'
            },
            'priority': 4,
            'requires_response': True
        }
        
        await mock_kernel.send_message(edu_request)
        
        # Wait for processing and response
        await asyncio.sleep(2.0)
        await mock_kernel.listen_for_responses(duration=3.0)
        
        # Verify educational response received
        responses = [msg for msg in mock_kernel.messages_received 
                    if msg.get('response_type') == 'educational_response']
        
        assert len(responses) > 0, "Should receive educational response"
        
        logger.info("✅ Educational request handling test passed")
        
    finally:
        await mock_kernel.disconnect()
        await bridge.stop()
        await consciousness_bus.stop()


async def test_bridge_statistics():
    """Test bridge statistics collection"""
    logger.info("=== Testing Bridge Statistics ===")
    
    # Create consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.start()
    
    # Create bridge
    bridge = KernelBridge(consciousness_bus, bridge_port=8904)
    await bridge.start()
    
    # Get initial statistics
    initial_stats = await bridge.get_bridge_status()
    assert 'statistics' in initial_stats, "Should have statistics"
    
    # Create mock kernel client
    mock_kernel = MockKernelClient(bridge_port=8904)
    
    try:
        # Connect and send some messages
        await mock_kernel.connect()
        await mock_kernel.receive_message()  # Welcome message
        
        # Send multiple test messages
        for i in range(3):
            test_message = {
                'id': f'test_stats_{i}',
                'event_type': 'system_performance',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'cpu_usage': '0.5',
                    'memory_usage': '0.3',
                    'io_load': '0.1',
                    'active_processes': '42'
                },
                'priority': 5,
                'requires_response': False
            }
            await mock_kernel.send_message(test_message)
            await asyncio.sleep(0.5)
        
        # Wait for processing
        await asyncio.sleep(2.0)
        
        # Get updated statistics
        final_stats = await bridge.get_bridge_status()
        
        # Verify statistics updated
        assert final_stats['statistics']['messages_received'] >= 3, "Should track received messages"
        assert final_stats['connected_clients'] >= 1, "Should track connected clients"
        
        logger.info("✅ Bridge statistics test passed")
        
    finally:
        await mock_kernel.disconnect()
        await bridge.stop()
        await consciousness_bus.stop()


async def run_all_tests():
    """Run all bridge tests"""
    logger.info("🧠 Starting Consciousness-Kernel Bridge Tests")
    logger.info("=" * 50)
    
    test_functions = [
        test_bridge_initialization,
        test_security_event_flow,
        test_memory_pressure_handling,
        test_educational_request_handling,
        test_bridge_statistics
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            logger.error(f"❌ Test {test_func.__name__} failed: {e}")
            failed += 1
        
        # Small delay between tests
        await asyncio.sleep(1.0)
    
    logger.info("=" * 50)
    logger.info(f"🧠 Bridge Tests Complete: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All bridge tests passed! Consciousness-kernel integration is working.")
    else:
        logger.error(f"⚠️  {failed} bridge tests failed. Check logs for details.")
    
    return failed == 0


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)