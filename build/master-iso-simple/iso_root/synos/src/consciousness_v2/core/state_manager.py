"""
Consciousness State Manager
==========================

Unified state management system for the consciousness architecture.
Provides centralized state coordination, persistence, and real-time updates
across all consciousness components.
"""

import asyncio
import logging
import json
import pickle
import time
from typing import Dict, List, Optional, Any, Callable, Set, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
import threading
import weakref
from collections import defaultdict

from .data_models import (
    ConsciousnessState, ComponentStatus, ComponentState,
    PopulationState, UserContextState, SystemMetrics,
    create_default_consciousness_state
)
from .event_types import (
    ConsciousnessEvent, EventType, EventPriority,
    create_state_update_event, create_error_recovery_event
)


@dataclass
class StateSnapshot:
    """Immutable state snapshot for versioning"""
    snapshot_id: str
    timestamp: datetime
    consciousness_state: ConsciousnessState
    component_states: Dict[str, ComponentStatus]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization"""
        return {
            'snapshot_id': self.snapshot_id,
            'timestamp': self.timestamp.isoformat(),
            'consciousness_state': self.consciousness_state.to_dict(),
            'component_states': {
                k: v.to_dict() for k, v in self.component_states.items()
            },
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        """Create snapshot from dictionary"""
        return cls(
            snapshot_id=data['snapshot_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            consciousness_state=ConsciousnessState.from_dict(data['consciousness_state']),
            component_states={
                k: ComponentStatus.from_dict(v) 
                for k, v in data['component_states'].items()
            },
            metadata=data.get('metadata', {})
        )


@dataclass
class StateChangeEvent:
    """State change tracking"""
    change_id: str
    timestamp: datetime
    component_id: str
    change_type: str
    old_value: Any
    new_value: Any
    path: str  # JSON path to the changed field
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'change_id': self.change_id,
            'timestamp': self.timestamp.isoformat(),
            'component_id': self.component_id,
            'change_type': self.change_type,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'path': self.path
        }


class StateManager:
    """
    Unified consciousness state management system
    
    Features:
    - Centralized state coordination
    - Real-time state synchronization
    - State versioning and snapshots
    - Conflict resolution
    - Performance optimization
    - Persistence and recovery
    """
    
    def __init__(self,
                 persistence_path: Optional[Path] = None,
                 snapshot_interval: float = 60.0,
                 max_snapshots: int = 100,
                 auto_save_interval: float = 30.0,
                 conflict_resolution_strategy: str = "latest_wins"):
        
        # Configuration
        self.persistence_path = persistence_path or Path("data/consciousness_state")
        self.snapshot_interval = snapshot_interval
        self.max_snapshots = max_snapshots
        self.auto_save_interval = auto_save_interval
        self.conflict_resolution_strategy = conflict_resolution_strategy
        
        # Core state
        self.consciousness_state: ConsciousnessState = create_default_consciousness_state()
        self.component_states: Dict[str, ComponentStatus] = {}
        
        # State management
        self.state_lock = asyncio.Lock()
        self.state_version = 0
        self.last_modified = datetime.now()
        
        # Change tracking
        self.change_history: List[StateChangeEvent] = []
        self.change_subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        
        # Snapshots
        self.snapshots: List[StateSnapshot] = []
        self.snapshot_lock = asyncio.Lock()
        
        # Background tasks
        self.snapshot_task: Optional[asyncio.Task] = None
        self.auto_save_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Performance tracking
        self.read_count = 0
        self.write_count = 0
        self.last_performance_reset = datetime.now()
        
        # Event bus reference (set externally)
        self.event_bus: Optional[Any] = None
        
        # Logger
        self.logger = logging.getLogger(f"{__name__}.StateManager")
        
        # Ensure persistence directory exists
        self.persistence_path.mkdir(parents=True, exist_ok=True)
    
    async def start(self) -> bool:
        """Start the state manager"""
        if self.is_running:
            self.logger.warning("State manager is already running")
            return True
        
        try:
            self.logger.info("Starting state manager...")
            
            # Load existing state if available
            await self._load_state()
            
            # Start background tasks
            self.snapshot_task = asyncio.create_task(self._snapshot_loop())
            self.auto_save_task = asyncio.create_task(self._auto_save_loop())
            
            self.is_running = True
            self.logger.info("State manager started successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start state manager: {e}")
            await self.stop()
            return False
    
    async def stop(self) -> None:
        """Stop the state manager"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping state manager...")
        self.is_running = False
        
        # Cancel background tasks
        if self.snapshot_task:
            self.snapshot_task.cancel()
        if self.auto_save_task:
            self.auto_save_task.cancel()
        
        # Save final state
        await self._save_state()
        
        self.logger.info("State manager stopped")
    
    async def get_consciousness_state(self) -> ConsciousnessState:
        """Get current consciousness state (thread-safe)"""
        async with self.state_lock:
            self.read_count += 1
            # Return a copy to prevent external modifications
            return ConsciousnessState.from_dict(self.consciousness_state.to_dict())
    
    async def update_consciousness_state(self,
                                       component_id: str,
                                       updates: Dict[str, Any],
                                       merge_strategy: str = "deep_merge") -> bool:
        """Update consciousness state with conflict resolution"""
        
        async with self.state_lock:
            try:
                old_state_dict = self.consciousness_state.to_dict()
                
                # Apply updates based on merge strategy
                if merge_strategy == "deep_merge":
                    await self._deep_merge_updates(updates)
                elif merge_strategy == "replace":
                    await self._replace_updates(updates)
                elif merge_strategy == "selective":
                    await self._selective_updates(updates, component_id)
                else:
                    raise ValueError(f"Unknown merge strategy: {merge_strategy}")
                
                # Track changes
                new_state_dict = self.consciousness_state.to_dict()
                await self._track_state_changes(
                    component_id, old_state_dict, new_state_dict
                )
                
                # Update metadata
                self.state_version += 1
                self.last_modified = datetime.now()
                self.write_count += 1
                self.consciousness_state.timestamp = self.last_modified
                
                # Notify subscribers
                await self._notify_state_change(component_id, updates)
                
                self.logger.debug(f"Updated consciousness state from {component_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update consciousness state: {e}")
                return False
    
    async def get_component_state(self, component_id: str) -> Optional[ComponentStatus]:
        """Get component state"""
        async with self.state_lock:
            self.read_count += 1
            component = self.component_states.get(component_id)
            if component:
                return ComponentStatus.from_dict(component.to_dict())
            return None
    
    async def update_component_state(self,
                                   component_id: str,
                                   component_status: ComponentStatus) -> bool:
        """Update component state"""
        
        async with self.state_lock:
            try:
                old_status = self.component_states.get(component_id)
                self.component_states[component_id] = component_status
                
                # Track change
                if old_status:
                    await self._track_component_change(
                        component_id, old_status, component_status
                    )
                
                self.write_count += 1
                
                # Notify subscribers
                await self._notify_component_change(component_id, component_status)
                
                self.logger.debug(f"Updated component state for {component_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update component state: {e}")
                return False
    
    async def create_snapshot(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a state snapshot"""
        
        async with self.snapshot_lock:
            try:
                snapshot_id = f"snapshot_{int(time.time() * 1000)}"
                
                # Create snapshot
                snapshot = StateSnapshot(
                    snapshot_id=snapshot_id,
                    timestamp=datetime.now(),
                    consciousness_state=ConsciousnessState.from_dict(
                        self.consciousness_state.to_dict()
                    ),
                    component_states={
                        k: ComponentStatus.from_dict(v.to_dict())
                        for k, v in self.component_states.items()
                    },
                    metadata=metadata or {}
                )
                
                # Add to snapshots list
                self.snapshots.append(snapshot)
                
                # Maintain max snapshots limit
                if len(self.snapshots) > self.max_snapshots:
                    self.snapshots = self.snapshots[-self.max_snapshots:]
                
                # Save snapshot to disk
                await self._save_snapshot(snapshot)
                
                self.logger.info(f"Created state snapshot {snapshot_id}")
                return snapshot_id
                
            except Exception as e:
                self.logger.error(f"Failed to create snapshot: {e}")
                return ""
    
    async def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore state from snapshot"""
        
        async with self.state_lock:
            try:
                # Find snapshot
                snapshot = None
                for snap in self.snapshots:
                    if snap.snapshot_id == snapshot_id:
                        snapshot = snap
                        break
                
                if not snapshot:
                    # Try loading from disk
                    snapshot = await self._load_snapshot(snapshot_id)
                
                if not snapshot:
                    self.logger.error(f"Snapshot {snapshot_id} not found")
                    return False
                
                # Restore state
                self.consciousness_state = ConsciousnessState.from_dict(
                    snapshot.consciousness_state.to_dict()
                )
                self.component_states = {
                    k: ComponentStatus.from_dict(v.to_dict())
                    for k, v in snapshot.component_states.items()
                }
                
                # Update metadata
                self.state_version += 1
                self.last_modified = datetime.now()
                
                # Notify all subscribers of full state change
                await self._notify_state_restore(snapshot_id)
                
                self.logger.info(f"Restored state from snapshot {snapshot_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to restore snapshot {snapshot_id}: {e}")
                return False
    
    async def subscribe_to_changes(self,
                                 component_id: str,
                                 callback: Callable[[str, Dict[str, Any]], None],
                                 filter_paths: Optional[List[str]] = None) -> str:
        """Subscribe to state changes"""
        
        subscription_id = f"{component_id}_{int(time.time() * 1000)}"
        
        # Wrap callback with filter if provided
        if filter_paths:
            original_callback = callback
            def filtered_callback(comp_id: str, changes: Dict[str, Any]):
                filtered_changes = {}
                for path in filter_paths:
                    if path in changes:
                        filtered_changes[path] = changes[path]
                if filtered_changes:
                    original_callback(comp_id, filtered_changes)
            callback = filtered_callback
        
        self.change_subscribers[subscription_id].add(callback)
        
        self.logger.debug(f"Component {component_id} subscribed to state changes")
        return subscription_id
    
    async def unsubscribe_from_changes(self, subscription_id: str) -> bool:
        """Unsubscribe from state changes"""
        
        if subscription_id in self.change_subscribers:
            del self.change_subscribers[subscription_id]
            self.logger.debug(f"Unsubscribed {subscription_id} from state changes")
            return True
        
        return False
    
    async def get_state_metrics(self) -> Dict[str, Any]:
        """Get state management metrics"""
        
        current_time = datetime.now()
        time_diff = (current_time - self.last_performance_reset).total_seconds()
        
        return {
            'state_version': self.state_version,
            'last_modified': self.last_modified.isoformat(),
            'read_count': self.read_count,
            'write_count': self.write_count,
            'reads_per_second': self.read_count / max(time_diff, 1),
            'writes_per_second': self.write_count / max(time_diff, 1),
            'snapshot_count': len(self.snapshots),
            'change_history_size': len(self.change_history),
            'active_subscriptions': len(self.change_subscribers),
            'component_count': len(self.component_states),
            'is_running': self.is_running,
            'persistence_path': str(self.persistence_path)
        }
    
    async def get_change_history(self,
                               component_id: Optional[str] = None,
                               since: Optional[datetime] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get state change history"""
        
        changes = self.change_history
        
        # Filter by component
        if component_id:
            changes = [c for c in changes if c.component_id == component_id]
        
        # Filter by time
        if since:
            changes = [c for c in changes if c.timestamp >= since]
        
        # Apply limit
        changes = changes[-limit:]
        
        return [change.to_dict() for change in changes]
    
    async def _deep_merge_updates(self, updates: Dict[str, Any]) -> None:
        """Deep merge updates into consciousness state"""
        
        def deep_merge(target: Dict, source: Dict) -> Dict:
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
            return target
        
        # Convert state to dict, merge, then convert back
        state_dict = self.consciousness_state.to_dict()
        merged_dict = deep_merge(state_dict, updates)
        self.consciousness_state = ConsciousnessState.from_dict(merged_dict)
    
    async def _replace_updates(self, updates: Dict[str, Any]) -> None:
        """Replace consciousness state fields"""
        
        state_dict = self.consciousness_state.to_dict()
        state_dict.update(updates)
        self.consciousness_state = ConsciousnessState.from_dict(state_dict)
    
    async def _selective_updates(self, updates: Dict[str, Any], component_id: str) -> None:
        """Apply selective updates based on component permissions"""
        
        # Define component update permissions
        permissions = {
            'neural_engine': ['neural_populations', 'consciousness_level'],
            'lm_studio': ['ai_models', 'inference_metrics'],
            'context_engine': ['user_contexts', 'context_metrics'],
            'security_tutor': ['user_contexts', 'learning_metrics'],
            'kernel_hooks': ['system_metrics', 'resource_usage']
        }
        
        allowed_fields = permissions.get(component_id, [])
        
        # Filter updates to only allowed fields
        filtered_updates = {
            k: v for k, v in updates.items() 
            if any(k.startswith(field) for field in allowed_fields)
        }
        
        if filtered_updates:
            await self._deep_merge_updates(filtered_updates)
    
    async def _track_state_changes(self,
                                 component_id: str,
                                 old_state: Dict[str, Any],
                                 new_state: Dict[str, Any]) -> None:
        """Track state changes for history"""
        
        def find_changes(old_dict: Dict, new_dict: Dict, path: str = "") -> List[StateChangeEvent]:
            changes = []
            
            # Check for modified/added keys
            for key, new_value in new_dict.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in old_dict:
                    # New key
                    changes.append(StateChangeEvent(
                        change_id=f"change_{int(time.time() * 1000000)}",
                        timestamp=datetime.now(),
                        component_id=component_id,
                        change_type="added",
                        old_value=None,
                        new_value=new_value,
                        path=current_path
                    ))
                elif old_dict[key] != new_value:
                    if isinstance(old_dict[key], dict) and isinstance(new_value, dict):
                        # Recursive check for nested dicts
                        changes.extend(find_changes(old_dict[key], new_value, current_path))
                    else:
                        # Value changed
                        changes.append(StateChangeEvent(
                            change_id=f"change_{int(time.time() * 1000000)}",
                            timestamp=datetime.now(),
                            component_id=component_id,
                            change_type="modified",
                            old_value=old_dict[key],
                            new_value=new_value,
                            path=current_path
                        ))
            
            # Check for removed keys
            for key in old_dict:
                if key not in new_dict:
                    current_path = f"{path}.{key}" if path else key
                    changes.append(StateChangeEvent(
                        change_id=f"change_{int(time.time() * 1000000)}",
                        timestamp=datetime.now(),
                        component_id=component_id,
                        change_type="removed",
                        old_value=old_dict[key],
                        new_value=None,
                        path=current_path
                    ))
            
            return changes
        
        changes = find_changes(old_state, new_state)
        self.change_history.extend(changes)
        
        # Maintain history size limit
        if len(self.change_history) > 1000:
            self.change_history = self.change_history[-1000:]
    
    async def _track_component_change(self,
                                    component_id: str,
                                    old_status: ComponentStatus,
                                    new_status: ComponentStatus) -> None:
        """Track component state changes"""
        
        change = StateChangeEvent(
            change_id=f"comp_change_{int(time.time() * 1000000)}",
            timestamp=datetime.now(),
            component_id=component_id,
            change_type="component_update",
            old_value=old_status.to_dict(),
            new_value=new_status.to_dict(),
            path=f"components.{component_id}"
        )
        
        self.change_history.append(change)
    
    async def _notify_state_change(self, component_id: str, updates: Dict[str, Any]) -> None:
        """Notify subscribers of state changes"""
        
        for subscription_id, callbacks in self.change_subscribers.items():
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(component_id, updates)
                    else:
                        callback(component_id, updates)
                except Exception as e:
                    self.logger.error(f"Error in state change callback: {e}")
        
        # Publish event to bus if available
        if self.event_bus and hasattr(self.event_bus, 'publish'):
            try:
                event = create_state_update_event(
                    source_component="state_manager",
                    state_data={
                        'updated_by': component_id,
                        'updates': updates,
                        'version': self.state_version,
                        'timestamp': self.last_modified.isoformat()
                    }
                )
                await self.event_bus.publish(event)
            except Exception as e:
                self.logger.warning(f"Failed to publish state update event: {e}")
    
    async def _notify_component_change(self, component_id: str, status: ComponentStatus) -> None:
        """Notify subscribers of component changes"""
        
        updates = {'component_states': {component_id: status.to_dict()}}
        await self._notify_state_change(component_id, updates)
    
    async def _notify_state_restore(self, snapshot_id: str) -> None:
        """Notify subscribers of state restoration"""
        
        updates = {
            'restored_from_snapshot': snapshot_id,
            'full_state_restore': True,
            'timestamp': datetime.now().isoformat()
        }
        await self._notify_state_change("state_manager", updates)
    
    async def _save_state(self) -> None:
        """Save current state to disk"""
        
        try:
            state_file = self.persistence_path / "current_state.json"
            
            state_data = {
                'consciousness_state': self.consciousness_state.to_dict(),
                'component_states': {
                    k: v.to_dict() for k, v in self.component_states.items()
                },
                'state_version': self.state_version,
                'last_modified': self.last_modified.isoformat(),
                'metadata': {
                    'saved_at': datetime.now().isoformat(),
                    'read_count': self.read_count,
                    'write_count': self.write_count
                }
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.debug("Saved state to disk")
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    async def _load_state(self) -> None:
        """Load state from disk"""
        
        try:
            state_file = self.persistence_path / "current_state.json"
            
            if not state_file.exists():
                self.logger.info("No existing state file found, using default state")
                return
            
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            # Restore consciousness state
            self.consciousness_state = ConsciousnessState.from_dict(
                state_data['consciousness_state']
            )
            
            # Restore component states
            self.component_states = {
                k: ComponentStatus.from_dict(v)
                for k, v in state_data['component_states'].items()
            }
            
            # Restore metadata
            self.state_version = state_data.get('state_version', 0)
            self.last_modified = datetime.fromisoformat(
                state_data.get('last_modified', datetime.now().isoformat())
            )
            
            self.logger.info(f"Loaded state from disk (version {self.state_version})")
            
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            self.logger.info("Using default state")
    
    async def _save_snapshot(self, snapshot: StateSnapshot) -> None:
        """Save snapshot to disk"""
        
        try:
            snapshot_file = self.persistence_path / f"snapshot_{snapshot.snapshot_id}.json"
            
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save snapshot {snapshot.snapshot_id}: {e}")
    
    async def _load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load snapshot from disk"""
        
        try:
            snapshot_file = self.persistence_path / f"snapshot_{snapshot_id}.json"
            
            if not snapshot_file.exists():
                return None
            
            with open(snapshot_file, 'r') as f:
                snapshot_data = json.load(f)
            
            return StateSnapshot.from_dict(snapshot_data)
            
        except Exception as e:
            self.logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
            return None
    
    async def _snapshot_loop(self) -> None:
        """Background snapshot creation loop"""
        
        while self.is_running:
            try:
                await asyncio.sleep(self.snapshot_interval)
                
                if self.is_running:
                    await self.create_snapshot({
                        'type': 'automatic',
                        'trigger': 'scheduled'
                    })
                    
            except Exception as e:
                self.logger.error(f"Error in snapshot loop: {e}")
    
    async def _auto_save_loop(self) -> None:
        """Background auto-save loop"""
        
        while self.is_running:
            try:
                await asyncio.sleep(self.auto_save_interval)
                
                if self.is_running:
                    await self._save_state()
                    
            except Exception as e:
                self.logger.error(f"Error in auto-save loop: {e}")