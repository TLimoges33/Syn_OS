"""
SynOS Performance Monitoring Module
Provides comprehensive metrics collection and monitoring for SynOS components
"""

import time
import psutil
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, CollectorRegistry, 
    generate_latest, CONTENT_TYPE_LATEST
)
import logging

logger = logging.getLogger(__name__)

# Prometheus Metrics
CONSCIOUSNESS_OPERATIONS = Counter(
    'synos_consciousness_operations_total', 
    'Total consciousness operations processed',
    ['operation_type', 'status']
)

CONSCIOUSNESS_DURATION = Histogram(
    'synos_consciousness_processing_duration_seconds',
    'Time spent processing consciousness operations',
    ['operation_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

MEMORY_USAGE = Gauge(
    'synos_memory_usage_bytes',
    'Memory usage by component',
    ['component', 'memory_type']
)

CPU_USAGE = Gauge(
    'synos_cpu_usage_percent',
    'CPU usage by component',
    ['component']
)

SECURITY_EVENTS = Counter(
    'synos_security_events_total',
    'Security events detected',
    ['event_type', 'severity']
)

KERNEL_METRICS = Gauge(
    'synos_kernel_metrics',
    'Kernel-level metrics',
    ['metric_type']
)

SYSTEM_HEALTH = Gauge(
    'synos_system_health_score',
    'Overall system health score (0-100)',
    ['component']
)

@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance at a point in time"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage: Dict[str, float]
    network_io: Dict[str, int]
    consciousness_metrics: Dict[str, Any]
    security_metrics: Dict[str, Any]
    kernel_metrics: Dict[str, Any]

class PerformanceMonitor:
    """Main performance monitoring class"""
    
    def __init__(self, collection_interval: float = 30.0):
        self.collection_interval = collection_interval
        self.snapshots: List[PerformanceSnapshot] = []
        self.max_snapshots = 1000  # Keep last 1000 snapshots
        self.running = False
        
        # Component-specific monitors
        self.consciousness_monitor = ConsciousnessMonitor()
        self.security_monitor = SecurityMonitor()
        self.kernel_monitor = KernelMonitor()
        
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.running = True
        logger.info("Performance monitoring started")
        
        while self.running:
            try:
                snapshot = await self._collect_metrics()
                self._update_prometheus_metrics(snapshot)
                
                # Store snapshot
                self.snapshots.append(snapshot)
                if len(self.snapshots) > self.max_snapshots:
                    self.snapshots.pop(0)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False
        logger.info("Performance monitoring stopped")
    
    async def _collect_metrics(self) -> PerformanceSnapshot:
        """Collect all system metrics"""
        timestamp = datetime.now()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_usage = {
            partition.mountpoint: psutil.disk_usage(partition.mountpoint).percent
            for partition in psutil.disk_partitions()
            if partition.fstype
        }
        network_io = psutil.net_io_counters()._asdict()
        
        # Component-specific metrics
        consciousness_metrics = await self.consciousness_monitor.collect_metrics()
        security_metrics = await self.security_monitor.collect_metrics()
        kernel_metrics = await self.kernel_monitor.collect_metrics()
        
        return PerformanceSnapshot(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available=memory.available,
            disk_usage=disk_usage,
            network_io=network_io,
            consciousness_metrics=consciousness_metrics,
            security_metrics=security_metrics,
            kernel_metrics=kernel_metrics
        )
    
    def _update_prometheus_metrics(self, snapshot: PerformanceSnapshot):
        """Update Prometheus metrics with collected data"""
        # System metrics
        MEMORY_USAGE.labels(component='system', memory_type='used').set(
            (100 - snapshot.memory_percent) * snapshot.memory_available / 100
        )
        MEMORY_USAGE.labels(component='system', memory_type='available').set(
            snapshot.memory_available
        )
        CPU_USAGE.labels(component='system').set(snapshot.cpu_percent)
        
        # Component metrics
        for component, metrics in {
            'consciousness': snapshot.consciousness_metrics,
            'security': snapshot.security_metrics,
            'kernel': snapshot.kernel_metrics
        }.items():
            if 'memory_usage' in metrics:
                MEMORY_USAGE.labels(component=component, memory_type='used').set(
                    metrics['memory_usage']
                )
            if 'cpu_usage' in metrics:
                CPU_USAGE.labels(component=component).set(metrics['cpu_usage'])
            if 'health_score' in metrics:
                SYSTEM_HEALTH.labels(component=component).set(metrics['health_score'])
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        if not self.snapshots:
            return {"status": "no_data", "message": "No monitoring data available"}
        
        recent_snapshots = self.snapshots[-10:]  # Last 10 snapshots
        avg_cpu = sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots)
        avg_memory = sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots)
        
        # Calculate overall health score
        health_score = self._calculate_health_score(recent_snapshots)
        
        return {
            "status": "healthy" if health_score > 80 else "degraded" if health_score > 60 else "critical",
            "health_score": health_score,
            "metrics": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_percent": avg_memory,
                "total_snapshots": len(self.snapshots),
                "monitoring_duration_hours": (
                    self.snapshots[-1].timestamp - self.snapshots[0].timestamp
                ).total_seconds() / 3600 if len(self.snapshots) > 1 else 0
            },
            "components": {
                "consciousness": recent_snapshots[-1].consciousness_metrics,
                "security": recent_snapshots[-1].security_metrics,
                "kernel": recent_snapshots[-1].kernel_metrics
            }
        }
    
    def _calculate_health_score(self, snapshots: List[PerformanceSnapshot]) -> float:
        """Calculate overall system health score (0-100)"""
        if not snapshots:
            return 0.0
        
        avg_cpu = sum(s.cpu_percent for s in snapshots) / len(snapshots)
        avg_memory = sum(s.memory_percent for s in snapshots) / len(snapshots)
        
        # Health score calculation (simple algorithm)
        cpu_score = max(0, 100 - avg_cpu)  # Lower CPU usage = higher score
        memory_score = max(0, 100 - avg_memory)  # Lower memory usage = higher score
        
        # Component health scores
        consciousness_health = snapshots[-1].consciousness_metrics.get('health_score', 50)
        security_health = snapshots[-1].security_metrics.get('health_score', 50)
        kernel_health = snapshots[-1].kernel_metrics.get('health_score', 50)
        
        # Weighted average
        return (
            cpu_score * 0.2 +
            memory_score * 0.2 +
            consciousness_health * 0.3 +
            security_health * 0.2 +
            kernel_health * 0.1
        )

