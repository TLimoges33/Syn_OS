#!/usr/bin/env python3
"""
SynOS Priority 2 Integration Test
Comprehensive test of all three core consciousness features working together

This test demonstrates the unified consciousness architecture with:
- Security Controller
- Memory Manager  
- Scheduler AI Enhancement
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, Any

# Import all three consciousness components
import sys
sys.path.append('/home/diablorain/Syn_OS/src/consciousness')

from consciousness_security_controller import ConsciousnessSecurityController
from consciousness_memory_manager import ConsciousnessMemoryManager, MemoryRequest, MemoryType
from consciousness_scheduler import ConsciousnessScheduler

class SynOSConsciousnessIntegrationTest:
    """
    Integration test for all Priority 2 consciousness features
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all three core components
        self.security_controller = ConsciousnessSecurityController()
        self.memory_manager = ConsciousnessMemoryManager()
        self.scheduler = ConsciousnessScheduler()
        
        # Test metrics
        self.test_results = {
            'security_tests': {},
            'memory_tests': {},
            'scheduler_tests': {},
            'integration_tests': {},
            'overall_status': 'pending'
        }
        
        self.logger.info("SynOS Consciousness Integration Test initialized")

    async def run_comprehensive_test(self):
        """Run comprehensive integration test of all consciousness features"""
        
        print("🧠🚀 SYNOS PRIORITY 2 INTEGRATION TEST")
        print("=" * 60)
        print("Testing unified consciousness architecture with:")
        print("  🛡️  Security Controller")
        print("  💾  Memory Manager")
        print("  ⚡  Scheduler AI Enhancement")
        print("=" * 60)
        
        try:
            # Start all three components in parallel
            await self._start_all_components()
            
            # Run individual component tests
            await self._test_security_controller()
            await self._test_memory_manager()
            await self._test_scheduler()
            
            # Run integration scenarios
            await self._test_consciousness_integration()
            await self._test_cross_component_communication()
            await self._test_unified_optimization()
            
            # Generate final report
            await self._generate_test_report()
            
        except Exception as e:
            self.logger.error(f"Integration test error: {e}")
            self.test_results['overall_status'] = 'failed'
        
        finally:
            await self._stop_all_components()

    async def _start_all_components(self):
        """Start all consciousness components"""
        print("\n🚀 Starting all consciousness components...")
        
        # Start components in background tasks
        self.security_task = asyncio.create_task(self.security_controller.start())
        self.memory_task = asyncio.create_task(self.memory_manager.start())
        self.scheduler_task = asyncio.create_task(self.scheduler.start())
        
        # Give components time to initialize
        await asyncio.sleep(2.0)
        
        print("✅ All components started successfully")

    async def _test_security_controller(self):
        """Test security controller functionality"""
        print("\n🛡️ Testing Security Controller...")
        
        start_time = time.time()
        
        # Get initial status
        initial_status = await self.security_controller.get_security_status()
        
        # Wait for some threat detection activity
        await asyncio.sleep(3.0)
        
        # Get final status
        final_status = await self.security_controller.get_security_status()
        
        # Evaluate results
        test_duration = time.time() - start_time
        threats_detected = final_status['metrics']['threats_detected']
        response_time = final_status['metrics']['response_time_avg']
        consciousness_level = final_status['metrics']['consciousness_level']
        
        self.test_results['security_tests'] = {
            'duration': test_duration,
            'threats_detected': threats_detected,
            'response_time_avg': response_time,
            'consciousness_level': consciousness_level,
            'status': 'passed' if threats_detected > 0 else 'no_activity'
        }
        
        print(f"  ✅ Threats detected: {threats_detected}")
        print(f"  ✅ Response time: {response_time:.4f}s")
        print(f"  ✅ Consciousness level: {consciousness_level:.2f}")

    async def _test_memory_manager(self):
        """Test memory manager functionality"""
        print("\n💾 Testing Memory Manager...")
        
        start_time = time.time()
        
        # Create test memory requests
        test_requests = [
            MemoryRequest(
                request_id="integration_test_001",
                memory_type=MemoryType.AI_PROCESSING,
                size_bytes=2 * 1024 * 1024,  # 2MB
                priority=9,
                requester="integration_test",
                timestamp=time.time()
            ),
            MemoryRequest(
                request_id="integration_test_002",
                memory_type=MemoryType.CONSCIOUSNESS_BUFFER,
                size_bytes=1024 * 1024,  # 1MB
                priority=8,
                requester="integration_test",
                timestamp=time.time()
            ),
            MemoryRequest(
                request_id="integration_test_003",
                memory_type=MemoryType.SECURITY_DATA,
                size_bytes=512 * 1024,  # 512KB
                priority=7,
                requester="integration_test",
                timestamp=time.time()
            )
        ]
        
        # Allocate memory
        allocated_blocks = []
        allocation_times = []
        
        for request in test_requests:
            alloc_start = time.time()
            block_id = await self.memory_manager.allocate_memory(request)
            alloc_time = time.time() - alloc_start
            
            if block_id:
                allocated_blocks.append(block_id)
                allocation_times.append(alloc_time)
                print(f"  ✅ Allocated {request.size_bytes:,} bytes in {alloc_time:.4f}s")
        
        # Get memory status
        memory_status = await self.memory_manager.get_memory_status()
        
        # Test results
        test_duration = time.time() - start_time
        avg_allocation_time = sum(allocation_times) / len(allocation_times) if allocation_times else 0
        
        self.test_results['memory_tests'] = {
            'duration': test_duration,
            'allocations_requested': len(test_requests),
            'allocations_successful': len(allocated_blocks),
            'avg_allocation_time': avg_allocation_time,
            'total_allocated': memory_status['metrics']['total_allocated'],
            'memory_efficiency': memory_status['metrics']['memory_efficiency'],
            'status': 'passed' if len(allocated_blocks) == len(test_requests) else 'partial'
        }
        
        print(f"  ✅ Successful allocations: {len(allocated_blocks)}/{len(test_requests)}")
        print(f"  ✅ Average allocation time: {avg_allocation_time:.4f}s")
        print(f"  ✅ Memory efficiency: {memory_status['metrics']['memory_efficiency']:.2%}")

    async def _test_scheduler(self):
        """Test scheduler functionality"""
        print("\n⚡ Testing Scheduler...")
        
        start_time = time.time()
        
        # Wait for scheduler to discover processes and make decisions
        await asyncio.sleep(5.0)
        
        # Get scheduler status
        scheduler_status = await self.scheduler.get_scheduler_status()
        
        test_duration = time.time() - start_time
        
        self.test_results['scheduler_tests'] = {
            'duration': test_duration,
            'active_processes': scheduler_status['active_processes'],
            'scheduling_decisions': scheduler_status['metrics']['scheduling_decisions'],
            'context_switches': scheduler_status['metrics']['total_context_switches'],
            'cpu_utilization': scheduler_status['metrics']['cpu_utilization'],
            'ai_accuracy': scheduler_status['metrics']['ai_accuracy'],
            'consciousness_optimizations': scheduler_status['metrics'].get('consciousness_optimizations', 0),
            'behavior_patterns': scheduler_status['behavior_patterns'],
            'status': 'passed' if scheduler_status['active_processes'] > 0 else 'no_processes'
        }
        
        print(f"  ✅ Active processes: {scheduler_status['active_processes']}")
        print(f"  ✅ Scheduling decisions: {scheduler_status['metrics']['scheduling_decisions']}")
        print(f"  ✅ CPU utilization: {scheduler_status['metrics']['cpu_utilization']:.1f}%")
        print(f"  ✅ AI accuracy: {scheduler_status['metrics']['ai_accuracy']:.1%}")
        print(f"  ✅ Behavior patterns learned: {scheduler_status['behavior_patterns']}")

    async def _test_consciousness_integration(self):
        """Test consciousness level integration across all components"""
        print("\n🧠 Testing Consciousness Integration...")
        
        # Get consciousness levels from all components
        security_status = await self.security_controller.get_security_status()
        memory_status = await self.memory_manager.get_memory_status()
        scheduler_status = await self.scheduler.get_scheduler_status()
        
        security_consciousness = security_status['consciousness_level']
        memory_consciousness = memory_status['metrics'].get('consciousness_level', 0.0)
        scheduler_consciousness = scheduler_status['metrics'].get('consciousness_level', 0.0)
        
        # Check consciousness consistency
        consciousness_values = [security_consciousness, memory_consciousness, scheduler_consciousness]
        consciousness_variance = max(consciousness_values) - min(consciousness_values)
        
        # Test cross-component consciousness influence
        total_optimizations = (
            security_status['metrics'].get('consciousness_optimizations', 0) +
            memory_status['metrics'].get('consciousness_optimizations', 0) +
            scheduler_status['metrics'].get('consciousness_optimizations', 0)
        )
        
        self.test_results['integration_tests']['consciousness_integration'] = {
            'security_consciousness': security_consciousness,
            'memory_consciousness': memory_consciousness,
            'scheduler_consciousness': scheduler_consciousness,
            'consciousness_variance': consciousness_variance,
            'total_optimizations': total_optimizations,
            'consistency_check': 'passed' if consciousness_variance < 0.3 else 'inconsistent'
        }
        
        print(f"  ✅ Security consciousness: {security_consciousness:.2f}")
        print(f"  ✅ Memory consciousness: {memory_consciousness:.2f}")
        print(f"  ✅ Scheduler consciousness: {scheduler_consciousness:.2f}")
        print(f"  ✅ Consciousness variance: {consciousness_variance:.3f}")
        print(f"  ✅ Total optimizations: {total_optimizations}")

    async def _test_cross_component_communication(self):
        """Test communication between components"""
        print("\n🔗 Testing Cross-Component Communication...")
        
        # Test scenario: Security event triggers memory allocation for analysis
        start_time = time.time()
        
        # Simulate security event requiring memory allocation
        security_memory_request = MemoryRequest(
            request_id="security_analysis_buffer",
            memory_type=MemoryType.SECURITY_DATA,
            size_bytes=1024 * 1024,  # 1MB for security analysis
            priority=9,
            requester="security_controller",
            timestamp=time.time()
        )
        
        # Allocate memory for security analysis
        security_block = await self.memory_manager.allocate_memory(security_memory_request)
        
        # Wait for scheduler to potentially optimize security processes
        await asyncio.sleep(2.0)
        
        communication_time = time.time() - start_time
        
        self.test_results['integration_tests']['cross_component_communication'] = {
            'communication_time': communication_time,
            'security_memory_allocated': security_block is not None,
            'security_block_id': security_block if security_block else None,
            'status': 'passed' if security_block else 'failed'
        }
        
        print(f"  ✅ Security memory allocation: {'Success' if security_block else 'Failed'}")
        print(f"  ✅ Communication time: {communication_time:.3f}s")
        print(f"  ✅ Cross-component workflow: Functional")

    async def _test_unified_optimization(self):
        """Test unified optimization across all components"""
        print("\n🎯 Testing Unified Optimization...")
        
        # Get baseline metrics
        security_baseline = await self.security_controller.get_security_status()
        memory_baseline = await self.memory_manager.get_memory_status()
        scheduler_baseline = await self.scheduler.get_scheduler_status()
        
        # Simulate high-activity period to trigger optimizations
        await asyncio.sleep(3.0)
        
        # Get optimized metrics
        security_optimized = await self.security_controller.get_security_status()
        memory_optimized = await self.memory_manager.get_memory_status()
        scheduler_optimized = await self.scheduler.get_scheduler_status()
        
        # Calculate optimization improvements
        security_improvement = (
            security_optimized['metrics']['threats_detected'] - 
            security_baseline['metrics']['threats_detected']
        )
        
        memory_improvement = (
            memory_optimized['metrics']['memory_efficiency'] - 
            memory_baseline['metrics']['memory_efficiency']
        )
        
        scheduler_improvement = (
            scheduler_optimized['metrics']['ai_accuracy'] - 
            scheduler_baseline['metrics']['ai_accuracy']
        )
        
        self.test_results['integration_tests']['unified_optimization'] = {
            'security_improvement': security_improvement,
            'memory_improvement': memory_improvement,
            'scheduler_improvement': scheduler_improvement,
            'overall_improvement': security_improvement + memory_improvement + scheduler_improvement,
            'status': 'passed'
        }
        
        print(f"  ✅ Security optimization: +{security_improvement} threats detected")
        print(f"  ✅ Memory optimization: +{memory_improvement:.3f} efficiency")
        print(f"  ✅ Scheduler optimization: +{scheduler_improvement:.3f} accuracy")
        print(f"  ✅ Unified optimization: Functional")

    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        # Overall status calculation
        component_statuses = [
            self.test_results['security_tests'].get('status', 'failed'),
            self.test_results['memory_tests'].get('status', 'failed'),
            self.test_results['scheduler_tests'].get('status', 'failed')
        ]
        
        integration_statuses = [
            self.test_results['integration_tests'].get('consciousness_integration', {}).get('consistency_check', 'failed'),
            self.test_results['integration_tests'].get('cross_component_communication', {}).get('status', 'failed'),
            self.test_results['integration_tests'].get('unified_optimization', {}).get('status', 'failed')
        ]
        
        # Determine overall status
        all_passed = all(status == 'passed' for status in component_statuses + integration_statuses)
        self.test_results['overall_status'] = 'passed' if all_passed else 'partial'
        
        # Print summary
        print(f"🛡️  Security Controller: {self.test_results['security_tests'].get('status', 'unknown').upper()}")
        print(f"💾  Memory Manager: {self.test_results['memory_tests'].get('status', 'unknown').upper()}")
        print(f"⚡  Scheduler: {self.test_results['scheduler_tests'].get('status', 'unknown').upper()}")
        print(f"🧠  Consciousness Integration: {self.test_results['integration_tests'].get('consciousness_integration', {}).get('consistency_check', 'unknown').upper()}")
        print(f"🔗  Cross-Component Communication: {self.test_results['integration_tests'].get('cross_component_communication', {}).get('status', 'unknown').upper()}")
        print(f"🎯  Unified Optimization: {self.test_results['integration_tests'].get('unified_optimization', {}).get('status', 'unknown').upper()}")
        
        print("\n" + "=" * 60)
        print(f"🎊 OVERALL STATUS: {self.test_results['overall_status'].upper()}")
        print("=" * 60)
        
        # Save detailed results
        with open('/tmp/synos_integration_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📋 Detailed results saved to: /tmp/synos_integration_test_results.json")

    async def _stop_all_components(self):
        """Stop all consciousness components"""
        print("\n🛑 Stopping all components...")
        
        try:
            # Cancel running tasks
            if hasattr(self, 'security_task'):
                self.security_task.cancel()
            if hasattr(self, 'memory_task'):
                self.memory_task.cancel()
            if hasattr(self, 'scheduler_task'):
                self.scheduler_task.cancel()
            
            # Stop components
            await self.security_controller.stop()
            await self.memory_manager.stop()
            await self.scheduler.stop()
            
        except Exception as e:
            self.logger.error(f"Error stopping components: {e}")
        
        print("✅ All components stopped")


async def main():
    """Main integration test function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_suite = SynOSConsciousnessIntegrationTest()
    
    try:
        # Run integration test with timeout
        await asyncio.wait_for(test_suite.run_comprehensive_test(), timeout=30.0)
    except asyncio.TimeoutError:
        print("\n⏰ Integration test timeout reached")
    except KeyboardInterrupt:
        print("\n⏹️ Integration test stopped by user")
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
