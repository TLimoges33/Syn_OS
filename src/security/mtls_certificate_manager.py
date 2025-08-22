#!/usr/bin/env python3
"""
mTLS Certificate Manager for SynapticOS Zero Trust Implementation
Manages mutual TLS certificates for service-to-service authentication
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.backends import default_backend
import hashlib
import secrets

class MTLSCertificateManager:
    """Manages mTLS certificates for Zero Trust authentication"""
    
    def __init__(self, cert_base_path: str = "certs/zero_trust"):
        """Initialize mTLS Certificate Manager"""
        self.logger = logging.getLogger("security.mtls.cert_manager")
        self.cert_base_path = Path(cert_base_path)
        self.ca_cert_path = self.cert_base_path / "ca"
        self.entity_cert_path = self.cert_base_path / "entities"
        self.server_cert_path = self.cert_base_path / "servers"
        
        # Certificate authority
        self.ca_private_key = None
        self.ca_certificate = None
        
        # Certificate registry
        self.certificate_registry: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.config = {
            "ca_validity_days": 3650,  # 10 years
            "entity_validity_days": 365,  # 1 year
            "key_size": 4096,
            "signature_algorithm": "sha256",
            "auto_renewal_threshold_days": 30
        }
        
        self._ensure_directory_structure()

    def _ensure_directory_structure(self):
        """Ensure certificate directory structure exists"""
        for path in [self.cert_base_path, self.ca_cert_path, 
                     self.entity_cert_path, self.server_cert_path]:
            path.mkdir(parents=True, mode=0o700, exist_ok=True)

    async def initialize(self) -> bool:
        """Initialize the certificate authority and load existing certificates"""
        try:
            self.logger.info("Initializing mTLS Certificate Manager...")
            
            # Load or create CA
            if not await self._load_ca():
                self.logger.info("Creating new Certificate Authority...")
                if not await self._create_ca():
                    return False
            
            # Load certificate registry
            await self._load_certificate_registry()
            
            # Check for expiring certificates
            await self._check_expiring_certificates()
            
            self.logger.info("mTLS Certificate Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate manager initialization failed: {e}")
            return False

    async def _create_ca(self) -> bool:
        """Create a new Certificate Authority"""
        try:
            # Generate CA private key
            self.ca_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.config["key_size"],
                backend=default_backend()
            )
            
            # Create CA certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Secure"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "ZeroTrust"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SynapticOS"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security"),
                x509.NameAttribute(NameOID.COMMON_NAME, "SynapticOS Zero Trust CA"),
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
                datetime.utcnow() + timedelta(days=self.config["ca_validity_days"])
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
            ).add_extension(
                x509.SubjectKeyIdentifier.from_public_key(self.ca_private_key.public_key()),
                critical=False,
            ).sign(self.ca_private_key, hashes.SHA256(), default_backend())
            
            # Save CA certificate and key
            await self._save_ca()
            
            self.logger.info("Certificate Authority created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"CA creation failed: {e}")
            return False

    async def _save_ca(self):
        """Save CA certificate and private key"""
        # Save CA private key (encrypted)
        ca_key_path = self.ca_cert_path / "ca_private_key.pem"
        with open(ca_key_path, "wb") as f:
            f.write(self.ca_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()  # TODO: Add password protection
            ))
        os.chmod(ca_key_path, 0o600)
        
        # Save CA certificate
        ca_cert_path = self.ca_cert_path / "ca_certificate.pem"
        with open(ca_cert_path, "wb") as f:
            f.write(self.ca_certificate.public_bytes(serialization.Encoding.PEM))

    async def _load_ca(self) -> bool:
        """Load existing Certificate Authority"""
        try:
            ca_key_path = self.ca_cert_path / "ca_private_key.pem"
            ca_cert_path = self.ca_cert_path / "ca_certificate.pem"
            
            if not (ca_key_path.exists() and ca_cert_path.exists()):
                return False
            
            # Load CA private key
            with open(ca_key_path, "rb") as f:
                self.ca_private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,  # TODO: Add password support
                    backend=default_backend()
                )
            
            # Load CA certificate
            with open(ca_cert_path, "rb") as f:
                self.ca_certificate = x509.load_pem_x509_certificate(
                    f.read(),
                    backend=default_backend()
                )
            
            # Verify CA certificate validity
            now = datetime.utcnow()
            if now < self.ca_certificate.not_valid_before or now > self.ca_certificate.not_valid_after:
                self.logger.warning("CA certificate has expired or is not yet valid")
                return False
            
            self.logger.info("Certificate Authority loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"CA loading failed: {e}")
            return False

    async def generate_entity_certificate(self, entity) -> str:
        """Generate certificate for a Zero Trust entity"""
        try:
            # Generate private key for entity
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,  # Smaller key for entities
                backend=default_backend()
            )
            
            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Secure"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "ZeroTrust"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SynapticOS"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, entity.entity_type),
                x509.NameAttribute(NameOID.COMMON_NAME, entity.name),
            ])
            
            # Create Subject Alternative Names
            san_list = []
            for ip in entity.ip_addresses:
                try:
                    san_list.append(x509.IPAddress(ipaddress.ip_address(ip)))
                except:
                    san_list.append(x509.DNSName(ip))
            
            # Build certificate
            cert_builder = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                self.ca_certificate.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.config["entity_validity_days"])
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=False,
                    crl_sign=False,
                    digital_signature=True,
                    content_commitment=True,
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
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                ]),
                critical=True,
            ).add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False,
            ).add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(self.ca_private_key.public_key()),
                critical=False,
            )
            
            # Add SAN if available
            if san_list:
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False,
                )
            
            # Sign the certificate
            certificate = cert_builder.sign(self.ca_private_key, hashes.SHA256(), default_backend())
            
            # Calculate certificate fingerprint
            fingerprint = hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()
            
            # Save certificate and private key
            await self._save_entity_certificate(entity.entity_id, certificate, private_key)
            
            # Register certificate
            self.certificate_registry[entity.entity_id] = {
                "fingerprint": fingerprint,
                "issued": datetime.utcnow().isoformat(),
                "expires": certificate.not_valid_after.isoformat(),
                "entity_type": entity.entity_type,
                "entity_name": entity.name,
                "serial_number": str(certificate.serial_number)
            }
            
            await self._save_certificate_registry()
            
            self.logger.info(f"Certificate generated for entity {entity.entity_id}")
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Certificate generation failed for {entity.entity_id}: {e}")
            raise

    async def _save_entity_certificate(self, entity_id: str, certificate: x509.Certificate, 
                                     private_key: rsa.RSAPrivateKey):
        """Save entity certificate and private key"""
        entity_dir = self.entity_cert_path / entity_id
        entity_dir.mkdir(exist_ok=True, mode=0o700)
        
        # Save private key
        key_path = entity_dir / "private_key.pem"
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        os.chmod(key_path, 0o600)
        
        # Save certificate
        cert_path = entity_dir / "certificate.pem"
        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

    async def get_entity_certificate_paths(self, entity_id: str) -> Tuple[str, str]:
        """Get paths to entity certificate and private key"""
        entity_dir = self.entity_cert_path / entity_id
        cert_path = entity_dir / "certificate.pem"
        key_path = entity_dir / "private_key.pem"
        
        if not (cert_path.exists() and key_path.exists()):
            raise FileNotFoundError(f"Certificate files not found for entity {entity_id}")
        
        return str(cert_path), str(key_path)

    async def get_ca_certificate_path(self) -> str:
        """Get path to CA certificate"""
        ca_cert_path = self.ca_cert_path / "ca_certificate.pem"
        if not ca_cert_path.exists():
            raise FileNotFoundError("CA certificate not found")
        return str(ca_cert_path)

    async def verify_certificate(self, certificate_pem: bytes) -> Dict[str, Any]:
        """Verify a certificate against the CA"""
        try:
            # Load certificate
            certificate = x509.load_pem_x509_certificate(certificate_pem, default_backend())
            
            # Verify signature
            ca_public_key = self.ca_certificate.public_key()
            ca_public_key.verify(
                certificate.signature,
                certificate.tbs_certificate_bytes,
                certificate.signature_algorithm_oid._name
            )
            
            # Check validity period
            now = datetime.utcnow()
            is_valid = (now >= certificate.not_valid_before and 
                       now <= certificate.not_valid_after)
            
            # Calculate fingerprint
            fingerprint = hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()
            
            return {
                "valid": is_valid,
                "fingerprint": fingerprint,
                "subject": str(certificate.subject),
                "issuer": str(certificate.issuer),
                "not_before": certificate.not_valid_before.isoformat(),
                "not_after": certificate.not_valid_after.isoformat(),
                "serial_number": str(certificate.serial_number)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    async def revoke_certificate(self, entity_id: str) -> bool:
        """Revoke a certificate (simplified implementation)"""
        try:
            if entity_id in self.certificate_registry:
                self.certificate_registry[entity_id]["revoked"] = True
                self.certificate_registry[entity_id]["revoked_at"] = datetime.utcnow().isoformat()
                await self._save_certificate_registry()
                
                self.logger.info(f"Certificate revoked for entity {entity_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Certificate revocation failed: {e}")
            return False

    async def _load_certificate_registry(self):
        """Load certificate registry from file"""
        registry_path = self.cert_base_path / "certificate_registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.certificate_registry = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load certificate registry: {e}")
                self.certificate_registry = {}

    async def _save_certificate_registry(self):
        """Save certificate registry to file"""
        registry_path = self.cert_base_path / "certificate_registry.json"
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.certificate_registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save certificate registry: {e}")

    async def _check_expiring_certificates(self):
        """Check for expiring certificates and log warnings"""
        threshold = datetime.utcnow() + timedelta(days=self.config["auto_renewal_threshold_days"])
        
        for entity_id, cert_info in self.certificate_registry.items():
            if cert_info.get("revoked", False):
                continue
                
            expires = datetime.fromisoformat(cert_info["expires"])
            if expires < threshold:
                self.logger.warning(f"Certificate for {entity_id} expires on {expires}")

    async def get_certificate_status(self, entity_id: str) -> Dict[str, Any]:
        """Get status of an entity's certificate"""
        if entity_id not in self.certificate_registry:
            return {"status": "not_found"}
        
        cert_info = self.certificate_registry[entity_id]
        if cert_info.get("revoked", False):
            return {"status": "revoked", "revoked_at": cert_info["revoked_at"]}
        
        expires = datetime.fromisoformat(cert_info["expires"])
        now = datetime.utcnow()
        
        if now > expires:
            return {"status": "expired", "expired_at": cert_info["expires"]}
        
        days_until_expiry = (expires - now).days
        if days_until_expiry <= self.config["auto_renewal_threshold_days"]:
            return {"status": "expiring_soon", "expires": cert_info["expires"], "days_remaining": days_until_expiry}
        
        return {"status": "valid", "expires": cert_info["expires"], "days_remaining": days_until_expiry}

    async def list_certificates(self) -> Dict[str, Any]:
        """List all certificates and their status"""
        result = {}
        for entity_id, cert_info in self.certificate_registry.items():
            status = await self.get_certificate_status(entity_id)
            result[entity_id] = {**cert_info, **status}
        return result
