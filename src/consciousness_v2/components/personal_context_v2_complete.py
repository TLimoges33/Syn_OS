#!/usr/bin/env python3
"""
Personal Context Engine v2 for SynapticOS Consciousness System
Enhanced with real-time consciousness feedback loops, predictive skill assessment,
and high-performance in-memory processing.

Based on Second-Me Personal Context Engine with consciousness integration.
"""

import asyncio
import json
import logging
import numpy as np
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Fallback for when PyTorch is not available
    class nn:
        class Module:
            def __init__(self):
                pass
        class Sequential:
            def __init__(self, *args):
                pass
        class Linear:
            def __init__(self, *args, **kwargs):
                pass
        class ReLU:
            def __init__(self):
                pass
        class Dropout:
            def __init__(self, *args):
                pass
        @staticmethod
        def softmax(x, dim=-1):
            return x

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle
import sqlite3
import aiosqlite

# Import consciousness system components
from ..core.consciousness_bus import ConsciousnessBus
from ..core.event_types import EventType, ConsciousnessEvent, create_context_update_event
from ..core.data_models import ConsciousnessState, ComponentStatus, PopulationState, ComponentState
from ..interfaces.consciousness_component import ConsciousnessComponent

logger = logging.getLogger('synapticos.context_engine_v2')

class SkillLevel(Enum):
    """Enhanced skill levels with numerical values for ML processing"""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5

class ActivityType(Enum):
    """Enhanced activity types with consciousness correlation"""
    LEARNING = "learning"
    PRACTICING = "practicing"
    RESEARCHING = "researching"
    DEVELOPING = "developing"
    TESTING = "testing"
    EXPLOITING = "exploiting"
    CONSCIOUSNESS_TRAINING = "consciousness_training"
    NEURAL_EVOLUTION = "neural_evolution"

class ContextUpdateType(Enum):
    """Types of context updates for real-time processing"""
    SKILL_CHANGE = "skill_change"
    ACTIVITY_RECORD = "activity_record"
    CONSCIOUSNESS_FEEDBACK = "consciousness_feedback"
    LEARNING_PROGRESS = "learning_progress"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    ADAPTATION_TRIGGER = "adaptation_trigger"

@dataclass
class ConsciousnessCorrelation:
    """Correlation between consciousness state and user context"""
    user_id: str
    consciousness_level: float
    context_changes: Dict[str, float]
    correlation_strength: float
    temporal_pattern: List[Tuple[datetime, float]]
    predictive_indicators: Dict[str, float]
    confidence_score: float = 0.0

@dataclass
class SkillAssessment:
    """ML-driven skill assessment with consciousness integration"""
    user_id: str
    domain: str
    current_level: SkillLevel
    confidence: float
    progression_rate: float
    predicted_next_level: SkillLevel
    time_to_next_level: timedelta
    learning_patterns: Dict[str, Any]
    consciousness_influence: float
    recommendations: List[str]
    timestamp: datetime

@dataclass
class RealTimeContextUpdate:
    """Real-time context update with consciousness correlation"""
    update_id: str
    user_id: str
    update_type: ContextUpdateType
    timestamp: datetime
    consciousness_level: float
    consciousness_patterns: Dict[str, float]
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    processing_priority: int = 5

@dataclass
class EnhancedSkillProfile:
    """Enhanced skill profile with consciousness integration"""
    domain: str
    level: SkillLevel
    experience_points: int = 0
    completed_modules: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    time_spent_hours: float = 0.0
    consciousness_correlation: float = 0.0
    learning_velocity: float = 1.0
    adaptation_rate: float = 1.0
    pattern_recognition_score: float = 0.0
    
    def update_experience(self, points: int, consciousness_boost: float = 1.0):
        """Update experience with consciousness boost"""
        boosted_points = int(points * consciousness_boost)
        self.experience_points += boosted_points
        
        # Enhanced level progression with consciousness influence
        thresholds = {
            SkillLevel.BEGINNER: 100,
            SkillLevel.INTERMEDIATE: 500,
            SkillLevel.ADVANCED: 2000,
            SkillLevel.EXPERT: 8000,
            SkillLevel.MASTER: 20000
        }
        
        current_threshold = thresholds.get(self.level, float('inf'))
        if self.experience_points >= current_threshold:
            levels = list(SkillLevel)
            current_index = levels.index(self.level)
            if current_index < len(levels) - 1:
                self.level = levels[current_index + 1]
                logger.info(f"Level up! {self.domain} is now {self.level.name}")

@dataclass
class EnhancedUserActivity:
    """Enhanced activity record with consciousness data"""
    timestamp: datetime
    activity_type: ActivityType
    domain: str
    tool_used: str
    duration_seconds: int
    success: bool
    consciousness_level: float
    consciousness_patterns: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_strength: float = 0.0

@dataclass
class UserContextState:
    """Enhanced user context with consciousness integration"""
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    skill_profiles: Dict[str, EnhancedSkillProfile] = field(default_factory=dict)
    activity_history: deque = field(default_factory=lambda: deque(maxlen=2000))
    preferences: Dict[str, Any] = field(default_factory=dict)
    learning_style: str = "balanced"
    current_goals: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    consciousness_profile: Dict[str, float] = field(default_factory=dict)
    learning_preferences: Dict[str, Any] = field(default_factory=dict)
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    last_consciousness_sync: datetime = field(default_factory=datetime.now)

