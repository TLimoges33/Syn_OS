#!/usr/bin/env python3
"""
Security Audit Logging System for Syn_OS
Comprehensive logging of security events, authentication attempts, and system access
"""

import logging
import json
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path
try:
    import geoip2.database
    import geoip2.errors
except ImportError:
    geoip2 = None

logger = logging.getLogger('synapticos.security.audit')


class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "authz_failure"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION_CHANGE = "config_change"
    SECURITY_VIOLATION = "security_violation"
    INJECTION_ATTEMPT = "injection_attempt"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SESSION_CREATED = "session_created"
    SESSION_TERMINATED = "session_terminated"
    API_ACCESS = "api_access"
    CONSCIOUSNESS_ACCESS = "consciousness_access"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"


class SecurityLevel(Enum):
    """Security event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: SecurityEventType
    severity: SecurityLevel
    timestamp: datetime
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    geolocation: Optional[Dict[str, str]] = None
    risk_score: Optional[float] = None


@dataclass
class AuditLogEntry:
    """Complete audit log entry"""
    log_id: str
    event: SecurityEvent
    system_info: Dict[str, Any]
    context: Dict[str, Any]
    hash_chain: Optional[str] = None


class SecurityAuditLogger:
    """Comprehensive security audit logging system"""
    
    def __init__(self, log_directory: str = "logs/security"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize log files
        self.audit_log_file = self.log_directory / "security_audit.log"
        self.json_log_file = self.log_directory / "security_audit.jsonl"
        self.alert_log_file = self.log_directory / "security_alerts.log"
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Event counters for anomaly detection
        self.event_counters: Dict[str, Dict[str, int]] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        
        # GeoIP database (optional)
        self.geoip_db = None
        self._initialize_geoip()
        
        # Hash chain for log integrity
        self.last_hash = "0" * 64
        
        # Setup logging handlers
        self._setup_logging()
        
        # Log system startup
        self.log_security_event(
            SecurityEventType.SYSTEM_STARTUP,
            SecurityLevel.MEDIUM,
            details={"component": "security_audit_logger"}
        )
    
    def _initialize_geoip(self):
        """Initialize GeoIP database if available"""
        if not geoip2:
            logger.info("GeoIP2 library not available")
            return
            
        try:
            # Try to find GeoLite2 database
            geoip_paths = [
                "/usr/share/GeoIP/GeoLite2-City.mmdb",
                "/var/lib/GeoIP/GeoLite2-City.mmdb",
                "./GeoLite2-City.mmdb"
            ]
            
            for path in geoip_paths:
                if Path(path).exists():
                    self.geoip_db = geoip2.database.Reader(path)
                    logger.info(f"GeoIP database loaded from {path}")
                    break
        except Exception as e:
            logger.warning(f"Could not initialize GeoIP database: {e}")
    
    def _setup_logging(self):
        """Setup logging handlers"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler for audit logs
        audit_handler = logging.FileHandler(self.audit_log_file)
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(detailed_formatter)
        
        # File handler for alerts
        alert_handler = logging.FileHandler(self.alert_log_file)
        alert_handler.setLevel(logging.WARNING)
        alert_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        logger.addHandler(audit_handler)
        logger.addHandler(alert_handler)
        logger.setLevel(logging.INFO)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(time.time_ns())
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]
    
    def _get_geolocation(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get geolocation information for IP address"""
        if not self.geoip_db or not ip_address or not geoip2:
            return None
        
        try:
            response = self.geoip_db.city(ip_address)
            return {
                'country': getattr(response.country, 'name', 'Unknown') or 'Unknown',
                'country_code': getattr(response.country, 'iso_code', 'Unknown') or 'Unknown',
                'city': getattr(response.city, 'name', 'Unknown') or 'Unknown',
                'latitude': str(getattr(response.location, 'latitude', 'Unknown')) if hasattr(response.location, 'latitude') else 'Unknown',
                'longitude': str(getattr(response.location, 'longitude', 'Unknown')) if hasattr(response.location, 'longitude') else 'Unknown'
            }
        except Exception:
            return None
    
    def _calculate_risk_score(self, event: SecurityEvent) -> float:
        """Calculate risk score for security event"""
        base_scores = {
            SecurityEventType.AUTHENTICATION_FAILURE: 0.3,
            SecurityEventType.AUTHORIZATION_FAILURE: 0.4,
            SecurityEventType.BRUTE_FORCE_ATTEMPT: 0.8,
            SecurityEventType.INJECTION_ATTEMPT: 0.9,
            SecurityEventType.PRIVILEGE_ESCALATION: 0.9,
            SecurityEventType.SUSPICIOUS_ACTIVITY: 0.6,
            SecurityEventType.SECURITY_VIOLATION: 0.7,
            SecurityEventType.AUTHENTICATION_SUCCESS: 0.1,
            SecurityEventType.SESSION_CREATED: 0.1,
        }
        
        base_score = base_scores.get(event.event_type, 0.2)
        
        # Adjust based on severity
        severity_multipliers = {
            SecurityLevel.LOW: 0.5,
            SecurityLevel.MEDIUM: 1.0,
            SecurityLevel.HIGH: 1.5,
            SecurityLevel.CRITICAL: 2.0
        }
        
        score = base_score * severity_multipliers.get(event.severity, 1.0)
        
        # Adjust based on frequency (anomaly detection)
        if event.user_id:
            recent_events = self._count_recent_events(event.user_id, event.event_type)
            if recent_events > 5:
                score *= 1.5
        
        return min(1.0, score)
    
    def _count_recent_events(self, user_id: str, event_type: SecurityEventType, minutes: int = 60) -> int:
        """Count recent events for anomaly detection"""
        key = f"{user_id}:{event_type.value}"
        if key not in self.event_counters:
            self.event_counters[key] = {}
        
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time.timestamp() - (minutes * 60)
        
        # Clean old entries
        self.event_counters[key] = {
            timestamp: count for timestamp, count in self.event_counters[key].items()
            if float(timestamp) > cutoff_time
        }
        
        return sum(self.event_counters[key].values())
    
    def _update_event_counter(self, user_id: str, event_type: SecurityEventType):
        """Update event counter for anomaly detection"""
        key = f"{user_id}:{event_type.value}"
        timestamp = str(datetime.now(timezone.utc).timestamp())
        
        if key not in self.event_counters:
            self.event_counters[key] = {}
        
        self.event_counters[key][timestamp] = self.event_counters[key].get(timestamp, 0) + 1
    
    def _calculate_hash_chain(self, log_entry: AuditLogEntry) -> str:
        """Calculate hash chain for log integrity"""
        entry_data = json.dumps(asdict(log_entry), sort_keys=True, default=str)
        combined = f"{self.last_hash}{entry_data}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        severity: SecurityLevel,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a security event"""
        
        with self.lock:
            # Create security event
            event = SecurityEvent(
                event_id=self._generate_event_id(),
                event_type=event_type,
                severity=severity,
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                resource=resource,
                action=action,
                result=result,
                details=details or {},
                geolocation=self._get_geolocation(ip_address) if ip_address else None
            )
            
            # Calculate risk score
            event.risk_score = self._calculate_risk_score(event)
            
            # Update event counters
            if user_id:
                self._update_event_counter(user_id, event_type)
            
            # Create audit log entry
            log_entry = AuditLogEntry(
                log_id=self._generate_event_id(),
                event=event,
                system_info={
                    'hostname': 'syn_os_node',  # Get from system
                    'component': 'security_audit',
                    'version': '2.0.0'
                },
                context={
                    'thread_id': threading.get_ident(),
                    'process_id': 'main'  # Get from os.getpid()
                }
            )
            
            # Calculate hash chain
            log_entry.hash_chain = self._calculate_hash_chain(log_entry)
            self.last_hash = log_entry.hash_chain
            
            # Write to logs
            self._write_audit_log(log_entry)
            self._write_json_log(log_entry)
            
            # Check for alerts
            if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL] or event.risk_score > 0.7:
                self._generate_alert(event)
            
            return event.event_id
    
    def _write_audit_log(self, log_entry: AuditLogEntry):
        """Write to human-readable audit log"""
        try:
            event = log_entry.event
            log_message = (
                f"[{event.event_type.value.upper()}] "
                f"User: {event.username or 'N/A'} "
                f"IP: {event.ip_address or 'N/A'} "
                f"Resource: {event.resource or 'N/A'} "
                f"Result: {event.result or 'N/A'} "
                f"Risk: {event.risk_score:.2f}"
            )
            
            if event.severity == SecurityLevel.CRITICAL:
                logger.critical(log_message)
            elif event.severity == SecurityLevel.HIGH:
                logger.error(log_message)
            elif event.severity == SecurityLevel.MEDIUM:
                logger.warning(log_message)
            else:
                logger.info(log_message)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def _write_json_log(self, log_entry: AuditLogEntry):
        """Write to JSON log file"""
        try:
            with open(self.json_log_file, 'a') as f:
                json_data = asdict(log_entry)
                # Convert datetime objects to ISO format
                json_data['event']['timestamp'] = log_entry.event.timestamp.isoformat()
                f.write(json.dumps(json_data, default=str) + '\n')
        except Exception as e:
            logger.error(f"Failed to write JSON log: {e}")
    
    def _generate_alert(self, event: SecurityEvent):
        """Generate security alert for high-risk events"""
        alert_message = (
            f"SECURITY ALERT: {event.event_type.value} - "
            f"Severity: {event.severity.value} - "
            f"Risk Score: {event.risk_score:.2f} - "
            f"User: {event.username or 'Unknown'} - "
            f"IP: {event.ip_address or 'Unknown'}"
        )
        
        # Log alert
        logger.critical(alert_message)
        
        # In production, send to SIEM, email, Slack, etc.
        self._send_alert_notification(event, alert_message)
    
    def _send_alert_notification(self, event: SecurityEvent, message: str):
        """Send alert notification (placeholder for integration)"""
        # Placeholder for alert integrations:
        # - Email notifications
        # - Slack/Teams webhooks
        # - SIEM integration
        # - SMS alerts for critical events
        pass
    
    def log_authentication_attempt(
        self,
        username: str,
        ip_address: str,
        success: bool,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log authentication attempt"""
        event_type = SecurityEventType.AUTHENTICATION_SUCCESS if success else SecurityEventType.AUTHENTICATION_FAILURE
        severity = SecurityLevel.LOW if success else SecurityLevel.MEDIUM
        
        # Check for brute force
        if not success:
            key = f"auth_fail:{ip_address}"
            if key not in self.failed_attempts:
                self.failed_attempts[key] = []
            
            # Clean old attempts
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=15)
            self.failed_attempts[key] = [
                attempt for attempt in self.failed_attempts[key]
                if attempt > cutoff_time
            ]
            
            self.failed_attempts[key].append(datetime.now(timezone.utc))
            
            # Check for brute force
            if len(self.failed_attempts[key]) >= 5:
                return self.log_security_event(
                    SecurityEventType.BRUTE_FORCE_ATTEMPT,
                    SecurityLevel.HIGH,
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={**(details or {}), 'failed_attempts': len(self.failed_attempts[key])}
                )
        
        return self.log_security_event(
            event_type,
            severity,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            result="success" if success else "failure",
            details=details
        )
    
    def log_api_access(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        ip_address: str,
        status_code: int,
        user_agent: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> str:
        """Log API access"""
        severity = SecurityLevel.LOW
        if status_code >= 400:
            severity = SecurityLevel.MEDIUM
        if status_code >= 500:
            severity = SecurityLevel.HIGH
        
        return self.log_security_event(
            SecurityEventType.API_ACCESS,
            severity,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=endpoint,
            action=method,
            result=str(status_code),
            details={
                'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:8] if api_key else None,
                'response_time': None  # Add if available
            }
        )
    
    def log_consciousness_access(
        self,
        user_id: str,
        consciousness_level: float,
        operation: str,
        ip_address: str,
        success: bool
    ) -> str:
        """Log consciousness system access"""
        severity = SecurityLevel.MEDIUM if consciousness_level > 0.8 else SecurityLevel.LOW
        
        return self.log_security_event(
            SecurityEventType.CONSCIOUSNESS_ACCESS,
            severity,
            user_id=user_id,
            ip_address=ip_address,
            resource="consciousness_system",
            action=operation,
            result="success" if success else "failure",
            details={
                'consciousness_level': consciousness_level,
                'high_level_access': consciousness_level > 0.8
            }
        )
    
    def log_injection_attempt(
        self,
        attack_type: str,
        payload: str,
        ip_address: str,
        endpoint: str,
        user_id: Optional[str] = None
    ) -> str:
        """Log injection attempt"""
        return self.log_security_event(
            SecurityEventType.INJECTION_ATTEMPT,
            SecurityLevel.HIGH,
            user_id=user_id,
            ip_address=ip_address,
            resource=endpoint,
            action="injection_attempt",
            result="blocked",
            details={
                'attack_type': attack_type,
                'payload_hash': hashlib.sha256(payload.encode()).hexdigest()[:16],
                'payload_length': len(payload)
            }
        )
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security event summary"""
        # This would query the JSON log file or database
        # For now, return a placeholder summary
        return {
            'time_period_hours': hours,
            'total_events': 0,
            'high_risk_events': 0,
            'authentication_failures': 0,
            'injection_attempts': 0,
            'unique_ips': 0,
            'top_event_types': [],
            'risk_score_average': 0.0
        }
    
    def verify_log_integrity(self) -> bool:
        """Verify log integrity using hash chain"""
        # This would verify the hash chain in the log files
        # For now, return True as placeholder
        return True
    
    def shutdown(self):
        """Shutdown audit logger"""
        self.log_security_event(
            SecurityEventType.SYSTEM_SHUTDOWN,
            SecurityLevel.MEDIUM,
            details={"component": "security_audit_logger"}
        )
        
        if self.geoip_db:
            self.geoip_db.close()


# Global audit logger instance
audit_logger = SecurityAuditLogger()


def get_audit_logger() -> SecurityAuditLogger:
    """Get the global audit logger instance"""
    return audit_logger


# Convenience functions
def log_auth_success(username: str, ip_address: str, **kwargs) -> str:
    return audit_logger.log_authentication_attempt(username, ip_address, True, **kwargs)


def log_auth_failure(username: str, ip_address: str, **kwargs) -> str:
    return audit_logger.log_authentication_attempt(username, ip_address, False, **kwargs)


def log_security_violation(description: str, ip_address: str, **kwargs) -> str:
    return audit_logger.log_security_event(
        SecurityEventType.SECURITY_VIOLATION,
        SecurityLevel.HIGH,
        ip_address=ip_address,
        details={'description': description, **kwargs}
    )


if __name__ == "__main__":
    # Test the audit logging system
    logger_test = SecurityAuditLogger()
    
    # Test various security events
    logger_test.log_authentication_attempt("admin", "192.168.1.100", True)
    logger_test.log_authentication_attempt("hacker", "10.0.0.1", False)
    logger_test.log_injection_attempt("sql", "' OR '1'='1' --", "10.0.0.1", "/api/login")
    
    print("✅ Security audit logging system tested")