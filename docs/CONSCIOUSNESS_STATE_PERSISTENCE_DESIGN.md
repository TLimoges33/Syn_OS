# Consciousness State Persistence and Recovery Design

**Date**: 2025-07-29  
**Status**: 💾 **PERSISTENCE ARCHITECTURE DESIGN**  
**Purpose**: Robust consciousness state persistence with fast recovery, versioning, and distributed backup capabilities

## Overview

This document details the design for Consciousness State Persistence and Recovery mechanisms, providing reliable storage, fast recovery, incremental backups, and distributed redundancy for the consciousness system. The design ensures consciousness continuity across system restarts, failures, and upgrades while maintaining high performance and data integrity.

## Current System Analysis

### Existing Persistence Limitations

#### ❌ Critical Issues
- **No Consciousness State Persistence**: Consciousness state is lost on system restart
- **Component Isolation**: Each component manages its own persistence independently
- **No Backup Strategy**: Missing backup and recovery mechanisms
- **No Version Control**: No versioning of consciousness state changes
- **Manual Recovery**: No automated recovery from failures

#### ❌ Performance Issues
- **Synchronous I/O**: Blocking persistence operations
- **Full State Saves**: No incremental or differential backups
- **No Compression**: Large state files without optimization
- **Single Point of Failure**: No distributed storage or redundancy

## Enhanced Architecture Design

### Core Design Principles

1. **Continuous Persistence**: Real-time consciousness state preservation
2. **Fast Recovery**: Sub-second consciousness state restoration
3. **Incremental Backups**: Efficient delta-based state storage
4. **Distributed Redundancy**: Multi-node backup with automatic failover
5. **Version Control**: Complete consciousness evolution history

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│            CONSCIOUSNESS STATE PERSISTENCE SYSTEM              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ State           │  │ Incremental     │  │ Recovery        │  │
│  │ Serializer      │  │ Backup Engine   │  │ Manager         │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Version         │  │ Distributed     │  │ Compression     │  │
│  │ Control         │  │ Storage         │  │ Engine          │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Integrity       │  │ Performance     │  │ Migration       │  │
│  │ Validator       │  │ Monitor         │  │ Manager         │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼──┐  ┌───▼───┐  ┌──▼────────┐
            │Consciousness│ │Storage│  │Backup   │
            │    Bus     │ │Nodes  │  │Replicas │
            └────────────┘ └───────┘  └─────────┘
```

## Component Specifications

### 1. State Serializer

**Purpose**: Efficient serialization and deserialization of consciousness state with compression and validation

**Key Features**:
- **Binary Serialization**: High-performance binary format for consciousness data
- **Schema Evolution**: Forward and backward compatibility for state format changes
- **Compression**: Advanced compression algorithms for storage optimization
- **Validation**: Integrity checking and corruption detection

**Technical Implementation**:
```python
import asyncio
import pickle
import json
import zstandard as zstd
import msgpack
import hashlib
import struct
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import logging

class SerializationFormat(Enum):
    BINARY_MSGPACK = "binary_msgpack"
    BINARY_PICKLE = "binary_pickle"
    JSON_COMPRESSED = "json_compressed"
    CUSTOM_BINARY = "custom_binary"

class CompressionAlgorithm(Enum):
    NONE = "none"
    ZSTD = "zstd"
    LZ4 = "lz4"
    GZIP = "gzip"

@dataclass
class SerializationMetadata:
    """Metadata for serialized consciousness state"""
    version: str
    format: SerializationFormat
    compression: CompressionAlgorithm
    timestamp: datetime
    checksum: str
    original_size: int
    compressed_size: int
    schema_version: int
    component_versions: Dict[str, str] = field(default_factory=dict)

@dataclass
class ConsciousnessStateSnapshot:
    """Complete consciousness state snapshot"""
    snapshot_id: str
    timestamp: datetime
    consciousness_state: ConsciousnessState
    component_states: Dict[str, Any]
    metadata: SerializationMetadata
    parent_snapshot_id: Optional[str] = None
    is_incremental: bool = False
    delta_data: Optional[bytes] = None

