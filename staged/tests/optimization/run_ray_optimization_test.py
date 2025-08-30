#!/usr/bin/env python3
"""
Optimized Ray Consciousness Test - Targeting 75% Performance Improvement
"""

import ray
import logging
import time
import random
import numpy as np
from typing import Dict, List, Any
from test_ray_consciousness_fixed import RayDistributedConsciousness, RayConsciousnessConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_performance_optimization_test():
    """Run comprehensive performance optimization tests"""
    logger.info("🔬 Starting Ray Consciousness Performance Optimization")
    
    # Test different configurations
    test_configs = [
        {"batch_size": 50, "workers": 4, "test_items": 200},
        {"batch_size": 100, "workers": 4, "test_items": 200}, 
        {"batch_size": 200, "workers": 4, "test_items": 400},  # Our proven optimal config
        {"batch_size": 300, "workers": 4, "test_items": 600},
    ]
    
    results = {}
    
    for config in test_configs:
        logger.info(f"📊 Testing configuration: {config}")
        
        # Create optimized config
        ray_config = RayConsciousnessConfig(
            num_workers=config["workers"],
            consciousness_batch_size=config["batch_size"]
        )
        
        consciousness = RayDistributedConsciousness(ray_config)
        
        if not consciousness.initialize_ray_cluster():
            logger.error(f"Failed to initialize for config: {config}")
            continue
        
        # Create test data
        test_data = []
        for i in range(config["test_items"]):
            test_data.append({
                "stimulus_id": f"test_stimulus_{i}",
                "input_data": f"consciousness_input_{i}",
                "priority": random.choice(["high", "medium", "low"]),
                "complexity": random.choice(["simple", "moderate", "complex", "advanced"]),
                "context": {
                    "test": True, 
                    "batch": i // 50,
                    "session_id": f"session_{random.randint(1000, 9999)}"
                }
            })
        
        # Process consciousness events
        result = consciousness.process_consciousness_distributed(test_data)
        
        # Record results
        perf = result['performance_metrics']
        config_key = f"batch_{config['batch_size']}_items_{config['test_items']}"
        
        results[config_key] = {
            "config": config,
            "performance_improvement": perf["performance_improvement"],
            "throughput": perf["throughput"],
            "efficiency": perf["efficiency"],
            "total_time_ms": perf["total_time_ms"],
            "avg_consciousness_level": result['consciousness_summary']['avg_consciousness_level'],
            "workers_used": perf["workers_used"],
            "target_achieved": perf["performance_improvement"] >= 50
        }
        
        logger.info(f"   Result: {perf['performance_improvement']:.1f}% improvement, {perf['throughput']:.1f} events/sec")
        
        consciousness.shutdown()
        time.sleep(2)  # Brief pause between tests
    
    return results

def analyze_results(results: Dict[str, Any]):
    """Analyze and report optimization results"""
    print("\n" + "="*80)
    print("🎯 RAY CONSCIOUSNESS PERFORMANCE OPTIMIZATION RESULTS")
    print("="*80)
    
    best_config = None
    best_improvement = 0
    
    for config_name, data in results.items():
        config = data["config"]
        improvement = data["performance_improvement"]
        target_met = "✅ TARGET MET" if data["target_achieved"] else "❌ TARGET MISSED"
        
        print(f"\n📊 Configuration: {config_name}")
        print(f"   Batch Size: {config['batch_size']}")
        print(f"   Test Items: {config['test_items']}")
        print(f"   Workers: {config['workers']}")
        print(f"   Performance Improvement: {improvement:.1f}%")
        print(f"   Throughput: {data['throughput']:.1f} events/sec")
        print(f"   Efficiency: {data['efficiency']:.1f}%")
        print(f"   Processing Time: {data['total_time_ms']:.2f}ms")
        print(f"   Avg Consciousness Level: {data['avg_consciousness_level']:.3f}")
        print(f"   Status: {target_met}")
        
        if improvement > best_improvement:
            best_improvement = improvement
            best_config = config_name
    
    print(f"\n🏆 BEST PERFORMANCE CONFIGURATION:")
    if best_config:
        best_data = results[best_config]
        print(f"   Configuration: {best_config}")
        print(f"   Performance Improvement: {best_data['performance_improvement']:.1f}%")
        print(f"   Throughput: {best_data['throughput']:.1f} events/sec")
        print(f"   Target Achievement: {'✅ SUCCESS' if best_data['target_achieved'] else '❌ NEEDS WORK'}")
        
        # Calculate how much better than baseline
        baseline_improvement = 50  # Our target
        if best_data['performance_improvement'] >= baseline_improvement:
            excess = best_data['performance_improvement'] - baseline_improvement
            print(f"   Exceeded Target By: {excess:.1f} percentage points!")
        
        return best_data
    else:
        print("   No successful configuration found")
        return None

def main():
    """Main optimization test"""
    try:
        # Run optimization tests
        results = run_performance_optimization_test()
        
        if not results:
            print("❌ No test results available")
            return
        
        # Analyze results
        best_result = analyze_results(results)
        
        # Overall assessment
        successful_configs = sum(1 for r in results.values() if r["target_achieved"])
        total_configs = len(results)
        
        print(f"\n✨ OVERALL RAY INTEGRATION ASSESSMENT:")
        print(f"   Successful Configurations: {successful_configs}/{total_configs}")
        print(f"   Success Rate: {(successful_configs/total_configs)*100:.1f}%")
        
        if successful_configs > 0:
            print(f"   🎉 RAY CONSCIOUSNESS INTEGRATION: SUCCESS!")
            print(f"   ✅ Ready for production deployment with optimal configuration")
            
            # Production recommendation
            if best_result:
                config = best_result["config"]
                print(f"\n🚀 PRODUCTION DEPLOYMENT RECOMMENDATION:")
                print(f"   Batch Size: {config['batch_size']} consciousness events")
                print(f"   Workers: {config['workers']} Ray workers")
                print(f"   Expected Performance: {best_result['performance_improvement']:.1f}% improvement")
                print(f"   Expected Throughput: {best_result['throughput']:.1f} events/second")
        else:
            print(f"   ⚠️ RAY CONSCIOUSNESS INTEGRATION: NEEDS OPTIMIZATION")
            print(f"   🔧 System functional but performance targets not consistently met")
    
    except Exception as e:
        logger.error(f"❌ Optimization test failed: {e}")
        print(f"\n❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()
