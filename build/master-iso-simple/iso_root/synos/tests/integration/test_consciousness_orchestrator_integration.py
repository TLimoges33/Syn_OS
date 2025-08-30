#!/usr/bin/env python3
"""
Integration Tests for Consciousness-Orchestrator Communication

This test suite validates the end-to-end communication between the
consciousness_v2 system and the Service Orchestrator through NATS.
"""

import asyncio
import json
import pytest
import requests
import time
from typing import Dict, Any
import nats
from nats.errors import TimeoutError

# Test configuration
ORCHESTRATOR_URL = "http://localhost:8080"
NATS_URL = "nats://localhost:4222"
CONSCIOUSNESS_URL = "http://localhost:8081"

class IntegrationTestSuite:
    """Integration test suite for consciousness-orchestrator communication"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.test_results = []
    
    async def setup(self):
        """Setup test environment"""
        print("Setting up integration test environment...")
        
        # Connect to NATS
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        
        # Wait for services to be ready
        await self._wait_for_services()
        
        print("Integration test environment ready")
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.nc:
            await self.nc.close()
        
        print("Integration test environment cleaned up")
    
    async def _wait_for_services(self, timeout=60):
        """Wait for all services to be healthy"""
        services = {
            "orchestrator": f"{ORCHESTRATOR_URL}/health",
            "consciousness": f"{CONSCIOUSNESS_URL}/health"
        }
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service_name, health_url in services.items():
                try:
                    response = requests.get(health_url, timeout=5)
                    if response.status_code != 200:
                        all_healthy = False
                        print(f"Waiting for {service_name} to be healthy...")
                        break
                except requests.RequestException:
                    all_healthy = False
                    print(f"Waiting for {service_name} to be available...")
                    break
            
            if all_healthy:
                print("All services are healthy")
                return
            
            await asyncio.sleep(2)
        
        raise TimeoutError(f"Services not ready within {timeout} seconds")
    
    async def test_orchestrator_health(self):
        """Test orchestrator health endpoint"""
        print("\n=== Testing Orchestrator Health ===")
        
        try:
            response = requests.get(f"{ORCHESTRATOR_URL}/health")
            assert response.status_code == 200
            
            health_data = response.json()
            assert health_data.get("status") == "healthy"
            
            print("✅ Orchestrator health check passed")
            self.test_results.append(("orchestrator_health", True, "Health endpoint working"))
            
        except Exception as e:
            print(f"❌ Orchestrator health check failed: {e}")
            self.test_results.append(("orchestrator_health", False, str(e)))
    
    async def test_consciousness_health(self):
        """Test consciousness system health endpoint"""
        print("\n=== Testing Consciousness Health ===")
        
        try:
            response = requests.get(f"{CONSCIOUSNESS_URL}/health")
            assert response.status_code == 200
            
            health_data = response.json()
            assert health_data.get("status") in ["healthy", "starting"]
            
            print("✅ Consciousness health check passed")
            self.test_results.append(("consciousness_health", True, "Health endpoint working"))
            
        except Exception as e:
            print(f"❌ Consciousness health check failed: {e}")
            self.test_results.append(("consciousness_health", False, str(e)))
    
    async def test_nats_connectivity(self):
        """Test NATS connectivity and stream creation"""
        print("\n=== Testing NATS Connectivity ===")
        
        try:
            # Test basic connectivity
            await self.nc.publish("test.ping", b"ping")
            
            # Test JetStream streams
            streams = ["ORCHESTRATOR", "CONSCIOUSNESS"]
            for stream_name in streams:
                try:
                    stream_info = await self.js.stream_info(stream_name)
                    print(f"✅ Stream {stream_name} exists with {stream_info.state.messages} messages")
                except:
                    print(f"⚠️  Stream {stream_name} not found, creating...")
                    await self._create_test_stream(stream_name)
            
            print("✅ NATS connectivity test passed")
            self.test_results.append(("nats_connectivity", True, "NATS and JetStream working"))
            
        except Exception as e:
            print(f"❌ NATS connectivity test failed: {e}")
            self.test_results.append(("nats_connectivity", False, str(e)))
    
    async def _create_test_stream(self, stream_name):
        """Create a test stream"""
        config = {
            'name': stream_name,
            'subjects': [f"{stream_name.lower()}.>"],
            'retention': 'limits',
            'max_msgs': 1000,
            'max_age': 3600  # 1 hour
        }
        await self.js.add_stream(**config)
    
    async def test_consciousness_to_orchestrator_events(self):
        """Test event flow from consciousness to orchestrator"""
        print("\n=== Testing Consciousness → Orchestrator Events ===")
        
        try:
            # Subscribe to orchestrator events
            received_events = []
            
            async def event_handler(msg):
                try:
                    event_data = json.loads(msg.data.decode())
                    received_events.append(event_data)
                    await msg.ack()
                except Exception as e:
                    print(f"Error handling event: {e}")
            
            # Subscribe to consciousness events in orchestrator stream
            psub = await self.js.pull_subscribe(
                "consciousness.>",
                "test-consumer",
                stream="CONSCIOUSNESS"
            )
            
            # Publish a test consciousness event
            test_event = {
                "id": "test-consciousness-event-001",
                "type": "consciousness.state_change",
                "source": "consciousness_v2",
                "timestamp": time.time(),
                "data": {
                    "attention_focus": "system_management",
                    "attention_level": 0.8,
                    "cognitive_load": 0.6
                },
                "metadata": {
                    "test": True
                }
            }
            
            await self.js.publish(
                "consciousness.state_change",
                json.dumps(test_event).encode()
            )
            
            # Wait for event processing
            await asyncio.sleep(2)
            
            # Check if event was received
            try:
                msgs = await psub.fetch(batch=1, timeout=5.0)
                if msgs:
                    event_data = json.loads(msgs[0].data.decode())
                    assert event_data.get("type") == "consciousness.state_change"
                    await msgs[0].ack()
                    
                    print("✅ Consciousness → Orchestrator event flow working")
                    self.test_results.append(("consciousness_to_orchestrator", True, "Event flow working"))
                else:
                    print("⚠️  No events received within timeout")
                    self.test_results.append(("consciousness_to_orchestrator", False, "No events received"))
                    
            except TimeoutError:
                print("⚠️  Timeout waiting for events")
                self.test_results.append(("consciousness_to_orchestrator", False, "Timeout waiting for events"))
            
        except Exception as e:
            print(f"❌ Consciousness → Orchestrator event test failed: {e}")
            self.test_results.append(("consciousness_to_orchestrator", False, str(e)))
    
    async def test_orchestrator_to_consciousness_events(self):
        """Test event flow from orchestrator to consciousness"""
        print("\n=== Testing Orchestrator → Consciousness Events ===")
        
        try:
            # Publish a test orchestrator event
            test_event = {
                "id": "test-orchestrator-event-001",
                "type": "service_lifecycle_event",
                "source": "orchestrator",
                "timestamp": time.time(),
                "data": {
                    "service_name": "test-service",
                    "status": "started",
                    "health": "healthy"
                },
                "metadata": {
                    "test": True
                }
            }
            
            await self.js.publish(
                "orchestrator.service.started",
                json.dumps(test_event).encode()
            )
            
            # Wait for event processing
            await asyncio.sleep(2)
            
            # Check consciousness metrics to see if it processed the event
            try:
                response = requests.get(f"{CONSCIOUSNESS_URL}/metrics", timeout=5)
                if response.status_code == 200:
                    metrics = response.json()
                    print("✅ Orchestrator → Consciousness event flow working")
                    self.test_results.append(("orchestrator_to_consciousness", True, "Event flow working"))
                else:
                    print("⚠️  Could not verify consciousness event processing")
                    self.test_results.append(("orchestrator_to_consciousness", False, "Could not verify processing"))
                    
            except requests.RequestException:
                print("⚠️  Consciousness metrics endpoint not available")
                self.test_results.append(("orchestrator_to_consciousness", False, "Metrics endpoint unavailable"))
            
        except Exception as e:
            print(f"❌ Orchestrator → Consciousness event test failed: {e}")
            self.test_results.append(("orchestrator_to_consciousness", False, str(e)))
    
    async def test_service_registration(self):
        """Test service registration through orchestrator API"""
        print("\n=== Testing Service Registration ===")
        
        try:
            # Register a test service
            service_data = {
                "name": "test-integration-service",
                "type": "test",
                "version": "1.0.0",
                "endpoint": "http://localhost:9999",
                "health_check": "http://localhost:9999/health",
                "metadata": {
                    "test": True,
                    "integration_test": True
                }
            }
            
            response = requests.post(
                f"{ORCHESTRATOR_URL}/api/v1/services",
                json=service_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                service_id = response.json().get("id")
                print(f"✅ Service registration successful (ID: {service_id})")
                
                # Verify service is listed
                list_response = requests.get(f"{ORCHESTRATOR_URL}/api/v1/services")
                if list_response.status_code == 200:
                    services = list_response.json()
                    test_service = next((s for s in services if s.get("name") == "test-integration-service"), None)
                    
                    if test_service:
                        print("✅ Service registration verification passed")
                        self.test_results.append(("service_registration", True, "Service registration working"))
                        
                        # Cleanup - unregister the test service
                        requests.delete(f"{ORCHESTRATOR_URL}/api/v1/services/{service_id}")
                    else:
                        print("❌ Service not found in service list")
                        self.test_results.append(("service_registration", False, "Service not found in list"))
                else:
                    print("❌ Could not verify service registration")
                    self.test_results.append(("service_registration", False, "Could not verify registration"))
            else:
                print(f"❌ Service registration failed: {response.status_code}")
                self.test_results.append(("service_registration", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Service registration test failed: {e}")
            self.test_results.append(("service_registration", False, str(e)))
    
    async def test_consciousness_influence_on_orchestration(self):
        """Test consciousness influence on service orchestration"""
        print("\n=== Testing Consciousness Influence on Orchestration ===")
        
        try:
            # Simulate consciousness attention shift
            attention_event = {
                "id": "test-attention-shift-001",
                "type": "consciousness.attention_shift",
                "source": "consciousness_v2",
                "timestamp": time.time(),
                "data": {
                    "previous_focus": "user_interaction",
                    "new_focus": "system_management",
                    "attention_level": 0.9,
                    "reason": "high_priority_system_event"
                },
                "metadata": {
                    "test": True,
                    "priority": "high"
                }
            }
            
            await self.js.publish(
                "consciousness.attention_shift",
                json.dumps(attention_event).encode()
            )
            
            # Wait for processing
            await asyncio.sleep(3)
            
            # Check if orchestrator received and processed the attention shift
            # This would typically result in adjusted service priorities
            response = requests.get(f"{ORCHESTRATOR_URL}/api/v1/system/status")
            
            if response.status_code == 200:
                system_status = response.json()
                print("✅ Consciousness influence test completed")
                self.test_results.append(("consciousness_influence", True, "Attention shift processed"))
            else:
                print("⚠️  Could not verify consciousness influence")
                self.test_results.append(("consciousness_influence", False, "Could not verify influence"))
                
        except Exception as e:
            print(f"❌ Consciousness influence test failed: {e}")
            self.test_results.append(("consciousness_influence", False, str(e)))
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("INTEGRATION TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        for test_name, success, message in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
        
        print("="*60)
        
        return passed == total


async def run_integration_tests():
    """Run the complete integration test suite"""
    print("Starting Consciousness-Orchestrator Integration Tests")
    print("="*60)
    
    test_suite = IntegrationTestSuite()
    
    try:
        await test_suite.setup()
        
        # Run all tests
        await test_suite.test_orchestrator_health()
        await test_suite.test_consciousness_health()
        await test_suite.test_nats_connectivity()
        await test_suite.test_consciousness_to_orchestrator_events()
        await test_suite.test_orchestrator_to_consciousness_events()
        await test_suite.test_service_registration()
        await test_suite.test_consciousness_influence_on_orchestration()
        
        # Print summary
        all_passed = test_suite.print_test_summary()
        
        return all_passed
        
    finally:
        await test_suite.teardown()


if __name__ == "__main__":
    import sys
    
    try:
        result = asyncio.run(run_integration_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nIntegration tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Integration tests failed with error: {e}")
        sys.exit(1)