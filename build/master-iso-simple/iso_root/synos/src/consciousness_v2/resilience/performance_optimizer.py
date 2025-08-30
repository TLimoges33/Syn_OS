"""
NATS Performance Optimization and Load Testing
==============================================

Provides performance monitoring, optimization, and load testing
capabilities for NATS message processing in the consciousness system.
"""

import asyncio
import time
import json
import logging
import statistics
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import deque, defaultdict
import psutil
import nats
from nats.js import JetStreamContext


@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    timestamp: datetime
    message_count: int = 0
    messages_per_second: float = 0.0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    connection_count: int = 0
    queue_depth: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'message_count': self.message_count,
            'messages_per_second': self.messages_per_second,
            'avg_latency_ms': self.avg_latency_ms,
            'min_latency_ms': self.min_latency_ms,
            'max_latency_ms': self.max_latency_ms,
            'p95_latency_ms': self.p95_latency_ms,
            'p99_latency_ms': self.p99_latency_ms,
            'error_count': self.error_count,
            'error_rate': self.error_rate,
            'cpu_usage': self.cpu_usage,
            'memory_usage_mb': self.memory_usage_mb,
            'connection_count': self.connection_count,
            'queue_depth': self.queue_depth
        }


@dataclass
class LoadTestConfig:
    """Load test configuration"""
    duration_seconds: int = 60
    message_rate: int = 100  # messages per second
    concurrent_publishers: int = 5
    concurrent_subscribers: int = 3
    message_size_bytes: int = 1024
    subjects: List[str] = field(default_factory=lambda: ['consciousness.>', 'orchestrator.>', 'security.>'])
    ramp_up_seconds: int = 10
    ramp_down_seconds: int = 10
    enable_persistence: bool = True
    enable_acknowledgments: bool = True
    max_pending_acks: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'duration_seconds': self.duration_seconds,
            'message_rate': self.message_rate,
            'concurrent_publishers': self.concurrent_publishers,
            'concurrent_subscribers': self.concurrent_subscribers,
            'message_size_bytes': self.message_size_bytes,
            'subjects': self.subjects,
            'ramp_up_seconds': self.ramp_up_seconds,
            'ramp_down_seconds': self.ramp_down_seconds,
            'enable_persistence': self.enable_persistence,
            'enable_acknowledgments': self.enable_acknowledgments,
            'max_pending_acks': self.max_pending_acks
        }


@dataclass
class LoadTestResult:
    """Load test result"""
    config: LoadTestConfig
    start_time: datetime
    end_time: datetime
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_errors: int = 0
    metrics_history: List[PerformanceMetrics] = field(default_factory=list)
    peak_throughput: float = 0.0
    avg_throughput: float = 0.0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'config': self.config.to_dict(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': (self.end_time - self.start_time).total_seconds(),
            'total_messages_sent': self.total_messages_sent,
            'total_messages_received': self.total_messages_received,
            'total_errors': self.total_errors,
            'peak_throughput': self.peak_throughput,
            'avg_throughput': self.avg_throughput,
            'success_rate': self.success_rate,
            'metrics_count': len(self.metrics_history)
        }


