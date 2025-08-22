#!/usr/bin/env python3
"""
Consciousness System Performance Benchmark Suite
===============================================

Comprehensive performance benchmarking and testing suite for the SynapticOS 
consciousness system. Provides load testing, stress testing, performance 
profiling, and optimization recommendations.
"""

import asyncio
import logging
import time
import statistics
import psutil
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import concurrent.futures
import threading
from collections import defaultdict, deque
import numpy as np

try:
    from ..core.consciousness_bus import ConsciousnessBus
    from ..core.state_manager import StateManager
    from ..core.event_types import EventType, ConsciousnessEvent, EventPriority
    from ..core.data_models import ComponentStatus, ComponentState
    from ..interfaces.consciousness_component import ConsciousnessComponent
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.consciousness_bus import ConsciousnessBus
    from core.state_manager import StateManager
    from core.event_types import EventType, ConsciousnessEvent, EventPriority
    from core.data_models import ComponentStatus, ComponentState
    from interfaces.consciousness_component import ConsciousnessComponent

logger = logging.getLogger('synapticos.performance_benchmark')


class BenchmarkType(Enum):
    """Types of performance benchmarks"""
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    ENDURANCE_TEST = "endurance_test"
    SPIKE_TEST = "spike_test"
    COMPONENT_PROFILE = "component_profile"
    SYSTEM_BASELINE = "system_baseline"


class LoadPattern(Enum):
    """Load generation patterns"""
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    STEP_UP = "step_up"
    SPIKE = "spike"
    WAVE = "wave"
    RANDOM = "random"


