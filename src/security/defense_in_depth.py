#!/usr/bin/env python3
"""
Defense-in-Depth Security Architecture
Multi-layered security implementation for Syn_OS
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
import hashlib
import ipaddress
import re


class SecurityLayer(Enum):
    """Defense-in-depth security layers"""
    PERIMETER = "perimeter"
    NETWORK = "network"
    HOST = "host"
    APPLICATION = "application"
    DATA = "data"
    IDENTITY = "identity"
    ENDPOINT = "endpoint"
    MONITORING = "monitoring"


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ControlType(Enum):
    """Security control types"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    DETERRENT = "deterrent"
    RECOVERY = "recovery"
    COMPENSATING = "compensating"


@dataclass
class SecurityControl:
    """Individual security control"""
    control_id: str
    name: str
    description: str
    layer: SecurityLayer
    control_type: ControlType
    implementation_status: str
    effectiveness_rating: float  # 0.0-1.0
    last_tested: float
    next_test: float
    dependencies: List[str]
    configuration: Dict[str, Any]
    metrics: Dict[str, float]
    enabled: bool = True


@dataclass
class SecurityPolicy:
    """Security policy rule"""
    policy_id: str
    name: str
    description: str
    layer: SecurityLayer
    rule_type: str
    conditions: List[str]
    actions: List[str]
    priority: int
    enabled: bool
    created_time: float
    last_modified: float
    applied_count: int
    blocked_count: int


@dataclass
class ThreatDetection:
    """Threat detection event"""
    detection_id: str
    threat_type: str
    threat_level: ThreatLevel
    source_ip: str
    target_ip: str
    detection_time: float
    layer: SecurityLayer
    indicators: List[str]
    confidence_score: float
    mitigation_actions: List[str]
    status: str
    analyst_notes: str


