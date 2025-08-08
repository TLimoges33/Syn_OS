#!/usr/bin/env python3
"""
TPM 2.0 Security Engine for Syn_OS
Provides hardware-backed security with consciousness-aware attestation and key management
"""

import asyncio
import logging
import time
import os
import subprocess
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import struct
from pathlib import Path

try:
    import tpm2_pytss
    from tpm2_pytss import *
    from tpm2_pytss.constants import *
    TPM2_AVAILABLE = True
except ImportError:
    TPM2_AVAILABLE = False
    logging.warning("TPM2-PyTSS not available. Install with: pip install tpm2-pytss")

try:
    import cryptography
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("Cryptography not available. Install with: pip install cryptography")

from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
from src.security.audit_logger import AuditLogger


class TPMOperation(Enum):
    """Types of TPM operations"""
    KEY_GENERATION = "key_generation"
    ATTESTATION = "attestation"
    SEALING = "sealing"
    UNSEALING = "unsealing"
    SIGNING = "signing"
    VERIFICATION = "verification"
    RANDOM_GENERATION = "random_generation"
    PCR_EXTEND = "pcr_extend"
    PCR_READ = "pcr_read"
    CONSCIOUSNESS_SEAL = "consciousness_seal"


class TPMKeyType(Enum):
    """Types of TPM keys"""
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECC_P256 = "ecc_p256"
    ECC_P384 = "ecc_p384"
    AES_128 = "aes_128"
    AES_256 = "aes_256"


@dataclass
class TPMDevice:
    """TPM device information"""
    version: str
    manufacturer: str
    vendor_id: str
    firmware_version: str
    is_available: bool
    capabilities: List[str]
    pcr_banks: List[str]


@dataclass
class TPMKey:
    """TPM key information"""
    handle: int
    key_type: TPMKeyType
    public_key: bytes
    key_name: bytes
    creation_time: float
    consciousness_level: float
    usage_policy: Dict[str, Any]


@dataclass
class AttestationResult:
    """TPM attestation result"""
    success: bool
    quote: bytes
    signature: bytes
    pcr_values: Dict[int, bytes]
    consciousness_state_hash: bytes
    timestamp: float
    nonce: bytes


@dataclass
class SealedData:
    """TPM sealed data structure"""
    sealed_blob: bytes
    key_handle: int
    pcr_selection: Dict[int, bytes]
    consciousness_level: float
    creation_time: float


