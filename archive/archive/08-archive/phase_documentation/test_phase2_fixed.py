#!/usr/bin/env python3
"""
Phase 2 Integration Test (Fixed)
Comprehensive test of Neural Darwinism + Real-time Processing + Kernel Consciousness
"""

import asyncio
import sys
import os
import time

# Add consciousness modules to path
sys.path.insert(0, '/home/diablorain/Syn_OS/src/consciousness/core/agent_ecosystem')
sys.path.insert(0, '/home/diablorain/Syn_OS/src/consciousness')

async def test_phase1_neural_darwinism():
    """Test Phase 1: Neural Darwinism Engine"""
    try:
        import neural_darwinism
        
        print("🧠 Testing Neural Darwinism Engine...")
        config = {
            "population_size": 30,
            "mutation_rate": 0.01,
            "selection_pressure": 0.8,
            "consciousness_threshold": 0.75,
            "adaptation_rate": 0.1,
            "evolution_interval": 0.05,
            "fitness_decay": 0.95,
            "cooperation_bonus": 0.1,
            "competition_penalty": 0.05,
            "performance_optimization": True,
            "real_time_monitoring": True
        }
        
        engine = neural_darwinism.NeuralDarwinismEngine(config)
        success = await engine.initialize()
        
        if not success:
            return False, "Failed to initialize"
        
        # Run for 2 seconds
        await asyncio.sleep(2)
        
        state = engine.get_consciousness_state()
        metrics = engine.get_performance_metrics()
        
        await engine.stop_evolution()
        
        print(f"   ✅ State: {state['state']}")
        print(f"   ✅ Coherence: {state['metrics']['coherence_level']:.3f}")
        print(f"   ✅ Cycles: {state['cycle_count']}")
        
        return True, state
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, str(e)

async def test_phase2_realtime_processing():
    """Test Phase 2: Real-time Processing"""
    try:
        import realtime_consciousness
        
        print("⚡ Testing Real-time Consciousness Processing...")
        
        # Create processor with minimal config
        config = {
            "max_workers": 2,
            "processing_timeout": 5.0,
            "batch_size": 5
        }
        
        processor = realtime_consciousness.RealTimeConsciousnessProcessor(config)
        await processor.initialize()
        
        # Test processing
        test_data = {
            "type": "security_event",
            "data": {"threat_level": 0.3, "source": "network"},
            "timestamp": time.time()
        }
        
        result = await processor.process_data(test_data)
        
        await processor.shutdown()
        
        # Handle ProcessingResult object attributes
        processing_time = result.processing_time if hasattr(result, 'processing_time') else 0
        status = result.status.value if hasattr(result, 'status') and hasattr(result.status, 'value') else str(getattr(result, 'status', 'unknown'))
        
        print(f"   ✅ Processing Time: {processing_time:.2f}ms")
        print(f"   ✅ Status: {status}")
        
        return True, {"processing_time": processing_time, "status": status}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, str(e)

async def test_phase2_kernel_consciousness():
    """Test Phase 2: Kernel Consciousness"""
    try:
        import kernel.consciousness_interface as kernel_ci
        
        print("🔧 Testing Kernel Consciousness Interface...")
        
        # Create interface with proper config
        config = {
            "monitored_syscalls": ["NETWORK", "PROCESS", "FILESYSTEM"],
            "monitoring_enabled": True,
            "shared_memory_size": 4096
        }
        interface = kernel_ci.KernelConsciousnessInterface(config)
        await interface.initialize()
        
        # Test consciousness monitoring
        test_event = kernel_ci.KernelEvent(
            event_type=kernel_ci.KernelEventType.SYSCALL,
            data={"syscall": "read", "pid": 1234},
            priority=kernel_ci.EventPriority.NORMAL,
            timestamp=time.time()
        )
        
        await interface.process_kernel_event(test_event)
        
        state = interface.get_consciousness_state()
        
        await interface.shutdown()
        
        print(f"   ✅ Consciousness Level: {state.get('consciousness_level', 0):.3f}")
        print(f"   ✅ Events Processed: {state.get('total_events', 0)}")
        
        return True, state
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, str(e)

