#!/usr/bin/env python3
"""
Encrypted Data Synchronization for Syn_OS
Provides secure, consciousness-aware data synchronization across cloud environments
"""

import asyncio
import logging
import time
import json
import hashlib
import secrets
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import aiofiles
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Mock imports for development - replace with actual imports when available
try:
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
except ImportError:
    class ConsciousnessState:
        def __init__(self):
            self.overall_consciousness_level = 0.7
            self.neural_populations = {}
    
    class ConsciousnessBus:
        async def get_consciousness_state(self):
            return ConsciousnessState()

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
        
        def get_connection_status(self):
            return {"endpoints": 1}

try:
    from src.hardware_security.tmp_security_engine import TPMSecurityEngine
except ImportError:
    class TPMSecurityEngine:
        def __init__(self, consciousness_bus):
            pass
        
        async def generate_secure_random(self, size):
            return secrets.token_bytes(size)

try:
    from src.security.audit_logger import AuditLogger
except ImportError:
    class AuditLogger:
        async def log_system_event(self, event_type, details):
            pass


class SyncOperation(Enum):
    """Types of synchronization operations"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    SYNC = "sync"
    BACKUP = "backup"
    RESTORE = "restore"


class DataType(Enum):
    """Types of data to synchronize"""
    CONSCIOUSNESS_STATE = "consciousness_state"
    SECURITY_CONFIGS = "security_configs"
    USER_PROFILES = "user_profiles"
    THREAT_INTELLIGENCE = "threat_intelligence"
    SCAN_RESULTS = "scan_results"
    CUSTOM_TOOLS = "custom_tools"
    SYSTEM_LOGS = "system_logs"
    CERTIFICATES = "certificates"


class EncryptionLevel(Enum):
    """Encryption levels for data"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    CONSCIOUSNESS_BOUND = "consciousness_bound"


@dataclass
class SyncItem:
    """Data item for synchronization"""
    item_id: str
    data_type: DataType
    local_path: str
    remote_path: str
    encryption_level: EncryptionLevel
    consciousness_level_required: float
    last_modified: float
    checksum: str
    size: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SyncResult:
    """Result of synchronization operation"""
    operation: SyncOperation
    item_id: str
    success: bool
    bytes_transferred: int
    processing_time: float
    encryption_used: bool
    consciousness_verified: bool
    error_message: Optional[str] = None


@dataclass
class SyncManifest:
    """Synchronization manifest"""
    manifest_id: str
    timestamp: float
    consciousness_level: float
    items: List[SyncItem]
    total_size: int
    checksum: str