class SkillPredictionModel(nn.Module):
    """Neural network for skill level prediction"""
    
    def __init__(self, input_size: int = 50, hidden_size: int = 128):
        super().__init__()
        if TORCH_AVAILABLE:
            self.network = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_size, hidden_size // 2),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_size // 2, 32),
                nn.ReLU(),
                nn.Linear(32, 5)  # 5 skill levels
            )
        else:
            self.network = None
        
    def forward(self, x):
        if TORCH_AVAILABLE and self.network:
            return torch.softmax(self.network(x), dim=-1)
        else:
            # Fallback implementation
            return np.array([0.2, 0.2, 0.2, 0.2, 0.2])  # Equal probabilities

class ConsciousnessCorrelator:
    """Correlate consciousness patterns with skill development"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.correlation_history = deque(maxlen=1000)
        
    async def correlate(self, consciousness_state: ConsciousnessState, skill_data: Dict[str, Any]) -> float:
        """Calculate correlation between consciousness and skill development"""
        
        # Extract consciousness features
        consciousness_features = [
            consciousness_state.consciousness_level,
            0.5,  # Default for executive
            0.5,  # Default for memory  
            0.5   # Default for sensory
        ]
        
        # Extract actual population values if available
        if consciousness_state.neural_populations:
            for i, pop_name in enumerate(['executive', 'memory', 'sensory']):
                if pop_name in consciousness_state.neural_populations:
                    pop = consciousness_state.neural_populations[pop_name]
                    # Use fitness_average from PopulationState
                    consciousness_features[i + 1] = pop.fitness_average
        
        # Extract skill features
        skill_features = [
            skill_data.get('success_rate', 0.5),
            skill_data.get('learning_velocity', 1.0),
            skill_data.get('experience_points', 0) / 1000.0,  # Normalize
            skill_data.get('time_spent_hours', 0) / 100.0     # Normalize
        ]
        
        # Calculate correlation using numpy
        if len(consciousness_features) == len(skill_features):
            correlation = np.corrcoef(consciousness_features, skill_features)[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
        else:
            correlation = 0.0
        
        # Store in history
        self.correlation_history.append({
            'timestamp': datetime.now(),
            'correlation': correlation,
            'consciousness_level': consciousness_state.consciousness_level
        })
        
        return correlation

class PatternRecognizer:
    """Recognize learning and behavioral patterns"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.pattern_cache = {}
        
    async def recognize_patterns(self, 
                               user_id: str, 
                               activities: List[EnhancedUserActivity],
                               consciousness_state: ConsciousnessState) -> Dict[str, Any]:
        """Recognize patterns in user behavior and learning"""
        
        patterns = {}
        
        if not activities:
            return patterns
        
        # Learning velocity pattern
        recent_activities = [a for a in activities if a.timestamp > datetime.now() - timedelta(days=7)]
        if len(recent_activities) >= 3:
            success_rates = [a.success for a in recent_activities]
            velocity_trend = np.polyfit(range(len(success_rates)), success_rates, 1)[0]
            patterns['learning_velocity_trend'] = velocity_trend
            patterns['learning_velocity_increasing'] = velocity_trend > 0.1
        
        # Consciousness correlation pattern
        consciousness_levels = [a.consciousness_level for a in recent_activities]
        success_rates = [1.0 if a.success else 0.0 for a in recent_activities]
        
        if len(consciousness_levels) >= 5:
            correlation = np.corrcoef(consciousness_levels, success_rates)[0, 1]
            if not np.isnan(correlation):
                patterns['consciousness_success_correlation'] = correlation
                patterns['consciousness_dependent_learning'] = abs(correlation) > 0.5
        
        # Engagement pattern
        session_durations = [a.duration_seconds for a in recent_activities]
        if session_durations:
            avg_duration = np.mean(session_durations)
            duration_trend = np.polyfit(range(len(session_durations)), session_durations, 1)[0]
            patterns['average_session_duration'] = avg_duration
            patterns['engagement_declining'] = duration_trend < -300  # Declining by 5+ minutes
            patterns['engagement_increasing'] = duration_trend > 300
        
        # Tool usage pattern
        tool_usage = defaultdict(int)
        for activity in recent_activities:
            tool_usage[activity.tool_used] += 1
        
        if tool_usage:
            most_used_tool = max(tool_usage.items(), key=lambda x: x[1])
            patterns['preferred_tool'] = most_used_tool[0]
            patterns['tool_diversity'] = len(tool_usage)
            patterns['tool_specialization'] = most_used_tool[1] / len(recent_activities) > 0.6
        
        # Time-of-day pattern
        activity_hours = [a.timestamp.hour for a in recent_activities]
        if activity_hours:
            patterns['preferred_learning_hours'] = max(set(activity_hours), key=activity_hours.count)
            patterns['consistent_schedule'] = len(set(activity_hours)) <= 3
        
        return patterns