class ConsciousnessMonitor:
    """Monitor consciousness system performance"""
    
    def __init__(self):
        self.operation_times = []
        self.error_count = 0
        self.last_operation_time = None
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect consciousness-specific metrics"""
        # Simulate consciousness metrics (replace with actual implementation)
        avg_operation_time = (
            sum(self.operation_times[-100:]) / len(self.operation_times[-100:])
            if self.operation_times else 0
        )
        
        health_score = min(100, max(0, 100 - (avg_operation_time * 10) - (self.error_count * 5)))
        
        return {
            "health_score": health_score,
            "avg_operation_time": avg_operation_time,
            "error_count": self.error_count,
            "operations_per_minute": len(self.operation_times[-60:]) if self.operation_times else 0,
            "memory_usage": psutil.Process().memory_info().rss,  # Current process memory
            "cpu_usage": psutil.Process().cpu_percent()
        }
    
    def record_operation(self, operation_type: str, duration: float, success: bool = True):
        """Record a consciousness operation"""
        CONSCIOUSNESS_OPERATIONS.labels(
            operation_type=operation_type, 
            status='success' if success else 'error'
        ).inc()
        
        CONSCIOUSNESS_DURATION.labels(operation_type=operation_type).observe(duration)
        
        self.operation_times.append(duration)
        if not success:
            self.error_count += 1
        
        # Keep only recent operations
        if len(self.operation_times) > 1000:
            self.operation_times = self.operation_times[-500:]

class SecurityMonitor:
    """Monitor security system performance"""
    
    def __init__(self):
        self.threat_count = 0
        self.scan_times = []
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect security-specific metrics"""
        avg_scan_time = (
            sum(self.scan_times[-50:]) / len(self.scan_times[-50:])
            if self.scan_times else 0
        )
        
        health_score = min(100, max(0, 100 - (self.threat_count * 10) - (avg_scan_time * 5)))
        
        return {
            "health_score": health_score,
            "threat_count": self.threat_count,
            "avg_scan_time": avg_scan_time,
            "scans_per_hour": len(self.scan_times[-60:]) if self.scan_times else 0,
            "memory_usage": psutil.Process().memory_info().rss,
            "cpu_usage": psutil.Process().cpu_percent()
        }
    
    def record_security_event(self, event_type: str, severity: str):
        """Record a security event"""
        SECURITY_EVENTS.labels(event_type=event_type, severity=severity).inc()
        
        if severity in ['high', 'critical']:
            self.threat_count += 1

