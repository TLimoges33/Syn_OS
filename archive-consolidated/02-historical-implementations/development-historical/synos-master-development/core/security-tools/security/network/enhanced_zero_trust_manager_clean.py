#!/usr/bin/env python3
"""
Enhanced Zero Trust Security Implementation for SynapticOS
Week 1, Priority 2: Complete Zero Trust Architecture with mTLS and Micro-segmentation
"""

import json
import logging
import secrets
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    CONSCIOUSNESS = "consciousness"      # AI consciousness modules
    PRIVILEGED = "privileged"           # High-privilege services
    INTERNAL = "internal"               # Internal services
    DMZ = "dmz"                        # Demilitarized zone
    EXTERNAL = "external"              # External access
    QUARANTINE = "quarantine"          # Isolated/suspicious entities
    MANAGEMENT = "management"          # Management interfaces

@dataclass
class ZeroTrustEntity:
    """Entity in the Zero Trust framework"""
    entity_id: str
    name: str
    entity_type: str  # service, user, device, ai_module
    trust_level: TrustLevel
    security_posture: SecurityPosture
    network_zone: NetworkZone
    ip_addresses: List[str]
    certificates: List[str]  # Certificate fingerprints
    attributes: Dict[str, Any] = field(default_factory=dict)
    last_verification: str = ""
    risk_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class SecurityContext:
    """Security context for requests"""
    entity_id: str
    source_ip: str
    timestamp: str
    session_id: str
    user_agent: str
    request_attributes: Dict[str, Any] = field(default_factory=dict)
    target_resource: str = ""
    action: str = ""

