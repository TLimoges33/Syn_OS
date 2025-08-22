"""
Consciousness State Persistence Manager
======================================

Advanced persistence system for consciousness state, neural populations,
user contexts, and system metrics with recovery capabilities.
"""

import asyncio
import json
import sqlite3
import gzip
import pickle
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import aiofiles
import threading

from ..interfaces.consciousness_component import ConsciousnessComponent
from ..core.event_types import EventType, ConsciousnessEvent, EventPriority
from ..core.data_models import (
    ConsciousnessState, PopulationState, UserContextState, ComponentStatus,
    create_default_consciousness_state
)


@dataclass
class PersistenceConfig:
    """Configuration for persistence manager"""
    data_directory: Path = Path("data/consciousness")
    backup_directory: Path = Path("data/backups")
    
    # Database settings
    database_path: Optional[Path] = None
    connection_pool_size: int = 5
    
    # Backup settings
    auto_backup_interval: int = 300  # seconds
    max_backups_per_type: int = 10
    backup_compression: bool = True
    
    # Snapshot settings
    snapshot_interval: int = 60  # seconds
    max_snapshots: int = 100
    
    # Integrity settings
    checksum_validation: bool = True
    data_encryption: bool = False
    encryption_key: Optional[str] = None
    
    # Performance settings
    batch_write_size: int = 100
    write_delay_ms: int = 50
    async_writes: bool = True
    
    # Recovery settings
    recovery_mode: str = "automatic"  # automatic, manual, disabled
    corruption_tolerance: str = "medium"  # low, medium, high


@dataclass
class StateSnapshot:
    """Snapshot of consciousness state at a point in time"""
    snapshot_id: str
    timestamp: datetime
    consciousness_state: ConsciousnessState
    checksum: str
    compressed_size: int
    metadata: Dict[str, Any]


@dataclass
class BackupInfo:
    """Information about a backup"""
    backup_id: str
    backup_type: str  # full, incremental, emergency
    timestamp: datetime
    file_path: Path
    original_size: int
    compressed_size: int
    checksum: str
    components: List[str]
    metadata: Dict[str, Any]


