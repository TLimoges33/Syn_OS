#!/usr/bin/env python3
"""
Advanced Monitoring and Alerting System for Syn_OS
Comprehensive monitoring, metrics collection, and intelligent alerting
"""

import asyncio
import json
import logging
import time
import psutil
import aiohttp
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import sqlite3
import threading
from pathlib import Path
import yaml
import hashlib
import subprocess
import socket
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Metric types for monitoring"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class MonitoringSource(Enum):
    """Sources of monitoring data"""
    SYSTEM = "system"
    APPLICATION = "application"
    CONSCIOUSNESS = "consciousness"
    EDUCATION = "education"
    SECURITY = "security"
    NETWORK = "network"
    CUSTOM = "custom"

@dataclass
class MetricData:
    """Metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    source: MonitoringSource
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    source: MonitoringSource
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[float] = None
    notification_sent: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ThresholdRule:
    """Threshold-based alerting rule"""
    name: str
    metric_name: str
    condition: str  # >, <, >=, <=, ==, !=
    threshold_value: Union[int, float]
    severity: AlertSeverity
    duration_seconds: int = 0  # How long condition must persist
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

class MetricsCollector:
    """Advanced metrics collection system"""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.retention_hours = retention_hours
        self.lock = threading.Lock()
        self.collection_interval = 30  # seconds
        self.running = False
        self.collection_task = None
        
    async def start_collection(self):
        """Start metric collection"""
        self.running = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Metrics collection started")
    
    async def stop_collection(self):
        """Stop metric collection"""
        self.running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collection stopped")
    
    async def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                await self._collect_system_metrics()
                await self._collect_application_metrics()
                await self._cleanup_old_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.add_metric(MetricData(
                name="system_cpu_usage_percent",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                source=MonitoringSource.SYSTEM,
                description="System CPU usage percentage"
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            await self.add_metric(MetricData(
                name="system_memory_usage_percent",
                value=memory.percent,
                metric_type=MetricType.GAUGE,
                source=MonitoringSource.SYSTEM,
                description="System memory usage percentage"
            ))
            
            await self.add_metric(MetricData(
                name="system_memory_available_gb",
                value=memory.available / (1024**3),
                metric_type=MetricType.GAUGE,
                source=MonitoringSource.SYSTEM,
                description="Available memory in GB"
            ))
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            await self.add_metric(MetricData(
                name="system_disk_usage_percent",
                value=(disk.used / disk.total) * 100,
                metric_type=MetricType.GAUGE,
                source=MonitoringSource.SYSTEM,
                description="Disk usage percentage"
            ))
            
            # Network metrics
            network = psutil.net_io_counters()
            await self.add_metric(MetricData(
                name="system_network_bytes_sent",
                value=network.bytes_sent,
                metric_type=MetricType.COUNTER,
                source=MonitoringSource.NETWORK,
                description="Total bytes sent"
            ))
            
            await self.add_metric(MetricData(
                name="system_network_bytes_recv",
                value=network.bytes_recv,
                metric_type=MetricType.COUNTER,
                source=MonitoringSource.NETWORK,
                description="Total bytes received"
            ))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Check service health
            services_to_check = [
                ("consciousness-unified", "http://localhost:8080/health"),
                ("educational-unified", "http://localhost:8081/health"),
                ("orchestrator", "http://localhost:8082/health")
            ]
            
            for service_name, health_url in services_to_check:
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        async with session.get(health_url) as response:
                            is_healthy = response.status == 200
                            
                            await self.add_metric(MetricData(
                                name="service_health_status",
                                value=1 if is_healthy else 0,
                                metric_type=MetricType.GAUGE,
                                source=MonitoringSource.APPLICATION,
                                labels={"service": service_name},
                                description="Service health status (1=healthy, 0=unhealthy)"
                            ))
                            
                            # Response time
                            if is_healthy:
                                response_time = time.time() - response.request_info.real_url.query.get('start', time.time())
                                await self.add_metric(MetricData(
                                    name="service_response_time_ms",
                                    value=response_time * 1000,
                                    metric_type=MetricType.GAUGE,
                                    source=MonitoringSource.APPLICATION,
                                    labels={"service": service_name},
                                    description="Service response time in milliseconds"
                                ))
                                
                except Exception as e:
                    # Service is down
                    await self.add_metric(MetricData(
                        name="service_health_status",
                        value=0,
                        metric_type=MetricType.GAUGE,
                        source=MonitoringSource.APPLICATION,
                        labels={"service": service_name},
                        description="Service health status (1=healthy, 0=unhealthy)"
                    ))
                    
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    async def add_metric(self, metric: MetricData):
        """Add a metric data point"""
        with self.lock:
            metric_key = f"{metric.source.value}_{metric.name}"
            if metric.labels:
                label_str = "_".join([f"{k}_{v}" for k, v in sorted(metric.labels.items())])
                metric_key += f"_{label_str}"
            
            self.metrics[metric_key].append(metric)
    
    async def _cleanup_old_metrics(self):
        """Clean up old metric data"""
        cutoff_time = time.time() - (self.retention_hours * 3600)
        
        with self.lock:
            for metric_key, metric_deque in self.metrics.items():
                # Remove old entries
                while metric_deque and metric_deque[0].timestamp < cutoff_time:
                    metric_deque.popleft()
    
    def get_latest_metrics(self, source: Optional[MonitoringSource] = None, 
                         metric_name: Optional[str] = None) -> List[MetricData]:
        """Get latest metrics"""
        with self.lock:
            results = []
            for metric_key, metric_deque in self.metrics.items():
                if metric_deque:
                    latest_metric = metric_deque[-1]
                    
                    # Filter by source if specified
                    if source and latest_metric.source != source:
                        continue
                    
                    # Filter by metric name if specified
                    if metric_name and latest_metric.name != metric_name:
                        continue
                    
                    results.append(latest_metric)
            
            return results
    
    def get_metric_history(self, metric_name: str, hours: int = 1) -> List[MetricData]:
        """Get metric history for specified time range"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            results = []
            for metric_key, metric_deque in self.metrics.items():
                for metric in metric_deque:
                    if (metric.name == metric_name and 
                        metric.timestamp >= cutoff_time):
                        results.append(metric)
            
            return sorted(results, key=lambda m: m.timestamp)

