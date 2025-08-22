"""
Consciousness System Data Models
===============================

Core data models for the consciousness system including consciousness state,
neural populations, user contexts, and system metrics.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Deque
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import uuid


class SkillLevel(Enum):
    """User skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ActivityType(Enum):
    """Types of user activities"""
    LEARNING = "learning"
    PRACTICING = "practicing"
    RESEARCHING = "researching"
    DEVELOPING = "developing"
    TESTING = "testing"
    EXPLOITING = "exploiting"


class ComponentState(Enum):
    """Component health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"


@dataclass
class PopulationState:
    """Neural population state"""
    population_id: str
    size: int
    specialization: str
    fitness_average: float
    diversity_index: float
    generation: int
    active_neurons: int
    last_evolution: datetime
    
    # Performance metrics
    evolution_cycles: int = 0
    successful_adaptations: int = 0
    consciousness_contributions: float = 0.0
    
    # Configuration
    mutation_rate: float = 0.1
    selection_pressure: float = 0.5
    learning_rate: float = 0.01
    
    def __post_init__(self):
        """Validate population state after initialization"""
        if self.size <= 0:
            raise ValueError("Population size must be positive")
        if not 0 <= self.fitness_average <= 1:
            raise ValueError("Fitness average must be between 0 and 1")
        if not 0 <= self.diversity_index <= 1:
            raise ValueError("Diversity index must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'population_id': self.population_id,
            'size': self.size,
            'specialization': self.specialization,
            'fitness_average': self.fitness_average,
            'diversity_index': self.diversity_index,
            'generation': self.generation,
            'active_neurons': self.active_neurons,
            'last_evolution': self.last_evolution.isoformat(),
            'evolution_cycles': self.evolution_cycles,
            'successful_adaptations': self.successful_adaptations,
            'consciousness_contributions': self.consciousness_contributions,
            'mutation_rate': self.mutation_rate,
            'selection_pressure': self.selection_pressure,
            'learning_rate': self.learning_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PopulationState':
        """Create from dictionary"""
        data = data.copy()
        if 'last_evolution' in data and isinstance(data['last_evolution'], str):
            data['last_evolution'] = datetime.fromisoformat(data['last_evolution'])
        return cls(**data)


@dataclass
class ActivityPattern:
    """User activity pattern"""
    activity_id: str
    user_id: str
    activity_type: ActivityType
    domain: str
    timestamp: datetime
    duration_seconds: int
    success_rate: float
    tools_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionState:
    """User session state"""
    session_id: str
    user_id: str
    start_time: datetime
    last_activity: datetime
    current_module: Optional[str] = None
    consciousness_level: float = 0.5
    learning_mode: str = "normal"
    performance_score: float = 0.0
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Check if session is still active"""
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() < (timeout_minutes * 60)