@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""
    benchmark_type: BenchmarkType
    duration_seconds: int
    load_pattern: LoadPattern
    
    # Load parameters
    initial_load: int = 10
    max_load: int = 100
    ramp_duration: int = 60
    
    # Test parameters
    target_components: List[str] = field(default_factory=list)
    event_types: List[EventType] = field(default_factory=list)
    
    # Monitoring parameters
    sample_interval: float = 1.0
    collect_detailed_metrics: bool = True
    
    # Output parameters
    output_format: str = "json"  # json, csv, html
    save_raw_data: bool = True


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: datetime
    component_id: str
    metric_name: str
    value: float
    unit: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Benchmark execution result"""
    benchmark_id: str
    config: BenchmarkConfig
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    
    # Performance metrics
    metrics: List[PerformanceMetric] = field(default_factory=list)
    
    # Summary statistics
    response_times: Dict[str, Dict[str, float]] = field(default_factory=dict)
    throughput: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # System state
    system_metrics: List[Dict[str, Any]] = field(default_factory=list)
    component_states: List[Dict[str, Any]] = field(default_factory=list)
    
    # Analysis results
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    performance_score: float = 0.0
    
    # Status
    success: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class LoadGenerator:
    """Load generation configuration"""
    pattern: LoadPattern
    initial_rate: int
    max_rate: int
    duration: int
    ramp_time: int = 60


class PerformanceBenchmark(ConsciousnessComponent):
    """Comprehensive performance benchmarking suite"""
    
    def __init__(self, results_dir: str = "benchmark_results"):
        super().__init__("performance_benchmark", "testing")
        
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Benchmark state
        self.active_benchmarks: Dict[str, BenchmarkResult] = {}
        self.benchmark_history: List[BenchmarkResult] = []
        
        # Load generation
        self.load_generators: Dict[str, asyncio.Task] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}
        
        # Metrics collection
        self.metrics_collectors: Dict[str, asyncio.Task] = {}
        self.collected_metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        
        # System monitoring
        self.system_monitor_task: Optional[asyncio.Task] = None
        self.system_metrics_history: List[Dict[str, Any]] = []
        
        # Performance baselines
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Benchmark templates
        self.benchmark_templates = {
            "quick_health_check": BenchmarkConfig(
                benchmark_type=BenchmarkType.SYSTEM_BASELINE,
                duration_seconds=30,
                load_pattern=LoadPattern.CONSTANT,
                initial_load=5,
                max_load=5
            ),
            "standard_load_test": BenchmarkConfig(
                benchmark_type=BenchmarkType.LOAD_TEST,
                duration_seconds=300,
                load_pattern=LoadPattern.RAMP_UP,
                initial_load=10,
                max_load=100,
                ramp_duration=60
            ),
            "stress_test": BenchmarkConfig(
                benchmark_type=BenchmarkType.STRESS_TEST,
                duration_seconds=600,
                load_pattern=LoadPattern.STEP_UP,
                initial_load=50,
                max_load=500,
                ramp_duration=120
            ),
            "endurance_test": BenchmarkConfig(
                benchmark_type=BenchmarkType.ENDURANCE_TEST,
                duration_seconds=3600,
                load_pattern=LoadPattern.CONSTANT,
                initial_load=50,
                max_load=50
            )
        }
    
    async def initialize(self, consciousness_bus: ConsciousnessBus, state_manager: StateManager) -> bool:
        """Initialize the benchmark suite"""
        await super().initialize(consciousness_bus, state_manager)
        
        try:
            # Load existing baselines
            await self._load_performance_baselines()
            
            # Start system monitoring
            self.system_monitor_task = asyncio.create_task(self._system_monitoring_loop())
            
            logger.info("Performance benchmark suite initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize performance benchmark suite: {e}")
            raise
    
    async def start(self) -> bool:
        """Start the performance benchmark suite"""
        try:
            self.state = ComponentState.HEALTHY
            logger.info(f"Performance benchmark suite {self.component_id} started")
            return True
        except Exception as e:
            logger.error(f"Failed to start performance benchmark suite: {e}")
            self.state = ComponentState.FAILED
            return False
    
    async def stop(self):
        """Stop the performance benchmark suite"""
        try:
            await self.cleanup()
            self.state = ComponentState.DEGRADED  # Stopped but not failed
            logger.info(f"Performance benchmark suite {self.component_id} stopped")
        except Exception as e:
            logger.error(f"Failed to stop performance benchmark suite: {e}")
            self.state = ComponentState.FAILED
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process consciousness events"""
        try:
            if event.event_type == EventType.PERFORMANCE_UPDATE:
                # Handle performance update events during benchmarks
                return True
            elif event.event_type == EventType.HEALTH_CHECK:
                # Handle health check events during benchmarks
                return True
            return True
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False
    
    async def get_status(self) -> ComponentStatus:
        """Get component status"""
        return ComponentStatus(
            component_id=self.component_id,
            component_type="performance_benchmark",
            state=self.state,
            health_score=1.0 if self.state == ComponentState.HEALTHY else 0.5,
            last_heartbeat=datetime.now(),
            response_time_ms=0.0,
            throughput=0.0,
            error_rate=0.0,
            configuration={
                "active_benchmarks": len(self.active_benchmarks),
                "benchmark_history_count": len(self.benchmark_history),
                "performance_baselines_count": len(self.performance_baselines)
            }
        )
    
    async def get_health_status(self) -> ComponentStatus:
        """Get health status"""
        return await self.get_status()
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update component configuration"""
        try:
            # Update benchmark templates if provided
            if "benchmark_templates" in config:
                self.benchmark_templates.update(config["benchmark_templates"])
            
            # Update results directory if provided
            if "results_dir" in config:
                self.results_dir = Path(config["results_dir"])
                self.results_dir.mkdir(exist_ok=True)
            
            logger.info("Performance benchmark configuration updated")
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    async def _load_performance_baselines(self):
        """Load existing performance baselines"""
        baseline_file = self.results_dir / "baselines.json"
        if baseline_file.exists():
            try:
                with open(baseline_file, 'r') as f:
                    self.performance_baselines = json.load(f)
                logger.info(f"Loaded {len(self.performance_baselines)} performance baselines")
            except Exception as e:
                logger.error(f"Error loading performance baselines: {e}")
    
    async def _save_performance_baselines(self):
        """Save performance baselines"""
        baseline_file = self.results_dir / "baselines.json"
        try:
            with open(baseline_file, 'w') as f:
                json.dump(self.performance_baselines, f, indent=2)
            logger.info("Performance baselines saved")
        except Exception as e:
            logger.error(f"Error saving performance baselines: {e}")
    
    async def _system_monitoring_loop(self):
        """Background system monitoring"""
        while True:
            try:
                # Collect system metrics
                system_metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {},
                    "network_io": dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {},
                    "process_count": len(psutil.pids()),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                }
                
                # Add to history (keep last 1000 entries)
                self.system_metrics_history.append(system_metrics)
                if len(self.system_metrics_history) > 1000:
                    self.system_metrics_history.pop(0)
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in system monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def run_benchmark(self, config: BenchmarkConfig, benchmark_id: Optional[str] = None) -> BenchmarkResult:
        """Run a performance benchmark"""
        if benchmark_id is None:
            benchmark_id = f"benchmark_{int(time.time())}"
        
        logger.info(f"Starting benchmark {benchmark_id}: {config.benchmark_type.value}")
        
        # Create benchmark result
        result = BenchmarkResult(
            benchmark_id=benchmark_id,
            config=config,
            start_time=datetime.now(),
            end_time=datetime.now(),  # Will be updated
            duration_seconds=0.0
        )
        
        self.active_benchmarks[benchmark_id] = result
        
        try:
            # Start metrics collection
            await self._start_metrics_collection(benchmark_id, config)
            
            # Start load generation
            await self._start_load_generation(benchmark_id, config)
            
            # Run benchmark for specified duration
            await asyncio.sleep(config.duration_seconds)
            
            # Stop load generation
            await self._stop_load_generation(benchmark_id)
            
            # Stop metrics collection
            await self._stop_metrics_collection(benchmark_id)
            
            # Analyze results
            await self._analyze_benchmark_results(result)
            
            # Update result
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            result.success = True
            
            # Save results
            await self._save_benchmark_results(result)
            
            logger.info(f"Benchmark {benchmark_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Benchmark {benchmark_id} failed: {e}")
            result.success = False
            result.errors.append(str(e))
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
        
        finally:
            # Cleanup
            if benchmark_id in self.active_benchmarks:
                del self.active_benchmarks[benchmark_id]
            
            # Add to history
            self.benchmark_history.append(result)
            
            # Keep only last 100 results in memory
            if len(self.benchmark_history) > 100:
                self.benchmark_history.pop(0)
        
        return result
    
    async def _start_metrics_collection(self, benchmark_id: str, config: BenchmarkConfig):
        """Start collecting performance metrics"""
        self.collected_metrics[benchmark_id] = []
        
        # Start metrics collection task
        collector_task = asyncio.create_task(
            self._metrics_collection_loop(benchmark_id, config)
        )
        self.metrics_collectors[benchmark_id] = collector_task
    
    async def _metrics_collection_loop(self, benchmark_id: str, config: BenchmarkConfig):
        """Metrics collection loop"""
        try:
            while benchmark_id in self.active_benchmarks:
                # Collect component metrics
                if self.consciousness_bus:
                    components = await self.consciousness_bus.get_registered_components()
                    
                    for component in components:
                        if not config.target_components or component.component_id in config.target_components:
                            # Response time metric
                            if component.response_time_ms > 0:
                                metric = PerformanceMetric(
                                    timestamp=datetime.now(),
                                    component_id=component.component_id,
                                    metric_name="response_time",
                                    value=component.response_time_ms,
                                    unit="ms"
                                )
                                self.collected_metrics[benchmark_id].append(metric)
                            
                            # Throughput metric
                            metric = PerformanceMetric(
                                timestamp=datetime.now(),
                                component_id=component.component_id,
                                metric_name="throughput",
                                value=component.throughput,
                                unit="ops/sec"
                            )
                            self.collected_metrics[benchmark_id].append(metric)
                            
                            # Error rate metric
                            metric = PerformanceMetric(
                                timestamp=datetime.now(),
                                component_id=component.component_id,
                                metric_name="error_rate",
                                value=component.error_rate,
                                unit="percentage"
                            )
                            self.collected_metrics[benchmark_id].append(metric)
                            
                            # Health score metric
                            metric = PerformanceMetric(
                                timestamp=datetime.now(),
                                component_id=component.component_id,
                                metric_name="health_score",
                                value=component.health_score,
                                unit="score"
                            )
                            self.collected_metrics[benchmark_id].append(metric)
                
                await asyncio.sleep(config.sample_interval)
                
        except Exception as e:
            logger.error(f"Error in metrics collection loop: {e}")
    
    async def _start_load_generation(self, benchmark_id: str, config: BenchmarkConfig):
        """Start generating load according to the specified pattern"""
        # Create event queue for this benchmark
        self.event_queues[benchmark_id] = asyncio.Queue()
        
        # Start load generator task
        generator_task = asyncio.create_task(
            self._load_generation_loop(benchmark_id, config)
        )
        self.load_generators[benchmark_id] = generator_task
        
        # Start event sender task
        sender_task = asyncio.create_task(
            self._event_sender_loop(benchmark_id, config)
        )
    
    async def _load_generation_loop(self, benchmark_id: str, config: BenchmarkConfig):
        """Generate load events according to pattern"""
        try:
            start_time = time.time()
            
            while benchmark_id in self.active_benchmarks:
                elapsed = time.time() - start_time
                
                # Calculate current load based on pattern
                current_load = self._calculate_load_for_pattern(config, elapsed)
                
                # Generate events at current load rate
                events_per_second = current_load
                interval = 1.0 / max(events_per_second, 1)
                
                # Create test event
                event = ConsciousnessEvent(
                    event_type=config.event_types[0] if config.event_types else EventType.PERFORMANCE_UPDATE,
                    source_component=self.component_id,
                    target_components=config.target_components or ["all"],
                    priority=EventPriority.NORMAL,
                    data={
                        "benchmark_id": benchmark_id,
                        "load_level": current_load,
                        "timestamp": time.time()
                    }
                )
                
                # Queue event for sending
                await self.event_queues[benchmark_id].put(event)
                
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"Error in load generation loop: {e}")
    
    async def _event_sender_loop(self, benchmark_id: str, config: BenchmarkConfig):
        """Send queued events to the consciousness bus"""
        try:
            while benchmark_id in self.active_benchmarks:
                try:
                    # Get event from queue (with timeout)
                    event = await asyncio.wait_for(
                        self.event_queues[benchmark_id].get(),
                        timeout=1.0
                    )
                    
                    # Send event
                    if self.consciousness_bus:
                        await self.consciousness_bus.publish(event)
                    
                except asyncio.TimeoutError:
                    continue  # No events to send
                    
        except Exception as e:
            logger.error(f"Error in event sender loop: {e}")
    
    def _calculate_load_for_pattern(self, config: BenchmarkConfig, elapsed_time: float) -> int:
        """Calculate current load based on pattern and elapsed time"""
        if config.load_pattern == LoadPattern.CONSTANT:
            return config.initial_load
        
        elif config.load_pattern == LoadPattern.RAMP_UP:
            if elapsed_time >= config.ramp_duration:
                return config.max_load
            else:
                progress = elapsed_time / config.ramp_duration
                return int(config.initial_load + (config.max_load - config.initial_load) * progress)
        
        elif config.load_pattern == LoadPattern.STEP_UP:
            steps = 5
            step_duration = config.ramp_duration / steps
            step_size = (config.max_load - config.initial_load) / steps
            current_step = min(int(elapsed_time / step_duration), steps)
            return int(config.initial_load + step_size * current_step)
        
        elif config.load_pattern == LoadPattern.SPIKE:
            spike_duration = 30  # 30 second spikes
            cycle_duration = 120  # 2 minute cycles
            cycle_position = elapsed_time % cycle_duration
            
            if cycle_position < spike_duration:
                return config.max_load
            else:
                return config.initial_load
        
        elif config.load_pattern == LoadPattern.WAVE:
            import math
            wave_period = 300  # 5 minute waves
            amplitude = (config.max_load - config.initial_load) / 2
            offset = config.initial_load + amplitude
            return int(offset + amplitude * math.sin(2 * math.pi * elapsed_time / wave_period))
        
        elif config.load_pattern == LoadPattern.RANDOM:
            import random
            return random.randint(config.initial_load, config.max_load)
        
        return config.initial_load
    
    async def _stop_load_generation(self, benchmark_id: str):
        """Stop load generation for benchmark"""
        if benchmark_id in self.load_generators:
            self.load_generators[benchmark_id].cancel()
            try:
                await self.load_generators[benchmark_id]
            except asyncio.CancelledError:
                pass
            del self.load_generators[benchmark_id]
        
        if benchmark_id in self.event_queues:
            del self.event_queues[benchmark_id]
    
    async def _stop_metrics_collection(self, benchmark_id: str):
        """Stop metrics collection for benchmark"""
        if benchmark_id in self.metrics_collectors:
            self.metrics_collectors[benchmark_id].cancel()
            try:
                await self.metrics_collectors[benchmark_id]
            except asyncio.CancelledError:
                pass
            del self.metrics_collectors[benchmark_id]
    
    async def _analyze_benchmark_results(self, result: BenchmarkResult):
        """Analyze benchmark results and generate insights"""
        try:
            benchmark_id = result.benchmark_id
            metrics = self.collected_metrics.get(benchmark_id, [])
            
            if not metrics:
                logger.warning(f"No metrics collected for benchmark {benchmark_id}")
                return
            
            # Group metrics by component and metric type
            grouped_metrics = defaultdict(lambda: defaultdict(list))
            for metric in metrics:
                grouped_metrics[metric.component_id][metric.metric_name].append(metric.value)
            
            # Calculate summary statistics
            for component_id, component_metrics in grouped_metrics.items():
                result.response_times[component_id] = {}
                result.throughput[component_id] = 0.0
                result.error_rates[component_id] = 0.0
                
                for metric_name, values in component_metrics.items():
                    if metric_name == "response_time":
                        result.response_times[component_id] = {
                            "min": float(min(values)),
                            "max": float(max(values)),
                            "mean": float(statistics.mean(values)),
                            "median": float(statistics.median(values)),
                            "p95": float(np.percentile(values, 95)),
                            "p99": float(np.percentile(values, 99)),
                            "std": float(statistics.stdev(values) if len(values) > 1 else 0)
                        }
                    elif metric_name == "throughput":
                        result.throughput[component_id] = statistics.mean(values)
                    elif metric_name == "error_rate":
                        result.error_rates[component_id] = statistics.mean(values)
            
            # Analyze system resource usage
            result.resource_usage = await self._analyze_resource_usage(result)
            
            # Identify bottlenecks
            result.bottlenecks = await self._identify_bottlenecks(result)
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(result)
            
            # Calculate performance score
            result.performance_score = await self._calculate_performance_score(result)
            
            # Update baselines if this is a baseline test
            if result.config.benchmark_type == BenchmarkType.SYSTEM_BASELINE:
                await self._update_performance_baselines(result)
            
        except Exception as e:
            logger.error(f"Error analyzing benchmark results: {e}")
            result.errors.append(f"Analysis error: {str(e)}")
    
    async def _analyze_resource_usage(self, result: BenchmarkResult) -> Dict[str, Dict[str, float]]:
        """Analyze system resource usage during benchmark"""
        resource_usage = {}
        
        try:
            # Get system metrics during benchmark period
            start_time = result.start_time
            end_time = result.end_time
            
            relevant_metrics = [
                m for m in self.system_metrics_history
                if start_time <= datetime.fromisoformat(m["timestamp"]) <= end_time
            ]
            
            if relevant_metrics:
                cpu_values = [m["cpu_percent"] for m in relevant_metrics]
                memory_values = [m["memory_percent"] for m in relevant_metrics]
                
                resource_usage["system"] = {
                    "cpu_mean": statistics.mean(cpu_values),
                    "cpu_max": max(cpu_values),
                    "memory_mean": statistics.mean(memory_values),
                    "memory_max": max(memory_values)
                }
            
        except Exception as e:
            logger.error(f"Error analyzing resource usage: {e}")
        
        return resource_usage
    
    async def _identify_bottlenecks(self, result: BenchmarkResult) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        try:
            # Check response times
            for component_id, response_times in result.response_times.items():
                if response_times.get("p95", 0) > 1000:  # > 1 second P95
                    bottlenecks.append(f"High response time in {component_id}: P95 = {response_times['p95']:.1f}ms")
                
                if response_times.get("std", 0) > response_times.get("mean", 0):
                    bottlenecks.append(f"High response time variability in {component_id}")
            
            # Check error rates
            for component_id, error_rate in result.error_rates.items():
                if error_rate > 0.01:  # > 1% error rate
                    bottlenecks.append(f"High error rate in {component_id}: {error_rate:.2%}")
            
            # Check resource usage
            system_usage = result.resource_usage.get("system", {})
            if system_usage.get("cpu_max", 0) > 90:
                bottlenecks.append(f"High CPU usage: {system_usage['cpu_max']:.1f}%")
            
            if system_usage.get("memory_max", 0) > 90:
                bottlenecks.append(f"High memory usage: {system_usage['memory_max']:.1f}%")
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
        
        return bottlenecks
    
    async def _generate_recommendations(self, result: BenchmarkResult) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        try:
            # Response time recommendations
            for component_id, response_times in result.response_times.items():
                mean_time = response_times.get("mean", 0)
                p95_time = response_times.get("p95", 0)
                
                if mean_time > 500:
                    recommendations.append(f"Consider optimizing {component_id} - average response time is {mean_time:.1f}ms")
                
                if p95_time > mean_time * 3:
                    recommendations.append(f"Investigate response time spikes in {component_id}")
            
            # Throughput recommendations
            for component_id, throughput in result.throughput.items():
                if throughput < 10:  # Less than 10 ops/sec
                    recommendations.append(f"Low throughput in {component_id}: {throughput:.1f} ops/sec")
            
            # Resource recommendations
            system_usage = result.resource_usage.get("system", {})
            if system_usage.get("cpu_mean", 0) > 70:
                recommendations.append("Consider CPU optimization or scaling")
            
            if system_usage.get("memory_mean", 0) > 80:
                recommendations.append("Consider memory optimization or increasing available memory")
            
            # Load pattern recommendations
            if result.config.load_pattern == LoadPattern.SPIKE and result.bottlenecks:
                recommendations.append("System may need better handling of traffic spikes")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def _calculate_performance_score(self, result: BenchmarkResult) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            score = 100.0
            
            # Deduct points for high response times
            for component_id, response_times in result.response_times.items():
                p95_time = response_times.get("p95", 0)
                if p95_time > 1000:
                    score -= min(20, (p95_time - 1000) / 100)
            
            # Deduct points for high error rates
            for component_id, error_rate in result.error_rates.items():
                if error_rate > 0:
                    score -= min(30, error_rate * 1000)
            
            # Deduct points for resource usage
            system_usage = result.resource_usage.get("system", {})
            cpu_usage = system_usage.get("cpu_max", 0)
            memory_usage = system_usage.get("memory_max", 0)
            
            if cpu_usage > 80:
                score -= (cpu_usage - 80) / 2
            
            if memory_usage > 80:
                score -= (memory_usage - 80) / 2
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 0.0
    
    async def _update_performance_baselines(self, result: BenchmarkResult):
        """Update performance baselines with new data"""
        try:
            for component_id, response_times in result.response_times.items():
                if component_id not in self.performance_baselines:
                    self.performance_baselines[component_id] = {}
                
                baseline_data = {
                    "response_time_mean": float(response_times.get("mean", 0)),
                    "response_time_p95": float(response_times.get("p95", 0)),
                    "throughput": float(result.throughput.get(component_id, 0)),
                    "error_rate": float(result.error_rates.get(component_id, 0)),
                    "last_updated": datetime.now().isoformat()
                }
                self.performance_baselines[component_id].update(baseline_data)
            
            await self._save_performance_baselines()
            
        except Exception as e:
            logger.error(f"Error updating performance baselines: {e}")
    
    async def _save_benchmark_results(self, result: BenchmarkResult):
        """Save benchmark results to file"""
        try:
            # Create filename
            timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"{result.benchmark_id}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            # Convert result to dict
            result_dict = asdict(result)
            
            # Convert datetime objects to ISO strings
            result_dict["start_time"] = result.start_time.isoformat()
            result_dict["end_time"] = result.end_time.isoformat()
            
            # Convert metrics
            result_dict["metrics"] = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "component_id": m.component_id,
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "unit": m.unit,
                    "metadata": m.metadata
                }
                for m in result.metrics
            ]
            
            # Save to JSON file
            with open(filepath, 'w') as f:
                json.dump(result_dict, f, indent=2)
            
            logger.info(f"Benchmark results saved to {filepath}")
            
            # Also save CSV summary if requested
            if result.config.output_format == "csv":
                await self._save_csv_summary(result)
            
        except Exception as e:
            logger.error(f"Error saving benchmark results: {e}")
    
    async def _save_csv_summary(self, result: BenchmarkResult):
        """Save benchmark summary as CSV"""
        try:
            timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"{result.benchmark_id}_{timestamp}_summary.csv"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow([
                    "Component", "Response Time Mean (ms)", "Response Time P95 (ms)",
                    "Throughput (ops/sec)", "Error Rate (%)", "Performance Score"
                ])
                
                # Data rows
                for component_id in result.response_times.keys():
                    response_times = result.response_times.get(component_id, {})
                    writer.writerow([
                        component_id,
                        response_times.get("mean", 0),
                        response_times.get("p95", 0),
                        result.throughput.get(component_id, 0),
                        result.error_rates.get(component_id, 0) * 100,
                        result.performance_score
                    ])
            
            logger.info(f"CSV summary saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving CSV summary: {e}")
    
    async def run_template_benchmark(self, template_name: str) -> BenchmarkResult:
        """Run a predefined benchmark template"""
        if template_name not in self.benchmark_templates:
            raise ValueError(f"Unknown benchmark template: {template_name}")
        
        config = self.benchmark_templates[template_name]
        return await self.run_benchmark(config, f"{template_name}_{int(time.time())}")
    
    async def get_benchmark_history(self, limit: int = 10) -> List[BenchmarkResult]:
        """Get recent benchmark history"""
        return self.benchmark_history[-limit:]
    
    async def get_performance_baselines(self) -> Dict[str, Dict[str, float]]:
        """Get current performance baselines"""
        return self.performance_baselines.copy()
    
    async def compare_with_baseline(self, result: BenchmarkResult) -> Dict[str, Dict[str, float]]:
        """Compare benchmark result with baseline performance"""
        comparison = {}
        
        for component_id, response_times in result.response_times.items():
            if component_id in self.performance_baselines:
                baseline = self.performance_baselines[component_id]
                
                comparison[component_id] = {
                    "response_time_change": (
                        (response_times.get("mean", 0) - baseline.get("response_time_mean", 0)) /
                        max(baseline.get("response_time_mean", 1), 1) * 100
                    ),
                    "throughput_change": (
                        (result.throughput.get(component_id, 0) - baseline.get("throughput", 0)) /
                        max(baseline.get("throughput", 1), 1) * 100
                    ),
                    "error_rate_change": (
                        result.error_rates.get(component_id, 0) - baseline.get("error_rate", 0)
                    ) * 100
                }
        
        return comparison
    
    async def generate_performance_report(self, result: BenchmarkResult) -> str:
        """Generate a comprehensive performance report"""
        report_lines = [
            f"Performance Benchmark Report",
            f"=" * 50,
            f"Benchmark ID: {result.benchmark_id}",
            f"Type: {result.config.benchmark_type.value}",
            f"Duration: {result.duration_seconds:.1f} seconds",
            f"Start Time: {result.start_time}",
            f"Success: {result.success}",
            f"Performance Score: {result.performance_score:.1f}/100",
            "",
            "Component Performance:",
            "-" * 30
        ]
        
        for component_id, response_times in result.response_times.items():
            report_lines.extend([
                f"Component: {component_id}",
                f"  Response Time (mean): {response_times.get('mean', 0):.1f}ms",
                f"  Response Time (P95): {response_times.get('p95', 0):.1f}ms",
                f"  Throughput: {result.throughput.get(component_id, 0):.1f} ops/sec",
                f"  Error Rate: {result.error_rates.get(component_id, 0):.2%}",
                ""
            ])
        
        if result.bottlenecks:
            report_lines.extend([
                "Identified Bottlenecks:",
                "-" * 30
            ])
            for bottleneck in result.bottlenecks:
                report_lines.append(f"• {bottleneck}")
            report_lines.append("")
        
        if result.recommendations:
            report_lines.extend([
                "Recommendations:",
                "-" * 30
            ])
            for recommendation in result.recommendations:
                report_lines.append(f"• {recommendation}")
            report_lines.append("")
        
        # Resource usage
        system_usage = result.resource_usage.get("system", {})
        if system_usage:
            report_lines.extend([
                "System Resource Usage:",
                "-" * 30,
                f"CPU (mean): {system_usage.get('cpu_mean', 0):.1f}%",
                f"CPU (max): {system_usage.get('cpu_max', 0):.1f}%",
                f"Memory (mean): {system_usage.get('memory_mean', 0):.1f}%",
                f"Memory (max): {system_usage.get('memory_max', 0):.1f}%",
                ""
            ])
        
        return "\n".join(report_lines)
    
    async def cleanup(self):
        """Cleanup benchmark resources"""
        try:
            # Cancel all active tasks
            for task in list(self.load_generators.values()):
                task.cancel()
            
            for task in list(self.metrics_collectors.values()):
                task.cancel()
            
            if self.system_monitor_task:
                self.system_monitor_task.cancel()
            
            # Clear data structures
            self.active_benchmarks.clear()
            self.load_generators.clear()
            self.event_queues.clear()
            self.metrics_collectors.clear()
            self.collected_metrics.clear()
            
            logger.info("Performance benchmark cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during benchmark cleanup: {e}")