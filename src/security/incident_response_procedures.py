#!/usr/bin/env python3
"""
Incident Response Procedures Implementation
Comprehensive incident response system for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IncidentStatus(Enum):
    """Incident status definitions"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCategory(Enum):
    """Incident category types"""
    SECURITY_BREACH = "security_breach"
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing"
    SYSTEM_COMPROMISE = "system_compromise"
    POLICY_VIOLATION = "policy_violation"
    OTHER = "other"


class ResponseAction(Enum):
    """Response action types"""
    CONTAIN = "contain"
    INVESTIGATE = "investigate"
    ERADICATE = "eradicate"
    RECOVER = "recover"
    MONITOR = "monitor"
    DOCUMENT = "document"
    COMMUNICATE = "communicate"
    ESCALATE = "escalate"


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    reporter: str
    assigned_to: Optional[str]
    detection_time: float
    reported_time: float
    response_time: Optional[float]
    resolution_time: Optional[float]
    affected_systems: List[str]
    indicators_of_compromise: List[str]
    evidence_collected: List[str]
    response_actions: List[str]
    lessons_learned: str
    root_cause: str
    created_by: str
    last_modified: float


@dataclass
class ResponseTeamMember:
    """Incident response team member"""
    member_id: str
    name: str
    role: str
    contact_email: str
    contact_phone: str
    expertise: List[str]
    availability_status: str
    escalation_level: int


@dataclass
class ResponsePlaybook:
    """Incident response playbook"""
    playbook_id: str
    name: str
    description: str
    incident_types: List[IncidentCategory]
    severity_levels: List[IncidentSeverity]
    response_steps: List[Dict[str, Any]]
    required_roles: List[str]
    estimated_duration: int
    success_criteria: List[str]
    created_date: float
    last_updated: float


@dataclass
class EscalationRule:
    """Escalation rule definition"""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    escalation_targets: List[str]
    notification_methods: List[str]
    escalation_delay: int
    auto_escalate: bool


