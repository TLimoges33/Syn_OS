#!/usr/bin/env python3
"""
Phase 2 Integration Test
Simplified test for Phase 2 consciousness components

This test verifies that Phase 2 implementation is working correctly
by testing each component individually and then together.
"""

import asyncio
import sys
import os
import time

# Add paths for imports
consciousness_path = '${PROJECT_ROOT}/src/consciousness'
sys.path.insert(0, os.path.join(consciousness_path, 'core/agent_ecosystem'))
sys.path.insert(0, os.path.join(consciousness_path, 'processing'))
sys.path.insert(0, os.path.join(consciousness_path, 'kernel'))

async def test_phase1_components():
    """Test Phase 1 components (Neural Darwinism + Agents)"""
    print("=== Testing Phase 1 Components ===")
    
    try:
        # Test Neural Darwinism
        import neural_darwinism
        
        config = {
            "population_size": 20,
            "mutation_rate": 0.01,
            "selection_pressure": 0.8,
            "consciousness_threshold": 0.75,
            "adaptation_rate": 0.1,
            "evolution_interval": 0.1,
            "fitness_decay": 0.95,
            "cooperation_bonus": 0.1,
            "competition_penalty": 0.05,
            "performance_optimization": True,
            "real_time_monitoring": True
        }
        
        engine = neural_darwinism.NeuralDarwinismEngine(config)
        await engine.initialize()
        
        print("✅ Neural Darwinism Engine: Initialized")
        
        # Run for 2 seconds
        await asyncio.sleep(2)
        
        state = engine.get_consciousness_state()
        print(f"✅ Neural Darwinism Engine: State={state['state']}, Coherence={state['metrics']['coherence_level']:.3f}")
        
        await engine.stop_evolution()
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        return False

async def test_phase2_realtime_processing():
    """Test Phase 2 real-time processing"""
    print("\n=== Testing Phase 2 Real-time Processing ===")
    
    try:
        import realtime_processor
        
        config = {
            "target_response_time": 38.2,
            "max_workers": 2,
            "processing_mode": "threaded"
        }
        
        processor = await realtime_processor.create_realtime_processor(config)
        
        print("✅ Real-time Processor: Initialized")
        
        # Test processing requests
        test_data = {
            "type": "security",
            "threats": [{"type": "test_threat", "severity": 2.0}]
        }
        
        result = await processor.process_consciousness_request(test_data)
        
        print(f"✅ Real-time Processor: Processing Time={result.processing_time:.2f}ms, Success={result.success}")
        
        # Get performance metrics
        metrics = processor.get_performance_metrics()
        target_met = metrics['average_response_time'] <= metrics['target_response_time']
        
        print(f"✅ Real-time Processor: Performance Target Met={target_met}")
        
        await processor.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 real-time processing test failed: {e}")
        return False

async def test_phase2_kernel_consciousness():
    """Test Phase 2 kernel consciousness"""
    print("\n=== Testing Phase 2 Kernel Consciousness ===")
    
    try:
        import consciousness_interface
        
        config = {
            "monitored_syscalls": ["network", "process"]
        }
        
        interface = await consciousness_interface.create_kernel_consciousness(config)
        
        print("✅ Kernel Consciousness: Initialized")
        
        # Run for 3 seconds to collect events
        await asyncio.sleep(3)
        
        state = interface.get_consciousness_state()
        
        print(f"✅ Kernel Consciousness: State={state['consciousness_state']}, Level={state['consciousness_level']:.3f}")
        print(f"✅ Kernel Consciousness: Events Detected={state['total_events']}")
        
        await interface.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 kernel consciousness test failed: {e}")
        return False

