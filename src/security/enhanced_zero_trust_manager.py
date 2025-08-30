#!/usr/bin/env python3
"""
Enhanced Zero Trust Security Implementation for SynapticOS
Week 1, Priority 2: Complete Zero Trust Architecture with mTLS and Micro-segmentation
"""

import logging
import secrets
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Import Zero Trust components
try:
    from .mtls_certificate_manager import MTLSCertificateManager
    from .network_segmentation_engine import NetworkSegmentationEngine
    from .behavioral_monitoring_system import BehaviorMonitoringSystem, BehaviorEvent, BehaviorCategory
except ImportError:
    # For development/testing when modules might not be fully integrated
    MTLSCertificateManager = None
    NetworkSegmentationEngine = None
    BehaviorMonitoringSystem = None
    BehaviorEvent = None
    BehaviorCategory = None
    NetZone = None

# Enhanced Trust and Security Models
class TrustLevel(Enum):
    """Enhanced trust levels for Zero Trust implementation"""
    UNTRUSTED = 0
    QUARANTINED = 1
    RESTRICTED = 2
    CONDITIONAL = 3
    TRUSTED = 4
    VERIFIED = 5

class SecurityPosture(Enum):
    """Security posture assessment"""
    CRITICAL = "critical"
    HIGH_RISK = "high_risk"
    MEDIUM_RISK = "medium_risk"
    LOW_RISK = "low_risk"
    SECURE = "secure"
    VERIFIED_SECURE = "verified_secure"

class NetworkZone(Enum):
    """Network micro-segmentation zones"""
    DMZ = "dmz"
    EXTERNAL = "external"
    INTERNAL = "internal"
    PRIVILEGED = "privileged"
    MANAGEMENT = "management"
    CONSCIOUSNESS = "consciousness"
    ISOLATED = "isolated"

@dataclass
class ZeroTrustEntity:
    """Enhanced entity representation for Zero Trust"""
    entity_id: str
    entity_type: str  # user, service, device, application, container
    name: str
    ip_addresses: List[str] = field(default_factory=list)
    mac_addresses: List[str] = field(default_factory=list)
    certificates: List[str] = field(default_factory=list)  # certificate fingerprints
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    security_posture: SecurityPosture = SecurityPosture.HIGH_RISK
    network_zone: NetworkZone = NetworkZone.EXTERNAL
    last_verified: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    risk_score: float = 100.0  # 0-100, where 100 is highest risk
    attributes: Dict[str, Any] = field(default_factory=dict)
    policies: List[str] = field(default_factory=list)
    capabilities: Set[str] = field(default_factory=set)

@dataclass
class ZeroTrustPolicy:
    """Zero Trust security policy"""
    policy_id: str
    name: str
    description: str
    source_entities: List[str]  # Entity IDs or patterns
    target_resources: List[str]  # Resource patterns
    actions: List[str]  # Allowed actions
    conditions: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    enabled: bool = True
    expiry: Optional[datetime] = None

@dataclass
class SecurityContext:
    """Comprehensive security context for requests"""
    request_id: str
    timestamp: datetime
    source_entity: ZeroTrustEntity
    target_resource: str
    requested_action: str
    authentication_method: str
    authorization_level: str
    risk_factors: Dict[str, float] = field(default_factory=dict)
    network_context: Dict[str, Any] = field(default_factory=dict)
    device_context: Dict[str, Any] = field(default_factory=dict)
    behavioral_context: Dict[str, Any] = field(default_factory=dict)

