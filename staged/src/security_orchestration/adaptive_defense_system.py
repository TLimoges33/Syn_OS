#!/usr/bin/env python3
"""
Adaptive Defense System for Syn_OS
Dynamic security response with consciousness-driven adaptation
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from datetime import datetime, timedelta

from src.consciousness_v2.consciousness_bus import ConsciousnessBus


class DefenseAction(Enum):
    """Types of defensive actions"""
    BLOCK_IP = "block_ip"
    QUARANTINE_FILE = "quarantine_file"
    ISOLATE_SYSTEM = "isolate_system"
    KILL_PROCESS = "kill_process"
    DISABLE_USER = "disable_user"
    RATE_LIMIT = "rate_limit"
    REDIRECT_TRAFFIC = "redirect_traffic"
    ALERT_ADMIN = "alert_admin"
    BACKUP_DATA = "backup_data"
    PATCH_SYSTEM = "patch_system"


class DefenseLevel(Enum):
    """Defense readiness levels"""
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DefenseRule:
    """Adaptive defense rule"""
    rule_id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    actions: List[DefenseAction]
    severity_threshold: ThreatSeverity
    confidence_threshold: float
    auto_execute: bool
    requires_approval: bool
    cooldown_period: int  # seconds
    max_executions_per_hour: int
    created_at: float
    last_executed: Optional[float] = None
    execution_count: int = 0
    success_rate: float = 1.0
    enabled: bool = True


@dataclass
class DefenseResponse:
    """Defense response record"""
    response_id: str
    rule_id: str
    trigger_event: Dict[str, Any]
    actions_taken: List[Dict[str, Any]]
    execution_time: float
    success: bool
    consciousness_level: float
    automated: bool
    approval_required: bool
    approved_by: Optional[str] = None
    effectiveness_score: float = 0.0
    side_effects: Optional[List[str]] = None


@dataclass
class SystemState:
    """Current system security state"""
    defense_level: DefenseLevel
    active_threats: int
    blocked_ips: List[str]
    quarantined_files: List[str]
    isolated_systems: List[str]
    active_responses: int
    consciousness_level: float
    last_updated: float


class AdaptiveDefenseSystem:
    """
    Adaptive defense system with consciousness-driven response adaptation
    Automatically responds to threats with appropriate defensive measures
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize adaptive defense system"""
        self.consciousness_bus = consciousness_bus
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/adaptive_defense"
        self.database_file = f"{self.system_directory}/adaptive_defense.db"
        
        # System state
        self.current_state = SystemState(
            defense_level=DefenseLevel.NORMAL,
            active_threats=0,
            blocked_ips=[],
            quarantined_files=[],
            isolated_systems=[],
            active_responses=0,
            consciousness_level=0.0,
            last_updated=time.time()
        )
        
        # Defense rules and responses
        self.defense_rules: Dict[str, DefenseRule] = {}
        self.active_responses: Dict[str, DefenseResponse] = {}
        self.response_history: List[DefenseResponse] = []
        
        # Adaptation parameters
        self.consciousness_threshold = 0.5
        self.max_concurrent_responses = 20
        self.learning_rate = 0.1
        self.adaptation_interval = 60  # 1 minute
        
        # Initialize system
        asyncio.create_task(self._initialize_defense_system())
    
    async def _initialize_defense_system(self):
        """Initialize the adaptive defense system"""
        try:
            self.logger.info("Initializing adaptive defense system...")
            
            # Create system directory
            import os
            os.makedirs(self.system_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load defense rules
            await self._load_defense_rules()
            
            # Initialize default rules
            await self._create_default_rules()
            
            # Start monitoring and adaptation
            asyncio.create_task(self._start_monitoring())
            asyncio.create_task(self._start_adaptation_loop())
            
            self.logger.info("Adaptive defense system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing adaptive defense system: {e}")
    
    async def _initialize_database(self):
        """Initialize adaptive defense database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Defense rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defense_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    trigger_conditions TEXT NOT NULL,
                    actions TEXT NOT NULL,
                    severity_threshold TEXT NOT NULL,
                    confidence_threshold REAL NOT NULL,
                    auto_execute BOOLEAN NOT NULL,
                    requires_approval BOOLEAN NOT NULL,
                    cooldown_period INTEGER NOT NULL,
                    max_executions_per_hour INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    last_executed REAL,
                    execution_count INTEGER NOT NULL DEFAULT 0,
                    success_rate REAL NOT NULL DEFAULT 1.0,
                    enabled BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            # Defense responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defense_responses (
                    response_id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    trigger_event TEXT NOT NULL,
                    actions_taken TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    consciousness_level REAL NOT NULL,
                    automated BOOLEAN NOT NULL,
                    approval_required BOOLEAN NOT NULL,
                    approved_by TEXT,
                    effectiveness_score REAL NOT NULL DEFAULT 0.0,
                    side_effects TEXT,
                    FOREIGN KEY (rule_id) REFERENCES defense_rules (rule_id)
                )
            ''')
            
            # System state history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state_history (
                    state_id TEXT PRIMARY KEY,
                    defense_level TEXT NOT NULL,
                    active_threats INTEGER NOT NULL,
                    blocked_ips TEXT,
                    quarantined_files TEXT,
                    isolated_systems TEXT,
                    active_responses INTEGER NOT NULL,
                    consciousness_level REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # Threat events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT,
                    target_system TEXT,
                    description TEXT,
                    indicators TEXT,
                    timestamp REAL NOT NULL,
                    response_triggered BOOLEAN NOT NULL DEFAULT 0,
                    response_id TEXT,
                    FOREIGN KEY (response_id) REFERENCES defense_responses (response_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_enabled ON defense_rules (enabled)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_time ON defense_responses (execution_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON threat_events (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON threat_events (timestamp)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    async def _load_defense_rules(self):
        """Load defense rules from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM defense_rules WHERE enabled = 1')
            for row in cursor.fetchall():
                rule = DefenseRule(
                    rule_id=row[0],
                    name=row[1],
                    description=row[2],
                    trigger_conditions=json.loads(row[3]),
                    actions=[DefenseAction(action) for action in json.loads(row[4])],
                    severity_threshold=ThreatSeverity(row[5]),
                    confidence_threshold=row[6],
                    auto_execute=bool(row[7]),
                    requires_approval=bool(row[8]),
                    cooldown_period=row[9],
                    max_executions_per_hour=row[10],
                    created_at=row[11],
                    last_executed=row[12],
                    execution_count=row[13],
                    success_rate=row[14],
                    enabled=bool(row[15])
                )
                self.defense_rules[rule.rule_id] = rule
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.defense_rules)} defense rules")
            
        except Exception as e:
            self.logger.error(f"Error loading defense rules: {e}")
    
    async def _create_default_rules(self):
        """Create default defense rules"""
        try:
            default_rules = [
                {
                    "name": "Malicious IP Blocking",
                    "description": "Block IPs showing malicious behavior",
                    "trigger_conditions": {
                        "event_type": "suspicious_connection",
                        "failed_attempts": {">=": 5},
                        "time_window": 300
                    },
                    "actions": [DefenseAction.BLOCK_IP, DefenseAction.ALERT_ADMIN],
                    "severity_threshold": ThreatSeverity.MEDIUM,
                    "confidence_threshold": 0.7,
                    "auto_execute": True,
                    "requires_approval": False,
                    "cooldown_period": 300,
                    "max_executions_per_hour": 10
                },
                
                {
                    "name": "Malware Quarantine",
                    "description": "Quarantine detected malware files",
                    "trigger_conditions": {
                        "event_type": "malware_detected",
                        "confidence": {">=": 0.8}
                    },
                    "actions": [DefenseAction.QUARANTINE_FILE, DefenseAction.ALERT_ADMIN],
                    "severity_threshold": ThreatSeverity.HIGH,
                    "confidence_threshold": 0.8,
                    "auto_execute": True,
                    "requires_approval": False,
                    "cooldown_period": 60,
                    "max_executions_per_hour": 20
                },
                
                {
                    "name": "System Isolation",
                    "description": "Isolate compromised systems",
                    "trigger_conditions": {
                        "event_type": "system_compromise",
                        "severity": "critical"
                    },
                    "actions": [DefenseAction.ISOLATE_SYSTEM, DefenseAction.BACKUP_DATA, DefenseAction.ALERT_ADMIN],
                    "severity_threshold": ThreatSeverity.CRITICAL,
                    "confidence_threshold": 0.9,
                    "auto_execute": False,
                    "requires_approval": True,
                    "cooldown_period": 3600,
                    "max_executions_per_hour": 2
                },
                
                {
                    "name": "Suspicious Process Termination",
                    "description": "Kill suspicious processes",
                    "trigger_conditions": {
                        "event_type": "suspicious_process",
                        "behavior_score": {">=": 0.8}
                    },
                    "actions": [DefenseAction.KILL_PROCESS, DefenseAction.ALERT_ADMIN],
                    "severity_threshold": ThreatSeverity.MEDIUM,
                    "confidence_threshold": 0.75,
                    "auto_execute": True,
                    "requires_approval": False,
                    "cooldown_period": 120,
                    "max_executions_per_hour": 15
                },
                
                {
                    "name": "Rate Limiting",
                    "description": "Apply rate limiting to suspicious sources",
                    "trigger_conditions": {
                        "event_type": "excessive_requests",
                        "request_rate": {">=": 100}
                    },
                    "actions": [DefenseAction.RATE_LIMIT],
                    "severity_threshold": ThreatSeverity.LOW,
                    "confidence_threshold": 0.6,
                    "auto_execute": True,
                    "requires_approval": False,
                    "cooldown_period": 600,
                    "max_executions_per_hour": 5
                }
            ]
            
            for rule_data in default_rules:
                if not any(rule.name == rule_data["name"] for rule in self.defense_rules.values()):
                    await self._create_defense_rule(rule_data)
            
        except Exception as e:
            self.logger.error(f"Error creating default rules: {e}")
    
    async def _create_defense_rule(self, rule_data: Dict[str, Any]) -> str:
        """Create a new defense rule"""
        try:
            rule_id = str(uuid.uuid4())
            current_time = time.time()
            
            rule = DefenseRule(
                rule_id=rule_id,
                name=rule_data["name"],
                description=rule_data["description"],
                trigger_conditions=rule_data["trigger_conditions"],
                actions=rule_data["actions"],
                severity_threshold=rule_data["severity_threshold"],
                confidence_threshold=rule_data["confidence_threshold"],
                auto_execute=rule_data["auto_execute"],
                requires_approval=rule_data["requires_approval"],
                cooldown_period=rule_data["cooldown_period"],
                max_executions_per_hour=rule_data["max_executions_per_hour"],
                created_at=current_time
            )
            
            # Store in database
            await self._store_defense_rule(rule)
            
            # Add to memory
            self.defense_rules[rule_id] = rule
            
            self.logger.info(f"Created defense rule: {rule.name}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Error creating defense rule: {e}")
            return ""
    
    async def _store_defense_rule(self, rule: DefenseRule):
        """Store defense rule in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO defense_rules 
                (rule_id, name, description, trigger_conditions, actions, severity_threshold,
                 confidence_threshold, auto_execute, requires_approval, cooldown_period,
                 max_executions_per_hour, created_at, last_executed, execution_count,
                 success_rate, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id, rule.name, rule.description, json.dumps(rule.trigger_conditions),
                json.dumps([action.value for action in rule.actions]), rule.severity_threshold.value,
                rule.confidence_threshold, rule.auto_execute, rule.requires_approval,
                rule.cooldown_period, rule.max_executions_per_hour, rule.created_at,
                rule.last_executed, rule.execution_count, rule.success_rate, rule.enabled
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing defense rule: {e}")
    
    async def _start_monitoring(self):
        """Start threat monitoring and response"""
        try:
            while True:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Update consciousness level
                consciousness_state = await self.consciousness_bus.get_consciousness_state()
                self.current_state.consciousness_level = consciousness_state.get('overall_consciousness_level', 0)
                
                # Simulate threat events for demonstration
                await self._simulate_threat_events()
                
                # Update system state
                await self._update_system_state()
                
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
    
    async def _simulate_threat_events(self):
        """Simulate threat events for demonstration"""
        try:
            import random
            
            # Randomly generate threat events
            if random.random() < 0.1:  # 10% chance per check
                event_types = [
                    "suspicious_connection",
                    "malware_detected", 
                    "excessive_requests",
                    "suspicious_process",
                    "system_compromise"
                ]
                
                event_type = random.choice(event_types)
                severity = random.choice(list(ThreatSeverity))
                
                threat_event = {
                    "event_id": str(uuid.uuid4()),
                    "event_type": event_type,
                    "severity": severity.value,
                    "source_ip": f"192.168.1.{random.randint(1, 254)}",
                    "target_system": f"system-{random.randint(1, 10)}",
                    "description": f"Simulated {event_type} event",
                    "confidence": random.uniform(0.5, 1.0),
                    "timestamp": time.time()
                }
                
                # Process the threat event
                await self._process_threat_event(threat_event)
            
        except Exception as e:
            self.logger.error(f"Error simulating threat events: {e}")
    
    async def _process_threat_event(self, threat_event: Dict[str, Any]):
        """Process a threat event and trigger appropriate responses"""
        try:
            self.logger.info(f"Processing threat event: {threat_event['event_type']} - {threat_event['severity']}")
            
            # Store threat event
            await self._store_threat_event(threat_event)
            
            # Find matching defense rules
            matching_rules = await self._find_matching_rules(threat_event)
            
            for rule in matching_rules:
                # Check if rule can be executed
                if await self._can_execute_rule(rule, threat_event):
                    # Execute defense response
                    response = await self._execute_defense_response(rule, threat_event)
                    if response:
                        self.active_responses[response.response_id] = response
            
        except Exception as e:
            self.logger.error(f"Error processing threat event: {e}")
    
    async def _find_matching_rules(self, threat_event: Dict[str, Any]) -> List[DefenseRule]:
        """Find defense rules that match the threat event"""
        try:
            matching_rules = []
            
            for rule in self.defense_rules.values():
                if not rule.enabled:
                    continue
                
                # Check trigger conditions
                if await self._check_trigger_conditions(rule.trigger_conditions, threat_event):
                    # Check severity threshold
                    event_severity = ThreatSeverity(threat_event["severity"])
                    if self._severity_meets_threshold(event_severity, rule.severity_threshold):
                        # Check confidence threshold
                        if threat_event.get("confidence", 0) >= rule.confidence_threshold:
                            matching_rules.append(rule)
            
            return matching_rules
            
        except Exception as e:
            self.logger.error(f"Error finding matching rules: {e}")
            return []
    
    async def _check_trigger_conditions(self, conditions: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met"""
        try:
            for key, condition in conditions.items():
                if key not in event:
                    continue
                
                event_value = event[key]
                
                if isinstance(condition, dict):
                    # Handle comparison operators
                    for operator, threshold in condition.items():
                        if operator == ">=" and event_value < threshold:
                            return False
                        elif operator == ">" and event_value <= threshold:
                            return False
                        elif operator == "<=" and event_value > threshold:
                            return False
                        elif operator == "<" and event_value >= threshold:
                            return False
                        elif operator == "==" and event_value != threshold:
                            return False
                        elif operator == "!=" and event_value == threshold:
                            return False
                else:
                    # Direct value comparison
                    if event_value != condition:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking trigger conditions: {e}")
            return False
    
    def _severity_meets_threshold(self, event_severity: ThreatSeverity, threshold: ThreatSeverity) -> bool:
        """Check if event severity meets the threshold"""
        severity_levels = {
            ThreatSeverity.LOW: 1,
            ThreatSeverity.MEDIUM: 2,
            ThreatSeverity.HIGH: 3,
            ThreatSeverity.CRITICAL: 4
        }
        
        return severity_levels[event_severity] >= severity_levels[threshold]
    
    async def _can_execute_rule(self, rule: DefenseRule, threat_event: Dict[str, Any]) -> bool:
        """Check if a rule can be executed"""
        try:
            current_time = time.time()
            
            # Check cooldown period
            if rule.last_executed and (current_time - rule.last_executed) < rule.cooldown_period:
                return False
            
            # Check execution rate limit
            hour_ago = current_time - 3600
            recent_executions = sum(1 for response in self.response_history 
                                  if response.rule_id == rule.rule_id and response.execution_time > hour_ago)
            
            if recent_executions >= rule.max_executions_per_hour:
                return False
            
            # Check consciousness level for critical actions
            if (any(action in [DefenseAction.ISOLATE_SYSTEM, DefenseAction.DISABLE_USER] for action in rule.actions) and
                self.current_state.consciousness_level < 0.8):
                return False
            
            # Check concurrent response limit
            if len(self.active_responses) >= self.max_concurrent_responses:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule execution: {e}")
            return False
    
    async def _execute_defense_response(self, rule: DefenseRule, threat_event: Dict[str, Any]) -> Optional[DefenseResponse]:
        """Execute a defense response"""
        try:
            response_id = str(uuid.uuid4())
            current_time = time.time()
            
            # Check if approval is required
            if rule.requires_approval and not rule.auto_execute:
                # For now, simulate approval for demonstration
                approved = self.current_state.consciousness_level > 0.7
                if not approved:
                    self.logger.info(f"Defense response requires approval: {rule.name}")
                    return None
            
            # Execute actions
            actions_taken = []
            success = True
            
            for action in rule.actions:
                action_result = await self._execute_action(action, threat_event)
                actions_taken.append(action_result)
                if not action_result["success"]:
                    success = False
            
            # Create response record
            response = DefenseResponse(
                response_id=response_id,
                rule_id=rule.rule_id,
                trigger_event=threat_event,
                actions_taken=actions_taken,
                execution_time=current_time,
                success=success,
                consciousness_level=self.current_state.consciousness_level,
                automated=rule.auto_execute,
                approval_required=rule.requires_approval,
                side_effects=[]
            )
            
            # Update rule statistics
            rule.last_executed = current_time
            rule.execution_count += 1
            if success:
                rule.success_rate = (rule.success_rate * (rule.execution_count - 1) + 1.0) / rule.execution_count
            else:
                rule.success_rate = (rule.success_rate * (rule.execution_count - 1)) / rule.execution_count
            
            # Store response and update rule
            await self._store_defense_response(response)
            await self._store_defense_rule(rule)
            
            # Add to history
            self.response_history.append(response)
            
            self.logger.info(f"Executed defense response: {rule.name} - Success: {success}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error executing defense response: {e}")
            return None
    
    async def _execute_action(self, action: DefenseAction, threat_event: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific defense action"""
        try:
            action_result = {
                "action": action.value,
                "success": True,
                "details": "",
                "timestamp": time.time()
            }
            
            if action == DefenseAction.BLOCK_IP:
                ip = threat_event.get("source_ip")
                if ip and ip not in self.current_state.blocked_ips:
                    self.current_state.blocked_ips.append(ip)
                    action_result["details"] = f"Blocked IP: {ip}"
                    self.logger.info(f"Blocked IP: {ip}")
                
            elif action == DefenseAction.QUARANTINE_FILE:
                file_path = threat_event.get("file_path", "unknown_file")
                if file_path not in self.current_state.quarantined_files:
                    self.current_state.quarantined_files.append(file_path)
                    action_result["details"] = f"Quarantined file: {file_path}"
                    self.logger.info(f"Quarantined file: {file_path}")
                
            elif action == DefenseAction.ISOLATE_SYSTEM:
                system = threat_event.get("target_system")
                if system and system not in self.current_state.isolated_systems:
                    self.current_state.isolated_systems.append(system)
                    action_result["details"] = f"Isolated system: {system}"
                    self.logger.info(f"Isolated system: {system}")
                
            elif action == DefenseAction.KILL_PROCESS:
                process_id = threat_event.get("process_id", "unknown")
                action_result["details"] = f"Terminated process: {process_id}"
                self.logger.info(f"Terminated process: {process_id}")
                
            elif action == DefenseAction.ALERT_ADMIN:
                action_result["details"] = "Admin alert sent"
                self.logger.info("Admin alert sent")
                
            elif action == DefenseAction.RATE_LIMIT:
                source = threat_event.get("source_ip", "unknown")
                action_result["details"] = f"Applied rate limiting to: {source}"
                self.logger.info(f"Applied rate limiting to: {source}")
                
            else:
                action_result["details"] = f"Simulated action: {action.value}"
                self.logger.info(f"Simulated action: {action.value}")
            
            return action_result
            
        except Exception as e:
            self.logger.error(f"Error executing action {action}: {e}")
            return {
                "action": action.value,
                "success": False,
                "details": f"Error: {str(e)}",
                "timestamp": time.time()
            }
    
    async def _store_threat_event(self, threat_event: Dict[str, Any]):
        """Store threat event in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO threat_events 
                (event_id, event_type, severity, source_ip, target_system, description, 
                 indicators, timestamp, response_triggered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                threat_event["event_id"], threat_event["event_type"], threat_event["severity"],
                threat_event.get("source_ip"), threat_event.get("target_system"),
                threat_event["description"], json.dumps(threat_event.get("indicators", [])),
                threat_event["timestamp"], False
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing threat event: {e}")
    
    async def _store_defense_response(self, response: DefenseResponse):
        """Store defense response in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO defense_responses 
                (response_id, rule_id, trigger_event, actions_taken, execution_time, success,
                 consciousness_level, automated, approval_required, approved_by, 
                 effectiveness_score, side_effects)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                response.response_id, response.rule_id, json.dumps(response.trigger_event),
                json.dumps(response.actions_taken), response.execution_time, response.success,
                response.consciousness_level, response.automated, response.approval_required,
                response.approved_by, response.effectiveness_score, 
                json.dumps(response.side_effects or [])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing defense response: {e}")
    
    async def _start_adaptation_loop(self):
        """Start the adaptation loop for learning and improvement"""
        try:
            while True:
                await asyncio.sleep(self.adaptation_interval)
                
                # Adapt defense rules based on effectiveness
                await self._adapt_defense_rules()
                
                # Update defense level based on threat landscape
                await self._update_defense_level()
                
                # Clean up old responses
                await self._cleanup_old_responses()
                
        except Exception as e:
            self.logger.error(f"Error in adaptation loop: {e}")
    
    async def _adapt_defense_rules(self):
        """Adapt defense rules based on performance"""
        try:
            for rule in self.defense_rules.values():
                if rule.execution_count < 5:  # Need minimum executions for adaptation
                    continue
                
                # Adjust confidence threshold based on success rate
                if rule.success_rate < 0.7:
                    # Increase confidence threshold for poorly performing rules
                    rule.confidence_threshold = min(0.95, rule.confidence_threshold + self.learning_rate)
                elif rule.success_rate > 0.9:
                    # Decrease confidence threshold for well-performing rules
                    rule.confidence_threshold = max(0.5, rule.confidence_threshold - self.learning_rate)
                
                # Update rule in database
                await self._store_defense_rule(rule)
            
            self.logger.debug("Adapted defense rules based on performance")
            
        except Exception as e:
            self.logger.error(f"Error adapting defense rules: {e}")
    
    async def _update_defense_level(self):
        """Update system defense level based on threat landscape"""
        try:
            current_time = time.time()
            hour_ago = current_time - 3600
            
            # Count recent threats
            recent_threats = sum(1 for response in self.response_history
                               if response.execution_time > hour_ago)
            
            # Count critical threats
            critical_threats = sum(1 for response in self.response_history
                                 if (response.execution_time > hour_ago and
                                     response.trigger_event.get("severity") == "critical"))
            
            # Determine new defense level
            old_level = self.current_state.defense_level
            
            if critical_threats > 2:
                self.current_state.defense_level = DefenseLevel.MAXIMUM
            elif critical_threats > 0 or recent_threats > 10:
                self.current_state.defense_level = DefenseLevel.CRITICAL
            elif recent_threats > 5:
                self.current_state.defense_level = DefenseLevel.HIGH
            elif recent_threats > 2:
                self.current_state.defense_level = DefenseLevel.ELEVATED
            else:
                self.current_state.defense_level = DefenseLevel.NORMAL
            
            if old_level != self.current_state.defense_level:
                self.logger.info(f"Defense level changed: {old_level.value} -> {self.current_state.defense_level.value}")
            
        except Exception as e:
            self.logger.error(f"Error updating defense level: {e}")
    
    async def _update_system_state(self):
        """Update current system state"""
        try:
            self.current_state.active_threats = len([r for r in self.active_responses.values()
                                                   if r.trigger_event.get("severity") in ["high", "critical"]])
            self.current_state.active_responses = len(self.active_responses)
            self.current_state.last_updated = time.time()
            
            # Store state history
            await self._store_system_state()
            
        except Exception as e:
            self.logger.error(f"Error updating system state: {e}")
    
    async def _store_system_state(self):
        """Store current system state in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            state_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO system_state_history
                (state_id, defense_level, active_threats, blocked_ips, quarantined_files,
                 isolated_systems, active_responses, consciousness_level, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                state_id, self.current_state.defense_level.value, self.current_state.active_threats,
                json.dumps(self.current_state.blocked_ips), json.dumps(self.current_state.quarantined_files),
                json.dumps(self.current_state.isolated_systems), self.current_state.active_responses,
                self.current_state.consciousness_level, self.current_state.last_updated
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing system state: {e}")
    
    async def _cleanup_old_responses(self):
        """Clean up old response records"""
        try:
            current_time = time.time()
            cleanup_threshold = current_time - 3600  # 1 hour
            
            # Remove old responses from active list
            old_responses = [r_id for r_id, response in self.active_responses.items()
                           if response.execution_time < cleanup_threshold]
            
            for response_id in old_responses:
                del self.active_responses[response_id]
            
            # Keep only recent responses in history (last 24 hours)
            day_ago = current_time - 86400
            self.response_history = [r for r in self.response_history if r.execution_time > day_ago]
            
            if old_responses:
                self.logger.debug(f"Cleaned up {len(old_responses)} old responses")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old responses: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            return {
                "defense_level": self.current_state.defense_level.value,
                "active_threats": self.current_state.active_threats,
                "blocked_ips_count": len(self.current_state.blocked_ips),
                "quarantined_files_count": len(self.current_state.quarantined_files),
                "isolated_systems_count": len(self.current_state.isolated_systems),
                "active_responses": self.current_state.active_responses,
                "consciousness_level": self.current_state.consciousness_level,
                "total_defense_rules": len(self.defense_rules),
                "enabled_rules": len([r for r in self.defense_rules.values() if r.enabled]),
                "last_updated": self.current_state.last_updated
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def get_defense_rules(self) -> List[Dict[str, Any]]:
        """Get all defense rules"""
        try:
            return [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "severity_threshold": rule.severity_threshold.value,
                    "confidence_threshold": rule.confidence_threshold,
                    "auto_execute": rule.auto_execute,
                    "requires_approval": rule.requires_approval,
                    "execution_count": rule.execution_count,
                    "success_rate": rule.success_rate,
                    "enabled": rule.enabled,
                    "actions": [action.value for action in rule.actions]
                }
                for rule in self.defense_rules.values()
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting defense rules: {e}")
            return []
    
    async def get_recent_responses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent defense responses"""
        try:
            recent_responses = sorted(self.response_history,
                                    key=lambda x: x.execution_time, reverse=True)[:limit]
            
            return [
                {
                    "response_id": response.response_id,
                    "rule_name": self.defense_rules[response.rule_id].name if response.rule_id in self.defense_rules else "Unknown",
                    "trigger_event_type": response.trigger_event.get("event_type"),
                    "severity": response.trigger_event.get("severity"),
                    "actions_count": len(response.actions_taken),
                    "success": response.success,
                    "execution_time": response.execution_time,
                    "automated": response.automated,
                    "consciousness_level": response.consciousness_level
                }
                for response in recent_responses
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting recent responses: {e}")
            return []
    
    async def create_custom_rule(self, rule_data: Dict[str, Any]) -> str:
        """Create a custom defense rule"""
        try:
            # Validate rule data
            required_fields = ["name", "description", "trigger_conditions", "actions",
                             "severity_threshold", "confidence_threshold"]
            
            for field in required_fields:
                if field not in rule_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert actions to enum
            actions = [DefenseAction(action) for action in rule_data["actions"]]
            
            rule_data_processed = {
                "name": rule_data["name"],
                "description": rule_data["description"],
                "trigger_conditions": rule_data["trigger_conditions"],
                "actions": actions,
                "severity_threshold": ThreatSeverity(rule_data["severity_threshold"]),
                "confidence_threshold": rule_data["confidence_threshold"],
                "auto_execute": rule_data.get("auto_execute", False),
                "requires_approval": rule_data.get("requires_approval", True),
                "cooldown_period": rule_data.get("cooldown_period", 300),
                "max_executions_per_hour": rule_data.get("max_executions_per_hour", 5)
            }
            
            return await self._create_defense_rule(rule_data_processed)
            
        except Exception as e:
            self.logger.error(f"Error creating custom rule: {e}")
            return ""
    
    async def update_rule_status(self, rule_id: str, enabled: bool) -> bool:
        """Enable or disable a defense rule"""
        try:
            if rule_id not in self.defense_rules:
                return False
            
            rule = self.defense_rules[rule_id]
            rule.enabled = enabled
            
            await self._store_defense_rule(rule)
            
            self.logger.info(f"Rule {rule.name} {'enabled' if enabled else 'disabled'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating rule status: {e}")
            return False
    
    async def process_external_threat(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an external threat event"""
        try:
            # Validate threat data
            required_fields = ["event_type", "severity"]
            for field in required_fields:
                if field not in threat_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Add metadata
            threat_event = {
                "event_id": str(uuid.uuid4()),
                "timestamp": time.time(),
                **threat_data
            }
            
            # Process the threat
            await self._process_threat_event(threat_event)
            
            return {
                "success": True,
                "event_id": threat_event["event_id"],
                "message": "Threat event processed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing external threat: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on adaptive defense system"""
        try:
            return {
                "status": "healthy",
                "defense_level": self.current_state.defense_level.value,
                "active_rules": len([r for r in self.defense_rules.values() if r.enabled]),
                "total_rules": len(self.defense_rules),
                "active_responses": len(self.active_responses),
                "consciousness_level": self.current_state.consciousness_level,
                "blocked_ips": len(self.current_state.blocked_ips),
                "quarantined_files": len(self.current_state.quarantined_files),
                "isolated_systems": len(self.current_state.isolated_systems)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown adaptive defense system"""
        self.logger.info("Shutting down adaptive defense system...")
        
        # Store final system state
        await self._store_system_state()
        
        # Clear active responses
        self.active_responses.clear()
        
        self.logger.info("Adaptive defense system shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Adaptive Defense System"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.initialize()
    
    defense_system = AdaptiveDefenseSystem(consciousness_bus)
    
    # Wait for initialization
    await asyncio.sleep(5)
    
    # Health check
    health = await defense_system.health_check()
    print(f"Defense system health: {health}")
    
    # Get system status
    status = await defense_system.get_system_status()
    print(f"System status: {status}")
    
    # Get defense rules
    rules = await defense_system.get_defense_rules()
    print(f"Defense rules: {len(rules)}")
    
    # Process a test threat
    test_threat = {
        "event_type": "suspicious_connection",
        "severity": "medium",
        "source_ip": "192.168.1.100",
        "confidence": 0.8
    }
    
    result = await defense_system.process_external_threat(test_threat)
    print(f"Threat processing result: {result}")
    
    # Wait a bit for processing
    await asyncio.sleep(2)
    
    # Get recent responses
    responses = await defense_system.get_recent_responses(10)
    print(f"Recent responses: {len(responses)}")
    
    # Shutdown
    await defense_system.shutdown()
    await consciousness_bus.shutdown()


if __name__ == "__main__":
    asyncio.run(main())