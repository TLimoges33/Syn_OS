"""
NATS Monitoring and Alerting Integration
=======================================

Provides comprehensive monitoring, metrics collection, and alerting
for NATS operations in the consciousness system.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'name': self.name,
            'severity': self.severity.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'labels': self.labels,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class Metric:
    """Metric data structure"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'help': self.help_text
        }


class MetricsCollector:
    """
    Collects and manages metrics for NATS operations
    """
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._get_metric_key(name, labels or {})
            
            if key in self.metrics:
                self.metrics[key].value += value
                self.metrics[key].timestamp = datetime.now()
            else:
                self.metrics[key] = Metric(
                    name=name,
                    metric_type=MetricType.COUNTER,
                    value=value,
                    labels=labels or {}
                )
            
            # Add to history
            self.metric_history[key].append(self.metrics[key].value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        with self.lock:
            key = self._get_metric_key(name, labels or {})
            
            self.metrics[key] = Metric(
                name=name,
                metric_type=MetricType.GAUGE,
                value=value,
                labels=labels or {}
            )
            
            # Add to history
            self.metric_history[key].append(value)
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a value for histogram metric"""
        with self.lock:
            key = self._get_metric_key(name, labels or {})
            
            # For simplicity, we'll store the latest value
            # In a real implementation, you'd maintain buckets
            self.metrics[key] = Metric(
                name=name,
                metric_type=MetricType.HISTOGRAM,
                value=value,
                labels=labels or {}
            )
            
            # Add to history
            self.metric_history[key].append(value)
    
    def get_metric(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[Metric]:
        """Get a metric by name and labels"""
        with self.lock:
            key = self._get_metric_key(name, labels or {})
            return self.metrics.get(key)
    
    def get_all_metrics(self) -> List[Metric]:
        """Get all metrics"""
        with self.lock:
            return list(self.metrics.values())
    
    def get_metrics_by_name(self, name: str) -> List[Metric]:
        """Get all metrics with a specific name"""
        with self.lock:
            return [metric for metric in self.metrics.values() if metric.name == name]
    
    def get_metric_history(self, name: str, labels: Optional[Dict[str, str]] = None) -> List[float]:
        """Get metric history"""
        with self.lock:
            key = self._get_metric_key(name, labels or {})
            return list(self.metric_history.get(key, []))
    
    def _get_metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Generate a unique key for a metric"""
        if not labels:
            return name
        
        label_str = ",".join([f"{k}={v}" for k, v in sorted(labels.items())])
        return f"{name}{{{label_str}}}"
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        with self.lock:
            for metric in self.metrics.values():
                # Help text
                if metric.help_text:
                    lines.append(f"# HELP {metric.name} {metric.help_text}")
                
                # Type
                lines.append(f"# TYPE {metric.name} {metric.metric_type.value}")
                
                # Metric line
                if metric.labels:
                    label_str = ",".join([f'{k}="{v}"' for k, v in metric.labels.items()])
                    lines.append(f"{metric.name}{{{label_str}}} {metric.value}")
                else:
                    lines.append(f"{metric.name} {metric.value}")
        
        return "\n".join(lines)


class AlertManager:
    """
    Manages alerts and notifications
    """
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler"""
        self.alert_handlers.append(handler)
    
    def fire_alert(self, name: str, severity: AlertSeverity, message: str, 
                   source: str = "", labels: Optional[Dict[str, str]] = None) -> str:
        """Fire an alert"""
        alert_id = f"{name}_{int(time.time() * 1000)}"
        
        alert = Alert(
            alert_id=alert_id,
            name=name,
            severity=severity,
            message=message,
            source=source,
            labels=labels or {}
        )
        
        with self.lock:
            self.alerts[alert_id] = alert
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
        
        self.logger.warning(f"Alert fired: {name} - {message}")
        return alert_id
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        with self.lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolved = True
                self.alerts[alert_id].resolved_at = datetime.now()
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
        
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        with self.lock:
            return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts"""
        with self.lock:
            return list(self.alerts.values())
    
    def cleanup_old_alerts(self, older_than_hours: int = 24) -> int:
        """Clean up old resolved alerts"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        with self.lock:
            to_remove = []
            for alert_id, alert in self.alerts.items():
                if (alert.resolved and alert.resolved_at and 
                    alert.resolved_at < cutoff_time):
                    to_remove.append(alert_id)
            
            for alert_id in to_remove:
                del self.alerts[alert_id]
            
            self.logger.info(f"Cleaned up {len(to_remove)} old alerts")
            return len(to_remove)


class NATSMonitor:
    """
    Main NATS monitoring system
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.logger = logging.getLogger(__name__)
        
        # Monitoring configuration
        self.monitoring_interval = 30.0  # seconds
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Thresholds for alerts
        self.thresholds = {
            'connection_failures': 5,
            'message_publish_failures': 10,
            'high_latency_ms': 1000,
            'circuit_breaker_opens': 3,
            'queue_size_warning': 1000,
            'queue_size_critical': 5000
        }
        
        # Initialize default metrics
        self._initialize_metrics()
        
        # Add default alert handler
        self.alert_manager.add_alert_handler(self._default_alert_handler)
    
    def _initialize_metrics(self):
        """Initialize default metrics"""
        # Connection metrics
        self.metrics_collector.set_gauge('nats_connection_status', 0.0, {'status': 'disconnected'})
        self.metrics_collector.set_gauge('nats_connection_count', 0.0)
        
        # Message metrics
        self.metrics_collector.increment_counter('nats_messages_published_total', 0.0)
        self.metrics_collector.increment_counter('nats_messages_received_total', 0.0)
        self.metrics_collector.increment_counter('nats_messages_failed_total', 0.0)
        
        # Performance metrics
        self.metrics_collector.set_gauge('nats_message_latency_ms', 0.0)
        self.metrics_collector.set_gauge('nats_queue_size', 0.0)
        
        # Circuit breaker metrics
        self.metrics_collector.increment_counter('nats_circuit_breaker_opens_total', 0.0)
        self.metrics_collector.set_gauge('nats_circuit_breaker_state', 0.0)  # 0=closed, 1=open, 2=half-open
    
    async def start(self):
        """Start the monitoring system"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("NATS monitoring started")
    
    async def stop(self):
        """Stop the monitoring system"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("NATS monitoring stopped")
    
    def record_connection_event(self, connected: bool):
        """Record a connection event"""
        status = 'connected' if connected else 'disconnected'
        self.metrics_collector.set_gauge('nats_connection_status', 1.0 if connected else 0.0, {'status': status})
        
        if not connected:
            self.alert_manager.fire_alert(
                'nats_connection_lost',
                AlertSeverity.ERROR,
                'NATS connection lost',
                'nats_monitor'
            )
    
    def record_message_published(self, subject: str, success: bool, latency_ms: float = 0.0):
        """Record a message publish event"""
        if success:
            self.metrics_collector.increment_counter('nats_messages_published_total', 1.0, {'subject': subject})
            if latency_ms > 0:
                self.metrics_collector.observe_histogram('nats_message_latency_ms', latency_ms, {'subject': subject})
                
                # Check for high latency
                if latency_ms > self.thresholds['high_latency_ms']:
                    self.alert_manager.fire_alert(
                        'nats_high_latency',
                        AlertSeverity.WARNING,
                        f'High message latency: {latency_ms:.1f}ms for subject {subject}',
                        'nats_monitor',
                        {'subject': subject}
                    )
        else:
            self.metrics_collector.increment_counter('nats_messages_failed_total', 1.0, {'subject': subject})
            
            # Check failure threshold
            failed_metric = self.metrics_collector.get_metric('nats_messages_failed_total', {'subject': subject})
            if failed_metric and failed_metric.value >= self.thresholds['message_publish_failures']:
                self.alert_manager.fire_alert(
                    'nats_publish_failures',
                    AlertSeverity.ERROR,
                    f'High number of publish failures for subject {subject}: {failed_metric.value}',
                    'nats_monitor',
                    {'subject': subject}
                )
    
    def record_message_received(self, subject: str):
        """Record a message receive event"""
        self.metrics_collector.increment_counter('nats_messages_received_total', 1.0, {'subject': subject})
    
    def record_circuit_breaker_event(self, circuit_name: str, state: str):
        """Record a circuit breaker event"""
        state_value = {'closed': 0.0, 'open': 1.0, 'half_open': 2.0}.get(state, 0.0)
        self.metrics_collector.set_gauge('nats_circuit_breaker_state', state_value, {'circuit': circuit_name})
        
        if state == 'open':
            self.metrics_collector.increment_counter('nats_circuit_breaker_opens_total', 1.0, {'circuit': circuit_name})
            
            # Check threshold
            opens_metric = self.metrics_collector.get_metric('nats_circuit_breaker_opens_total', {'circuit': circuit_name})
            if opens_metric and opens_metric.value >= self.thresholds['circuit_breaker_opens']:
                self.alert_manager.fire_alert(
                    'nats_circuit_breaker_frequent_opens',
                    AlertSeverity.WARNING,
                    f'Circuit breaker {circuit_name} has opened {opens_metric.value} times',
                    'nats_monitor',
                    {'circuit': circuit_name}
                )
    
    def record_queue_size(self, queue_name: str, size: int):
        """Record queue size"""
        self.metrics_collector.set_gauge('nats_queue_size', float(size), {'queue': queue_name})
        
        # Check thresholds
        if size >= self.thresholds['queue_size_critical']:
            self.alert_manager.fire_alert(
                'nats_queue_size_critical',
                AlertSeverity.CRITICAL,
                f'Queue {queue_name} size is critical: {size}',
                'nats_monitor',
                {'queue': queue_name}
            )
        elif size >= self.thresholds['queue_size_warning']:
            self.alert_manager.fire_alert(
                'nats_queue_size_warning',
                AlertSeverity.WARNING,
                f'Queue {queue_name} size is high: {size}',
                'nats_monitor',
                {'queue': queue_name}
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        active_alerts = self.alert_manager.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        error_alerts = [a for a in active_alerts if a.severity == AlertSeverity.ERROR]
        
        if critical_alerts:
            status = 'critical'
        elif error_alerts:
            status = 'error'
        elif active_alerts:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'active_alerts': len(active_alerts),
            'critical_alerts': len(critical_alerts),
            'error_alerts': len(error_alerts),
            'total_metrics': len(self.metrics_collector.get_all_metrics()),
            'monitoring_active': self.is_running
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        all_metrics = self.metrics_collector.get_all_metrics()
        
        summary = {
            'total_metrics': len(all_metrics),
            'by_type': defaultdict(int),
            'key_metrics': {}
        }
        
        for metric in all_metrics:
            summary['by_type'][metric.metric_type.value] += 1
            
            # Include key metrics
            if metric.name in ['nats_connection_status', 'nats_messages_published_total', 
                              'nats_messages_failed_total', 'nats_circuit_breaker_opens_total']:
                summary['key_metrics'][metric.name] = metric.value
        
        return summary
    
    def export_metrics(self, format_type: str = 'prometheus') -> str:
        """Export metrics in specified format"""
        if format_type == 'prometheus':
            return self.metrics_collector.export_prometheus_format()
        elif format_type == 'json':
            metrics = [m.to_dict() for m in self.metrics_collector.get_all_metrics()]
            return json.dumps(metrics, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _default_alert_handler(self, alert: Alert):
        """Default alert handler - logs alerts"""
        level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        self.logger.log(level, f"ALERT [{alert.severity.value.upper()}] {alert.name}: {alert.message}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_running:
            try:
                # Perform periodic checks
                await self._perform_health_checks()
                
                # Clean up old alerts
                self.alert_manager.cleanup_old_alerts()
                
                # Wait for next iteration
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _perform_health_checks(self):
        """Perform periodic health checks"""
        # This would typically check NATS connection status,
        # JetStream health, etc. For now, it's a placeholder.
        pass


# Global monitoring instance
nats_monitor = NATSMonitor()