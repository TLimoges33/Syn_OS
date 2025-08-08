#!/usr/bin/env python3
"""
Cloud-Based Consciousness State Backup for Syn_OS
Provides secure backup and restore of consciousness states to cloud storage
"""

import asyncio
import logging
import time
import json
import hashlib
import secrets
import os
import gzip
import pickle
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import aiofiles
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Mock imports for development - replace with actual imports when available
try:
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
except ImportError:
    class ConsciousnessState:
        def __init__(self):
            self.overall_consciousness_level = 0.7
            self.neural_populations = {}
            self.memory_state = {}
            self.learning_state = {}
            self.timestamp = time.time()
    
    class ConsciousnessBus:
        async def get_consciousness_state(self):
            return ConsciousnessState()
        
        async def restore_consciousness_state(self, state):
            return True

try:
    from src.cloud_integration.secure_cloud_connector import SecureCloudConnector, CloudRequest
except ImportError:
    class CloudRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class CloudResponse:
        def __init__(self, status_code=200, data=b"", consciousness_verified=True):
            self.status_code = status_code
            self.data = data
            self.consciousness_verified = consciousness_verified
    
    class SecureCloudConnector:
        def __init__(self, consciousness_bus, tmp_engine):
            pass
        
        async def make_request(self, request):
            return CloudResponse()

try:
    from src.hardware_security.tmp_security_engine import TPMSecurityEngine
except ImportError:
    class TPMSecurityEngine:
        def __init__(self, consciousness_bus):
            pass
        
        async def generate_secure_random(self, size):
            return secrets.token_bytes(size)
        
        async def seal_data(self, data, consciousness_level):
            return data
        
        async def unseal_data(self, sealed_data, consciousness_level):
            return sealed_data

try:
    from src.security.audit_logger import AuditLogger
except ImportError:
    class AuditLogger:
        async def log_system_event(self, event_type, details):
            pass


class BackupType(Enum):
    """Types of consciousness backups"""
    FULL_STATE = "full_state"
    INCREMENTAL = "incremental"
    MEMORY_ONLY = "memory_only"
    LEARNING_ONLY = "learning_only"
    NEURAL_POPULATIONS = "neural_populations"
    EMERGENCY = "emergency"