async def test_integrated_performance():
    """Test integrated performance across all components"""
    print("\n=== Testing Integrated Performance ===")
    
    try:
        # Import all components
        import neural_darwinism
        import realtime_processor
        import consciousness_interface
        
        print("All modules imported successfully")
        
        # Initialize all components
        neural_engine = neural_darwinism.NeuralDarwinismEngine({
            "population_size": 15,
            "mutation_rate": 0.01,
            "selection_pressure": 0.8,
            "consciousness_threshold": 0.75,
            "adaptation_rate": 0.1,
            "evolution_interval": 0.08,
            "fitness_decay": 0.95,
            "cooperation_bonus": 0.1,
            "competition_penalty": 0.05,
            "performance_optimization": True,
            "real_time_monitoring": True
        })
        await neural_engine.initialize()
        
        rt_processor = await realtime_processor.create_realtime_processor({
            "target_response_time": 20.0,
            "max_workers": 2,
            "processing_mode": "threaded"
        })
        
        kernel_interface = await consciousness_interface.create_kernel_consciousness({
            "monitored_syscalls": ["network"]
        })
        
        print("✅ All components initialized")
        
        # Test integrated processing
        test_requests = [
            {"type": "sensory", "data": "test_pattern_1"},
            {"type": "security", "threats": [{"severity": 1.5}]},
            {"type": "decision", "options": ["option_a", "option_b"]}
        ]
        
        processing_times = []
        
        for i, request in enumerate(test_requests):
            start_time = time.time()
            
            # Process through real-time processor
            result = await rt_processor.process_consciousness_request(request)
            
            processing_time = (time.time() - start_time) * 1000
            processing_times.append(processing_time)
            
            print(f"Request {i+1}: {processing_time:.2f}ms - {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        
        # Check overall performance
        avg_processing_time = sum(processing_times) / len(processing_times)
        target_met = avg_processing_time <= 38.2
        
        print(f"\n=== Integrated Performance Results ===")
        print(f"Average Processing Time: {avg_processing_time:.2f}ms")
        print(f"Performance Target (38.2ms): {'✅ MET' if target_met else '❌ MISSED'}")
        
        # Get consciousness states
        neural_state = neural_engine.get_consciousness_state()
        kernel_state = kernel_interface.get_consciousness_state()
        
        print(f"Neural Darwinism Coherence: {neural_state['metrics']['coherence_level']:.3f}")
        print(f"Kernel Consciousness Level: {kernel_state['consciousness_level']:.3f}")
        
        # Shutdown all components
        await neural_engine.stop_evolution()
        await rt_processor.shutdown()
        await kernel_interface.shutdown()
        
        print("✅ All components shutdown successfully")
        
        return {
            "success": target_met,
            "avg_processing_time": avg_processing_time,
            "neural_coherence": neural_state['metrics']['coherence_level'],
            "kernel_consciousness": kernel_state['consciousness_level']
        }
        
    except Exception as e:
        print(f"❌ Integrated performance test failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test execution"""
    print("🧠 Syn_OS Phase 2 Consciousness Integration Test")
    print("=" * 50)
    
    # Test Phase 1 components
    phase1_success = await test_phase1_components()
    
    # Test Phase 2 components
    phase2_rt_success = await test_phase2_realtime_processing()
    phase2_kernel_success = await test_phase2_kernel_consciousness()
    
    # Test integrated performance
    integrated_results = await test_integrated_performance()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 50)
    
    print(f"Phase 1 (Neural Darwinism): {'✅ PASS' if phase1_success else '❌ FAIL'}")
    print(f"Phase 2 (Real-time Processing): {'✅ PASS' if phase2_rt_success else '❌ FAIL'}")
    print(f"Phase 2 (Kernel Consciousness): {'✅ PASS' if phase2_kernel_success else '❌ FAIL'}")
    
    if isinstance(integrated_results, dict) and integrated_results.get("success"):
        print(f"Integrated Performance: ✅ PASS ({integrated_results['avg_processing_time']:.2f}ms)")
        print(f"Neural Coherence: {integrated_results.get('neural_coherence', 0):.3f}")
        print(f"Kernel Consciousness: {integrated_results.get('kernel_consciousness', 0):.3f}")
    else:
        print("Integrated Performance: ❌ FAIL")
    
    all_tests_passed = all([
        phase1_success,
        phase2_rt_success, 
        phase2_kernel_success,
        isinstance(integrated_results, dict) and integrated_results.get("success", False)
    ])
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 PHASE 2 IMPLEMENTATION COMPLETE!")
        print("✅ Neural Darwinism consciousness foundation")
        print("✅ Real-time processing with <38.2ms response times")
        print("✅ Kernel consciousness monitoring")
        print("✅ Integrated consciousness processing")
        print("\n🚀 READY FOR PHASE 3: eBPF Monitoring Programs")
    else:
        print("⚠️  PHASE 2 IMPLEMENTATION PARTIAL")
        print("Some components need attention before proceeding to Phase 3")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