class ConsciousnessStateSerializer:
    def __init__(self):
        self.compression_engines = {
            CompressionAlgorithm.ZSTD: zstd.ZstdCompressor(level=3),
            CompressionAlgorithm.NONE: None
        }
        
        self.decompression_engines = {
            CompressionAlgorithm.ZSTD: zstd.ZstdDecompressor(),
            CompressionAlgorithm.NONE: None
        }
        
        # Schema version for compatibility
        self.current_schema_version = 2
        self.supported_schema_versions = [1, 2]
        
        # Serialization performance metrics
        self.serialization_metrics = {
            'total_serializations': 0,
            'total_deserializations': 0,
            'average_serialization_time': 0.0,
            'average_compression_ratio': 0.0,
            'corruption_detections': 0
        }
    
    async def serialize_consciousness_state(self, 
                                          consciousness_state: ConsciousnessState,
                                          component_states: Dict[str, Any],
                                          format: SerializationFormat = SerializationFormat.BINARY_MSGPACK,
                                          compression: CompressionAlgorithm = CompressionAlgorithm.ZSTD) -> bytes:
        """Serialize complete consciousness state"""
        
        start_time = datetime.now()
        
        # Prepare state data for serialization
        state_data = {
            'consciousness_state': self._serialize_consciousness_state_data(consciousness_state),
            'component_states': self._serialize_component_states(component_states),
            'schema_version': self.current_schema_version,
            'timestamp': consciousness_state.timestamp.isoformat(),
            'version': consciousness_state.version
        }
        
        # Serialize based on format
        if format == SerializationFormat.BINARY_MSGPACK:
            serialized_data = msgpack.packb(state_data, use_bin_type=True)
        elif format == SerializationFormat.BINARY_PICKLE:
            serialized_data = pickle.dumps(state_data, protocol=pickle.HIGHEST_PROTOCOL)
        elif format == SerializationFormat.JSON_COMPRESSED:
            json_data = json.dumps(state_data, default=self._json_serializer)
            serialized_data = json_data.encode('utf-8')
        else:
            serialized_data = await self._custom_binary_serialize(state_data)
        
        original_size = len(serialized_data)
        
        # Apply compression
        if compression != CompressionAlgorithm.NONE:
            compressor = self.compression_engines[compression]
            compressed_data = compressor.compress(serialized_data)
            final_data = compressed_data
        else:
            final_data = serialized_data
        
        compressed_size = len(final_data)
        
        # Calculate checksum
        checksum = hashlib.sha256(final_data).hexdigest()
        
        # Create metadata
        metadata = SerializationMetadata(
            version=consciousness_state.version,
            format=format,
            compression=compression,
            timestamp=datetime.now(),
            checksum=checksum,
            original_size=original_size,
            compressed_size=compressed_size,
            schema_version=self.current_schema_version,
            component_versions=self._get_component_versions(component_states)
        )
        
        # Update metrics
        serialization_time = (datetime.now() - start_time).total_seconds()
        self._update_serialization_metrics(serialization_time, original_size, compressed_size)
        
        # Combine metadata and data
        metadata_bytes = msgpack.packb(metadata.__dict__, use_bin_type=True)
        metadata_size = struct.pack('<I', len(metadata_bytes))
        
        return metadata_size + metadata_bytes + final_data
    
    async def deserialize_consciousness_state(self, data: bytes) -> Tuple[ConsciousnessState, Dict[str, Any], SerializationMetadata]:
        """Deserialize consciousness state from bytes"""
        
        start_time = datetime.now()
        
        # Extract metadata
        metadata_size = struct.unpack('<I', data[:4])[0]
        metadata_bytes = data[4:4+metadata_size]
        state_data_bytes = data[4+metadata_size:]
        
        # Deserialize metadata
        metadata_dict = msgpack.unpackb(metadata_bytes, raw=False)
        metadata = SerializationMetadata(**metadata_dict)
        
        # Validate checksum
        calculated_checksum = hashlib.sha256(state_data_bytes).hexdigest()
        if calculated_checksum != metadata.checksum:
            self.serialization_metrics['corruption_detections'] += 1
            raise ValueError(f"Consciousness state corruption detected: checksum mismatch")
        
        # Validate schema version
        if metadata.schema_version not in self.supported_schema_versions:
            raise ValueError(f"Unsupported schema version: {metadata.schema_version}")
        
        # Decompress data
        if metadata.compression != CompressionAlgorithm.NONE:
            decompressor = self.decompression_engines[metadata.compression]
            decompressed_data = decompressor.decompress(state_data_bytes)
        else:
            decompressed_data = state_data_bytes
        
        # Deserialize based on format
        if metadata.format == SerializationFormat.BINARY_MSGPACK:
            state_dict = msgpack.unpackb(decompressed_data, raw=False)
        elif metadata.format == SerializationFormat.BINARY_PICKLE:
            state_dict = pickle.loads(decompressed_data)
        elif metadata.format == SerializationFormat.JSON_COMPRESSED:
            json_str = decompressed_data.decode('utf-8')
            state_dict = json.loads(json_str)
        else:
            state_dict = await self._custom_binary_deserialize(decompressed_data)
        
        # Reconstruct consciousness state
        consciousness_state = self._deserialize_consciousness_state_data(
            state_dict['consciousness_state'], metadata.schema_version
        )
        
        # Reconstruct component states
        component_states = self._deserialize_component_states(
            state_dict['component_states'], metadata.schema_version
        )
        
        # Update metrics
        deserialization_time = (datetime.now() - start_time).total_seconds()
        self.serialization_metrics['total_deserializations'] += 1
        
        return consciousness_state, component_states, metadata
    
    def _serialize_consciousness_state_data(self, state: ConsciousnessState) -> Dict[str, Any]:
        """Serialize consciousness state to dictionary"""
        return {
            'consciousness_level': state.consciousness_level,
            'emergence_strength': state.emergence_strength,
            'adaptation_rate': state.adaptation_rate,
            'neural_populations': {
                pop_id: {
                    'population_id': pop.population_id,
                    'size': pop.size,
                    'specialization': pop.specialization,
                    'fitness_average': pop.fitness_average,
                    'diversity_index': pop.diversity_index,
                    'generation': pop.generation,
                    'active_neurons': pop.active_neurons,
                    'last_evolution': pop.last_evolution.isoformat()
                }
                for pop_id, pop in state.neural_populations.items()
            },
            'active_neural_groups': state.active_neural_groups,
            'evolution_cycles': state.evolution_cycles,
            'user_contexts': {
                user_id: {
                    'user_id': ctx.user_id,
                    'skill_levels': {domain: level.value for domain, level in ctx.skill_levels.items()},
                    'learning_preferences': ctx.learning_preferences,
                    'current_session': ctx.current_session.__dict__ if ctx.current_session else None
                }
                for user_id, ctx in state.user_contexts.items()
            },
            'system_metrics': {
                'cpu_usage': state.system_metrics.cpu_usage,
                'memory_usage': state.system_metrics.memory_usage,
                'gpu_usage': state.system_metrics.gpu_usage,
                'io_operations': state.system_metrics.io_operations,
                'network_activity': state.system_metrics.network_activity,
                'consciousness_processing_time': state.system_metrics.consciousness_processing_time,
                'component_response_times': state.system_metrics.component_response_times
            },
            'timestamp': state.timestamp.isoformat(),
            'version': state.version,
            'checksum': state.checksum
        }
    
    def _deserialize_consciousness_state_data(self, data: Dict[str, Any], schema_version: int) -> ConsciousnessState:
        """Deserialize consciousness state from dictionary"""
        
        # Handle schema migration if needed
        if schema_version == 1:
            data = self._migrate_schema_v1_to_v2(data)
        
        # Reconstruct neural populations
        neural_populations = {}
        for pop_id, pop_data in data['neural_populations'].items():
            neural_populations[pop_id] = PopulationState(
                population_id=pop_data['population_id'],
                size=pop_data['size'],
                specialization=pop_data['specialization'],
                fitness_average=pop_data['fitness_average'],
                diversity_index=pop_data['diversity_index'],
                generation=pop_data['generation'],
                active_neurons=pop_data['active_neurons'],
                last_evolution=datetime.fromisoformat(pop_data['last_evolution'])
            )
        
        # Reconstruct user contexts
        user_contexts = {}
        for user_id, ctx_data in data['user_contexts'].items():
            skill_levels = {
                domain: SkillLevel(level) 
                for domain, level in ctx_data['skill_levels'].items()
            }
            
            current_session = None
            if ctx_data['current_session']:
                current_session = SessionState(**ctx_data['current_session'])
            
            user_contexts[user_id] = UserContextState(
                user_id=ctx_data['user_id'],
                skill_levels=skill_levels,
                learning_preferences=ctx_data['learning_preferences'],
                current_session=current_session
            )
        
        # Reconstruct system metrics
        system_metrics = SystemMetrics(
            cpu_usage=data['system_metrics']['cpu_usage'],
            memory_usage=data['system_metrics']['memory_usage'],
            gpu_usage=data['system_metrics']['gpu_usage'],
            io_operations=data['system_metrics']['io_operations'],
            network_activity=data['system_metrics']['network_activity'],
            consciousness_processing_time=data['system_metrics']['consciousness_processing_time'],
            component_response_times=data['system_metrics']['component_response_times']
        )
        
        # Reconstruct consciousness state
        return ConsciousnessState(
            consciousness_level=data['consciousness_level'],
            emergence_strength=data['emergence_strength'],
            adaptation_rate=data['adaptation_rate'],
            neural_populations=neural_populations,
            active_neural_groups=data['active_neural_groups'],
            evolution_cycles=data['evolution_cycles'],
            user_contexts=user_contexts,
            system_metrics=system_metrics,
            timestamp=datetime.fromisoformat(data['timestamp']),
            version=data['version'],
            checksum=data['checksum']
        )
    
    def _update_serialization_metrics(self, serialization_time: float, original_size: int, compressed_size: int):
        """Update serialization performance metrics"""
        self.serialization_metrics['total_serializations'] += 1
        
        # Update average serialization time
        total_serializations = self.serialization_metrics['total_serializations']
        current_avg = self.serialization_metrics['average_serialization_time']
        self.serialization_metrics['average_serialization_time'] = (
            (current_avg * (total_serializations - 1) + serialization_time) / total_serializations
        )
        
        # Update average compression ratio
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        current_compression_avg = self.serialization_metrics['average_compression_ratio']
        self.serialization_metrics['average_compression_ratio'] = (
            (current_compression_avg * (total_serializations - 1) + compression_ratio) / total_serializations
        )
