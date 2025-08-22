#!/usr/bin/env python3
"""
Consciousness System Monitor and Debugger
=========================================

Comprehensive monitoring and debugging tools for the SynapticOS consciousness system.
Provides real-time monitoring, performance analysis, debugging capabilities, and
system health visualization.
"""

import asyncio
import logging
import json
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
from pathlib import Path
import sqlite3
from collections import defaultdict, deque

from ..core.consciousness_bus import ConsciousnessBus
from ..core.state_manager import StateManager
from ..core.event_types import EventType, ConsciousnessEvent
from ..core.data_models import ComponentStatus, ComponentState
from ..interfaces.consciousness_component import ConsciousnessComponent

logger = logging.getLogger('synapticos.consciousness_monitor')


class MonitoringLevel(Enum):
    """Monitoring detail levels"""
    BASIC = "basic"
    DETAILED = "detailed"
    VERBOSE = "verbose"
    DEBUG = "debug"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: datetime
    component_id: str
    
    # Response time metrics
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    
    # Throughput metrics
    requests_per_second: float
    events_processed: int
    
    # Resource usage
    cpu_usage_percent: float
    memory_usage_mb: float
    
    # Error metrics
    error_rate: float
    error_count: int
    
    # Health metrics
    health_score: float
    uptime_seconds: float


