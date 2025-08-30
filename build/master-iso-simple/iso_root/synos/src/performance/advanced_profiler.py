#!/usr/bin/env python3
"""
Advanced Performance Profiler for A+ Achievement
===============================================

Real-time performance monitoring and optimization analysis for Syn_OS
authentication system with academic-grade metrics collection.

Features:
- Real-time performance monitoring
- Statistical analysis with confidence intervals  
- Resource utilization tracking
- Bottleneck identification
- A+ performance validation
"""

import asyncio
import time
import statistics
import psutil
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class PerformanceSnapshot:
    """Single performance measurement snapshot"""
    timestamp: float
    operation_type: str
    response_time_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    concurrent_operations: int
    success: bool
    error_message: Optional[str] = None

@dataclass
class PerformanceStatistics:
    """Statistical analysis of performance data"""
    operation_type: str
    sample_count: int
    mean_response_time_ms: float
    median_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    std_deviation_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    success_rate: float
    confidence_interval_95: Tuple[float, float]
    operations_per_second: float
    cpu_utilization_avg: float
    memory_utilization_avg: float

class AdvancedPerformanceProfiler:
    """Advanced performance profiler with real-time analytics"""
    
    def __init__(self, max_snapshots: int = 10000):
        self.max_snapshots = max_snapshots
        self.snapshots: List[PerformanceSnapshot] = []
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Performance thresholds for A+ achievement
        self.a_plus_thresholds = {
            "min_ops_per_second": 200,
            "max_p95_response_ms": 100,
            "min_success_rate": 0.99,
            "max_cpu_usage": 80.0,
            "max_memory_usage_mb": 500
        }
        
    def start_monitoring(self):
        """Start real-time performance monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 Advanced performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                memory_mb = memory_info.used / (1024 * 1024)
                
                # Store system snapshot if needed
                if len(self.snapshots) > 0:
                    with self.lock:
                        if self.snapshots:
                            # Update last snapshot with system metrics
                            last_snapshot = self.snapshots[-1]
                            last_snapshot.cpu_usage_percent = cpu_percent
                            last_snapshot.memory_usage_mb = memory_mb
                
                time.sleep(0.1)  # 100ms monitoring interval
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)
    
    def record_operation(self, operation_type: str, response_time_ms: float, 
                        concurrent_ops: int = 1, success: bool = True, 
                        error_message: Optional[str] = None):
        """Record a performance operation"""
        
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            operation_type=operation_type,
            response_time_ms=response_time_ms,
            cpu_usage_percent=0.0,  # Will be updated by monitoring loop
            memory_usage_mb=0.0,    # Will be updated by monitoring loop
            concurrent_operations=concurrent_ops,
            success=success,
            error_message=error_message
        )
        
        with self.lock:
            self.snapshots.append(snapshot)
            
            # Maintain max snapshots limit
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots.pop(0)
    
    def analyze_performance(self, operation_type: Optional[str] = None,
                          time_window_minutes: Optional[int] = None) -> PerformanceStatistics:
        """Analyze performance with statistical rigor"""
        
        with self.lock:
            # Filter snapshots based on criteria
            filtered_snapshots = self.snapshots.copy()
            
            if operation_type:
                filtered_snapshots = [s for s in filtered_snapshots if s.operation_type == operation_type]
            
            if time_window_minutes:
                cutoff_time = time.time() - (time_window_minutes * 60)
                filtered_snapshots = [s for s in filtered_snapshots if s.timestamp >= cutoff_time]
            
            if not filtered_snapshots:
                return None
            
            # Extract response times and success data
            response_times = [s.response_time_ms for s in filtered_snapshots]
            successful_ops = [s for s in filtered_snapshots if s.success]
            
            # Calculate basic statistics
            mean_response = statistics.mean(response_times)
            median_response = statistics.median(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            min_response = min(response_times)
            max_response = max(response_times)
            
            # Calculate percentiles
            p95_response = np.percentile(response_times, 95) if len(response_times) > 0 else 0
            p99_response = np.percentile(response_times, 99) if len(response_times) > 0 else 0
            
            # Calculate confidence interval (95%)
            n = len(response_times)
            margin_of_error = 1.96 * (std_dev / np.sqrt(n)) if n > 1 else 0
            confidence_interval = (mean_response - margin_of_error, mean_response + margin_of_error)
            
            # Calculate operations per second
            if len(filtered_snapshots) > 1:
                time_span = filtered_snapshots[-1].timestamp - filtered_snapshots[0].timestamp
                ops_per_second = len(filtered_snapshots) / time_span if time_span > 0 else 0
            else:
                ops_per_second = 0
            
            # Calculate success rate
            success_rate = len(successful_ops) / len(filtered_snapshots)
            
            # Calculate resource utilization
            cpu_values = [s.cpu_usage_percent for s in filtered_snapshots if s.cpu_usage_percent > 0]
            memory_values = [s.memory_usage_mb for s in filtered_snapshots if s.memory_usage_mb > 0]
            
            avg_cpu = statistics.mean(cpu_values) if cpu_values else 0
            avg_memory = statistics.mean(memory_values) if memory_values else 0
            
            return PerformanceStatistics(
                operation_type=operation_type or "all_operations",
                sample_count=len(filtered_snapshots),
                mean_response_time_ms=mean_response,
                median_response_time_ms=median_response,
                p95_response_time_ms=p95_response,
                p99_response_time_ms=p99_response,
                std_deviation_ms=std_dev,
                min_response_time_ms=min_response,
                max_response_time_ms=max_response,
                success_rate=success_rate,
                confidence_interval_95=confidence_interval,
                operations_per_second=ops_per_second,
                cpu_utilization_avg=avg_cpu,
                memory_utilization_avg=avg_memory
            )
    
    def evaluate_a_plus_performance(self, stats: PerformanceStatistics) -> Dict[str, Any]:
        """Evaluate performance against A+ criteria"""
        
        evaluation = {
            "overall_grade": "F",
            "a_plus_achieved": False,
            "criteria_met": {},
            "performance_score": 0,
            "recommendations": []
        }
        
        criteria_results = {}
        
        # Operations per second
        ops_criterion = stats.operations_per_second >= self.a_plus_thresholds["min_ops_per_second"]
        criteria_results["operations_per_second"] = {
            "met": ops_criterion,
            "value": stats.operations_per_second,
            "threshold": self.a_plus_thresholds["min_ops_per_second"],
            "points": 25 if ops_criterion else int((stats.operations_per_second / self.a_plus_thresholds["min_ops_per_second"]) * 25)
        }
        
        # P95 response time
        p95_criterion = stats.p95_response_time_ms <= self.a_plus_thresholds["max_p95_response_ms"]
        criteria_results["p95_response_time"] = {
            "met": p95_criterion,
            "value": stats.p95_response_time_ms,
            "threshold": self.a_plus_thresholds["max_p95_response_ms"],
            "points": 25 if p95_criterion else max(0, int(25 - ((stats.p95_response_time_ms - self.a_plus_thresholds["max_p95_response_ms"]) / 10)))
        }
        
        # Success rate
        success_criterion = stats.success_rate >= self.a_plus_thresholds["min_success_rate"]
        criteria_results["success_rate"] = {
            "met": success_criterion,
            "value": stats.success_rate,
            "threshold": self.a_plus_thresholds["min_success_rate"],
            "points": 25 if success_criterion else int(stats.success_rate * 25)
        }
        
        # Resource utilization
        cpu_criterion = stats.cpu_utilization_avg <= self.a_plus_thresholds["max_cpu_usage"]
        memory_criterion = stats.memory_utilization_avg <= self.a_plus_thresholds["max_memory_usage_mb"]
        resource_criterion = cpu_criterion and memory_criterion
        
        criteria_results["resource_utilization"] = {
            "met": resource_criterion,
            "cpu_value": stats.cpu_utilization_avg,
            "memory_value": stats.memory_utilization_avg,
            "cpu_threshold": self.a_plus_thresholds["max_cpu_usage"],
            "memory_threshold": self.a_plus_thresholds["max_memory_usage_mb"],
            "points": 25 if resource_criterion else 15
        }
        
        # Calculate overall score
        total_points = sum(criterion["points"] for criterion in criteria_results.values())
        evaluation["performance_score"] = total_points
        evaluation["criteria_met"] = criteria_results
        
        # Determine grade
        if total_points >= 95:
            evaluation["overall_grade"] = "A+"
            evaluation["a_plus_achieved"] = True
        elif total_points >= 85:
            evaluation["overall_grade"] = "A"
        elif total_points >= 75:
            evaluation["overall_grade"] = "B+"
        elif total_points >= 65:
            evaluation["overall_grade"] = "B"
        else:
            evaluation["overall_grade"] = "C or below"
        
        # Generate recommendations
        recommendations = []
        if not ops_criterion:
            recommendations.append(f"Improve throughput: {stats.operations_per_second:.1f} ops/sec → target: {self.a_plus_thresholds['min_ops_per_second']} ops/sec")
        
        if not p95_criterion:
            recommendations.append(f"Reduce P95 latency: {stats.p95_response_time_ms:.1f}ms → target: {self.a_plus_thresholds['max_p95_response_ms']}ms")
        
        if not success_criterion:
            recommendations.append(f"Improve success rate: {stats.success_rate:.1%} → target: {self.a_plus_thresholds['min_success_rate']:.1%}")
        
        if not resource_criterion:
            if not cpu_criterion:
                recommendations.append(f"Optimize CPU usage: {stats.cpu_utilization_avg:.1f}% → target: <{self.a_plus_thresholds['max_cpu_usage']}%")
            if not memory_criterion:
                recommendations.append(f"Optimize memory usage: {stats.memory_utilization_avg:.1f}MB → target: <{self.a_plus_thresholds['max_memory_usage_mb']}MB")
        
        evaluation["recommendations"] = recommendations
        
        return evaluation
    
    def generate_performance_report(self, operation_type: Optional[str] = None,
                                  save_to_file: bool = True) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        # Analyze current performance
        stats = self.analyze_performance(operation_type)
        if not stats:
            return {"error": "No performance data available"}
        
        # Evaluate A+ performance
        evaluation = self.evaluate_a_plus_performance(stats)
        
        # Create comprehensive report (ensure JSON serializable)
        report = {
            "report_metadata": {
                "timestamp": datetime.now().isoformat(),
                "operation_type": operation_type or "all_operations",
                "sample_count": int(stats.sample_count),
                "analysis_duration_minutes": float((time.time() - self.snapshots[0].timestamp) / 60) if self.snapshots else 0.0
            },
            "performance_statistics": {
                "response_times": {
                    "mean_ms": float(stats.mean_response_time_ms),
                    "median_ms": float(stats.median_response_time_ms),
                    "p95_ms": float(stats.p95_response_time_ms),
                    "p99_ms": float(stats.p99_response_time_ms),
                    "std_deviation_ms": float(stats.std_deviation_ms),
                    "min_ms": float(stats.min_response_time_ms),
                    "max_ms": float(stats.max_response_time_ms),
                    "confidence_interval_95": [float(stats.confidence_interval_95[0]), float(stats.confidence_interval_95[1])]
                },
                "throughput": {
                    "operations_per_second": float(stats.operations_per_second),
                    "success_rate": float(stats.success_rate)
                },
                "resource_utilization": {
                    "cpu_usage_avg_percent": float(stats.cpu_utilization_avg),
                    "memory_usage_avg_mb": float(stats.memory_utilization_avg)
                }
            },
            "a_plus_evaluation": {
                "overall_grade": str(evaluation["overall_grade"]),
                "a_plus_achieved": bool(evaluation["a_plus_achieved"]),
                "performance_score": int(evaluation["performance_score"]),
                "criteria_met": {
                    k: {
                        "met": bool(v["met"]),
                        "value": float(v.get("value", 0)),
                        "threshold": float(v.get("threshold", 0)),
                        "points": int(v["points"])
                    } if isinstance(v, dict) and "met" in v else v
                    for k, v in evaluation["criteria_met"].items()
                },
                "recommendations": list(evaluation["recommendations"])
            },
            "academic_insights": {
                "statistical_significance": "High" if stats.sample_count > 100 else "Medium" if stats.sample_count > 30 else "Low",
                "confidence_level": "95%",
                "methodology": "Academic-grade statistical analysis with confidence intervals",
                "performance_classification": str(evaluation["overall_grade"])
            }
        }
        
        if save_to_file:
            # Save report to file
            os.makedirs("results/performance_reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/performance_reports/advanced_profile_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📊 Advanced performance report saved: {filename}")
        
        return report
    
    def create_performance_visualization(self, operation_type: Optional[str] = None):
        """Create performance visualization charts"""
        
        with self.lock:
            snapshots = [s for s in self.snapshots if not operation_type or s.operation_type == operation_type]
        
        if len(snapshots) < 10:
            print("⚠️ Insufficient data for visualization (need at least 10 data points)")
            return
        
        # Extract data for plotting
        timestamps = [s.timestamp for s in snapshots]
        response_times = [s.response_time_ms for s in snapshots]
        cpu_usage = [s.cpu_usage_percent for s in snapshots if s.cpu_usage_percent > 0]
        memory_usage = [s.memory_usage_mb for s in snapshots if s.memory_usage_mb > 0]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Advanced Performance Analysis', fontsize=16, fontweight='bold')
        
        # Response time over time
        ax1.plot(timestamps, response_times, color='blue', alpha=0.7)
        ax1.set_title('Response Time Over Time')
        ax1.set_ylabel('Response Time (ms)')
        ax1.set_xlabel('Time')
        ax1.grid(True, alpha=0.3)
        
        # Response time histogram
        ax2.hist(response_times, bins=30, color='green', alpha=0.7, edgecolor='black')
        ax2.set_title('Response Time Distribution')
        ax2.set_xlabel('Response Time (ms)')
        ax2.set_ylabel('Frequency')
        ax2.axvline(np.mean(response_times), color='red', linestyle='--', label=f'Mean: {np.mean(response_times):.1f}ms')
        ax2.axvline(np.percentile(response_times, 95), color='orange', linestyle='--', label=f'P95: {np.percentile(response_times, 95):.1f}ms')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # CPU utilization
        if cpu_usage:
            cpu_timestamps = [s.timestamp for s in snapshots if s.cpu_usage_percent > 0]
            ax3.plot(cpu_timestamps, cpu_usage, color='red', alpha=0.7)
            ax3.set_title('CPU Utilization')
            ax3.set_ylabel('CPU Usage (%)')
            ax3.set_xlabel('Time')
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No CPU data available', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('CPU Utilization - No Data')
        
        # Memory utilization
        if memory_usage:
            memory_timestamps = [s.timestamp for s in snapshots if s.memory_usage_mb > 0]
            ax4.plot(memory_timestamps, memory_usage, color='purple', alpha=0.7)
            ax4.set_title('Memory Utilization')
            ax4.set_ylabel('Memory Usage (MB)')
            ax4.set_xlabel('Time')
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No memory data available', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Memory Utilization - No Data')
        
        plt.tight_layout()
        
        # Save visualization
        os.makedirs("results/performance_visualizations", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/performance_visualizations/performance_analysis_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        print(f"📈 Performance visualization saved: {filename}")
        return filename


# Demonstration usage
async def demo_profiler():
    """Demonstrate advanced profiler capabilities"""
    print("🚀 ADVANCED PERFORMANCE PROFILER DEMO")
    print("=" * 50)
    
    profiler = AdvancedPerformanceProfiler()
    profiler.start_monitoring()
    
    # Simulate authentication operations with varying performance
    print("📊 Simulating authentication operations...")
    
    for i in range(100):
        # Simulate operation timing
        start_time = time.time()
        
        # Simulate some work (authentication process)
        await asyncio.sleep(0.01 + (i % 10) * 0.001)  # Variable latency
        
        response_time = (time.time() - start_time) * 1000
        success = i % 20 != 0  # 95% success rate
        
        profiler.record_operation(
            operation_type="authentication",
            response_time_ms=response_time,
            concurrent_ops=1,
            success=success
        )
    
    # Wait for monitoring data
    await asyncio.sleep(1)
    
    # Generate performance report
    print("\n📈 Generating performance analysis...")
    report = profiler.generate_performance_report("authentication")
    
    # Print key metrics
    stats = profiler.analyze_performance("authentication")
    if stats:
        print(f"\n🏆 PERFORMANCE ANALYSIS RESULTS:")
        print(f"  Operations/sec: {stats.operations_per_second:.1f}")
        print(f"  Mean response: {stats.mean_response_time_ms:.2f}ms")
        print(f"  P95 response: {stats.p95_response_time_ms:.2f}ms")
        print(f"  Success rate: {stats.success_rate:.1%}")
    
    # A+ evaluation
    if "a_plus_evaluation" in report:
        eval_result = report["a_plus_evaluation"]
        print(f"\n🎯 A+ EVALUATION:")
        print(f"  Overall Grade: {eval_result['overall_grade']}")
        print(f"  Performance Score: {eval_result['performance_score']}/100")
        print(f"  A+ Achieved: {'✅' if eval_result['a_plus_achieved'] else '❌'}")
    
    # Create visualization
    profiler.create_performance_visualization("authentication")
    
    profiler.stop_monitoring()
    print("\n✅ Advanced profiler demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demo_profiler())