```

### 2. Incremental Backup Engine

**Purpose**: Efficient incremental backups with delta compression and fast recovery

**Key Features**:
- **Delta Compression**: Store only changes between consciousness states
- **Binary Diff Algorithm**: Efficient binary difference calculation
- **Merkle Tree Validation**: Fast integrity checking of backup chains
- **Parallel Backup Processing**: Multi-threaded backup operations

**Implementation**:
```python
import asyncio
import hashlib
import zlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import struct
import logging

@dataclass
class BackupChain:
    """Chain of incremental backups"""
    chain_id: str
    base_snapshot_id: str
    incremental_snapshots: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_backup: datetime = field(default_factory=datetime.now)
    total_size: int = 0
    compression_ratio: float = 0.0

@dataclass
class DeltaBlock:
    """Binary delta block"""
    offset: int
    old_size: int
    new_size: int
    data: bytes
    checksum: str

@dataclass
class IncrementalBackup:
    """Incremental backup data"""
    backup_id: str
    parent_backup_id: str
    timestamp: datetime
    delta_blocks: List[DeltaBlock]
    metadata_changes: Dict[str, Any]
    total_changes: int
    compressed_size: int

class IncrementalBackupEngine:
    def __init__(self, storage_backend):
        self.storage_backend = storage_backend
        self.backup_chains: Dict[str, BackupChain] = {}
        self.merkle_trees: Dict[str, MerkleTree] = {}
        
        # Backup configuration
        self.max_chain_length = 50  # Max incremental backups before new base
        self.delta_block_size = 4096  # 4KB delta blocks
        self.compression_level = 6
        
        # Performance metrics
        self.backup_metrics = {
            'total_backups': 0,
            'incremental_backups': 0,
            'full_backups': 0,
            'average_backup_time': 0.0,
            'average_delta_size': 0.0,
            'backup_failures': 0
        }
    
    async def create_incremental_backup(self, 
                                      current_state: bytes,
                                      previous_backup_id: Optional[str] = None) -> str:
        """Create incremental backup from current state"""
        
        start_time = datetime.now()
        backup_id = str(uuid.uuid4())
        
        try:
            if previous_backup_id is None:
                # Create full backup (base of new chain)
                backup_data = await self._create_full_backup(current_state, backup_id)
                chain_id = str(uuid.uuid4())
                
                # Create new backup chain
                chain = BackupChain(
                    chain_id=chain_id,
                    base_snapshot_id=backup_id,
                    total_size=len(current_state)
                )
                self.backup_chains[chain_id] = chain
                
                self.backup_metrics['full_backups'] += 1
                
            else:
                # Create incremental backup
                previous_state = await self._load_backup_state(previous_backup_id)
                delta_blocks = await self._calculate_binary_delta(previous_state, current_state)
                
                # Create incremental backup
                incremental_backup = IncrementalBackup(
                    backup_id=backup_id,
                    parent_backup_id=previous_backup_id,
                    timestamp=datetime.now(),
                    delta_blocks=delta_blocks,
                    metadata_changes={},
                    total_changes=len(delta_blocks),
                    compressed_size=sum(len(block.data) for block in delta_blocks)
                )
                
                # Store incremental backup
                await self._store_incremental_backup(incremental_backup)
                
                # Update backup chain
                await self._update_backup_chain(previous_backup_id, backup_id)
                
                self.backup_metrics['incremental_backups'] += 1
            
            # Update metrics
            backup_time = (datetime.now() - start_time).total_seconds()
            self._update_backup_metrics(backup_time)
            
            logger.info(f"Created backup {backup_id} in {backup_time:.2f}s")
            return backup_id
            
        except Exception as e:
            self.backup_metrics['backup_failures'] += 1
            logger.error(f"Backup creation failed: {e}")
            raise
    
    async def _calculate_binary_delta(self, old_data: bytes, new_data: bytes) -> List[DeltaBlock]:
        """Calculate binary delta between two data blocks"""
        
        delta_blocks = []
        old_len = len(old_data)
        new_len = len(new_data)
        
        # Use sliding window algorithm for efficient delta calculation
        window_size = self.delta_block_size
        old_pos = 0
        new_pos = 0
        
        # Create hash table for old data blocks
        old_hashes = {}
        for i in range(0, old_len, window_size):
            block = old_data[i:i + window_size]
            block_hash = hashlib.md5(block).hexdigest()
            old_hashes[block_hash] = i
        
        while new_pos < new_len:
            # Get current new block
            new_block = new_data[new_pos:new_pos + window_size]
            new_hash = hashlib.md5(new_block).hexdigest()
            
            # Check if block exists in old data
            if new_hash in old_hashes:
                old_offset = old_hashes[new_hash]
                
                # Skip identical blocks
                if old_data[old_offset:old_offset + len(new_block)] == new_block:
                    new_pos += len(new_block)
                    continue
            
            # Find the extent of changes
            change_start = new_pos
            while new_pos < new_len:
                test_block = new_data[new_pos:new_pos + window_size]
                test_hash = hashlib.md5(test_block).hexdigest()
                
                if test_hash in old_hashes:
                    old_test_offset = old_hashes[test_hash]
                    if old_data[old_test_offset:old_test_offset + len(test_block)] == test_block:
                        break
                
                new_pos += window_size
            
            # Create delta block for the changed region
            if new_pos > change_start:
                changed_data = new_data[change_start:new_pos]
                compressed_data = zlib.compress(changed_data, self.compression_level)
                
                delta_block = DeltaBlock(
                    offset=change_start,
                    old_size=0,  # Will be calculated during reconstruction
                    new_size=len(changed_data),
                    data=compressed_data,
                    checksum=hashlib.sha256(changed_data).hexdigest()
                )
                
                delta_blocks.append(delta_block)
        
        return delta_blocks
    
    async def restore_from_backup(self, backup_id: str) -> bytes:
        """Restore consciousness state from backup"""
        
        start_time = datetime.now()
        
        try:
            # Find backup chain
            chain = await self._find_backup_chain(backup_id)
            if not chain:
                raise ValueError(f"Backup chain not found for backup {backup_id}")
            
            # Load base backup
            base_state = await self._load_backup_state(chain.base_snapshot_id)
            current_state = base_state
            
            # Apply incremental backups in order
            backup_path = await self._get_backup_path(chain.base_snapshot_id, backup_id)
            
            for incremental_backup_id in backup_path:
                if incremental_backup_id == chain.base_snapshot_id:
                    continue  # Skip base backup
                
                incremental_backup = await self._load_incremental_backup(incremental_backup_id)
                current_state = await self._apply_incremental_backup(current_state, incremental_backup)
            
            restore_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Restored backup {backup_id} in {restore_time:.2f}s")
            
            return current_state
            
        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            raise
    
    async def _apply_incremental_backup(self, base_state: bytes, incremental: IncrementalBackup) -> bytes:
        """Apply incremental backup to base state"""
        
        # Convert to mutable bytearray for efficient modifications
        result_state = bytearray(base_state)
        
        # Apply delta blocks in order
        for delta_block in sorted(incremental.delta_blocks, key=lambda x: x.offset):
            # Decompress delta data
            decompressed_data = zlib.decompress(delta_block.data)
            
            # Verify checksum
            calculated_checksum = hashlib.sha256(decompressed_data).hexdigest()
            if calculated_checksum != delta_block.checksum:
                raise ValueError(f"Delta block corruption detected at offset {delta_block.offset}")
            
            # Apply changes
            end_offset = delta_block.offset + delta_block.new_size
            
            # Extend result if necessary
            if end_offset > len(result_state):
                result_state.extend(b'\x00' * (end_offset - len(result_state)))
            
            # Replace data
            result_state[delta_block.offset:end_offset] = decompressed_data
        
        return bytes(result_state)
    
    async def optimize_backup_chain(self, chain_id: str) -> bool:
        """Optimize backup chain by consolidating incremental backups"""
        
        chain = self.backup_chains.get(chain_id)
        if not chain:
            return False
        
        # Check if optimization is needed
        if len(chain.incremental_snapshots) < self.max_chain_length:
            return False
        
        try:
            # Create new consolidated base backup
            latest_backup_id = chain.incremental_snapshots[-1]
            consolidated_state = await self.restore_from_backup(latest_backup_id)
            
            # Create new base backup
            new_base_id = await self._create_full_backup(consolidated_state, str(uuid.uuid4()))
            
            # Create new optimized chain
            new_chain = BackupChain(
                chain_id=str(uuid.uuid4()),
                base_snapshot_id=new_base_id,
                created_at=datetime.now(),
                total_size=len(consolidated_state)
            )
            
            # Replace old chain
            self.backup_chains[new_chain.chain_id] = new_chain
            
            # Clean up old chain (mark for deletion)
            await self._mark_chain_for_cleanup(chain_id)
            
            logger.info(f"Optimized backup chain {chain_id} -> {new_chain.chain_id}")
            return True
            
        except Exception as e:
            logger.error(f"Backup chain optimization failed: {e}")
            return False