class IncidentResponseProcedures:
    """
    Incident Response Procedures System
    Implements comprehensive incident response capabilities
    """
    
    def __init__(self):
        """Initialize incident response system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.ir_directory = "/var/lib/synos/incident_response"
        self.database_file = f"{self.ir_directory}/incidents.db"
        self.evidence_directory = f"{self.ir_directory}/evidence"
        self.playbooks_directory = f"{self.ir_directory}/playbooks"
        
        # System components
        self.incidents: Dict[str, SecurityIncident] = {}
        self.response_team: Dict[str, ResponseTeamMember] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        
        # Response configuration
        self.sla_targets = {
            IncidentSeverity.CRITICAL: {"response": 15, "resolution": 240},  # 15 min, 4 hours
            IncidentSeverity.HIGH: {"response": 60, "resolution": 480},      # 1 hour, 8 hours
            IncidentSeverity.MEDIUM: {"response": 240, "resolution": 1440},  # 4 hours, 24 hours
            IncidentSeverity.LOW: {"response": 1440, "resolution": 4320},    # 24 hours, 72 hours
            IncidentSeverity.INFORMATIONAL: {"response": 4320, "resolution": 10080}  # 72 hours, 1 week
        }
        
        self.notification_config = {
            "smtp_server": "localhost",
            "smtp_port": 587,
            "from_email": "security@synos.local",
            "emergency_contacts": [
                "ciso@synos.local",
                "cto@synos.local",
                "security-team@synos.local"
            ]
        }
        
        # System metrics
        self.metrics = {
            "total_incidents": 0,
            "open_incidents": 0,
            "critical_incidents": 0,
            "average_response_time": 0.0,
            "average_resolution_time": 0.0,
            "sla_compliance": 0.0,
            "escalated_incidents": 0,
            "false_positives": 0
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_incident_response())
    
    async def _initialize_incident_response(self):
        """Initialize incident response system"""
        try:
            self.logger.info("Initializing incident response procedures...")
            
            # Create directories
            os.makedirs(self.ir_directory, exist_ok=True)
            os.makedirs(self.evidence_directory, exist_ok=True)
            os.makedirs(self.playbooks_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Create response team
            await self._create_response_team()
            
            # Deploy response playbooks
            await self._deploy_response_playbooks()
            
            # Configure escalation rules
            await self._configure_escalation_rules()
            
            # Start monitoring tasks
            asyncio.create_task(self._sla_monitoring_task())
            asyncio.create_task(self._escalation_monitoring_task())
            
            self.logger.info("Incident response procedures initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing incident response: {e}")
    
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
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reporter TEXT,
                    assigned_to TEXT,
                    detection_time REAL,
                    reported_time REAL,
                    response_time REAL,
                    resolution_time REAL,
                    affected_systems TEXT,
                    indicators_of_compromise TEXT,
                    evidence_collected TEXT,
                    response_actions TEXT,
                    lessons_learned TEXT,
                    root_cause TEXT,
                    created_by TEXT,
                    last_modified REAL
                )
            ''')
            
            # Response team table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_team (
                    member_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    contact_email TEXT,
                    contact_phone TEXT,
                    expertise TEXT,
                    availability_status TEXT,
                    escalation_level INTEGER
                )
            ''')
            
            # Playbooks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS playbooks (
                    playbook_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    incident_types TEXT,
                    severity_levels TEXT,
                    response_steps TEXT,
                    required_roles TEXT,
                    estimated_duration INTEGER,
                    success_criteria TEXT,
                    created_date REAL,
                    last_updated REAL
                )
            ''')
            
            # Escalation rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS escalation_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    conditions TEXT,
                    escalation_targets TEXT,
                    notification_methods TEXT,
                    escalation_delay INTEGER,
                    auto_escalate BOOLEAN
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_detection_time ON incidents (detection_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_role ON response_team (role)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing incident response database: {e}")
            raise
    
    async def _create_response_team(self):
        """Create incident response team"""
        try:
            current_time = time.time()
            
            team_members = [
                ResponseTeamMember(
                    member_id="IRT-001",
                    name="Incident Commander",
                    role="incident_commander",
                    contact_email="ic@synos.local",
                    contact_phone="+1-555-0001",
                    expertise=["incident_management", "crisis_communication", "decision_making"],
                    availability_status="available",
                    escalation_level=1
                ),
                ResponseTeamMember(
                    member_id="IRT-002",
                    name="Security Analyst Lead",
                    role="security_analyst",
                    contact_email="security-lead@synos.local",
                    contact_phone="+1-555-0002",
                    expertise=["threat_analysis", "forensics", "malware_analysis"],
                    availability_status="available",
                    escalation_level=1
                ),
                ResponseTeamMember(
                    member_id="IRT-003",
                    name="IT Operations Lead",
                    role="it_operations",
                    contact_email="itops-lead@synos.local",
                    contact_phone="+1-555-0003",
                    expertise=["system_administration", "network_management", "recovery"],
                    availability_status="available",
                    escalation_level=1
                ),
                ResponseTeamMember(
                    member_id="IRT-004",
                    name="Legal Counsel",
                    role="legal",
                    contact_email="legal@synos.local",
                    contact_phone="+1-555-0004",
                    expertise=["regulatory_compliance", "breach_notification", "legal_advice"],
                    availability_status="on_call",
                    escalation_level=2
                ),
                ResponseTeamMember(
                    member_id="IRT-005",
                    name="Communications Lead",
                    role="communications",
                    contact_email="comms@synos.local",
                    contact_phone="+1-555-0005",
                    expertise=["public_relations", "stakeholder_communication", "media_relations"],
                    availability_status="on_call",
                    escalation_level=2
                ),
                ResponseTeamMember(
                    member_id="IRT-006",
                    name="Forensics Specialist",
                    role="forensics",
                    contact_email="forensics@synos.local",
                    contact_phone="+1-555-0006",
                    expertise=["digital_forensics", "evidence_collection", "chain_of_custody"],
                    availability_status="available",
                    escalation_level=1
                )
            ]
            
            for member in team_members:
                await self._store_team_member(member)
                self.response_team[member.member_id] = member
            
            self.logger.info(f"Created incident response team with {len(team_members)} members")
            
        except Exception as e:
            self.logger.error(f"Error creating response team: {e}")
    
    async def _deploy_response_playbooks(self):
        """Deploy incident response playbooks"""
        try:
            current_time = time.time()
            
            playbooks = [
                ResponsePlaybook(
                    playbook_id="PB-001",
                    name="Security Breach Response",
                    description="Response procedures for confirmed security breaches",
                    incident_types=[IncidentCategory.SECURITY_BREACH, IncidentCategory.UNAUTHORIZED_ACCESS],
                    severity_levels=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
                    response_steps=[
                        {"step": 1, "action": "Immediate containment", "duration": 15, "responsible": "security_analyst"},
                        {"step": 2, "action": "Evidence preservation", "duration": 30, "responsible": "forensics"},
                        {"step": 3, "action": "Impact assessment", "duration": 60, "responsible": "incident_commander"},
                        {"step": 4, "action": "Stakeholder notification", "duration": 30, "responsible": "communications"},
                        {"step": 5, "action": "Eradication", "duration": 120, "responsible": "security_analyst"},
                        {"step": 6, "action": "Recovery", "duration": 240, "responsible": "it_operations"},
                        {"step": 7, "action": "Lessons learned", "duration": 60, "responsible": "incident_commander"}
                    ],
                    required_roles=["incident_commander", "security_analyst", "forensics", "it_operations"],
                    estimated_duration=555,
                    success_criteria=["Threat contained", "Systems restored", "Evidence preserved", "Stakeholders notified"],
                    created_date=current_time,
                    last_updated=current_time
                ),
                ResponsePlaybook(
                    playbook_id="PB-002",
                    name="Malware Incident Response",
                    description="Response procedures for malware infections",
                    incident_types=[IncidentCategory.MALWARE],
                    severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
                    response_steps=[
                        {"step": 1, "action": "Isolate infected systems", "duration": 10, "responsible": "security_analyst"},
                        {"step": 2, "action": "Malware analysis", "duration": 60, "responsible": "security_analyst"},
                        {"step": 3, "action": "Scope assessment", "duration": 30, "responsible": "security_analyst"},
                        {"step": 4, "action": "Containment verification", "duration": 15, "responsible": "it_operations"},
                        {"step": 5, "action": "Malware removal", "duration": 90, "responsible": "it_operations"},
                        {"step": 6, "action": "System restoration", "duration": 120, "responsible": "it_operations"},
                        {"step": 7, "action": "Monitoring", "duration": 60, "responsible": "security_analyst"}
                    ],
                    required_roles=["security_analyst", "it_operations"],
                    estimated_duration=385,
                    success_criteria=["Malware removed", "Systems clean", "No lateral movement", "Monitoring active"],
                    created_date=current_time,
                    last_updated=current_time
                ),
                ResponsePlaybook(
                    playbook_id="PB-003",
                    name="Data Breach Response",
                    description="Response procedures for data breaches",
                    incident_types=[IncidentCategory.DATA_BREACH],
                    severity_levels=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
                    response_steps=[
                        {"step": 1, "action": "Immediate containment", "duration": 15, "responsible": "security_analyst"},
                        {"step": 2, "action": "Data impact assessment", "duration": 60, "responsible": "incident_commander"},
                        {"step": 3, "action": "Legal consultation", "duration": 30, "responsible": "legal"},
                        {"step": 4, "action": "Regulatory notification", "duration": 60, "responsible": "legal"},
                        {"step": 5, "action": "Customer notification", "duration": 120, "responsible": "communications"},
                        {"step": 6, "action": "Forensic investigation", "duration": 240, "responsible": "forensics"},
                        {"step": 7, "action": "Remediation", "duration": 180, "responsible": "security_analyst"},
                        {"step": 8, "action": "Credit monitoring setup", "duration": 60, "responsible": "legal"}
                    ],
                    required_roles=["incident_commander", "security_analyst", "forensics", "legal", "communications"],
                    estimated_duration=765,
                    success_criteria=["Breach contained", "Notifications sent", "Investigation complete", "Remediation implemented"],
                    created_date=current_time,
                    last_updated=current_time
                )
            ]
            
            for playbook in playbooks:
                await self._store_playbook(playbook)
                self.playbooks[playbook.playbook_id] = playbook
                
                # Save playbook as JSON file
                playbook_file = f"{self.playbooks_directory}/{playbook.playbook_id}_{playbook.name.replace(' ', '_')}.json"
                with open(playbook_file, 'w') as f:
                    json.dump(asdict(playbook), f, indent=2, default=str)
            
            self.logger.info(f"Deployed {len(playbooks)} incident response playbooks")
            
        except Exception as e:
            self.logger.error(f"Error deploying playbooks: {e}")
    
    async def _configure_escalation_rules(self):
        """Configure escalation rules"""
        try:
            escalation_rules = [
                EscalationRule(
                    rule_id="ESC-001",
                    name="Critical Incident Auto-Escalation",
                    conditions={"severity": "critical", "no_response_time": 15},
                    escalation_targets=["ciso@synos.local", "cto@synos.local"],
                    notification_methods=["email", "sms"],
                    escalation_delay=15,
                    auto_escalate=True
                ),
                EscalationRule(
                    rule_id="ESC-002",
                    name="High Severity SLA Breach",
                    conditions={"severity": "high", "sla_breach": True},
                    escalation_targets=["security-manager@synos.local"],
                    notification_methods=["email"],
                    escalation_delay=60,
                    auto_escalate=True
                ),
                EscalationRule(
                    rule_id="ESC-003",
                    name="Data Breach Escalation",
                    conditions={"category": "data_breach"},
                    escalation_targets=["ciso@synos.local", "legal@synos.local", "ceo@synos.local"],
                    notification_methods=["email", "phone"],
                    escalation_delay=0,
                    auto_escalate=True
                )
            ]
            
            for rule in escalation_rules:
                await self._store_escalation_rule(rule)
                self.escalation_rules[rule.rule_id] = rule
            
            self.logger.info(f"Configured {len(escalation_rules)} escalation rules")
            
        except Exception as e:
            self.logger.error(f"Error configuring escalation rules: {e}")
    
    async def create_incident(self, title: str, description: str, category: IncidentCategory,
                            severity: IncidentSeverity, reporter: str, affected_systems: Optional[List[str]] = None,
                            indicators: Optional[List[str]] = None) -> str:
        """Create new security incident"""
        try:
            current_time = time.time()
            incident_id = f"INC-{int(current_time)}-{str(uuid.uuid4())[:8]}"
            
            incident = SecurityIncident(
                incident_id=incident_id,
                title=title,
                description=description,
                category=category,
                severity=severity,
                status=IncidentStatus.NEW,
                reporter=reporter,
                assigned_to=None,
                detection_time=current_time,
                reported_time=current_time,
                response_time=None,
                resolution_time=None,
                affected_systems=affected_systems or [],
                indicators_of_compromise=indicators or [],
                evidence_collected=[],
                response_actions=[],
                lessons_learned="",
                root_cause="",
                created_by=reporter,
                last_modified=current_time
            )
            
            await self._store_incident(incident)
            self.incidents[incident_id] = incident
            
            # Update metrics
            self.metrics["total_incidents"] += 1
            self.metrics["open_incidents"] += 1
            if severity == IncidentSeverity.CRITICAL:
                self.metrics["critical_incidents"] += 1
            
            # Auto-assign based on severity and category
            await self._auto_assign_incident(incident)
            
            # Send notifications
            await self._send_incident_notifications(incident, "created")
            
            # Check for immediate escalation
            await self._check_escalation_rules(incident)
            
            self.logger.info(f"Created incident: {incident_id} - {title}")
            return incident_id
            
        except Exception as e:
            self.logger.error(f"Error creating incident: {e}")
            raise
    
    async def _auto_assign_incident(self, incident: SecurityIncident):
        """Auto-assign incident based on severity and category"""
        try:
            # Find available team member based on incident characteristics
            assigned_member = None
            
            if incident.category in [IncidentCategory.DATA_BREACH, IncidentCategory.SECURITY_BREACH]:
                # Assign to incident commander for critical incidents
                for member in self.response_team.values():
                    if member.role == "incident_commander" and member.availability_status == "available":
                        assigned_member = member.member_id
                        break
            elif incident.category == IncidentCategory.MALWARE:
                # Assign to security analyst for malware
                for member in self.response_team.values():
                    if member.role == "security_analyst" and member.availability_status == "available":
                        assigned_member = member.member_id
                        break
            
            if assigned_member:
                incident.assigned_to = assigned_member
                incident.status = IncidentStatus.ASSIGNED
                incident.response_time = time.time()
                incident.last_modified = time.time()
                
                await self._store_incident(incident)
                self.logger.info(f"Auto-assigned incident {incident.incident_id} to {assigned_member}")
            
        except Exception as e:
            self.logger.error(f"Error auto-assigning incident: {e}")
    
    async def _send_incident_notifications(self, incident: SecurityIncident, action: str):
        """Send incident notifications"""
        try:
            subject = f"[{incident.severity.value.upper()}] Security Incident {action.title()}: {incident.title}"
            
            body = f"""