class KernelMonitor:
    """Monitor kernel performance"""
    
    def __init__(self):
        self.interrupt_count = 0
        self.context_switches = 0
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect kernel-specific metrics"""
        # Get system-level kernel metrics
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        # Simulate kernel health (replace with actual kernel metrics)
        health_score = min(100, max(0, 100 - (self.interrupt_count / 1000)))
        
        KERNEL_METRICS.labels(metric_type='uptime').set(uptime)
        KERNEL_METRICS.labels(metric_type='interrupt_count').set(self.interrupt_count)
        
        return {
            "health_score": health_score,
            "uptime_seconds": uptime,
            "interrupt_count": self.interrupt_count,
            "context_switches": self.context_switches,
            "memory_usage": 0,  # Kernel memory usage (would need kernel module)
            "cpu_usage": 0      # Kernel CPU usage
        }

# Decorators for automatic monitoring
def monitor_consciousness_operation(operation_type: str):
    """Decorator to automatically monitor consciousness operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Get monitor instance (would need proper dependency injection)
                monitor = getattr(wrapper, '_monitor', None)
                if monitor and hasattr(monitor, 'consciousness_monitor'):
                    monitor.consciousness_monitor.record_operation(
                        operation_type, duration, True
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                monitor = getattr(wrapper, '_monitor', None)
                if monitor and hasattr(monitor, 'consciousness_monitor'):
                    monitor.consciousness_monitor.record_operation(
                        operation_type, duration, False
                    )
                
                raise e
        return wrapper
    return decorator

def monitor_security_scan(scan_type: str):
    """Decorator to automatically monitor security scans"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                monitor = getattr(wrapper, '_monitor', None)
                if monitor and hasattr(monitor, 'security_monitor'):
                    monitor.security_monitor.scan_times.append(duration)
                
                return result
            except Exception as e:
                monitor = getattr(wrapper, '_monitor', None)
                if monitor and hasattr(monitor, 'security_monitor'):
                    monitor.security_monitor.record_security_event(
                        'scan_error', 'high'
                    )
                raise e
        return wrapper
    return decorator

# Global monitor instance
global_monitor: Optional[PerformanceMonitor] = None

def get_monitor() -> PerformanceMonitor:
    """Get the global monitor instance"""
    global global_monitor
    if global_monitor is None:
        global_monitor = PerformanceMonitor()
    return global_monitor

def get_prometheus_metrics() -> str:
    """Get current Prometheus metrics"""
    return generate_latest()

if __name__ == "__main__":
    # Example usage
    async def main():
        monitor = PerformanceMonitor(collection_interval=10.0)
        
        # Start monitoring
        monitoring_task = asyncio.create_task(monitor.start_monitoring())
        
        # Run for 60 seconds
        await asyncio.sleep(60)
        
        # Stop monitoring
        monitor.stop_monitoring()
        await monitoring_task
        
        # Generate report
        report = monitor.get_health_report()
        print("Health Report:", report)
    
    asyncio.run(main())