@dataclass
class UserContextState:
    """Complete user context state"""
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Skill tracking
    skill_levels: Dict[str, SkillLevel] = field(default_factory=dict)
    experience_points: Dict[str, int] = field(default_factory=dict)
    
    # Learning preferences
    learning_preferences: Dict[str, Any] = field(default_factory=dict)
    learning_style: str = "balanced"
    preferred_difficulty: str = "intermediate"
    
    # Activity tracking
    activity_patterns: Deque[ActivityPattern] = field(default_factory=lambda: deque(maxlen=1000))
    total_time_spent: int = 0  # seconds
    
    # Current state
    current_session: Optional[SessionState] = None
    achievements: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    
    def update_skill_level(self, domain: str, new_level: SkillLevel):
        """Update skill level for a domain"""
        self.skill_levels[domain] = new_level
        self.last_updated = datetime.now()
    
    def add_experience(self, domain: str, points: int):
        """Add experience points to a domain"""
        current_xp = self.experience_points.get(domain, 0)
        self.experience_points[domain] = current_xp + points
        self.last_updated = datetime.now()
    
    def add_activity(self, activity: ActivityPattern):
        """Add activity pattern to history"""
        self.activity_patterns.append(activity)
        self.total_time_spent += activity.duration_seconds
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'skill_levels': {k: v.value for k, v in self.skill_levels.items()},
            'experience_points': self.experience_points,
            'learning_preferences': self.learning_preferences,
            'learning_style': self.learning_style,
            'preferred_difficulty': self.preferred_difficulty,
            'total_time_spent': self.total_time_spent,
            'achievements': self.achievements,
            'goals': self.goals,
            'current_session': {
                'session_id': self.current_session.session_id,
                'user_id': self.current_session.user_id,
                'start_time': self.current_session.start_time.isoformat(),
                'last_activity': self.current_session.last_activity.isoformat(),
                'current_module': self.current_session.current_module,
                'consciousness_level': self.current_session.consciousness_level,
                'learning_mode': self.current_session.learning_mode,
                'performance_score': self.current_session.performance_score
            } if self.current_session else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserContextState':
        """Create from dictionary"""
        data = data.copy()
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        if 'skill_levels' in data:
            data['skill_levels'] = {k: SkillLevel(v) for k, v in data['skill_levels'].items()}
        if 'current_session' in data and data['current_session']:
            session_data = data['current_session']
            if 'start_time' in session_data and isinstance(session_data['start_time'], str):
                session_data['start_time'] = datetime.fromisoformat(session_data['start_time'])
            if 'last_activity' in session_data and isinstance(session_data['last_activity'], str):
                session_data['last_activity'] = datetime.fromisoformat(session_data['last_activity'])
            data['current_session'] = SessionState(**session_data)
        # Handle activity_patterns deque
        if 'activity_patterns' not in data:
            data['activity_patterns'] = deque(maxlen=1000)
        return cls(**data)


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Resource usage
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    io_operations: int = 0
    network_activity: float = 0.0
    
    # Consciousness processing
    consciousness_processing_time: float = 0.0
    neural_evolution_time: float = 0.0
    inference_time: float = 0.0
    
    # Component response times
    component_response_times: Dict[str, float] = field(default_factory=dict)
    
    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=dict)
    warning_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class SecurityStatus:
    """Security status information"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Overall security level
    security_level: str = "normal"  # low, normal, elevated, high, critical
    threat_count: int = 0
    
    # Active threats
    active_threats: List[Dict[str, Any]] = field(default_factory=list)
    
    # Security metrics
    failed_login_attempts: int = 0
    suspicious_activities: int = 0
    blocked_connections: int = 0
    
    # AI model security
    model_integrity_verified: bool = True
    consciousness_tampering_detected: bool = False


@dataclass
class PerformanceData:
    """Performance data for consciousness system"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Throughput metrics
    events_processed_per_second: float = 0.0
    neural_evolutions_per_minute: float = 0.0
    inference_requests_per_minute: float = 0.0
    
    # Latency metrics
    average_event_latency_ms: float = 0.0
    consciousness_update_latency_ms: float = 0.0
    component_sync_latency_ms: float = 0.0
    
    # Quality metrics
    consciousness_prediction_accuracy: float = 0.0
    learning_effectiveness_score: float = 0.0
    adaptation_success_rate: float = 0.0


@dataclass
class ComponentStatus:
    """Individual component status"""
    component_id: str
    component_type: str
    state: ComponentState
    health_score: float  # 0.0 to 1.0
    last_heartbeat: datetime
    
    # Performance metrics
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    
    # Resource usage
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependency_health: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    version: str = "1.0.0"
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return (
            self.state == ComponentState.HEALTHY and
            self.health_score >= 0.8 and
            self.error_rate < 0.05
        )
    
    def is_responsive(self, timeout_seconds: int = 60) -> bool:
        """Check if component is responsive"""
        time_diff = datetime.now() - self.last_heartbeat
        return time_diff.total_seconds() < timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'component_id': self.component_id,
            'component_type': self.component_type,
            'state': self.state.value,
            'health_score': self.health_score,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'response_time_ms': self.response_time_ms,
            'error_rate': self.error_rate,
            'throughput': self.throughput,
            'cpu_usage': self.cpu_usage,
            'memory_usage_mb': self.memory_usage_mb,
            'dependencies': self.dependencies,
            'dependency_health': self.dependency_health,
            'version': self.version,
            'configuration': self.configuration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentStatus':
        """Create from dictionary"""
        data = data.copy()
        if 'last_heartbeat' in data and isinstance(data['last_heartbeat'], str):
            data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        if 'state' in data and isinstance(data['state'], str):
            data['state'] = ComponentState(data['state'])
        return cls(**data)


