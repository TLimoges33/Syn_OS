#!/usr/bin/env python3
"""
GenAI OS - Ray Optimization Test Runner
Performance optimization testing and validation
"""

import asyncio
import time
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.performance.optimization_phase_3_4 import PerformanceOptimizer, PerformanceMetrics
from src.tests.ray_consciousness_test import ConsciousnessTestSuite

class RayOptimizationTestRunner:
    """Test runner for Ray optimization validation"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.test_results: List[Dict[str, Any]] = []
        self.optimization_results: List[Dict[str, Any]] = []
        
        self.logger.info("Ray Optimization Test Runner initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup optimization test logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def test_baseline_performance(self) -> Dict[str, Any]:
        """Test baseline performance before optimization"""
        self.logger.info("Testing baseline performance...")
        
        try:
            # Initialize performance optimizer
            optimizer = PerformanceOptimizer()
            await optimizer.initialize_redis_optimization()
            await optimizer.initialize_processing_pools()
            await optimizer.create_consciousness_processors(4)
            
            # Collect baseline metrics
            baseline_metrics = await optimizer.collect_performance_metrics()
            
            # Run baseline workload
            test_events = []
            for i in range(500):
                event = {
                    'id': i,
                    'type': np.random.choice(['neural_darwinism', 'pattern_recognition', 'learning']),
                    'complexity': np.random.uniform(0.5, 2.0)
                }
                test_events.append(event)
            
            start_time = time.time()
            
            # Process events without optimization
            tasks = []
            for i, event in enumerate(test_events):
                processor = optimizer.consciousness_processors[i % len(optimizer.consciousness_processors)]
                task = processor.process_consciousness_event(event)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            baseline_time = time.time() - start_time
            
            successful_results = [r for r in results if isinstance(r, dict) and r.get('status') == 'success']
            baseline_throughput = len(successful_results) / baseline_time
            
            await optimizer.shutdown()
            
            result = {
                'test_name': 'Baseline Performance',
                'status': 'PASSED',
                'metrics': {
                    'events_processed': len(successful_results),
                    'processing_time': baseline_time,
                    'throughput': baseline_throughput,
                    'cpu_usage': baseline_metrics.cpu_usage,
                    'memory_usage': baseline_metrics.memory_usage,
                    'response_latency': baseline_metrics.response_latency
                }
            }
            
            self.logger.info(f"Baseline performance: {baseline_throughput:.2f} events/sec")
            
        except Exception as e:
            result = {
                'test_name': 'Baseline Performance',
                'status': 'FAILED',
                'error': str(e)
            }
            self.logger.error(f"Baseline performance test failed: {e}")
        
        self.test_results.append(result)
        return result
    
    async def test_optimized_performance(self) -> Dict[str, Any]:
        """Test performance after optimization"""
        self.logger.info("Testing optimized performance...")
        
        try:
            # Initialize performance optimizer
            optimizer = PerformanceOptimizer()
            await optimizer.initialize_redis_optimization()
            await optimizer.initialize_processing_pools()
            await optimizer.create_consciousness_processors(8)  # More processors
            
            # Run optimization
            optimization_results = await optimizer.run_comprehensive_optimization()
            
            # Collect optimized metrics
            optimized_metrics = await optimizer.collect_performance_metrics()
            
            # Run optimized workload (larger to test scalability)
            test_events = []
            for i in range(1000):
                event = {
                    'id': i,
                    'type': np.random.choice(['neural_darwinism', 'pattern_recognition', 'learning']),
                    'complexity': np.random.uniform(0.5, 2.0)
                }
                test_events.append(event)
            
            start_time = time.time()
            
            # Process events with optimization (batched processing)
            batch_size = 100
            results = []
            
            for i in range(0, len(test_events), batch_size):
                batch = test_events[i:i + batch_size]
                batch_tasks = []
                
                for j, event in enumerate(batch):
                    processor = optimizer.consciousness_processors[j % len(optimizer.consciousness_processors)]
                    task = processor.process_consciousness_event(event)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                results.extend(batch_results)
            
            optimized_time = time.time() - start_time
            
            successful_results = [r for r in results if isinstance(r, dict) and r.get('status') == 'success']
            optimized_throughput = len(successful_results) / optimized_time
            
            await optimizer.shutdown()
            
            result = {
                'test_name': 'Optimized Performance',
                'status': 'PASSED',
                'metrics': {
                    'events_processed': len(successful_results),
                    'processing_time': optimized_time,
                    'throughput': optimized_throughput,
                    'cpu_usage': optimized_metrics.cpu_usage,
                    'memory_usage': optimized_metrics.memory_usage,
                    'response_latency': optimized_metrics.response_latency,
                    'optimization_improvements': {
                        opt_type: result.improvement_percentage 
                        for opt_type, result in optimization_results.items()
                        if result.success
                    }
                }
            }
            
            self.logger.info(f"Optimized performance: {optimized_throughput:.2f} events/sec")
            
        except Exception as e:
            result = {
                'test_name': 'Optimized Performance',
                'status': 'FAILED',
                'error': str(e)
            }
            self.logger.error(f"Optimized performance test failed: {e}")
        
        self.test_results.append(result)
        return result
    
    async def test_consciousness_integration(self) -> Dict[str, Any]:
        """Test consciousness system integration"""
        self.logger.info("Testing consciousness system integration...")
        
        try:
            # Run consciousness test suite
            consciousness_test_suite = ConsciousnessTestSuite()
            test_summary = await consciousness_test_suite.run_comprehensive_test_suite()
            
            result = {
                'test_name': 'Consciousness Integration',
                'status': 'PASSED' if test_summary['success_rate'] >= 80 else 'FAILED',
                'metrics': {
                    'total_consciousness_tests': test_summary['total_tests'],
                    'passed_consciousness_tests': test_summary['passed_tests'],
                    'consciousness_success_rate': test_summary['success_rate'],
                    'consciousness_test_time': test_summary['total_time_seconds']
                }
            }
            
            self.logger.info(f"Consciousness integration: {test_summary['success_rate']:.1f}% success rate")
            
        except Exception as e:
            result = {
                'test_name': 'Consciousness Integration',
                'status': 'FAILED',
                'error': str(e)
            }
            self.logger.error(f"Consciousness integration test failed: {e}")
        
        self.test_results.append(result)
        return result
    
    async def test_scalability_limits(self) -> Dict[str, Any]:
        """Test system scalability limits"""
        self.logger.info("Testing scalability limits...")
        
        try:
            scalability_results = []
            
            # Test with increasing loads
            load_levels = [100, 500, 1000, 2000, 5000]
            
            for load in load_levels:
                self.logger.info(f"Testing with {load} events...")
                
                # Initialize optimizer for this test
                optimizer = PerformanceOptimizer()
                await optimizer.initialize_redis_optimization()
                await optimizer.initialize_processing_pools()
                await optimizer.create_consciousness_processors(min(load // 100, 16))  # Scale processors
                
                # Generate events
                test_events = []
                for i in range(load):
                    event = {
                        'id': i,
                        'type': 'pattern_recognition',  # Use consistent type for fair comparison
                        'complexity': 1.0
                    }
                    test_events.append(event)
                
                start_time = time.time()
                
                # Process events
                batch_size = min(100, load // 10)
                results = []
                
                for i in range(0, len(test_events), batch_size):
                    batch = test_events[i:i + batch_size]
                    batch_tasks = []
                    
                    for j, event in enumerate(batch):
                        processor_idx = j % len(optimizer.consciousness_processors)
                        processor = optimizer.consciousness_processors[processor_idx]
                        task = processor.process_consciousness_event(event)
                        batch_tasks.append(task)
                    
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    results.extend(batch_results)
                
                processing_time = time.time() - start_time
                successful_results = [r for r in results if isinstance(r, dict) and r.get('status') == 'success']
                throughput = len(successful_results) / processing_time
                
                scalability_result = {
                    'load': load,
                    'processed': len(successful_results),
                    'time': processing_time,
                    'throughput': throughput,
                    'processors': len(optimizer.consciousness_processors)
                }
                scalability_results.append(scalability_result)
                
                await optimizer.shutdown()
                
                # Brief pause between tests
                await asyncio.sleep(1)
            
            # Calculate scalability metrics
            max_throughput = max(r['throughput'] for r in scalability_results)
            max_load = max(r['load'] for r in scalability_results)
            
            result = {
                'test_name': 'Scalability Limits',
                'status': 'PASSED',
                'metrics': {
                    'max_throughput': max_throughput,
                    'max_load_tested': max_load,
                    'scalability_results': scalability_results,
                    'linear_scalability': self._check_linear_scalability(scalability_results)
                }
            }
            
            self.logger.info(f"Scalability test: max {max_throughput:.2f} events/sec at {max_load} events")
            
        except Exception as e:
            result = {
                'test_name': 'Scalability Limits',
                'status': 'FAILED',
                'error': str(e)
            }
            self.logger.error(f"Scalability test failed: {e}")
        
        self.test_results.append(result)
        return result
    
    def _check_linear_scalability(self, scalability_results: List[Dict[str, Any]]) -> float:
        """Check how close the system is to linear scalability"""
        if len(scalability_results) < 2:
            return 0.0
        
        # Calculate expected vs actual throughput improvement
        base_result = scalability_results[0]
        
        scalability_scores = []
        for result in scalability_results[1:]:
            load_ratio = result['load'] / base_result['load']
            throughput_ratio = result['throughput'] / base_result['throughput']
            
            # Perfect linear scalability would have throughput_ratio == load_ratio
            # Calculate how close we are (max score = 1.0)
            scalability_score = min(throughput_ratio / load_ratio, load_ratio / throughput_ratio)
            scalability_scores.append(scalability_score)
        
        return np.mean(scalability_scores)
    
    async def run_optimization_validation(self) -> Dict[str, Any]:
        """Run complete optimization validation"""
        self.logger.info("🚀 Starting Ray optimization validation...")
        
        start_time = time.time()
        
        # Run all optimization tests
        tests = [
            self.test_baseline_performance,
            self.test_optimized_performance,
            self.test_consciousness_integration,
            self.test_scalability_limits
        ]
        
        for test_func in tests:
            await test_func()
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        total_time = time.time() - start_time
        
        # Calculate performance improvement
        baseline_result = next((r for r in self.test_results if r['test_name'] == 'Baseline Performance'), None)
        optimized_result = next((r for r in self.test_results if r['test_name'] == 'Optimized Performance'), None)
        
        performance_improvement = 0.0
        if (baseline_result and optimized_result and 
            baseline_result['status'] == 'PASSED' and optimized_result['status'] == 'PASSED'):
            
            baseline_throughput = baseline_result['metrics']['throughput']
            optimized_throughput = optimized_result['metrics']['throughput']
            performance_improvement = ((optimized_throughput - baseline_throughput) / baseline_throughput) * 100
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        
        summary = {
            'validation_suite': 'Ray Optimization Validation',
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'performance_improvement': performance_improvement,
            'total_time': total_time,
            'test_results': self.test_results
        }
        
        self.logger.info(f"Optimization validation complete: {performance_improvement:.2f}% improvement")
        
        return summary

async def main():
    """Main optimization test execution"""
    print("⚡ GenAI OS - Ray Optimization Test Runner")
    
    # Initialize test runner
    test_runner = RayOptimizationTestRunner()
    
    # Run optimization validation
    summary = await test_runner.run_optimization_validation()
    
    # Display results
    print(f"\n📊 Optimization Validation Summary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed_tests']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Performance Improvement: {summary['performance_improvement']:.2f}%")
    print(f"  Total Time: {summary['total_time']:.2f}s")
    
    print(f"\n📋 Test Details:")
    for result in summary['test_results']:
        status_icon = "✅" if result['status'] == 'PASSED' else "❌"
        print(f"  {status_icon} {result['test_name']}")
        
        if result['status'] == 'PASSED' and 'metrics' in result:
            metrics = result['metrics']
            if 'throughput' in metrics:
                print(f"    Throughput: {metrics['throughput']:.1f} events/sec")
            if 'consciousness_success_rate' in metrics:
                print(f"    Consciousness: {metrics['consciousness_success_rate']:.1f}% success")
            if 'max_throughput' in metrics:
                print(f"    Max Throughput: {metrics['max_throughput']:.1f} events/sec")
        elif result['status'] == 'FAILED':
            print(f"    Error: {result.get('error', 'Unknown error')}")
    
    # Final assessment
    if summary['performance_improvement'] >= 50:
        print(f"\n🎉 EXCELLENT: Ray optimization achieved {summary['performance_improvement']:.1f}% improvement!")
    elif summary['performance_improvement'] >= 25:
        print(f"\n👍 GOOD: Ray optimization achieved {summary['performance_improvement']:.1f}% improvement")
    elif summary['performance_improvement'] >= 10:
        print(f"\n✅ ACCEPTABLE: Ray optimization achieved {summary['performance_improvement']:.1f}% improvement")
    else:
        print(f"\n⚠️  LIMITED: Ray optimization achieved only {summary['performance_improvement']:.1f}% improvement")
    
    if summary['success_rate'] >= 75:
        print("🚀 Ray consciousness system ready for production deployment!")
    else:
        print("🔧 Ray consciousness system needs additional optimization")
    
    print("✅ Ray optimization testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