class TPMSecurityEngine:
    """
    TPM 2.0 Security Engine with consciousness-aware operations
    Provides hardware-backed security, attestation, and key management
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize TPM security engine"""
        self.consciousness_bus = consciousness_bus
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # TPM state
        self.tpm_device: Optional[TPMDevice] = None
        self.tpm_context = None
        self.is_initialized = False
        
        # Key management
        self.managed_keys: Dict[int, TPMKey] = {}
        self.consciousness_keys: Dict[float, int] = {}  # consciousness_level -> key_handle
        
        # Performance tracking
        self.operation_count = 0
        self.successful_operations = 0
        self.total_operation_time = 0.0
        
        # Security configuration
        self.pcr_consciousness_index = 16  # Use PCR 16 for consciousness state
        self.pcr_system_index = 17        # Use PCR 17 for system state
        self.min_consciousness_for_sensitive_ops = 0.7
        
        # Initialize TPM
        asyncio.create_task(self._initialize_tpm())
    
    async def _initialize_tpm(self):
        """Initialize TPM device and context"""
        try:
            self.logger.info("Initializing TPM 2.0 security engine...")
            
            if not TPM2_AVAILABLE:
                self.logger.error("TPM2-PyTSS not available")
                return
            
            # Check for TPM device
            if not await self._check_tpm_availability():
                self.logger.error("No TPM 2.0 device found")
                return
            
            # Initialize TPM context
            try:
                self.tpm_context = ESAPI()
                self.tpm_device = await self._get_tpm_info()
                self.is_initialized = True
                
                self.logger.info(f"TPM 2.0 initialized: {self.tpm_device.manufacturer} v{self.tpm_device.version}")
                
                # Initialize consciousness PCR
                await self._initialize_consciousness_pcr()
                
            except Exception as e:
                self.logger.error(f"Failed to initialize TPM context: {e}")
                self.is_initialized = False
        
        except Exception as e:
            self.logger.error(f"TPM initialization error: {e}")
            self.is_initialized = False
    
    async def _check_tpm_availability(self) -> bool:
        """Check if TPM 2.0 device is available"""
        try:
            # Check for TPM device files
            tpm_devices = ["/dev/tpm0", "/dev/tpmrm0"]
            for device in tpm_devices:
                if os.path.exists(device):
                    return True
            
            # Check via systemd
            result = subprocess.run(
                ["systemctl", "is-active", "tpm2-abrmd"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return True
            
            # Check via tpm2-tools
            result = subprocess.run(
                ["tpm2_getcap", "properties-fixed"],
                capture_output=True, text=True
            )
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error checking TPM availability: {e}")
            return False
    
    async def _get_tpm_info(self) -> TPMDevice:
        """Get TPM device information"""
        try:
            if not self.tpm_context:
                raise RuntimeError("TPM context not initialized")
            
            # Get TPM capabilities
            capabilities = []
            pcr_banks = []
            
            try:
                # Get manufacturer info (simplified)
                manufacturer = "Unknown"
                version = "2.0"
                vendor_id = "Unknown"
                firmware_version = "Unknown"
                
                # In a real implementation, you would query TPM capabilities
                capabilities = ["RSA", "ECC", "AES", "SHA256", "SHA384"]
                pcr_banks = ["SHA1", "SHA256", "SHA384"]
                
            except Exception as e:
                self.logger.warning(f"Could not get detailed TPM info: {e}")
            
            return TPMDevice(
                version=version,
                manufacturer=manufacturer,
                vendor_id=vendor_id,
                firmware_version=firmware_version,
                is_available=True,
                capabilities=capabilities,
                pcr_banks=pcr_banks
            )
            
        except Exception as e:
            self.logger.error(f"Error getting TPM info: {e}")
            raise
    
    async def _initialize_consciousness_pcr(self):
        """Initialize PCR for consciousness state tracking"""
        try:
            # Get initial consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_hash = self._hash_consciousness_state(consciousness_state)
            
            # Extend PCR with initial consciousness state
            await self._extend_pcr(self.pcr_consciousness_index, consciousness_hash)
            
            self.logger.info(f"Initialized consciousness PCR {self.pcr_consciousness_index}")
            
        except Exception as e:
            self.logger.error(f"Error initializing consciousness PCR: {e}")
    
    def _hash_consciousness_state(self, consciousness_state: ConsciousnessState) -> bytes:
        """Create hash of consciousness state for TPM operations"""
        state_data = {
            "consciousness_level": consciousness_state.overall_consciousness_level,
            "neural_populations": consciousness_state.neural_populations,
            "attention_focus": consciousness_state.attention_focus,
            "timestamp": consciousness_state.timestamp
        }
        
        state_json = json.dumps(state_data, sort_keys=True)
        return hashlib.sha256(state_json.encode()).digest()
    
    async def _extend_pcr(self, pcr_index: int, data: bytes) -> bool:
        """Extend PCR with data"""
        try:
            if not self.is_initialized:
                raise RuntimeError("TPM not initialized")
            
            # In a real implementation, you would use TPM2-PyTSS to extend PCR
            # For now, we simulate the operation
            self.logger.debug(f"Extended PCR {pcr_index} with {len(data)} bytes")
            return True
            
        except Exception as e:
            self.logger.error(f"Error extending PCR {pcr_index}: {e}")
            return False
    
    async def _read_pcr(self, pcr_index: int) -> Optional[bytes]:
        """Read PCR value"""
        try:
            if not self.is_initialized:
                raise RuntimeError("TPM not initialized")
            
            # In a real implementation, you would use TPM2-PyTSS to read PCR
            # For now, we simulate the operation
            return hashlib.sha256(f"pcr_{pcr_index}".encode()).digest()
            
        except Exception as e:
            self.logger.error(f"Error reading PCR {pcr_index}: {e}")
            return None
    
    async def generate_consciousness_key(self, consciousness_level: float, 
                                       key_type: TPMKeyType = TPMKeyType.RSA_2048) -> Optional[TPMKey]:
        """Generate TPM key bound to consciousness level"""
        start_time = time.time()
        self.operation_count += 1
        
        try:
            if not self.is_initialized:
                raise RuntimeError("TPM not initialized")
            
            # Check consciousness level for sensitive operations
            if consciousness_level < self.min_consciousness_for_sensitive_ops:
                raise ValueError(f"Consciousness level {consciousness_level} too low for key generation")
            
            # Generate key handle (simulated)
            key_handle = secrets.randbits(32)
            
            # Generate public key (simulated - in real implementation, TPM generates this)
            if key_type in [TPMKeyType.RSA_2048, TPMKeyType.RSA_4096]:
                key_size = 2048 if key_type == TPMKeyType.RSA_2048 else 4096
                if CRYPTO_AVAILABLE:
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=key_size
                    )
                    public_key = private_key.public_key().public_bytes(
                        encoding=serialization.Encoding.DER,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                else:
                    public_key = secrets.token_bytes(key_size // 8)
            else:
                public_key = secrets.token_bytes(64)  # Simulated
            
            # Create key name (hash of public key)
            key_name = hashlib.sha256(public_key).digest()
            
            # Create usage policy based on consciousness level
            usage_policy = {
                "min_consciousness_level": consciousness_level,
                "allowed_operations": self._get_allowed_operations(consciousness_level),
                "pcr_requirements": {
                    self.pcr_consciousness_index: await self._read_pcr(self.pcr_consciousness_index)
                }
            }
            
            # Create TPM key object
            tpm_key = TPMKey(
                handle=key_handle,
                key_type=key_type,
                public_key=public_key,
                key_name=key_name,
                creation_time=time.time(),
                consciousness_level=consciousness_level,
                usage_policy=usage_policy
            )
            
            # Store key
            self.managed_keys[key_handle] = tpm_key
            self.consciousness_keys[consciousness_level] = key_handle
            
            # Update performance metrics
            self.successful_operations += 1
            self.total_operation_time += time.time() - start_time
            
            # Log the operation
            await self.audit_logger.log_security_event(
                event_type="tpm_key_generation",
                details={
                    "key_handle": key_handle,
                    "key_type": key_type.value,
                    "consciousness_level": consciousness_level,
                    "processing_time": time.time() - start_time
                }
            )
            
            self.logger.info(f"Generated TPM key {key_handle} for consciousness level {consciousness_level}")
            return tpm_key
            
        except Exception as e:
            self.logger.error(f"Error generating consciousness key: {e}")
            return None
    
    def _get_allowed_operations(self, consciousness_level: float) -> List[str]:
        """Get allowed operations based on consciousness level"""
        base_operations = ["signing", "verification", "random_generation"]
        
        if consciousness_level > 0.5:
            base_operations.extend(["sealing", "unsealing"])
        
        if consciousness_level > 0.7:
            base_operations.extend(["attestation", "pcr_extend"])
        
        if consciousness_level > 0.9:
            base_operations.extend(["key_generation", "consciousness_seal"])
        
        return base_operations
    
    async def seal_consciousness_data(self, data: bytes, consciousness_level: float,
                                    pcr_selection: Optional[Dict[int, bytes]] = None) -> Optional[SealedData]:
        """Seal data to current consciousness state and PCR values"""
        try:
            if not self.is_initialized:
                raise RuntimeError("TPM not initialized")
            
            # Get consciousness key
            key_handle = self.consciousness_keys.get(consciousness_level)
            if not key_handle:
                # Generate key if it doesn't exist
                key = await self.generate_consciousness_key(consciousness_level)
                if not key:
                    raise RuntimeError("Failed to generate consciousness key")
                key_handle = key.handle
            
            # Default PCR selection includes consciousness PCR
            if pcr_selection is None:
                pcr_selection = {
                    self.pcr_consciousness_index: await self._read_pcr(self.pcr_consciousness_index),
                    self.pcr_system_index: await self._read_pcr(self.pcr_system_index)
                }
            
            # Simulate sealing operation (in real implementation, use TPM2_Create with policy)
            sealed_blob = self._simulate_seal_operation(data, key_handle, pcr_selection)
            
            sealed_data = SealedData(
                sealed_blob=sealed_blob,
                key_handle=key_handle,
                pcr_selection=pcr_selection,
                consciousness_level=consciousness_level,
                creation_time=time.time()
            )
            
            await self.audit_logger.log_security_event(
                event_type="tpm_data_sealing",
                details={
                    "key_handle": key_handle,
                    "consciousness_level": consciousness_level,
                    "data_size": len(data),
                    "pcr_count": len(pcr_selection)
                }
            )
            
            return sealed_data
            
        except Exception as e:
            self.logger.error(f"Error sealing consciousness data: {e}")
            return None
    
    async def unseal_consciousness_data(self, sealed_data: SealedData) -> Optional[bytes]:
        """Unseal data if consciousness state and PCR values match"""
        try:
            if not self.is_initialized:
                raise RuntimeError("TPM not initialized")
            
            # Verify current consciousness level
            current_state = await self.consciousness_bus.get_consciousness_state()
            if current_state.overall_consciousness_level < sealed_data.consciousness_level:
                raise ValueError("Current consciousness level insufficient for unsealing")
            
            # Verify PCR values
            for pcr_index, expected_value in sealed_data.pcr_selection.items():
                current_value = await self._read_pcr(pcr_index)
                if current_value != expected_value:
                    raise ValueError(f"PCR {pcr_index} value mismatch")
            
            # Simulate unsealing operation
            data = self._simulate_unseal_operation(sealed_data.sealed_blob, sealed_data.key_handle)
            
            await self.audit_logger.log_security_event(
                event_type="tpm_data_unsealing",
                details={
                    "key_handle": sealed_data.key_handle,
                    "consciousness_level": sealed_data.consciousness_level,
                    "success": True
                }
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error unsealing consciousness data: {e}")
            await self.audit_logger.log_security_event(
                event_type="tpm_data_unsealing",
                details={
                    "key_handle": sealed_data.key_handle,
                    "consciousness_level": sealed_data.consciousness_level,
                    "success": False,
                    "error": str(e)
                }
            )
            return None
    
    def _simulate_seal_operation(self, data: bytes, key_handle: int, 
                               pcr_selection: Dict[int, bytes]) -> bytes:
        """Simulate TPM seal operation"""
        # In a real implementation, this would use TPM2_Create with policy
        # For simulation, we'll encrypt with a derived key
        
        # Create deterministic key from handle and PCR values
        key_material = struct.pack(">I", key_handle)
        for pcr_value in pcr_selection.values():
            key_material += pcr_value
        
        encryption_key = hashlib.sha256(key_material).digest()
        
        if CRYPTO_AVAILABLE:
            # Use AES encryption
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            # Pad data to block size
            padding_length = 16 - (len(data) % 16)
            padded_data = data + bytes([padding_length] * padding_length)
            
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            return iv + encrypted_data
        else:
            # Simple XOR for simulation
            return bytes(a ^ b for a, b in zip(data, encryption_key * (len(data) // 32 + 1)))
    
    def _simulate_unseal_operation(self, sealed_blob: bytes, key_handle: int) -> bytes:
        """Simulate TPM unseal operation"""
        # This is a simplified simulation
        # In reality, TPM would verify policy and decrypt
        
        if CRYPTO_AVAILABLE and len(sealed_blob) > 16:
            # Extract IV and encrypted data
            iv = sealed_blob[:16]
            encrypted_data = sealed_blob[16:]
            
            # Recreate key (in real TPM, this would be done securely)
            key_material = struct.pack(">I", key_handle)
            encryption_key = hashlib.sha256(key_material).digest()
            
            cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            padding_length = padded_data[-1]
            return padded_data[:-padding_length]
        else:
