#!/usr/bin/env python3
"""
Hardware Security Module (HSM) Manager
Provides hardware-backed key storage and cryptographic operations using TPM 2.0
"""

import os
import subprocess
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class HSMKeyType(Enum):
    RSA_2048 = "rsa2048"
    RSA_4096 = "rsa4096"
    AES_256 = "aes256"
    ECDSA_P256 = "ecdsa_p256"

@dataclass
class HSMKey:
    key_id: str
    key_type: HSMKeyType
    handle: str
    public_key: Optional[bytes] = None
    created_at: str = ""
    usage: str = ""

class TPMManager:
    """TPM 2.0 Hardware Security Module Manager"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.hsm.tpm")
        self.tpm_available = self._check_tpm_availability()
        self.key_storage_path = "/var/lib/syn_os/tpm_keys"
        self._ensure_key_storage()
    
    def _check_tpm_availability(self) -> bool:
        """Check if TPM 2.0 is available and accessible"""
        try:
            result = subprocess.run(
                ["tpm2_getcap", "properties-fixed"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("TPM 2.0 detected and accessible")
                return True
            else:
                self.logger.warning("TPM 2.0 not accessible, falling back to software HSM")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"TPM tools not available: {e}")
            return False
    
    def _ensure_key_storage(self):
        """Ensure key storage directory exists"""
        try:
            os.makedirs(self.key_storage_path, mode=0o700, exist_ok=True)
        except OSError:
            # Fallback to local directory if system path not accessible
            self.key_storage_path = "keys/tpm"
            os.makedirs(self.key_storage_path, mode=0o700, exist_ok=True)
    
    async def create_primary_key(self) -> str:
        """Create TPM primary key for key hierarchy"""
        if not self.tpm_available:
            return await self._create_software_primary_key()
        
        try:
            # Create primary key in TPM
            result = subprocess.run([
                "tpm2_createprimary",
                "-C", "o",  # Owner hierarchy
                "-g", "sha256",
                "-G", "rsa",
                "-c", f"{self.key_storage_path}/primary.ctx"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("TPM primary key created successfully")
                return "primary.ctx"
            else:
                self.logger.error(f"Failed to create TPM primary key: {result.stderr}")
                return await self._create_software_primary_key()
                
        except Exception as e:
            self.logger.error(f"TPM primary key creation failed: {e}")
            return await self._create_software_primary_key()
    
    async def _create_software_primary_key(self) -> str:
        """Fallback software-based primary key creation"""
        self.logger.info("Creating software-based primary key")
        
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Save private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        primary_key_path = f"{self.key_storage_path}/primary_software.pem"
        with open(primary_key_path, 'wb') as f:
            f.write(private_pem)
        
        os.chmod(primary_key_path, 0o600)
        return "primary_software.pem"
    
    async def create_key(self, key_type: HSMKeyType, key_id: str, usage: str = "signing") -> HSMKey:
        """Create a new key in the HSM"""
        if not self.tpm_available:
            return await self._create_software_key(key_type, key_id, usage)
        
        try:
            if key_type == HSMKeyType.RSA_2048:
                return await self._create_tpm_rsa_key(key_id, 2048, usage)
            elif key_type == HSMKeyType.RSA_4096:
                return await self._create_tpm_rsa_key(key_id, 4096, usage)
            elif key_type == HSMKeyType.AES_256:
                return await self._create_tpm_aes_key(key_id, usage)
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
                
        except Exception as e:
            self.logger.error(f"TPM key creation failed: {e}")
            return await self._create_software_key(key_type, key_id, usage)
    
    async def _create_tpm_rsa_key(self, key_id: str, key_size: int, usage: str) -> HSMKey:
        """Create RSA key in TPM"""
        key_path = f"{self.key_storage_path}/{key_id}"
        
        # Create RSA key
        result = subprocess.run([
            "tpm2_create",
            "-g", "sha256",
            "-G", "rsa",
            "-u", f"{key_path}.pub",
            "-r", f"{key_path}.priv",
            "-C", f"{self.key_storage_path}/primary.ctx"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"Failed to create TPM RSA key: {result.stderr}")
        
        # Load the key
        load_result = subprocess.run([
            "tpm2_load",
            "-C", f"{self.key_storage_path}/primary.ctx",
            "-u", f"{key_path}.pub",
            "-r", f"{key_path}.priv",
            "-c", f"{key_path}.ctx"
        ], capture_output=True, text=True, timeout=30)
        
        if load_result.returncode != 0:
            raise Exception(f"Failed to load TPM RSA key: {load_result.stderr}")
        
        # Read public key
        pub_result = subprocess.run([
            "tpm2_readpublic",
            "-c", f"{key_path}.ctx",
            "-o", f"{key_path}_public.pem"
        ], capture_output=True, text=True, timeout=30)
        
        public_key_data = None
        if pub_result.returncode == 0:
            try:
                with open(f"{key_path}_public.pem", 'rb') as f:
                    public_key_data = f.read()
            except Exception:
                pass
        
        key_type = HSMKeyType.RSA_2048 if key_size == 2048 else HSMKeyType.RSA_4096
        
        return HSMKey(
            key_id=key_id,
            key_type=key_type,
            handle=f"{key_path}.ctx",
            public_key=public_key_data,
            created_at=str(subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip()),
            usage=usage
        )
    
    async def _create_tpm_aes_key(self, key_id: str, usage: str) -> HSMKey:
        """Create AES key in TPM"""
        key_path = f"{self.key_storage_path}/{key_id}"
        
        # Create AES key
        result = subprocess.run([
            "tpm2_create",
            "-g", "sha256",
            "-G", "aes",
            "-u", f"{key_path}.pub",
            "-r", f"{key_path}.priv",
            "-C", f"{self.key_storage_path}/primary.ctx"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"Failed to create TPM AES key: {result.stderr}")
        
        # Load the key
        load_result = subprocess.run([
            "tpm2_load",
            "-C", f"{self.key_storage_path}/primary.ctx",
            "-u", f"{key_path}.pub",
            "-r", f"{key_path}.priv",
            "-c", f"{key_path}.ctx"
        ], capture_output=True, text=True, timeout=30)
        
        if load_result.returncode != 0:
            raise Exception(f"Failed to load TPM AES key: {load_result.stderr}")
        
        return HSMKey(
            key_id=key_id,
            key_type=HSMKeyType.AES_256,
            handle=f"{key_path}.ctx",
            created_at=str(subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip()),
            usage=usage
        )
    
    async def _create_software_key(self, key_type: HSMKeyType, key_id: str, usage: str) -> HSMKey:
        """Fallback software key creation"""
        self.logger.info(f"Creating software-based {key_type.value} key: {key_id}")
        
        key_path = f"{self.key_storage_path}/{key_id}_software"
        
        if key_type in [HSMKeyType.RSA_2048, HSMKeyType.RSA_4096]:
            key_size = 2048 if key_type == HSMKeyType.RSA_2048 else 4096
            
            # Generate RSA key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            # Save private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            with open(f"{key_path}.pem", 'wb') as f:
                f.write(private_pem)
            
            # Save public key
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(f"{key_path}_public.pem", 'wb') as f:
                f.write(public_pem)
            
            os.chmod(f"{key_path}.pem", 0o600)
            os.chmod(f"{key_path}_public.pem", 0o644)
            
            return HSMKey(
                key_id=key_id,
                key_type=key_type,
                handle=f"{key_path}.pem",
                public_key=public_pem,
                created_at=str(subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip()),
                usage=usage
            )
        
        elif key_type == HSMKeyType.AES_256:
            # Generate AES key
            aes_key = secrets.token_bytes(32)  # 256 bits
            
            with open(f"{key_path}.key", 'wb') as f:
                f.write(aes_key)
            
            os.chmod(f"{key_path}.key", 0o600)
            
            return HSMKey(
                key_id=key_id,
                key_type=key_type,
                handle=f"{key_path}.key",
                created_at=str(subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip()),
                usage=usage
            )
        
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
    
    async def sign_data(self, key: HSMKey, data: bytes) -> bytes:
        """Sign data using HSM key"""
        if not self.tpm_available or "_software" in key.handle:
            return await self._software_sign_data(key, data)
        
        try:
            # Create hash of data
            data_hash = hashlib.sha256(data).digest()
            hash_file = f"{self.key_storage_path}/temp_hash_{key.key_id}"
            
            with open(hash_file, 'wb') as f:
                f.write(data_hash)
            
            # Sign with TPM
            result = subprocess.run([
                "tpm2_sign",
                "-c", key.handle,
                "-g", "sha256",
                "-o", f"{hash_file}.sig",
                hash_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"TPM signing failed: {result.stderr}")
            
            # Read signature
            with open(f"{hash_file}.sig", 'rb') as f:
                signature = f.read()
            
            # Cleanup
            os.unlink(hash_file)
            os.unlink(f"{hash_file}.sig")
            
            return signature
            
        except Exception as e:
            self.logger.error(f"TPM signing failed: {e}")
            return await self._software_sign_data(key, data)
    
    async def _software_sign_data(self, key: HSMKey, data: bytes) -> bytes:
        """Software-based signing fallback"""
        if key.key_type not in [HSMKeyType.RSA_2048, HSMKeyType.RSA_4096]:
            raise ValueError("Software signing only supports RSA keys")
        
        # Load private key
        with open(key.handle, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        # Sign data
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    async def encrypt_data(self, key: HSMKey, data: bytes) -> bytes:
        """Encrypt data using HSM key"""
        if key.key_type == HSMKeyType.AES_256:
            return await self._aes_encrypt(key, data)
        elif key.key_type in [HSMKeyType.RSA_2048, HSMKeyType.RSA_4096]:
            return await self._rsa_encrypt(key, data)
        else:
            raise ValueError(f"Encryption not supported for key type: {key.key_type}")
    
    async def _aes_encrypt(self, key: HSMKey, data: bytes) -> bytes:
        """AES encryption"""
        # Load AES key
        if "_software" in key.handle:
            with open(key.handle, 'rb') as f:
                aes_key = f.read()
        else:
            # For TPM AES keys, we'd need to use TPM encrypt command
            # For now, fallback to software
            raise NotImplementedError("TPM AES encryption not yet implemented")
        
        # Generate IV
        iv = secrets.token_bytes(16)
        
        # Encrypt
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad data to block size
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + ciphertext
        return iv + ciphertext
    
    async def _rsa_encrypt(self, key: HSMKey, data: bytes) -> bytes:
        """RSA encryption using public key"""
        if key.public_key is None:
            raise ValueError("Public key not available for RSA encryption")
        
        # Load public key
        public_key = serialization.load_pem_public_key(
            key.public_key,
            backend=default_backend()
        )
        
        # Encrypt
        ciphertext = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return ciphertext

class HSMManager:
    """High-level Hardware Security Module Manager"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.hsm")
        self.tpm_manager = TPMManager()
        self.keys: Dict[str, HSMKey] = {}
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize HSM system"""
        try:
            self.logger.info("Initializing Hardware Security Module")
            
            # Create primary key
            primary_handle = await self.tpm_manager.create_primary_key()
            self.logger.info(f"Primary key created: {primary_handle}")
            
            # Create default system keys
            await self._create_system_keys()
            
            self.initialized = True
            self.logger.info("HSM initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"HSM initialization failed: {e}")
            return False
    
    async def _create_system_keys(self):
        """Create default system keys"""
        # JWT signing key
        jwt_key = await self.tpm_manager.create_key(
            HSMKeyType.RSA_2048,
            "jwt_signing_key",
            "jwt_signing"
        )
        self.keys["jwt_signing"] = jwt_key
        
        # Data encryption key
        encryption_key = await self.tpm_manager.create_key(
            HSMKeyType.AES_256,
            "data_encryption_key",
            "data_encryption"
        )
        self.keys["data_encryption"] = encryption_key
        
        # API signing key
        api_key = await self.tpm_manager.create_key(
            HSMKeyType.RSA_2048,
            "api_signing_key",
            "api_signing"
        )
        self.keys["api_signing"] = api_key
    
    async def get_key(self, key_id: str) -> Optional[HSMKey]:
        """Get key by ID"""
        return self.keys.get(key_id)
    
    async def create_key(self, key_type: HSMKeyType, key_id: str, usage: str = "general") -> HSMKey:
        """Create a new key"""
        key = await self.tpm_manager.create_key(key_type, key_id, usage)
        self.keys[key_id] = key
        return key
    
    async def sign_jwt_token(self, payload: bytes) -> bytes:
        """Sign JWT token using HSM"""
        jwt_key = self.keys.get("jwt_signing")
        if not jwt_key:
            raise ValueError("JWT signing key not available")
        
        return await self.tpm_manager.sign_data(jwt_key, payload)
    
    async def encrypt_sensitive_data(self, data: bytes) -> bytes:
        """Encrypt sensitive data using HSM"""
        encryption_key = self.keys.get("data_encryption")
        if not encryption_key:
            raise ValueError("Data encryption key not available")
        
        return await self.tpm_manager.encrypt_data(encryption_key, data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get HSM status"""
        return {
            "initialized": self.initialized,
            "tpm_available": self.tpm_manager.tpm_available,
            "keys_loaded": len(self.keys),
            "key_storage_path": self.tpm_manager.key_storage_path,
            "keys": {key_id: {
                "type": key.key_type.value,
                "usage": key.usage,
                "created_at": key.created_at
            } for key_id, key in self.keys.items()}
        }

