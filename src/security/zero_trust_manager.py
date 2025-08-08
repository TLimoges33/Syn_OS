#!/usr/bin/env python3
"""
Zero-Trust Network Architecture Manager
Implements "never trust, always verify" security model with continuous authentication
"""

import asyncio
import logging
import json
import time
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress
import ssl
import socket
from datetime import datetime, timedelta
import aiohttp
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

class TrustLevel(Enum):
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4

class AccessDecision(Enum):
    DENY = "deny"
    ALLOW = "allow"
    CHALLENGE = "challenge"
    MONITOR = "monitor"

@dataclass
class NetworkEntity:
    entity_id: str
    entity_type: str  # user, device, service, application
    ip_address: str
    mac_address: Optional[str] = None
    certificate_fingerprint: Optional[str] = None
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    last_verified: Optional[datetime] = None
    risk_score: float = 0.0
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

@dataclass
class AccessRequest:
    request_id: str
    source_entity: NetworkEntity
    target_resource: str
    requested_action: str
    timestamp: datetime
    context: Dict[str, Any]
    decision: Optional[AccessDecision] = None
    reason: Optional[str] = None

@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int = 100
    enabled: bool = True

class CertificateManager:
    """Manages mTLS certificates for zero-trust authentication"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.zero_trust.certs")
        self.ca_private_key = None
        self.ca_certificate = None
        self.cert_storage_path = "certs/zero_trust"
        self._ensure_cert_storage()
    
    def _ensure_cert_storage(self):
        """Ensure certificate storage directory exists"""
        import os
        os.makedirs(self.cert_storage_path, mode=0o700, exist_ok=True)
    
    async def initialize_ca(self) -> bool:
        """Initialize Certificate Authority for zero-trust"""
        try:
            # Generate CA private key
            self.ca_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            
            # Create CA certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Secure"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "ZeroTrust"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Syn_OS"),
                x509.NameAttribute(NameOID.COMMON_NAME, "Syn_OS Zero-Trust CA"),
            ])
            
            self.ca_certificate = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                self.ca_private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=3650)  # 10 years
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=False,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).sign(self.ca_private_key, hashes.SHA256(), default_backend())
            
            # Save CA certificate and key
            await self._save_ca_files()
            
            self.logger.info("Zero-Trust CA initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"CA initialization failed: {e}")
            return False
    
    async def _save_ca_files(self):
        """Save CA certificate and private key to files"""
        # Save CA private key
        ca_key_pem = self.ca_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(f"{self.cert_storage_path}/ca_private_key.pem", 'wb') as f:
            f.write(ca_key_pem)
        
        # Save CA certificate
        ca_cert_pem = self.ca_certificate.public_bytes(serialization.Encoding.PEM)
        
        with open(f"{self.cert_storage_path}/ca_certificate.pem", 'wb') as f:
            f.write(ca_cert_pem)
        
        # Set secure permissions
        import os
        os.chmod(f"{self.cert_storage_path}/ca_private_key.pem", 0o600)
        os.chmod(f"{self.cert_storage_path}/ca_certificate.pem", 0o644)
    
    async def issue_client_certificate(self, entity: NetworkEntity) -> Tuple[bytes, bytes]:
        """Issue client certificate for mTLS authentication"""
        # Generate client private key
        client_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Create client certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Syn_OS"),
            x509.NameAttribute(NameOID.COMMON_NAME, entity.entity_id),
        ])
        
        client_certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_certificate.subject
        ).public_key(
            client_private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)  # 1 year
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(entity.entity_id),
                x509.IPAddress(ipaddress.ip_address(entity.ip_address)),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).sign(self.ca_private_key, hashes.SHA256(), default_backend())
        
        # Return certificate and private key as PEM
        cert_pem = client_certificate.public_bytes(serialization.Encoding.PEM)
        key_pem = client_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return cert_pem, key_pem

class PolicyEngine:
    """Zero-Trust policy evaluation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.zero_trust.policy")
        self.policies: Dict[str, SecurityPolicy] = {}
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default zero-trust policies"""
        # Default deny policy
        self.policies["default_deny"] = SecurityPolicy(
            policy_id="default_deny",
            name="Default Deny",
            description="Deny all access by default",
            conditions={"default": True},
            actions=["deny"],
            priority=1000
        )
        
        # Untrusted entity policy
        self.policies["untrusted_deny"] = SecurityPolicy(
            policy_id="untrusted_deny",
            name="Untrusted Entity Deny",
            description="Deny access for untrusted entities",
            conditions={"trust_level": TrustLevel.UNTRUSTED.value},
            actions=["deny"],
            priority=900
        )
        
        # High trust policy
        self.policies["high_trust_allow"] = SecurityPolicy(
            policy_id="high_trust_allow",
            name="High Trust Allow",
            description="Allow access for high trust entities with monitoring",
            conditions={"trust_level": TrustLevel.HIGH.value},
            actions=["allow", "monitor"],
            priority=200
        )
        
        # Verified entity policy
        self.policies["verified_allow"] = SecurityPolicy(
            policy_id="verified_allow",
            name="Verified Entity Allow",
            description="Allow access for verified entities",
            conditions={"trust_level": TrustLevel.VERIFIED.value},
            actions=["allow"],
            priority=100
        )
    
    async def evaluate_access_request(self, request: AccessRequest) -> AccessDecision:
        """Evaluate access request against policies"""
        applicable_policies = self._get_applicable_policies(request)
        
        # Sort by priority (lower number = higher priority)
        applicable_policies.sort(key=lambda p: p.priority)
        
        for policy in applicable_policies:
            if self._policy_matches(policy, request):
                decision = self._get_policy_decision(policy)
                request.decision = decision
                request.reason = f"Policy: {policy.name}"
                
                self.logger.info(f"Access decision: {decision.value} for {request.source_entity.entity_id} -> {request.target_resource}")
                return decision
        
        # Default deny
        request.decision = AccessDecision.DENY
        request.reason = "No matching policy - default deny"
        return AccessDecision.DENY
    
    def _get_applicable_policies(self, request: AccessRequest) -> List[SecurityPolicy]:
        """Get policies applicable to the request"""
        return [policy for policy in self.policies.values() if policy.enabled]
    
    def _policy_matches(self, policy: SecurityPolicy, request: AccessRequest) -> bool:
        """Check if policy conditions match the request"""
        conditions = policy.conditions
        
        # Check trust level
        if "trust_level" in conditions:
            if request.source_entity.trust_level.value != conditions["trust_level"]:
                return False
        
        # Check entity type
        if "entity_type" in conditions:
            if request.source_entity.entity_type not in conditions["entity_type"]:
                return False
        
        # Check resource pattern
        if "resource_pattern" in conditions:
            import re
            if not re.match(conditions["resource_pattern"], request.target_resource):
                return False
        
        # Check time-based conditions
        if "time_range" in conditions:
            current_hour = datetime.now().hour
            start_hour, end_hour = conditions["time_range"]
            if not (start_hour <= current_hour <= end_hour):
                return False
        
        # Default condition matches all
        if "default" in conditions:
            return conditions["default"]
        
        return True
    
    def _get_policy_decision(self, policy: SecurityPolicy) -> AccessDecision:
        """Get access decision from policy actions"""
        if "deny" in policy.actions:
            return AccessDecision.DENY
        elif "challenge" in policy.actions:
            return AccessDecision.CHALLENGE
        elif "allow" in policy.actions:
            return AccessDecision.ALLOW
        else:
            return AccessDecision.MONITOR

class TrustEvaluator:
    """Evaluates and maintains trust levels for network entities"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.zero_trust.trust")
        self.trust_factors = {
            "certificate_valid": 0.3,
            "recent_verification": 0.2,
            "behavioral_normal": 0.2,
            "location_expected": 0.1,
            "time_expected": 0.1,
            "device_known": 0.1
        }
    
    async def evaluate_trust(self, entity: NetworkEntity, context: Dict[str, Any]) -> TrustLevel:
        """Evaluate trust level for an entity"""
        trust_score = 0.0
        
        # Certificate validation
        if entity.certificate_fingerprint and context.get("certificate_valid"):
            trust_score += self.trust_factors["certificate_valid"]
        
        # Recent verification
        if entity.last_verified:
            time_since_verification = datetime.now() - entity.last_verified
            if time_since_verification < timedelta(hours=1):
                trust_score += self.trust_factors["recent_verification"]
            elif time_since_verification < timedelta(hours=24):
                trust_score += self.trust_factors["recent_verification"] * 0.5
        
        # Behavioral analysis
        if context.get("behavioral_score", 0) > 0.7:
            trust_score += self.trust_factors["behavioral_normal"]
        
        # Location verification
        if context.get("location_expected", False):
            trust_score += self.trust_factors["location_expected"]
        
        # Time-based verification
        if context.get("time_expected", True):
            trust_score += self.trust_factors["time_expected"]
        
        # Device recognition
        if entity.mac_address and context.get("device_known", False):
            trust_score += self.trust_factors["device_known"]
        
        # Convert score to trust level
        if trust_score >= 0.9:
            return TrustLevel.VERIFIED
        elif trust_score >= 0.7:
            return TrustLevel.HIGH
        elif trust_score >= 0.5:
            return TrustLevel.MEDIUM
        elif trust_score >= 0.3:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    async def update_entity_trust(self, entity: NetworkEntity, context: Dict[str, Any]):
        """Update entity trust level and risk score"""
        new_trust_level = await self.evaluate_trust(entity, context)
        
        # Update trust level
        old_trust_level = entity.trust_level
        entity.trust_level = new_trust_level
        entity.last_verified = datetime.now()
        
        # Calculate risk score
        entity.risk_score = await self._calculate_risk_score(entity, context)
        
        if old_trust_level != new_trust_level:
            self.logger.info(f"Trust level changed for {entity.entity_id}: {old_trust_level.name} -> {new_trust_level.name}")
    
    async def _calculate_risk_score(self, entity: NetworkEntity, context: Dict[str, Any]) -> float:
        """Calculate risk score for entity"""
        risk_score = 0.0
        
        # Base risk from trust level
        trust_risk = {
            TrustLevel.UNTRUSTED: 1.0,
            TrustLevel.LOW: 0.8,
            TrustLevel.MEDIUM: 0.5,
            TrustLevel.HIGH: 0.2,
            TrustLevel.VERIFIED: 0.1
        }
        risk_score += trust_risk.get(entity.trust_level, 1.0)
        
        # Behavioral risk
        behavioral_score = context.get("behavioral_score", 0.5)
        risk_score += (1.0 - behavioral_score) * 0.3
        
        # Location risk
        if not context.get("location_expected", True):
            risk_score += 0.2
        
        # Time-based risk
        if not context.get("time_expected", True):
            risk_score += 0.1
        
        return min(risk_score, 1.0)