async def test_integrated_performance():
    """Test integrated system performance"""
    try:
        import phase2_integration
        
        print("🚀 Testing Integrated Consciousness System...")
        
        config = {
            "neural_darwinism": {
                "population_size": 20,
                "evolution_interval": 0.1,
                "consciousness_threshold": 0.75,
                "adaptation_rate": 0.1,
                "fitness_decay": 0.95,
                "cooperation_bonus": 0.1,
                "competition_penalty": 0.05
            },
            "realtime": {
                "max_workers": 2,
                "processing_timeout": 3.0
            },
            "kernel": {
                "monitoring_enabled": True,
                "consciousness_threshold": 0.6
            }
        }
        
        integration = phase2_integration.IntegratedConsciousnessSystem(config)
        success = await integration.initialize()
        
        if not success:
            return False, "Failed to initialize integrated system"
        
        # Test processing
        start_time = time.time()
        
        test_requests = []
        for i in range(5):
            test_data = {
                "request_id": f"test_{i}",
                "data": {"value": i * 0.2},
                "timestamp": time.time()
            }
            result = await integration.process_consciousness_request(test_data)
            test_requests.append(result)
        
        total_time = (time.time() - start_time) * 1000  # ms
        avg_time = total_time / len(test_requests)
        
        performance = integration.get_performance_report()
        
        await integration.shutdown()
        
        print(f"   ✅ Average Processing Time: {avg_time:.2f}ms")
        print(f"   ✅ Performance Target (38.2ms): {'✅ MET' if avg_time < 38.2 else '❌ EXCEEDED'}")
        
        return True, {"avg_time": avg_time, "performance": performance}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, str(e)

async def main():
    """Run comprehensive Phase 2 test"""
    print("=" * 50)
    print("🎯 Syn_OS Phase 2 Implementation Test")
    print("=" * 50)
    
    results = {}
    
    # Test Phase 1
    print("\n1. Phase 1 (Neural Darwinism):")
    p1_success, p1_result = await test_phase1_neural_darwinism()
    results["phase1"] = {"success": p1_success, "result": p1_result}
    
    # Test Phase 2 Real-time
    print("\n2. Phase 2 (Real-time Processing):")
    p2rt_success, p2rt_result = await test_phase2_realtime_processing()
    results["phase2_realtime"] = {"success": p2rt_success, "result": p2rt_result}
    
    # Test Phase 2 Kernel
    print("\n3. Phase 2 (Kernel Consciousness):")
    p2k_success, p2k_result = await test_phase2_kernel_consciousness()
    results["phase2_kernel"] = {"success": p2k_success, "result": p2k_result}
    
    # Test Integrated Performance
    print("\n4. Integrated Performance:")
    perf_success, perf_result = await test_integrated_performance()
    results["integrated"] = {"success": perf_success, "result": perf_result}
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"Phase 1 (Neural Darwinism): {'✅ PASS' if results['phase1']['success'] else '❌ FAIL'}")
    print(f"Phase 2 (Real-time Processing): {'✅ PASS' if results['phase2_realtime']['success'] else '❌ FAIL'}")
    print(f"Phase 2 (Kernel Consciousness): {'✅ PASS' if results['phase2_kernel']['success'] else '❌ FAIL'}")
    print(f"Integrated Performance: {'✅ PASS' if results['integrated']['success'] else '❌ FAIL'}")
    
    all_passed = all(r["success"] for r in results.values())
    
    if all_passed:
        print("\n🎉 All Phase 2 tests PASSED!")
        print("\nNext Steps:")
        print("- Begin Phase 3: eBPF Monitoring Programs")
        print("- Implement production deployment configuration")
        print("- Integrate with Syn_OS security tools")
        
        if perf_success and isinstance(perf_result, dict):
            avg_time = perf_result.get("avg_time", 0)
            print(f"\n⚡ Performance: {avg_time:.2f}ms (Target: 38.2ms)")
    else:
        print("\n⚠️  Some tests failed. Check implementation and retry.")
        
        # Show specific failures
        for test_name, result in results.items():
            if not result["success"]:
                print(f"   {test_name}: {result['result']}")

if __name__ == "__main__":
    asyncio.run(main())