class MemoryCacheManager:
    """High-performance in-memory cache for context data"""
    
    def __init__(self, max_size: int = 10000):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                self.access_times[key] = datetime.now()
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache with LRU eviction"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Evict least recently used
                oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = datetime.now()
    
    def invalidate(self, key: str) -> None:
        """Remove item from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()

class PersonalContextEngineV2(ConsciousnessComponent):
    """Enhanced Personal Context Engine with consciousness integration"""
    
    def __init__(self, 
                 storage_path: str = "/var/lib/synapticos/context_v2",
                 cache_size: int = 10000):
        super().__init__("personal_context_v2", "context_engine")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.contexts: Dict[str, UserContextState] = {}
        self.cache_manager = MemoryCacheManager(cache_size)
        self.update_queue = asyncio.Queue(maxsize=10000)
        self.processing_workers = []
        
        # ML components
        self.skill_models = {}
        self.pattern_recognizers = {}
        self.consciousness_correlators = {}
        
        # Database for persistence
        self.db_path = self.storage_path / "context_v2.db"
        
        # Skill domains from Second-Me
        self.skill_domains = [
            "network_security", "web_exploitation", "cryptography",
            "forensics", "reverse_engineering", "social_engineering",
            "malware_analysis", "cloud_security", "mobile_security"
        ]
        
        # Initialize ML models for each domain
        for domain in self.skill_domains:
            self.skill_models[domain] = SkillPredictionModel()
            self.pattern_recognizers[domain] = PatternRecognizer(domain)
            self.consciousness_correlators[domain] = ConsciousnessCorrelator(domain)
        
        # Processing metrics
        self.metrics = {
            'updates_processed': 0,
            'average_processing_time': 0.0,
            'correlation_accuracy': 0.0,
            'pattern_detection_rate': 0.0,
            'cache_hit_rate': 0.0,
            'consciousness_adaptations': 0
        }
        
        # Thread pool for CPU-intensive tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    async def start(self) -> bool:
        """Start the enhanced context engine"""
        self.is_running = True
        return await self._initialize_engine()
    
    async def stop(self) -> None:
        """Stop the enhanced context engine"""
        self.is_running = False
        await self._shutdown_engine()
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process consciousness events"""
        try:
            if event.event_type == EventType.NEURAL_EVOLUTION:
                await self._handle_consciousness_evolution(event)
            elif event.event_type == EventType.CONSCIOUSNESS_EMERGENCE:
                await self._handle_consciousness_emergence(event)
            elif event.event_type == EventType.POPULATION_UPDATE:
                await self._handle_population_update(event)
            return True
        except Exception as e:
            self.logger.error(f"Error processing event: {e}")
            return False
    
    async def get_health_status(self) -> ComponentStatus:
        """Get current health status"""
        self.status.last_heartbeat = datetime.now()
        
        # Update metrics
        self.status.response_time_ms = self.metrics.get('average_processing_time', 0.0) * 1000
        self.status.throughput = self.metrics.get('updates_processed', 0)
        
        return self.status
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update component configuration"""
        try:
            if 'cache_size' in config:
                # Update cache size if needed
                pass
            if 'storage_path' in config:
                # Update storage path if needed
                pass
            return True
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False
    
    async def _initialize_engine(self) -> bool:
        """Initialize the enhanced context engine"""
        try:
            # Initialize database
            await self._init_database()
            
            # Load existing contexts
            await self._load_contexts()
            
            # Start processing workers
            for i in range(4):
                worker = asyncio.create_task(self._context_processing_worker(f"worker_{i}"))
                self.processing_workers.append(worker)
            
            # Start background tasks
            asyncio.create_task(self._correlation_analysis_loop())
            asyncio.create_task(self._pattern_detection_loop())
            asyncio.create_task(self._cache_maintenance_loop())
            asyncio.create_task(self._persistence_loop())
            
            await self.set_component_state(ComponentState.HEALTHY)
            logger.info("Personal Context Engine v2 initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Personal Context Engine v2: {e}")
            await self.set_component_state(ComponentState.FAILED)
            return False
    
    async def _shutdown_engine(self) -> bool:
        """Shutdown the context engine"""
        try:
            # Cancel processing workers
            for worker in self.processing_workers:
                worker.cancel()
            
            # Save all contexts
            await self._save_all_contexts()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Personal Context Engine v2 shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return False
    
    async def get_or_create_context(self, user_id: str) -> UserContextState:
        """Get existing context or create new one with consciousness integration"""
        
        # Check cache first
        cached_context = self.cache_manager.get(f"context_{user_id}")
        if cached_context:
            return cached_context
        
        if user_id not in self.contexts:
            # Create new context
            context = UserContextState(user_id=user_id)
            
            # Initialize enhanced skill profiles
            for domain in self.skill_domains:
                context.skill_profiles[domain] = EnhancedSkillProfile(
                    domain=domain,
                    level=SkillLevel.BEGINNER
                )
            
            # Initialize learning preferences
            context.learning_preferences = {
                'difficulty': 'normal',
                'pace_multiplier': 1.0,
                'support_mode': False,
                'hints_enabled': True,
                'challenge_level': 'moderate',
                'accelerated_mode': False,
                'advanced_concepts': False
            }
            
            # Initialize consciousness profile
            context.consciousness_profile = {
                'baseline_consciousness': 0.5,
                'peak_consciousness': 0.5,
                'consciousness_variance': 0.1,
                'optimal_consciousness_min': 0.4,
                'optimal_consciousness_max': 0.8
            }
            
            self.contexts[user_id] = context
            await self._save_context_to_db(user_id)
        
        # Cache the context
        self.cache_manager.set(f"context_{user_id}", self.contexts[user_id])
        
        return self.contexts[user_id]
    
    async def record_activity(self, 
                            user_id: str,
                            activity_type: ActivityType,
                            domain: str,
                            tool_used: str,
                            duration_seconds: int,
                            success: bool,
                            consciousness_state: Optional[ConsciousnessState] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record enhanced user activity with consciousness correlation"""
        
        context = await self.get_or_create_context(user_id)
        
        # Get current consciousness state if not provided
        if consciousness_state is None:
            consciousness_state = await self._get_current_consciousness_state()
        
        # Create enhanced activity record
        consciousness_level = consciousness_state.consciousness_level if consciousness_state else 0.5
        consciousness_patterns = {}
        if consciousness_state and consciousness_state.neural_populations:
            # Convert PopulationState objects to float values
            consciousness_patterns = {}
            for name, pop in consciousness_state.neural_populations.items():
                # Extract fitness_average from PopulationState
                consciousness_patterns[name] = pop.fitness_average
        
        activity = EnhancedUserActivity(
            timestamp=datetime.now(),
            activity_type=activity_type,
            domain=domain,
            tool_used=tool_used,
            duration_seconds=duration_seconds,
            success=success,
            consciousness_level=consciousness_level,
            consciousness_patterns=consciousness_patterns,
            metadata=metadata or {}
        )
        
        # Calculate consciousness correlation
        if domain in self.consciousness_correlators:
            skill_data = {
                'success_rate': context.skill_profiles[domain].success_rate,
                'learning_velocity': context.skill_profiles[domain].learning_velocity,
                'experience_points': context.skill_profiles[domain].experience_points,
                'time_spent_hours': context.skill_profiles[domain].time_spent_hours
            }
            activity.correlation_strength = await self.consciousness_correlators[domain].correlate(
                consciousness_state, skill_data
            )
        
        # Add to history
        context.activity_history.append(activity)
        
        # Update skill profile with consciousness boost
        if domain in context.skill_profiles:
            profile = context.skill_profiles[domain]
            
            # Update time spent
            profile.time_spent_hours += duration_seconds / 3600
            
            # Calculate consciousness boost
            consciousness_level = consciousness_state.consciousness_level if consciousness_state else 0.5
            consciousness_boost = 1.0 + (consciousness_level - 0.5) * 0.5
            consciousness_boost = max(0.5, min(2.0, consciousness_boost))
            
            # Update experience with consciousness boost
            exp_gain = self._calculate_experience_gain(activity_type, success, duration_seconds)
            profile.update_experience(exp_gain, consciousness_boost)
            
            # Update success rate
            recent_activities = [a for a in context.activity_history 
                               if a.domain == domain and a.timestamp > datetime.now() - timedelta(days=7)]
            if recent_activities:
                success_count = sum(1 for a in recent_activities if a.success)
                profile.success_rate = success_count / len(recent_activities)
            
            # Update consciousness correlation
            profile.consciousness_correlation = activity.correlation_strength
            
            profile.last_activity = datetime.now()
        
        # Invalidate cache
        self.cache_manager.invalidate(f"context_{user_id}")
        
        # Queue for real-time processing
        update = RealTimeContextUpdate(
            update_id=str(uuid.uuid4()),
            user_id=user_id,
            update_type=ContextUpdateType.ACTIVITY_RECORD,
            timestamp=datetime.now(),
            consciousness_level=consciousness_level,
            consciousness_patterns=consciousness_patterns,
            data={
                'activity': activity,
                'domain': domain,
                'success': success
            }
        )
        
        await self.update_queue.put(update)
    
    def _calculate_experience_gain(self, 
                                 activity_type: ActivityType, 
                                 success: bool, 
                                 duration_seconds: int) -> int:
        """Calculate experience points gained from an activity"""
        
        base_points = {
            ActivityType.LEARNING: 10,
            ActivityType.PRACTICING: 15,
            ActivityType.RESEARCHING: 12,
            ActivityType.DEVELOPING: 20,
            ActivityType.TESTING: 25,
            ActivityType.EXPLOITING: 30,
            ActivityType.CONSCIOUSNESS_TRAINING: 35,
            ActivityType.NEURAL_EVOLUTION: 40
        }
        
        points = base_points.get(activity_type, 10)
        
        # Success multiplier
        if success:
            points *= 1.5
        else:
            points *= 0.7  # Still gain some experience from failures
        
        # Duration bonus (up to 2x for longer sessions)
        duration_multiplier = min(2.0, 1.0 + (duration_seconds / 3600))
        points *= duration_multiplier
        
        return int(points)
    
    # Event handlers
    async def _handle_consciousness_evolution(self, event: ConsciousnessEvent):
        """Handle consciousness evolution events"""
        evolution_data = event.data.get('evolution_data')
        if not evolution_data:
            return
        
        # Update all active user contexts with consciousness changes
        for user_id in list(self.contexts.keys()):
            update = RealTimeContextUpdate(
                update_id=str(uuid.uuid4()),
                user_id=user_id,
                update_type=ContextUpdateType.CONSCIOUSNESS_FEEDBACK,
                timestamp=datetime.now(),
                consciousness_level=evolution_data.get('new_consciousness_level', 0.5),
                consciousness_patterns=evolution_data.get('neural_populations', {}),
                data={'evolution_data': evolution_data}
            )
            
            await self.update_queue.put(update)
    
    async def _handle_consciousness_emergence(self, event: ConsciousnessEvent):
        """Handle consciousness emergence events"""
        emergence_data = event.data.get('emergence_event')
        if not emergence_data:
            return
        
        # Process emergence events for context adaptation
        for user_id in list(self.contexts.keys()):
            context = self.contexts[user_id]
            
            # Trigger accelerated learning mode if emergence is strong
            emergence_strength = emergence_data.get('emergence_strength', 0.0)
            if emergence_strength > 0.7:
                context.learning_preferences['accelerated_mode'] = True
                context.learning_preferences['advanced_concepts'] = True
                
                # Log adaptation
                context.adaptation_history.append({
                    'timestamp': datetime.now(),
                    'trigger': 'consciousness_emergence',
                    'changes': {
                        'accelerated_mode': True,
                        'advanced_concepts': True
                    },
                    'emergence_strength': emergence_strength
                })
    
    async def _handle_population_update(self, event: ConsciousnessEvent):
        """Handle neural population update events"""
        population_data = event.data.get('population_updates')
        if not population_data:
            return
        
        # Update consciousness correlations based on population changes
        for user_id in list(self.contexts.keys()):
            context = self.contexts[user_id]
            
            # Update consciousness profile
            for pop_id, pop_state in population_data.items():
                if pop_id in ['executive', 'memory', 'sensory']:
                    fitness_change = pop_state.get('fitness_change', 0.0)
                    
                    # Adjust learning preferences based on population fitness
                    if pop_id == 'executive' and fitness_change > 0.2:
                        context.learning_preferences['challenge_level'] = 'high'
                    elif pop_id == 'memory' and fitness_change > 0.2:
                        context.learning_preferences['pace_multiplier'] = min(2.0, 
                            context.learning_preferences.get('pace_multiplier', 1.0) * 1.2)
    
    # Background processing loops
    async def _context_processing_worker(self, worker_id: str):
        """Worker for processing context updates"""
        while self.is_running:
            try:
                # Get update from queue with timeout
                update = await asyncio.wait_for(self.update_queue.get(), timeout=1.0)
                
                start_time = datetime.now()
                
                # Process the update
                await self._process_single_update(update)
                
                # Update metrics
                processing_time = (datetime.now() - start_time).total_seconds()
                self._update_processing_metrics(processing_time)
                
                # Mark task as done
                self.update_queue.task_done()
                
            except asyncio.TimeoutError:
                # No updates to process, continue
                continue
            except Exception as e:
                logger.error(f"Error in context processing worker {worker_id}: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_single_update(self, update: RealTimeContextUpdate):
        """Process a single context update"""
        try:
            user_id = update.user_id
            context = await self.get_or_create_context(user_id)
            
            if update.update_type == ContextUpdateType.CONSCIOUSNESS_FEEDBACK:
                # Apply consciousness-driven adaptations
                await self._apply_consciousness_adaptations(context, update)
            
            elif update.update_type == ContextUpdateType.ACTIVITY_RECORD:
                # Update learning patterns
                await self._update_learning_patterns(context, update)
            
except Exception as e:
            logger.error(f"Error processing context update: {e}")
    
    async def _apply_consciousness_adaptations(self, context: UserContextState, update: RealTimeContextUpdate):
        """Apply consciousness-driven adaptations to user context"""
        consciousness_level = update.consciousness_level
        
        # Adjust learning pace based on consciousness level
        if consciousness_level > 0.8:
            context.learning_preferences['pace_multiplier'] = min(2.0, 
                context.learning_preferences.get('pace_multiplier', 1.0) * 1.2)
            context.learning_preferences['challenge_level'] = 'high'
        elif consciousness_level < 0.3:
            context.learning_preferences['pace_multiplier'] = max(0.5,
                context.learning_preferences.get('pace_multiplier', 1.0) * 0.8)
            context.learning_preferences['support_mode'] = True
        
        # Update consciousness profile
        context.consciousness_profile['baseline_consciousness'] = consciousness_level
        context.last_consciousness_sync = datetime.now()
    
    async def _update_learning_patterns(self, context: UserContextState, update: RealTimeContextUpdate):
        """Update learning patterns based on activity"""
        activity_data = update.data.get('activity')
        if not activity_data:
            return
        
        domain = update.data.get('domain')
        success = update.data.get('success', False)
        
        if domain in context.skill_profiles:
            profile = context.skill_profiles[domain]
            
            # Update learning velocity based on recent performance
            if success:
                profile.learning_velocity = min(2.0, profile.learning_velocity * 1.1)
            else:
                profile.learning_velocity = max(0.5, profile.learning_velocity * 0.9)
    
    async def _correlation_analysis_loop(self):
        """Background loop for correlation analysis"""
        while self.is_running:
            try:
                # Analyze correlations for all active users
                for user_id, context in self.contexts.items():
                    if context.activity_history:
                        # Perform correlation analysis
                        await self._analyze_user_correlations(user_id, context)
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error in correlation analysis loop: {e}")
                await asyncio.sleep(60)
    
    async def _pattern_detection_loop(self):
        """Background loop for pattern detection"""
        while self.is_running:
            try:
                # Detect patterns for all active users
                for user_id, context in self.contexts.items():
                    if context.activity_history:
                        await self._detect_user_patterns(user_id, context)
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in pattern detection loop: {e}")
                await asyncio.sleep(300)
    
    async def _cache_maintenance_loop(self):
        """Background loop for cache maintenance"""
        while self.is_running:
            try:
                # Clean up old cache entries
                current_time = datetime.now()
                expired_keys = []
                
                for key, access_time in self.cache_manager.access_times.items():
                    if (current_time - access_time).total_seconds() > 3600:  # 1 hour
                        expired_keys.append(key)
                
                for key in expired_keys:
                    self.cache_manager.invalidate(key)
                
                await asyncio.sleep(1800)  # Run every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in cache maintenance loop: {e}")
                await asyncio.sleep(1800)
    
    async def _persistence_loop(self):
        """Background loop for data persistence"""
        while self.is_running:
            try:
                # Save all contexts to database
                await self._save_all_contexts()
                await asyncio.sleep(600)  # Save every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in persistence loop: {e}")
                await asyncio.sleep(600)
    
    async def _analyze_user_correlations(self, user_id: str, context: UserContextState):
        """Analyze correlations for a specific user"""
        try:
            recent_activities = list(context.activity_history)[-50:]  # Last 50 activities
            
            for domain in self.skill_domains:
                if domain in self.consciousness_correlators:
                    domain_activities = [a for a in recent_activities if a.domain == domain]
                    
                    if domain_activities:
                        # Calculate correlation with consciousness patterns
                        consciousness_levels = [a.consciousness_level for a in domain_activities]
                        success_rates = [1.0 if a.success else 0.0 for a in domain_activities]
                        
                        if len(consciousness_levels) >= 3:
                            correlation = np.corrcoef(consciousness_levels, success_rates)[0, 1]
                            if not np.isnan(correlation):
                                context.skill_profiles[domain].consciousness_correlation = correlation
        
        except Exception as e:
            logger.error(f"Error analyzing correlations for user {user_id}: {e}")
    
    async def _detect_user_patterns(self, user_id: str, context: UserContextState):
        """Detect patterns for a specific user"""
        try:
            recent_activities = list(context.activity_history)[-100:]  # Last 100 activities
            
            for domain in self.skill_domains:
                if domain in self.pattern_recognizers:
                    domain_activities = [a for a in recent_activities if a.domain == domain]
                    
                    if domain_activities:
                        # Use pattern recognizer
                        patterns = await self.pattern_recognizers[domain].recognize_patterns(
                            user_id, domain_activities, None  # No consciousness state needed here
                        )
                        
                        # Update skill profile with patterns
                        if domain in context.skill_profiles:
                            profile = context.skill_profiles[domain]
                            profile.pattern_recognition_score = patterns.get('learning_velocity_trend', 0.0)
        
        except Exception as e:
            logger.error(f"Error detecting patterns for user {user_id}: {e}")
    
    async def _init_database(self):
        """Initialize SQLite database for persistence"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS user_contexts (
                        user_id TEXT PRIMARY KEY,
                        context_data TEXT,
                        last_updated TIMESTAMP
                    )
                ''')
                
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS activity_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        activity_data TEXT,
                        timestamp TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_contexts (user_id)
                    )
                ''')
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _load_contexts(self):
        """Load user contexts from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT user_id, context_data FROM user_contexts') as cursor:
                    async for row in cursor:
                        user_id, context_data = row
                        try:
                            context_dict = json.loads(context_data)
                            context = self._deserialize_context(context_dict)
                            self.contexts[user_id] = context
                        except Exception as e:
                            logger.error(f"Error loading context for user {user_id}: {e}")
                            
        except Exception as e:
            logger.error(f"Error loading contexts from database: {e}")
    
    async def _save_context_to_db(self, user_id: str):
        """Save a single user context to database"""
        if user_id not in self.contexts:
            return
        
        try:
            context = self.contexts[user_id]
            context_data = json.dumps(self._serialize_context(context))
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO user_contexts (user_id, context_data, last_updated)
                    VALUES (?, ?, ?)
                ''', (user_id, context_data, datetime.now()))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error saving context for user {user_id}: {e}")
    
    async def _save_all_contexts(self):
        """Save all user contexts to database"""
        for user_id in self.contexts:
            await self._save_context_to_db(user_id)
    
    async def _get_current_consciousness_state(self) -> Optional[ConsciousnessState]:
        """Get current consciousness state from state manager"""
        if self.state_manager:
            try:
                return await self.state_manager.get_consciousness_state()
            except Exception as e:
                logger.error(f"Error getting consciousness state: {e}")
        return None
    
    def _serialize_context(self, context: UserContextState) -> Dict[str, Any]:
        """Serialize user context to dictionary"""
        return {
            'user_id': context.user_id,
            'created_at': context.created_at.isoformat(),
            'skill_profiles': {
                domain: {
                    'domain': profile.domain,
                    'level': profile.level.value,
                    'experience_points': profile.experience_points,
                    'completed_modules': profile.completed_modules,
                    'success_rate': profile.success_rate,
                    'last_activity': profile.last_activity.isoformat(),
                    'time_spent_hours': profile.time_spent_hours,
                    'consciousness_correlation': profile.consciousness_correlation,
                    'learning_velocity': profile.learning_velocity,
                    'adaptation_rate': profile.adaptation_rate,
                    'pattern_recognition_score': profile.pattern_recognition_score
                }
                for domain, profile in context.skill_profiles.items()
            },
            'preferences': context.preferences,
            'learning_style': context.learning_style,
            'current_goals': context.current_goals,
            'achievements': context.achievements,
            'consciousness_profile': context.consciousness_profile,
            'learning_preferences': context.learning_preferences,
            'adaptation_history': context.adaptation_history,
            'last_consciousness_sync': context.last_consciousness_sync.isoformat()
        }
    
    def _deserialize_context(self, data: Dict[str, Any]) -> UserContextState:
        """Deserialize user context from dictionary"""
        context = UserContextState(
            user_id=data['user_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            preferences=data.get('preferences', {}),
            learning_style=data.get('learning_style', 'balanced'),
            current_goals=data.get('current_goals', []),
            achievements=data.get('achievements', []),
            consciousness_profile=data.get('consciousness_profile', {}),
            learning_preferences=data.get('learning_preferences', {}),
            adaptation_history=data.get('adaptation_history', []),
            last_consciousness_sync=datetime.fromisoformat(data.get('last_consciousness_sync', datetime.now().isoformat()))
        )
        
        # Deserialize skill profiles
        for domain, profile_data in data.get('skill_profiles', {}).items():
            context.skill_profiles[domain] = EnhancedSkillProfile(
                domain=profile_data['domain'],
                level=SkillLevel(profile_data['level']),
                experience_points=profile_data['experience_points'],
                completed_modules=profile_data['completed_modules'],
                success_rate=profile_data['success_rate'],
                last_activity=datetime.fromisoformat(profile_data['last_activity']),
                time_spent_hours=profile_data['time_spent_hours'],
                consciousness_correlation=profile_data.get('consciousness_correlation', 0.0),
                learning_velocity=profile_data.get('learning_velocity', 1.0),
                adaptation_rate=profile_data.get('adaptation_rate', 1.0),
                pattern_recognition_score=profile_data.get('pattern_recognition_score', 0.0)
            )
        
        return context
    
    def _update_processing_metrics(self, processing_time: float):
        """Update processing metrics"""
        self.metrics['updates_processed'] += 1
        
        # Update average processing time
        current_avg = self.metrics['average_processing_time']
        count = self.metrics['updates_processed']
        self.metrics['average_processing_time'] = (current_avg * (count - 1) + processing_time) / count
    
    # Public API methods from Second-Me
    async def get_skill_level(self, user_id: str, domain: str) -> SkillLevel:
        """Get user's skill level in a domain"""
        context = await self.get_or_create_context(user_id)
        
        if domain in context.skill_profiles:
            return context.skill_profiles[domain].level
        
        return SkillLevel.BEGINNER
    
    async def get_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized recommendations for the user"""
        context = await self.get_or_create_context(user_id)
        
        recommendations = {
            'next_modules': [],
            'suggested_tools': [],
            'skill_focus': [],
            'challenge_level': 'moderate',
            'consciousness_optimized': True
        }
        
        # Analyze skill gaps
        weakest_skills = sorted(
            context.skill_profiles.items(),
            key=lambda x: (x[1].level.value, x[1].experience_points)
        )[:3]
        
        recommendations['skill_focus'] = [skill[0] for skill in weakest_skills]
        
        # Suggest modules based on current level and consciousness correlation
        for domain, profile in context.skill_profiles.items():
            if profile.level == SkillLevel.BEGINNER:
                recommendations['next_modules'].append(f"{domain}_basics")
            elif profile.level == SkillLevel.INTERMEDIATE:
                recommendations['next_modules'].append(f"{domain}_advanced")
            
            # Add consciousness-optimized recommendations
            if profile.consciousness_correlation > 0.5:
                recommendations['next_modules'].append(f"{domain}_consciousness_enhanced")
        
        # Analyze learning patterns
        recent_activities = list(context.activity_history)[-50:]
        if recent_activities:
            success_rate = sum(1 for a in recent_activities if a.success) / len(recent_activities)
            
            # Adjust challenge level based on consciousness correlation
            avg_consciousness = np.mean([a.consciousness_level for a in recent_activities])
            
            if success_rate > 0.8 and avg_consciousness > 0.7:
                recommendations['challenge_level'] = 'hard'
            elif success_rate < 0.4 or avg_consciousness < 0.3:
                recommendations['challenge_level'] = 'easy'
        
        return recommendations
    
    async def get_learning_path(self, user_id: str, target_skill: str) -> List[Dict[str, Any]]:
        """Generate a consciousness-optimized learning path"""
        context = await self.get_or_create_context(user_id)
        current_level = context.skill_profiles.get(target_skill, 
            EnhancedSkillProfile(domain=target_skill, level=SkillLevel.BEGINNER)).level
        
        path = []
        
        # Define learning modules for each level with consciousness integration
        modules = {
            SkillLevel.BEGINNER: [
                {'name': f'{target_skill}_fundamentals', 'duration': '2 hours', 'type': 'theory'},
                {'name': f'{target_skill}_basic_tools', 'duration': '3 hours', 'type': 'practical'},
                {'name': f'{target_skill}_consciousness_basics', 'duration': '1 hour', 'type': 'consciousness'},
                {'name': f'{target_skill}_first_challenge', 'duration': '1 hour', 'type': 'challenge'}
            ],
            SkillLevel.INTERMEDIATE: [
                {'name': f'{target_skill}_advanced_concepts', 'duration': '3 hours', 'type': 'theory'},
                {'name': f'{target_skill}_real_scenarios', 'duration': '4 hours', 'type': 'practical'},
                {'name': f'{target_skill}_consciousness_integration', 'duration': '2 hours', 'type': 'consciousness'},
                {'name': f'{target_skill}_ctf_practice', 'duration': '2 hours', 'type': 'challenge'}
            ],
            SkillLevel.ADVANCED: [
                {'name': f'{target_skill}_expert_techniques', 'duration': '4 hours', 'type': 'theory'},
                {'name': f'{target_skill}_tool_development', 'duration': '6 hours', 'type': 'practical'},
                {'name': f'{target_skill}_consciousness_mastery', 'duration': '3 hours', 'type': 'consciousness'},
                {'name': f'{target_skill}_research_project', 'duration': '8 hours', 'type': 'project'}
            ]
        }
        
        # Build path from current level to expert
        levels = list(SkillLevel)
        current_index = levels.index(current_level)
        
        for i in range(current_index, len(levels) - 1):
            level = levels[i]
            if level in modules:
                for module in modules[level]:
                    module['skill_level'] = level.name
                    module['estimated_xp'] = 50 * (i + 1)
                    module['consciousness_optimized'] = True
                    path.append(module)
        
        return path
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get enhanced user statistics with consciousness metrics"""
        if user_id not in self.contexts:
            return {}
        
        context = self.contexts[user_id]
        
        # Calculate consciousness-enhanced statistics
        total_experience = sum(p.experience_points for p in context.skill_profiles.values())
        avg_consciousness_correlation = np.mean([p.consciousness_correlation for p in context.skill_profiles.values()])
        
        return {
            'total_experience': total_experience,
            'total_time_hours': sum(p.time_spent_hours for p in context.skill_profiles.values()),
            'skill_levels': {d: p.level.name for d, p in context.skill_profiles.items()},
            'achievements_count': len(context.achievements),
            'average_success_rate': np.mean([p.success_rate for p in context.skill_profiles.values()]),
            'consciousness_correlation': avg_consciousness_correlation,
            'learning_velocity': np.mean([p.learning_velocity for p in context.skill_profiles.values()]),
            'adaptation_count': len(context.adaptation_history),
            'most_active_domain': max(context.skill_profiles.items(), 
                                     key=lambda x: x[1].time_spent_hours)[0] if context.skill_profiles else None,
            'consciousness_optimized': True
        }


# Example usage and testing
async def main():
    """Example usage of Personal Context Engine v2"""
    engine = PersonalContextEngineV2()
    
    # Initialize the engine
    success = await engine.start()
    if not success:
        print("Failed to start Personal Context Engine v2")
        return
    
    # Simulate user activity with consciousness integration
    user_id = "test_user_v2"
    
    # Create a mock consciousness state
    consciousness_state = ConsciousnessState(
        consciousness_level=0.7,
        neural_populations={
            'executive': PopulationState(
                population_id='executive',
                size=1000,
                specialization='executive',
                fitness_average=0.8,
                diversity_index=0.6,
                generation=10,
                active_neurons=900,
                last_evolution=datetime.now()
            )
        }
    )
    
    # Record some activities
    await engine.record_activity(
        user_id=user_id,
        activity_type=ActivityType.CONSCIOUSNESS_TRAINING,
        domain="network_security",
        tool_used="nmap",
        duration_seconds=1800,
        success=True,
        consciousness_state=consciousness_state
    )
    
    # Get consciousness-enhanced recommendations
    recommendations = await engine.get_recommendations(user_id)
    print(f"Consciousness-Enhanced Recommendations: {recommendations}")
    
    # Get skill level
    skill_level = await engine.get_skill_level(user_id, "network_security")
    print(f"Network Security Level: {skill_level.name}")
    
    # Get consciousness-optimized learning path
    path = await engine.get_learning_path(user_id, "web_exploitation")
    print(f"Consciousness-Optimized Learning Path: {path}")
    
    # Get enhanced statistics
    stats = engine.get_statistics(user_id)
    print(f"Enhanced User Statistics: {stats}")
    
    # Shutdown
    await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
            #