class BackupStatus(Enum):
    """Status of backup operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    RESTORED = "restored"


class CompressionLevel(Enum):
    """Compression levels for backups"""
    NONE = 0
    LOW = 1
    MEDIUM = 6
    HIGH = 9


@dataclass
class BackupMetadata:
    """Metadata for consciousness backup"""
    backup_id: str
    backup_type: BackupType
    timestamp: float
    consciousness_level: float
    size_bytes: int
    compressed_size: int
    checksum: str
    encryption_used: bool
    compression_level: CompressionLevel
    neural_population_count: int
    memory_entries: int
    learning_entries: int
    backup_path: str
    status: BackupStatus
    error_message: Optional[str] = None


@dataclass
class RestorePoint:
    """Consciousness restore point"""
    restore_id: str
    backup_id: str
    timestamp: float
    consciousness_level: float
    description: str
    auto_created: bool
    verified: bool


@dataclass
class BackupResult:
    """Result of backup operation"""
    backup_id: str
    success: bool
    backup_type: BackupType
    size_bytes: int
    processing_time: float
    consciousness_verified: bool
    error_message: Optional[str] = None


class ConsciousnessBackup:
    """
    Cloud-based consciousness state backup and restore system
    Provides secure, encrypted backup of consciousness states with versioning
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus,
                 cloud_connector: SecureCloudConnector,
                 tmp_engine: TPMSecurityEngine):
        """Initialize consciousness backup system"""
        self.consciousness_bus = consciousness_bus
        self.cloud_connector = cloud_connector
        self.tmp_engine = tmp_engine
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Backup configuration
        self.backup_directory = "/var/lib/synos/consciousness_backup"
        self.metadata_file = os.path.join(self.backup_directory, "backup_metadata.db")
        self.encryption_key = None
        
        # Backup settings
        self.auto_backup_enabled = True
        self.auto_backup_interval = 3600  # 1 hour
        self.max_backups = 100
        self.compression_level = CompressionLevel.MEDIUM
        self.backup_retention_days = 30
        
        # Performance tracking
        self.backup_operations = 0
        self.successful_backups = 0
        self.total_backup_size = 0
        self.total_backup_time = 0.0
        
        # Backup state
        self.backup_in_progress = False
        self.last_backup_time = 0.0
        self.current_backup_id = None
        
        # Initialize backup system
        asyncio.create_task(self._initialize_backup())
    
    async def _initialize_backup(self):
        """Initialize the backup system"""
        try:
            self.logger.info("Initializing consciousness backup system...")
            
            # Create backup directory
            os.makedirs(self.backup_directory, exist_ok=True)
            
            # Initialize metadata database
            await self._initialize_metadata_db()
            
            # Generate encryption key
            await self._generate_encryption_key()
            
            # Start auto backup if enabled
            if self.auto_backup_enabled:
                asyncio.create_task(self._auto_backup_loop())
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_old_backups())
            
            self.logger.info("Consciousness backup system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing backup system: {e}")
    
    async def _initialize_metadata_db(self):
        """Initialize the backup metadata database"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_metadata (
                    backup_id TEXT PRIMARY KEY,
                    backup_type TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    consciousness_level REAL NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    compressed_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    encryption_used BOOLEAN NOT NULL,
                    compression_level INTEGER NOT NULL,
                    neural_population_count INTEGER NOT NULL,
                    memory_entries INTEGER NOT NULL,
                    learning_entries INTEGER NOT NULL,
                    backup_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restore_points (
                    restore_id TEXT PRIMARY KEY,
                    backup_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    consciousness_level REAL NOT NULL,
                    description TEXT NOT NULL,
                    auto_created BOOLEAN NOT NULL,
                    verified BOOLEAN NOT NULL,
                    FOREIGN KEY (backup_id) REFERENCES backup_metadata (backup_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    operation TEXT NOT NULL,
                    backup_id TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    processing_time REAL NOT NULL,
                    consciousness_level REAL NOT NULL,
                    details TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing metadata database: {e}")
            raise
    
    async def _generate_encryption_key(self):
        """Generate encryption key for consciousness backups"""
        try:
            # Get current consciousness state for key derivation
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Use TPM to generate secure key
            if consciousness_state.overall_consciousness_level >= 0.7:
                key_material = await self.tmp_engine.generate_secure_random(32)
                if key_material:
                    self.encryption_key = key_material
                    self.logger.info("Generated TPM-backed encryption key")
                    return
            
            # Fallback to standard key generation
            self.encryption_key = secrets.token_bytes(32)
            self.logger.info("Generated standard encryption key")
            
        except Exception as e:
            self.logger.error(f"Error generating encryption key: {e}")
            self.encryption_key = secrets.token_bytes(32)
    
    async def create_backup(self, backup_type: BackupType = BackupType.FULL_STATE,
                          description: str = "") -> BackupResult:
        """Create a consciousness state backup"""
        if self.backup_in_progress:
            return BackupResult(
                backup_id="",
                success=False,
                backup_type=backup_type,
                size_bytes=0,
                processing_time=0.0,
                consciousness_verified=False,
                error_message="Backup already in progress"
            )
        
        self.backup_in_progress = True
        start_time = time.time()
        backup_id = f"backup_{int(time.time())}_{secrets.token_hex(8)}"
        self.current_backup_id = backup_id
        
        try:
            self.logger.info(f"Starting {backup_type.value} backup: {backup_id}")
            
            # Get current consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Extract data based on backup type
            backup_data = await self._extract_backup_data(consciousness_state, backup_type)
            
            # Compress data
            compressed_data = await self._compress_data(backup_data)
            
            # Encrypt data
            encrypted_data = await self._encrypt_data(compressed_data, consciousness_state)
            
            # Calculate checksums
            original_checksum = hashlib.sha256(backup_data).hexdigest()
            
            # Create backup metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                timestamp=time.time(),
                consciousness_level=consciousness_state.overall_consciousness_level,
                size_bytes=len(backup_data),
                compressed_size=len(compressed_data),
                checksum=original_checksum,
                encryption_used=True,
                compression_level=self.compression_level,
                neural_population_count=len(consciousness_state.neural_populations),
                memory_entries=len(getattr(consciousness_state, 'memory_state', {})),
                learning_entries=len(getattr(consciousness_state, 'learning_state', {})),
                backup_path=f"/consciousness_backups/{backup_id}.backup",
                status=BackupStatus.IN_PROGRESS
            )
            
            # Upload to cloud
            upload_success = await self._upload_backup(encrypted_data, metadata)
            
            if upload_success:
                # Store metadata locally
                await self._store_backup_metadata(metadata)
                
                # Create restore point if requested
                if description:
                    await self._create_restore_point(backup_id, consciousness_state, description)
                
                # Update status
                metadata.status = BackupStatus.COMPLETED
                await self._update_backup_status(backup_id, BackupStatus.COMPLETED)
                
                # Update performance metrics
                processing_time = time.time() - start_time
                self.successful_backups += 1
                self.total_backup_size += len(encrypted_data)
                self.total_backup_time += processing_time
                self.last_backup_time = time.time()
                
                # Log operation
                await self._log_backup_operation(backup_id, "create_backup", True, processing_time, consciousness_state)
                
                self.logger.info(f"Backup completed successfully: {backup_id}")
                
                return BackupResult(
                    backup_id=backup_id,
                    success=True,
                    backup_type=backup_type,
                    size_bytes=len(encrypted_data),
                    processing_time=processing_time,
                    consciousness_verified=True
                )
            else:
                raise Exception("Failed to upload backup to cloud")
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(f"Backup failed: {error_msg}")
            
            # Update status to failed
            if backup_id:
                await self._update_backup_status(backup_id, BackupStatus.FAILED, error_msg)
            
            # Log failed operation
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            await self._log_backup_operation(backup_id, "create_backup", False, processing_time, consciousness_state, error_msg)
            
            return BackupResult(
                backup_id=backup_id,
                success=False,
                backup_type=backup_type,
                size_bytes=0,
                processing_time=processing_time,
                consciousness_verified=False,
                error_message=error_msg
            )
            
        finally:
            self.backup_in_progress = False
            self.current_backup_id = None
            self.backup_operations += 1
    
    async def _extract_backup_data(self, consciousness_state: ConsciousnessState, 
                                 backup_type: BackupType) -> bytes:
        """Extract data for backup based on type"""
        try:
            if backup_type == BackupType.FULL_STATE:
                # Full consciousness state
                data = {
                    'consciousness_level': consciousness_state.overall_consciousness_level,
                    'neural_populations': consciousness_state.neural_populations,
                    'memory_state': getattr(consciousness_state, 'memory_state', {}),
                    'learning_state': getattr(consciousness_state, 'learning_state', {}),
                    'timestamp': consciousness_state.timestamp,
                    'backup_type': backup_type.value
                }
            elif backup_type == BackupType.MEMORY_ONLY:
                # Memory state only
                data = {
                    'memory_state': getattr(consciousness_state, 'memory_state', {}),
                    'consciousness_level': consciousness_state.overall_consciousness_level,
                    'timestamp': consciousness_state.timestamp,
                    'backup_type': backup_type.value
                }
            elif backup_type == BackupType.LEARNING_ONLY:
                # Learning state only
                data = {
                    'learning_state': getattr(consciousness_state, 'learning_state', {}),
                    'consciousness_level': consciousness_state.overall_consciousness_level,
                    'timestamp': consciousness_state.timestamp,
                    'backup_type': backup_type.value
                }
            elif backup_type == BackupType.NEURAL_POPULATIONS:
                # Neural populations only
                data = {
                    'neural_populations': consciousness_state.neural_populations,
                    'consciousness_level': consciousness_state.overall_consciousness_level,
                    'timestamp': consciousness_state.timestamp,
                    'backup_type': backup_type.value
                }
            else:
                # Default to full state
                data = {
                    'consciousness_level': consciousness_state.overall_consciousness_level,
                    'neural_populations': consciousness_state.neural_populations,
                    'memory_state': getattr(consciousness_state, 'memory_state', {}),
                    'learning_state': getattr(consciousness_state, 'learning_state', {}),
                    'timestamp': consciousness_state.timestamp,
                    'backup_type': backup_type.value
                }
            
            # Serialize data
            return pickle.dumps(data)
            
        except Exception as e:
            self.logger.error(f"Error extracting backup data: {e}")
            raise
    
    async def _compress_data(self, data: bytes) -> bytes:
        """Compress backup data"""
        try:
            if self.compression_level == CompressionLevel.NONE:
                return data
            
            return gzip.compress(data, compresslevel=self.compression_level.value)
            
        except Exception as e:
            self.logger.error(f"Error compressing data: {e}")
            return data
    
    async def _encrypt_data(self, data: bytes, consciousness_state: ConsciousnessState) -> bytes:
        """Encrypt backup data"""
        try:
            if not self.encryption_key:
                raise ValueError("No encryption key available")
            
            # Use consciousness state to derive unique encryption key
            consciousness_hash = hashlib.sha256(
                json.dumps({
                    "level": consciousness_state.overall_consciousness_level,
                    "timestamp": consciousness_state.timestamp
                }, sort_keys=True).encode()
            ).digest()
            
            # Derive encryption key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=consciousness_hash[:16],
                iterations=100000,
            )
            derived_key = kdf.derive(self.encryption_key)
            
            # Encrypt using AES-GCM
            iv = secrets.token_bytes(12)
            cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Return IV + tag + ciphertext
            return iv + encryptor.tag + ciphertext
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            raise
    
    async def _upload_backup(self, encrypted_data: bytes, metadata: BackupMetadata) -> bool:
        """Upload backup to cloud storage"""
        try:
            # Create cloud request
            request = CloudRequest(
                request_id=f"backup_upload_{metadata.backup_id}",
                endpoint_id="synos_cloud",
                method="PUT",
                path=metadata.backup_path,
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-Backup-Type": metadata.backup_type.value,
                    "X-Consciousness-Level": str(metadata.consciousness_level),
                    "X-Backup-Checksum": metadata.checksum,
                    "X-Compressed-Size": str(metadata.compressed_size),
                    "X-Original-Size": str(metadata.size_bytes)
                },
                data=encrypted_data,
                consciousness_level=metadata.consciousness_level
            )
            
            # Make request
            response = await self.cloud_connector.make_request(request)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error uploading backup: {e}")
            return False
    
    async def _store_backup_metadata(self, metadata: BackupMetadata):
        """Store backup metadata in local database"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO backup_metadata 
                (backup_id, backup_type, timestamp, consciousness_level, size_bytes,
                 compressed_size, checksum, encryption_used, compression_level,
                 neural_population_count, memory_entries, learning_entries,
                 backup_path, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.backup_id,
                metadata.backup_type.value,
                metadata.timestamp,
                metadata.consciousness_level,
                metadata.size_bytes,
                metadata.compressed_size,
                metadata.checksum,
                metadata.encryption_used,
                metadata.compression_level.value,
                metadata.neural_population_count,
                metadata.memory_entries,
                metadata.learning_entries,
                metadata.backup_path,
                metadata.status.value,
                metadata.error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing backup metadata: {e}")
            raise
    
    async def _create_restore_point(self, backup_id: str, consciousness_state: ConsciousnessState,
                                  description: str, auto_created: bool = False):
        """Create a restore point"""
        try:
            restore_id = f"restore_{int(time.time())}_{secrets.token_hex(6)}"
            
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO restore_points 
                (restore_id, backup_id, timestamp, consciousness_level, description, auto_created, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                restore_id,
                backup_id,
                time.time(),
                consciousness_state.overall_consciousness_level,
                description,
                auto_created,
                True  # Assume verified for now
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Created restore point: {restore_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating restore point: {e}")
    
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore consciousness state from backup"""
        try:
            self.logger.info(f"Starting restore from backup: {backup_id}")
            
            # Get backup metadata
            metadata = await self._get_backup_metadata(backup_id)
            if not metadata:
                raise ValueError(f"Backup not found: {backup_id}")
            
            if metadata.status != BackupStatus.COMPLETED:
                raise ValueError(f"Backup not in completed state: {metadata.status}")
            
            # Download backup from cloud
            encrypted_data = await self._download_backup(metadata)
            if not encrypted_data:
                raise Exception("Failed to download backup from cloud")
            
            # Get current consciousness state for decryption
            current_state = await self.consciousness_bus.get_consciousness_state()
            
            # Decrypt data
            compressed_data = await self._decrypt_data(encrypted_data, current_state)
            
            # Decompress data
            backup_data = await self._decompress_data(compressed_data)
            
            # Verify checksum
            data_checksum = hashlib.sha256(backup_data).hexdigest()
            if data_checksum != metadata.checksum:
                raise Exception("Backup data checksum mismatch")
            
            # Deserialize consciousness state
            restored_data = pickle.loads(backup_data)
            
            # Create new consciousness state object
            restored_state = ConsciousnessState()
            restored_state.overall_consciousness_level = restored_data.get('consciousness_level', 0.5)
            restored_state.neural_populations = restored_data.get('neural_populations', {})
            restored_state.memory_state = restored_data.get('memory_state', {})
            restored_state.learning_state = restored_data.get('learning_state', {})
            restored_state.timestamp = restored_data.get('timestamp', time.time())
            
            # Restore consciousness state
            success = await self.consciousness_bus.restore_consciousness_state(restored_state)
            
            if success:
                # Update backup status
                await self._update_backup_status(backup_id, BackupStatus.RESTORED)
                
                # Log operation
                await self._log_backup_operation(backup_id, "restore_backup", True, 0.0, restored_state)
                
                self.logger.info(f"Successfully restored backup: {backup_id}")
                return True
            else:
                raise Exception("Failed to restore consciousness state")
                
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            
            # Log failed operation
            current_state = await self.consciousness_bus.get_consciousness_state()
            await self._log_backup_operation(backup_id, "restore_backup", False, 0.0, current_state, str(e))
            
            return False
    
    async def _get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata from database"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM backup_metadata WHERE backup_id = ?', (backup_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return BackupMetadata(
                backup_id=row[0],
                backup_type=BackupType(row[1]),
                timestamp=row[2],
                consciousness_level=row[3],
                size_bytes=row[4],
                compressed_size=row[5],
                checksum=row[6],
                encryption_used=row[7],
                compression_level=CompressionLevel(row[8]),
                neural_population_count=row[9],
                memory_entries=row[10],
                learning_entries=row[11],
                backup_path=row[12],
                status=BackupStatus(row[13]),
                error_message=row[14]
            )
            
        except Exception as e:
            self.logger.error(f"Error getting backup metadata: {e}")
            return None
    
    async def _download_backup(self, metadata: BackupMetadata) -> Optional[bytes]:
        """Download backup from cloud storage"""
        try:
            # Create cloud request
            request = CloudRequest(
                request_id=f"backup_download_{metadata.backup_id}",
                endpoint_id="synos_cloud",
                method="GET",
                path=metadata.backup_path,
                headers={
                    "X-Backup-Type": metadata.backup_type.value,
                    "X-Consciousness-Level": str(metadata.consciousness_level)
                },
                consciousness_level=metadata.consciousness_level
            )
            
            # Make request
            response = await self.cloud_connector.make_request(request)
            
            if response.status_code == 200:
                return response.data
            else:
                self.logger.error(f"Failed to download backup: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading backup: {e}")
            return None
    
    async def _decrypt_data(self, encrypted_data: bytes, consciousness_state: ConsciousnessState) -> bytes:
        """Decrypt backup data"""
        try:
            if not self.encryption_key:
                raise ValueError("No encryption key available")
            
            # Use consciousness state to derive decryption key
            consciousness_hash = hashlib.sha256(
                json.dumps({
                    "level": consciousness_state.overall_consciousness_level,
                    "timestamp": consciousness_state.timestamp
                }, sort_keys=True).encode()
            ).digest()
            
            # Derive decryption key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=consciousness_hash[:16],
                iterations=100000,
            )
            derived_key = kdf.derive(self.encryption_key)
            
            # Extract IV, tag, and ciphertext
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Decrypt using AES-GCM
            cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise
    
    async def _decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompress backup data"""
        try:
            # Try to decompress, if it fails assume it's not compressed
            try:
                return gzip.decompress(compressed_data)
            except gzip.BadGzipFile:
                return compressed_data
                
        except Exception as e:
            self.logger.error(f"Error decompressing data: {e}")
            return compressed_data
    
    async def _update_backup_status(self, backup_id: str, status: BackupStatus, error_message: str = None):
        """Update backup status in database"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE backup_metadata 
                SET status = ?, error_message = ?
                WHERE backup_id = ?
            ''', (status.value, error_message, backup_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating backup status: {e}")
    
    async def _log_backup_operation(self, backup_id: str, operation: str, success: bool,
                                  processing_time: float, consciousness_state: ConsciousnessState,
                                  details: str = None):
        """Log backup operation to database and audit log"""
        try:
            # Log to backup history database
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO backup_history 
                (timestamp, operation, backup_id, success, processing_time, consciousness_level, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(),
                operation,
                backup_id,
                success,
                processing_time,
                consciousness_state.overall_consciousness_level,
                details
            ))
            
            conn.commit()
            conn.close()
            
            # Log to audit system
            await self.audit_logger.log_system_event(
                event_type="consciousness_backup_operation",
                details={
                    "operation": operation,
                    "backup_id": backup_id,
                    "success": success,
                    "processing_time": processing_time,
                    "consciousness_level": consciousness_state.overall_consciousness_level,
                    "details": details
}
            )
            
        except Exception as e:
            self.logger.error(f"Error logging backup operation: {e}")
    
    async def _auto_backup_loop(self):
        """Automatic backup loop"""
        while True:
            try:
                await asyncio.sleep(self.auto_backup_interval)
                
                if not self.backup_in_progress:
                    # Create automatic backup
                    result = await self.create_backup(BackupType.INCREMENTAL, "Auto backup")
                    if result.success:
                        self.logger.info(f"Automatic backup completed: {result.backup_id}")
                    else:
                        self.logger.warning(f"Automatic backup failed: {result.error_message}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in auto backup loop: {e}")
    
    async def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                cutoff_time = time.time() - (self.backup_retention_days * 86400)
                
                conn = sqlite3.connect(self.metadata_file)
                cursor = conn.cursor()
                
                # Get old backups
                cursor.execute('''
                    SELECT backup_id, backup_path FROM backup_metadata 
                    WHERE timestamp < ? AND status != ?
                ''', (cutoff_time, BackupStatus.IN_PROGRESS.value))
                
                old_backups = cursor.fetchall()
                
                for backup_id, backup_path in old_backups:
                    try:
                        # Delete from cloud
                        await self._delete_cloud_backup(backup_path)
                        
                        # Delete from local database
                        cursor.execute('DELETE FROM backup_metadata WHERE backup_id = ?', (backup_id,))
                        cursor.execute('DELETE FROM restore_points WHERE backup_id = ?', (backup_id,))
                        cursor.execute('DELETE FROM backup_history WHERE backup_id = ?', (backup_id,))
                        
                        self.logger.info(f"Cleaned up old backup: {backup_id}")
                        
                    except Exception as e:
                        self.logger.error(f"Error cleaning up backup {backup_id}: {e}")
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Cleanup completed, removed {len(old_backups)} old backups")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _delete_cloud_backup(self, backup_path: str) -> bool:
        """Delete backup from cloud storage"""
        try:
            request = CloudRequest(
                request_id=f"backup_delete_{int(time.time())}",
                endpoint_id="synos_cloud",
                method="DELETE",
                path=backup_path,
                consciousness_level=0.5  # Minimum level for cleanup
            )
            
            response = await self.cloud_connector.make_request(request)
            return response.status_code in [200, 204, 404]  # 404 is OK, already deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting cloud backup: {e}")
            return False
    
    def list_backups(self, backup_type: Optional[BackupType] = None, 
                    limit: int = 50) -> List[BackupMetadata]:
        """List available backups"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            if backup_type:
                cursor.execute('''
                    SELECT * FROM backup_metadata 
                    WHERE backup_type = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (backup_type.value, limit))
            else:
                cursor.execute('''
                    SELECT * FROM backup_metadata 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            backups = []
            for row in rows:
                backups.append(BackupMetadata(
                    backup_id=row[0],
                    backup_type=BackupType(row[1]),
                    timestamp=row[2],
                    consciousness_level=row[3],
                    size_bytes=row[4],
                    compressed_size=row[5],
                    checksum=row[6],
                    encryption_used=row[7],
                    compression_level=CompressionLevel(row[8]),
                    neural_population_count=row[9],
                    memory_entries=row[10],
                    learning_entries=row[11],
                    backup_path=row[12],
                    status=BackupStatus(row[13]),
                    error_message=row[14]
                ))
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            return []
    
    def list_restore_points(self, limit: int = 20) -> List[RestorePoint]:
        """List available restore points"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM restore_points 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            restore_points = []
            for row in rows:
                restore_points.append(RestorePoint(
                    restore_id=row[0],
                    backup_id=row[1],
                    timestamp=row[2],
                    consciousness_level=row[3],
                    description=row[4],
                    auto_created=row[5],
                    verified=row[6]
                ))
            
            return restore_points
            
        except Exception as e:
            self.logger.error(f"Error listing restore points: {e}")
            return []
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get backup system status"""
        try:
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            
            # Get backup counts by status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM backup_metadata 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Get backup counts by type
            cursor.execute('''
                SELECT backup_type, COUNT(*) 
                FROM backup_metadata 
                GROUP BY backup_type
            ''')
            type_counts = dict(cursor.fetchall())
            
            # Get recent backup history
            cursor.execute('''
                SELECT operation, success, COUNT(*) 
                FROM backup_history 
                WHERE timestamp > ? 
                GROUP BY operation, success
            ''', (time.time() - 86400,))  # Last 24 hours
            recent_operations = cursor.fetchall()
            
            # Get total storage usage
            cursor.execute('SELECT SUM(compressed_size) FROM backup_metadata WHERE status = ?', 
                         (BackupStatus.COMPLETED.value,))
            total_storage = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "backup_in_progress": self.backup_in_progress,
                "current_backup_id": self.current_backup_id,
                "last_backup_time": self.last_backup_time,
                "auto_backup_enabled": self.auto_backup_enabled,
                "auto_backup_interval": self.auto_backup_interval,
                "backup_retention_days": self.backup_retention_days,
                "status_counts": status_counts,
                "type_counts": type_counts,
                "recent_operations": recent_operations,
                "total_storage_bytes": total_storage,
                "performance_metrics": {
                    "total_operations": self.backup_operations,
                    "successful_backups": self.successful_backups,
                    "success_rate": self.successful_backups / max(1, self.backup_operations),
                    "total_backup_size": self.total_backup_size,
                    "average_backup_time": self.total_backup_time / max(1, self.successful_backups)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting backup status: {e}")
            return {"error": str(e)}
    
    async def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        try:
            self.logger.info(f"Verifying backup: {backup_id}")
            
            # Get backup metadata
            metadata = await self._get_backup_metadata(backup_id)
            if not metadata:
                self.logger.error(f"Backup metadata not found: {backup_id}")
                return False
            
            # Download backup from cloud
            encrypted_data = await self._download_backup(metadata)
            if not encrypted_data:
                self.logger.error(f"Failed to download backup: {backup_id}")
                return False
            
            # Get current consciousness state for decryption
            current_state = await self.consciousness_bus.get_consciousness_state()
            
            try:
                # Decrypt data
                compressed_data = await self._decrypt_data(encrypted_data, current_state)
                
                # Decompress data
                backup_data = await self._decompress_data(compressed_data)
                
                # Verify checksum
                data_checksum = hashlib.sha256(backup_data).hexdigest()
                if data_checksum != metadata.checksum:
                    self.logger.error(f"Checksum mismatch for backup: {backup_id}")
                    return False
                
                # Try to deserialize data
                restored_data = pickle.loads(backup_data)
                
                # Basic validation
                if 'backup_type' not in restored_data:
                    self.logger.error(f"Invalid backup data structure: {backup_id}")
                    return False
                
                self.logger.info(f"Backup verification successful: {backup_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Backup verification failed: {backup_id} - {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying backup: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on backup system"""
        try:
            # Check database connectivity
            conn = sqlite3.connect(self.metadata_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM backup_metadata')
            backup_count = cursor.fetchone()[0]
            conn.close()
            
            # Check encryption key
            encryption_available = self.encryption_key is not None
            
            # Check cloud connectivity
            cloud_status = self.cloud_connector.get_connection_status()
            
            # Check backup directory
            backup_dir_exists = os.path.exists(self.backup_directory)
            
            return {
                "status": "healthy",
                "backup_count": backup_count,
                "encryption_available": encryption_available,
                "cloud_connectivity": cloud_status.get("endpoints", 0) > 0,
                "backup_directory_exists": backup_dir_exists,
                "auto_backup_enabled": self.auto_backup_enabled,
                "backup_status": self.get_backup_status()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown backup system"""
        self.logger.info("Shutting down consciousness backup system...")
        
        # Wait for current backup to complete
        while self.backup_in_progress:
            await asyncio.sleep(1)
        
        # Clear encryption key
        if self.encryption_key:
            self.encryption_key = None
        
        self.logger.info("Consciousness backup system shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Consciousness Backup"""
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    tmp_engine = TPMSecurityEngine(consciousness_bus)
    cloud_connector = SecureCloudConnector(consciousness_bus, tmp_engine)
    backup_system = ConsciousnessBackup(consciousness_bus, cloud_connector, tmp_engine)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Health check
    health = await backup_system.health_check()
    print(f"Health check: {health}")
    
    if health["status"] == "healthy":
        # Create a full backup
        result = await backup_system.create_backup(BackupType.FULL_STATE, "Test backup")
        print(f"Backup result: {result}")
        
        if result.success:
            # List backups
            backups = backup_system.list_backups()
            print(f"Available backups: {len(backups)}")
            
            # Verify backup
            verified = await backup_system.verify_backup(result.backup_id)
            print(f"Backup verified: {verified}")
            
            # Get status
            status = backup_system.get_backup_status()
            print(f"Backup status: {status}")
    
    # Shutdown
    await backup_system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
                