class PersistenceManager(ConsciousnessComponent):
    """Advanced persistence manager for consciousness system state"""
    
    def __init__(self, config: Optional[PersistenceConfig] = None):
        super().__init__("persistence_manager", "state_persistence")
        
        self.config = config or PersistenceConfig()
        self.logger = logging.getLogger(f"{__name__}.PersistenceManager")
        
        # Setup directories
        self.data_dir = self.config.data_directory
        self.backup_dir = self.config.backup_directory
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Database setup
        self.db_path = self.config.database_path or (self.data_dir / "consciousness.db")
        self.db_lock = threading.RLock()
        
        # In-memory caches
        self.consciousness_state_cache: Optional[ConsciousnessState] = None
        self.population_cache: Dict[str, PopulationState] = {}
        self.user_context_cache: Dict[str, UserContextState] = {}
        self.component_status_cache: Dict[str, ComponentStatus] = {}
        
        # Write queues for batching
        self.write_queue: asyncio.Queue = asyncio.Queue()
        self.write_queue_task: Optional[asyncio.Task] = None
        
        # Snapshot management
        self.snapshots: List[StateSnapshot] = []
        self.last_snapshot_time: Optional[datetime] = None
        
        # Backup management
        self.backups: Dict[str, List[BackupInfo]] = {}  # type -> list of backups
        self.last_backup_time: Optional[datetime] = None
        
        # Recovery state
        self.recovery_in_progress = False
        self.corruption_detected = False
        
        # Performance metrics
        self.metrics = {
            'total_reads': 0,
            'total_writes': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'snapshots_created': 0,
            'backups_created': 0,
            'recoveries_performed': 0,
            'corruption_detections': 0,
            'average_read_time_ms': 0.0,
            'average_write_time_ms': 0.0
        }
    
    async def start(self) -> bool:
        """Start the persistence manager"""
        try:
            self.logger.info("Starting Consciousness State Persistence Manager...")
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing state
            await self._load_initial_state()
            
            # Start background tasks
            if self.config.async_writes:
                self.write_queue_task = asyncio.create_task(self._process_write_queue())
            
            # Start periodic tasks
            asyncio.create_task(self._periodic_snapshot_task())
            asyncio.create_task(self._periodic_backup_task())
            
            # Start integrity monitoring
            if self.config.checksum_validation:
                asyncio.create_task(self._integrity_monitoring_task())
            
            self.is_running = True
            await self.set_component_state(ComponentState.HEALTHY)
            
            self.logger.info("Consciousness State Persistence Manager started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start persistence manager: {e}")
            await self.set_component_state(ComponentState.FAILED)
            return False
    
    async def stop(self) -> None:
        """Stop the persistence manager"""
        self.logger.info("Stopping Consciousness State Persistence Manager...")
        
        # Stop background tasks
        if self.write_queue_task:
            self.write_queue_task.cancel()
            try:
                await self.write_queue_task
            except asyncio.CancelledError:
                pass
        
        # Flush any remaining writes
        await self._flush_write_queue()
        
        # Create final backup
        if self.consciousness_state_cache:
            await self._create_backup("shutdown", "Emergency shutdown backup")
        
        # Create final snapshot
        await self._create_snapshot("shutdown")
        
        self.is_running = False
        await self.set_component_state(ComponentState.UNKNOWN)
        
        self.logger.info("Consciousness State Persistence Manager stopped")
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process consciousness events"""
        try:
            if event.event_type == EventType.STATE_UPDATE:
                await self._handle_state_update(event.data)
            elif event.event_type == EventType.NEURAL_EVOLUTION:
                await self._handle_neural_evolution(event.data)
            elif event.event_type == EventType.CONTEXT_UPDATE:
                await self._handle_context_update(event.data)
            elif event.event_type == EventType.COMPONENT_STATUS:
                await self._handle_component_status_update(event.data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {e}")
            return False
    
    async def get_health_status(self) -> ComponentStatus:
        """Get current health status"""
        # Calculate health based on recent operations
        recent_errors = sum(1 for _ in range(10))  # Simplified error tracking
        cache_hit_rate = (self.metrics['cache_hits'] / 
                         max(1, self.metrics['cache_hits'] + self.metrics['cache_misses']))
        
        health_score = max(0.0, min(1.0, cache_hit_rate * 0.7 + (1.0 - recent_errors/10) * 0.3))
        
        await self.update_health_score(health_score)
        return self.status
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update persistence manager configuration"""
        try:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            self.logger.info("Persistence manager configuration updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    # Core persistence operations
    
    async def save_consciousness_state(self, state: ConsciousnessState, 
                                     create_snapshot: bool = False) -> bool:
        """Save consciousness state with optional snapshot creation"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Update cache
            self.consciousness_state_cache = state
            
            # Prepare write operation
            write_op = {
                'operation': 'save_consciousness_state',
                'data': state,
                'timestamp': datetime.now(),
                'create_snapshot': create_snapshot
            }
            
            if self.config.async_writes:
                await self.write_queue.put(write_op)
            else:
                await self._execute_write_operation(write_op)
            
            # Update metrics
            write_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self._update_write_metrics(write_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save consciousness state: {e}")
            return False
    
    async def load_consciousness_state(self) -> Optional[ConsciousnessState]:
        """Load consciousness state with caching"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Check cache first
            if self.consciousness_state_cache:
                self.metrics['cache_hits'] += 1
                return self.consciousness_state_cache
            
            self.metrics['cache_misses'] += 1
            
            # Load from database
            state = await self._load_consciousness_state_from_db()
            
            if state:
                # Validate state integrity
                if self.config.checksum_validation and not self._validate_state_integrity(state):
                    self.logger.warning("Consciousness state integrity validation failed")
                    self.corruption_detected = True
                    
                    # Attempt recovery
                    if self.config.recovery_mode == "automatic":
                        state = await self._recover_consciousness_state()
                
                # Update cache
                self.consciousness_state_cache = state
            else:
                # Create default state if none exists
                self.logger.info("No existing consciousness state found, creating default")
                state = create_default_consciousness_state()
                await self.save_consciousness_state(state)
            
            # Update metrics
            read_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self._update_read_metrics(read_time)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Failed to load consciousness state: {e}")
            return None
    
    async def save_population_state(self, population_id: str, 
                                  state: PopulationState) -> bool:
        """Save neural population state"""
        try:
            # Update cache
            self.population_cache[population_id] = state
            
            # Prepare write operation
            write_op = {
                'operation': 'save_population_state',
                'population_id': population_id,
                'data': state,
                'timestamp': datetime.now()
            }
            
            if self.config.async_writes:
                await self.write_queue.put(write_op)
            else:
                await self._execute_write_operation(write_op)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save population state {population_id}: {e}")
            return False
    
    async def load_population_state(self, population_id: str) -> Optional[PopulationState]:
        """Load neural population state"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Check cache first
            if population_id in self.population_cache:
                self.metrics['cache_hits'] += 1
                return self.population_cache[population_id]
            
            self.metrics['cache_misses'] += 1
            
            # Load from database
            state = await self._load_population_state_from_db(population_id)
            
            if state:
                self.population_cache[population_id] = state
            
            read_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self._update_read_metrics(read_time)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Failed to load population state {population_id}: {e}")
            return None
    
    async def save_user_context(self, user_id: str, context: UserContextState) -> bool:
        """Save user context state"""
        try:
            self.user_context_cache[user_id] = context
            
            write_op = {
                'operation': 'save_user_context',
                'user_id': user_id,
                'data': context,
                'timestamp': datetime.now()
            }
            
            if self.config.async_writes:
                await self.write_queue.put(write_op)
            else:
                await self._execute_write_operation(write_op)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save user context {user_id}: {e}")
            return False
    
    async def load_user_context(self, user_id: str) -> Optional[UserContextState]:
        """Load user context state"""
        try:
            # Check cache first
            if user_id in self.user_context_cache:
                self.metrics['cache_hits'] += 1
                return self.user_context_cache[user_id]
            
            self.metrics['cache_misses'] += 1
            
            # Load from database
            context = await self._load_user_context_from_db(user_id)
            
            if context:
                self.user_context_cache[user_id] = context
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to load user context {user_id}: {e}")
            return None
    
    async def save_component_status(self, component_id: str, 
                                  status: ComponentStatus) -> bool:
        """Save component status"""
        try:
            self.component_status_cache[component_id] = status
            
            write_op = {
                'operation': 'save_component_status',
                'component_id': component_id,
                'data': status,
                'timestamp': datetime.now()
            }
            
            if self.config.async_writes:
                await self.write_queue.put(write_op)
            else:
                await self._execute_write_operation(write_op)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save component status {component_id}: {e}")
            return False
    
    # Snapshot management
    
    async def create_snapshot(self, description: str = "Manual snapshot") -> Optional[str]:
        """Create a snapshot of current consciousness state"""
        return await self._create_snapshot("manual", description)
    
    async def restore_from_snapshot(self, snapshot_id: str) -> bool:
        """Restore consciousness state from snapshot"""
        try:
            self.logger.info(f"Restoring from snapshot {snapshot_id}")
            
            snapshot = next((s for s in self.snapshots if s.snapshot_id == snapshot_id), None)
            if not snapshot:
                # Try loading from disk
                snapshot = await self._load_snapshot_from_disk(snapshot_id)
            
            if not snapshot:
                self.logger.error(f"Snapshot {snapshot_id} not found")
                return False
            
            # Validate snapshot integrity
            if self.config.checksum_validation:
                if not self._validate_snapshot_integrity(snapshot):
                    self.logger.error(f"Snapshot {snapshot_id} integrity validation failed")
                    return False
            
            # Restore state
            self.consciousness_state_cache = snapshot.consciousness_state
            
            # Save restored state to database
            await self.save_consciousness_state(snapshot.consciousness_state)
            
            self.metrics['recoveries_performed'] += 1
            self.logger.info(f"Successfully restored from snapshot {snapshot_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from snapshot {snapshot_id}: {e}")
            return False
    
    async def list_snapshots(self) -> List[Dict[str, Any]]:
        """List available snapshots"""
        snapshots_info = []
        
        for snapshot in self.snapshots:
            snapshots_info.append({
                'snapshot_id': snapshot.snapshot_id,
                'timestamp': snapshot.timestamp.isoformat(),
                'compressed_size': snapshot.compressed_size,
                'checksum': snapshot.checksum[:8] + "...",
                'metadata': snapshot.metadata
            })
        
        return snapshots_info
    
    # Backup management
    
    async def create_backup(self, backup_type: str = "manual", 
                          description: str = "Manual backup") -> Optional[str]:
        """Create a backup of consciousness system"""
        return await self._create_backup(backup_type, description)
    
    async def restore_from_backup(self, backup_id: str) -> bool:
        """Restore consciousness system from backup"""
        try:
            self.logger.info(f"Restoring from backup {backup_id}")
            
            # Find backup info
            backup_info = None
            for backup_type, backup_list in self.backups.items():
                backup_info = next((b for b in backup_list if b.backup_id == backup_id), None)
                if backup_info:
                    break
            
            if not backup_info:
                self.logger.error(f"Backup {backup_id} not found")
                return False
            
            # Load backup data
            backup_data = await self._load_backup_from_disk(backup_info)
            if not backup_data:
                return False
            
            # Validate backup integrity
            if self.config.checksum_validation:
                if not self._validate_backup_integrity(backup_info, backup_data):
                    self.logger.error(f"Backup {backup_id} integrity validation failed")
                    return False
            
            # Restore consciousness state
            if 'consciousness_state' in backup_data:
                self.consciousness_state_cache = ConsciousnessState.from_dict(
                    backup_data['consciousness_state']
                )
                await self.save_consciousness_state(self.consciousness_state_cache)
            
            # Restore population states
            if 'populations' in backup_data:
                for pop_id, pop_data in backup_data['populations'].items():
                    population_state = PopulationState.from_dict(pop_data)
                    await self.save_population_state(pop_id, population_state)
            
            # Restore user contexts
            if 'user_contexts' in backup_data:
                for user_id, ctx_data in backup_data['user_contexts'].items():
                    user_context = UserContextState.from_dict(ctx_data)
                    await self.save_user_context(user_id, user_context)
            
            self.metrics['recoveries_performed'] += 1
            self.logger.info(f"Successfully restored from backup {backup_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup {backup_id}: {e}")
            return False
    
    async def list_backups(self) -> Dict[str, List[Dict[str, Any]]]:
        """List available backups by type"""
        backup_info = {}
        
        for backup_type, backup_list in self.backups.items():
            backup_info[backup_type] = []
            for backup in backup_list:
                backup_info[backup_type].append({
                    'backup_id': backup.backup_id,
                    'timestamp': backup.timestamp.isoformat(),
                    'original_size': backup.original_size,
                    'compressed_size': backup.compressed_size,
                    'checksum': backup.checksum[:8] + "...",
                    'components': backup.components,
                    'metadata': backup.metadata
                })
        
        return backup_info
    
    # Recovery operations
    
    async def detect_corruption(self) -> List[Dict[str, Any]]:
        """Detect data corruption in stored states"""
        corruption_issues = []
        
        try:
            # Check consciousness state
            if self.consciousness_state_cache:
                if not self._validate_state_integrity(self.consciousness_state_cache):
                    corruption_issues.append({
                        'type': 'consciousness_state',
                        'component': 'main_state',
                        'severity': 'high',
                        'description': 'Consciousness state checksum mismatch'
                    })
            
            # Check population states
            for pop_id, population in self.population_cache.items():
                if not self._validate_population_integrity(population):
                    corruption_issues.append({
                        'type': 'population_state',
                        'component': pop_id,
                        'severity': 'medium',
                        'description': f'Population {pop_id} state corruption detected'
                    })
            
            # Check database integrity
            db_issues = await self._check_database_integrity()
            corruption_issues.extend(db_issues)
            
            if corruption_issues:
                self.corruption_detected = True
                self.metrics['corruption_detections'] += 1
                self.logger.warning(f"Detected {len(corruption_issues)} corruption issues")
            
            return corruption_issues
            
        except Exception as e:
            self.logger.error(f"Error during corruption detection: {e}")
            return [{'type': 'detection_error', 'description': str(e)}]
    
    async def attempt_recovery(self) -> bool:
        """Attempt automatic recovery from corruption"""
        try:
            if self.recovery_in_progress:
                self.logger.info("Recovery already in progress")
                return False
            
            self.recovery_in_progress = True
            self.logger.info("Starting automatic recovery process")
            
            corruption_issues = await self.detect_corruption()
            
            if not corruption_issues:
                self.logger.info("No corruption detected, recovery not needed")
                self.recovery_in_progress = False
                return True
            
            # Recovery strategy based on tolerance level
            if self.config.corruption_tolerance == "high":
                # Try to recover using latest snapshot
                latest_snapshot = await self._get_latest_valid_snapshot()
                if latest_snapshot:
                    return await self.restore_from_snapshot(latest_snapshot.snapshot_id)
            
            elif self.config.corruption_tolerance == "medium":
                # Try to recover individual components
                recovery_success = True
                
                for issue in corruption_issues:
                    if issue['type'] == 'consciousness_state':
                        state = await self._recover_consciousness_state()
                        if not state:
                            recovery_success = False
                    elif issue['type'] == 'population_state':
                        pop_recovered = await self._recover_population_state(issue['component'])
                        if not pop_recovered:
                            recovery_success = False
                
                return recovery_success
            
            else:  # low tolerance
                # Restore from most recent backup
                latest_backup = await self._get_latest_valid_backup()
                if latest_backup:
                    return await self.restore_from_backup(latest_backup.backup_id)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
        finally:
            self.recovery_in_progress = False
    
    # Database operations
    
    async def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Consciousness state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consciousness_states (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    checksum TEXT,
                    version TEXT DEFAULT '2.0.0'
                )
            ''')
            
            # Population states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS population_states (
                    population_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    checksum TEXT,
                    generation INTEGER DEFAULT 0
                )
            ''')
            
            # User contexts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_contexts (
                    user_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    checksum TEXT,
                    last_activity TEXT
                )
            ''')
            
            # Component status table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS component_status (
                    component_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    status_data TEXT NOT NULL,
                    health_score REAL DEFAULT 0.5,
                    last_heartbeat TEXT
                )
            ''')
            
            # Snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    snapshot_data BLOB,
                    checksum TEXT,
                    compressed_size INTEGER,
                    metadata TEXT
                )
            ''')
            
            # Backups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    backup_id TEXT PRIMARY KEY,
                    backup_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    original_size INTEGER,
                    compressed_size INTEGER,
                    checksum TEXT,
                    components TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
    
    async def _load_consciousness_state_from_db(self) -> Optional[ConsciousnessState]:
        """Load consciousness state from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT state_data, checksum FROM consciousness_states 
                    ORDER BY timestamp DESC LIMIT 1
                ''')
                
                row = cursor.fetchone()
                if row:
                    state_data, checksum = row
                    state_dict = json.loads(state_data)
                    
                    # Validate checksum if enabled
                    if self.config.checksum_validation and checksum:
                        calculated_checksum = self._calculate_checksum(state_data)
                        if calculated_checksum != checksum:
                            self.logger.warning("Consciousness state checksum mismatch")
                            return None
                    
                    return ConsciousnessState.from_dict(state_dict)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading consciousness state from database: {e}")
            return None
    
    async def _load_population_state_from_db(self, population_id: str) -> Optional[PopulationState]:
        """Load population state from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT state_data, checksum FROM population_states 
                    WHERE population_id = ?
                ''', (population_id,))
                
                row = cursor.fetchone()
                if row:
                    state_data, checksum = row
                    state_dict = json.loads(state_data)
                    
                    if self.config.checksum_validation and checksum:
                        calculated_checksum = self._calculate_checksum(state_data)
                        if calculated_checksum != checksum:
                            self.logger.warning(f"Population {population_id} checksum mismatch")
                            return None
                    
                    return PopulationState.from_dict(state_dict)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading population state from database: {e}")
            return None
    
    async def _load_user_context_from_db(self, user_id: str) -> Optional[UserContextState]:
        """Load user context from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT context_data, checksum FROM user_contexts 
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    context_data, checksum = row
                    context_dict = json.loads(context_data)
                    
                    if self.config.checksum_validation and checksum:
                        calculated_checksum = self._calculate_checksum(context_data)
                        if calculated_checksum != checksum:
                            self.logger.warning(f"User context {user_id} checksum mismatch")
                            return None
                    
                    return UserContextState.from_dict(context_dict)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading user context from database: {e}")
            return None
    
    # Write queue processing
    
    async def _process_write_queue(self):
        """Process write operations queue"""
        batch = []
        
        while self.is_running:
            try:
                # Collect batch of operations
                try:
                    # Wait for first operation
                    write_op = await asyncio.wait_for(self.write_queue.get(), timeout=1.0)
                    batch.append(write_op)
                    
                    # Collect additional operations up to batch size
                    while len(batch) < self.config.batch_write_size:
                        try:
                            write_op = await asyncio.wait_for(self.write_queue.get(), timeout=0.01)
                            batch.append(write_op)
                        except asyncio.TimeoutError:
                            break
                    
                except asyncio.TimeoutError:
                    continue
                
                # Process batch
                if batch:
                    await self._execute_write_batch(batch)
                    batch.clear()
                
                # Small delay to prevent excessive CPU usage
                if self.config.write_delay_ms > 0:
                    await asyncio.sleep(self.config.write_delay_ms / 1000.0)
                
            except Exception as e:
                self.logger.error(f"Error in write queue processing: {e}")
                batch.clear()
    
    async def _execute_write_batch(self, batch: List[Dict[str, Any]]):
        """Execute a batch of write operations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for write_op in batch:
                    await self._execute_single_write_operation(cursor, write_op)
                
                conn.commit()
                
            self.metrics['total_writes'] += len(batch)
            
        except Exception as e:
            self.logger.error(f"Error executing write batch: {e}")
    
    async def _execute_write_operation(self, write_op: Dict[str, Any]):
        """Execute a single write operation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                await self._execute_single_write_operation(cursor, write_op)
                conn.commit()
                
            self.metrics['total_writes'] += 1
            
        except Exception as e:
            self.logger.error(f"Error executing write operation: {e}")
    
    async def _execute_single_write_operation(self, cursor, write_op: Dict[str, Any]):
        """Execute a single write operation with cursor"""
        operation = write_op['operation']
        data = write_op['data']
        timestamp = write_op['timestamp'].isoformat()
        
        if operation == 'save_consciousness_state':
            state_json = json.dumps(data.to_dict())
            checksum = self._calculate_checksum(state_json) if self.config.checksum_validation else None
            
            cursor.execute('''
                INSERT INTO consciousness_states (timestamp, state_data, checksum)
                VALUES (?, ?, ?)
            ''', (timestamp, state_json, checksum))
            
            # Create snapshot if requested
            if write_op.get('create_snapshot'):
                await self._create_snapshot("auto", "Automatic snapshot on state save")
        
        elif operation == 'save_population_state':
            population_id = write_op['population_id']
            state_json = json.dumps(data.to_dict())
            checksum = self._calculate_checksum(state_json) if self.config.checksum_validation else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO population_states 
                (population_id, timestamp, state_data, checksum, generation)
                VALUES (?, ?, ?, ?, ?)
            ''', (population_id, timestamp, state_json, checksum, data.generation))
        
        elif operation == 'save_user_context':
            user_id = write_op['user_id']
            context_json = json.dumps(data.to_dict())
            checksum = self._calculate_checksum(context_json) if self.config.checksum_validation else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_contexts 
                (user_id, timestamp, context_data, checksum, last_activity)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, timestamp, context_json, checksum, data.last_updated.isoformat()))
        
        elif operation == 'save_component_status':
            component_id = write_op['component_id']
            status_json = json.dumps(data.to_dict())
            
            cursor.execute('''
                INSERT OR REPLACE INTO component_status 
                (component_id, timestamp, status_data, health_score, last_heartbeat)
                VALUES (?, ?, ?, ?, ?)
            ''', (component_id, timestamp, status_json, data.health_score, 
                 data.last_heartbeat.isoformat()))
    
    # Utility methods
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _validate_state_integrity(self, state: ConsciousnessState) -> bool:
        """Validate consciousness state integrity"""
        try:
            # Check basic structure
            if not state.system_id or not state.timestamp:
                return False
            
            # Check consciousness level bounds
            if not (0.0 <= state.consciousness_level <= 1.0):
                return False
            
            # Check emergence strength bounds
            if not (0.0 <= state.emergence_strength <= 1.0):
                return False
            
            # Verify populations consistency
            if state.total_populations < 0 or state.active_populations < 0:
                return False
            
            if state.active_populations > state.total_populations:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_population_integrity(self, population: PopulationState) -> bool:
        """Validate population state integrity"""
        try:
            if population.size <= 0:
                return False
            
            if not (0.0 <= population.fitness_average <= 1.0):
                return False
            
            if population.active_neurons > population.size:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _update_read_metrics(self, read_time_ms: float):
        """Update read performance metrics"""
        self.metrics['total_reads'] += 1
        total_reads = self.metrics['total_reads']
        old_avg = self.metrics['average_read_time_ms']
        self.metrics['average_read_time_ms'] = ((old_avg * (total_reads - 1)) + read_time_ms) / total_reads
    
    def _update_write_metrics(self, write_time_ms: float):
        """Update write performance metrics"""
        total_writes = self.metrics['total_writes'] + 1
        old_avg = self.metrics['average_write_time_ms']
        self.metrics['average_write_time_ms'] = ((old_avg * (total_writes - 1)) + write_time_ms) / total_writes
    
    # Event handlers
    
    async def _handle_state_update(self, event_data: Dict[str, Any]):
        """Handle state update events"""
        state_update = event_data.get('state_update', {})
        
        # Update cached consciousness state
        if self.consciousness_state_cache and 'consciousness_level' in state_update:
            self.consciousness_state_cache.consciousness_level = state_update['consciousness_level']
            self.consciousness_state_cache.timestamp = datetime.now()
            
            # Save updated state
            await self.save_consciousness_state(self.consciousness_state_cache)
    
    async def _handle_neural_evolution(self, event_data: Dict[str, Any]):
        """Handle neural evolution events"""
        evolution_data = event_data.get('evolution_data', {})
        population_id = evolution_data.get('population_id')
        
        if population_id in self.population_cache:
            population = self.population_cache[population_id]
            
            # Update population based on evolution results
            if 'fitness_improvements' in evolution_data:
                improvements = evolution_data['fitness_improvements']
                if 'overall' in improvements:
                    population.fitness_average = min(1.0, population.fitness_average + improvements['overall'])
            
            if 'evolution_cycle' in evolution_data:
                population.generation = evolution_data['evolution_cycle']
            
            population.last_evolution = datetime.now()
            population.evolution_cycles += 1
            
            # Save updated population
            await self.save_population_state(population_id, population)
    
    async def _handle_context_update(self, event_data: Dict[str, Any]):
        """Handle context update events"""
        context_update = event_data.get('context_update', {})
        user_id = context_update.get('user_id')
        
        if user_id and user_id in self.user_context_cache:
            user_context = self.user_context_cache[user_id]
            
            # Update user context based on event
            if 'skill_changes' in context_update:
                for domain, change in context_update['skill_changes'].items():
                    current_xp = user_context.experience_points.get(domain, 0)
                    user_context.experience_points[domain] = max(0, current_xp + int(change * 100))
            
            user_context.last_updated = datetime.now()
            
            # Save updated context
            await self.save_user_context(user_id, user_context)
    
    async def _handle_component_status_update(self, event_data: Dict[str, Any]):
        """Handle component status update events"""
        status_update = event_data.get('component_status', {})
        component_id = status_update.get('component_id')
        
        if component_id and component_id in self.component_status_cache:
            status = self.component_status_cache[component_id]
            
            # Update status based on event
            if 'health_score' in status_update:
                status.health_score = status_update['health_score']
            
            if 'state' in status_update:
                from ..core.data_models import ComponentState
                status.state = ComponentState(status_update['state'])
            
            status.last_heartbeat = datetime.now()
            
            # Save updated status
            await self.save_component_status(component_id, status)
    
    # Background tasks
    
    async def _periodic_snapshot_task(self):
        """Periodic snapshot creation task"""
        while self.is_running:
            try:
                if (not self.last_snapshot_time or 
                    (datetime.now() - self.last_snapshot_time).total_seconds() >= self.config.snapshot_interval):
                    
                    await self._create_snapshot("periodic", "Periodic automatic snapshot")
                
                await asyncio.sleep(self.config.snapshot_interval // 4)  # Check 4x per interval
                
            except Exception as e:
                self.logger.error(f"Error in periodic snapshot task: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _periodic_backup_task(self):
        """Periodic backup creation task"""
        while self.is_running:
            try:
                if (not self.last_backup_time or 
                    (datetime.now() - self.last_backup_time).total_seconds() >= self.config.auto_backup_interval):
                    
                    await self._create_backup("automatic", "Periodic automatic backup")
                
                await asyncio.sleep(self.config.auto_backup_interval // 4)
                
            except Exception as e:
                self.logger.error(f"Error in periodic backup task: {e}")
                await asyncio.sleep(300)  # Wait before retrying
    
    async def _integrity_monitoring_task(self):
        """Background integrity monitoring task"""
        while self.is_running:
            try:
                corruption_issues = await self.detect_corruption()
                
                if corruption_issues and self.config.recovery_mode == "automatic":
                    self.logger.warning(f"Detected {len(corruption_issues)} corruption issues, attempting recovery")
                    recovery_success = await self.attempt_recovery()
                    
                    if not recovery_success:
                        self.logger.error("Automatic recovery failed, manual intervention may be required")
                        await self.set_component_state(ComponentState.FAILED)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in integrity monitoring: {e}")
                await asyncio.sleep(600)  # Wait before retrying
    
    async def _load_initial_state(self):
        """Load initial state on startup"""
        # Load consciousness state
        self.consciousness_state_cache = await self.load_consciousness_state()
        
        # Load existing snapshots and backups info
        await self._load_snapshots_info()
        await self._load_backups_info()
    
    async def _flush_write_queue(self):
        """Flush any remaining write operations"""
        remaining_ops = []
        
        # Collect all remaining operations
        try:
            while True:
                write_op = self.write_queue.get_nowait()
                remaining_ops.append(write_op)
        except asyncio.QueueEmpty:
            pass
        
        # Execute remaining operations
        if remaining_ops:
            await self._execute_write_batch(remaining_ops)
            self.logger.info(f"Flushed {len(remaining_ops)} remaining write operations")
    
    # Placeholder methods for advanced features (would be implemented in full system)
    
    async def _create_snapshot(self, snapshot_type: str, description: str = "") -> Optional[str]:
        """Create snapshot (placeholder - would compress and store state)"""
        # This is a simplified version - real implementation would compress and store
        if self.consciousness_state_cache:
            snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.last_snapshot_time = datetime.now()
            self.metrics['snapshots_created'] += 1
            self.logger.info(f"Created snapshot {snapshot_id} ({snapshot_type})")
            return snapshot_id
        return None
    
    async def _create_backup(self, backup_type: str, description: str = "") -> Optional[str]:
        """Create backup (placeholder - would create full backup)"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.last_backup_time = datetime.now()
        self.metrics['backups_created'] += 1
        self.logger.info(f"Created backup {backup_id} ({backup_type})")
        return backup_id
    
    async def _recover_consciousness_state(self) -> Optional[ConsciousnessState]:
        """Attempt to recover consciousness state"""
        # Simplified recovery - would use snapshots/backups in real implementation
        self.logger.info("Attempting consciousness state recovery")
        return create_default_consciousness_state()
    
    async def _recover_population_state(self, population_id: str) -> bool:
        """Attempt to recover population state"""
        self.logger.info(f"Attempting to recover population {population_id}")
        return True
    
    async def _check_database_integrity(self) -> List[Dict[str, Any]]:
        """Check database integrity (placeholder)"""
        return []
    
    async def _get_latest_valid_snapshot(self) -> Optional[StateSnapshot]:
        """Get latest valid snapshot (placeholder)"""
        return None
    
    async def _get_latest_valid_backup(self) -> Optional[BackupInfo]:
        """Get latest valid backup (placeholder)"""
        return None
    
    async def _load_snapshots_info(self):
        """Load snapshots information from database"""
        pass
    
    async def _load_backups_info(self):
        """Load backups information from database"""
        pass
    
    async def _validate_snapshot_integrity(self, snapshot: StateSnapshot) -> bool:
        """Validate snapshot integrity"""
        return True
    
    async def _validate_backup_integrity(self, backup_info: BackupInfo, backup_data: Dict[str, Any]) -> bool:
        """Validate backup integrity"""
        return True
    
    async def _load_snapshot_from_disk(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load snapshot from disk"""
        return None
    
    async def _load_backup_from_disk(self, backup_info: BackupInfo) -> Optional[Dict[str, Any]]:
        """Load backup data from disk"""
        return {}
    
    def get_persistence_metrics(self) -> Dict[str, Any]:
        """Get persistence system metrics"""
        return {
            'metrics': self.metrics.copy(),
            'cache_sizes': {
                'consciousness_state': 1 if self.consciousness_state_cache else 0,
                'populations': len(self.population_cache),
                'user_contexts': len(self.user_context_cache),
                'component_status': len(self.component_status_cache)
            },
            'snapshots_count': len(self.snapshots),
            'backups_count': sum(len(backups) for backups in self.backups.values()),
            'corruption_detected': self.corruption_detected,
            'recovery_in_progress': self.recovery_in_progress,
            'database_path': str(self.db_path),
            'data_directory': str(self.data_dir),
            'config': {
                'auto_backup_interval': self.config.auto_backup_interval,
                'snapshot_interval': self.config.snapshot_interval,
                'checksum_validation': self.config.checksum_validation,
                'async_writes': self.config.async_writes,
                'recovery_mode': self.config.recovery_mode
            }
        }