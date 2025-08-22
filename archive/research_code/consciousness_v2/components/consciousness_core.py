"""
Consciousness Core Component
===========================

Core consciousness management system that provides the main interface
for consciousness state, attention management, and cognitive processing.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ..core.state_manager import StateManager
from ..core.data_models import ConsciousnessState, create_default_consciousness_state
from ..core.event_types import (
    ConsciousnessEvent, EventType, EventPriority,
    create_state_update_event, create_neural_evolution_event
)


@dataclass
class AttentionFocus:
    """Attention focus tracking"""
    domain: str
    intensity: float  # 0.0 to 1.0
    duration: float   # seconds
    last_updated: datetime = field(default_factory=datetime.now)
    
    def decay(self, decay_rate: float = 0.1) -> None:
        """Apply attention decay over time"""
        time_diff = (datetime.now() - self.last_updated).total_seconds()
        self.intensity *= (1.0 - decay_rate * time_diff / 60.0)  # Decay per minute
        self.intensity = max(0.0, self.intensity)
        self.last_updated = datetime.now()


@dataclass
class CognitiveLoad:
    """Cognitive load tracking"""
    processing_tasks: int = 0
    memory_usage: float = 0.0  # 0.0 to 1.0
    attention_fragmentation: float = 0.0  # 0.0 to 1.0
    decision_complexity: float = 0.0  # 0.0 to 1.0
    
    def calculate_total_load(self) -> float:
        """Calculate total cognitive load"""
        return min(1.0, (
            self.processing_tasks * 0.1 +
            self.memory_usage * 0.3 +
            self.attention_fragmentation * 0.3 +
            self.decision_complexity * 0.3
        ))


@dataclass
class EmotionalState:
    """Emotional state tracking"""
    valence: float = 0.0      # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.0      # 0.0 (calm) to 1.0 (excited)
    confidence: float = 0.5   # 0.0 to 1.0
    curiosity: float = 0.5    # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update(self, valence_delta: float = 0.0, arousal_delta: float = 0.0,
               confidence_delta: float = 0.0, curiosity_delta: float = 0.0) -> None:
        """Update emotional state with deltas"""
        self.valence = max(-1.0, min(1.0, self.valence + valence_delta))
        self.arousal = max(0.0, min(1.0, self.arousal + arousal_delta))
        self.confidence = max(0.0, min(1.0, self.confidence + confidence_delta))
        self.curiosity = max(0.0, min(1.0, self.curiosity + curiosity_delta))
        self.last_updated = datetime.now()


class ConsciousnessCore:
    """
    Core consciousness management system
    
    Features:
    - Attention management and focus tracking
    - Emotional state monitoring
    - Cognitive load assessment
    - Learning mode adaptation
    - Memory context management
    - Problem-solving coordination
    """
    
    def __init__(self, state_manager: Optional[StateManager] = None):
        """
        Initialize consciousness core
        
        Args:
            state_manager: State manager instance for persistence
        """
        self.state_manager = state_manager or StateManager()
        self.logger = logging.getLogger(__name__)
        
        # Core consciousness state
        self.consciousness_state: ConsciousnessState = create_default_consciousness_state()
        
        # Attention management
        self.attention_foci: Dict[str, AttentionFocus] = {}
        self.attention_decay_rate = 0.1  # per minute
        
        # Cognitive processing
        self.cognitive_load = CognitiveLoad()
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
        # Emotional state
        self.emotional_state = EmotionalState()
        
        # Learning and adaptation
        self.learning_mode = "adaptive"  # adaptive, focused, exploratory
        self.learning_rate = 0.1
        
        # Memory and context
        self.working_memory: Dict[str, Any] = {}
        self.working_memory_limit = 7  # Miller's rule
        self.long_term_memory_active = True
        self.recent_experiences: List[Dict[str, Any]] = []
        
        # Background tasks
        self.attention_decay_task: Optional[asyncio.Task] = None
        self.state_sync_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Performance metrics
        self.decision_count = 0
        self.problem_solving_sessions = 0
        self.attention_shifts = 0
        self.last_metrics_reset = datetime.now()
    
    async def start(self) -> bool:
        """Start the consciousness core"""
        if self.is_running:
            self.logger.warning("Consciousness core is already running")
            return True
        
        try:
            self.logger.info("Starting consciousness core...")
            
            # Start state manager if not running
            if not self.state_manager.is_running:
                await self.state_manager.start()
            
            # Load existing consciousness state
            existing_state = await self.state_manager.get_consciousness_state()
            if existing_state:
                self.consciousness_state = existing_state
                self.logger.info("Loaded existing consciousness state")
            
            # Start background tasks
            self.attention_decay_task = asyncio.create_task(self._attention_decay_loop())
            self.state_sync_task = asyncio.create_task(self._state_sync_loop())
            
            self.is_running = True
            self.logger.info("Consciousness core started successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start consciousness core: {e}")
            await self.stop()
            return False
    
    async def stop(self) -> None:
        """Stop the consciousness core"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping consciousness core...")
        self.is_running = False
        
        # Cancel background tasks
        if self.attention_decay_task:
            self.attention_decay_task.cancel()
        if self.state_sync_task:
            self.state_sync_task.cancel()
        
        # Save final state
        await self._sync_state_to_manager()
        
        # Stop state manager if we started it
        if self.state_manager.is_running:
            await self.state_manager.stop()
        
        self.logger.info("Consciousness core stopped")
    
    # Attention Management
    
    async def adjust_attention(self, domain: str, intensity_delta: float) -> None:
        """
        Adjust attention focus for a specific domain
        
        Args:
            domain: Attention domain (e.g., 'system_management', 'user_interaction')
            intensity_delta: Change in attention intensity (-1.0 to 1.0)
        """
        try:
            if domain not in self.attention_foci:
                self.attention_foci[domain] = AttentionFocus(
                    domain=domain,
                    intensity=0.5,
                    duration=0.0
                )
            
            focus = self.attention_foci[domain]
            old_intensity = focus.intensity
            
            # Apply intensity change
            focus.intensity = max(0.0, min(1.0, focus.intensity + intensity_delta))
            focus.last_updated = datetime.now()
            
            # Track attention shift
            if abs(intensity_delta) > 0.1:
                self.attention_shifts += 1
            
            # Update cognitive load
            self._update_cognitive_load()
            
            self.logger.debug(
                f"Adjusted attention for {domain}: {old_intensity:.2f} -> {focus.intensity:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to adjust attention for {domain}: {e}")
    
    def get_attention_focus(self) -> Dict[str, float]:
        """Get current attention focus distribution"""
        return {
            domain: focus.intensity 
            for domain, focus in self.attention_foci.items()
            if focus.intensity > 0.01
        }
    
    def get_attention_level(self) -> float:
        """Get overall attention level"""
        if not self.attention_foci:
            return 0.5
        
        total_attention = sum(focus.intensity for focus in self.attention_foci.values())
        return min(1.0, total_attention)
    
    # Emotional State Management
    
    def get_emotional_state(self) -> Dict[str, float]:
        """Get current emotional state"""
        return {
            'valence': self.emotional_state.valence,
            'arousal': self.emotional_state.arousal,
            'confidence': self.emotional_state.confidence,
            'curiosity': self.emotional_state.curiosity
        }
    
    async def update_emotional_state(self, **kwargs) -> None:
        """Update emotional state"""
        try:
            self.emotional_state.update(**kwargs)
            
            # Emotional state affects attention and learning
            if self.emotional_state.arousal > 0.7:
                # High arousal increases attention fragmentation
                self.cognitive_load.attention_fragmentation = min(1.0, 
                    self.cognitive_load.attention_fragmentation + 0.1)
            
            if self.emotional_state.confidence < 0.3:
                # Low confidence increases decision complexity
                self.cognitive_load.decision_complexity = min(1.0,
                    self.cognitive_load.decision_complexity + 0.1)
            
            self.logger.debug(f"Updated emotional state: {self.get_emotional_state()}")
            
        except Exception as e:
            self.logger.error(f"Failed to update emotional state: {e}")
    
    # Cognitive Load Management
    
    def get_cognitive_load(self) -> float:
        """Get current cognitive load"""
        return self.cognitive_load.calculate_total_load()
    
    def _update_cognitive_load(self) -> None:
        """Update cognitive load based on current state"""
        # Calculate attention fragmentation
        active_foci = [f for f in self.attention_foci.values() if f.intensity > 0.1]
        self.cognitive_load.attention_fragmentation = min(1.0, len(active_foci) * 0.2)
        
        # Calculate memory usage
        memory_usage = len(self.working_memory) / self.working_memory_limit
        self.cognitive_load.memory_usage = min(1.0, memory_usage)
        
        # Processing tasks updated externally
        # Decision complexity updated by problem-solving
    
    # Learning and Adaptation
    
    def get_learning_mode(self) -> str:
        """Get current learning mode"""
        return self.learning_mode
    
    async def set_learning_mode(self, mode: str) -> None:
        """
        Set learning mode
        
        Args:
            mode: Learning mode ('adaptive', 'focused', 'exploratory')
        """
        if mode in ['adaptive', 'focused', 'exploratory']:
            old_mode = self.learning_mode
            self.learning_mode = mode
            
            # Adjust learning rate based on mode
            if mode == 'focused':
                self.learning_rate = 0.05  # Slower, more deliberate
            elif mode == 'exploratory':
                self.learning_rate = 0.2   # Faster, more experimental
            else:  # adaptive
                self.learning_rate = 0.1   # Balanced
            
            self.logger.info(f"Learning mode changed: {old_mode} -> {mode}")
        else:
            self.logger.warning(f"Invalid learning mode: {mode}")
    
    # Memory Management
    
    def get_working_memory_size(self) -> int:
        """Get current working memory size"""
        return len(self.working_memory)
    
    def is_long_term_memory_active(self) -> bool:
        """Check if long-term memory is active"""
        return self.long_term_memory_active
    
    def get_recent_experiences(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent experiences"""
        return self.recent_experiences[-limit:] if self.recent_experiences else []
    
    async def add_experience(self, experience: Dict[str, Any]) -> None:
        """Add experience to memory"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in experience:
                experience['timestamp'] = datetime.now().isoformat()
            
            # Add to recent experiences
            self.recent_experiences.append(experience)
            
            # Maintain experience limit
            if len(self.recent_experiences) > 100:
                self.recent_experiences = self.recent_experiences[-100:]
            
            # Update working memory if relevant
            if experience.get('importance', 0.5) > 0.7:
                memory_key = f"exp_{len(self.recent_experiences)}"
                self.working_memory[memory_key] = experience
                
                # Manage working memory limit
                if len(self.working_memory) > self.working_memory_limit:
                    # Remove oldest item
                    oldest_key = min(self.working_memory.keys())
                    del self.working_memory[oldest_key]
            
            self.logger.debug(f"Added experience: {experience.get('type', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Failed to add experience: {e}")
    
    # Problem Solving
    
    async def trigger_problem_solving(self, problem_description: str) -> None:
        """
        Trigger problem-solving mode
        
        Args:
            problem_description: Description of the problem to solve
        """
        try:
            self.problem_solving_sessions += 1
            
            # Increase cognitive load
            self.cognitive_load.processing_tasks += 1
            self.cognitive_load.decision_complexity = min(1.0,
                self.cognitive_load.decision_complexity + 0.2)
            
            # Adjust attention to problem-solving
            await self.adjust_attention('problem_solving', 0.3)
            
            # Update emotional state (increased arousal, decreased confidence initially)
            await self.update_emotional_state(arousal=0.1, confidence=-0.1)
            
            # Add to experiences
            await self.add_experience({
                'type': 'problem_solving_initiated',
                'description': problem_description,
                'session_id': self.problem_solving_sessions,
                'importance': 0.8
            })
            
            self.logger.info(f"Triggered problem-solving: {problem_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger problem-solving: {e}")
    
    async def complete_problem_solving(self, success: bool = True) -> None:
        """Complete problem-solving session"""
        try:
            # Reduce cognitive load
            self.cognitive_load.processing_tasks = max(0, 
                self.cognitive_load.processing_tasks - 1)
            self.cognitive_load.decision_complexity = max(0.0,
                self.cognitive_load.decision_complexity - 0.2)
            
            # Adjust emotional state based on success
            if success:
                await self.update_emotional_state(valence=0.1, confidence=0.1)
            else:
                await self.update_emotional_state(valence=-0.1, confidence=-0.05)
            
            # Reduce problem-solving attention
            await self.adjust_attention('problem_solving', -0.2)
            
            self.logger.debug(f"Completed problem-solving session (success: {success})")
            
        except Exception as e:
            self.logger.error(f"Failed to complete problem-solving: {e}")
    
    # State Synchronization
    
    async def _sync_state_to_manager(self) -> None:
        """Sync consciousness state to state manager"""
        try:
            # Update consciousness state with current values
            self.consciousness_state.consciousness_level = self.get_attention_level()
            self.consciousness_state.timestamp = datetime.now()
            
            # Prepare state updates
            state_updates = {
                'consciousness_level': self.consciousness_state.consciousness_level,
                'attention_foci': {
                    domain: {
                        'intensity': focus.intensity,
                        'duration': focus.duration,
                        'last_updated': focus.last_updated.isoformat()
                    }
                    for domain, focus in self.attention_foci.items()
                },
                'emotional_state': self.get_emotional_state(),
                'cognitive_load': self.get_cognitive_load(),
                'learning_mode': self.learning_mode,
                'working_memory_size': len(self.working_memory),
                'recent_experiences_count': len(self.recent_experiences),
                'metrics': {
                    'decision_count': self.decision_count,
                    'problem_solving_sessions': self.problem_solving_sessions,
                    'attention_shifts': self.attention_shifts
                }
            }
            
            # Update state manager
            await self.state_manager.update_consciousness_state(
                "consciousness_core", state_updates
            )
            
        except Exception as e:
            self.logger.error(f"Failed to sync state to manager: {e}")
    
    # Background Tasks
    
    async def _attention_decay_loop(self) -> None:
        """Background loop for attention decay"""
        while self.is_running:
            try:
                # Apply decay to all attention foci
                for focus in self.attention_foci.values():
                    focus.decay(self.attention_decay_rate)
                
                # Remove very low attention foci
                self.attention_foci = {
                    domain: focus for domain, focus in self.attention_foci.items()
                    if focus.intensity > 0.01
                }
                
                # Update cognitive load
                self._update_cognitive_load()
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in attention decay loop: {e}")
                await asyncio.sleep(30)
    
    async def _state_sync_loop(self) -> None:
        """Background loop for state synchronization"""
        while self.is_running:
            try:
                await self._sync_state_to_manager()
                await asyncio.sleep(60)  # Sync every minute
                
            except Exception as e:
                self.logger.error(f"Error in state sync loop: {e}")
                await asyncio.sleep(60)


# Convenience function to create consciousness core
async def create_consciousness_core(state_manager: Optional[StateManager] = None) -> ConsciousnessCore:
    """Create and start a consciousness core instance"""
    core = ConsciousnessCore(state_manager)
    await core.start()
    return core