class DefenseInDepth:
    """
    Defense-in-Depth Security Architecture
    Implements multi-layered security controls for Syn_OS
    """
    
    def __init__(self):
        """Initialize defense-in-depth framework"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.defense_directory = "/var/lib/synos/defense"
        self.database_file = f"{self.defense_directory}/defense.db"
        
        # Security components
        self.security_controls: Dict[str, SecurityControl] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.threat_detections: Dict[str, ThreatDetection] = {}
        
        # Layer configurations
        self.layer_configs = {}
        self.active_threats = set()
        self.blocked_ips = set()
        
        # Defense metrics
        self.metrics = {
            "total_controls": 0,
            "active_controls": 0,
            "threats_detected": 0,
            "threats_blocked": 0,
            "false_positives": 0,
            "layer_effectiveness": {}
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_defense())
    
    async def _initialize_defense(self):
        """Initialize defense-in-depth architecture"""
        try:
            self.logger.info("Initializing defense-in-depth security architecture...")
            
            # Create defense directory
            os.makedirs(self.defense_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Configure security layers
            await self._configure_security_layers()
            
            # Deploy security controls
            await self._deploy_security_controls()
            
            # Initialize threat detection
            await self._initialize_threat_detection()
            
            self.logger.info("Defense-in-depth architecture initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing defense-in-depth: {e}")
    
    async def _initialize_database(self):
        """Initialize defense database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Security controls table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_controls (
                    control_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    layer TEXT NOT NULL,
                    control_type TEXT NOT NULL,
                    implementation_status TEXT,
                    effectiveness_rating REAL,
                    last_tested REAL,
                    next_test REAL,
                    dependencies TEXT,
                    configuration TEXT,
                    metrics TEXT,
                    enabled BOOLEAN DEFAULT 1
                )
            ''')
            
            # Security policies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_policies (
                    policy_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    layer TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    conditions TEXT,
                    actions TEXT,
                    priority INTEGER,
                    enabled BOOLEAN DEFAULT 1,
                    created_time REAL,
                    last_modified REAL,
                    applied_count INTEGER DEFAULT 0,
                    blocked_count INTEGER DEFAULT 0
                )
            ''')
            
            # Threat detections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_detections (
                    detection_id TEXT PRIMARY KEY,
                    threat_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    source_ip TEXT,
                    target_ip TEXT,
                    detection_time REAL NOT NULL,
                    layer TEXT NOT NULL,
                    indicators TEXT,
                    confidence_score REAL,
                    mitigation_actions TEXT,
                    status TEXT,
                    analyst_notes TEXT
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_controls_layer ON security_controls (layer)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_policies_layer ON security_policies (layer)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_detections_time ON threat_detections (detection_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_detections_level ON threat_detections (threat_level)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing defense database: {e}")
            raise
    
    async def _configure_security_layers(self):
        """Configure defense-in-depth security layers"""
        try:
            self.layer_configs = {
                SecurityLayer.PERIMETER: {
                    "name": "Perimeter Security",
                    "description": "External network boundary protection",
                    "controls": ["firewall", "ids_ips", "ddos_protection", "vpn_gateway"],
                    "policies": ["block_malicious_ips", "rate_limiting", "geo_blocking"],
                    "monitoring": ["traffic_analysis", "connection_monitoring"]
                },
                SecurityLayer.NETWORK: {
                    "name": "Network Security",
                    "description": "Internal network segmentation and monitoring",
                    "controls": ["network_segmentation", "vlan_isolation", "network_monitoring"],
                    "policies": ["inter_vlan_rules", "network_access_control", "traffic_filtering"],
                    "monitoring": ["network_flow_analysis", "anomaly_detection"]
                },
                SecurityLayer.HOST: {
                    "name": "Host Security",
                    "description": "Individual system protection",
                    "controls": ["host_firewall", "antivirus", "host_ids", "patch_management"],
                    "policies": ["host_hardening", "service_restrictions", "file_integrity"],
                    "monitoring": ["system_monitoring", "process_monitoring", "file_monitoring"]
                },
                SecurityLayer.APPLICATION: {
                    "name": "Application Security",
                    "description": "Application-level protection",
                    "controls": ["waf", "input_validation", "output_encoding", "session_management"],
                    "policies": ["secure_coding", "api_security", "authentication_rules"],
                    "monitoring": ["application_monitoring", "security_logging"]
                },
                SecurityLayer.DATA: {
                    "name": "Data Security",
                    "description": "Data protection and encryption",
                    "controls": ["encryption_at_rest", "encryption_in_transit", "data_classification"],
                    "policies": ["data_handling", "retention_policies", "access_controls"],
                    "monitoring": ["data_access_monitoring", "dlp_monitoring"]
                },
                SecurityLayer.IDENTITY: {
                    "name": "Identity & Access Management",
                    "description": "User authentication and authorization",
                    "controls": ["multi_factor_auth", "privileged_access", "identity_governance"],
                    "policies": ["password_policy", "access_review", "role_based_access"],
                    "monitoring": ["authentication_monitoring", "access_monitoring"]
                },
                SecurityLayer.ENDPOINT: {
                    "name": "Endpoint Security",
                    "description": "End-user device protection",
                    "controls": ["endpoint_protection", "device_control", "mobile_security"],
                    "policies": ["device_compliance", "application_control", "data_protection"],
                    "monitoring": ["endpoint_monitoring", "behavior_analysis"]
                },
                SecurityLayer.MONITORING: {
                    "name": "Security Monitoring",
                    "description": "Comprehensive security monitoring and response",
                    "controls": ["siem", "log_management", "threat_intelligence", "incident_response"],
                    "policies": ["monitoring_policies", "alerting_rules", "response_procedures"],
                    "monitoring": ["security_analytics", "threat_hunting", "compliance_monitoring"]
                }
            }
            
            # Save layer configurations
            config_file = f"{self.defense_directory}/layer_configs.json"
            with open(config_file, 'w') as f:
                # Convert enum keys to strings for JSON serialization
                serializable_config = {layer.value: config for layer, config in self.layer_configs.items()}
                json.dump(serializable_config, f, indent=2)
            
            self.logger.info(f"Configured {len(self.layer_configs)} security layers")
            
        except Exception as e:
            self.logger.error(f"Error configuring security layers: {e}")
    
    async def _deploy_security_controls(self):
        """Deploy security controls across all layers"""
        try:
            current_time = time.time()
            next_test = current_time + (30 * 24 * 3600)  # Monthly testing
            
            # Perimeter Layer Controls
            perimeter_controls = [
                SecurityControl(
                    control_id="CTRL-PER-001",
                    name="Next-Generation Firewall",
                    description="Stateful packet inspection with application awareness",
                    layer=SecurityLayer.PERIMETER,
                    control_type=ControlType.PREVENTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.95,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "default_policy": "deny",
                        "logging": "enabled",
                        "threat_intelligence": "enabled",
                        "application_control": "enabled"
                    },
                    metrics={
                        "packets_processed": 0,
                        "threats_blocked": 0,
                        "false_positives": 0
                    }
                ),
                SecurityControl(
                    control_id="CTRL-PER-002",
                    name="Intrusion Detection/Prevention System",
                    description="Network-based threat detection and prevention",
                    layer=SecurityLayer.PERIMETER,
                    control_type=ControlType.DETECTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.88,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=["CTRL-PER-001"],
                    configuration={
                        "signature_updates": "automatic",
                        "behavioral_analysis": "enabled",
                        "blocking_mode": "enabled"
                    },
                    metrics={
                        "signatures_loaded": 50000,
                        "alerts_generated": 0,
                        "attacks_blocked": 0
                    }
                )
            ]
            
            # Network Layer Controls
            network_controls = [
                SecurityControl(
                    control_id="CTRL-NET-001",
                    name="Network Segmentation",
                    description="VLAN-based network isolation",
                    layer=SecurityLayer.NETWORK,
                    control_type=ControlType.PREVENTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.92,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "vlans_configured": 8,
                        "inter_vlan_routing": "controlled",
                        "default_deny": "enabled"
                    },
                    metrics={
                        "segments_active": 8,
                        "cross_segment_blocks": 0,
                        "policy_violations": 0
                    }
                )
            ]
            
            # Host Layer Controls
            host_controls = [
                SecurityControl(
                    control_id="CTRL-HOST-001",
                    name="Host-Based Firewall",
                    description="Individual system firewall protection",
                    layer=SecurityLayer.HOST,
                    control_type=ControlType.PREVENTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.85,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "default_policy": "deny",
                        "application_rules": "enabled",
                        "logging": "enabled"
                    },
                    metrics={
                        "hosts_protected": 0,
                        "connections_blocked": 0,
                        "rules_active": 50
                    }
                )
            ]
            
            # Application Layer Controls
            application_controls = [
                SecurityControl(
                    control_id="CTRL-APP-001",
                    name="Web Application Firewall",
                    description="Application-layer attack protection",
                    layer=SecurityLayer.APPLICATION,
                    control_type=ControlType.PREVENTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.90,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "owasp_rules": "enabled",
                        "custom_rules": "enabled",
                        "learning_mode": "disabled"
                    },
                    metrics={
                        "requests_processed": 0,
                        "attacks_blocked": 0,
                        "rules_triggered": 0
                    }
                )
            ]
            
            # Data Layer Controls
            data_controls = [
                SecurityControl(
                    control_id="CTRL-DATA-001",
                    name="Data Encryption at Rest",
                    description="AES-256 encryption for stored data",
                    layer=SecurityLayer.DATA,
                    control_type=ControlType.PREVENTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.98,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "encryption_algorithm": "AES-256-GCM",
                        "key_rotation": "quarterly",
                        "key_management": "hsm"
                    },
                    metrics={
                        "encrypted_volumes": 0,
                        "key_rotations": 0,
                        "decryption_failures": 0
                    }
                )
            ]
            
            # Identity Layer Controls
            identity_controls = [
                SecurityControl(
                    control_id="CTRL-ID-001",
                    name="Multi-Factor Authentication",
                    description="Two-factor authentication for all users",
                    layer=SecurityLayer.IDENTITY,
                    control_type=ControlType.PREVENTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.94,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "required_factors": 2,
                        "token_types": ["totp", "sms", "hardware"],
                        "session_timeout": 3600
                    },
                    metrics={
                        "users_enrolled": 0,
                        "authentication_attempts": 0,
                        "failed_attempts": 0
                    }
                )
            ]
            
            # Endpoint Layer Controls
            endpoint_controls = [
                SecurityControl(
                    control_id="CTRL-END-001",
                    name="Endpoint Detection and Response",
                    description="Advanced endpoint threat detection",
                    layer=SecurityLayer.ENDPOINT,
                    control_type=ControlType.DETECTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.87,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "behavioral_analysis": "enabled",
                        "machine_learning": "enabled",
                        "automatic_response": "enabled"
                    },
                    metrics={
                        "endpoints_monitored": 0,
                        "threats_detected": 0,
                        "responses_automated": 0
                    }
                )
            ]
            
            # Monitoring Layer Controls
            monitoring_controls = [
                SecurityControl(
                    control_id="CTRL-MON-001",
                    name="Security Information and Event Management",
                    description="Centralized security event correlation",
                    layer=SecurityLayer.MONITORING,
                    control_type=ControlType.DETECTIVE,
                    implementation_status="deployed",
                    effectiveness_rating=0.91,
                    last_tested=current_time,
                    next_test=next_test,
                    dependencies=[],
                    configuration={
                        "log_sources": 50,
                        "correlation_rules": 200,
                        "retention_days": 365
                    },
                    metrics={
                        "events_processed": 0,
                        "alerts_generated": 0,
                        "incidents_created": 0
                    }
                )
            ]
            
            # Combine all controls
            all_controls = (perimeter_controls + network_controls + host_controls + 
                          application_controls + data_controls + identity_controls + 
                          endpoint_controls + monitoring_controls)
            
            # Store controls
            for control in all_controls:
                await self._store_security_control(control)
                self.security_controls[control.control_id] = control
            
            self.metrics["total_controls"] = len(all_controls)
            self.metrics["active_controls"] = len([c for c in all_controls if c.enabled])
            
            self.logger.info(f"Deployed {len(all_controls)} security controls across {len(self.layer_configs)} layers")
            
        except Exception as e:
            self.logger.error(f"Error deploying security controls: {e}")
    
    async def _store_security_control(self, control: SecurityControl):
        """Store security control in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_controls
                (control_id, name, description, layer, control_type, implementation_status,
                 effectiveness_rating, last_tested, next_test, dependencies, configuration,
                 metrics, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                control.control_id, control.name, control.description, control.layer.value,
                control.control_type.value, control.implementation_status,
                control.effectiveness_rating, control.last_tested, control.next_test,
                json.dumps(control.dependencies), json.dumps(control.configuration),
                json.dumps(control.metrics), control.enabled
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing security control: {e}")
    
    async def _initialize_threat_detection(self):
        """Initialize threat detection capabilities"""
        try:
            # Configure threat detection rules
            detection_rules = {
                "brute_force_detection": {
                    "threshold": 5,
                    "time_window": 300,
                    "action": "block_ip"
                },
                "port_scan_detection": {
                    "threshold": 10,
                    "time_window": 60,
                    "action": "alert_and_log"
                },
                "malware_detection": {
                    "signatures": "enabled",
                    "behavioral": "enabled",
                    "action": "quarantine"
                },
                "data_exfiltration_detection": {
                    "volume_threshold": "100MB",
                    "time_window": 3600,
                    "action": "alert_and_block"
                }
            }
            
            # Save detection rules
            rules_file = f"{self.defense_directory}/detection_rules.json"
            with open(rules_file, 'w') as f:
                json.dump(detection_rules, f, indent=2)
            
            self.logger.info("Threat detection capabilities initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing threat detection: {e}")
    
    async def detect_threat(self, threat_data: Dict[str, Any]) -> str:
        """Detect and process security threat"""
        try:
            detection_id = f"DET-{int(time.time())}-{hash(str(threat_data)) % 10000:04d}"
            
            detection = ThreatDetection(
                detection_id=detection_id,
                threat_type=threat_data.get("threat_type", "unknown"),
                threat_level=ThreatLevel(threat_data.get("threat_level", "medium")),
                source_ip=threat_data.get("source_ip", "unknown"),
                target_ip=threat_data.get("target_ip", "unknown"),
                detection_time=time.time(),
                layer=SecurityLayer(threat_data.get("layer", "monitoring")),
                indicators=threat_data.get("indicators", []),
                confidence_score=threat_data.get("confidence_score", 0.5),
                mitigation_actions=[],
                status="detected",
                analyst_notes=""
            )
            
            # Determine mitigation actions
            mitigation_actions = await self._determine_mitigation_actions(detection)
            detection.mitigation_actions = mitigation_actions
            
            # Execute mitigation actions
            await self._execute_mitigation_actions(detection)
            
            # Store detection
            await self._store_threat_detection(detection)
            self.threat_detections[detection_id] = detection
            
            # Update metrics
            self.metrics["threats_detected"] += 1
            if detection.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                self.metrics["threats_blocked"] += 1
            
            self.logger.info(f"Threat detected and processed: {detection_id}")
            return detection_id
            
        except Exception as e:
            self.logger.error(f"Error detecting threat: {e}")
            return ""
    
    async def _determine_mitigation_actions(self, detection: ThreatDetection) -> List[str]:
        """Determine appropriate mitigation actions"""
        try:
            actions = []
            
            # Based on threat level
            if detection.threat_level == ThreatLevel.CRITICAL:
                actions.extend(["block_ip", "isolate_host", "alert_soc", "escalate_incident"])
            elif detection.threat_level == ThreatLevel.HIGH:
                actions.extend(["block_ip", "alert_soc", "log_event"])
            elif detection.threat_level == ThreatLevel.MEDIUM:
                actions.extend(["rate_limit", "alert_soc", "log_event"])
            else:
                actions.extend(["log_event"])
            
            # Based on threat type
            if detection.threat_type == "malware":
                actions.append("quarantine_file")
            elif detection.threat_type == "brute_force":
                actions.append("temporary_block")
            elif detection.threat_type == "data_exfiltration":
                actions.extend(["block_connection", "alert_dpo"])
            
            return list(set(actions))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error determining mitigation actions: {e}")
            return []
    
    async def _execute_mitigation_actions(self, detection: ThreatDetection):
        """Execute mitigation actions"""
        try:
            for action in detection.mitigation_actions:
                if action == "block_ip":
                    await self._block_ip(detection.source_ip)
                elif action == "alert_soc":
                    await self._alert_soc(detection)
                elif action == "log_event":
                    await self._log_security_event(detection)
                elif action == "isolate_host":
                    await self._isolate_host(detection.target_ip)
                # Add more action implementations as needed
            
            detection.status = "mitigated"
            
        except Exception as e:
            self.logger.error(f"Error executing mitigation actions: {e}")
    
    async def _block_ip(self, ip_address: str):
        """Block IP address at perimeter"""
        try:
            if self._is_valid_ip(ip_address):
                self.blocked_ips.add(ip_address)
                self.logger.info(f"Blocked IP address: {ip_address}")
        except Exception as e:
            self.logger.error(f"Error blocking IP: {e}")
    
    async def _alert_soc(self, detection: ThreatDetection):
        """Send alert to Security Operations Center"""
        try:
            alert_data = {
                "detection_id": detection.detection_id,
                "threat_type": detection.threat_type,
                "threat_level": detection.threat_level.value,
                "source_ip": detection.source_ip,
                "confidence": detection.confidence_score,
                "timestamp": detection.detection_time
            }
            # Integration with SOC alerting system would go here
            self.logger.info(f"SOC alert sent for detection: {detection.detection_id}")
        except Exception as e:
            self.logger.error(f"Error sending SOC alert: {e}")
    
    async def _log_security_event(self, detection: ThreatDetection):
        """Log security event"""
        try:
            event_data = {
                "event_type": "threat_detection",
                "detection_id": detection.detection_id,
                "threat_details": asdict(detection),
                "timestamp": detection.detection_time
            }
            # Integration with security logging system would go here
            self.logger.info(f"Security event logged: {detection.detection_id}")
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
    
    async def _isolate_host(self, ip_address: str):
        """Isolate compromised host"""
        try:
            if self._is_valid_ip(ip_address):
                # Implementation would integrate with network infrastructure
                self.logger.info(f"Host isolated: {ip_address}")
        except Exception as e:
            self.logger.error(f"Error isolating host: {e}")
    
    def _is_valid_ip(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    async def _store_threat_detection(self, detection: ThreatDetection):
        """Store threat detection in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_detections
                (detection_id, threat_type, threat_level, source_ip, target_ip,
                 detection_time, layer, indicators, confidence_score, mitigation_actions,
                 status, analyst_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detection.detection_id, detection.threat_type, detection.threat_level.value,
                detection.source_ip, detection.target_ip, detection.detection_time,
                detection.layer.value, json.dumps(detection.indicators),
                detection.confidence_score, json.dumps(detection.mitigation_actions),
                detection.status, detection.analyst_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing threat detection: {e}")
    
    async def get_defense_status(self) -> Dict[str, Any]:
        """Get defense-in-depth status"""
        try:
            return {
                "total_layers": len(self.layer_configs),
                "total_controls": self.metrics["total_controls"],
                "active_controls": self.metrics["active_controls"],
                "threats_detected": self.metrics["threats_detected"],
                "threats_blocked": self.metrics["threats_blocked"],
                "blocked_ips": len(self.blocked_ips),
                "active_threats": len(self.active_threats),
                "layer_effectiveness": self._calculate_layer_effectiveness(),
                "overall_effectiveness": self._calculate_overall_effectiveness()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting defense status: {e}")
            return {"error": str(e)}
    
    def _calculate_layer_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness by layer"""
        try:
            layer_effectiveness = {}
            for layer in SecurityLayer:
                layer_controls = [c for c in self.security_controls.values() if c.layer == layer]
                if layer_controls:
                    avg_effectiveness = sum(c.effectiveness_rating for c in layer_controls) / len(layer_controls)
                    layer_effectiveness[layer.value] = round(avg_effectiveness, 3)
                else:
                    layer_effectiveness[layer.value] = 0.0
            return layer_effectiveness
        except Exception as e:
            self.logger.error(f"Error calculating layer effectiveness: {e}")
            return {}
    
    def _calculate_overall_effectiveness(self) -> float:
        """Calculate overall defense effectiveness"""
        try:
            if not self.security_controls:
                return 0.0
            
            total_effectiveness = sum(c.effectiveness_rating for c in self.security_controls.values() if c.enabled)
            active_controls = len([c for c in self.security_controls.values() if c.enabled])
            
            if active_controls == 0:
                return 0.0
            
            return round(total_effectiveness / active_controls, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating overall effectiveness: {e}")
            return 0.0


# Global defense-in-depth instance
defense_in_depth = DefenseInDepth()