@dataclass
class SystemAlert:
    """System alert/notification"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    component_id: str
    title: str
    description: str
    metrics: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class DebugSession:
    """Debug session information"""
    session_id: str
    start_time: datetime
    component_filter: Optional[str]
    event_filter: Optional[List[EventType]]
    monitoring_level: MonitoringLevel
    captured_events: List[ConsciousnessEvent] = field(default_factory=list)
    captured_metrics: List[PerformanceMetrics] = field(default_factory=list)
    active: bool = True


class ConsciousnessMonitor(ConsciousnessComponent):
    """Comprehensive consciousness system monitor and debugger"""
    
    def __init__(self, db_path: str = "consciousness_monitor.db"):
        super().__init__("consciousness_monitor", "monitoring")
        
        self.db_path = db_path
        self.monitoring_level = MonitoringLevel.DETAILED
        
        # Monitoring state
        self.component_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.system_alerts: List[SystemAlert] = []
        self.debug_sessions: Dict[str, DebugSession] = {}
        
        # Performance tracking
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Database connection
        self.db_connection: Optional[sqlite3.Connection] = None
        
        # Alert thresholds
        self.alert_thresholds = {
            'response_time_ms': 1000,
            'error_rate': 0.05,
            'memory_usage_mb': 1024,
            'cpu_usage_percent': 80,
            'health_score': 0.7
        }
    
    async def initialize(self, consciousness_bus: ConsciousnessBus, state_manager: StateManager) -> bool:
        """Initialize the consciousness monitor"""
        await super().initialize(consciousness_bus, state_manager)
        
        try:
            # Initialize database
            await self._initialize_database()
            
            # Register for all events to monitor system activity
            if self.consciousness_bus:
                for event_type in EventType:
                    await self.consciousness_bus.subscribe(
                        event_type, self._handle_monitoring_event, self.component_id
                    )
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            logger.info("Consciousness monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize consciousness monitor: {e}")
            raise
    
    async def _initialize_database(self):
        """Initialize SQLite database for metrics storage"""
        self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Create tables
        cursor = self.db_connection.cursor()
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                component_id TEXT NOT NULL,
                avg_response_time_ms REAL,
                p95_response_time_ms REAL,
                p99_response_time_ms REAL,
                requests_per_second REAL,
                events_processed INTEGER,
                cpu_usage_percent REAL,
                memory_usage_mb REAL,
                error_rate REAL,
                error_count INTEGER,
                health_score REAL,
                uptime_seconds REAL
            )
        ''')
        
        # System alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                component_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                metrics TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TEXT
            )
        ''')
        
        # Event log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source_component TEXT NOT NULL,
                target_components TEXT,
                priority INTEGER,
                processing_duration_ms REAL,
                success BOOLEAN
            )
        ''')
        
        self.db_connection.commit()
        logger.info("Database initialized successfully")
    
    async def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        self.monitoring_active = True
        
        # Component health monitoring
        health_task = asyncio.create_task(self._component_health_monitoring())
        self.monitoring_tasks.append(health_task)
        
        # Performance metrics collection
        metrics_task = asyncio.create_task(self._performance_metrics_collection())
        self.monitoring_tasks.append(metrics_task)
        
        # Alert processing
        alert_task = asyncio.create_task(self._alert_processing())
        self.monitoring_tasks.append(alert_task)
        
        # Database cleanup
        cleanup_task = asyncio.create_task(self._database_cleanup())
        self.monitoring_tasks.append(cleanup_task)
        
        logger.info("Monitoring tasks started")
    
    async def _component_health_monitoring(self):
        """Monitor component health continuously"""
        while self.monitoring_active:
            try:
                if self.consciousness_bus:
                    # Get all registered components
                    components = await self.consciousness_bus.get_registered_components()
                    
                    for component_status in components:
                        await self._check_component_health(component_status)
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in component health monitoring: {e}")
                await asyncio.sleep(10.0)
    
    async def _performance_metrics_collection(self):
        """Collect performance metrics continuously"""
        while self.monitoring_active:
            try:
                if self.consciousness_bus:
                    components = await self.consciousness_bus.get_registered_components()
                    
                    for component_status in components:
                        metrics = await self._collect_component_metrics(component_status)
                        if metrics:
                            await self._store_metrics(metrics)
                
                await asyncio.sleep(10.0)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in performance metrics collection: {e}")
                await asyncio.sleep(30.0)
    
    async def _alert_processing(self):
        """Process and manage system alerts"""
        while self.monitoring_active:
            try:
                # Check for alert conditions
                await self._check_alert_conditions()
                
                # Clean up resolved alerts
                await self._cleanup_resolved_alerts()
                
                await asyncio.sleep(30.0)  # Process alerts every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert processing: {e}")
                await asyncio.sleep(60.0)
    
    async def _database_cleanup(self):
        """Clean up old database records"""
        while self.monitoring_active:
            try:
                if self.db_connection:
                    # Clean up old metrics (keep last 7 days)
                    cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
                    
                    cursor = self.db_connection.cursor()
                    cursor.execute(
                        "DELETE FROM performance_metrics WHERE timestamp < ?",
                        (cutoff_date,)
                    )
                    cursor.execute(
                        "DELETE FROM event_log WHERE timestamp < ?",
                        (cutoff_date,)
                    )
                    
                    # Clean up resolved alerts (keep last 30 days)
                    alert_cutoff = (datetime.now() - timedelta(days=30)).isoformat()
                    cursor.execute(
                        "DELETE FROM system_alerts WHERE resolved = TRUE AND resolved_at < ?",
                        (alert_cutoff,)
                    )
                    
                    self.db_connection.commit()
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in database cleanup: {e}")
                await asyncio.sleep(7200)  # Retry in 2 hours
    
    async def _handle_monitoring_event(self, event: ConsciousnessEvent):
        """Handle events for monitoring purposes"""
        try:
            # Record event processing time
            start_time = time.time()
            
            # Update event counts
            self.event_counts[event.source_component] += 1
            self.event_counts['total'] += 1
            
            # Store event in database if detailed monitoring
            if self.monitoring_level in [MonitoringLevel.DETAILED, MonitoringLevel.VERBOSE, MonitoringLevel.DEBUG]:
                await self._store_event_log(event)
            
            # Add to active debug sessions
            for session in self.debug_sessions.values():
                if session.active and self._event_matches_filter(event, session):
                    session.captured_events.append(event)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            self.response_times[event.source_component].append(processing_time)
            
        except Exception as e:
            logger.error(f"Error handling monitoring event: {e}")
            self.error_counts[event.source_component] += 1
    
    async def _check_component_health(self, component_status: ComponentStatus):
        """Check individual component health and generate alerts"""
        try:
            component_id = component_status.component_id
            
            # Check health score
            if component_status.health_score < self.alert_thresholds['health_score']:
                await self._create_alert(
                    AlertSeverity.WARNING,
                    component_id,
                    "Low Health Score",
                    f"Component health score is {component_status.health_score:.2f}",
                    {"health_score": component_status.health_score}
                )
            
            # Check component state
            if component_status.state == ComponentState.FAILED:
                await self._create_alert(
                    AlertSeverity.CRITICAL,
                    component_id,
                    "Component Failed",
                    f"Component is in FAILED state",
                    {"state": component_status.state.name}
                )
            elif component_status.state == ComponentState.DEGRADED:
                await self._create_alert(
                    AlertSeverity.WARNING,
                    component_id,
                    "Component Degraded",
                    f"Component is in DEGRADED state",
                    {"state": component_status.state.name}
                )
            
        except Exception as e:
            logger.error(f"Error checking component health for {component_status.component_id}: {e}")
    
    async def _collect_component_metrics(self, component_status: ComponentStatus) -> Optional[PerformanceMetrics]:
        """Collect detailed metrics for a component"""
        try:
            component_id = component_status.component_id
            
            # Calculate response time percentiles
            response_times = list(self.response_times[component_id])
            if response_times:
                response_times.sort()
                avg_response = sum(response_times) / len(response_times)
                p95_response = response_times[int(len(response_times) * 0.95)] if response_times else 0
                p99_response = response_times[int(len(response_times) * 0.99)] if response_times else 0
            else:
                avg_response = p95_response = p99_response = 0
            
            # Calculate requests per second
            event_count = self.event_counts.get(component_id, 0)
            rps = event_count / 60.0  # Events per minute / 60
            
            # Get system resource usage
            try:
                process = psutil.Process()
                cpu_usage = process.cpu_percent()
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            except:
                cpu_usage = 0
                memory_usage = 0
            
            # Calculate error rate
            error_count = self.error_counts.get(component_id, 0)
            total_events = max(event_count, 1)
            error_rate = error_count / total_events
            
            # Calculate uptime
            uptime = (datetime.now() - component_status.last_heartbeat).total_seconds()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                component_id=component_id,
                avg_response_time_ms=avg_response,
                p95_response_time_ms=p95_response,
                p99_response_time_ms=p99_response,
                requests_per_second=rps,
                events_processed=event_count,
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_usage,
                error_rate=error_rate,
                error_count=error_count,
                health_score=component_status.health_score,
                uptime_seconds=uptime
            )
            
            # Store in memory for quick access
            self.component_metrics[component_id].append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {component_status.component_id}: {e}")
            return None
    
    async def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in database"""
        try:
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO performance_metrics (
                        timestamp, component_id, avg_response_time_ms, p95_response_time_ms,
                        p99_response_time_ms, requests_per_second, events_processed,
                        cpu_usage_percent, memory_usage_mb, error_rate, error_count,
                        health_score, uptime_seconds
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp.isoformat(),
                    metrics.component_id,
                    metrics.avg_response_time_ms,
                    metrics.p95_response_time_ms,
                    metrics.p99_response_time_ms,
                    metrics.requests_per_second,
                    metrics.events_processed,
                    metrics.cpu_usage_percent,
                    metrics.memory_usage_mb,
                    metrics.error_rate,
                    metrics.error_count,
                    metrics.health_score,
                    metrics.uptime_seconds
                ))
                self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def _store_event_log(self, event: ConsciousnessEvent):
        """Store event in database log"""
        try:
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO event_log (
                        timestamp, event_id, event_type, source_component,
                        target_components, priority, processing_duration_ms, success
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.timestamp.isoformat(),
                    event.event_id,
                    event.event_type.value,
                    event.source_component,
                    json.dumps(event.target_components),
                    event.priority.value,
                    event.processing_duration_ms,
                    event.processed_at is not None
                ))
                self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error storing event log: {e}")
    
    async def _create_alert(self, severity: AlertSeverity, component_id: str, 
                          title: str, description: str, metrics: Dict[str, Any]):
        """Create a system alert"""
        try:
            alert_id = f"{component_id}_{title.replace(' ', '_').lower()}_{int(time.time())}"
            
            # Check if similar alert already exists
            existing_alert = None
            for alert in self.system_alerts:
                if (alert.component_id == component_id and 
                    alert.title == title and 
                    not alert.resolved):
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert
                existing_alert.timestamp = datetime.now()
                existing_alert.metrics.update(metrics)
            else:
                # Create new alert
                alert = SystemAlert(
                    alert_id=alert_id,
                    timestamp=datetime.now(),
                    severity=severity,
                    component_id=component_id,
                    title=title,
                    description=description,
                    metrics=metrics
                )
                
                self.system_alerts.append(alert)
                
                # Store in database
                if self.db_connection:
                    cursor = self.db_connection.cursor()
                    cursor.execute('''
                        INSERT INTO system_alerts (
                            alert_id, timestamp, severity, component_id,
                            title, description, metrics
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        alert.alert_id,
                        alert.timestamp.isoformat(),
                        alert.severity.value,
                        alert.component_id,
                        alert.title,
                        alert.description,
                        json.dumps(alert.metrics)
                    ))
                    self.db_connection.commit()
                
                logger.warning(f"Alert created: {title} for {component_id}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    async def _check_alert_conditions(self):
        """Check for alert conditions across the system"""
        try:
            # Check overall system health
            if self.consciousness_bus:
                components = await self.consciousness_bus.get_registered_components()
                
                total_components = len(components)
                failed_components = sum(1 for c in components if c.state == ComponentState.FAILED)
                degraded_components = sum(1 for c in components if c.state == ComponentState.DEGRADED)
                
                if failed_components > 0:
                    await self._create_alert(
                        AlertSeverity.CRITICAL,
                        "system",
                        "System Components Failed",
                        f"{failed_components} out of {total_components} components have failed",
                        {"failed_components": failed_components, "total_components": total_components}
                    )
                
                if degraded_components > total_components * 0.3:  # More than 30% degraded
                    await self._create_alert(
                        AlertSeverity.WARNING,
                        "system",
                        "System Performance Degraded",
                        f"{degraded_components} out of {total_components} components are degraded",
                        {"degraded_components": degraded_components, "total_components": total_components}
                    )
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
    
    async def _cleanup_resolved_alerts(self):
        """Clean up resolved alerts"""
        try:
            # Auto-resolve alerts that are no longer relevant
            current_time = datetime.now()
            
            for alert in self.system_alerts:
                if not alert.resolved:
                    # Check if alert condition still exists
                    if await self._is_alert_condition_resolved(alert):
                        alert.resolved = True
                        alert.resolved_at = current_time
                        
                        # Update database
                        if self.db_connection:
                            cursor = self.db_connection.cursor()
                            cursor.execute('''
                                UPDATE system_alerts 
                                SET resolved = TRUE, resolved_at = ?
                                WHERE alert_id = ?
                            ''', (current_time.isoformat(), alert.alert_id))
                            self.db_connection.commit()
                        
                        logger.info(f"Alert resolved: {alert.title} for {alert.component_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up resolved alerts: {e}")
    
    async def _is_alert_condition_resolved(self, alert: SystemAlert) -> bool:
        """Check if an alert condition has been resolved"""
        try:
            if self.consciousness_bus:
                components = await self.consciousness_bus.get_registered_components()
                
                for component in components:
                    if component.component_id == alert.component_id:
                        # Check specific alert conditions
                        if "Low Health Score" in alert.title:
                            return component.health_score >= self.alert_thresholds['health_score']
                        elif "Component Failed" in alert.title:
                            return component.state != ComponentState.FAILED
                        elif "Component Degraded" in alert.title:
                            return component.state not in [ComponentState.FAILED, ComponentState.DEGRADED]
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if alert condition resolved: {e}")
            return False
    
    def _event_matches_filter(self, event: ConsciousnessEvent, session: DebugSession) -> bool:
        """Check if event matches debug session filters"""
        if session.component_filter and event.source_component != session.component_filter:
            return False
        
        if session.event_filter and event.event_type not in session.event_filter:
            return False
        
        return True
    
    # Public API methods
    
    async def start_debug_session(self, session_id: str, component_filter: Optional[str] = None,
                                event_filter: Optional[List[EventType]] = None,
                                monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED) -> bool:
        """Start a debug session"""
        try:
            session = DebugSession(
                session_id=session_id,
                start_time=datetime.now(),
                component_filter=component_filter,
                event_filter=event_filter,
                monitoring_level=monitoring_level
            )
            
            self.debug_sessions[session_id] = session
            logger.info(f"Debug session started: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting debug session: {e}")
            return False
    
    async def stop_debug_session(self, session_id: str) -> Optional[DebugSession]:
        """Stop a debug session and return captured data"""
        try:
            if session_id in self.debug_sessions:
                session = self.debug_sessions[session_id]
                session.active = False
                
                logger.info(f"Debug session stopped: {session_id}")
                return session
            
            return None
            
        except Exception as e:
            logger.error(f"Error stopping debug session: {e}")
            return None
    
    async def get_component_metrics(self, component_id: str, 
                                  hours: int = 1) -> List[PerformanceMetrics]:
        """Get performance metrics for a component"""
        try:
            # Get from memory first (recent data)
            recent_metrics = list(self.component_metrics.get(component_id, []))
            
            # Get from database for historical data
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            db_metrics = []
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    SELECT * FROM performance_metrics 
                    WHERE component_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (component_id, cutoff_time))
                
                for row in cursor.fetchall():
                    metrics = PerformanceMetrics(
                        timestamp=datetime.fromisoformat(row[1]),
                        component_id=row[2],
                        avg_response_time_ms=row[3],
                        p95_response_time_ms=row[4],
                        p99_response_time_ms=row[5],
                        requests_per_second=row[6],
                        events_processed=row[7],
                        cpu_usage_percent=row[8],
                        memory_usage_mb=row[9],
                        error_rate=row[10],
                        error_count=row[11],
                        health_score=row[12],
                        uptime_seconds=row[13]
                    )
                    db_metrics.append(metrics)
            
            # Combine and deduplicate
            all_metrics = recent_metrics + db_metrics
            unique_metrics = {}
            for metric in all_metrics:
                key = f"{metric.component_id}_{metric.timestamp.isoformat()}"
                unique_metrics[key] = metric
            
            return sorted(unique_metrics.values(), key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting component metrics: {e}")
            return []
    
    async def get_system_alerts(self, severity: Optional[AlertSeverity] = None,
                              resolved: Optional[bool] = None) -> List[SystemAlert]:
        """Get system alerts with optional filtering"""
        try:
            filtered_alerts = []
            
            for alert in self.system_alerts:
                if severity and alert.severity != severity:
                    continue
                if resolved is not None and alert.resolved != resolved:
                    continue
                
                filtered_alerts.append(alert)
            
            return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting system alerts: {e}")
            return []
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        try:
            overview = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_level": self.monitoring_level.value,
                "components": {},
                "alerts": {
                    "total": len(self.system_alerts),
                    "unresolved": len([a for a in self.system_alerts if not a.resolved]),
                    "critical": len([a for a in self.system_alerts if a.severity == AlertSeverity.CRITICAL and not a.resolved]),
                    "warnings": len([a for a in self.system_alerts if a.severity == AlertSeverity.WARNING and not a.resolved])
                },
                "events": {
                    "total_processed": self.event_counts.get('total', 0),
                    "by_component": dict(self.event_counts)
                },
                "errors": {
                    "total": sum(self.error_counts.values()),
                    "by_component": dict(self.error_counts)
                }
            }
            
            # Get component status
            if self.consciousness_bus:
                components = await self.consciousness_bus.get_registered_components()
                
                for component in components:
                    recent_metrics = list(self.component_metrics.get(component.component_id, []))
                    latest_metric = recent_metrics[-1] if recent_metrics else None
                    
                    overview["components"][component.component_id] = {
                        "state": component.state.name,
                        "health_score": component.health_score,
                        "last_heartbeat": component.last_heartbeat.isoformat(),
                        "response_time_ms": component.response_time_ms,
                        "error_rate": component.error_rate,
                        "latest_metrics": asdict(latest_metric) if latest_metric else None
                    }
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting system overview: {e}")
            return {"error": str(e)}
    
    async def set_monitoring_level(self, level: MonitoringLevel):
        """Set monitoring detail level"""
        self.monitoring_level = level
        logger.info(f"Monitoring level set to: {level.value}")
    
    async def update_alert_thresholds(self, thresholds: Dict[str, float]):
        """Update alert thresholds"""
        self.alert_thresholds.update(thresholds)
        logger.info(f"Alert thresholds updated: {thresholds}")
    
    # ConsciousnessComponent interface implementation
    
    async def start(self) -> bool:
        """Start the consciousness monitor"""
        try:
            self.monitoring_active = True
            logger.info("Consciousness monitor started")
            return True
        except Exception as e:
            logger.error(f"Error starting consciousness monitor: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the consciousness monitor"""
        try:
            self.monitoring_active = False
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Close database connection
            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None
            
            logger.info("Consciousness monitor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping consciousness monitor: {e}")
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process consciousness events for monitoring"""
        try:
            await self._handle_monitoring_event(event)
            return True
        except Exception as e:
            logger.error(f"Error processing event in monitor: {e}")
            return False
    
    async def get_health_status(self) -> ComponentStatus:
        """Get monitor health status"""
        try:
            return ComponentStatus(
                component_id=self.component_id,
                component_type=self.component_type,
                state=ComponentState.HEALTHY if self.monitoring_active else ComponentState.FAILED,
                health_score=1.0 if self.monitoring_active else 0.0,
                last_heartbeat=datetime.now(),
                response_time_ms=0.0,
                error_rate=0.0,
                throughput=len(self.system_alerts),
                cpu_usage=0.0,
                memory_usage_mb=0.0,
                dependencies=["sqlite3"],
                dependency_health={"sqlite3": self.db_connection is not None},
                version="1.0.0"
            )
        except Exception as e:
            logger.error(f"Error getting monitor health status: {e}")
            return ComponentStatus(
                component_id=self.component_id,
                component_type=self.component_type,
                state=ComponentState.FAILED,
                health_score=0.0,
                last_heartbeat=datetime.now()
            )
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update monitor configuration"""
        try:
            if "monitoring_level" in config:
                level_str = config["monitoring_level"]
                if hasattr(MonitoringLevel, level_str.upper()):
                    self.monitoring_level = MonitoringLevel(level_str.lower())
            
            if "alert_thresholds" in config:
                await self.update_alert_thresholds(config["alert_thresholds"])
            
            logger.info("Monitor configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating monitor configuration: {e}")
            return False