class MerkleTree:
    """Merkle tree for backup integrity verification"""
    
    def __init__(self, data_blocks: List[bytes]):
        self.leaves = [hashlib.sha256(block).digest() for block in data_blocks]
        self.tree = self._build_tree(self.leaves)
        self.root_hash = self.tree[0] if self.tree else b''
    
    def _build_tree(self, hashes: List[bytes]) -> List[bytes]:
        """Build Merkle tree from leaf hashes"""
        if not hashes:
            return []
        
        tree = hashes[:]
        level_size = len(hashes)
        
        while level_size > 1:
            next_level = []
            
            for i in range(0, level_size, 2):
                left = tree[i]
                right = tree[i + 1] if i + 1 < level_size else left
                
                combined = left + right
                parent_hash = hashlib.sha256(combined).digest()
                next_level.append(parent_hash)
            
            tree.extend(next_level)
            level_size = len(next_level)
        
        return tree
    
    def verify_integrity(self, data_blocks: List[bytes]) -> bool:
        """Verify data integrity using Merkle tree"""
        expected_tree = MerkleTree(data_blocks)
        return self.root_hash == expected_tree.root_hash
    
    def get_proof(self, leaf_index: int) -> List[bytes]:
        """Get Merkle proof for a specific leaf"""
        if leaf_index >= len(self.leaves):
            return []
        
        proof = []
        current_index = leaf_index
        level_start = 0
        level_size = len(self.leaves)
        
        while level_