class PerformanceMonitor:
    """
    Real-time performance monitoring for NATS operations
    """
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.latency_samples: deque = deque(maxlen=10000)
        self.message_counts: deque = deque(maxlen=window_size)
        self.error_counts: deque = deque(maxlen=window_size)
        self.timestamps: deque = deque(maxlen=window_size)
        
        # Thread-safe counters
        self._lock = threading.Lock()
        self._message_count = 0
        self._error_count = 0
        self._connection_count = 0
        self._queue_depth = 0
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.metric_callbacks: List[Callable[[PerformanceMetrics], None]] = []
    
    def start_monitoring(self, interval_seconds: float = 1.0):
        """Start performance monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self._monitor_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        self.logger.info("Performance monitoring stopped")
    
    def record_message(self, latency_ms: float = 0.0):
        """Record a processed message"""
        with self._lock:
            self._message_count += 1
            if latency_ms > 0:
                self.latency_samples.append(latency_ms)
    
    def record_error(self):
        """Record an error"""
        with self._lock:
            self._error_count += 1
    
    def update_connection_count(self, count: int):
        """Update connection count"""
        with self._lock:
            self._connection_count = count
    
    def update_queue_depth(self, depth: int):
        """Update queue depth"""
        with self._lock:
            self._queue_depth = depth
    
    def add_metric_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """Add metric callback"""
        self.metric_callbacks.append(callback)
    
    def _monitor_loop(self, interval_seconds: float):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                
                # Store metrics
                self.message_counts.append(metrics.message_count)
                self.error_counts.append(metrics.error_count)
                self.timestamps.append(metrics.timestamp)
                
                # Call callbacks
                for callback in self.metric_callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        self.logger.error(f"Metric callback error: {e}")
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval_seconds)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        now = datetime.now()
        
        with self._lock:
            message_count = self._message_count
            error_count = self._error_count
            connection_count = self._connection_count
            queue_depth = self._queue_depth
            latency_samples = list(self.latency_samples)
        
        # Calculate throughput
        messages_per_second = 0.0
        if len(self.message_counts) >= 2 and len(self.timestamps) >= 2:
            time_diff = (self.timestamps[-1] - self.timestamps[0]).total_seconds()
            if time_diff > 0:
                message_diff = sum(self.message_counts) - sum(list(self.message_counts)[:-10])
                messages_per_second = message_diff / min(time_diff, 10.0)
        
        # Calculate latency statistics
        avg_latency = 0.0
        min_latency = 0.0
        max_latency = 0.0
        p95_latency = 0.0
        p99_latency = 0.0
        
        if latency_samples:
            avg_latency = statistics.mean(latency_samples)
            min_latency = min(latency_samples)
            max_latency = max(latency_samples)
            
            sorted_samples = sorted(latency_samples)
            n = len(sorted_samples)
            p95_latency = sorted_samples[int(n * 0.95)] if n > 0 else 0.0
            p99_latency = sorted_samples[int(n * 0.99)] if n > 0 else 0.0
        
        # Calculate error rate
        error_rate = 0.0
        if message_count > 0:
            error_rate = (error_count / message_count) * 100.0
        
        # Get system metrics
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_usage_mb = memory_info.used / (1024 * 1024)
        
        return PerformanceMetrics(
            timestamp=now,
            message_count=message_count,
            messages_per_second=messages_per_second,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            error_count=error_count,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            connection_count=connection_count,
            queue_depth=queue_depth
        )
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self._collect_metrics()
    
    def reset_counters(self):
        """Reset all counters"""
        with self._lock:
            self._message_count = 0
            self._error_count = 0
            self.latency_samples.clear()
            self.message_counts.clear()
            self.error_counts.clear()
            self.timestamps.clear()


class NATSLoadTester:
    """
    NATS load testing framework
    """
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.logger = logging.getLogger(__name__)
        self.monitor = PerformanceMonitor()
        
        # Test state
        self._test_running = False
        self._publishers: List[nats.NATS] = []
        self._subscribers: List[nats.NATS] = []
        self._js_contexts: List[JetStreamContext] = []
        
        # Results
        self.current_result: Optional[LoadTestResult] = None
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """
        Run a comprehensive load test
        
        Args:
            config: Load test configuration
            
        Returns:
            LoadTestResult with detailed metrics
        """
        self.logger.info(f"Starting load test with config: {config.to_dict()}")
        
        # Initialize result
        start_time = datetime.now()
        result = LoadTestResult(
            config=config,
            start_time=start_time,
            end_time=start_time  # Will be updated
        )
        self.current_result = result
        
        try:
            # Setup monitoring
            self.monitor.reset_counters()
            self.monitor.add_metric_callback(self._record_metrics)
            self.monitor.start_monitoring(interval_seconds=1.0)
            
            # Setup publishers and subscribers
            await self._setup_publishers(config)
            await self._setup_subscribers(config)
            
            # Run test phases
            await self._run_ramp_up_phase(config)
            await self._run_steady_state_phase(config)
            await self._run_ramp_down_phase(config)
            
            # Finalize results
            result.end_time = datetime.now()
            await self._calculate_final_metrics(result)
            
            self.logger.info(f"Load test completed: {result.to_dict()}")
            return result
            
        except Exception as e:
            self.logger.error(f"Load test failed: {e}")
            result.end_time = datetime.now()
            raise
        finally:
            # Cleanup
            self.monitor.stop_monitoring()
            await self._cleanup_connections()
            self._test_running = False
    
    async def _setup_publishers(self, config: LoadTestConfig):
        """Setup publisher connections"""
        self.logger.info(f"Setting up {config.concurrent_publishers} publishers")
        
        for i in range(config.concurrent_publishers):
            try:
                nc = await nats.connect(self.nats_url)
                js = nc.jetstream()
                
                self._publishers.append(nc)
                self._js_contexts.append(js)
                
            except Exception as e:
                self.logger.error(f"Failed to setup publisher {i}: {e}")
                raise
    
    async def _setup_subscribers(self, config: LoadTestConfig):
        """Setup subscriber connections"""
        self.logger.info(f"Setting up {config.concurrent_subscribers} subscribers")
        
        for i in range(config.concurrent_subscribers):
            try:
                nc = await nats.connect(self.nats_url)
                js = nc.jetstream()
                
                # Subscribe to all test subjects
                for subject in config.subjects:
                    await js.subscribe(
                        subject,
                        cb=self._message_handler,
                        manual_ack=config.enable_acknowledgments,
                        max_pending=config.max_pending_acks
                    )
                
                self._subscribers.append(nc)
                
            except Exception as e:
                self.logger.error(f"Failed to setup subscriber {i}: {e}")
                raise
    
    async def _message_handler(self, msg):
        """Handle received messages"""
        try:
            # Record message processing
            start_time = time.time()
            
            # Simulate processing
            await asyncio.sleep(0.001)  # 1ms processing time
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            self.monitor.record_message(latency_ms)
            
            # Acknowledge if required
            if hasattr(msg, 'ack'):
                await msg.ack()
            
            # Update result
            if self.current_result:
                self.current_result.total_messages_received += 1
                
        except Exception as e:
            self.logger.error(f"Message handler error: {e}")
            self.monitor.record_error()
            if self.current_result:
                self.current_result.total_errors += 1
    
    async def _run_ramp_up_phase(self, config: LoadTestConfig):
        """Run ramp-up phase"""
        if config.ramp_up_seconds <= 0:
            return
        
        self.logger.info(f"Starting ramp-up phase ({config.ramp_up_seconds}s)")
        self._test_running = True
        
        # Gradually increase message rate
        steps = min(config.ramp_up_seconds, 10)
        step_duration = config.ramp_up_seconds / steps
        
        for step in range(steps):
            if not self._test_running:
                break
            
            # Calculate current rate
            rate_factor = (step + 1) / steps
            current_rate = int(config.message_rate * rate_factor)
            
            # Send messages for this step
            await self._send_messages_for_duration(
                config, current_rate, step_duration
            )
    
    async def _run_steady_state_phase(self, config: LoadTestConfig):
        """Run steady-state phase"""
        self.logger.info(f"Starting steady-state phase ({config.duration_seconds}s)")
        
        await self._send_messages_for_duration(
            config, config.message_rate, config.duration_seconds
        )
    
    async def _run_ramp_down_phase(self, config: LoadTestConfig):
        """Run ramp-down phase"""
        if config.ramp_down_seconds <= 0:
            return
        
        self.logger.info(f"Starting ramp-down phase ({config.ramp_down_seconds}s)")
        
        # Gradually decrease message rate
        steps = min(config.ramp_down_seconds, 10)
        step_duration = config.ramp_down_seconds / steps
        
        for step in range(steps):
            if not self._test_running:
                break
            
            # Calculate current rate
            rate_factor = (steps - step) / steps
            current_rate = int(config.message_rate * rate_factor)
            
            # Send messages for this step
            await self._send_messages_for_duration(
                config, current_rate, step_duration
            )
    
    async def _send_messages_for_duration(self, config: LoadTestConfig, 
                                        rate: int, duration: float):
        """Send messages at specified rate for duration"""
        if rate <= 0:
            await asyncio.sleep(duration)
            return
        
        interval = 1.0 / rate if rate > 0 else 1.0
        end_time = time.time() + duration
        
        # Create message template
        message_template = {
            'id': '',
            'type': 'load_test.message',
            'source': 'load_tester',
            'timestamp': '',
            'data': {
                'payload': 'x' * (config.message_size_bytes - 200),  # Approximate size
                'sequence': 0
            },
            'priority': 5
        }
        
        sequence = 0
        
        while time.time() < end_time and self._test_running:
            try:
                # Prepare message
                sequence += 1
                message = message_template.copy()
                message['id'] = f"load_test_{sequence}_{time.time()}"
                message['timestamp'] = datetime.now().isoformat()
                message['data']['sequence'] = sequence
                
                # Select random subject and publisher
                subject = config.subjects[sequence % len(config.subjects)]
                publisher_idx = sequence % len(self._publishers)
                js = self._js_contexts[publisher_idx]
                
                # Send message
                start_time = time.time()
                
                if config.enable_persistence:
                    await js.publish(subject, json.dumps(message).encode())
                else:
                    await self._publishers[publisher_idx].publish(
                        subject, json.dumps(message).encode()
                    )
                
                # Record metrics
                send_latency = (time.time() - start_time) * 1000
                self.monitor.record_message(send_latency)
                
                # Update result
                if self.current_result:
                    self.current_result.total_messages_sent += 1
                
                # Rate limiting
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Send message error: {e}")
                self.monitor.record_error()
                if self.current_result:
                    self.current_result.total_errors += 1
    
    def _record_metrics(self, metrics: PerformanceMetrics):
        """Record metrics in test result"""
        if self.current_result:
            self.current_result.metrics_history.append(metrics)
    
    async def _calculate_final_metrics(self, result: LoadTestResult):
        """Calculate final test metrics"""
        if not result.metrics_history:
            return
        
        # Calculate peak and average throughput
        throughputs = [m.messages_per_second for m in result.metrics_history]
        result.peak_throughput = max(throughputs) if throughputs else 0.0
        result.avg_throughput = statistics.mean(throughputs) if throughputs else 0.0
        
        # Calculate success rate
        total_messages = result.total_messages_sent
        if total_messages > 0:
            result.success_rate = ((total_messages - result.total_errors) / total_messages) * 100.0
        
        self.logger.info(f"Final metrics - Peak: {result.peak_throughput:.1f} msg/s, "
                        f"Avg: {result.avg_throughput:.1f} msg/s, "
                        f"Success: {result.success_rate:.1f}%")
    
    async def _cleanup_connections(self):
        """Cleanup all connections"""
        self.logger.info("Cleaning up connections")
        
        # Close publishers
        for nc in self._publishers:
            try:
                await nc.close()
            except Exception as e:
                self.logger.error(f"Error closing publisher: {e}")
        
        # Close subscribers
        for nc in self._subscribers:
            try:
                await nc.close()
            except Exception as e:
                self.logger.error(f"Error closing subscriber: {e}")
        
        self._publishers.clear()
        self._subscribers.clear()
        self._js_contexts.clear()
    
    def stop_test(self):
        """Stop running test"""
        self._test_running = False
        self.logger.info("Load test stop requested")


class PerformanceOptimizer:
    """
    NATS performance optimization recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_performance(self, metrics_history: List[PerformanceMetrics]) -> Dict[str, Any]:
        """
        Analyze performance metrics and provide optimization recommendations
        
        Args:
            metrics_history: List of performance metrics
            
        Returns:
            Analysis results with recommendations
        """
        if not metrics_history:
            return {'error': 'No metrics provided'}
        
        analysis = {
            'summary': self._analyze_summary(metrics_history),
            'bottlenecks': self._identify_bottlenecks(metrics_history),
            'recommendations': self._generate_recommendations(metrics_history),
            'trends': self._analyze_trends(metrics_history)
        }
        
        return analysis
    
    def _analyze_summary(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze performance summary"""
        if not metrics:
            return {}
        
        throughputs = [m.messages_per_second for m in metrics]
        latencies = [m.avg_latency_ms for m in metrics if m.avg_latency_ms > 0]
        error_rates = [m.error_rate for m in metrics]
        cpu_usage = [m.cpu_usage for m in metrics]
        memory_usage = [m.memory_usage_mb for m in metrics]
        
        return {
            'peak_throughput': max(throughputs) if throughputs else 0,
            'avg_throughput': statistics.mean(throughputs) if throughputs else 0,
            'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
            'max_latency_ms': max([m.max_latency_ms for m in metrics]) if metrics else 0,
            'avg_error_rate': statistics.mean(error_rates) if error_rates else 0,
            'peak_cpu_usage': max(cpu_usage) if cpu_usage else 0,
            'avg_memory_usage_mb': statistics.mean(memory_usage) if memory_usage else 0,
            'duration_minutes': len(metrics) / 60.0
        }
    
    def _identify_bottlenecks(self, metrics: List[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        if not metrics:
            return bottlenecks
        
        # High latency bottleneck
        high_latency_count = sum(1 for m in metrics if m.avg_latency_ms > 100)
        if high_latency_count > len(metrics) * 0.1:  # More than 10% of samples
            bottlenecks.append({
                'type': 'high_latency',
                'severity': 'high' if high_latency_count > len(metrics) * 0.3 else 'medium',
                'description': f'High latency detected in {high_latency_count} samples',
                'affected_percentage': (high_latency_count / len(metrics)) * 100
            })
        
        # High error rate bottleneck
        high_error_count = sum(1 for m in metrics if m.error_rate > 5.0)
        if high_error_count > 0:
            bottlenecks.append({
                'type': 'high_error_rate',
                'severity': 'critical' if high_error_count > len(metrics) * 0.1 else 'medium',
                'description': f'High error rate detected in {high_error_count} samples',
                'max_error_rate': max(m.error_rate for m in metrics)
            })
        
        # CPU bottleneck
        high_cpu_count = sum(1 for m in metrics if m.cpu_usage > 80.0)
        if high_cpu_count > len(metrics) * 0.2:
            bottlenecks.append({
                'type': 'cpu_bottleneck',
                'severity': 'high',
                'description': f'High CPU usage detected in {high_cpu_count} samples',
                'peak_cpu_usage': max(m.cpu_usage for m in metrics)
            })
        
        # Memory bottleneck
        memory_values = [m.memory_usage_mb for m in metrics if m.memory_usage_mb > 0]
        if memory_values:
            avg_memory = statistics.mean(memory_values)
            if avg_memory > 1024:  # More than 1GB
                bottlenecks.append({
                    'type': 'memory_usage',
                    'severity': 'medium' if avg_memory < 2048 else 'high',
                    'description': f'High memory usage: {avg_memory:.1f} MB average',
                    'peak_memory_mb': max(memory_values)
                })
        
        return bottlenecks
    
    def _generate_recommendations(self, metrics: List[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if not metrics:
            return recommendations
        
        summary = self._analyze_summary(metrics)
        bottlenecks = self._identify_bottlenecks(metrics)
        
        # Throughput recommendations
        if summary['avg_throughput'] < 100:
            recommendations.append({
                'category': 'throughput',
                'priority': 'high',
                'title': 'Increase Message Throughput',
                'description': 'Current throughput is below optimal levels',
                'actions': [
                    'Increase concurrent publishers',
                    'Optimize message serialization',
                    'Use message batching',
                    'Consider connection pooling'
                ]
            })
        
        # Latency recommendations
        if summary['avg_latency_ms'] > 50:
            recommendations.append({
                'category': 'latency',
                'priority': 'high',
                'title': 'Reduce Message Latency',
                'description': f'Average latency is {summary["avg_latency_ms"]:.1f}ms',
                'actions': [
                    'Optimize message processing logic',
                    'Reduce message size',
                    'Use local NATS clustering',
                    'Implement message compression'
                ]
            })
        
        # Error rate recommendations
        if summary['avg_error_rate'] > 1.0:
            recommendations.append({
                'category': 'reliability',
                'priority': 'critical',
                'title': 'Reduce Error Rate',
                'description': f'Error rate is {summary["avg_error_rate"]:.1f}%',
                'actions': [
                    'Implement circuit breakers',
                    'Add retry mechanisms',
                    'Improve error handling',
                    'Monitor connection health'
                ]
            })
        
        # Resource recommendations
        if summary['peak_cpu_usage'] > 80:
            recommendations.append({
                'category': 'resources',
                'priority': 'medium',
                'title': 'Optimize CPU Usage',
                'description': f'Peak CPU usage: {summary["peak_cpu_usage"]:.1f}%',
                'actions': [
                    'Profile CPU-intensive operations',
                    'Implement async processing',
                    'Scale horizontally',
                    'Optimize algorithms'
                ]
            })
        
        if summary['avg_memory_usage_mb'] > 1024:
            recommendations.append({
                'category': 'resources',
                'priority': 'medium',
                'title': 'Optimize Memory Usage',
                'description': f'Average memory usage: {summary["avg_memory_usage_mb"]:.1f} MB',
                'actions': [
                    'Implement message streaming',
                    'Use memory-efficient data structures',
                    'Add garbage collection tuning',
                    'Implement message compression'
                ]
            })
        
        return recommendations
    
    def _analyze_trends(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze performance trends"""
        if len(metrics) < 10:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Split into first and second half for comparison
        mid_point = len(metrics) // 2
        first_half = metrics[:mid_point]
        second_half = metrics[mid_point:]
        
        first_avg_throughput = statistics.mean(m.messages_per_second for m in first_half)
        second_avg_throughput = statistics.mean(m.messages_per_second for m in second_half)
        
        first_avg_latency = statistics.mean(m.avg_latency_ms for m in first_half if m.avg_latency_ms > 0)
        second_avg_latency = statistics.mean(m.avg_latency_ms for m in second_half if m.avg_latency_ms > 0)
        
        throughput_trend = 'improving' if second_avg_throughput > first_avg_throughput else 'declining'
        latency_trend = 'improving' if second_avg_latency < first_avg_latency else 'declining'
        
        return {
            'throughput_trend': throughput_trend,
            'throughput_change_percent': ((second_avg_throughput - first_avg_throughput) / max(first_avg_throughput, 1)) * 100,
            'latency_trend': latency_trend,
            'latency_change_percent': ((second_avg_latency - first_avg_latency) / max(first_avg_latency, 1)) * 100,
            'first_half_avg_throughput': first_avg_throughput,
            'second_half_avg_throughput': second_avg_throughput,
            'first_half_avg_latency': first_avg_latency,
            'second_half_avg_latency': second_avg_latency
        }


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()