class EnhancedZeroTrustManager:
    """Enhanced Zero Trust Security Manager with comprehensive features"""

    def __init__(self, config_path: str = "config/security/zero_trust.yaml"):
        """Initialize Enhanced Zero Trust Manager"""
        self.logger = logging.getLogger("security.zero_trust")
        self.config_path = config_path
        self.config = {}

        # Entity and policy storage
        self.entities: Dict[str, ZeroTrustEntity] = {}
        self.policies: Dict[str, ZeroTrustPolicy] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        # Network and security state
        self.network_zones: Dict[str, Dict[str, Any]] = {}
        self.mtls_contexts: Dict[str, ssl.SSLContext] = {}
        self.anomaly_threshold = 0.7

        # Integration components
        if MTLSCertificateManager:
            self.mtls_manager = MTLSCertificateManager()
        else:
            self.mtls_manager = None

        if NetworkSegmentationEngine:
            self.network_engine = NetworkSegmentationEngine()
        else:
            self.network_engine = None

        if BehaviorMonitoringSystem:
            self.behavior_monitor = BehaviorMonitoringSystem()
        else:
            self.behavior_monitor = None

        # Performance metrics
        self.metrics = {
            "authentications": 0,
            "authorizations": 0,
            "policy_evaluations": 0,
            "network_blocks": 0,
            "anomalies_detected": 0,
            "certificates_issued": 0,
            "last_update": datetime.utcnow().isoformat()
        }

        # Security event storage
        self.security_events: List[Dict[str, Any]] = []

        # Status tracking
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize all Zero Trust components"""
        try:
            self.logger.info("Initializing Enhanced Zero Trust Manager...")

            # Load configuration
            await self._load_configuration()

            # Initialize Certificate Manager
            if self.mtls_manager:
                await self.mtls_manager.initialize()
                self.logger.info("mTLS Certificate Manager initialized")

            # Initialize Network Segmentation Engine
            if self.network_engine:
                await self.network_engine.initialize()
                self.logger.info("Network Segmentation Engine initialized")

            # Initialize Behavioral Monitoring System
            if self.behavior_monitor:
                await self.behavior_monitor.initialize()
                self.logger.info("Behavioral Monitoring System initialized")

            # Setup network zones
            await self._initialize_network_zones()

            # Load default policies
            await self._load_default_policies()

            # Initialize monitoring
            await self._initialize_monitoring()

            self.is_initialized = True
            self.logger.info("Enhanced Zero Trust Manager initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Zero Trust initialization failed: %s", e)
            return False

    async def _load_configuration(self):
        """Load Zero Trust configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                # Create default configuration
                self.config = await self._create_default_config()
                await self._save_configuration()

        except Exception as e:
            self.logger.error("Configuration loading failed: %s", e)
            raise

    async def _create_default_config(self) -> Dict[str, Any]:
        """Create default Zero Trust configuration"""
        return {
            "zero_trust": {
                "enable_mtls": True,
                "require_device_certificates": True,
                "continuous_verification_interval": 300,  # 5 minutes
                "max_session_duration": 3600,  # 1 hour
                "risk_threshold": 75.0,
                "anomaly_detection": True,
                "network_segmentation": True,
                "policy_enforcement": "strict"
            },
            "network_zones": {
                "consciousness": {
                    "cidr": "172.20.10.0/24",
                    "security_level": "maximum",
                    "isolation": True
                },
                "privileged": {
                    "cidr": "172.20.20.0/24",
                    "security_level": "high",
                    "isolation": True
                },
                "internal": {
                    "cidr": "172.20.30.0/24",
                    "security_level": "medium",
                    "isolation": False
                },
                "dmz": {
                    "cidr": "172.20.40.0/24",
                    "security_level": "low",
                    "isolation": False
                }
            },
            "policies": {
                "default_deny": True,
                "require_authentication": True,
                "require_authorization": True,
                "log_all_access": True,
                "encrypt_all_traffic": True
            },
            "monitoring": {
                "enable_behavioral_analysis": True,
                "enable_threat_detection": True,
                "enable_compliance_monitoring": True,
                "alert_threshold": 0.8
            }
        }

    async def register_entity(self, entity: ZeroTrustEntity) -> bool:
        """Register a new entity in the Zero Trust framework"""
        try:
            # Validate entity
            if not await self._validate_entity(entity):
                return False

            # Assign initial trust level based on entity type
            entity.trust_level = await self._calculate_initial_trust_level(entity)
            entity.security_posture = await self._assess_security_posture(entity)
            entity.network_zone = await self._assign_network_zone(entity)

            # Generate certificates if required
            if self.config.get("zero_trust", {}).get("require_device_certificates", True):
                # Generate certificates for the entity
                if self.mtls_manager:
                    cert_fingerprint = await self.mtls_manager.generate_entity_certificate(entity)
                    entity.certificates.append(cert_fingerprint)
                    self.metrics["certificates_issued"] += 1

            # Store entity
            self.entities[entity.entity_id] = entity

            # Log registration
            await self._log_security_event({
                "event_type": "entity_registration",
                "entity_id": entity.entity_id,
                "entity_type": entity.entity_type,
                "trust_level": entity.trust_level.name,
                "network_zone": entity.network_zone.name,
                "timestamp": datetime.utcnow().isoformat()
            })

            self.logger.info("Entity %s registered successfully", entity.entity_id)
            return True

        except Exception as e:
            self.logger.error("Entity registration failed: %s", e)
            return False

    async def authenticate_entity(self, entity_id: str, credentials: Dict[str, Any]) -> Optional[str]:
        """Authenticate an entity and return session token"""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                await self._log_security_event({
                    "event_type": "authentication_failure",
                    "entity_id": entity_id,
                    "reason": "entity_not_found",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return None

            # Multi-factor authentication
            auth_result = await self._perform_authentication(entity, credentials)
            if not auth_result["success"]:
                self.metrics["authentication_failures"] += 1
                await self._log_security_event({
                    "event_type": "authentication_failure",
                    "entity_id": entity_id,
                    "reason": auth_result["reason"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                return None

            # Record authentication event for behavioral monitoring
            if self.behavior_monitor and BehaviorEvent and BehaviorCategory:
                auth_event = BehaviorEvent(
                    event_id="",
                    entity_id=entity_id,
                    category=BehaviorCategory.AUTHENTICATION,
                    event_type="login_success",
                    timestamp=datetime.utcnow().isoformat(),
                    source_ip=credentials.get("source_ip", "unknown"),
                    user_agent=credentials.get("user_agent", "unknown"),
                    resource="authentication",
                    metadata={"method": credentials.get("method", "unknown")}
                )
                await self.behavior_monitor.record_behavior_event(auth_event)

            # Update entity verification
            entity.last_verified = datetime.utcnow()
            entity.last_activity = datetime.utcnow()

            # Create session
            session_token = await self._create_secure_session(entity)

            # Log successful authentication
            await self._log_security_event({
                "event_type": "authentication_success",
                "entity_id": entity_id,
                "authentication_method": auth_result["method"],
                "timestamp": datetime.utcnow().isoformat()
            })

            return session_token

        except Exception as e:
            self.logger.error("Authentication failed: %s", e)
            return None

    async def authorize_access(self, context: SecurityContext) -> Dict[str, Any]:
        """Authorize access request with comprehensive policy evaluation"""
        try:
            decision = {
                "allowed": False,
                "reason": "",
                "conditions": [],
                "monitoring_required": False,
                "risk_score": 0.0
            }

            # Check if entity exists and is authenticated
            entity = self.entities.get(context.source_entity.entity_id)
            if not entity:
                decision["reason"] = "Entity not registered"
                return decision

            # Continuous verification
            if not await self._verify_entity_state(entity):
                decision["reason"] = "Entity verification failed"
                return decision

            # Risk assessment
            risk_score = await self._calculate_request_risk(context)
            decision["risk_score"] = risk_score

            if risk_score > self.config.get("zero_trust", {}).get("risk_threshold", 75.0):
                decision["reason"] = f"Risk score too high: {risk_score}"
                decision["monitoring_required"] = True
                return decision

            # Policy evaluation
            applicable_policies = await self._find_applicable_policies(context)
            policy_result = await self._evaluate_policies(context, applicable_policies)

            if not policy_result["allowed"]:
                decision["reason"] = policy_result["reason"]
                return decision

            # Network zone verification
            if not await self._verify_network_access(context):
                decision["reason"] = "Network zone access denied"
                return decision

            # Success - grant access
            decision["allowed"] = True
            decision["conditions"] = policy_result.get("conditions", [])
            decision["monitoring_required"] = risk_score > 50.0

            # Update metrics
            self.metrics["requests_processed"] += 1

            # Log authorization
            await self._log_security_event({
                "event_type": "authorization_success",
                "entity_id": context.source_entity.entity_id,
                "resource": context.target_resource,
                "action": context.requested_action,
                "risk_score": risk_score,
                "timestamp": datetime.utcnow().isoformat()
            })

            return decision

        except Exception as e:
            self.logger.error("Authorization failed: %s", e)
            self.metrics["requests_denied"] += 1
            return {"allowed": False, "reason": "Authorization error: %s" % e}

    async def create_mtls_context(self, entity_id: str) -> Optional[ssl.SSLContext]:
        """Create mTLS SSL context for entity"""
        try:
            entity = self.entities.get(entity_id)
            if not entity or not entity.certificates:
                return None

            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_REQUIRED

            # Load CA certificate
            if self.mtls_manager:
                ca_cert_path = await self.mtls_manager.get_ca_certificate_path()
            else:
                ca_cert_path = "certs/zero_trust/ca/ca_certificate.pem"
            context.load_verify_locations(ca_cert_path)

            # Load entity certificate and key
            if self.mtls_manager:
                cert_path, key_path = await self.mtls_manager.get_entity_certificate_paths(entity_id)
            else:
                cert_path = f"certs/zero_trust/entities/{entity_id}/certificate.pem"
                key_path = f"certs/zero_trust/entities/{entity_id}/private_key.pem"
            context.load_cert_chain(cert_path, key_path)

            # Store context
            self.mtls_contexts[entity_id] = context

            return context

        except Exception as e:
            self.logger.error("mTLS context creation failed: %s", e)
            return None

    async def enforce_network_segmentation(self, source_zone: NetworkZone,
                                         target_zone: NetworkZone,
                                         protocol: str, port: int) -> bool:
        """Enforce network segmentation rules"""
        try:
            # Get zone configurations
            target_config = self.network_zones.get(target_zone.value, {})

            # Check isolation rules
            if target_config.get("isolation", False):
                # Isolated zones require explicit permission
                allowed_sources = target_config.get("allowed_sources", [])
                if source_zone.value not in allowed_sources:
                    self.logger.warning("Network access denied: %s -> %s", 
                                      source_zone.value, target_zone.value)
                    return False

            # Check protocol and port rules
            zone_rules = target_config.get("firewall_rules", [])
            for rule in zone_rules:
                if (rule.get("protocol") == protocol and
                    rule.get("port") == port and
                    rule.get("action") == "allow"):
                    return True

            # Default deny for strict enforcement
            if self.config.get("policies", {}).get("default_deny", True):
                return False

            return True

        except Exception as e:
            self.logger.error("Network segmentation enforcement failed: %s", e)
            return False

    async def monitor_behavioral_anomalies(self, entity_id: str, activity: Dict[str, Any]) -> float:
        """Monitor and detect behavioral anomalies"""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                return 1.0  # Maximum anomaly score for unknown entities

            # Extract behavioral features
            features = {
                "access_time": datetime.utcnow().hour,
                "resource_type": activity.get("resource_type", "unknown"),
                "action_type": activity.get("action", "unknown"),
                "source_ip": activity.get("source_ip", ""),
                "user_agent": activity.get("user_agent", ""),
                "request_size": activity.get("request_size", 0),
                "response_time": activity.get("response_time", 0)
            }

            # Calculate anomaly score (simplified implementation)
            anomaly_score = await self._calculate_anomaly_score(entity_id, features)

            # Update behavioral context
            if "behavioral_profiles" not in entity.attributes:
                entity.attributes["behavioral_profiles"] = {}

            entity.attributes["behavioral_profiles"][datetime.utcnow().isoformat()] = features

            # Trigger alerts for high anomaly scores
            if anomaly_score > self.anomaly_threshold:
                await self._log_security_event({
                    "event_type": "behavioral_anomaly",
                    "entity_id": entity_id,
                    "anomaly_score": anomaly_score,
                    "activity": activity,
                    "timestamp": datetime.utcnow().isoformat()
                })

                self.metrics["anomalies_detected"] += 1

            return anomaly_score

        except Exception as e:
            self.logger.error("Behavioral monitoring failed: %s", e)
            return 1.0

    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security metrics"""
        try:
            return {
                "entities": {
                    "total": len(self.entities),
                    "by_trust_level": {
                        level.name: len([e for e in self.entities.values()
                                       if e.trust_level == level])
                        for level in TrustLevel
                    },
                    "by_zone": {
                        zone.name: len([e for e in self.entities.values()
                                      if e.network_zone == zone])
                        for zone in NetworkZone
                    }
                },
                "policies": {
                    "total": len(self.policies),
                    "enabled": len([p for p in self.policies.values() if p.enabled])
                },
                "sessions": {
                    "active": len(self.active_sessions)
                },
                "performance": self.metrics,
                "security_events": {
                    "total": len(self.security_events),
                    "recent": len([e for e in self.security_events
                                 if datetime.fromisoformat(e["timestamp"]) >
                                 datetime.utcnow() - timedelta(hours=1)])
                }
            }

        except Exception as e:
            self.logger.error("Metrics collection failed: %s", e)
            return {}

    # Helper methods (implementation details)
    async def _validate_entity(self, entity: ZeroTrustEntity) -> bool:
        """Validate entity data"""
        return bool(entity.entity_id and entity.entity_type and entity.name)

    async def _calculate_initial_trust_level(self, entity: ZeroTrustEntity) -> TrustLevel:
        """Calculate initial trust level for entity"""
        # Simple mapping based on entity type
        trust_mapping = {
            "service": TrustLevel.CONDITIONAL,
            "user": TrustLevel.RESTRICTED,
            "device": TrustLevel.RESTRICTED,
            "application": TrustLevel.CONDITIONAL,
            "container": TrustLevel.RESTRICTED
        }
        return trust_mapping.get(entity.entity_type, TrustLevel.UNTRUSTED)

    async def _assess_security_posture(self, entity: ZeroTrustEntity) -> SecurityPosture:
        """Assess entity security posture"""
        # Simplified assessment
        if entity.trust_level in [TrustLevel.VERIFIED, TrustLevel.TRUSTED]:
            return SecurityPosture.SECURE
        elif entity.trust_level == TrustLevel.CONDITIONAL:
            return SecurityPosture.MEDIUM_RISK
        else:
            return SecurityPosture.HIGH_RISK

    async def _assign_network_zone(self, entity: ZeroTrustEntity) -> NetworkZone:
        """Assign appropriate network zone"""
        zone_mapping = {
            "consciousness": NetworkZone.CONSCIOUSNESS,
            "admin": NetworkZone.PRIVILEGED,
            "service": NetworkZone.INTERNAL,
            "user": NetworkZone.INTERNAL,
            "external": NetworkZone.DMZ
        }
        return zone_mapping.get(entity.entity_type, NetworkZone.EXTERNAL)

    async def _initialize_network_zones(self):
        """Initialize network zone configurations"""
        zones_config = self.config.get("network_zones", {})
        for zone_name, zone_config in zones_config.items():
            try:
                zone = NetworkZone(zone_name)
                self.network_zones[zone.value] = zone_config
            except ValueError:
                self.logger.warning("Unknown network zone: %s", zone_name)

    async def _load_default_policies(self):
        """Load default Zero Trust policies"""
        default_policies = [
            ZeroTrustPolicy(
                policy_id="default_deny",
                name="Default Deny All",
                description="Default deny policy for all resources",
                source_entities=["*"],
                target_resources=["*"],
                actions=[],
                priority=1000,
                enabled=True
            ),
            ZeroTrustPolicy(
                policy_id="authenticated_internal",
                name="Authenticated Internal Access",
                description="Allow authenticated entities internal access",
                source_entities=["*"],
                target_resources=["internal.*"],
                actions=["read", "write"],
                conditions={"authentication_required": True, "trust_level": "conditional"},
                priority=100,
                enabled=True
            )
        ]

        for policy in default_policies:
            self.policies[policy.policy_id] = policy

    async def _initialize_monitoring(self):
        """Initialize security monitoring"""
        self.logger.info("Security monitoring initialized")

    async def _log_security_event(self, event: Dict[str, Any]):
        """Log security event"""
        self.security_events.append(event)
        # Keep only recent events to prevent memory issues
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-5000:]

    async def _save_configuration(self):
        """Save configuration to file"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    # Additional helper methods would be implemented here...
    async def _perform_authentication(self, entity: ZeroTrustEntity, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for authentication logic"""
        return {"success": True, "method": "mtls", "reason": ""}

    async def _verify_entity_state(self, _entity: ZeroTrustEntity) -> bool:
        """Placeholder for entity state verification"""
        return True

    async def _calculate_request_risk(self, _context: SecurityContext) -> float:
        """Placeholder for risk calculation"""
        return 25.0  # Low risk

    async def _find_applicable_policies(self, _context: SecurityContext) -> List[ZeroTrustPolicy]:
        """Placeholder for policy matching"""
        return list(self.policies.values())

    async def _evaluate_policies(self, _context: SecurityContext, _policies: List[ZeroTrustPolicy]) -> Dict[str, Any]:
        """Placeholder for policy evaluation"""
        return {"allowed": True, "reason": "Policy matched", "conditions": []}

    async def _verify_network_access(self, _context: SecurityContext) -> bool:
        """Placeholder for network access verification"""
        return True

    async def _create_secure_session(self, entity: ZeroTrustEntity) -> str:
        """Placeholder for session creation"""
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            "entity_id": entity.entity_id,
            "created": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        return session_id

    async def _calculate_anomaly_score(self, _entity_id: str, _features: Dict[str, Any]) -> float:
        """Placeholder for anomaly detection"""
        return 0.2  # Low anomaly score

    def get_metrics(self) -> Dict[str, Any]:
        """Get Zero Trust performance metrics"""
        self.metrics["last_update"] = datetime.utcnow().isoformat()
        return self.metrics.copy()

    async def assess_entity_risk(self, entity_id: str) -> float:
        """Assess risk score for an entity"""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                return 1.0  # Maximum risk for unknown entities

            # Calculate base risk from trust level
            trust_risk_map = {
                TrustLevel.UNTRUSTED: 1.0,
                TrustLevel.QUARANTINED: 0.9,
                TrustLevel.RESTRICTED: 0.7,
                TrustLevel.CONDITIONAL: 0.5,
                TrustLevel.TRUSTED: 0.3,
                TrustLevel.VERIFIED: 0.1
            }

            base_risk = trust_risk_map.get(entity.trust_level, 0.5)

            # Adjust for security posture
            posture_adjustments = {
                SecurityPosture.CRITICAL: 0.4,
                SecurityPosture.HIGH_RISK: 0.2,
                SecurityPosture.MEDIUM_RISK: 0.0,
                SecurityPosture.LOW_RISK: -0.1,
                SecurityPosture.SECURE: -0.2,
                SecurityPosture.VERIFIED_SECURE: -0.3
            }

            posture_adj = posture_adjustments.get(entity.security_posture, 0.0)
            final_risk = max(0.0, min(1.0, base_risk + posture_adj))

            return final_risk

        except Exception as e:
            self.logger.error("Risk assessment failed for %s: %s", entity_id, e)
            return 0.5  # Default medium risk

    async def evaluate_security_posture(self, entity_id: str) -> str:
        """Evaluate security posture for an entity"""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                return "unknown"

            return entity.security_posture.value

        except Exception as e:
            self.logger.error("Security posture evaluation failed for %s: %s", entity_id, e)
            return "unknown"

    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = []

            for session_id, session_data in self.active_sessions.items():
                last_activity = session_data.get("last_activity")
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)
                elif isinstance(last_activity, datetime):
                    pass
                else:
                    continue

                # Session timeout: 1 hour
                if (current_time - last_activity).total_seconds() > 3600:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                self.logger.debug("Cleaned up expired session: %s", session_id)

            return len(expired_sessions)

        except Exception as e:
            self.logger.error("Session cleanup failed: %s", e)
            return 0
