#!/usr/bin/env python3
"""
Incident Response Automation System for Syn_OS
Automated incident detection, classification, and response with consciousness-driven decision making
"""

import asyncio
import logging
import time
import json
import hashlib
import re
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from datetime import datetime, timedelta
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.consciousness_v2.consciousness_bus import ConsciousnessBus


class IncidentSeverity(Enum):
    """Incident severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status levels"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCategory(Enum):
    """Incident categories"""
    MALWARE = "malware"
    INTRUSION = "intrusion"
    DATA_BREACH = "data_breach"
    DENIAL_OF_SERVICE = "denial_of_service"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"
    SYSTEM_COMPROMISE = "system_compromise"
    NETWORK_ANOMALY = "network_anomaly"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    POLICY_VIOLATION = "policy_violation"


class ResponseActionType(Enum):
    """Automated response actions"""
    ISOLATE_HOST = "isolate_host"
    BLOCK_IP = "block_ip"
    DISABLE_USER = "disable_user"
    QUARANTINE_FILE = "quarantine_file"
    RESET_PASSWORD = "reset_password"
    COLLECT_EVIDENCE = "collect_evidence"
    NOTIFY_TEAM = "notify_team"
    ESCALATE = "escalate"
    CREATE_TICKET = "create_ticket"
    RUN_SCAN = "run_scan"


@dataclass
class Incident:
    """Security incident record"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    status: IncidentStatus
    source_system: str
    affected_assets: List[str]
    indicators: List[Dict[str, Any]]
    created_at: float
    updated_at: float
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    response_actions: Optional[List[Dict[str, Any]]] = None
    consciousness_level: float = 0.0
    automated: bool = True
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
        if self.response_actions is None:
            self.response_actions = []


@dataclass
class ResponsePlaybook:
    """Incident response playbook"""
    playbook_id: str
    name: str
    description: str
    category: IncidentCategory
    severity_threshold: IncidentSeverity
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    approval_required: bool
    consciousness_threshold: float
    created_at: float
    updated_at: float
    active: bool = True


@dataclass
class ResponseAction:
    """Individual response action"""
    action_id: str
    incident_id: str
    action_type: ResponseActionType
    parameters: Dict[str, Any]
    status: str  # pending, running, completed, failed
    result: Optional[Dict[str, Any]]
    executed_at: Optional[float]
    completed_at: Optional[float]
    error_message: Optional[str] = None


