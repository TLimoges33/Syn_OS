#!/usr/bin/env python3
"""
Test script for Performance Benchmark Suite
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append('src')

from consciousness_v2.tools.performance_benchmark import (
    PerformanceBenchmark, BenchmarkConfig, BenchmarkType, LoadPattern
)
from consciousness_v2.core.event_types import EventType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_performance_benchmark():
    """Test the performance benchmark suite"""
    print("Testing Performance Benchmark Suite...")
    
    try:
        # Create benchmark instance
        benchmark = PerformanceBenchmark("test_benchmark_results")
        print(f"✓ Created benchmark instance: {benchmark.component_id}")
        
        # Test basic functionality
        print(f"✓ Results directory: {benchmark.results_dir}")
        print(f"✓ Available templates: {list(benchmark.benchmark_templates.keys())}")
        
        # Test template benchmark
        print("\n--- Running Quick Health Check ---")
        result = await benchmark.run_template_benchmark("quick_health_check")
        print(f"✓ Quick health check completed")
        print(f"  - Duration: {result.duration_seconds:.1f}s")
        print(f"  - Success: {result.success}")
        print(f"  - Performance Score: {result.performance_score:.1f}/100")
        print(f"  - Bottlenecks: {len(result.bottlenecks)}")
        print(f"  - Recommendations: {len(result.recommendations)}")
        
        # Test custom benchmark configuration
        print("\n--- Running Custom Benchmark ---")
        custom_config = BenchmarkConfig(
            benchmark_type=BenchmarkType.LOAD_TEST,
            duration_seconds=15,
            load_pattern=LoadPattern.RAMP_UP,
            initial_load=5,
            max_load=20,
            ramp_duration=10,
            event_types=[EventType.PERFORMANCE_UPDATE],
            sample_interval=0.5
        )
        
        custom_result = await benchmark.run_benchmark(custom_config, "custom_test")
        print(f"✓ Custom benchmark completed")
        print(f"  - Duration: {custom_result.duration_seconds:.1f}s")
        print(f"  - Success: {custom_result.success}")
        print(f"  - Performance Score: {custom_result.performance_score:.1f}/100")
        
        # Test performance report generation
        print("\n--- Generating Performance Report ---")
        report = await benchmark.generate_performance_report(custom_result)
        print("✓ Performance report generated")
        print(f"  - Report length: {len(report)} characters")
        
        # Test benchmark history
        print("\n--- Testing Benchmark History ---")
        history = await benchmark.get_benchmark_history(5)
        print(f"✓ Retrieved benchmark history: {len(history)} results")
        
        # Test performance baselines
        print("\n--- Testing Performance Baselines ---")
        baselines = await benchmark.get_performance_baselines()
        print(f"✓ Retrieved performance baselines: {len(baselines)} components")
        
        # Test baseline comparison
        if baselines:
            print("\n--- Testing Baseline Comparison ---")
            comparison = await benchmark.compare_with_baseline(custom_result)
            print(f"✓ Baseline comparison completed: {len(comparison)} components")
            
            for component_id, changes in comparison.items():
                print(f"  - {component_id}:")
                print(f"    Response time change: {changes.get('response_time_change', 0):.1f}%")
                print(f"    Throughput change: {changes.get('throughput_change', 0):.1f}%")
                print(f"    Error rate change: {changes.get('error_rate_change', 0):.2f}%")
        
        # Test different load patterns
        print("\n--- Testing Load Patterns ---")
        patterns = [LoadPattern.CONSTANT, LoadPattern.SPIKE, LoadPattern.WAVE]
        
        for pattern in patterns:
            print(f"Testing {pattern.value} pattern...")
            pattern_config = BenchmarkConfig(
                benchmark_type=BenchmarkType.LOAD_TEST,
                duration_seconds=10,
                load_pattern=pattern,
                initial_load=3,
                max_load=10,
                ramp_duration=5
            )
            
            pattern_result = await benchmark.run_benchmark(pattern_config, f"pattern_{pattern.value}")
            print(f"✓ {pattern.value} pattern test completed - Score: {pattern_result.performance_score:.1f}")
        
        # Test cleanup
        print("\n--- Testing Cleanup ---")
        await benchmark.cleanup()
        print("✓ Benchmark cleanup completed")
        
        print("\n✓ All performance benchmark tests passed!")
        
        # Display sample report
        print("\n" + "="*60)
        print("SAMPLE PERFORMANCE REPORT")
        print("="*60)
        print(report[:1000] + "..." if len(report) > 1000 else report)
        
    except Exception as e:
        print(f"✗ Performance benchmark test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_performance_benchmark())
    sys.exit(0 if success else 1)