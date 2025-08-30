#!/usr/bin/env python3
"""
SIEM and Security Monitoring System
Comprehensive security information and event management for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
import uuid
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import queue
import subprocess


class EventSeverity(Enum):
    """Security event severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class EventCategory(Enum):
    """Security event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK_TRAFFIC = "network_traffic"
    SYSTEM_ACCESS = "system_access"
    FILE_ACCESS = "file_access"
    PROCESS_EXECUTION = "process_execution"
    MALWARE_DETECTION = "malware_detection"
    INTRUSION_DETECTION = "intrusion_detection"
    DATA_EXFILTRATION = "data_exfiltration"
    POLICY_VIOLATION = "policy_violation"
    CONFIGURATION_CHANGE = "configuration_change"
    VULNERABILITY_SCAN = "vulnerability_scan"


class AlertStatus(Enum):
    """Alert status definitions"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    timestamp: float
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    event_type: str
    category: EventCategory
    severity: EventSeverity
    description: str
    raw_log: str
    source_system: str
    user_id: Optional[str]
    process_name: Optional[str]
    file_path: Optional[str]
    command_line: Optional[str]
    hash_values: Dict[str, str]
    indicators_of_compromise: List[str]
    risk_score: float
    correlation_id: Optional[str]
    tags: List[str]


@dataclass
class SecurityAlert:
    """Security alert record"""
    alert_id: str
    title: str
    description: str
    severity: EventSeverity
    category: EventCategory
    status: AlertStatus
    created_time: float
    updated_time: float
    source_events: List[str]
    affected_assets: List[str]
    indicators_of_compromise: List[str]
    recommended_actions: List[str]
    assigned_analyst: Optional[str]
    false_positive_reason: Optional[str]
    resolution_notes: Optional[str]


@dataclass
class ThreatIntelligence:
    """Threat intelligence indicator"""
    indicator_id: str
    indicator_type: str  # ip, domain, hash, url, etc.
    indicator_value: str
    threat_type: str
    confidence_level: float
    severity: EventSeverity
    source: str
    first_seen: float
    last_seen: float
    description: str
    tags: List[str]
    ttl: int  # time to live in seconds