Security Incident {action.title()}

Incident ID: {incident.incident_id}
Title: {incident.title}
Severity: {incident.severity.value.upper()}
Category: {incident.category.value.replace('_', ' ').title()}
Status: {incident.status.value.replace('_', ' ').title()}
Reporter: {incident.reporter}
Detection Time: {datetime.fromtimestamp(incident.detection_time)}

Description:
{incident.description}

Affected Systems:
{', '.join(incident.affected_systems) if incident.affected_systems else 'None specified'}

This is an automated notification from the Syn_OS Incident Response System.
Please respond according to established procedures.
            """
            
            # Determine notification recipients based on severity
            recipients = []
            if incident.severity == IncidentSeverity.CRITICAL:
                recipients = self.notification_config["emergency_contacts"]
            elif incident.severity == IncidentSeverity.HIGH:
                recipients = ["security-team@synos.local"]
            else:
                recipients = ["security-team@synos.local"]
            
            # Send notifications (placeholder implementation)
            for recipient in recipients:
                self.logger.info(f"Sending notification to {recipient}: {subject}")
                # In a real implementation, this would send actual emails
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
    
    async def _check_escalation_rules(self, incident: SecurityIncident):
        """Check and apply escalation rules"""
        try:
            for rule in self.escalation_rules.values():
                should_escalate = False
                
                # Check conditions
                conditions = rule.conditions
                
                if "severity" in conditions and incident.severity.value == conditions["severity"]:
                    should_escalate = True
                
                if "category" in conditions and incident.category.value == conditions["category"]:
                    should_escalate = True
                
                if should_escalate and rule.auto_escalate:
                    await self._escalate_incident(incident, rule)
            
        except Exception as e:
            self.logger.error(f"Error checking escalation rules: {e}")
    
    async def _escalate_incident(self, incident: SecurityIncident, rule: EscalationRule):
        """Escalate incident according to rule"""
        try:
            incident.status = IncidentStatus.ESCALATED
            incident.last_modified = time.time()
            
            await self._store_incident(incident)
            
            # Send escalation notifications
            subject = f"[ESCALATED] {incident.severity.value.upper()} Incident: {incident.title}"
            body = f"""