class IncidentResponseAutomation:
    """
    Automated incident response system with consciousness-driven decision making
    Detects, classifies, and responds to security incidents automatically
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize incident response automation"""
        self.consciousness_bus = consciousness_bus
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/incident_response"
        self.database_file = f"{self.system_directory}/incident_response.db"
        
        # Data stores
        self.incidents: Dict[str, Incident] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.active_responses: Dict[str, ResponseAction] = {}
        
        # Configuration
        self.consciousness_threshold = 0.7
        self.auto_response_enabled = True
        self.max_concurrent_responses = 10
        self.escalation_timeout = 3600  # 1 hour
        
        # Event sources
        self.event_sources = []
        
        # Notification settings
        self.notification_settings = {
            "email_enabled": True,
            "smtp_server": "localhost",
            "smtp_port": 587,
            "from_address": "synos-ir@localhost",
            "alert_recipients": ["security-team@localhost"]
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        """Initialize the incident response system"""
        try:
            self.logger.info("Initializing incident response automation...")
            
            # Create system directory
            import os
            os.makedirs(self.system_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_system_data()
            
            # Initialize default playbooks
            await self._initialize_default_playbooks()
            
            # Start event monitoring
            asyncio.create_task(self._start_event_monitoring())
            
            # Start response processor
            asyncio.create_task(self._process_responses())
            
            # Start incident aging
            asyncio.create_task(self._age_incidents())
            
            self.logger.info("Incident response automation initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing incident response system: {e}")
    
    async def _initialize_database(self):
        """Initialize incident response database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    affected_assets TEXT,
                    indicators TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    assigned_to TEXT,
                    resolution TEXT,
                    evidence TEXT,
                    response_actions TEXT,
                    consciousness_level REAL NOT NULL DEFAULT 0.0,
                    automated BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            # Playbooks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS playbooks (
                    playbook_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    severity_threshold TEXT NOT NULL,
                    conditions TEXT,
                    actions TEXT,
                    approval_required BOOLEAN NOT NULL DEFAULT 0,
                    consciousness_threshold REAL NOT NULL DEFAULT 0.7,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            # Response actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_actions (
                    action_id TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    parameters TEXT,
                    status TEXT NOT NULL,
                    result TEXT,
                    executed_at REAL,
                    completed_at REAL,
                    error_message TEXT,
                    FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_category ON incidents (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_playbooks_category ON playbooks (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_incident ON response_actions (incident_id)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    async def _load_system_data(self):
        """Load existing system data from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load incidents
            cursor.execute('SELECT * FROM incidents WHERE status NOT IN (?, ?)', 
                         (IncidentStatus.RESOLVED.value, IncidentStatus.CLOSED.value))
            for row in cursor.fetchall():
                incident = Incident(
                    incident_id=row[0],
                    title=row[1],
                    description=row[2],
                    severity=IncidentSeverity(row[3]),
                    category=IncidentCategory(row[4]),
                    status=IncidentStatus(row[5]),
                    source_system=row[6],
                    affected_assets=json.loads(row[7]) if row[7] else [],
                    indicators=json.loads(row[8]) if row[8] else [],
                    created_at=row[9],
                    updated_at=row[10],
                    assigned_to=row[11],
                    resolution=row[12],
                    evidence=json.loads(row[13]) if row[13] else [],
                    response_actions=json.loads(row[14]) if row[14] else [],
                    consciousness_level=row[15],
                    automated=bool(row[16])
                )
                self.incidents[incident.incident_id] = incident
            
            # Load playbooks
            cursor.execute('SELECT * FROM playbooks WHERE active = 1')
            for row in cursor.fetchall():
                playbook = ResponsePlaybook(
                    playbook_id=row[0],
                    name=row[1],
                    description=row[2],
                    category=IncidentCategory(row[3]),
                    severity_threshold=IncidentSeverity(row[4]),
                    conditions=json.loads(row[5]) if row[5] else [],
                    actions=json.loads(row[6]) if row[6] else [],
                    approval_required=bool(row[7]),
                    consciousness_threshold=row[8],
                    created_at=row[9],
                    updated_at=row[10],
                    active=bool(row[11])
                )
                self.playbooks[playbook.playbook_id] = playbook
            
            # Load active response actions
            cursor.execute('SELECT * FROM response_actions WHERE status IN (?, ?)', 
                         ('pending', 'running'))
            for row in cursor.fetchall():
                action = ResponseAction(
                    action_id=row[0],
                    incident_id=row[1],
                    action_type=ResponseActionType(row[2]),
                    parameters=json.loads(row[3]) if row[3] else {},
                    status=row[4],
                    result=json.loads(row[5]) if row[5] else None,
                    executed_at=row[6],
                    completed_at=row[7],
                    error_message=row[8]
                )
                self.active_responses[action.action_id] = action
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.incidents)} active incidents, "
                           f"{len(self.playbooks)} playbooks, {len(self.active_responses)} active responses")
            
        except Exception as e:
            self.logger.error(f"Error loading system data: {e}")
    
    async def _initialize_default_playbooks(self):
        """Initialize default incident response playbooks"""
        try:
            current_time = time.time()
            
            default_playbooks = [
                {
                    "name": "Malware Detection Response",
                    "description": "Automated response to malware detection",
                    "category": IncidentCategory.MALWARE,
                    "severity_threshold": IncidentSeverity.MEDIUM,
                    "conditions": [
                        {"type": "indicator_match", "value": "malware_signature"},
                        {"type": "file_hash", "operation": "in_blacklist"}
                    ],
                    "actions": [
                        {"type": ResponseActionType.QUARANTINE_FILE.value, "priority": 1},
                        {"type": ResponseActionType.ISOLATE_HOST.value, "priority": 2},
                        {"type": ResponseActionType.COLLECT_EVIDENCE.value, "priority": 3},
                        {"type": ResponseActionType.NOTIFY_TEAM.value, "priority": 4}
                    ],
                    "approval_required": False,
                    "consciousness_threshold": 0.6
                },
                {
                    "name": "Network Intrusion Response",
                    "description": "Response to detected network intrusions",
                    "category": IncidentCategory.INTRUSION,
                    "severity_threshold": IncidentSeverity.HIGH,
                    "conditions": [
                        {"type": "network_anomaly", "threshold": 0.8},
                        {"type": "suspicious_traffic", "volume": "high"}
                    ],
                    "actions": [
                        {"type": ResponseActionType.BLOCK_IP.value, "priority": 1},
                        {"type": ResponseActionType.COLLECT_EVIDENCE.value, "priority": 2},
                        {"type": ResponseActionType.RUN_SCAN.value, "priority": 3},
                        {"type": ResponseActionType.ESCALATE.value, "priority": 4}
                    ],
                    "approval_required": True,
                    "consciousness_threshold": 0.8
                },
                {
                    "name": "Data Breach Response",
                    "description": "Critical response to data breach incidents",
                    "category": IncidentCategory.DATA_BREACH,
                    "severity_threshold": IncidentSeverity.CRITICAL,
                    "conditions": [
                        {"type": "data_exfiltration", "confirmed": True},
                        {"type": "unauthorized_access", "sensitive_data": True}
                    ],
                    "actions": [
                        {"type": ResponseActionType.ISOLATE_HOST.value, "priority": 1},
                        {"type": ResponseActionType.DISABLE_USER.value, "priority": 1},
                        {"type": ResponseActionType.COLLECT_EVIDENCE.value, "priority": 2},
                        {"type": ResponseActionType.NOTIFY_TEAM.value, "priority": 2},
                        {"type": ResponseActionType.ESCALATE.value, "priority": 3},
                        {"type": ResponseActionType.CREATE_TICKET.value, "priority": 4}
                    ],
                    "approval_required": True,
                    "consciousness_threshold": 0.9
                },
                {
                    "name": "Phishing Attack Response",
                    "description": "Response to phishing attacks",
                    "category": IncidentCategory.PHISHING,
                    "severity_threshold": IncidentSeverity.MEDIUM,
                    "conditions": [
                        {"type": "phishing_email", "detected": True},
                        {"type": "user_interaction", "suspicious": True}
                    ],
                    "actions": [
                        {"type": ResponseActionType.RESET_PASSWORD.value, "priority": 1},
                        {"type": ResponseActionType.BLOCK_IP.value, "priority": 2},
                        {"type": ResponseActionType.NOTIFY_TEAM.value, "priority": 3},
                        {"type": ResponseActionType.RUN_SCAN.value, "priority": 4}
                    ],
                    "approval_required": False,
                    "consciousness_threshold": 0.5
                }
            ]
            
            for playbook_data in default_playbooks:
                # Check if playbook already exists
                existing = any(p.name == playbook_data["name"] for p in self.playbooks.values())
                if existing:
                    continue
                
                playbook_id = str(uuid.uuid4())
                playbook = ResponsePlaybook(
                    playbook_id=playbook_id,
                    name=playbook_data["name"],
                    description=playbook_data["description"],
                    category=playbook_data["category"],
                    severity_threshold=playbook_data["severity_threshold"],
                    conditions=playbook_data["conditions"],
                    actions=playbook_data["actions"],
                    approval_required=playbook_data["approval_required"],
                    consciousness_threshold=playbook_data["consciousness_threshold"],
                    created_at=current_time,
                    updated_at=current_time
                )
                
                await self._store_playbook(playbook)
                self.playbooks[playbook_id] = playbook
            
            self.logger.info(f"Initialized {len(default_playbooks)} default playbooks")
            
        except Exception as e:
            self.logger.error(f"Error initializing default playbooks: {e}")
    
    async def _start_event_monitoring(self):
        """Start monitoring for security events"""
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check consciousness level
                consciousness_state = await self.consciousness_bus.get_consciousness_state()
                consciousness_level = consciousness_state.get('overall_consciousness_level', 0)
                
                if consciousness_level < self.consciousness_threshold:
                    continue
                
                # Monitor various event sources
                await self._check_system_logs()
                await self._check_network_events()
                await self._check_security_alerts()
                
        except Exception as e:
            self.logger.error(f"Error in event monitoring: {e}")
    
    async def _check_system_logs(self):
        """Check system logs for security events"""
        try:
            # Simulate log analysis
            # In a real implementation, this would parse actual system logs
            
            # Example: Detect failed login attempts
            failed_logins = await self._simulate_failed_login_detection()
            if failed_logins > 10:
                await self._create_incident({
                    "title": "Multiple Failed Login Attempts",
                    "description": f"Detected {failed_logins} failed login attempts",
                    "severity": IncidentSeverity.MEDIUM,
                    "category": IncidentCategory.INTRUSION,
                    "source_system": "auth_logs",
                    "indicators": [
                        {"type": "failed_logins", "count": failed_logins, "timeframe": "5min"}
                    ]
                })
            
        except Exception as e:
            self.logger.error(f"Error checking system logs: {e}")
    
    async def _simulate_failed_login_detection(self) -> int:
        """Simulate failed login detection"""
        import random
        return random.randint(0, 20)
    
    async def _check_network_events(self):
        """Check network events for anomalies"""
        try:
            # Simulate network monitoring
            # In a real implementation, this would analyze network traffic
            
            # Example: Detect suspicious network activity
            suspicious_connections = await self._simulate_network_anomaly_detection()
            if suspicious_connections:
                await self._create_incident({
                    "title": "Suspicious Network Activity",
                    "description": f"Detected {len(suspicious_connections)} suspicious connections",
                    "severity": IncidentSeverity.HIGH,
                    "category": IncidentCategory.NETWORK_ANOMALY,
                    "source_system": "network_monitor",
                    "affected_assets": [conn["source_ip"] for conn in suspicious_connections],
                    "indicators": suspicious_connections
                })
            
        except Exception as e:
            self.logger.error(f"Error checking network events: {e}")
    
    async def _simulate_network_anomaly_detection(self) -> List[Dict[str, Any]]:
        """Simulate network anomaly detection"""
        import random
        if random.random() < 0.1:  # 10% chance of anomaly
            return [
                {
                    "type": "suspicious_connection",
                    "source_ip": "192.168.1.100",
                    "dest_ip": "10.0.0.50",
                    "port": 4444,
                    "protocol": "tcp",
                    "anomaly_score": 0.85
                }
            ]
        return []
    
    async def _check_security_alerts(self):
        """Check security tool alerts"""
        try:
            # Simulate security tool integration
            # In a real implementation, this would integrate with security tools
            
            # Example: Check for malware alerts
            malware_alerts = await self._simulate_malware_detection()
            for alert in malware_alerts:
                await self._create_incident({
                    "title": f"Malware Detected: {alert['malware_name']}",
                    "description": f"Malware {alert['malware_name']} detected on {alert['host']}",
                    "severity": IncidentSeverity.HIGH,
                    "category": IncidentCategory.MALWARE,
                    "source_system": "antivirus",
                    "affected_assets": [alert["host"]],
                    "indicators": [alert]
                })
            
        except Exception as e:
            self.logger.error(f"Error checking security alerts: {e}")
    
    async def _simulate_malware_detection(self) -> List[Dict[str, Any]]:
        """Simulate malware detection"""
        import random
        import tempfile
        import os
        if random.random() < 0.05:  # 5% chance of malware
            # Use secure temp directory instead of hardcoded /tmp
            temp_dir = tempfile.mkdtemp(prefix="syn_os_incident_", suffix="_files")
            return [
                {
                    "type": "malware_detection",
                    "malware_name": "Trojan.Generic.12345",
                    "host": "workstation-01",
                    "file_path": os.path.join(temp_dir, "suspicious_file.exe"),
                    "hash": "a1b2c3d4e5f6789012345678901234567890abcd",
                    "confidence": 0.95
                }
            ]
        return []
    
    async def _create_incident(self, incident_data: Dict[str, Any]) -> str:
        """Create a new security incident"""
        try:
            incident_id = str(uuid.uuid4())
            current_time = time.time()
            
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.get('overall_consciousness_level', 0)
            
            incident = Incident(
                incident_id=incident_id,
                title=incident_data["title"],
                description=incident_data["description"],
                severity=incident_data["severity"],
                category=incident_data["category"],
                status=IncidentStatus.NEW,
                source_system=incident_data["source_system"],
                affected_assets=incident_data.get("affected_assets", []),
                indicators=incident_data.get("indicators", []),
                created_at=current_time,
                updated_at=current_time,
                consciousness_level=consciousness_level
            )
            
            # Store incident
            await self._store_incident(incident)
            self.incidents[incident_id] = incident
            
            self.logger.info(f"Created incident: {incident.title} - {incident.severity.value}")
            
            # Trigger automated response
            if self.auto_response_enabled:
                asyncio.create_task(self._trigger_automated_response(incident))
            
            # Send notifications
            await self._send_incident_notification(incident)
            
            return incident_id
            
        except Exception as e:
            self.logger.error(f"Error creating incident: {e}")
            return ""
    
    async def _store_incident(self, incident: Incident):
        """Store incident in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO incidents 
                (incident_id, title, description, severity, category, status, source_system,
                 affected_assets, indicators, created_at, updated_at, assigned_to, resolution,
                 evidence, response_actions, consciousness_level, automated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.incident_id, incident.title, incident.description,
                incident.severity.value, incident.category.value, incident.status.value,
                incident.source_system, json.dumps(incident.affected_assets),
                json.dumps(incident.indicators), incident.created_at, incident.updated_at,
                incident.assigned_to, incident.resolution, json.dumps(incident.evidence),
                json.dumps(incident.response_actions), incident.consciousness_level,
                incident.automated
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing incident: {e}")
    
    async def _store_playbook(self, playbook: ResponsePlaybook):
        """Store playbook in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO playbooks 
                (playbook_id, name, description, category, severity_threshold, conditions,
                 actions, approval_required, consciousness_threshold, created_at, updated_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                playbook.playbook_id, playbook.name, playbook.description,
                playbook.category.value, playbook.severity_threshold.value,
                json.dumps(playbook.conditions), json.dumps(playbook.actions),
                playbook.approval_required, playbook.consciousness_threshold,
                playbook.created_at, playbook.updated_at, playbook.active
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing playbook: {e}")
    
    async def _send_incident_notification(self, incident: Incident):
        """Send incident notification"""
        try:
            if not self.notification_settings["email_enabled"]:
                return
            
            subject = f"[Syn_OS IR] {incident.severity.value.upper()}: {incident.title}"
            body = f"""
Security Incident Alert

Incident ID: {incident.incident_id}
Title: {incident.title}
Severity: {incident.severity.value.upper()}
Category: {incident.category.value}
Status: {incident.status.value}
Source: {incident.source_system}

Description:
{incident.description}

Affected Assets:
{', '.join(incident.affected_assets) if incident.affected_assets else 'None'}

Created: {datetime.fromtimestamp(incident.created_at)}

This is an automated alert from Syn_OS Incident Response System.
            """
            
            # In a real implementation, this would send actual emails
            self.logger.info(f"Notification sent for incident {incident.incident_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending incident notification: {e}")
    
    async def _trigger_automated_response(self, incident: Incident):
        """Trigger automated response for an incident"""
        try:
            # Find matching playbooks
            matching_playbooks = await self._find_matching_playbooks(incident)
            
            if not matching_playbooks:
                self.logger.info(f"No matching playbooks found for incident {incident.incident_id}")
                return
            
            # Check consciousness level
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.get('overall_consciousness_level', 0)
            
            for playbook in matching_playbooks:
                if consciousness_level < playbook.consciousness_threshold:
                    self.logger.info(f"Consciousness level too low for playbook {playbook.name}")
                    continue
                
                if playbook.approval_required and incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
                    # Request approval for high-severity incidents
                    await self._request_approval(incident, playbook)
                else:
                    # Execute playbook automatically
                    await self._execute_playbook(incident, playbook)
            
        except Exception as e:
            self.logger.error(f"Error triggering automated response: {e}")
    
    async def _find_matching_playbooks(self, incident: Incident) -> List[ResponsePlaybook]:
        """Find playbooks that match the incident"""
        matching_playbooks = []
        
        try:
            for playbook in self.playbooks.values():
                if not playbook.active:
                    continue
                
                # Check category match
                if playbook.category != incident.category:
                    continue
                
                # Check severity threshold
                severity_levels = {
                    IncidentSeverity.INFO: 0,
                    IncidentSeverity.LOW: 1,
                    IncidentSeverity.MEDIUM: 2,
                    IncidentSeverity.HIGH: 3,
                    IncidentSeverity.CRITICAL: 4
                }
                
                if severity_levels[incident.severity] < severity_levels[playbook.severity_threshold]:
                    continue
                
                # Check conditions
                if await self._evaluate_playbook_conditions(incident, playbook):
                    matching_playbooks.append(playbook)
            
        except Exception as e:
            self.logger.error(f"Error finding matching playbooks: {e}")
        
        return matching_playbooks
    
    async def _evaluate_playbook_conditions(self, incident: Incident, playbook: ResponsePlaybook) -> bool:
        """Evaluate if playbook conditions are met"""
        try:
            if not playbook.conditions:
                return True
            
            for condition in playbook.conditions:
                condition_type = condition.get("type")
                
                if condition_type == "indicator_match":
                    value = condition.get("value")
                    if not any(indicator.get("type") == value for indicator in incident.indicators):
                        return False
                
                elif condition_type == "affected_assets_count":
                    min_count = condition.get("min_count", 1)
                    if len(incident.affected_assets) < min_count:
                        return False
                
                elif condition_type == "source_system":
                    required_system = condition.get("system")
                    if incident.source_system != required_system:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating playbook conditions: {e}")
            return False
    
    async def _request_approval(self, incident: Incident, playbook: ResponsePlaybook):
        """Request approval for playbook execution"""
        try:
            self.logger.info(f"Requesting approval for playbook {playbook.name} on incident {incident.incident_id}")
            
            # Update incident status
            incident.status = IncidentStatus.ACKNOWLEDGED
            incident.updated_at = time.time()
            await self._store_incident(incident)
            
            # Send approval request notification
            await self._send_approval_request(incident, playbook)
            
        except Exception as e:
            self.logger.error(f"Error requesting approval: {e}")
    
    async def _send_approval_request(self, incident: Incident, playbook: ResponsePlaybook):
        """Send approval request notification"""
        try:
            self.logger.info(f"Approval request sent for incident {incident.incident_id} - playbook {playbook.name}")
            # In a real implementation, this would send actual approval requests
            
        except Exception as e:
            self.logger.error(f"Error sending approval request: {e}")
    
    async def _execute_playbook(self, incident: Incident, playbook: ResponsePlaybook):
        """Execute a response playbook"""
        try:
            self.logger.info(f"Executing playbook {playbook.name} for incident {incident.incident_id}")
            
            # Update incident status
            incident.status = IncidentStatus.INVESTIGATING
            incident.updated_at = time.time()
            await self._store_incident(incident)
            
            # Sort actions by priority
            actions = sorted(playbook.actions, key=lambda x: x.get("priority", 999))
            
            # Execute actions
            for action_data in actions:
                action_type = ResponseActionType(action_data["type"])
                
                # Create response action
                action_id = str(uuid.uuid4())
                action = ResponseAction(
                    action_id=action_id,
                    incident_id=incident.incident_id,
                    action_type=action_type,
                    parameters=action_data.get("parameters", {}),
                    status="pending",
                    result=None,
                    executed_at=None,
                    completed_at=None
                )
                
                # Store and queue action
                await self._store_response_action(action)
                self.active_responses[action_id] = action
                
                self.logger.info(f"Queued response action: {action_type.value} for incident {incident.incident_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing playbook: {e}")
    
    async def _store_response_action(self, action: ResponseAction):
        """Store response action in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO response_actions
                (action_id, incident_id, action_type, parameters, status, result,
                 executed_at, completed_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                action.action_id, action.incident_id, action.action_type.value,
                json.dumps(action.parameters), action.status,
                json.dumps(action.result) if action.result else None,
                action.executed_at, action.completed_at, action.error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing response action: {e}")
    
    async def _process_responses(self):
        """Process queued response actions"""
        try:
            while True:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Get pending actions
                pending_actions = [action for action in self.active_responses.values()
                                 if action.status == "pending"]
                
                # Limit concurrent responses
                running_count = len([action for action in self.active_responses.values()
                                   if action.status == "running"])
                
                available_slots = self.max_concurrent_responses - running_count
                
                for action in pending_actions[:available_slots]:
                    asyncio.create_task(self._execute_response_action(action))
                
        except Exception as e:
            self.logger.error(f"Error processing responses: {e}")
    
    async def _execute_response_action(self, action: ResponseAction):
        """Execute a single response action"""
        try:
            self.logger.info(f"Executing response action: {action.action_type.value}")
            
            # Update action status
            action.status = "running"
            action.executed_at = time.time()
            await self._store_response_action(action)
            
            # Execute based on action type
            result = {}
            
            if action.action_type == ResponseActionType.ISOLATE_HOST:
                result = await self._isolate_host(action.parameters)
            elif action.action_type == ResponseActionType.BLOCK_IP:
                result = await self._block_ip(action.parameters)
            elif action.action_type == ResponseActionType.DISABLE_USER:
                result = await self._disable_user(action.parameters)
            elif action.action_type == ResponseActionType.QUARANTINE_FILE:
                result = await self._quarantine_file(action.parameters)
            elif action.action_type == ResponseActionType.RESET_PASSWORD:
                result = await self._reset_password(action.parameters)
            elif action.action_type == ResponseActionType.COLLECT_EVIDENCE:
                result = await self._collect_evidence(action.parameters)
            elif action.action_type == ResponseActionType.NOTIFY_TEAM:
                result = await self._notify_team(action.parameters)
            elif action.action_type == ResponseActionType.ESCALATE:
                result = await self._escalate_incident(action.parameters)
            elif action.action_type == ResponseActionType.CREATE_TICKET:
                result = await self._create_ticket(action.parameters)
            elif action.action_type == ResponseActionType.RUN_SCAN:
                result = await self._run_scan(action.parameters)
            
            # Update action completion
            action.status = "completed"
            action.result = result
            action.completed_at = time.time()
            await self._store_response_action(action)
            
            self.logger.info(f"Response action completed: {action.action_type.value}")
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            action.completed_at = time.time()
            await self._store_response_action(action)
            self.logger.error(f"Response action failed: {action.action_type.value} - {e}")
    
    # Response action implementations
    
    async def _isolate_host(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate a host from the network"""
        try:
            host = parameters.get("host", "unknown")
            self.logger.info(f"Isolating host: {host}")
            
            # Simulate host isolation
            await asyncio.sleep(2)
            
            return {
                "action": "isolate_host",
                "host": host,
                "status": "isolated",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error isolating host: {e}")
            return {"error": str(e)}
    
    async def _block_ip(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Block an IP address"""
        try:
            ip_address = parameters.get("ip_address", "unknown")
            self.logger.info(f"Blocking IP address: {ip_address}")
            
            # Simulate IP blocking
            await asyncio.sleep(1)
            
            return {
                "action": "block_ip",
                "ip_address": ip_address,
                "status": "blocked",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error blocking IP: {e}")
            return {"error": str(e)}
    
    async def _disable_user(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a user account"""
        try:
            username = parameters.get("username", "unknown")
            self.logger.info(f"Disabling user account: {username}")
            
            # Simulate user account disabling
            await asyncio.sleep(1)
            
            return {
                "action": "disable_user",
                "username": username,
                "status": "disabled",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error disabling user: {e}")
            return {"error": str(e)}
    
    async def _quarantine_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Quarantine a malicious file"""
        try:
            file_path = parameters.get("file_path", "unknown")
            self.logger.info(f"Quarantining file: {file_path}")
            
            # Simulate file quarantine
            await asyncio.sleep(1)
            
            return {
                "action": "quarantine_file",
                "file_path": file_path,
                "status": "quarantined",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error quarantining file: {e}")
            return {"error": str(e)}
    
    async def _reset_password(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reset a user password"""
        try:
            username = parameters.get("username", "unknown")
            self.logger.info(f"Resetting password for user: {username}")
            
            # Simulate password reset
            await asyncio.sleep(1)
            
            return {
                "action": "reset_password",
                "username": username,
                "status": "reset",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error resetting password: {e}")
            return {"error": str(e)}
    
    async def _collect_evidence(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Collect digital evidence"""
        try:
            evidence_type = parameters.get("evidence_type", "system_logs")
            self.logger.info(f"Collecting evidence: {evidence_type}")
            
            # Simulate evidence collection
            await asyncio.sleep(3)
            
            return {
                "action": "collect_evidence",
                "evidence_type": evidence_type,
                "status": "collected",
                "evidence_id": str(uuid.uuid4()),
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting evidence: {e}")
            return {"error": str(e)}
    
    async def _notify_team(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Notify security team"""
        try:
            message = parameters.get("message", "Security incident detected")
            self.logger.info(f"Notifying security team: {message}")
            
            # Simulate team notification
            await asyncio.sleep(1)
            
            return {
                "action": "notify_team",
                "message": message,
                "status": "notified",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error notifying team: {e}")
            return {"error": str(e)}
    
    async def _escalate_incident(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate incident to higher tier"""
        try:
            escalation_level = parameters.get("escalation_level", "tier2")
            self.logger.info(f"Escalating incident to: {escalation_level}")
            
            # Simulate escalation
            await asyncio.sleep(1)
            
            return {
                "action": "escalate",
                "escalation_level": escalation_level,
                "status": "escalated",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error escalating incident: {e}")
            return {"error": str(e)}
    
    async def _create_ticket(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create support ticket"""
        try:
            ticket_type = parameters.get("ticket_type", "security_incident")
            self.logger.info(f"Creating ticket: {ticket_type}")
            
            # Simulate ticket creation
            await asyncio.sleep(1)
            
            return {
                "action": "create_ticket",
                "ticket_type": ticket_type,
                "ticket_id": f"INC-{int(time.time())}",
                "status": "created",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating ticket: {e}")
            return {"error": str(e)}
    
    async def _run_scan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run security scan"""
        try:
            scan_type = parameters.get("scan_type", "vulnerability_scan")
            target = parameters.get("target", "localhost")
            self.logger.info(f"Running {scan_type} on {target}")
            
            # Simulate scan execution
            await asyncio.sleep(5)
            
            return {
                "action": "run_scan",
                "scan_type": scan_type,
                "target": target,
                "scan_id": str(uuid.uuid4()),
                "status": "completed",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error running scan: {e}")
            return {"error": str(e)}
    
    async def _age_incidents(self):
        """Age incidents and handle escalation timeouts"""
        try:
            while True:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = time.time()
                
                for incident in self.incidents.values():
                    # Check for escalation timeout
                    if (incident.status == IncidentStatus.ACKNOWLEDGED and
                        current_time - incident.updated_at > self.escalation_timeout):
                        
                        self.logger.info(f"Escalating incident {incident.incident_id} due to timeout")
                        incident.status = IncidentStatus.INVESTIGATING
                        incident.updated_at = current_time
                        await self._store_incident(incident)
                
        except Exception as e:
            self.logger.error(f"Error aging incidents: {e}")
    
    # Public API methods
    
    async def create_manual_incident(self, incident_data: Dict[str, Any]) -> str:
        """Create a manual incident"""
        try:
            # Validate required fields
            required_fields = ["title", "description", "severity", "category"]
            for field in required_fields:
                if field not in incident_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert string enums if needed
            if isinstance(incident_data["severity"], str):
                incident_data["severity"] = IncidentSeverity(incident_data["severity"])
            if isinstance(incident_data["category"], str):
                incident_data["category"] = IncidentCategory(incident_data["category"])
            
            # Set defaults
            incident_data.setdefault("source_system", "manual")
            incident_data.setdefault("affected_assets", [])
            incident_data.setdefault("indicators", [])
            
            return await self._create_incident(incident_data)
            
        except Exception as e:
            self.logger.error(f"Error creating manual incident: {e}")
            return ""
    
    async def get_incidents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get incidents with optional filters"""
        try:
            if filters is None:
                filters = {}
            
            incidents = []
            
            for incident in self.incidents.values():
                # Apply filters
                if filters.get("severity") and incident.severity.value != filters["severity"]:
                    continue
                if filters.get("status") and incident.status.value != filters["status"]:
                    continue
                if filters.get("category") and incident.category.value != filters["category"]:
                    continue
                
                # Convert to dict
                incident_dict = asdict(incident)
                incident_dict["severity"] = incident.severity.value
                incident_dict["category"] = incident.category.value
                incident_dict["status"] = incident.status.value
                incidents.append(incident_dict)
            
            # Sort by created_at descending
            incidents.sort(key=lambda x: x["created_at"], reverse=True)
            
            return incidents
            
        except Exception as e:
            self.logger.error(f"Error getting incidents: {e}")
            return []
    
    async def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Update incident record"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            
            # Apply updates
            if "status" in updates:
                if isinstance(updates["status"], str):
                    incident.status = IncidentStatus(updates["status"])
                else:
                    incident.status = updates["status"]
            
            if "assigned_to" in updates:
                incident.assigned_to = updates["assigned_to"]
            
            if "resolution" in updates:
                incident.resolution = updates["resolution"]
            
            # Update timestamp
            incident.updated_at = time.time()
            
            # Store updated incident
            await self._store_incident(incident)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating incident: {e}")
            return False
    
    async def get_incident_statistics(self) -> Dict[str, Any]:
        """Get incident statistics"""
        try:
            stats = {
                "total_incidents": len(self.incidents),
                "by_severity": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0
                },
                "by_status": {
                    "new": 0,
                    "acknowledged": 0,
                    "investigating": 0,
                    "contained": 0,
                    "resolved": 0,
                    "closed": 0
                },
                "by_category": {},
                "active_responses": len([r for r in self.active_responses.values()
                                       if r.status in ["pending", "running"]]),
                "total_playbooks": len(self.playbooks)
            }
            
            for incident in self.incidents.values():
                stats["by_severity"][incident.severity.value] += 1
                stats["by_status"][incident.status.value] += 1
                
                category = incident.category.value
                if category not in stats["by_category"]:
                    stats["by_category"][category] = 0
                stats["by_category"][category] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting incident statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            return {
                "status": "healthy",
                "consciousness_level": consciousness_state.get('overall_consciousness_level', 0),
                "active_incidents": len([i for i in self.incidents.values()
                                       if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]]),
                "active_responses": len([r for r in self.active_responses.values()
                                       if r.status in ["pending", "running"]]),
                "total_playbooks": len(self.playbooks),
                "auto_response_enabled": self.auto_response_enabled,
                "database_connected": True
            }
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def shutdown(self):
        """Shutdown the incident response system"""
        try:
            self.logger.info("Shutting down incident response automation...")
            
            # Cancel all pending responses
            for action in self.active_responses.values():
                if action.status == "pending":
                    action.status = "cancelled"
                    await self._store_response_action(action)
            
            self.logger.info("Incident response automation shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Example usage and testing
async def main():
    """Example usage of the incident response automation"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    
    # Create incident response system
    ir_system = IncidentResponseAutomation(consciousness_bus)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Get health status
    health = await ir_system.health_check()
    print(f"IR System health: {health}")
    
    # Get statistics
    stats = await ir_system.get_incident_statistics()
    print(f"Incident statistics: {stats}")
    
    # Create a manual incident
    incident_id = await ir_system.create_manual_incident({
        "title": "Suspicious Network Activity",
        "description": "Detected unusual network traffic patterns",
        "severity": "high",
        "category": "network_anomaly",
        "affected_assets": ["server-01", "workstation-05"],
        "indicators": [
            {"type": "network_anomaly", "score": 0.85}
        ]
    })
    print(f"Manual incident created: {incident_id}")
    
    # Wait for automated response
    await asyncio.sleep(10)
    
    # Get incidents
    incidents = await ir_system.get_incidents()
    print(f"Total incidents: {len(incidents)}")
    
    # Update incident status
    if incident_id:
        updated = await ir_system.update_incident(incident_id, {
            "status": "resolved",
            "resolution": "False positive - normal backup traffic"
        })
        print(f"Incident updated: {updated}")
    
    # Shutdown
    await ir_system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())