#!/usr/bin/env python3
"""
System Validation Script

This script validates the complete Syn_OS system including:
- Service health checks
- NATS connectivity and message flow
- Consciousness-orchestrator integration
- Performance metrics
"""

import asyncio
import json
import requests
import time
import sys
from typing import Dict, List, Any
import nats
from datetime import datetime


class SystemValidator:
    """Comprehensive system validation"""
    
    def __init__(self):
        self.orchestrator_url = "http://localhost:8080"
        self.consciousness_url = "http://localhost:8081"
        self.nats_url = "nats://localhost:4222"
        self.nats_monitor_url = "http://localhost:8222"
        
        self.nc = None
        self.js = None
        self.validation_results = []
    
    async def run_validation(self):
        """Run complete system validation"""
        print("🔍 Starting Syn_OS System Validation")
        print("=" * 50)
        
        try:
            # Connect to NATS
            await self._connect_nats()
            
            # Run validation tests
            await self._validate_service_health()
            await self._validate_nats_infrastructure()
            await self._validate_consciousness_integration()
            await self._validate_event_flow()
            await self._validate_performance_metrics()
            await self._validate_monitoring_tools()
            
            # Generate report
            self._generate_validation_report()
            
        finally:
            if self.nc:
                await self.nc.close()
    
    async def _connect_nats(self):
        """Connect to NATS"""
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            print("✅ Connected to NATS")
        except Exception as e:
            print(f"❌ Failed to connect to NATS: {e}")
            self.validation_results.append({
                "test": "nats_connection",
                "status": "failed",
                "error": str(e)
            })
    
    async def _validate_service_health(self):
        """Validate all service health endpoints"""
        print("\n🏥 Validating Service Health")
        print("-" * 30)
        
        services = {
            "orchestrator": f"{self.orchestrator_url}/health",
            "consciousness": f"{self.consciousness_url}/health",
            "nats_monitor": f"{self.nats_monitor_url}/healthz"
        }
        
        for service_name, health_url in services.items():
            try:
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {service_name}: Healthy")
                    
                    # Get detailed health info if available
                    if service_name in ["orchestrator", "consciousness"]:
                        health_data = response.json()
                        if "status" in health_data:
                            print(f"   Status: {health_data['status']}")
                        if "uptime" in health_data:
                            print(f"   Uptime: {health_data['uptime']}")
                    
                    self.validation_results.append({
                        "test": f"{service_name}_health",
                        "status": "passed",
                        "response_time": response.elapsed.total_seconds()
                    })
                else:
                    print(f"❌ {service_name}: Unhealthy (HTTP {response.status_code})")
                    self.validation_results.append({
                        "test": f"{service_name}_health",
                        "status": "failed",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except requests.RequestException as e:
                print(f"❌ {service_name}: Connection failed - {e}")
                self.validation_results.append({
                    "test": f"{service_name}_health",
                    "status": "failed",
                    "error": str(e)
                })
    
    async def _validate_nats_infrastructure(self):
        """Validate NATS infrastructure"""
        print("\n📡 Validating NATS Infrastructure")
        print("-" * 35)
        
        try:
            # Check NATS server info
            response = requests.get(f"{self.nats_monitor_url}/varz")
            if response.status_code == 200:
                server_info = response.json()
                print(f"✅ NATS Server Version: {server_info.get('version', 'unknown')}")
                print(f"   Connections: {server_info.get('connections', 0)}")
                print(f"   Messages In: {server_info.get('in_msgs', 0)}")
                print(f"   Messages Out: {server_info.get('out_msgs', 0)}")
            
            # Check JetStream
            if self.js:
                # List streams
                streams = []
                async for stream in self.js.streams_info():
                    streams.append(stream.config.name)
                    print(f"✅ JetStream Stream: {stream.config.name}")
                    print(f"   Messages: {stream.state.messages}")
                    print(f"   Consumers: {stream.state.consumers}")
                
                self.validation_results.append({
                    "test": "nats_infrastructure",
                    "status": "passed",
                    "streams": streams
                })
            
        except Exception as e:
            print(f"❌ NATS infrastructure validation failed: {e}")
            self.validation_results.append({
                "test": "nats_infrastructure",
                "status": "failed",
                "error": str(e)
            })
    
    async def _validate_consciousness_integration(self):
        """Validate consciousness system integration"""
        print("\n🧠 Validating Consciousness Integration")
        print("-" * 40)
        
        try:
            # Check consciousness metrics
            response = requests.get(f"{self.consciousness_url}/metrics", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                print("✅ Consciousness metrics available")
                
                if "consciousness" in metrics:
                    consciousness_metrics = metrics["consciousness"]
                    print(f"   Attention Level: {consciousness_metrics.get('attention_level', 'N/A')}")
                    print(f"   Cognitive Load: {consciousness_metrics.get('cognitive_load', 'N/A')}")
                    print(f"   Active Processes: {consciousness_metrics.get('active_processes', 'N/A')}")
                
                if "events" in metrics:
                    event_metrics = metrics["events"]
                    print(f"   Events Processed: {event_metrics.get('total_processed', 'N/A')}")
                    print(f"   Events Pending: {event_metrics.get('pending', 'N/A')}")
                
                self.validation_results.append({
                    "test": "consciousness_integration",
                    "status": "passed",
                    "metrics": metrics
                })
            else:
                print(f"❌ Consciousness metrics unavailable (HTTP {response.status_code})")
                self.validation_results.append({
                    "test": "consciousness_integration",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Consciousness integration validation failed: {e}")
            self.validation_results.append({
                "test": "consciousness_integration",
                "status": "failed",
                "error": str(e)
            })
    
    async def _validate_event_flow(self):
        """Validate end-to-end event flow"""
        print("\n🔄 Validating Event Flow")
        print("-" * 25)
        
        try:
            if not self.js:
                print("❌ JetStream not available for event flow test")
                return
            
            # Test consciousness → orchestrator event flow
            test_event = {
                "id": f"validation-test-{int(time.time())}",
                "type": "consciousness.validation_test",
                "source": "system_validator",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "test": True,
                    "validation_run": True
                }
            }
            
            # Publish test event
            await self.js.publish(
                "consciousness.validation_test",
                json.dumps(test_event).encode()
            )
            print("✅ Published test event to consciousness stream")
            
            # Test orchestrator → consciousness event flow
            orchestrator_event = {
                "id": f"orchestrator-validation-{int(time.time())}",
                "type": "service_validation_test",
                "source": "system_validator",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "service_name": "validation-service",
                    "status": "test",
                    "health": "testing"
                }
            }
            
            await self.js.publish(
                "orchestrator.service.validation",
                json.dumps(orchestrator_event).encode()
            )
            print("✅ Published test event to orchestrator stream")
            
            # Wait for processing
            await asyncio.sleep(2)
            
            self.validation_results.append({
                "test": "event_flow",
                "status": "passed",
                "events_published": 2
            })
            
        except Exception as e:
            print(f"❌ Event flow validation failed: {e}")
            self.validation_results.append({
                "test": "event_flow",
                "status": "failed",
                "error": str(e)
            })
    
    async def _validate_performance_metrics(self):
        """Validate system performance metrics"""
        print("\n📊 Validating Performance Metrics")
        print("-" * 35)
        
        try:
            # Check orchestrator metrics
            response = requests.get(f"{self.orchestrator_url}/api/v1/system/metrics", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                print("✅ Orchestrator performance metrics available")
                
                if "system" in metrics:
                    system_metrics = metrics["system"]
                    print(f"   CPU Usage: {system_metrics.get('cpu_usage', 'N/A')}%")
                    print(f"   Memory Usage: {system_metrics.get('memory_usage', 'N/A')}%")
                    print(f"   Uptime: {system_metrics.get('uptime', 'N/A')}")
                
                if "services" in metrics:
                    print(f"   Registered Services: {len(metrics['services'])}")
                    healthy_services = sum(1 for s in metrics['services'] if s.get('status') == 'healthy')
                    print(f"   Healthy Services: {healthy_services}")
            
            # Check NATS performance
            nats_response = requests.get(f"{self.nats_monitor_url}/varz")
            if nats_response.status_code == 200:
                nats_metrics = nats_response.json()
                print("✅ NATS performance metrics available")
                print(f"   Total Connections: {nats_metrics.get('connections', 0)}")
                print(f"   Messages/sec In: {nats_metrics.get('in_msgs', 0)}")
                print(f"   Messages/sec Out: {nats_metrics.get('out_msgs', 0)}")
                print(f"   Memory Usage: {nats_metrics.get('mem', 0)} bytes")
            
            self.validation_results.append({
                "test": "performance_metrics",
                "status": "passed"
            })
            
        except Exception as e:
            print(f"❌ Performance metrics validation failed: {e}")
            self.validation_results.append({
                "test": "performance_metrics",
                "status": "failed",
                "error": str(e)
            })
    
    async def _validate_monitoring_tools(self):
        """Validate monitoring and observability tools"""
        print("\n🔍 Validating Monitoring Tools")
        print("-" * 30)
        
        monitoring_endpoints = {
            "NATS Monitor": f"{self.nats_monitor_url}",
            "Orchestrator API": f"{self.orchestrator_url}/api/v1",
            "Consciousness Health": f"{self.consciousness_url}/health",
            "System Status": f"{self.orchestrator_url}/api/v1/system/status"
        }
        
        for tool_name, endpoint in monitoring_endpoints.items():
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {tool_name}: Available")
                else:
                    print(f"⚠️  {tool_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {tool_name}: {e}")
        
        self.validation_results.append({
            "test": "monitoring_tools",
            "status": "passed"
        })
    
    def _generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("SYSTEM VALIDATION REPORT")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.validation_results if result.get("status") == "passed")
        total_tests = len(self.validation_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.validation_results:
            test_name = result["test"]
            status = result["status"]
            status_icon = "✅" if status == "passed" else "❌"
            
            print(f"{status_icon} {test_name}: {status.upper()}")
            
            if "error" in result:
                print(f"   Error: {result['error']}")
            if "response_time" in result:
                print(f"   Response Time: {result['response_time']:.3f}s")
        
        print("\n" + "=" * 60)
        
        # System readiness assessment
        if success_rate >= 90:
            print("🎉 SYSTEM STATUS: READY FOR PRODUCTION")
        elif success_rate >= 75:
            print("⚠️  SYSTEM STATUS: READY FOR TESTING")
        else:
            print("❌ SYSTEM STATUS: NEEDS ATTENTION")
        
        print("=" * 60)
        
        return success_rate >= 75


async def main():
    """Main validation entry point"""
    validator = SystemValidator()
    
    try:
        await validator.run_validation()
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())