@dataclass
class CorrelationRule:
    """Event correlation rule"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    time_window: int  # seconds
    threshold: int
    severity: EventSeverity
    alert_template: Dict[str, str]
    enabled: bool
    created_time: float
    last_modified: float


class SIEMSecurityMonitoring:
    """
    SIEM and Security Monitoring System
    Comprehensive security event management and correlation
    """
    
    def __init__(self):
        """Initialize SIEM system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.siem_directory = "/var/lib/synos/siem"
        self.database_file = f"{self.siem_directory}/siem.db"
        self.logs_directory = f"{self.siem_directory}/logs"
        self.rules_directory = f"{self.siem_directory}/rules"
        
        # System components
        self.events: deque = deque(maxlen=100000)  # Recent events buffer
        self.alerts: Dict[str, SecurityAlert] = {}
        self.threat_intel: Dict[str, ThreatIntelligence] = {}
        self.correlation_rules: Dict[str, CorrelationRule] = {}
        
        # Event processing
        self.event_queue = queue.Queue()
        self.processing_threads = []
        self.correlation_engine_running = False
        
        # Monitoring configuration
        self.log_sources = {
            "/var/log/auth.log": {"category": EventCategory.AUTHENTICATION, "parser": "syslog"},
            "/var/log/syslog": {"category": EventCategory.SYSTEM_ACCESS, "parser": "syslog"},
            "/var/log/apache2/access.log": {"category": EventCategory.NETWORK_TRAFFIC, "parser": "apache"},
            "/var/log/nginx/access.log": {"category": EventCategory.NETWORK_TRAFFIC, "parser": "nginx"},
            "/var/log/fail2ban.log": {"category": EventCategory.INTRUSION_DETECTION, "parser": "fail2ban"}
        }
        
        # Threat intelligence feeds
        self.threat_feeds = {
            "malware_domains": "https://mirror1.malwaredomains.com/files/justdomains",
            "abuse_ch": "https://feodotracker.abuse.ch/downloads/ipblocklist.txt",
            "emergingthreats": "https://rules.emergingthreats.net/open/suricata/rules/emerging-compromised.rules"
        }
        
        # System metrics
        self.metrics = {
            "events_processed": 0,
            "alerts_generated": 0,
            "false_positives": 0,
            "events_per_second": 0.0,
            "correlation_rules_triggered": 0,
            "threat_intel_matches": 0,
            "system_uptime": time.time()
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_siem())
    
    async def _initialize_siem(self):
        """Initialize SIEM system"""
        try:
            self.logger.info("Initializing SIEM security monitoring...")
            
            # Create directories
            os.makedirs(self.siem_directory, exist_ok=True)
            os.makedirs(self.logs_directory, exist_ok=True)
            os.makedirs(self.rules_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load threat intelligence
            await self._load_threat_intelligence()
            
            # Deploy correlation rules
            await self._deploy_correlation_rules()
            
            # Start monitoring services
            await self._start_log_monitoring()
            await self._start_correlation_engine()
            await self._start_threat_intel_updates()
            
            self.logger.info("SIEM security monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing SIEM: {e}")
    
    async def _initialize_database(self):
        """Initialize SIEM database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    source_ip TEXT,
                    destination_ip TEXT,
                    source_port INTEGER,
                    destination_port INTEGER,
                    protocol TEXT,
                    event_type TEXT,
                    category TEXT,
                    severity TEXT,
                    description TEXT,
                    raw_log TEXT,
                    source_system TEXT,
                    user_id TEXT,
                    process_name TEXT,
                    file_path TEXT,
                    command_line TEXT,
                    hash_values TEXT,
                    indicators_of_compromise TEXT,
                    risk_score REAL,
                    correlation_id TEXT,
                    tags TEXT
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    alert_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT,
                    category TEXT,
                    status TEXT,
                    created_time REAL,
                    updated_time REAL,
                    source_events TEXT,
                    affected_assets TEXT,
                    indicators_of_compromise TEXT,
                    recommended_actions TEXT,
                    assigned_analyst TEXT,
                    false_positive_reason TEXT,
                    resolution_notes TEXT
                )
            ''')
            
            # Threat intelligence table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_intelligence (
                    indicator_id TEXT PRIMARY KEY,
                    indicator_type TEXT,
                    indicator_value TEXT,
                    threat_type TEXT,
                    confidence_level REAL,
                    severity TEXT,
                    source TEXT,
                    first_seen REAL,
                    last_seen REAL,
                    description TEXT,
                    tags TEXT,
                    ttl INTEGER
                )
            ''')
            
            # Correlation rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS correlation_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    conditions TEXT,
                    time_window INTEGER,
                    threshold INTEGER,
                    severity TEXT,
                    alert_template TEXT,
                    enabled BOOLEAN,
                    created_time REAL,
                    last_modified REAL
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON security_events (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source_ip ON security_events (source_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON security_alerts (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON security_alerts (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_intel_value ON threat_intelligence (indicator_value)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing SIEM database: {e}")
            raise
    
    async def _load_threat_intelligence(self):
        """Load threat intelligence indicators"""
        try:
            # Load built-in threat indicators
            builtin_indicators = [
                ThreatIntelligence(
                    indicator_id="TI-001",
                    indicator_type="ip",
                    indicator_value="192.168.1.100",
                    threat_type="malware_c2",
                    confidence_level=0.9,
                    severity=EventSeverity.HIGH,
                    source="internal_analysis",
                    first_seen=time.time(),
                    last_seen=time.time(),
                    description="Known malware command and control server",
                    tags=["malware", "c2", "botnet"],
                    ttl=86400  # 24 hours
                ),
                ThreatIntelligence(
                    indicator_id="TI-002",
                    indicator_type="domain",
                    indicator_value="malicious-domain.com",
                    threat_type="phishing",
                    confidence_level=0.95,
                    severity=EventSeverity.HIGH,
                    source="threat_feed",
                    first_seen=time.time(),
                    last_seen=time.time(),
                    description="Known phishing domain",
                    tags=["phishing", "credential_theft"],
                    ttl=172800  # 48 hours
                ),
                ThreatIntelligence(
                    indicator_id="TI-003",
                    indicator_type="hash",
                    indicator_value="d41d8cd98f00b204e9800998ecf8427e",
                    threat_type="malware",
                    confidence_level=0.85,
                    severity=EventSeverity.CRITICAL,
                    source="malware_analysis",
                    first_seen=time.time(),
                    last_seen=time.time(),
                    description="Known malware hash",
                    tags=["malware", "trojan"],
                    ttl=604800  # 1 week
                )
            ]
            
            for indicator in builtin_indicators:
                await self._store_threat_intelligence(indicator)
                self.threat_intel[indicator.indicator_value] = indicator
            
            self.logger.info(f"Loaded {len(builtin_indicators)} threat intelligence indicators")
            
        except Exception as e:
            self.logger.error(f"Error loading threat intelligence: {e}")
    
    async def _deploy_correlation_rules(self):
        """Deploy correlation rules"""
        try:
            current_time = time.time()
            
            correlation_rules = [
                CorrelationRule(
                    rule_id="CR-001",
                    name="Multiple Failed Login Attempts",
                    description="Detect multiple failed login attempts from same source",
                    conditions={
                        "event_type": "authentication_failure",
                        "field": "source_ip",
                        "operator": "count"
                    },
                    time_window=300,  # 5 minutes
                    threshold=5,
                    severity=EventSeverity.MEDIUM,
                    alert_template={
                        "title": "Multiple Failed Login Attempts Detected",
                        "description": "Multiple failed login attempts from {source_ip}",
                        "recommended_actions": "Block source IP, Investigate user account, Check for credential stuffing"
                    },
                    enabled=True,
                    created_time=current_time,
                    last_modified=current_time
                ),
                CorrelationRule(
                    rule_id="CR-002",
                    name="Suspicious Process Execution",
                    description="Detect execution of suspicious processes",
                    conditions={
                        "event_type": "process_execution",
                        "field": "process_name",
                        "operator": "contains",
                        "values": ["powershell.exe", "cmd.exe", "nc.exe", "ncat.exe"]
                    },
                    time_window=60,  # 1 minute
                    threshold=1,
                    severity=EventSeverity.HIGH,
                    alert_template={
                        "title": "Suspicious Process Execution",
                        "description": "Suspicious process {process_name} executed by {user_id}",
                        "recommended_actions": "Investigate process, Check parent process, Analyze command line"
                    },
                    enabled=True,
                    created_time=current_time,
                    last_modified=current_time
                ),
                CorrelationRule(
                    rule_id="CR-003",
                    name="Data Exfiltration Pattern",
                    description="Detect potential data exfiltration based on network traffic",
                    conditions={
                        "event_type": "network_connection",
                        "field": "bytes_out",
                        "operator": "greater_than",
                        "value": 10485760  # 10MB
                    },
                    time_window=600,  # 10 minutes
                    threshold=3,
                    severity=EventSeverity.CRITICAL,
                    alert_template={
                        "title": "Potential Data Exfiltration Detected",
                        "description": "Large data transfer to {destination_ip}",
                        "recommended_actions": "Block connection, Investigate data transfer, Check file access logs"
                    },
                    enabled=True,
                    created_time=current_time,
                    last_modified=current_time
                )
            ]
            
            for rule in correlation_rules:
                await self._store_correlation_rule(rule)
                self.correlation_rules[rule.rule_id] = rule
                
                # Save rule as JSON file
                rule_file = f"{self.rules_directory}/{rule.rule_id}_{rule.name.replace(' ', '_')}.json"
                with open(rule_file, 'w') as f:
                    json.dump(asdict(rule), f, indent=2, default=str)
            
            self.logger.info(f"Deployed {len(correlation_rules)} correlation rules")
            
        except Exception as e:
            self.logger.error(f"Error deploying correlation rules: {e}")
    
    async def _start_log_monitoring(self):
        """Start log file monitoring"""
        try:
            # Start event processing threads
            for i in range(3):  # 3 processing threads
                thread = threading.Thread(target=self._event_processing_worker, daemon=True)
                thread.start()
                self.processing_threads.append(thread)
            
            # Start log file watchers
            asyncio.create_task(self._monitor_log_files())
            
            self.logger.info("Started log monitoring services")
            
        except Exception as e:
            self.logger.error(f"Error starting log monitoring: {e}")
    
    async def _start_correlation_engine(self):
        """Start event correlation engine"""
        try:
            self.correlation_engine_running = True
            asyncio.create_task(self._correlation_engine_task())
            
            self.logger.info("Started correlation engine")
            
        except Exception as e:
            self.logger.error(f"Error starting correlation engine: {e}")
    
    async def _start_threat_intel_updates(self):
        """Start threat intelligence updates"""
        try:
            asyncio.create_task(self._threat_intel_update_task())
            
            self.logger.info("Started threat intelligence updates")
            
        except Exception as e:
            self.logger.error(f"Error starting threat intel updates: {e}")
    
    def _event_processing_worker(self):
        """Event processing worker thread"""
        while True:
            try:
                event_data = self.event_queue.get(timeout=1)
                if event_data is None:  # Shutdown signal
                    break
                
                # Parse and process event
                event = self._parse_log_entry(event_data)
                if event:
                    # Store event
                    asyncio.run(self._store_security_event(event))
                    
                    # Add to recent events buffer
                    self.events.append(event)
                    
                    # Check against threat intelligence
                    self._check_threat_intelligence(event)
                    
                    # Update metrics
                    self.metrics["events_processed"] += 1
                
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in event processing worker: {e}")
    
    async def _monitor_log_files(self):
        """Monitor log files for new entries"""
        file_positions = {}
        
        while True:
            try:
                for log_file, config in self.log_sources.items():
                    if os.path.exists(log_file):
                        # Get current file size
                        current_size = os.path.getsize(log_file)
                        last_position = file_positions.get(log_file, 0)
                        
                        if current_size > last_position:
                            # Read new content
                            with open(log_file, 'r') as f:
                                f.seek(last_position)
                                new_lines = f.readlines()
                                file_positions[log_file] = f.tell()
                            
                            # Queue new log entries for processing
                            for line in new_lines:
                                if line.strip():
                                    self.event_queue.put({
                                        "log_file": log_file,
                                        "category": config["category"],
                                        "parser": config["parser"],
                                        "raw_log": line.strip(),
                                        "timestamp": time.time()
                                    })
                
                # Sleep for 1 second
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error monitoring log files: {e}")
                await asyncio.sleep(5)
    
    def _parse_log_entry(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Parse log entry into security event"""
        try:
            parser = event_data["parser"]
            raw_log = event_data["raw_log"]
            category = event_data["category"]
            
            # Basic event structure
            event = SecurityEvent(
                event_id=f"EVT-{int(time.time())}-{str(uuid.uuid4())[:8]}",
                timestamp=event_data["timestamp"],
                source_ip="",
                destination_ip="",
                source_port=0,
                destination_port=0,
                protocol="",
                event_type="",
                category=category,
                severity=EventSeverity.INFORMATIONAL,
                description="",
                raw_log=raw_log,
                source_system=event_data["log_file"],
                user_id=None,
                process_name=None,
                file_path=None,
                command_line=None,
                hash_values={},
                indicators_of_compromise=[],
                risk_score=0.0,
                correlation_id=None,
                tags=[]
            )
            
            # Parser-specific logic
            if parser == "syslog":
                event = self._parse_syslog(event, raw_log)
            elif parser == "apache":
                event = self._parse_apache_log(event, raw_log)
            elif parser == "nginx":
                event = self._parse_nginx_log(event, raw_log)
            elif parser == "fail2ban":
                event = self._parse_fail2ban_log(event, raw_log)
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error parsing log entry: {e}")
            return None
    
    def _parse_syslog(self, event: SecurityEvent, raw_log: str) -> SecurityEvent:
        """Parse syslog format"""
        try:
            # Extract basic syslog components
            if "authentication failure" in raw_log.lower():
                event.event_type = "authentication_failure"
                event.severity = EventSeverity.MEDIUM
                event.description = "Authentication failure detected"
                
                # Extract IP address if present
                ip_match = re.search(r'rhost=(\d+\.\d+\.\d+\.\d+)', raw_log)
                if ip_match:
                    event.source_ip = ip_match.group(1)
                    event.indicators_of_compromise.append(event.source_ip)
                
                # Extract username if present
                user_match = re.search(r'user=(\w+)', raw_log)
                if user_match:
                    event.user_id = user_match.group(1)
                
                event.risk_score = 3.0
                event.tags = ["authentication", "failure"]
            
            elif "sudo" in raw_log.lower():
                event.event_type = "privilege_escalation"
                event.severity = EventSeverity.LOW
                event.description = "Sudo command executed"
                event.risk_score = 1.0
                event.tags = ["sudo", "privilege"]
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error parsing syslog: {e}")
            return event
    
    def _parse_apache_log(self, event: SecurityEvent, raw_log: str) -> SecurityEvent:
        """Parse Apache access log format"""
        try:
            # Common Log Format: IP - - [timestamp] "method path protocol" status size
            parts = raw_log.split()
            if len(parts) >= 7:
                event.source_ip = parts[0]
                event.event_type = "http_request"
                
                # Extract HTTP method and path
                if '"' in raw_log:
                    request_match = re.search(r'"([A-Z]+) ([^\s]+) HTTP/[\d\.]+"', raw_log)
                    if request_match:
                        method = request_match.group(1)
                        path = request_match.group(2)
                        event.description = f"{method} request to {path}"
                        
                        # Check for suspicious patterns
                        if any(pattern in path.lower() for pattern in ['../', 'etc/passwd', 'cmd=', 'exec=']):
                            event.severity = EventSeverity.HIGH
                            event.risk_score = 7.0
                            event.tags = ["web_attack", "injection"]
                            event.indicators_of_compromise.append(event.source_ip)
                        else:
                            event.severity = EventSeverity.INFORMATIONAL
                            event.risk_score = 0.5
                            event.tags = ["web_traffic"]
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error parsing Apache log: {e}")
            return event
    
    def _parse_nginx_log(self, event: SecurityEvent, raw_log: str) -> SecurityEvent:
        """Parse Nginx access log format"""
        try:
            # Similar to Apache but with slight format differences
            return self._parse_apache_log(event, raw_log)
            
        except Exception as e:
            self.logger.error(f"Error parsing Nginx log: {e}")
            return event
    
    def _parse_fail2ban_log(self, event: SecurityEvent, raw_log: str) -> SecurityEvent:
        """Parse Fail2ban log format"""
        try:
            if "ban" in raw_log.lower():
                event.event_type = "ip_banned"
                event.severity = EventSeverity.MEDIUM
                event.description = "IP address banned by Fail2ban"
                
                # Extract banned IP
                ip_match = re.search(r'Ban (\d+\.\d+\.\d+\.\d+)', raw_log)
                if ip_match:
                    event.source_ip = ip_match.group(1)
                    event.indicators_of_compromise.append(event.source_ip)
                
                event.risk_score = 4.0
                event.tags = ["fail2ban", "banned_ip"]
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error parsing Fail2ban log: {e}")
            return event
    
    def _check_threat_intelligence(self, event: SecurityEvent):
        """Check event against threat intelligence"""
        try:
            indicators_to_check = []
            
            # Collect indicators from event
            if event.source_ip:
                indicators_to_check.append(event.source_ip)
            if event.destination_ip:
                indicators_to_check.append(event.destination_ip)
            
            # Add any IOCs from the event
            indicators_to_check.extend(event.indicators_of_compromise)
            
            # Check against threat intelligence
            for indicator in indicators_to_check:
                if indicator in self.threat_intel:
                    threat_info = self.threat_intel[indicator]
                    
                    # Increase event severity and risk score
                    if threat_info.severity == EventSeverity.CRITICAL:
                        event.severity = EventSeverity.CRITICAL
                        event.risk_score += 8.0
                    elif threat_info.severity == EventSeverity.HIGH:
                        event.severity = EventSeverity.HIGH
                        event.risk_score += 6.0
                    
                    # Add threat intelligence tags
                    event.tags.extend(threat_info.tags)
                    event.tags.append("threat_intel_match")
                    
                    # Update metrics
                    self.metrics["threat_intel_matches"] += 1
                    
                    self.logger.warning(f"Threat intelligence match: {indicator} - {threat_info.description}")
            
        except Exception as e:
            self.logger.error(f"Error checking threat intelligence: {e}")
    
    async def _correlation_engine_task(self):
        """Correlation engine background task"""
        while self.correlation_engine_running:
            try:
                current_time = time.time()
                
                # Process each correlation rule
                for rule in self.correlation_rules.values():
                    if rule.enabled:
                        await self._process_correlation_rule(rule, current_time)
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in correlation engine: {e}")
                await asyncio.sleep(60)
    
    async def _process_correlation_rule(self, rule: CorrelationRule, current_time: float):
        """Process a single correlation rule"""
        try:
            # Get events within time window
            time_threshold = current_time - rule.time_window
            relevant_events = [
                event for event in self.events
                if event.timestamp >= time_threshold
            ]
            
            # Apply rule conditions
            matching_events = []
            conditions = rule.conditions
            
            for event in relevant_events:
                if self._event_matches_conditions(event, conditions):
                    matching_events.append(event)
            
            # Check if threshold is met
            if len(matching_events) >= rule.threshold:
                # Generate alert
                await self._generate_correlation_alert(rule, matching_events)
                
                # Update metrics
                self.metrics["correlation_rules_triggered"] += 1
            
        except Exception as e:
            self.logger.error(f"Error processing correlation rule {rule.rule_id}: {e}")
    
    def _event_matches_conditions(self, event: SecurityEvent, conditions: Dict[str, Any]) -> bool:
        """Check if event matches rule conditions"""
        try:
            if "event_type" in conditions:
                if event.event_type != conditions["event_type"]:
                    return False
            
            if "category" in conditions:
                if event.category.value != conditions["category"]:
                    return False
            
            if "severity" in conditions:
                if event.severity.value != conditions["severity"]:
                    return False
            
            # Field-specific conditions
            if "field" in conditions and "operator" in conditions:
                field = conditions["field"]
                operator = conditions["operator"]
                
                field_value = getattr(event, field, None)
                if field_value is None:
                    return False
                
                if operator == "contains" and "values" in conditions:
                    return any(value in str(field_value).lower() for value in conditions["values"])
                elif operator == "equals" and "value" in conditions:
                    return str(field_value) == str(conditions["value"])
                elif operator == "greater_than" and "value" in conditions:
                    return float(field_value) > float(conditions["value"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error matching event conditions: {e}")
            return False
    
    async def _generate_correlation_alert(self, rule: CorrelationRule, events: List[SecurityEvent]):
        """Generate alert from correlation rule"""
        try:
            current_time = time.time()
            alert_id = f"ALT-{int(current_time)}-{str(uuid.uuid4())[:8]}"
            
            # Build alert from template
            template = rule.alert_template
            
            # Extract common values from events
            source_ips = list(set([event.source_ip for event in events if event.source_ip]))
            affected_systems = list(set([event.source_system for event in events]))
            
            # Format alert title and description
            title = template.get("title", f"Correlation Alert: {rule.name}")
            description = template.get("description", f"Rule {rule.name} triggered")
            
            # Replace placeholders
            if source_ips:
                title = title.replace("{source_ip}", source_ips[0])
                description = description.replace("{source_ip}", source_ips[0])
            
            if events and events[0].process_name:
                title = title.replace("{process_name}", events[0].process_name)
                description = description.replace("{process_name}", events[0].process_name)
            
            if events and events[0].user_id:
                title = title.replace("{user_id}", events[0].user_id)
                description = description.replace("{user_id}", events[0].user_id)
            
            if events and events[0].destination_ip:
                title = title.replace("{destination_ip}", events[0].destination_ip)
                description = description.replace("{destination_ip}", events[0].destination_ip)
            
            # Create alert
            alert = SecurityAlert(
                alert_id=alert_id,
                title=title,
                description=description,
                severity=rule.severity,
                category=events[0].category if events else EventCategory.INTRUSION_DETECTION,
                status=AlertStatus.NEW,
                created_time=current_time,
                updated_time=current_time,
                source_events=[event.event_id for event in events],
                affected_assets=affected_systems,
                indicators_of_compromise=list(set([ioc for event in events for ioc in event.indicators_of_compromise])),
                recommended_actions=template.get("recommended_actions", "Investigate alert").split(", "),
                assigned_analyst=None,
                false_positive_reason=None,
                resolution_notes=None
            )
            
            # Store alert
            await self._store_security_alert(alert)
            self.alerts[alert_id] = alert
            
            # Update metrics
            self.metrics["alerts_generated"] += 1
            
            self.logger.warning(f"Generated correlation alert: {alert_id} - {title}")
            
        except Exception as e:
            self.logger.error(f"Error generating correlation alert: {e}")
    
    async def _threat_intel_update_task(self):
        """Background task to update threat intelligence"""
        while True:
            try:
                # Update threat intelligence every 4 hours
                await asyncio.sleep(14400)
                
                # Remove expired indicators
                current_time = time.time()
                expired_indicators = []
                
                for indicator_value, threat_info in self.threat_intel.items():
                    if current_time - threat_info.first_seen > threat_info.ttl:
                        expired_indicators.append(indicator_value)
                
                for indicator in expired_indicators:
                    del self.threat_intel[indicator]
                    self.logger.info(f"Removed expired threat intelligence: {indicator}")
                
                self.logger.info(f"Threat intelligence update complete. Active indicators: {len(self.threat_intel)}")
                
            except Exception as e:
                self.logger.error(f"Error in threat intelligence update: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _store_security_event(self, event: SecurityEvent):
        """Store security event in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_events
                (event_id, timestamp, source_ip, destination_ip, source_port, destination_port,
                 protocol, event_type, category, severity, description, raw_log, source_system,
                 user_id, process_name, file_path, command_line, hash_values,
                 indicators_of_compromise, risk_score, correlation_id, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id, event.timestamp, event.source_ip, event.destination_ip,
                event.source_port, event.destination_port, event.protocol, event.event_type,
                event.category.value, event.severity.value, event.description, event.raw_log,
                event.source_system, event.user_id, event.process_name, event.file_path,
                event.command_line, json.dumps(event.hash_values),
                json.dumps(event.indicators_of_compromise), event.risk_score,
                event.correlation_id, json.dumps(event.tags)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing security event: {e}")
            raise
    
    async def _store_security_alert(self, alert: SecurityAlert):
        """Store security alert in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_alerts
                (alert_id, title, description, severity, category, status, created_time,
                 updated_time, source_events, affected_assets, indicators_of_compromise,
                 recommended_actions, assigned_analyst, false_positive_reason, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id, alert.title, alert.description, alert.severity.value,
                alert.category.value, alert.status.value, alert.created_time, alert.updated_time,
                json.dumps(alert.source_events), json.dumps(alert.affected_assets),
                json.dumps(alert.indicators_of_compromise), json.dumps(alert.recommended_actions),
                alert.assigned_analyst, alert.false_positive_reason, alert.resolution_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing security alert: {e}")
            raise
    
    async def _store_threat_intelligence(self, threat_info: ThreatIntelligence):
        """Store threat intelligence in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_intelligence
                (indicator_id, indicator_type, indicator_value, threat_type, confidence_level,
                 severity, source, first_seen, last_seen, description, tags, ttl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                threat_info.indicator_id, threat_info.indicator_type, threat_info.indicator_value,
                threat_info.threat_type, threat_info.confidence_level, threat_info.severity.value,
                threat_info.source, threat_info.first_seen, threat_info.last_seen,
                threat_info.description, json.dumps(threat_info.tags), threat_info.ttl
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing threat intelligence: {e}")
            raise
    
    async def _store_correlation_rule(self, rule: CorrelationRule):
        """Store correlation rule in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO correlation_rules
                (rule_id, name, description, conditions, time_window, threshold, severity,
                 alert_template, enabled, created_time, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id, rule.name, rule.description, json.dumps(rule.conditions),
                rule.time_window, rule.threshold, rule.severity.value,
                json.dumps(rule.alert_template), rule.enabled, rule.created_time, rule.last_modified
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing correlation rule: {e}")
            raise
    
    async def create_manual_event(self, event_type: str, category: EventCategory, severity: EventSeverity,
                                description: str, source_ip: str = "", **kwargs) -> str:
        """Create manual security event"""
        try:
            current_time = time.time()
            
            event = SecurityEvent(
                event_id=f"EVT-{int(current_time)}-{str(uuid.uuid4())[:8]}",
                timestamp=current_time,
                source_ip=source_ip,
                destination_ip=kwargs.get("destination_ip", ""),
                source_port=kwargs.get("source_port", 0),
                destination_port=kwargs.get("destination_port", 0),
                protocol=kwargs.get("protocol", ""),
                event_type=event_type,
                category=category,
                severity=severity,
                description=description,
                raw_log=kwargs.get("raw_log", "Manual event creation"),
                source_system=kwargs.get("source_system", "manual"),
                user_id=kwargs.get("user_id"),
                process_name=kwargs.get("process_name"),
                file_path=kwargs.get("file_path"),
                command_line=kwargs.get("command_line"),
                hash_values=kwargs.get("hash_values", {}),
                indicators_of_compromise=kwargs.get("indicators_of_compromise", []),
                risk_score=kwargs.get("risk_score", 1.0),
                correlation_id=None,
                tags=kwargs.get("tags", [])
            )
            
            # Store event
            await self._store_security_event(event)
            self.events.append(event)
            
            # Check against threat intelligence
            self._check_threat_intelligence(event)
            
            # Update metrics
            self.metrics["events_processed"] += 1
            
            self.logger.info(f"Created manual security event: {event.event_id}")
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Error creating manual event: {e}")
            raise
    
    async def get_siem_metrics(self) -> Dict[str, Any]:
        """Get SIEM system metrics"""
        try:
            current_time = time.time()
            uptime = current_time - self.metrics["system_uptime"]
            
            # Calculate events per second
            if uptime > 0:
                self.metrics["events_per_second"] = self.metrics["events_processed"] / uptime
            
            return {
                **self.metrics,
                "uptime_hours": uptime / 3600,
                "active_alerts": len([alert for alert in self.alerts.values() if alert.status == AlertStatus.NEW]),
                "total_alerts": len(self.alerts),
                "threat_intel_indicators": len(self.threat_intel),
                "correlation_rules": len(self.correlation_rules),
                "recent_events": len(self.events)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SIEM metrics: {e}")
            return {}
    
    async def get_recent_events(self, limit: int = 100, severity_filter: Optional[EventSeverity] = None) -> List[Dict[str, Any]]:
        """Get recent security events"""
        try:
            events = list(self.events)
            
            # Apply severity filter
            if severity_filter:
                events = [event for event in events if event.severity == severity_filter]
            
            # Sort by timestamp (most recent first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Limit results
            events = events[:limit]
            
            # Convert to dict format
            result = []
            for event in events:
                result.append({
                    "event_id": event.event_id,
                    "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
                    "event_type": event.event_type,
                    "category": event.category.value,
                    "severity": event.severity.value,
                    "description": event.description,
                    "source_ip": event.source_ip,
                    "destination_ip": event.destination_ip,
                    "source_system": event.source_system,
                    "risk_score": event.risk_score,
                    "tags": event.tags
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
            return []
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active security alerts"""
        try:
            active_alerts = []
            
            for alert in self.alerts.values():
                if alert.status in [AlertStatus.NEW, AlertStatus.INVESTIGATING]:
                    active_alerts.append({
                        "alert_id": alert.alert_id,
                        "title": alert.title,
                        "description": alert.description,
                        "severity": alert.severity.value,
                        "category": alert.category.value,
                        "status": alert.status.value,
                        "created_time": datetime.fromtimestamp(alert.created_time).isoformat(),
                        "affected_assets": alert.affected_assets,
                        "indicators_of_compromise": alert.indicators_of_compromise,
                        "recommended_actions": alert.recommended_actions,
                        "assigned_analyst": alert.assigned_analyst
                    })
            
            # Sort by severity and creation time
            severity_order = {
                EventSeverity.CRITICAL.value: 0,
                EventSeverity.HIGH.value: 1,
                EventSeverity.MEDIUM.value: 2,
                EventSeverity.LOW.value: 3,
                EventSeverity.INFORMATIONAL.value: 4
            }
            
            active_alerts.sort(key=lambda x: (severity_order.get(x["severity"], 5), x["created_time"]))
            
            return active_alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []


# Example usage and testing
async def main():
    """Example usage of SIEM security monitoring"""
    siem_system = SIEMSecurityMonitoring()
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Create test event
    event_id = await siem_system.create_manual_event(
        event_type="authentication_failure",
        category=EventCategory.AUTHENTICATION,
        severity=EventSeverity.MEDIUM,
        description="Failed login attempt",
        source_ip="192.168.1.100",
        user_id="testuser",
        tags=["authentication", "failure"]
    )
    
    print(f"Created test event: {event_id}")
    
    # Get recent events
    recent_events = await siem_system.get_recent_events(limit=10)
    print(f"Recent events: {len(recent_events)}")
    
    # Get active alerts
    active_alerts = await siem_system.get_active_alerts()
    print(f"Active alerts: {len(active_alerts)}")
    
    # Get metrics
    metrics = await siem_system.get_siem_metrics()
    print(f"SIEM metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())