# Global HSM instance
hsm_manager = HSMManager()

async def initialize_hsm() -> bool:
    """Initialize the global HSM manager"""
    return await hsm_manager.initialize()

async def get_hsm_status() -> Dict[str, Any]:
    """Get HSM status"""
    return hsm_manager.get_status()

# Example usage and testing
async def main():
    """Test HSM functionality"""
    print("🔐 Testing Hardware Security Module")
    
    # Initialize HSM
    success = await initialize_hsm()
    if success:
        print("✅ HSM initialized successfully")
    else:
        print("❌ HSM initialization failed")
        return
    
    # Get status
    status = await get_hsm_status()
    print(f"📊 HSM Status: {json.dumps(status, indent=2)}")
    
    # Test JWT signing
    try:
        test_payload = b"test_jwt_payload"
        signature = await hsm_manager.sign_jwt_token(test_payload)
        print(f"✅ JWT signing successful: {len(signature)} bytes")
    except Exception as e:
        print(f"❌ JWT signing failed: {e}")
    
    # Test data encryption
    try:
        test_data = b"sensitive_test_data"
        encrypted = await hsm_manager.encrypt_sensitive_data(test_data)
        print(f"✅ Data encryption successful: {len(encrypted)} bytes")
    except Exception as e:
        print(f"❌ Data encryption failed: {e}")

if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test
    asyncio.run(main())