class AlertEngine:
    """Advanced alerting engine with multiple notification channels"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.alerts: Dict[str, Alert] = {}
        self.threshold_rules: List[ThresholdRule] = []
        self.notification_channels: Dict[str, Callable] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.config = self._load_config(config_path)
        
        # Initialize notification channels
        self._init_notification_channels()
        
        # Load threshold rules
        self._load_threshold_rules()
        
        # Alert suppression (prevent spam)
        self.suppression_windows: Dict[str, float] = {}
        self.default_suppression_minutes = 15
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_address': 'monitoring@synos.local',
                'to_addresses': []
            },
            'webhook': {
                'enabled': False,
                'url': '',
                'headers': {}
            },
            'slack': {
                'enabled': False,
                'webhook_url': ''
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
        
        return default_config
    
    def _init_notification_channels(self):
        """Initialize notification channels"""
        self.notification_channels['email'] = self._send_email_notification
        self.notification_channels['webhook'] = self._send_webhook_notification
        self.notification_channels['slack'] = self._send_slack_notification
        self.notification_channels['log'] = self._send_log_notification
    
    def _load_threshold_rules(self):
        """Load threshold-based alerting rules"""
        # Default system monitoring rules
        default_rules = [
            ThresholdRule(
                name="high_cpu_usage",
                metric_name="system_cpu_usage_percent",
                condition=">",
                threshold_value=85.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=60
            ),
            ThresholdRule(
                name="critical_cpu_usage",
                metric_name="system_cpu_usage_percent",
                condition=">",
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL,
                duration_seconds=30
            ),
            ThresholdRule(
                name="high_memory_usage",
                metric_name="system_memory_usage_percent",
                condition=">",
                threshold_value=80.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=60
            ),
            ThresholdRule(
                name="critical_memory_usage",
                metric_name="system_memory_usage_percent",
                condition=">",
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL,
                duration_seconds=30
            ),
            ThresholdRule(
                name="low_disk_space",
                metric_name="system_disk_usage_percent",
                condition=">",
                threshold_value=85.0,
                severity=AlertSeverity.WARNING
            ),
            ThresholdRule(
                name="critical_disk_space",
                metric_name="system_disk_usage_percent",
                condition=">",
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL
            ),
            ThresholdRule(
                name="service_down",
                metric_name="service_health_status",
                condition="==",
                threshold_value=0,
                severity=AlertSeverity.CRITICAL,
                duration_seconds=30
            )
        ]
        
        self.threshold_rules.extend(default_rules)
    
    async def evaluate_metrics(self, metrics: List[MetricData]):
        """Evaluate metrics against threshold rules"""
        for metric in metrics:
            for rule in self.threshold_rules:
                if not rule.enabled:
                    continue
                
                if rule.metric_name == metric.name:
                    if self._evaluate_condition(metric.value, rule.condition, rule.threshold_value):
                        await self._trigger_alert(rule, metric)
    
    def _evaluate_condition(self, value: Union[int, float], condition: str, threshold: Union[int, float]) -> bool:
        """Evaluate threshold condition"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            logger.error(f"Unknown condition: {condition}")
            return False
    
    async def _trigger_alert(self, rule: ThresholdRule, metric: MetricData):
        """Trigger an alert based on rule and metric"""
        alert_key = f"{rule.name}_{metric.source.value}"
        if metric.labels:
            label_str = "_".join([f"{k}_{v}" for k, v in sorted(metric.labels.items())])
            alert_key += f"_{label_str}"
        
        # Check suppression
        if self._is_suppressed(alert_key):
            return
        
        # Check if alert already exists and is active
        if alert_key in self.alerts and not self.alerts[alert_key].resolved:
            return
        
        alert_id = hashlib.md5(f"{alert_key}_{time.time()}".encode()).hexdigest()[:8]
        
        alert = Alert(
            alert_id=alert_id,
            name=rule.name,
            severity=rule.severity,
            message=f"{rule.name}: {metric.name} = {metric.value} (threshold: {rule.threshold_value})",
            source=metric.source,
            labels={**rule.labels, **metric.labels}
        )
        
        self.alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        # Set suppression window
        self._set_suppression(alert_key, self.default_suppression_minutes * 60)
        
        logger.warning(f"Alert triggered: {alert.name} - {alert.message}")
    
    def _is_suppressed(self, alert_key: str) -> bool:
        """Check if alert is suppressed"""
        if alert_key in self.suppression_windows:
            return time.time() < self.suppression_windows[alert_key]
        return False
    
    def _set_suppression(self, alert_key: str, duration_seconds: int):
        """Set suppression window for alert"""
        self.suppression_windows[alert_key] = time.time() + duration_seconds
    
    async def _send_notifications(self, alert: Alert):
        """Send notifications through all enabled channels"""
        for channel_name, channel_func in self.notification_channels.items():
            try:
                await channel_func(alert)
            except Exception as e:
                logger.error(f"Error sending notification via {channel_name}: {e}")
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        if not self.config['email']['enabled']:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.config['email']['from_address']
            msg['To'] = ', '.join(self.config['email']['to_addresses'])
            msg['Subject'] = f"[{alert.severity.value.upper()}] Syn_OS Alert: {alert.name}"
            
            body = f"""
Alert Details:
- Name: {alert.name}
- Severity: {alert.severity.value}
- Source: {alert.source.value}
- Message: {alert.message}
- Time: {datetime.fromtimestamp(alert.timestamp).isoformat()}
- Labels: {alert.labels}

Syn_OS Monitoring System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
            alert.notification_sent = True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""
        if not self.config['webhook']['enabled']:
            return
        
        try:
            payload = {
                'alert': alert.to_dict(),
                'timestamp': datetime.fromtimestamp(alert.timestamp).isoformat()
            }
            
            headers = {'Content-Type': 'application/json', **self.config['webhook']['headers']}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config['webhook']['url'], 
                                      json=payload, 
                                      headers=headers) as response:
                    if response.status == 200:
                        alert.notification_sent = True
                        
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""
        if not self.config['slack']['enabled']:
            return
        
        try:
            severity_colors = {
                AlertSeverity.DEBUG: "#36a64f",
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9500",
                AlertSeverity.ERROR: "#ff0000",
                AlertSeverity.CRITICAL: "#8b0000"
            }
            
            payload = {
                "attachments": [{
                    "color": severity_colors.get(alert.severity, "#36a64f"),
                    "title": f"Syn_OS Alert: {alert.name}",
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Source", "value": alert.source.value, "short": True},
                        {"title": "Message", "value": alert.message, "short": False}
                    ],
                    "timestamp": alert.timestamp
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config['slack']['webhook_url'], json=payload) as response:
                    if response.status == 200:
                        alert.notification_sent = True
                        
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def _send_log_notification(self, alert: Alert):
        """Send log notification (always enabled)"""
        log_level = {
            AlertSeverity.DEBUG: logging.DEBUG,
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        logger.log(log_level, f"ALERT [{alert.severity.value.upper()}] {alert.name}: {alert.message}")
        alert.notification_sent = True
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        active_alerts = self.get_active_alerts()
        
        severity_counts = defaultdict(int)
        for alert in active_alerts:
            severity_counts[alert.severity.value] += 1
        
        return {
            'total_active': len(active_alerts),
            'by_severity': dict(severity_counts),
            'total_all_time': len(self.alert_history),
            'suppressed_alerts': len([k for k, v in self.suppression_windows.items() if time.time() < v])
        }

class AdvancedMonitoringSystem:
    """Main monitoring system orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.metrics_collector = MetricsCollector()
        self.alert_engine = AlertEngine(config_path)
        self.running = False
        self.monitoring_task = None
        
        # Database for persistence
        self.db_path = Path("/var/lib/synos/monitoring.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize monitoring database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    labels TEXT,
                    description TEXT
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    labels TEXT,
                    resolved BOOLEAN NOT NULL DEFAULT 0,
                    resolved_at REAL,
                    notification_sent BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts (timestamp)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing monitoring database: {e}")
    
    async def start(self):
        """Start the monitoring system"""
        if self.running:
            return
        
        logger.info("Starting advanced monitoring system...")
        self.running = True
        
        # Start metrics collection
        await self.metrics_collector.start_collection()
        
        # Start monitoring loop
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Advanced monitoring system started successfully")
    
    async def stop(self):
        """Stop the monitoring system"""
        logger.info("Stopping monitoring system...")
        self.running = False
        
        # Stop metrics collection
        await self.metrics_collector.stop_collection()
        
        # Stop monitoring loop
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring evaluation loop"""
        while self.running:
            try:
                # Get latest metrics
                latest_metrics = self.metrics_collector.get_latest_metrics()
                
                # Evaluate against alert rules
                await self.alert_engine.evaluate_metrics(latest_metrics)
                
                # Persist metrics and alerts
                await self._persist_data(latest_metrics)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _persist_data(self, metrics: List[MetricData]):
        """Persist metrics and alerts to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Persist metrics
            for metric in metrics[-100:]:  # Only persist latest 100 metrics per cycle
                cursor.execute('''
                    INSERT INTO metrics (name, value, metric_type, source, timestamp, labels, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric.name,
                    metric.value,
                    metric.metric_type.value,
                    metric.source.value,
                    metric.timestamp,
                    json.dumps(metric.labels),
                    metric.description
                ))
            
            # Persist new alerts
            for alert in self.alert_engine.alerts.values():
                cursor.execute('''
                    INSERT OR REPLACE INTO alerts 
                    (alert_id, name, severity, message, source, timestamp, labels, resolved, resolved_at, notification_sent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id,
                    alert.name,
                    alert.severity.value,
                    alert.message,
                    alert.source.value,
                    alert.timestamp,
                    json.dumps(alert.labels),
                    alert.resolved,
                    alert.resolved_at,
                    alert.notification_sent
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting monitoring data: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        latest_metrics = self.metrics_collector.get_latest_metrics()
        alert_summary = self.alert_engine.get_alert_summary()
        
        # Extract key system metrics
        key_metrics = {}
        for metric in latest_metrics:
            if metric.name in ['system_cpu_usage_percent', 'system_memory_usage_percent', 'system_disk_usage_percent']:
                key_metrics[metric.name] = metric.value
        
        return {
            'monitoring_active': self.running,
            'key_metrics': key_metrics,
            'alert_summary': alert_summary,
            'total_metrics_collected': sum(len(deque_obj) for deque_obj in self.metrics_collector.metrics.values()),
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring system"""
        return {
            'status': 'healthy' if self.running else 'stopped',
            'metrics_collector_running': self.metrics_collector.running,
            'database_accessible': self.db_path.exists(),
            'timestamp': datetime.now().isoformat()
        }

# Global monitoring system instance
monitoring_system = AdvancedMonitoringSystem()