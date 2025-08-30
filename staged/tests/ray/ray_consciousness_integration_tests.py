#!/usr/bin/env python3
"""
Ray Distributed Consciousness Integration Tests
Validates the 50% performance improvement target and system integration
"""

import asyncio
import pytest
import aiohttp
import time
import json
import numpy as np
from typing import Dict, List

# Test configuration
RAY_CONSCIOUSNESS_URL = "http://localhost:8010"
BASELINE_TIME = 0.0763  # Current consciousness processing baseline
PERFORMANCE_TARGET = 0.50  # 50% improvement target

class RayConsciousnessTests:
    """Test suite for Ray distributed consciousness system"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
        
        # Wait for Ray consciousness system to be ready
        await self.wait_for_service_ready()
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
    
    async def wait_for_service_ready(self, max_retries=30):
        """Wait for Ray consciousness service to be ready"""
        for attempt in range(max_retries):
            try:
                async with self.session.get(f"{RAY_CONSCIOUSNESS_URL}/health") as response:
                    if response.status == 200:
                        print("Ray consciousness service is ready")
                        return
            except:
                pass
            
            print(f"Waiting for Ray consciousness service... (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(2)
        
        raise Exception("Ray consciousness service failed to start")
    
    async def test_consciousness_processing_performance(self):
        """Test consciousness processing performance vs baseline"""
        test_cases = [
            {"complexity": 0.3, "population": 500},
            {"complexity": 0.5, "population": 1000},
            {"complexity": 0.7, "population": 1500},
            {"complexity": 0.9, "population": 2000}
        ]
        
        performance_results = []
        
        for i, test_case in enumerate(test_cases):
            print(f"Running performance test {i+1}/4: complexity={test_case['complexity']}")
            
            request_data = {
                "stimulus": f"performance_test_{i}",
                "context": "integration_testing",
                "complexity": test_case["complexity"],
                "population_size": test_case["population"],
                "evolution_cycles": 10,
                "distributed": True
            }
            
            start_time = time.time()
            
            async with self.session.post(
                f"{RAY_CONSCIOUSNESS_URL}/consciousness/process",
                json=request_data
            ) as response:
                result = await response.json()
                
                processing_time = time.time() - start_time
                improvement = (BASELINE_TIME - processing_time) / BASELINE_TIME * 100
                
                performance_results.append({
                    'test_case': i + 1,
                    'complexity': test_case['complexity'],
                    'processing_time': processing_time,
                    'improvement_percentage': improvement,
                    'consciousness_level': result.get('consciousness_level', 0.0),
                    'distributed_workers': result.get('distributed_workers', 0),
                    'meets_target': improvement >= PERFORMANCE_TARGET * 100
                })
                
                print(f"  Processing time: {processing_time:.3f}s")
                print(f"  Improvement: {improvement:.1f}%")
                print(f"  Target met: {improvement >= PERFORMANCE_TARGET * 100}")
        
        # Calculate overall performance
        avg_improvement = sum(r['improvement_percentage'] for r in performance_results) / len(performance_results)
        tests_passed = sum(1 for r in performance_results if r['meets_target'])
        
        self.test_results.append({
            'test_name': 'consciousness_processing_performance',
            'average_improvement': avg_improvement,
            'target_improvement': PERFORMANCE_TARGET * 100,
            'tests_passed': tests_passed,
            'total_tests': len(performance_results),
            'success': avg_improvement >= PERFORMANCE_TARGET * 100,
            'details': performance_results
        })
        
        print(f"\nPerformance Test Results:")
        print(f"  Average improvement: {avg_improvement:.1f}%")
        print(f"  Target: {PERFORMANCE_TARGET * 100}%")
        print(f"  Tests passed: {tests_passed}/{len(performance_results)}")
        
        return avg_improvement >= PERFORMANCE_TARGET * 100
    
    async def test_distributed_scaling(self):
        """Test distributed processing scaling with multiple workers"""
        print("Testing distributed scaling...")
        
        # Test with different numbers of workers (simulated by batch sizes)
        scaling_tests = [
            {"workers": 1, "population": 1000},
            {"workers": 2, "population": 2000},
            {"workers": 4, "population": 4000}
        ]
        
        scaling_results = []
        
        for test in scaling_tests:
            request_data = {
                "stimulus": "scaling_test",
                "context": "distributed_scaling",
                "complexity": 0.7,
                "population_size": test["population"],
                "evolution_cycles": 10,
                "distributed": True
            }
            
            start_time = time.time()
            
            async with self.session.post(
                f"{RAY_CONSCIOUSNESS_URL}/consciousness/process",
                json=request_data
            ) as response:
                result = await response.json()
                
                processing_time = time.time() - start_time
                
                scaling_results.append({
                    'expected_workers': test['workers'],
                    'population_size': test['population'],
                    'processing_time': processing_time,
                    'actual_workers': result.get('distributed_workers', 0),
                    'consciousness_level': result.get('consciousness_level', 0.0)
                })
                
                print(f"  Workers: {test['workers']}, Time: {processing_time:.3f}s")
        
        # Validate scaling efficiency
        baseline_time = scaling_results[0]['processing_time']
        scaling_efficiency = []
        
        for i, result in enumerate(scaling_results[1:], 1):
            expected_speedup = scaling_tests[i]['workers']
            actual_speedup = baseline_time / result['processing_time']
            efficiency = actual_speedup / expected_speedup
            scaling_efficiency.append(efficiency)
        
        avg_efficiency = sum(scaling_efficiency) / len(scaling_efficiency) if scaling_efficiency else 0
        
        self.test_results.append({
            'test_name': 'distributed_scaling',
            'scaling_efficiency': avg_efficiency,
            'target_efficiency': 0.7,  # 70% scaling efficiency target
            'success': avg_efficiency >= 0.7,
            'details': scaling_results
        })
        
        print(f"  Scaling efficiency: {avg_efficiency:.2f}")
        
        return avg_efficiency >= 0.7
    
    async def test_system_status_integration(self):
        """Test system status and health monitoring"""
        print("Testing system status integration...")
        
        try:
            async with self.session.get(f"{RAY_CONSCIOUSNESS_URL}/consciousness/status") as response:
                status = await response.json()
                
                required_fields = [
                    'ray_cluster_status',
                    'worker_count',
                    'total_tasks_processed',
                    'cluster_health'
                ]
                
                missing_fields = [field for field in required_fields if field not in status]
                
                self.test_results.append({
                    'test_name': 'system_status_integration',
                    'status_response': status,
                    'missing_fields': missing_fields,
                    'worker_count': status.get('worker_count', 0),
                    'cluster_health': status.get('cluster_health', 'unknown'),
                    'success': len(missing_fields) == 0 and status.get('worker_count', 0) > 0
                })
                
                print(f"  Cluster status: {status.get('ray_cluster_status', 'unknown')}")
                print(f"  Worker count: {status.get('worker_count', 0)}")
                print(f"  Cluster health: {status.get('cluster_health', 'unknown')}")
                
                return len(missing_fields) == 0 and status.get('worker_count', 0) > 0
                
        except Exception as e:
            print(f"  Status test failed: {e}")
            return False
    
    async def test_consciousness_benchmark(self):
        """Test comprehensive consciousness benchmark"""
        print("Running consciousness benchmark...")
        
        try:
            # Start benchmark
            async with self.session.post(f"{RAY_CONSCIOUSNESS_URL}/consciousness/benchmark") as response:
                benchmark_start = await response.json()
                print(f"  Benchmark started: {benchmark_start.get('message', 'unknown')}")
            
            # Wait for benchmark to complete
            await asyncio.sleep(35)  # Benchmark takes ~30 seconds
            
            # Get benchmark results
            async with self.session.get(f"{RAY_CONSCIOUSNESS_URL}/consciousness/metrics") as response:
                metrics = await response.json()
                
                benchmark_data = metrics.get('latest_benchmark', {})
                achieved_improvement = benchmark_data.get('achieved_improvement', 0)
                target_improvement = benchmark_data.get('target_improvement', 50)
                
                self.test_results.append({
                    'test_name': 'consciousness_benchmark',
                    'achieved_improvement': achieved_improvement,
                    'target_improvement': target_improvement,
                    'benchmark_data': benchmark_data,
                    'success': achieved_improvement >= target_improvement
                })
                
                print(f"  Achieved improvement: {achieved_improvement:.1f}%")
                print(f"  Target improvement: {target_improvement}%")
                
                return achieved_improvement >= target_improvement
                
        except Exception as e:
            print(f"  Benchmark test failed: {e}")
            return False
    
    async def test_bridge_integration(self):
        """Test integration with existing consciousness bridge"""
        print("Testing consciousness bridge integration...")
        
        try:
            bridge_data = {
                "stimulus": "bridge_integration_test",
                "context": "bridge_compatibility",
                "complexity": 0.6
            }
            
            async with self.session.post(
                f"{RAY_CONSCIOUSNESS_URL}/bridge/integrate",
                json=bridge_data
            ) as response:
                result = await response.json()
                
                required_fields = [
                    'consciousness_level',
                    'processing_time',
                    'distributed',
                    'integration_status'
                ]
                
                missing_fields = [field for field in required_fields if field not in result]
                integration_success = result.get('integration_status') == 'successful'
                
                self.test_results.append({
                    'test_name': 'bridge_integration',
                    'integration_result': result,
                    'missing_fields': missing_fields,
                    'integration_successful': integration_success,
                    'success': len(missing_fields) == 0 and integration_success
                })
                
                print(f"  Integration status: {result.get('integration_status', 'unknown')}")
                print(f"  Processing time: {result.get('processing_time', 0):.3f}s")
                
                return len(missing_fields) == 0 and integration_success
                
        except Exception as e:
            print(f"  Bridge integration test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("Starting Ray Distributed Consciousness Integration Tests")
        print("=" * 60)
        
        await self.setup()
        
        tests = [
            ("Performance Test", self.test_consciousness_processing_performance),
            ("Distributed Scaling", self.test_distributed_scaling),
            ("System Status", self.test_system_status_integration),
            ("Consciousness Benchmark", self.test_consciousness_benchmark),
            ("Bridge Integration", self.test_bridge_integration)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\nRunning {test_name}...")
            try:
                result = await test_func()
                results[test_name] = result
                print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                results[test_name] = False
                print(f"❌ {test_name}: FAILED ({e})")
        
        await self.teardown()
        
        # Generate test report
        await self.generate_test_report(results)
        
        return results
    
    async def generate_test_report(self, results: Dict):
        """Generate comprehensive test report"""
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': passed_tests / total_tests * 100
            },
            'test_results': results,
            'detailed_results': self.test_results,
            'performance_targets': {
                'target_improvement': f"{PERFORMANCE_TARGET * 100}%",
                'baseline_time': f"{BASELINE_TIME}s",
                'target_time': f"{BASELINE_TIME * (1 - PERFORMANCE_TARGET)}s"
            }
        }
        
        # Save report
        with open('/tmp/ray_consciousness_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")
        print(f"\nTest report saved to: /tmp/ray_consciousness_test_report.json")

async def main():
    """Main test execution"""
    test_suite = RayConsciousnessTests()
    results = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)

if __name__ == "__main__":
    asyncio.run(main())