class EncryptedDataSync:
    """
    Encrypted data synchronization with consciousness-aware security
    Provides secure cloud data synchronization with TPM-backed encryption
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus, 
                 cloud_connector: SecureCloudConnector,
                 tmp_engine: TPMSecurityEngine):
        """Initialize encrypted data sync"""
        self.consciousness_bus = consciousness_bus
        self.cloud_connector = cloud_connector
        self.tmp_engine = tmp_engine
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Sync configuration
        self.sync_directory = "/var/lib/synos/sync"
        self.manifest_file = os.path.join(self.sync_directory, "sync_manifest.db")
        self.encryption_keys: Dict[str, bytes] = {}
        
        # Performance tracking
        self.sync_operations = 0
        self.successful_syncs = 0
        self.total_bytes_synced = 0
        self.total_sync_time = 0.0
        
        # Sync state
        self.sync_in_progress = False
        self.last_sync_time = 0.0
        self.sync_interval = 300  # 5 minutes default
        
        # Initialize sync system
        asyncio.create_task(self._initialize_sync())
    
    async def _initialize_sync(self):
        """Initialize the synchronization system"""
        try:
            self.logger.info("Initializing encrypted data sync...")
            
            # Create sync directory
            os.makedirs(self.sync_directory, exist_ok=True)
            
            # Initialize manifest database
            await self._initialize_manifest_db()
            
            # Generate encryption keys
            await self._generate_encryption_keys()
            
            # Start periodic sync
            asyncio.create_task(self._periodic_sync())
            
            self.logger.info("Encrypted data sync initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing data sync: {e}")
    
    async def _initialize_manifest_db(self):
        """Initialize the sync manifest database"""
        try:
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_items (
                    item_id TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    local_path TEXT NOT NULL,
                    remote_path TEXT NOT NULL,
                    encryption_level TEXT NOT NULL,
                    consciousness_level_required REAL NOT NULL,
                    last_modified REAL NOT NULL,
                    checksum TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    operation TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    bytes_transferred INTEGER NOT NULL,
                    processing_time REAL NOT NULL,
                    consciousness_level REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing manifest database: {e}")
            raise
    
    async def _generate_encryption_keys(self):
        """Generate encryption keys for different security levels"""
        try:
            # Get current consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Generate keys for different encryption levels
            for level in EncryptionLevel:
                if level == EncryptionLevel.CONSCIOUSNESS_BOUND:
                    # Use TPM for consciousness-bound encryption
                    if consciousness_state.overall_consciousness_level >= 0.8:
                        key_bytes = await self.tmp_engine.generate_secure_random(32)
                        if key_bytes:
                            self.encryption_keys[level.value] = key_bytes
                            continue
                
                # Generate standard encryption key
                self.encryption_keys[level.value] = secrets.token_bytes(32)
            
            self.logger.info(f"Generated {len(self.encryption_keys)} encryption keys")
            
        except Exception as e:
            self.logger.error(f"Error generating encryption keys: {e}")
            # Fallback to basic keys
            for level in EncryptionLevel:
                self.encryption_keys[level.value] = secrets.token_bytes(32)
    
    async def add_sync_item(self, item: SyncItem) -> bool:
        """Add item to synchronization manifest"""
        try:
            # Validate item
            if not os.path.exists(item.local_path):
                self.logger.error(f"Local path does not exist: {item.local_path}")
                return False
            
            # Calculate file checksum
            checksum = await self._calculate_file_checksum(item.local_path)
            item.checksum = checksum
            
            # Get file size
            item.size = os.path.getsize(item.local_path)
            item.last_modified = os.path.getmtime(item.local_path)
            
            # Store in database
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sync_items 
                (item_id, data_type, local_path, remote_path, encryption_level, 
                 consciousness_level_required, last_modified, checksum, size, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.item_id,
                item.data_type.value,
                item.local_path,
                item.remote_path,
                item.encryption_level.value,
                item.consciousness_level_required,
                item.last_modified,
                item.checksum,
                item.size,
                json.dumps(item.metadata) if item.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added sync item: {item.item_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding sync item: {e}")
            return False
    
    async def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        try:
            hash_sha256 = hashlib.sha256()
            async with aiofiles.open(file_path, 'rb') as f:
                async for chunk in f:
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return ""
    
    async def sync_item(self, item_id: str, operation: SyncOperation) -> SyncResult:
        """Synchronize a specific item"""
        start_time = time.time()
        self.sync_operations += 1
        
        try:
            # Get item from manifest
            item = await self._get_sync_item(item_id)
            if not item:
                raise ValueError(f"Sync item not found: {item_id}")
            
            # Check consciousness level requirement
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            current_consciousness = consciousness_state.overall_consciousness_level
            
            if current_consciousness < item.consciousness_level_required:
                raise ValueError(
                    f"Insufficient consciousness level: {current_consciousness} < {item.consciousness_level_required}"
                )
            
            # Perform sync operation
            if operation == SyncOperation.UPLOAD:
                result = await self._upload_item(item, consciousness_state)
            elif operation == SyncOperation.DOWNLOAD:
                result = await self._download_item(item, consciousness_state)
            elif operation == SyncOperation.DELETE:
                result = await self._delete_item(item, consciousness_state)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Update performance metrics
            processing_time = time.time() - start_time
            if result.success:
                self.successful_syncs += 1
                self.total_bytes_synced += result.bytes_transferred
                self.total_sync_time += processing_time
            
            # Log sync operation
            await self._log_sync_operation(result, consciousness_state)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.error(f"Sync operation error: {e}")
            
            return SyncResult(
                operation=operation,
                item_id=item_id,
                success=False,
                bytes_transferred=0,
                processing_time=processing_time,
                encryption_used=False,
                consciousness_verified=False,
                error_message=str(e)
            )
    
    async def _get_sync_item(self, item_id: str) -> Optional[SyncItem]:
        """Get sync item from manifest"""
        try:
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sync_items WHERE item_id = ?', (item_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return SyncItem(
                item_id=row[0],
                data_type=DataType(row[1]),
                local_path=row[2],
                remote_path=row[3],
                encryption_level=EncryptionLevel(row[4]),
                consciousness_level_required=row[5],
                last_modified=row[6],
                checksum=row[7],
                size=row[8],
                metadata=json.loads(row[9]) if row[9] else None
            )
            
        except Exception as e:
            self.logger.error(f"Error getting sync item: {e}")
            return None
    
    async def _upload_item(self, item: SyncItem, consciousness_state: ConsciousnessState) -> SyncResult:
        """Upload item to cloud"""
        try:
            # Read file data
            async with aiofiles.open(item.local_path, 'rb') as f:
                file_data = await f.read()
            
            # Encrypt data
            encrypted_data, encryption_used = await self._encrypt_data(
                file_data, item.encryption_level, consciousness_state
            )
            
            # Create cloud request
            request = CloudRequest(
                request_id=f"upload_{item.item_id}_{int(time.time())}",
                endpoint_id="synos_cloud",
                method="PUT",
                path=f"/api/v1/sync{item.remote_path}",
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-Data-Type": item.data_type.value,
                    "X-Encryption-Level": item.encryption_level.value,
                    "X-Consciousness-Required": str(item.consciousness_level_required),
                    "X-File-Checksum": item.checksum
                },
                data=encrypted_data,
                consciousness_level=consciousness_state.overall_consciousness_level
            )
            
            # Make request
            response = await self.cloud_connector.make_request(request)
            
            if response.status_code in [200, 201]:
                return SyncResult(
                    operation=SyncOperation.UPLOAD,
                    item_id=item.item_id,
                    success=True,
                    bytes_transferred=len(encrypted_data),
                    processing_time=0.0,  # Will be set by caller
                    encryption_used=encryption_used,
                    consciousness_verified=response.consciousness_verified
                )
            else:
                raise Exception(f"Upload failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error uploading item: {e}")
            raise
    
    async def _download_item(self, item: SyncItem, consciousness_state: ConsciousnessState) -> SyncResult:
        """Download item from cloud"""
        try:
            # Create cloud request
            request = CloudRequest(
                request_id=f"download_{item.item_id}_{int(time.time())}",
                endpoint_id="synos_cloud",
                method="GET",
                path=f"/api/v1/sync{item.remote_path}",
                headers={
                    "X-Data-Type": item.data_type.value,
                    "X-Consciousness-Required": str(item.consciousness_level_required)
                },
                consciousness_level=consciousness_state.overall_consciousness_level
            )
            
            # Make request
            response = await self.cloud_connector.make_request(request)
            
            if response.status_code == 200:
                # Decrypt data
                decrypted_data, encryption_used = await self._decrypt_data(
                    response.data, item.encryption_level, consciousness_state
                )
                
                # Verify checksum
                downloaded_checksum = hashlib.sha256(decrypted_data).hexdigest()
                if downloaded_checksum != item.checksum:
                    raise Exception("Checksum mismatch after download")
                
                # Write to local file
                os.makedirs(os.path.dirname(item.local_path), exist_ok=True)
                async with aiofiles.open(item.local_path, 'wb') as f:
                    await f.write(decrypted_data)
                
                return SyncResult(
                    operation=SyncOperation.DOWNLOAD,
                    item_id=item.item_id,
                    success=True,
                    bytes_transferred=len(response.data),
                    processing_time=0.0,  # Will be set by caller
                    encryption_used=encryption_used,
                    consciousness_verified=response.consciousness_verified
                )
            else:
                raise Exception(f"Download failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error downloading item: {e}")
            raise
    
    async def _delete_item(self, item: SyncItem, consciousness_state: ConsciousnessState) -> SyncResult:
        """Delete item from cloud"""
        try:
            # Create cloud request
            request = CloudRequest(
                request_id=f"delete_{item.item_id}_{int(time.time())}",
                endpoint_id="synos_cloud",
                method="DELETE",
                path=f"/api/v1/sync{item.remote_path}",
                headers={
                    "X-Data-Type": item.data_type.value,
                    "X-Consciousness-Required": str(item.consciousness_level_required)
                },
                consciousness_level=consciousness_state.overall_consciousness_level
            )
            
            # Make request
            response = await self.cloud_connector.make_request(request)
            
            if response.status_code in [200, 204]:
                # Remove from local manifest
                conn = sqlite3.connect(self.manifest_file)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM sync_items WHERE item_id = ?', (item.item_id,))
                conn.commit()
                conn.close()
                
                return SyncResult(
                    operation=SyncOperation.DELETE,
                    item_id=item.item_id,
                    success=True,
                    bytes_transferred=0,
                    processing_time=0.0,  # Will be set by caller
                    encryption_used=False,
                    consciousness_verified=response.consciousness_verified
                )
            else:
                raise Exception(f"Delete failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error deleting item: {e}")
            raise
    
    async def _encrypt_data(self, data: bytes, encryption_level: EncryptionLevel, 
                          consciousness_state: ConsciousnessState) -> Tuple[bytes, bool]:
        """Encrypt data based on encryption level"""
        try:
            if encryption_level == EncryptionLevel.BASIC:
                return data, False  # No encryption for basic level
            
            # Get encryption key
            encryption_key = self.encryption_keys.get(encryption_level.value)
            if not encryption_key:
                raise ValueError(f"No encryption key for level: {encryption_level}")
            
            # For consciousness-bound encryption, mix with consciousness state
            if encryption_level == EncryptionLevel.CONSCIOUSNESS_BOUND:
                consciousness_hash = hashlib.sha256(
                    json.dumps({
                        "level": consciousness_state.overall_consciousness_level,
                        "populations": consciousness_state.neural_populations
                    }, sort_keys=True).encode()
                ).digest()
                
                # Derive key from base key + consciousness
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=consciousness_hash[:16],
                    iterations=100000,
                )
                encryption_key = kdf.derive(encryption_key)
            
            # Encrypt using AES-GCM
            iv = secrets.token_bytes(12)
            cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Return IV + tag + ciphertext
            encrypted_data = iv + encryptor.tag + ciphertext
            return encrypted_data, True
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            raise
    
    async def _decrypt_data(self, encrypted_data: bytes, encryption_level: EncryptionLevel,
                          consciousness_state: ConsciousnessState) -> Tuple[bytes, bool]:
        """Decrypt data based on encryption level"""
        try:
            if encryption_level == EncryptionLevel.BASIC:
                return encrypted_data, False  # No decryption for basic level
            
            # Get encryption key
            encryption_key = self.encryption_keys.get(encryption_level.value)
            if not encryption_key:
                raise ValueError(f"No encryption key for level: {encryption_level}")
            
            # For consciousness-bound encryption, mix with consciousness state
            if encryption_level == EncryptionLevel.CONSCIOUSNESS_BOUND:
                consciousness_hash = hashlib.sha256(
                    json.dumps({
                        "level": consciousness_state.overall_consciousness_level,
                        "populations": consciousness_state.neural_populations
                    }, sort_keys=True).encode()
                ).digest()
                
                # Derive key from base key + consciousness
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=consciousness_hash[:16],
                    iterations=100000,
                )
                encryption_key = kdf.derive(encryption_key)
            
            # Extract IV, tag, and ciphertext
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Decrypt using AES-GCM
            cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext, True
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise
    
    async def _log_sync_operation(self, result: SyncResult, consciousness_state: ConsciousnessState):
        """Log sync operation to database and audit log"""
        try:
            # Log to sync history database
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sync_history 
                (timestamp, operation, item_id, success, bytes_transferred, 
                 processing_time, consciousness_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(),
                result.operation.value,
                result.item_id,
                result.success,
                result.bytes_transferred,
                result.processing_time,
                consciousness_state.overall_consciousness_level
            ))
            
            conn.commit()
            conn.close()
            
            # Log to audit system
            await self.audit_logger.log_system_event(
                event_type="data_sync_operation",
                details={
                    "operation": result.operation.value,
                    "item_id": result.item_id,
                    "success": result.success,
                    "bytes_transferred": result.bytes_transferred,
                    "encryption_used": result.encryption_used,
                    "consciousness_verified": result.consciousness_verified,
                    "consciousness_level": consciousness_state.overall_consciousness_level
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error logging sync operation: {e}")
    
    async def sync_all(self) -> List[SyncResult]:
        """Synchronize all items in manifest"""
        if self.sync_in_progress:
            self.logger.warning("Sync already in progress")
            return []
        
        self.sync_in_progress = True
        results = []
        
        try:
            # Get all sync items
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            cursor.execute('SELECT item_id FROM sync_items')
            item_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.logger.info(f"Starting sync of {len(item_ids)} items")
            
            # Sync each item
            for item_id in item_ids:
                try:
                    # Check if local file is newer
                    item = await self._get_sync_item(item_id)
                    if item and os.path.exists(item.local_path):
                        current_mtime = os.path.getmtime(item.local_path)
                        if current_mtime > item.last_modified:
                            # Upload newer local file
                            result = await self.sync_item(item_id, SyncOperation.UPLOAD)
                            results.append(result)
                            
                            # Update manifest with new modification time
                            if result.success:
                                await self._update_item_manifest(item_id, current_mtime)
                    
                except Exception as e:
                        self.logger.error(f"Error syncing item {item_id}: {e}")
                        results.append(SyncResult(
                            operation=SyncOperation.SYNC,
                            item_id=item_id,
                            success=False,
                            bytes_transferred=0,
                            processing_time=0.0,
                            encryption_used=False,
                            consciousness_verified=False,
                            error_message=str(e)
                        ))
            
            self.last_sync_time = time.time()
            self.logger.info(f"Sync completed: {len([r for r in results if r.success])}/{len(results)} successful")
            
            return results
            
        finally:
            self.sync_in_progress = False
    
    async def _update_item_manifest(self, item_id: str, new_mtime: float):
        """Update item modification time in manifest"""
        try:
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE sync_items SET last_modified = ? WHERE item_id = ?',
                (new_mtime, item_id)
            )
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating item manifest: {e}")
    
    async def _periodic_sync(self):
        """Perform periodic synchronization"""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                
                if not self.sync_in_progress:
                    await self.sync_all()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic sync: {e}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        try:
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            
            # Get item counts by type
            cursor.execute('''
                SELECT data_type, COUNT(*) 
                FROM sync_items 
                GROUP BY data_type
            ''')
            items_by_type = dict(cursor.fetchall())
            
            # Get recent sync history
            cursor.execute('''
                SELECT operation, success, COUNT(*) 
                FROM sync_history 
                WHERE timestamp > ? 
                GROUP BY operation, success
            ''', (time.time() - 86400,))  # Last 24 hours
            recent_operations = cursor.fetchall()
            
            conn.close()
            
            return {
                "sync_in_progress": self.sync_in_progress,
                "last_sync_time": self.last_sync_time,
                "sync_interval": self.sync_interval,
                "items_by_type": items_by_type,
                "recent_operations": recent_operations,
                "performance_metrics": {
                    "total_operations": self.sync_operations,
                    "successful_syncs": self.successful_syncs,
                    "success_rate": self.successful_syncs / max(1, self.sync_operations),
                    "total_bytes_synced": self.total_bytes_synced,
                    "average_sync_time": self.total_sync_time / max(1, self.successful_syncs)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sync status: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on data sync"""
        try:
            # Check database connectivity
            conn = sqlite3.connect(self.manifest_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM sync_items')
            item_count = cursor.fetchone()[0]
            conn.close()
            
            # Check encryption keys
            keys_available = len(self.encryption_keys)
            
            # Check cloud connectivity
            cloud_status = self.cloud_connector.get_connection_status()
            
            return {
                "status": "healthy",
                "manifest_items": item_count,
                "encryption_keys": keys_available,
                "cloud_connectivity": cloud_status.get("endpoints", 0) > 0,
                "sync_directory_exists": os.path.exists(self.sync_directory),
                "sync_status": self.get_sync_status()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown data sync system"""
        self
self.logger.info("Shutting down encrypted data sync...")
        
        # Wait for current sync to complete
        while self.sync_in_progress:
            await asyncio.sleep(1)
        
        # Clear encryption keys
        self.encryption_keys.clear()
        
        self.logger.info("Encrypted data sync shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Encrypted Data Sync"""
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    tmp_engine = TPMSecurityEngine(consciousness_bus)
    cloud_connector = SecureCloudConnector(consciousness_bus, tmp_engine)
    data_sync = EncryptedDataSync(consciousness_bus, cloud_connector, tmp_engine)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Health check
    health = await data_sync.health_check()
    print(f"Health check: {health}")
    
    if health["status"] == "healthy":
        # Add test sync item
        test_item = SyncItem(
            item_id="test_config",
            data_type=DataType.SECURITY_CONFIGS,
            local_path="/tmp/test_config.json",
            remote_path="/configs/test_config.json",
            encryption_level=EncryptionLevel.ENHANCED,
            consciousness_level_required=0.5,
            last_modified=time.time(),
            checksum="",
            size=0
        )
        
        # Create test file
        test_data = {"test": "configuration"}
        os.makedirs("/tmp", exist_ok=True)
        with open("/tmp/test_config.json", "w") as f:
            json.dump(test_data, f)
        
        # Add to sync
        success = await data_sync.add_sync_item(test_item)
        print(f"Added sync item: {success}")
        
        if success:
            # Test sync operation
            result = await data_sync.sync_item("test_config", SyncOperation.UPLOAD)
            print(f"Sync result: {result}")
    
    # Shutdown
    await data_sync.shutdown()


if __name__ == "__main__":
    asyncio.run(main())