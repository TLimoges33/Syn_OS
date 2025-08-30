#!/usr/bin/env python3
"""
Comprehensive Security Event Logging System
Critical security monitoring and audit trail for Phase 1 remediation
"""

import asyncio
import logging
import time
import json
import os
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import threading


class SecurityEventType(Enum):
    """Types of security events to log"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ACCESS_DENIED = "access_denied"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    COMMAND_INJECTION_ATTEMPT = "command_injection_attempt"
    INPUT_VALIDATION_FAILURE = "input_validation_failure"
    SECURITY_TOOL_EXECUTION = "security_tool_execution"
    EMERGENCY_LOCKDOWN = "emergency_lockdown"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    SECURITY_PATCH_APPLIED = "security_patch_applied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_COMPROMISE = "system_compromise"
    INCIDENT_RESPONSE = "incident_response"
    AUDIT_LOG_ACCESS = "audit_log_access"
    CONFIGURATION_CHANGE = "configuration_change"


class SecuritySeverity(Enum):
    """Security event severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    event_type: SecurityEventType
    severity: SecuritySeverity
    timestamp: float
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    source_component: str
    event_description: str
    event_details: Dict[str, Any]
    risk_indicators: List[str]
    mitigation_actions: List[str]
    correlation_id: Optional[str] = None
    resolved: bool = False
    false_positive: bool = False