class ZeroTrustManager:
    """Main Zero-Trust Network Architecture Manager"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.zero_trust")
        self.certificate_manager = CertificateManager()
        self.policy_engine = PolicyEngine()
        self.trust_evaluator = TrustEvaluator()
        self.entities: Dict[str, NetworkEntity] = {}
        self.access_logs: List[AccessRequest] = []
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Zero-Trust system"""
        try:
            self.logger.info("Initializing Zero-Trust Network Architecture")
            
            # Initialize Certificate Authority
            ca_success = await self.certificate_manager.initialize_ca()
            if not ca_success:
                self.logger.error("Failed to initialize Certificate Authority")
                return False
            
            self.initialized = True
            self.logger.info("Zero-Trust system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Zero-Trust initialization failed: {e}")
            return False
    
    async def register_entity(self, entity_id: str, entity_type: str, ip_address: str, 
                            mac_address: Optional[str] = None) -> NetworkEntity:
        """Register a new network entity"""
        entity = NetworkEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            ip_address=ip_address,
            mac_address=mac_address
        )
        
        # Issue client certificate
        cert_pem, key_pem = await self.certificate_manager.issue_client_certificate(entity)
        
        # Calculate certificate fingerprint
        cert_hash = hashlib.sha256(cert_pem).hexdigest()
        entity.certificate_fingerprint = cert_hash
        
        # Store entity
        self.entities[entity_id] = entity
        
        self.logger.info(f"Registered entity: {entity_id} ({entity_type}) at {ip_address}")
        return entity
    
    async def authenticate_entity(self, entity_id: str, certificate_data: bytes, 
                                context: Dict[str, Any]) -> bool:
        """Authenticate entity using certificate"""
        entity = self.entities.get(entity_id)
        if not entity:
            self.logger.warning(f"Unknown entity authentication attempt: {entity_id}")
            return False
        
        # Verify certificate
        cert_hash = hashlib.sha256(certificate_data).hexdigest()
        if cert_hash != entity.certificate_fingerprint:
            self.logger.warning(f"Certificate mismatch for entity: {entity_id}")
            return False
        
        # Update trust level
        context["certificate_valid"] = True
        await self.trust_evaluator.update_entity_trust(entity, context)
        
        self.logger.info(f"Entity authenticated: {entity_id} (trust: {entity.trust_level.name})")
        return True
    
    async def authorize_access(self, entity_id: str, target_resource: str, 
                             requested_action: str, context: Dict[str, Any]) -> AccessDecision:
        """Authorize access request"""
        entity = self.entities.get(entity_id)
        if not entity:
            self.logger.warning(f"Access request from unknown entity: {entity_id}")
            return AccessDecision.DENY
        
        # Create access request
        request = AccessRequest(
            request_id=secrets.token_hex(16),
            source_entity=entity,
            target_resource=target_resource,
            requested_action=requested_action,
            timestamp=datetime.now(),
            context=context
        )
        
        # Evaluate access request
        decision = await self.policy_engine.evaluate_access_request(request)
        
        # Log access request
        self.access_logs.append(request)
        
        # Update entity trust based on access pattern
        await self._update_trust_from_access(entity, request, context)
        
        return decision
    
    async def _update_trust_from_access(self, entity: NetworkEntity, request: AccessRequest, 
                                      context: Dict[str, Any]):
        """Update entity trust based on access patterns"""
        # Analyze access patterns for behavioral scoring
        recent_requests = [req for req in self.access_logs 
                          if req.source_entity.entity_id == entity.entity_id 
                          and (datetime.now() - req.timestamp) < timedelta(hours=1)]
        
        # Calculate behavioral score based on access patterns
        if len(recent_requests) > 10:  # Too many requests
            context["behavioral_score"] = 0.3
        elif len(recent_requests) > 5:  # Moderate activity
            context["behavioral_score"] = 0.7
        else:  # Normal activity
            context["behavioral_score"] = 0.9
        
        # Update trust
        await self.trust_evaluator.update_entity_trust(entity, context)
    
    async def continuous_verification(self):
        """Continuous verification of all entities"""
        while True:
            try:
                for entity in self.entities.values():
                    # Re-evaluate trust for entities not verified recently
                    if (not entity.last_verified or 
                        datetime.now() - entity.last_verified > timedelta(hours=1)):
                        
                        context = {
                            "behavioral_score": 0.5,  # Default score
                            "location_expected": True,  # Would check actual location
                            "time_expected": True,  # Would check time patterns
                            "device_known": bool(entity.mac_address)
                        }
                        
                        await self.trust_evaluator.update_entity_trust(entity, context)
                
                # Sleep for verification interval
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Continuous verification error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    def get_entity_status(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity status"""
        entity = self.entities.get(entity_id)
        if not entity:
            return None
        
        return {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type,
            "ip_address": entity.ip_address,
            "trust_level": entity.trust_level.name,
            "risk_score": entity.risk_score,
            "last_verified": entity.last_verified.isoformat() if entity.last_verified else None,
            "certificate_fingerprint": entity.certificate_fingerprint
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get zero-trust system status"""
        return {
            "initialized": self.initialized,
            "entities_registered": len(self.entities),
            "access_requests_logged": len(self.access_logs),
            "policies_loaded": len(self.policy_engine.policies),
            "trust_levels": {
                level.name: len([e for e in self.entities.values() if e.trust_level == level])
                for level in TrustLevel
            }
        }

# Global zero-trust instance
zero_trust_manager = ZeroTrustManager()

async def initialize_zero_trust() -> bool:
    """Initialize the global zero-trust manager"""
    return await zero_trust_manager.initialize()

async def get_zero_trust_status() -> Dict[str, Any]:
    """Get zero-trust system status"""
    return zero_trust_manager.get_system_status()

# Example usage and testing
async def main():
    """Test Zero-Trust functionality"""
    print("🛡️ Testing Zero-Trust Network Architecture")
    
    # Initialize Zero-Trust
    success = await initialize_zero_trust()
    if success:
        print("✅ Zero-Trust system initialized successfully")
    else:
        print("❌ Zero-Trust initialization failed")
        return
    
    # Get status
    status = await get_zero_trust_status()
    print(f"📊 Zero-Trust Status: {json.dumps(status, indent=2)}")
    
    # Register test entity
    try:
        entity = await zero_trust_manager.register_entity(
            "test_user_001",
            "user",
            "192.168.1.100",
            "aa:bb:cc:dd:ee:ff"
        )
        print(f"✅ Entity registered: {entity.entity_id}")
    except Exception as e:
        print(f"❌ Entity registration failed: {e}")
        return
    
    # Test authentication
    try:
        # Simulate certificate data
        cert_data = b"test_certificate_data"
        context = {
            "location_expected": True,
            "time_expected": True,
            "device_known": True
        }
        
        auth_success = await zero_trust_manager.authenticate_entity(
            "test_user_001",
            cert_data,
            context
        )
        print(f"✅ Authentication: {'Success' if auth_success else 'Failed'}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
    
    # Test authorization
    try:
        decision = await zero_trust_manager.authorize_access(
            "test_user_001",
            "/api/secure/data",
            "read",
            {"source_ip": "192.168.1.100"}
        )
        print(f"✅ Authorization decision: {decision.value}")
    except Exception as e:
        print(f"❌ Authorization failed: {e}")
    
    # Get entity status
    entity_status = zero_trust_manager.get_entity_status("test_user_001")
    if entity_status:
        print(f"📋 Entity Status: {json.dumps(entity_status, indent=2)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test
    asyncio.run(main())