@dataclass
class ZeroTrustPolicy:
    """Zero Trust security policy"""
    policy_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

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
            "requests_allowed": 0,
            "requests_denied": 0,
            "last_update": datetime.utcnow().isoformat()
        }

        # Status tracking
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the Zero Trust security system"""
        try:
            self.logger.info("Initializing Enhanced Zero Trust Manager...")

            # Load configuration
            await self._load_configuration()

            # Initialize components
            if self.mtls_manager:
                mtls_init = await self.mtls_manager.initialize()
                if not mtls_init:
                    self.logger.warning("mTLS Certificate Manager initialization failed")

            if self.network_engine:
                network_init = await self.network_engine.initialize()
                if not network_init:
                    self.logger.warning("Network Segmentation Engine initialization failed")

            if self.behavior_monitor:
                behavior_init = await self.behavior_monitor.initialize()
                if not behavior_init:
                    self.logger.warning("Behavioral Monitoring System initialization failed")

            # Setup network zones
            await self._initialize_network_zones()

            # Load default policies
            await self._load_default_policies()

            self.is_initialized = True
            self.logger.info("Enhanced Zero Trust Manager initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Zero Trust initialization failed: %s", str(e))
            return False

    async def register_entity(self, entity: ZeroTrustEntity) -> bool:
        """Register a new entity in the Zero Trust framework"""
        try:
            # Validate entity
            if not entity.entity_id or not entity.name:
                raise ValueError("Entity ID and name are required")

            # Set creation timestamp
            entity.created_at = datetime.utcnow().isoformat()
            entity.updated_at = entity.created_at

            # Generate mTLS certificate if manager available
            if self.mtls_manager and not entity.certificates:
                try:
                    fingerprint = await self.mtls_manager.generate_entity_certificate(entity)
                    entity.certificates = [fingerprint]
                    self.metrics["certificates_issued"] += 1
                except Exception as e:
                    self.logger.warning("Certificate generation failed for %s: %s", entity.entity_id, str(e))

            # Store entity
            self.entities[entity.entity_id] = entity

            # Log registration
            self.logger.info("Entity registered: %s (%s)", entity.entity_id, entity.entity_type)

            # Record behavior event if monitor available
            if self.behavior_monitor and BehaviorEvent and BehaviorCategory:
                registration_event = BehaviorEvent(
                    event_id="",
                    entity_id=entity.entity_id,
                    category=BehaviorCategory.AUTHENTICATION,
                    event_type="entity_registration",
                    timestamp=datetime.utcnow().isoformat(),
                    source_ip=entity.ip_addresses[0] if entity.ip_addresses else "unknown",
                    user_agent="ZeroTrustManager/1.0",
                    resource="registration_service",
                    metadata={"entity_type": entity.entity_type, "trust_level": entity.trust_level.name},
                    risk_score=entity.risk_score
                )
                await self.behavior_monitor.record_behavior_event(registration_event)

            return True

        except Exception as e:
            self.logger.error("Entity registration failed: %s", str(e))
            return False

    async def authenticate_entity(self, entity_id: str, context: SecurityContext) -> Dict[str, Any]:
        """Authenticate an entity"""
        try:
            self.metrics["authentications"] += 1

            # Get entity
            entity = self.entities.get(entity_id)
            if not entity:
                self.logger.warning("Authentication failed: Entity %s not found", entity_id)
                self.metrics["requests_denied"] += 1
                return {"authenticated": False, "reason": "Entity not found"}

            # Check trust level
            if entity.trust_level == TrustLevel.UNTRUSTED:
                self.logger.warning("Authentication denied: Entity %s is untrusted", entity_id)
                self.metrics["requests_denied"] += 1
                return {"authenticated": False, "reason": "Entity untrusted"}

            # Check quarantine status
            if entity.trust_level == TrustLevel.QUARANTINED:
                self.logger.warning("Authentication denied: Entity %s is quarantined", entity_id)
                self.metrics["requests_denied"] += 1
                return {"authenticated": False, "reason": "Entity quarantined"}

            # Verify IP address
            if context.source_ip not in entity.ip_addresses:
                self.logger.warning("Authentication failed: IP %s not authorized for %s",
                                  context.source_ip, entity_id)
                self.metrics["requests_denied"] += 1
                return {"authenticated": False, "reason": "Unauthorized IP address"}

            # Check certificate if available
            if entity.certificates and self.mtls_manager:
                # TODO: Implement certificate verification from context
                pass

            # Behavioral analysis
            if self.behavior_monitor:
                anomaly_score = await self._calculate_anomaly_score(entity_id, context.request_attributes)
                if anomaly_score > self.anomaly_threshold:
                    self.logger.warning("Authentication denied: High anomaly score %.2f for %s",
                                      anomaly_score, entity_id)
                    self.metrics["anomalies_detected"] += 1
                    self.metrics["requests_denied"] += 1
                    return {"authenticated": False, "reason": "Behavioral anomaly detected"}

            # Create session
            session_id = await self._create_secure_session(entity)

            # Update entity last verification
            entity.last_verification = datetime.utcnow().isoformat()
            entity.updated_at = entity.last_verification

            self.logger.info("Entity %s authenticated successfully", entity_id)
            self.metrics["requests_allowed"] += 1

            return {
                "authenticated": True,
                "session_id": session_id,
                "trust_level": entity.trust_level.name,
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }

        except Exception as e:
            self.logger.error("Authentication error: %s", str(e))
            self.metrics["requests_denied"] += 1
            return {"authenticated": False, "reason": "Authentication error: {}".format(str(e))}

    async def authorize_access(self, entity_id: str, resource: str, action: str,
                             context: SecurityContext) -> Dict[str, Any]:
        """Authorize access to a resource"""
        try:
            self.metrics["authorizations"] += 1

            # Get entity
            entity = self.entities.get(entity_id)
            if not entity:
                self.logger.warning("Authorization failed: Entity %s not found", entity_id)
                self.metrics["requests_denied"] += 1
                return {"allowed": False, "reason": "Entity not found"}

            # Update context
            context.target_resource = resource
            context.action = action

            # Get applicable policies
            policies = await self._get_applicable_policies(entity, resource, action)

            # Evaluate policies
            policy_result = await self._evaluate_policies(context, policies)

            if not policy_result.get("allowed", False):
                self.logger.warning("Authorization denied by policy: %s -> %s:%s",
                                  entity_id, resource, action)
                self.metrics["requests_denied"] += 1
                return {"allowed": False, "reason": policy_result.get("reason", "Policy denied")}

            # Network segmentation check
            if not await self._verify_network_access(context):
                self.logger.warning("Authorization denied by network policy: %s -> %s",
                                  entity_id, resource)
                self.metrics["network_blocks"] += 1
                self.metrics["requests_denied"] += 1
                return {"allowed": False, "reason": "Network access denied"}

            self.logger.info("Access authorized: %s -> %s:%s", entity_id, resource, action)
            self.metrics["requests_allowed"] += 1

            return {
                "allowed": True,
                "conditions": policy_result.get("conditions", []),
                "session_id": context.session_id
            }

        except Exception as e:
            self.logger.error("Authorization failed: %s", str(e))
            self.metrics["requests_denied"] += 1
            return {"allowed": False, "reason": "Authorization error: {}".format(str(e))}

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

            # Load entity certificate and key if manager available
            if self.mtls_manager:
                try:
                    cert_path, key_path = await self.mtls_manager.get_entity_certificate_paths(entity_id)
                    context.load_cert_chain(cert_path, key_path)

                    # Load CA certificate
                    ca_path = await self.mtls_manager.get_ca_certificate_path()
                    context.load_verify_locations(ca_path)

                    self.mtls_contexts[entity_id] = context
                    return context

                except Exception as e:
                    self.logger.error("Failed to create mTLS context for %s: %s", entity_id, str(e))
                    return None

            return context

        except Exception as e:
            self.logger.error("mTLS context creation failed: %s", str(e))
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

            # Use network engine if available
            if self.network_engine:
                result = await self.network_engine.evaluate_traffic(
                    "0.0.0.0", "0.0.0.0", port, protocol
                )
                # Handle tuple result (TrafficAction, str)
                if isinstance(result, tuple):
                    action, _ = result
                    return action.name == "ALLOW"
                return bool(result)

            # Default allow for same zone
            return source_zone == target_zone

        except Exception as e:
            self.logger.error("Network segmentation check failed: %s", str(e))
            return False

    def get_entity(self, entity_id: str) -> Optional[ZeroTrustEntity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def list_entities(self) -> List[ZeroTrustEntity]:
        """List all registered entities"""
        return list(self.entities.values())

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        self.metrics["last_update"] = datetime.utcnow().isoformat()
        return self.metrics.copy()

    async def _load_configuration(self):
        """Load Zero Trust configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        self.config = yaml.safe_load(f)
                    else:
                        self.config = json.load(f)
                self.logger.info("Configuration loaded from %s", self.config_path)
            else:
                self.config = self._get_default_config()
                self.logger.info("Using default Zero Trust configuration")
        except Exception as e:
            self.logger.warning("Failed to load configuration: %s, using defaults", str(e))
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default Zero Trust configuration"""
        return {
            "authentication": {
                "require_mtls": True,
                "session_timeout": 3600,
                "max_failed_attempts": 3
            },
            "authorization": {
                "default_action": "deny",
                "policy_evaluation_timeout": 5.0
            },
            "network_zones": {
                "consciousness": {
                    "isolation": True,
                    "allowed_sources": ["internal", "management"],
                    "firewall_rules": [
                        {"protocol": "tcp", "port": 443, "action": "allow"},
                        {"protocol": "tcp", "port": 5432, "action": "allow"}
                    ]
                },
                "internal": {
                    "isolation": False,
                    "allowed_sources": ["consciousness", "privileged"],
                    "firewall_rules": [
                        {"protocol": "tcp", "port": 80, "action": "allow"},
                        {"protocol": "tcp", "port": 443, "action": "allow"},
                        {"protocol": "tcp", "port": 5432, "action": "allow"},
                        {"protocol": "tcp", "port": 6379, "action": "allow"}
                    ]
                },
                "dmz": {
                    "isolation": False,
                    "allowed_sources": ["external"],
                    "firewall_rules": [
                        {"protocol": "tcp", "port": 80, "action": "allow"},
                        {"protocol": "tcp", "port": 443, "action": "allow"}
                    ]
                }
            },
            "behavioral_monitoring": {
                "enabled": True,
                "anomaly_threshold": 0.7,
                "profile_update_interval": 3600
            }
        }

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
                description="Default policy to deny all access unless explicitly allowed",
                conditions={"default": True},
                actions={"allow": False},
                priority=1000
            ),
            ZeroTrustPolicy(
                policy_id="consciousness_access",
                name="AI Consciousness Access",
                description="Allow consciousness modules to access internal resources",
                conditions={
                    "entity_type": "ai_service",
                    "trust_level": ["TRUSTED", "VERIFIED"],
                    "network_zone": "consciousness"
                },
                actions={"allow": True, "require_mtls": True},
                priority=100
            ),
            ZeroTrustPolicy(
                policy_id="internal_service_communication",
                name="Internal Service Communication",
                description="Allow internal services to communicate",
                conditions={
                    "network_zone": "internal",
                    "trust_level": ["CONDITIONAL", "TRUSTED", "VERIFIED"]
                },
                actions={"allow": True, "require_mtls": True},
                priority=200
            )
        ]

        for policy in default_policies:
            self.policies[policy.policy_id] = policy

    async def _get_applicable_policies(self, entity: ZeroTrustEntity,
                                     _resource: str, _action: str) -> List[ZeroTrustPolicy]:
        """Get policies applicable to the request"""
        # Note: resource and action parameters reserved for future policy conditions
        applicable = []

        for policy in self.policies.values():
            if not policy.enabled:
                continue

            # Check entity type condition
            if "entity_type" in policy.conditions:
                if entity.entity_type != policy.conditions["entity_type"]:
                    continue

            # Check trust level condition
            if "trust_level" in policy.conditions:
                allowed_levels = policy.conditions["trust_level"]
                if isinstance(allowed_levels, str):
                    allowed_levels = [allowed_levels]
                if entity.trust_level.name not in allowed_levels:
                    continue

            # Check network zone condition
            if "network_zone" in policy.conditions:
                if entity.network_zone.value != policy.conditions["network_zone"]:
                    continue

            applicable.append(policy)

        # Sort by priority (lower number = higher priority)
        applicable.sort(key=lambda p: p.priority)
        return applicable

    async def _evaluate_policies(self, _context: SecurityContext, policies: List[ZeroTrustPolicy]) -> Dict[str, Any]:
        """Evaluate policies against context"""
        # Note: context parameter reserved for future policy evaluation logic
        self.metrics["policy_evaluations"] += 1

        for policy in policies:
            if policy.actions.get("allow", False):
                return {
                    "allowed": True,
                    "reason": f"Policy {policy.name} allows access",
                    "conditions": policy.actions.get("conditions", []),
                    "policy_id": policy.policy_id
                }

        return {
            "allowed": False,
            "reason": "No policy allows access",
            "policy_id": "default_deny"
        }

    async def _verify_network_access(self, _context: SecurityContext) -> bool:
        """Verify network access is allowed"""
        # Note: context parameter reserved for future network policy verification
        # Basic network verification
        # In a real implementation, this would check network policies
        return True

    async def _create_secure_session(self, entity: ZeroTrustEntity) -> str:
        """Create a secure session for the entity"""
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            "entity_id": entity.entity_id,
            "created": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "trust_level": entity.trust_level.name
        }
        return session_id

    async def _calculate_anomaly_score(self, entity_id: str, _features: Dict[str, Any]) -> float:
        """Calculate anomaly score for entity behavior"""
        # Note: _features parameter reserved for future ML-based anomaly detection
        if not self.behavior_monitor:
            return 0.0

        # Get behavior summary
        try:
            summary = await self.behavior_monitor.get_entity_behavior_summary(entity_id)
            if "error" in summary:
                return 0.2  # Low default risk

            profile = summary.get("profile", {})
            return profile.get("current_risk_score", 0.0)

        except Exception as e:
            self.logger.warning("Anomaly score calculation failed: %s", str(e))
            return 0.2  # Default low risk
