#!/usr/bin/env python3
"""
24/7 Security Operations Center (SOC) Framework
ISO 27001 compliant SOC implementation for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import threading
import queue


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class AlertStatus(Enum):
    """Alert status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class SOCRole(Enum):
    """SOC team roles"""
    SOC_MANAGER = "soc_manager"
    SOC_ANALYST_L1 = "soc_analyst_l1"
    SOC_ANALYST_L2 = "soc_analyst_l2"
    SOC_ANALYST_L3 = "soc_analyst_l3"
    INCIDENT_RESPONDER = "incident_responder"
    THREAT_HUNTER = "threat_hunter"
    FORENSICS_ANALYST = "forensics_analyst"


class MonitoringSource(Enum):
    """Monitoring data sources"""
    SIEM = "siem"
    IDS_IPS = "ids_ips"
    ENDPOINT_DETECTION = "endpoint_detection"
    NETWORK_MONITORING = "network_monitoring"
    VULNERABILITY_SCANNER = "vulnerability_scanner"
    THREAT_INTELLIGENCE = "threat_intelligence"
    LOG_ANALYSIS = "log_analysis"
    USER_BEHAVIOR = "user_behavior"


@dataclass
class SecurityAlert:
    """Security alert"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: MonitoringSource
    source_system: str
    detection_time: float
    affected_assets: List[str]
    indicators: List[str]
    raw_data: Dict[str, Any]
    assigned_analyst: Optional[str]
    escalated_to: Optional[str]
    investigation_notes: List[str]
    resolution_summary: str
    false_positive_reason: str
    created_time: float
    updated_time: float
    closed_time: Optional[float]


@dataclass
class SOCAnalyst:
    """SOC analyst"""
    analyst_id: str
    name: str
    role: SOCRole
    shift: str
    email: str
    phone: str
    skills: List[str]
    certifications: List[str]
    active_alerts: List[str]
    max_concurrent_alerts: int
    performance_metrics: Dict[str, float]
    last_login: float
    status: str  # online, offline, busy, away


@dataclass
class SOCShift:
    """SOC shift schedule"""
    shift_id: str
    shift_name: str
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    timezone: str
    assigned_analysts: List[str]
    backup_analysts: List[str]
    shift_lead: str
    coverage_areas: List[str]
    escalation_contacts: List[str]


class SecurityOperationsCenter:
    """
    24/7 Security Operations Center Framework
    Implements ISO 27001 compliant SOC for Syn_OS
    """
    
    def __init__(self):
        """Initialize SOC framework"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.soc_directory = "/var/lib/synos/soc"
        self.database_file = f"{self.soc_directory}/soc.db"
        
        # SOC components
        self.alerts: Dict[str, SecurityAlert] = {}
        self.analysts: Dict[str, SOCAnalyst] = {}
        self.shifts: Dict[str, SOCShift] = {}
        
        # Alert processing
        self.alert_queue = queue.PriorityQueue()
        self.processing_threads = []
        self.monitoring_active = False
        
        # SOC metrics
        self.metrics = {
            "total_alerts": 0,
            "alerts_by_severity": {},
            "mean_time_to_acknowledge": 0.0,
            "mean_time_to_resolve": 0.0,
            "false_positive_rate": 0.0,
            "analyst_utilization": 0.0
        }
        
        # SOC status
        self.soc_operational = False
        self.current_shift = None
        self.escalation_active = False
        
        # Initialize system
        asyncio.create_task(self._initialize_soc())
    
    async def _initialize_soc(self):
        """Initialize SOC framework"""
        try:
            self.logger.info("Initializing 24/7 Security Operations Center...")
            
            # Create SOC directory
            os.makedirs(self.soc_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Setup SOC team
            await self._setup_soc_team()
            
            # Configure shift schedules
            await self._configure_shifts()
            
            # Initialize monitoring systems
            await self._initialize_monitoring()
            
            # Start alert processing
            await self._start_alert_processing()
            
            self.soc_operational = True
            self.logger.info("24/7 Security Operations Center operational")
            
        except Exception as e:
            self.logger.error(f"Error initializing SOC: {e}")
    
    async def _initialize_database(self):
        """Initialize SOC database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Security alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    alert_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_system TEXT,
                    detection_time REAL NOT NULL,
                    affected_assets TEXT,
                    indicators TEXT,
                    raw_data TEXT,
                    assigned_analyst TEXT,
                    escalated_to TEXT,
                    investigation_notes TEXT,
                    resolution_summary TEXT,
                    false_positive_reason TEXT,
                    created_time REAL NOT NULL,
                    updated_time REAL NOT NULL,
                    closed_time REAL
                )
            ''')
            
            # SOC analysts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soc_analysts (
                    analyst_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    shift TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    skills TEXT,
                    certifications TEXT,
                    active_alerts TEXT,
                    max_concurrent_alerts INTEGER DEFAULT 5,
                    performance_metrics TEXT,
                    last_login REAL,
                    status TEXT DEFAULT 'offline'
                )
            ''')
            
            # SOC shifts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soc_shifts (
                    shift_id TEXT PRIMARY KEY,
                    shift_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    assigned_analysts TEXT,
                    backup_analysts TEXT,
                    shift_lead TEXT,
                    coverage_areas TEXT,
                    escalation_contacts TEXT
                )
            ''')
            
            # SOC metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soc_metrics (
                    metric_date TEXT PRIMARY KEY,
                    total_alerts INTEGER,
                    alerts_by_severity TEXT,
                    mean_time_to_acknowledge REAL,
                    mean_time_to_resolve REAL,
                    false_positive_rate REAL,
                    analyst_utilization REAL,
                    escalations INTEGER,
                    incidents_created INTEGER
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON security_alerts (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON security_alerts (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_detection_time ON security_alerts (detection_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysts_role ON soc_analysts (role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysts_shift ON soc_analysts (shift)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing SOC database: {e}")
            raise
    
    async def _setup_soc_team(self):
        """Setup SOC team structure"""
        try:
            current_time = time.time()
            
            # Define SOC team members
            analysts = [
                SOCAnalyst(
                    analyst_id="SOC-MGR-001",
                    name="SOC Manager",
                    role=SOCRole.SOC_MANAGER,
                    shift="day",
                    email="soc.manager@synos.org",
                    phone="+1-555-SOC-MGR",
                    skills=[
                        "Team leadership",
                        "Incident management",
                        "Strategic planning",
                        "Vendor management",
                        "Compliance oversight"
                    ],
                    certifications=[
                        "CISSP",
                        "CISM",
                        "GCIH",
                        "ITIL"
                    ],
                    active_alerts=[],
                    max_concurrent_alerts=10,
                    performance_metrics={
                        "alerts_handled": 0,
                        "escalations_managed": 0,
                        "team_satisfaction": 0.0,
                        "sla_compliance": 0.0
                    },
                    last_login=current_time,
                    status="online"
                ),
                SOCAnalyst(
                    analyst_id="SOC-L1-001",
                    name="L1 Analyst - Day Shift",
                    role=SOCRole.SOC_ANALYST_L1,
                    shift="day",
                    email="l1.day@synos.org",
                    phone="+1-555-L1-DAY",
                    skills=[
                        "Alert triage",
                        "Basic investigation",
                        "Documentation",
                        "Tool operation",
                        "Communication"
                    ],
                    certifications=[
                        "Security+",
                        "CySA+",
                        "GCFA"
                    ],
                    active_alerts=[],
                    max_concurrent_alerts=8,
                    performance_metrics={
                        "alerts_triaged": 0,
                        "false_positives_identified": 0,
                        "escalation_accuracy": 0.0,
                        "response_time": 0.0
                    },
                    last_login=current_time,
                    status="online"
                ),
                SOCAnalyst(
                    analyst_id="SOC-L1-002",
                    name="L1 Analyst - Night Shift",
                    role=SOCRole.SOC_ANALYST_L1,
                    shift="night",
                    email="l1.night@synos.org",
                    phone="+1-555-L1-NIGHT",
                    skills=[
                        "Alert triage",
                        "Basic investigation",
                        "Documentation",
                        "Tool operation",
                        "Communication"
                    ],
                    certifications=[
                        "Security+",
                        "CySA+",
                        "GCIH"
                    ],
                    active_alerts=[],
                    max_concurrent_alerts=8,
                    performance_metrics={
                        "alerts_triaged": 0,
                        "false_positives_identified": 0,
                        "escalation_accuracy": 0.0,
                        "response_time": 0.0
                    },
                    last_login=current_time,
                    status="online"
                ),
                SOCAnalyst(
                    analyst_id="SOC-L2-001",
                    name="L2 Analyst - Senior",
                    role=SOCRole.SOC_ANALYST_L2,
                    shift="day",
                    email="l2.senior@synos.org",
                    phone="+1-555-L2-SR",
                    skills=[
                        "Advanced investigation",
                        "Malware analysis",
                        "Network forensics",
                        "Threat hunting",
                        "Mentoring"
                    ],
                    certifications=[
                        "GCIH",
                        "GCFA",
                        "GNFA",
                        "CISSP"
                    ],
                    active_alerts=[],
                    max_concurrent_alerts=6,
                    performance_metrics={
                        "complex_investigations": 0,
                        "threat_discoveries": 0,
                        "mentoring_hours": 0.0,
                        "investigation_quality": 0.0
                    },
                    last_login=current_time,
                    status="online"
                ),
                SOCAnalyst(
                    analyst_id="SOC-L3-001",
                    name="L3 Analyst - Expert",
                    role=SOCRole.SOC_ANALYST_L3,
                    shift="on-call",
                    email="l3.expert@synos.org",
                    phone="+1-555-L3-EXP",
                    skills=[
                        "Expert investigation",
                        "Advanced malware analysis",
                        "Digital forensics",
                        "Threat intelligence",
                        "Custom tool development"
                    ],
                    certifications=[
                        "CISSP",
                        "GCFA",
                        "GNFA",
                        "GREM",
                        "GCTI"
                    ],
                    active_alerts=[],
                    max_concurrent_alerts=4,
                    performance_metrics={
                        "expert_investigations": 0,
                        "custom_tools_developed": 0,
                        "threat_intel_contributions": 0,
                        "research_publications": 0
                    },
                    last_login=current_time,
                    status="on-call"
                ),
                SOCAnalyst(
                    analyst_id="SOC-IR-001",
                    name="Incident Responder",
                    role=SOCRole.INCIDENT_RESPONDER,
                    shift="on-call",
                    email="incident.responder@synos.org",
                    phone="+1-555-IR-001",
                    skills=[
                        "Incident response",
                        "Crisis management",
                        "Forensics",
                        "Recovery planning",
                        "Stakeholder communication"
                    ],
                    certifications=[
                        "GCIH",
                        "GCFA",
                        "CISSP",
                        "CISM"
                    ],
                    active_alerts=[],
                    max_concurrent_alerts=3,
                    performance_metrics={
                        "incidents_handled": 0,
                        "recovery_time": 0.0,
                        "stakeholder_satisfaction": 0.0,
                        "lessons_learned": 0
                    },
                    last_login=current_time,
                    status="on-call"
                )
            ]
            
            # Store analysts
            for analyst in analysts:
                await self._store_analyst(analyst)
                self.analysts[analyst.analyst_id] = analyst
            
            self.logger.info(f"Setup SOC team with {len(analysts)} analysts")
            
        except Exception as e:
            self.logger.error(f"Error setting up SOC team: {e}")
    
    async def _store_analyst(self, analyst: SOCAnalyst):
        """Store SOC analyst in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO soc_analysts
                (analyst_id, name, role, shift, email, phone, skills, certifications,
                 active_alerts, max_concurrent_alerts, performance_metrics, last_login, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analyst.analyst_id, analyst.name, analyst.role.value, analyst.shift,
                analyst.email, analyst.phone, json.dumps(analyst.skills),
                json.dumps(analyst.certifications), json.dumps(analyst.active_alerts),
                analyst.max_concurrent_alerts, json.dumps(analyst.performance_metrics),
                analyst.last_login, analyst.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing analyst: {e}")
    
    async def _configure_shifts(self):
        """Configure SOC shift schedules"""
        try:
            shifts = [
                SOCShift(
                    shift_id="SHIFT-DAY",
                    shift_name="Day Shift",
                    start_time="08:00",
                    end_time="20:00",
                    timezone="America/New_York",
                    assigned_analysts=["SOC-MGR-001", "SOC-L1-001", "SOC-L2-001"],
                    backup_analysts=["SOC-L1-002", "SOC-L3-001"],
                    shift_lead="SOC-MGR-001",
                    coverage_areas=[
                        "Alert monitoring",
                        "Incident response",
                        "Threat hunting",
                        "Vulnerability management",
                        "Compliance reporting"
                    ],
                    escalation_contacts=[
                        "SOC-L2-001",
                        "SOC-L3-001",
                        "SOC-IR-001"
                    ]
                ),
                SOCShift(
                    shift_id="SHIFT-NIGHT",
                    shift_name="Night Shift",
                    start_time="20:00",
                    end_time="08:00",
                    timezone="America/New_York",
                    assigned_analysts=["SOC-L1-002"],
                    backup_analysts=["SOC-L2-001", "SOC-L3-001"],
                    shift_lead="SOC-L1-002",
                    coverage_areas=[
                        "Alert monitoring",
                        "Basic incident response",
                        "Escalation management"
                    ],
                    escalation_contacts=[
                        "SOC-L2-001",
                        "SOC-L3-001",
                        "SOC-MGR-001",
                        "SOC-IR-001"
                    ]
                ),
                SOCShift(
                    shift_id="SHIFT-WEEKEND",
                    shift_name="Weekend Shift",
                    start_time="00:00",
                    end_time="23:59",
                    timezone="America/New_York",
                    assigned_analysts=["SOC-L1-001", "SOC-L1-002"],
                    backup_analysts=["SOC-L2-001", "SOC-L3-001"],
                    shift_lead="SOC-L1-001",
                    coverage_areas=[
                        "Alert monitoring",
                        "Basic incident response",
                        "Escalation management"
                    ],
                    escalation_contacts=[
                        "SOC-L2-001",
                        "SOC-L3-001",
                        "SOC-MGR-001",
                        "SOC-IR-001"
                    ]
                )
            ]
            
            # Store shifts
            for shift in shifts:
                await self._store_shift(shift)
                self.shifts[shift.shift_id] = shift
            
            self.logger.info(f"Configured {len(shifts)} SOC shifts")
            
        except Exception as e:
            self.logger.error(f"Error configuring shifts: {e}")
    
    async def _store_shift(self, shift: SOCShift):
        """Store SOC shift in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO soc_shifts
                (shift_id, shift_name, start_time, end_time, timezone,
                 assigned_analysts, backup_analysts, shift_lead, coverage_areas, escalation_contacts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                shift.shift_id, shift.shift_name, shift.start_time, shift.end_time,
                shift.timezone, json.dumps(shift.assigned_analysts),
                json.dumps(shift.backup_analysts), shift.shift_lead,
                json.dumps(shift.coverage_areas), json.dumps(shift.escalation_contacts)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing shift: {e}")
    
    async def _initialize_monitoring(self):
        """Initialize monitoring systems integration"""
        try:
            # Configure monitoring sources
            monitoring_config = {
                "siem_integration": {
                    "enabled": True,
                    "endpoint": "https://siem.synos.org/api/alerts",
                    "poll_interval": 30,
                    "authentication": "api_key"
                },
                "ids_ips_integration": {
                    "enabled": True,
                    "endpoint": "https://ids.synos.org/api/alerts",
                    "poll_interval": 15,
                    "authentication": "certificate"
                },
                "endpoint_detection": {
                    "enabled": True,
                    "endpoint": "https://edr.synos.org/api/alerts",
                    "poll_interval": 10,
                    "authentication": "oauth2"
                },
                "vulnerability_scanner": {
                    "enabled": True,
                    "endpoint": "https://vuln.synos.org/api/alerts",
                    "poll_interval": 300,
                    "authentication": "api_key"
                },
                "threat_intelligence": {
                    "enabled": True,
                    "feeds": [
                        "https://ti.synos.org/api/indicators",
                        "https://external-ti.com/api/feed"
                    ],
                    "poll_interval": 600,
                    "authentication": "api_key"
                }
            }
            
            # Save monitoring configuration
            config_file = f"{self.soc_directory}/monitoring_config.json"
            with open(config_file, 'w') as f:
                json.dump(monitoring_config, f, indent=2)
            
            self.logger.info("Monitoring systems integration configured")
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring: {e}")
    
    async def _start_alert_processing(self):
        """Start alert processing threads"""
        try:
            # Start alert processing threads
            for i in range(3):  # 3 processing threads
                thread = threading.Thread(
                    target=self._process_alerts,
                    name=f"AlertProcessor-{i+1}",
                    daemon=True
                )
                thread.start()
                self.processing_threads.append(thread)
            
            self.monitoring_active = True
            self.logger.info("Alert processing threads started")
            
        except Exception as e:
            self.logger.error(f"Error starting alert processing: {e}")
    
    def _process_alerts(self):
        """Process alerts from queue"""
        while self.monitoring_active:
            try:
                # Get alert from queue (blocks until available)
                priority, alert_data = self.alert_queue.get(timeout=1)
                
                # Create security alert
                alert = self._create_alert_from_data(alert_data)
                
                # Auto-assign to available analyst
                assigned_analyst = self._assign_alert_to_analyst(alert)
                
                if assigned_analyst:
                    alert.assigned_analyst = assigned_analyst
                    self.logger.info(f"Alert {alert.alert_id} assigned to {assigned_analyst}")
                else:
                    self.logger.warning(f"No available analyst for alert {alert.alert_id}")
                
                # Store alert
                asyncio.run(self._store_alert(alert))
                self.alerts[alert.alert_id] = alert
                
                # Update metrics
                self._update_soc_metrics(alert)
                
                self.alert_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing alert: {e}")
    
    def _create_alert_from_data(self, alert_data: Dict[str, Any]) -> SecurityAlert:
        """Create SecurityAlert from raw data"""
        current_time = time.time()
        alert_id = f"ALERT-{int(current_time)}-{hash(str(alert_data)) % 10000:04d}"
        
        return SecurityAlert(
            alert_id=alert_id,
            title=alert_data.get("title", "Security Alert"),
            description=alert_data.get("description", ""),
            severity=AlertSeverity(alert_data.get("severity", "medium")),
            status=AlertStatus.NEW,
            source=MonitoringSource(alert_data.get("source", "siem")),
            source_system=alert_data.get("source_system", "unknown"),
            detection_time=alert_data.get("detection_time", current_time),
            affected_assets=alert_data.get("affected_assets", []),
            indicators=alert_data.get("indicators", []),
            raw_data=alert_data,
            assigned_analyst=None,
            escalated_to=None,
            investigation_notes=[],
            resolution_summary="",
            false_positive_reason="",
            created_time=current_time,
            updated_time=current_time,
            closed_time=None
        )
    
    def _assign_alert_to_analyst(self, alert: SecurityAlert) -> Optional[str]:
        """Assign alert to available analyst"""
        try:
            # Get current shift analysts
            current_shift_analysts = self._get_current_shift_analysts()
            
            # Find available analyst with capacity
            for analyst_id in current_shift_analysts:
                analyst = self.analysts.get(analyst_id)
                if analyst and len(analyst.active_alerts) < analyst.max_concurrent_alerts:
                    analyst.active_alerts.append(alert.alert_id)
                    return analyst_id
            
            # If no capacity, escalate to higher tier
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                for analyst in self.analysts.values():
                    if analyst.role in [SOCRole.SOC_ANALYST_L2, SOCRole.SOC_ANALYST_L3]:
                        if len(analyst.active_alerts) < analyst.max_concurrent_alerts:
                            analyst.active_alerts.append(alert.alert_id)
                            return analyst.analyst_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error assigning alert: {e}")
            return None
    
    def _get_current_shift_analysts(self) -> List[str]:
        """Get analysts for current shift"""
        try:
            current_hour = datetime.now().hour
            
            # Determine current shift
            if 8 <= current_hour < 20:
                shift = self.shifts.get("SHIFT-DAY")
            else:
                shift = self.shifts.get("SHIFT-NIGHT")
            
            if shift:
                return shift.assigned_analysts
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting current shift analysts: {e}")
            return []
    
    async def _store_alert(self, alert: SecurityAlert):
        """Store security alert in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_alerts
                (alert_id, title, description, severity, status, source, source_system,
                 detection_time, affected_assets, indicators, raw_data, assigned_analyst,
                 escalated_to, investigation_notes, resolution_summary, false_positive_reason,
                 created_time, updated_time, closed_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id, alert.title, alert.description, alert.severity.value,
                alert.status.value, alert.source.value, alert.source_system,
                alert.detection_time, json.dumps(alert.affected_assets),
                json.dumps(alert.indicators), json.dumps(alert.raw_data),
                alert.assigned_analyst, alert.escalated_to,
                json.dumps(alert.investigation_notes), alert.resolution_summary,
                alert.false_positive_reason, alert.created_time, alert.updated_time,
                alert.closed_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")
    
    def _update_soc_metrics(self, alert: SecurityAlert):
        """Update SOC metrics"""
        try:
            self.metrics["total_alerts"] += 1
            
            # Update severity distribution
            severity = alert.severity.value
            if severity not in self.metrics["alerts_by_severity"]:
                self.metrics["alerts_by_severity"][severity] = 0
            self.metrics["alerts_by_severity"][severity] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating SOC metrics: {e}")
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> str:
        """Create new security alert"""
        try:
            # Calculate priority based on severity
            severity = AlertSeverity(alert_data.get("severity", "medium"))
            priority = {
                AlertSeverity.CRITICAL: 1,
                AlertSeverity.HIGH: 2,
                AlertSeverity.MEDIUM: 3,
                AlertSeverity.LOW: 4,
                AlertSeverity.INFORMATIONAL: 5
            }.get(severity, 3)
            
            # Add to processing queue
            self.alert_queue.put((priority, alert_data))
            
            # Generate alert ID for tracking
            alert_id = f"ALERT-{int(time.time())}-{hash(str(alert_data)) % 10000:04d}"
            
            self.logger.info(f"Alert {alert_id} queued for processing")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return ""
    
    async def get_soc_status(self) -> Dict[str, Any]:
        """Get SOC operational status"""
        try:
            return {
                "soc_operational": self.soc_operational,
                "monitoring_active": self.monitoring_active,
                "total_analysts": len(self.analysts),
                "active_analysts": len([a for a in self.analysts.values() if a.status == "online"]),
                "total_alerts": len(self.alerts),
                "open_alerts": len([a for a in self.alerts.values() if a.status != AlertStatus.CLOSED]),
                "processing_threads": len(self.processing_threads),
                "queue_size": self.alert_queue.qsize(),
                "current_shift": self.current_shift,
                "escalation_active": self.escalation_active,
                "metrics": self.metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SOC status: {e}")
            return {"error": str(e)}
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        try:
            alerts = []
            for alert in self.alerts.values():
                if alert.status != AlertStatus.CLOSED:
                    alert_dict = asdict(alert)
                    alert_dict["severity"] = alert.severity.value
                    alert_dict["status"] = alert.status.value
                    alert_dict["source"] = alert.source.value
                    alerts.append(alert_dict)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_soc_analysts(self) -> List[Dict[str, Any]]:
        """Get all SOC analysts"""
        try:
            analysts = []
            for analyst in self.analysts.values():
                analyst_dict = asdict(analyst)
                analyst_dict["role"] = analyst.role.value
                analysts.append(analyst_dict)
            
            return analysts
            
        except Exception as e:
            self.logger.error(f"Error getting SOC analysts: {e}")
            return []
    
    async def escalate_alert(self, alert_id: str, escalation_reason: str) -> bool:
        """Escalate alert to higher tier"""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            
            # Find appropriate escalation target
            escalation_target = None
            if alert.assigned_analyst:
                current_analyst = self.analysts.get(alert.assigned_analyst)
                if current_analyst:
                    if current_analyst.role == SOCRole.SOC_ANALYST_L1:
                        # Escalate to L2
                        for analyst in self.analysts.values():
                            if analyst.role == SOCRole.SOC_ANALYST_L2 and analyst.status == "online":
                                escalation_target = analyst.analyst_id
                                break
                    elif current_analyst.role == SOCRole.SOC_ANALYST_L2:
                        # Escalate to L3
                        for analyst in self.analysts.values():
                            if analyst.role == SOCRole.SOC_ANALYST_L3:
                                escalation_target = analyst.analyst_id
                                break
            
            if escalation_target:
                alert.escalated_to = escalation_target
                alert.investigation_notes.append(f"Escalated to {escalation_target}: {escalation_reason}")
                alert.updated_time = time.time()
                
                # Update database
                await self._store_alert(alert)
                
                self.logger.info(f"Alert {alert_id} escalated to {escalation_target}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error escalating alert: {e}")
            return False
    
    async def shutdown_soc(self):
        """Shutdown SOC operations"""
        try:
            self.logger.info("Shutting down SOC operations...")
            
            # Stop monitoring
            self.monitoring_active = False
            
            # Wait for processing threads to finish
            for thread in self.processing_threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            self.soc_operational = False
            self.logger.info("SOC operations shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error shutting down SOC: {e}")


# Global SOC instance
security_operations_center = SecurityOperationsCenter()