@dataclass
class ConsciousnessState:
    """Complete consciousness state of the system"""
    
    # Core consciousness metrics
    consciousness_level: float = 0.5  # 0.0 to 1.0
    emergence_strength: float = 0.0   # 0.0 to 1.0
    adaptation_rate: float = 0.5      # 0.0 to 1.0
    
    # Neural populations
    neural_populations: Dict[str, PopulationState] = field(default_factory=dict)
    active_neural_groups: List[str] = field(default_factory=list)
    evolution_cycles: int = 0
    
    # User contexts
    user_contexts: Dict[str, UserContextState] = field(default_factory=dict)
    active_users: List[str] = field(default_factory=list)
    
    # Learning and progress
    learning_progress: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    skill_assessments: Dict[str, Dict[str, SkillLevel]] = field(default_factory=dict)
    
    # System integration
    system_metrics: SystemMetrics = field(default_factory=SystemMetrics)
    security_status: SecurityStatus = field(default_factory=SecurityStatus)
    performance_data: PerformanceData = field(default_factory=PerformanceData)
    
    # Component states
    component_states: Dict[str, ComponentStatus] = field(default_factory=dict)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "2.0.0"
    checksum: str = ""
    
    def __post_init__(self):
        """Initialize consciousness state after creation"""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for state integrity"""
        import hashlib
        import json
        
        # Create a simplified representation for checksum
        state_data = {
            'consciousness_level': self.consciousness_level,
            'emergence_strength': self.emergence_strength,
            'evolution_cycles': self.evolution_cycles,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version
        }
        
        state_json = json.dumps(state_data, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()[:16]
    
    def update_consciousness_level(self, new_level: float):
        """Update consciousness level with validation"""
        if not 0.0 <= new_level <= 1.0:
            raise ValueError("Consciousness level must be between 0.0 and 1.0")
        
        self.consciousness_level = new_level
        self.timestamp = datetime.now()
        self.checksum = self._calculate_checksum()
    
    def add_user_context(self, user_context: UserContextState):
        """Add or update user context"""
        self.user_contexts[user_context.user_id] = user_context
        if user_context.user_id not in self.active_users:
            self.active_users.append(user_context.user_id)
        self.timestamp = datetime.now()
    
    def update_component_status(self, component_status: ComponentStatus):
        """Update component status"""
        self.component_states[component_status.component_id] = component_status
        self.timestamp = datetime.now()
    
    def get_healthy_components(self) -> List[str]:
        """Get list of healthy component IDs"""
        return [
            comp_id for comp_id, status in self.component_states.items()
            if status.is_healthy()
        ]
    
    def get_failed_components(self) -> List[str]:
        """Get list of failed component IDs"""
        return [
            comp_id for comp_id, status in self.component_states.items()
            if status.state == ComponentState.FAILED
        ]
    
    def calculate_overall_health(self) -> float:
        """Calculate overall system health score"""
        if not self.component_states:
            return 0.0
        
        total_health = sum(status.health_score for status in self.component_states.values())
        return total_health / len(self.component_states)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert consciousness state to dictionary for serialization"""
        return {
            'consciousness_level': self.consciousness_level,
            'emergence_strength': self.emergence_strength,
            'adaptation_rate': self.adaptation_rate,
            'neural_populations': {
                pop_id: {
                    'population_id': pop.population_id,
                    'size': pop.size,
                    'specialization': pop.specialization,
                    'fitness_average': pop.fitness_average,
                    'diversity_index': pop.diversity_index,
                    'generation': pop.generation,
                    'active_neurons': pop.active_neurons,
                    'last_evolution': pop.last_evolution.isoformat(),
                    'evolution_cycles': pop.evolution_cycles,
                    'successful_adaptations': pop.successful_adaptations,
                    'consciousness_contributions': pop.consciousness_contributions
                }
                for pop_id, pop in self.neural_populations.items()
            },
            'active_neural_groups': self.active_neural_groups,
            'evolution_cycles': self.evolution_cycles,
            'user_contexts': {
                user_id: {
                    'user_id': ctx.user_id,
                    'created_at': ctx.created_at.isoformat(),
                    'last_updated': ctx.last_updated.isoformat(),
                    'skill_levels': {domain: level.value for domain, level in ctx.skill_levels.items()},
                    'experience_points': ctx.experience_points,
                    'learning_preferences': ctx.learning_preferences,
                    'learning_style': ctx.learning_style,
                    'preferred_difficulty': ctx.preferred_difficulty,
                    'total_time_spent': ctx.total_time_spent,
                    'achievements': ctx.achievements,
                    'goals': ctx.goals,
                    'current_session': {
                        'session_id': ctx.current_session.session_id,
                        'start_time': ctx.current_session.start_time.isoformat(),
                        'last_activity': ctx.current_session.last_activity.isoformat(),
                        'current_module': ctx.current_session.current_module,
                        'consciousness_level': ctx.current_session.consciousness_level,
                        'learning_mode': ctx.current_session.learning_mode,
                        'performance_score': ctx.current_session.performance_score
                    } if ctx.current_session else None
                }
                for user_id, ctx in self.user_contexts.items()
            },
            'active_users': self.active_users,
            'system_metrics': {
                'timestamp': self.system_metrics.timestamp.isoformat(),
                'cpu_usage': self.system_metrics.cpu_usage,
                'memory_usage': self.system_metrics.memory_usage,
                'gpu_usage': self.system_metrics.gpu_usage,
                'io_operations': self.system_metrics.io_operations,
                'network_activity': self.system_metrics.network_activity,
                'consciousness_processing_time': self.system_metrics.consciousness_processing_time,
                'component_response_times': self.system_metrics.component_response_times,
                'error_counts': self.system_metrics.error_counts
            },
            'component_states': {
                comp_id: {
                    'component_id': status.component_id,
                    'component_type': status.component_type,
                    'state': status.state.value,
                    'health_score': status.health_score,
                    'last_heartbeat': status.last_heartbeat.isoformat(),
                    'response_time_ms': status.response_time_ms,
                    'error_rate': status.error_rate,
                    'cpu_usage': status.cpu_usage,
                    'memory_usage_mb': status.memory_usage_mb,
                    'version': status.version
                }
                for comp_id, status in self.component_states.items()
            },
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'checksum': self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsciousnessState':
        """Create from dictionary"""
        data = data.copy()
        
        # Handle timestamp
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Handle neural populations
        if 'neural_populations' in data:
            populations = {}
            for pop_id, pop_data in data['neural_populations'].items():
                populations[pop_id] = PopulationState.from_dict(pop_data)
            data['neural_populations'] = populations
        
        # Handle user contexts
        if 'user_contexts' in data:
            contexts = {}
            for user_id, ctx_data in data['user_contexts'].items():
                contexts[user_id] = UserContextState.from_dict(ctx_data)
            data['user_contexts'] = contexts
        
        # Handle component states
        if 'component_states' in data:
            components = {}
            for comp_id, comp_data in data['component_states'].items():
                components[comp_id] = ComponentStatus.from_dict(comp_data)
            data['component_states'] = components
        
        # Handle system metrics
        if 'system_metrics' in data:
            metrics_data = data['system_metrics']
            if 'timestamp' in metrics_data and isinstance(metrics_data['timestamp'], str):
                metrics_data['timestamp'] = datetime.fromisoformat(metrics_data['timestamp'])
            data['system_metrics'] = SystemMetrics(**metrics_data)
        
        return cls(**data)


# Factory functions for creating common data structures

def create_population_state(
    population_id: str,
    size: int,
    specialization: str,
    fitness_average: float = 0.5
) -> PopulationState:
    """Create a new population state"""
    return PopulationState(
        population_id=population_id,
        size=size,
        specialization=specialization,
        fitness_average=fitness_average,
        diversity_index=0.5,
        generation=0,
        active_neurons=size,
        last_evolution=datetime.now()
    )


def create_user_context(user_id: str) -> UserContextState:
    """Create a new user context with default values"""
    return UserContextState(
        user_id=user_id,
        learning_preferences={
            'pace': 'normal',
            'difficulty': 'adaptive',
            'feedback_frequency': 'moderate',
            'visual_aids': True,
            'hands_on_preference': 0.7
        }
    )


def create_component_status(
    component_id: str,
    component_type: str,
    state: ComponentState = ComponentState.HEALTHY
) -> ComponentStatus:
    """Create a new component status"""
    return ComponentStatus(
        component_id=component_id,
        component_type=component_type,
        state=state,
        health_score=1.0 if state == ComponentState.HEALTHY else 0.5,
        last_heartbeat=datetime.now()
    )


def create_default_consciousness_state() -> ConsciousnessState:
    """Create a default consciousness state with basic populations"""
    state = ConsciousnessState()
    
    # Add default neural populations
    populations = [
        ('executive', 2000, 'executive'),
        ('sensory', 1500, 'sensory'),
        ('memory', 1000, 'memory'),
        ('motor', 1000, 'motor')
    ]
    
    for pop_id, size, specialization in populations:
        state.neural_populations[pop_id] = create_population_state(
            pop_id, size, specialization
        )
    
    return state


# Learning and Security Tutor Data Models

@dataclass
class LearningProgressData:
    """Learning progress tracking data"""
    user_id: str
    session_id: str
    platform: str
    topic: str
    progress_percentage: float
    skills_acquired: List[str] = field(default_factory=list)
    challenges_completed: int = 0
    time_spent_minutes: int = 0
    difficulty_level: str = "intermediate"
    consciousness_level: float = 0.5
    learning_mode: str = "focused"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'platform': self.platform,
            'topic': self.topic,
            'progress_percentage': self.progress_percentage,
            'skills_acquired': self.skills_acquired,
            'challenges_completed': self.challenges_completed,
            'time_spent_minutes': self.time_spent_minutes,
            'difficulty_level': self.difficulty_level,
            'consciousness_level': self.consciousness_level,
            'learning_mode': self.learning_mode,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class LearningSession:
    """Learning session data"""
    session_id: str
    user_id: str
    platform: str
    start_time: datetime
    consciousness_level: float = 0.5
    learning_mode: str = "focused"
    progress_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize progress data if empty"""
        if not self.progress_data:
            self.progress_data = {
                'history': [],
                'current_content': {},
                'difficulty_adjustment': 'maintain',
                'browser_guidance': {}
            }


@dataclass
class ConsciousnessLearningSession:
    """Enhanced learning session with consciousness awareness"""
    session_id: str
    user_id: str
    platform: str
    start_time: datetime
    consciousness_level: float = 0.5
    learning_mode: str = "focused"
    progress_data: Dict[str, Any] = field(default_factory=dict)
    browser_session: Optional[str] = None
    
    def __post_init__(self):
        """Initialize progress data if empty"""
        if not self.progress_data:
            self.progress_data = {
                'history': [],
                'current_content': {},
                'difficulty_adjustment': 'maintain',
                'browser_guidance': {},
                'consciousness_adaptations': []
            }


@dataclass
class LearningContent:
    """Learning content structure"""
    content_id: str
    title: str
    platform: str
    content_type: str
    difficulty_level: str
    consciousness_optimized: bool
    content_data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'content_id': self.content_id,
            'title': self.title,
            'platform': self.platform,
            'content_type': self.content_type,
            'difficulty_level': self.difficulty_level,
            'consciousness_optimized': self.consciousness_optimized,
            'content_data': self.content_data,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ConsciousnessEvent:
    """Consciousness system event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source_component: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'source_component': self.source_component,
            'data': self.data,
            'priority': self.priority
        }