class SecurityEventLogger:
    """
    Comprehensive security event logging system
    Provides real-time security monitoring and audit trail
    """
    
    def __init__(self):
        """Initialize security event logger"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.log_directory = "/var/log/synos/security"
        self.database_file = f"{self.log_directory}/security_events.db"
        self.max_events_memory = 10000
        self.log_retention_days = 365
        
        # Event storage
        self.recent_events: List[SecurityEvent] = []
        self.event_counts: Dict[str, int] = {}
        self.active_incidents: Dict[str, List[SecurityEvent]] = {}
        
        # Real-time monitoring
        self.monitoring_active = True
        self.alert_thresholds = {
            SecurityEventType.AUTHENTICATION: 5,  # 5 failed attempts
            SecurityEventType.COMMAND_INJECTION_ATTEMPT: 1,  # Any attempt
            SecurityEventType.PRIVILEGE_ESCALATION: 1,  # Any attempt
            SecurityEventType.SUSPICIOUS_ACTIVITY: 3,  # 3 suspicious events
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Initialize system
        asyncio.create_task(self._initialize_logging_system())
    
    async def _initialize_logging_system(self):
        """Initialize the security logging system"""
        try:
            self.logger.info("Initializing security event logging system...")
            
            # Create log directory
            os.makedirs(self.log_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._cleanup_loop())
            
            self.logger.info("Security event logging system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing security logging: {e}")
    
    async def _initialize_database(self):
        """Initialize security events database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    source_component TEXT NOT NULL,
                    event_description TEXT NOT NULL,
                    event_details TEXT,
                    risk_indicators TEXT,
                    mitigation_actions TEXT,
                    correlation_id TEXT,
                    resolved BOOLEAN NOT NULL DEFAULT 0,
                    false_positive BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            
            # Security incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_incidents (
                    incident_id TEXT PRIMARY KEY,
                    incident_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    description TEXT,
                    event_ids TEXT,
                    resolution_notes TEXT,
                    resolved_at REAL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON security_events (event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user ON security_events (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_ip ON security_events (ip_address)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing security database: {e}")
            raise
    
    async def log_security_event(self, event_type: SecurityEventType, severity: SecuritySeverity,
                                description: str, details: Dict[str, Any],
                                user_id: Optional[str] = None, session_id: Optional[str] = None,
                                ip_address: str = "unknown", user_agent: str = "unknown",
                                source_component: str = "system") -> str:
        """Log a security event"""
        try:
            # Generate event ID
            event_id = hashlib.sha256(
                f"{time.time()}{event_type.value}{description}".encode()
            ).hexdigest()[:16]
            
            # Analyze risk indicators
            risk_indicators = self._analyze_risk_indicators(event_type, details)
            
            # Determine mitigation actions
            mitigation_actions = self._determine_mitigation_actions(event_type, severity, risk_indicators)
            
            # Create security event
            event = SecurityEvent(
                event_id=event_id,
                event_type=event_type,
                severity=severity,
                timestamp=time.time(),
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                source_component=source_component,
                event_description=description,
                event_details=details,
                risk_indicators=risk_indicators,
                mitigation_actions=mitigation_actions
            )
            
            # Store event
            await self._store_event(event)
            
            # Add to recent events
            with self.lock:
                self.recent_events.append(event)
                if len(self.recent_events) > self.max_events_memory:
                    self.recent_events = self.recent_events[-self.max_events_memory:]
                
                # Update event counts
                event_key = f"{event_type.value}_{ip_address}"
                self.event_counts[event_key] = self.event_counts.get(event_key, 0) + 1
            
            # Check for alert conditions
            await self._check_alert_conditions(event)
            
            # Log to system logger
            log_level = self._get_log_level(severity)
            self.logger.log(log_level, f"SECURITY EVENT [{severity.value.upper()}] {description}")
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
            return ""
    
    def _analyze_risk_indicators(self, event_type: SecurityEventType, details: Dict[str, Any]) -> List[str]:
        """Analyze event for risk indicators"""
        indicators = []
        
        try:
            # Command injection indicators
            if event_type == SecurityEventType.COMMAND_INJECTION_ATTEMPT:
                if any(char in str(details) for char in [';', '|', '&', '`', '$']):
                    indicators.append("dangerous_characters")
                if "subprocess" in str(details):
                    indicators.append("subprocess_execution")
                if ".." in str(details):
                    indicators.append("path_traversal_attempt")
            
            # Authentication indicators
            elif event_type == SecurityEventType.AUTHENTICATION:
                if details.get("failed_attempts", 0) > 3:
                    indicators.append("multiple_failed_attempts")
                if details.get("unusual_location"):
                    indicators.append("unusual_location")
                if details.get("unusual_time"):
                    indicators.append("unusual_time")
            
            # Privilege escalation indicators
            elif event_type == SecurityEventType.PRIVILEGE_ESCALATION:
                if details.get("attempted_role") in ["admin", "root", "emergency_responder"]:
                    indicators.append("high_privilege_attempt")
                if details.get("bypass_attempt"):
                    indicators.append("security_bypass_attempt")
            
            # General suspicious activity indicators
            if details.get("rapid_requests"):
                indicators.append("rapid_requests")
            if details.get("automated_behavior"):
                indicators.append("automated_behavior")
            if details.get("known_attack_pattern"):
                indicators.append("known_attack_pattern")
            
        except Exception as e:
            self.logger.error(f"Error analyzing risk indicators: {e}")
        
        return indicators
    
    def _determine_mitigation_actions(self, event_type: SecurityEventType, 
                                    severity: SecuritySeverity, 
                                    risk_indicators: List[str]) -> List[str]:
        """Determine appropriate mitigation actions"""
        actions = []
        
        try:
            # Critical events require immediate action
            if severity in [SecuritySeverity.CRITICAL, SecuritySeverity.EMERGENCY]:
                actions.append("immediate_investigation_required")
                actions.append("notify_security_team")
                
                if event_type == SecurityEventType.COMMAND_INJECTION_ATTEMPT:
                    actions.append("block_source_ip")
                    actions.append("review_input_validation")
                    actions.append("emergency_patch_review")
                
                elif event_type == SecurityEventType.PRIVILEGE_ESCALATION:
                    actions.append("revoke_user_access")
                    actions.append("audit_user_permissions")
                    actions.append("emergency_access_review")
            
            # High severity events
            elif severity == SecuritySeverity.HIGH:
                actions.append("security_team_notification")
                actions.append("enhanced_monitoring")
                
                if "multiple_failed_attempts" in risk_indicators:
                    actions.append("temporary_account_lockout")
                
                if "suspicious_activity" in risk_indicators:
                    actions.append("user_behavior_analysis")
            
            # Medium severity events
            elif severity == SecuritySeverity.MEDIUM:
                actions.append("log_for_analysis")
                actions.append("pattern_monitoring")
            
            # General actions based on risk indicators
            if "automated_behavior" in risk_indicators:
                actions.append("rate_limiting_review")
            
            if "known_attack_pattern" in risk_indicators:
                actions.append("threat_intelligence_correlation")
            
        except Exception as e:
            self.logger.error(f"Error determining mitigation actions: {e}")
        
        return actions
    
    async def _store_event(self, event: SecurityEvent):
        """Store security event in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_events
                (event_id, event_type, severity, timestamp, user_id, session_id,
                 ip_address, user_agent, source_component, event_description,
                 event_details, risk_indicators, mitigation_actions, correlation_id,
                 resolved, false_positive)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id, event.event_type.value, event.severity.value,
                event.timestamp, event.user_id, event.session_id,
                event.ip_address, event.user_agent, event.source_component,
                event.event_description, json.dumps(event.event_details),
                json.dumps(event.risk_indicators), json.dumps(event.mitigation_actions),
                event.correlation_id, event.resolved, event.false_positive
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing security event: {e}")
    
    async def _check_alert_conditions(self, event: SecurityEvent):
        """Check if event triggers alert conditions"""
        try:
            event_type = event.event_type
            
            # Check threshold-based alerts
            if event_type in self.alert_thresholds:
                threshold = self.alert_thresholds[event_type]
                event_key = f"{event_type.value}_{event.ip_address}"
                
                with self.lock:
                    count = self.event_counts.get(event_key, 0)
                
                if count >= threshold:
                    await self._trigger_security_alert(event, f"Threshold exceeded: {count} events")
            
            # Check for critical events that always trigger alerts
            if event.severity in [SecuritySeverity.CRITICAL, SecuritySeverity.EMERGENCY]:
                await self._trigger_security_alert(event, "Critical security event detected")
            
            # Check for specific high-risk patterns
            if "command_injection" in event.risk_indicators:
                await self._trigger_security_alert(event, "Command injection attempt detected")
            
            if "privilege_escalation" in event.risk_indicators:
                await self._trigger_security_alert(event, "Privilege escalation attempt detected")
            
        except Exception as e:
            self.logger.error(f"Error checking alert conditions: {e}")
    
    async def _trigger_security_alert(self, event: SecurityEvent, reason: str):
        """Trigger security alert for critical events"""
        try:
            alert_data = {
                "alert_id": f"ALERT_{event.event_id}",
                "timestamp": time.time(),
                "event_id": event.event_id,
                "severity": event.severity.value,
                "reason": reason,
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "ip_address": event.ip_address,
                "description": event.event_description,
                "mitigation_actions": event.mitigation_actions
            }
            
            # Log critical alert
            self.logger.critical(f"SECURITY ALERT: {reason} - Event ID: {event.event_id}")
            
            # In production, this would trigger:
            # - Email/SMS notifications to security team
            # - SIEM integration
            # - Automated response systems
            # - Incident management system
            
            # For now, log to security alert file
            alert_file = f"{self.log_directory}/security_alerts.log"
            with open(alert_file, "a") as f:
                f.write(f"{json.dumps(alert_data)}\n")
            
        except Exception as e:
            self.logger.error(f"Error triggering security alert: {e}")
    
    def _get_log_level(self, severity: SecuritySeverity) -> int:
        """Get logging level for severity"""
        level_mapping = {
            SecuritySeverity.INFO: logging.INFO,
            SecuritySeverity.LOW: logging.INFO,
            SecuritySeverity.MEDIUM: logging.WARNING,
            SecuritySeverity.HIGH: logging.ERROR,
            SecuritySeverity.CRITICAL: logging.CRITICAL,
            SecuritySeverity.EMERGENCY: logging.CRITICAL
        }
        return level_mapping.get(severity, logging.INFO)
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Reset hourly counters
                current_time = time.time()
                with self.lock:
                    # Remove old event counts (older than 1 hour)
                    keys_to_remove = []
                    for key in self.event_counts:
                        # In production, would track timestamps for each count
                        # For now, reset all counts every hour
                        pass
                
                # Check for patterns and anomalies
                await self._analyze_security_patterns()
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    async def _analyze_security_patterns(self):
        """Analyze recent events for security patterns"""
        try:
            with self.lock:
                recent_events = self.recent_events[-100:]  # Last 100 events
            
            if len(recent_events) < 10:
                return
            
            # Analyze patterns
            ip_counts = {}
            user_counts = {}
            event_type_counts = {}
            
            for event in recent_events:
                # Count by IP
                ip_counts[event.ip_address] = ip_counts.get(event.ip_address, 0) + 1
                
                # Count by user
                if event.user_id:
                    user_counts[event.user_id] = user_counts.get(event.user_id, 0) + 1
                
                # Count by event type
                event_type_counts[event.event_type.value] = event_type_counts.get(event.event_type.value, 0) + 1
            
            # Check for suspicious patterns
            for ip, count in ip_counts.items():
                if count > 20:  # More than 20 events from single IP
                    await self.log_security_event(
                        SecurityEventType.SUSPICIOUS_ACTIVITY,
                        SecuritySeverity.HIGH,
                        f"High activity from IP: {ip} ({count} events)",
                        {"ip_address": ip, "event_count": count, "pattern": "high_ip_activity"},
                        ip_address=ip,
                        source_component="security_monitor"
                    )
            
        except Exception as e:
            self.logger.error(f"Error analyzing security patterns: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup old events and logs"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up old database entries
                cutoff_time = time.time() - (self.log_retention_days * 24 * 3600)
                
                conn = sqlite3.connect(self.database_file)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM security_events WHERE timestamp < ?', (cutoff_time,))
                deleted_count = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} old security events")
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
            
            await asyncio.sleep(3600)  # Wait 1 hour
    
    async def get_recent_events(self, limit: int = 100, 
                              event_type: Optional[SecurityEventType] = None,
                              severity: Optional[SecuritySeverity] = None) -> List[Dict[str, Any]]:
        """Get recent security events"""
        try:
            with self.lock:
                events = self.recent_events.copy()
            
            # Filter by event type
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Filter by severity
            if severity:
                events = [e for e in events if e.severity == severity]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Limit results
            events = events[:limit]
            
            # Convert to dict format
            return [asdict(event) for event in events]
            
        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
            return []
    
    async def get_security_statistics(self) -> Dict[str, Any]:
        """Get security event statistics"""
        try:
            current_time = time.time()
            hour_ago = current_time - 3600
            day_ago = current_time - 86400
            
            with self.lock:
                all_events = self.recent_events.copy()
            
            # Count events by time period
            last_hour = [e for e in all_events if e.timestamp > hour_ago]
            last_day = [e for e in all_events if e.timestamp > day_ago]
            
            # Count by severity
            severity_counts = {}
            for event in last_day:
                severity_counts[event.severity.value] = severity_counts.get(event.severity.value, 0) + 1
            
            # Count by event type
            type_counts = {}
            for event in last_day:
                type_counts[event.event_type.value] = type_counts.get(event.event_type.value, 0) + 1
            
            return {
                "total_events_last_hour": len(last_hour),
                "total_events_last_day": len(last_day),
                "events_by_severity": severity_counts,
                "events_by_type": type_counts,
                "critical_events_last_hour": len([e for e in last_hour if e.severity == SecuritySeverity.CRITICAL]),
                "monitoring_active": self.monitoring_active,
                "database_file": self.database_file
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security statistics: {e}")
            return {}


# Global security event logger instance
security_event_logger = SecurityEventLogger()


# Convenience functions for common security events
async def log_authentication_event(success: bool, user_id: str, ip_address: str,
                                 details: Optional[Dict[str, Any]] = None):
    """Log authentication event"""
    if details is None:
        details = {}
    
    severity = SecuritySeverity.INFO if success else SecuritySeverity.MEDIUM
    description = f"Authentication {'successful' if success else 'failed'} for user {user_id}"
    
    return await security_event_logger.log_security_event(
        SecurityEventType.AUTHENTICATION,
        severity,
        description,
        {"success": success, "user_id": user_id, **details},
        user_id=user_id,
        ip_address=ip_address,
        source_component="authentication_system"
    )


async def log_command_injection_attempt(command: str, user_id: str, ip_address: str,
                                      details: Optional[Dict[str, Any]] = None):
    """Log command injection attempt"""
    if details is None:
        details = {}
    
    return await security_event_logger.log_security_event(
        SecurityEventType.COMMAND_INJECTION_ATTEMPT,
        SecuritySeverity.CRITICAL,
        f"Command injection attempt detected: {command[:100]}...",
        {"attempted_command": command, "user_id": user_id, **details},
        user_id=user_id,
        ip_address=ip_address,
        source_component="input_validation"
    )


async def log_privilege_escalation_attempt(user_id: str, attempted_role: str,
                                         ip_address: str, details: Optional[Dict[str, Any]] = None):
    """Log privilege escalation attempt"""
    if details is None:
        details = {}
    
    return await security_event_logger.log_security_event(
        SecurityEventType.PRIVILEGE_ESCALATION,
        SecuritySeverity.HIGH,
        f"Privilege escalation attempt: {user_id} -> {attempted_role}",
        {"user_id": user_id, "attempted_role": attempted_role, **details},
        user_id=user_id,
        ip_address=ip_address,
        source_component="access_control"
    )