INCIDENT ESCALATION NOTICE

Incident ID: {incident.incident_id}
Escalation Rule: {rule.name}
Escalation Time: {datetime.fromtimestamp(time.time())}

Original Details:
Title: {incident.title}
Severity: {incident.severity.value.upper()}
Category: {incident.category.value.replace('_', ' ').title()}
Detection Time: {datetime.fromtimestamp(incident.detection_time)}

This incident has been escalated according to established procedures.
Immediate attention required.
            """
            
            for target in rule.escalation_targets:
                self.logger.info(f"Escalating incident {incident.incident_id} to {target}")
                # In a real implementation, this would send actual notifications
            
            self.metrics["escalated_incidents"] += 1
            
        except Exception as e:
            self.logger.error(f"Error escalating incident: {e}")
    
    async def _sla_monitoring_task(self):
        """Background task to monitor SLA compliance"""
        while True:
            try:
                current_time = time.time()
                
                for incident in self.incidents.values():
                    if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
                        sla = self.sla_targets[incident.severity]
                        
                        # Check response SLA
                        if not incident.response_time:
                            response_elapsed = (current_time - incident.detection_time) / 60  # minutes
                            if response_elapsed > sla["response"]:
                                self.logger.warning(f"Incident {incident.incident_id} response SLA breach: {response_elapsed:.1f} minutes")
                        
                        # Check resolution SLA
                        if incident.response_time and not incident.resolution_time:
                            resolution_elapsed = (current_time - incident.detection_time) / 60  # minutes
                            if resolution_elapsed > sla["resolution"]:
                                self.logger.warning(f"Incident {incident.incident_id} resolution SLA breach: {resolution_elapsed:.1f} minutes")
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in SLA monitoring task: {e}")
                await asyncio.sleep(60)
    
    async def _escalation_monitoring_task(self):
        """Background task to monitor escalation conditions"""
        while True:
            try:
                current_time = time.time()
                
                for incident in self.incidents.values():
                    if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED, IncidentStatus.ESCALATED]:
                        # Check time-based escalation conditions
                        for rule in self.escalation_rules.values():
                            if "no_response_time" in rule.conditions:
                                if not incident.response_time:
                                    elapsed = (current_time - incident.detection_time) / 60  # minutes
                                    if elapsed >= rule.conditions["no_response_time"]:
                                        await self._escalate_incident(incident, rule)
                
                # Sleep for 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in escalation monitoring task: {e}")
                await asyncio.sleep(60)
    
    async def _store_incident(self, incident: SecurityIncident):
        """Store incident in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO incidents
                (incident_id, title, description, category, severity, status, reporter, assigned_to,
                 detection_time, reported_time, response_time, resolution_time, affected_systems,
                 indicators_of_compromise, evidence_collected, response_actions, lessons_learned,
                 root_cause, created_by, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.incident_id, incident.title, incident.description, incident.category.value,
                incident.severity.value, incident.status.value, incident.reporter, incident.assigned_to,
                incident.detection_time, incident.reported_time, incident.response_time, incident.resolution_time,
                json.dumps(incident.affected_systems), json.dumps(incident.indicators_of_compromise),
                json.dumps(incident.evidence_collected), json.dumps(incident.response_actions),
                incident.lessons_learned, incident.root_cause, incident.created_by, incident.last_modified
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing incident: {e}")
            raise
    
    async def _store_team_member(self, member: ResponseTeamMember):
        """Store team member in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO response_team
                (member_id, name, role, contact_email, contact_phone, expertise, availability_status, escalation_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                member.member_id, member.name, member.role, member.contact_email, member.contact_phone,
                json.dumps(member.expertise), member.availability_status, member.escalation_level
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing team member: {e}")
            raise
    
    async def _store_playbook(self, playbook: ResponsePlaybook):
        """Store playbook in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO playbooks
                (playbook_id, name, description, incident_types, severity_levels, response_steps,
                 required_roles, estimated_duration, success_criteria, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                playbook.playbook_id, playbook.name, playbook.description,
                json.dumps([t.value for t in playbook.incident_types]),
                json.dumps([s.value for s in playbook.severity_levels]),
                json.dumps(playbook.response_steps),
                json.dumps(playbook.required_roles),
                playbook.estimated_duration,
                json.dumps(playbook.success_criteria),
                playbook.created_date, playbook.last_updated
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing playbook: {e}")
            raise
    
    async def _store_escalation_rule(self, rule: EscalationRule):
        """Store escalation rule in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO escalation_rules
                (rule_id, name, conditions, escalation_targets, notification_methods, escalation_delay, auto_escalate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id, rule.name, json.dumps(rule.conditions),
                json.dumps(rule.escalation_targets), json.dumps(rule.notification_methods),
                rule.escalation_delay, rule.auto_escalate
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing escalation rule: {e}")
            raise
    
    async def update_incident(self, incident_id: str, **updates) -> bool:
        """Update incident with new information"""
        try:
            if incident_id not in self.incidents:
                self.logger.error(f"Incident {incident_id} not found")
                return False
            
            incident = self.incidents[incident_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(incident, field):
                    setattr(incident, field, value)
            
            incident.last_modified = time.time()
            
            # Store updated incident
            await self._store_incident(incident)
            
            # Send update notifications if status changed
            if 'status' in updates:
                await self._send_incident_notifications(incident, "updated")
            
            self.logger.info(f"Updated incident {incident_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating incident: {e}")
            return False
    
    async def resolve_incident(self, incident_id: str, resolution_notes: str, root_cause: str = "") -> bool:
        """Resolve incident"""
        try:
            if incident_id not in self.incidents:
                self.logger.error(f"Incident {incident_id} not found")
                return False
            
            incident = self.incidents[incident_id]
            incident.status = IncidentStatus.RESOLVED
            incident.resolution_time = time.time()
            incident.lessons_learned = resolution_notes
            incident.root_cause = root_cause
            incident.last_modified = time.time()
            
            await self._store_incident(incident)
            
            # Update metrics
            self.metrics["open_incidents"] -= 1
            if incident.severity == IncidentSeverity.CRITICAL:
                self.metrics["critical_incidents"] -= 1
            
            # Calculate response and resolution times for metrics
            if incident.response_time:
                response_time = (incident.response_time - incident.detection_time) / 60  # minutes
                self._update_average_response_time(response_time)
            
            resolution_time = (incident.resolution_time - incident.detection_time) / 60  # minutes
            self._update_average_resolution_time(resolution_time)
            
            await self._send_incident_notifications(incident, "resolved")
            
            self.logger.info(f"Resolved incident {incident_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving incident: {e}")
            return False
    
    def _update_average_response_time(self, response_time: float):
        """Update average response time metric"""
        current_avg = self.metrics["average_response_time"]
        total_incidents = self.metrics["total_incidents"]
        
        if total_incidents > 0:
            self.metrics["average_response_time"] = ((current_avg * (total_incidents - 1)) + response_time) / total_incidents
    
    def _update_average_resolution_time(self, resolution_time: float):
        """Update average resolution time metric"""
        current_avg = self.metrics["average_resolution_time"]
        total_incidents = self.metrics["total_incidents"]
        
        if total_incidents > 0:
            self.metrics["average_resolution_time"] = ((current_avg * (total_incidents - 1)) + resolution_time) / total_incidents
    
    async def get_incident_metrics(self) -> Dict[str, Any]:
        """Get incident response metrics"""
        try:
            # Calculate SLA compliance
            total_resolved = 0
            sla_compliant = 0
            
            for incident in self.incidents.values():
                if incident.status == IncidentStatus.RESOLVED and incident.resolution_time:
                    total_resolved += 1
                    resolution_time = (incident.resolution_time - incident.detection_time) / 60  # minutes
                    sla_target = self.sla_targets[incident.severity]["resolution"]
                    
                    if resolution_time <= sla_target:
                        sla_compliant += 1
            
            if total_resolved > 0:
                self.metrics["sla_compliance"] = (sla_compliant / total_resolved) * 100
            
            return self.metrics.copy()
            
        except Exception as e:
            self.logger.error(f"Error getting incident metrics: {e}")
            return {}
    
    async def get_incident_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident status and details"""
        try:
            if incident_id not in self.incidents:
                return None
            
            incident = self.incidents[incident_id]
            return {
                "incident_id": incident.incident_id,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "category": incident.category.value,
                "assigned_to": incident.assigned_to,
                "detection_time": datetime.fromtimestamp(incident.detection_time).isoformat(),
                "response_time": datetime.fromtimestamp(incident.response_time).isoformat() if incident.response_time else None,
                "resolution_time": datetime.fromtimestamp(incident.resolution_time).isoformat() if incident.resolution_time else None,
                "affected_systems": incident.affected_systems,
                "indicators_of_compromise": incident.indicators_of_compromise
            }
            
        except Exception as e:
            self.logger.error(f"Error getting incident status: {e}")
            return None
    
    async def list_active_incidents(self) -> List[Dict[str, Any]]:
        """List all active incidents"""
        try:
            active_incidents = []
            
            for incident in self.incidents.values():
                if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
                    incident_data = await self.get_incident_status(incident.incident_id)
                    if incident_data:
                        active_incidents.append(incident_data)
            
            # Sort by severity and detection time
            severity_order = {
                IncidentSeverity.CRITICAL.value: 0,
                IncidentSeverity.HIGH.value: 1,
                IncidentSeverity.MEDIUM.value: 2,
                IncidentSeverity.LOW.value: 3,
                IncidentSeverity.INFORMATIONAL.value: 4
            }
            
            active_incidents.sort(key=lambda x: (severity_order.get(x["severity"], 5), x["detection_time"]))
            
            return active_incidents
            
        except Exception as e:
            self.logger.error(f"Error listing active incidents: {e}")
            return []


# Example usage and testing
async def main():
    """Example usage of incident response procedures"""
    ir_system = IncidentResponseProcedures()
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Create test incident
    incident_id = await ir_system.create_incident(
        title="Suspicious Network Activity Detected",
        description="Unusual outbound connections detected from production server",
        category=IncidentCategory.SECURITY_BREACH,
        severity=IncidentSeverity.HIGH,
        reporter="security_analyst_001",
        affected_systems=["prod-web-01", "prod-db-01"],
        indicators=["192.168.1.100:443", "suspicious_process.exe"]
    )
    
    print(f"Created incident: {incident_id}")
    
    # Get incident status
    status = await ir_system.get_incident_status(incident_id)
    print(f"Incident status: {status}")
    
    # List active incidents
    active = await ir_system.list_active_incidents()
    print(f"Active incidents: {len(active)}")
    
    # Get metrics
    metrics = await ir_system.get_incident_metrics()
    print(f"Incident metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())