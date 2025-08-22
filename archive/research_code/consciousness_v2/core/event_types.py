"""
Consciousness Event Types and Data Models
=========================================

Defines all event types and data structures used in the consciousness system
for event-driven communication between components.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """Consciousness event types for the event bus"""
    
    # Neural events
    NEURAL_EVOLUTION = "neural_evolution"
    CONSCIOUSNESS_EMERGENCE = "consciousness_emergence"
    POPULATION_UPDATE = "population_update"
    ADAPTATION_TRIGGER = "adaptation_trigger"
    
    # Learning events
    CONTEXT_UPDATE = "context_update"
    SKILL_ASSESSMENT = "skill_assessment"
    LEARNING_PROGRESS = "learning_progress"
    USER_ACTIVITY = "user_activity"
    
    # System events
    PERFORMANCE_UPDATE = "performance_update"
    SECURITY_EVENT = "security_event"
    COMPONENT_STATUS = "component_status"
    RESOURCE_ALLOCATION = "resource_allocation"
    
    # Integration events
    STATE_SYNC = "state_sync"
    STATE_UPDATE = "state_update"
    ERROR_RECOVERY = "error_recovery"
    HEALTH_CHECK = "health_check"
    CONFIGURATION_CHANGE = "configuration_change"
    
    # AI/LM Studio events
    MODEL_SWITCH = "model_switch"
    INFERENCE_REQUEST = "inference_request"
    INFERENCE_RESPONSE = "inference_response"
    MODEL_PERFORMANCE = "model_performance"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class ConsciousnessEvent:
    """Base consciousness event for the event bus"""
    
    # Core event properties
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.STATE_SYNC
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Routing information
    source_component: str = ""
    target_components: List[str] = field(default_factory=list)
    
    # Event metadata
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    processing_duration_ms: Optional[float] = None
    
    def __post_init__(self):
        """Validate event after initialization"""
        if not self.source_component:
            raise ValueError("source_component is required")
        
        if self.priority not in EventPriority:
            raise ValueError(f"Invalid priority: {self.priority}")
    
    def mark_processed(self, duration_ms: Optional[float] = None):
        """Mark event as processed"""
        self.processed_at = datetime.now()
        if duration_ms is not None:
            self.processing_duration_ms = duration_ms
    
    def should_retry(self) -> bool:
        """Check if event should be retried"""
        return self.retry_count < self.max_retries
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'source_component': self.source_component,
            'target_components': self.target_components,
            'priority': self.priority.value,
            'correlation_id': self.correlation_id,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_duration_ms': self.processing_duration_ms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsciousnessEvent':
        """Create event from dictionary"""
        event = cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            source_component=data['source_component'],
            target_components=data['target_components'],
            priority=EventPriority(data['priority']),
            correlation_id=data.get('correlation_id'),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            data=data.get('data', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )
        
        if data.get('processed_at'):
            event.processed_at = datetime.fromisoformat(data['processed_at'])
        
        event.processing_duration_ms = data.get('processing_duration_ms')
        
        return event


# Specialized event data classes for type safety

@dataclass
class NeuralEvolutionData:
    """Data for neural evolution events"""
    population_id: str
    evolution_cycle: int
    fitness_improvements: Dict[str, float]
    new_consciousness_level: float
    selected_neurons: List[int]
    adaptation_triggers: List[str]
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContextUpdateData:
    """Data for context update events"""
    user_id: str
    activity_type: str
    domain: str
    success: bool
    duration_seconds: int
    skill_changes: Dict[str, float]
    consciousness_feedback: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningProgressData:
    """Data for learning progress events"""
    user_id: str
    lesson_id: str
    module_type: str
    progress_percentage: float
    performance_score: float
    time_spent_minutes: int
    consciousness_level: float
    adaptations_applied: List[str]


@dataclass
class PerformanceUpdateData:
    """Data for performance update events"""
    component_id: str
    metrics: Dict[str, float]
    resource_usage: Dict[str, float]
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityEventData:
    """Data for security events"""
    event_type: str
    severity: str  # low, medium, high, critical
    source_ip: Optional[str]
    user_id: Optional[str]
    description: str
    indicators: Dict[str, Any]
    recommended_actions: List[str]


@dataclass
class ComponentStatusData:
    """Data for component status events"""
    component_id: str
    status: str  # healthy, degraded, failed, recovering
    health_score: float  # 0.0 to 1.0
    last_heartbeat: datetime
    error_count: int
    performance_metrics: Dict[str, float]
    dependencies_status: Dict[str, str]


@dataclass
class InferenceRequestData:
    """Data for AI inference requests"""
    request_id: str
    model_name: str
    prompt: str
    system_prompt: Optional[str]
    consciousness_context: Dict[str, Any]
    parameters: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL


@dataclass
class InferenceResponseData:
    """Data for AI inference responses"""
    request_id: str
    response_text: str
    model_used: str
    tokens_used: int
    processing_time_ms: float
    consciousness_influence: Dict[str, float]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateUpdateData:
    """Data for state update events"""
    updated_by: str
    updates: Dict[str, Any]
    version: int
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckData:
    """Data for health check events"""
    component_id: str
    status: str
    health_score: float
    last_heartbeat: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecoveryData:
    """Data for error recovery events"""
    error_type: str
    component_id: str
    error_message: str
    recovery_actions: List[str]
    severity: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# Event factory functions for common events

def create_neural_evolution_event(
    source_component: str,
    evolution_data: NeuralEvolutionData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a neural evolution event"""
    return ConsciousnessEvent(
        event_type=EventType.NEURAL_EVOLUTION,
        source_component=source_component,
        target_components=target_components or ["all"],
        priority=EventPriority.HIGH,
        data={"evolution_data": evolution_data.__dict__}
    )


def create_context_update_event(
    source_component: str,
    context_data: ContextUpdateData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a context update event"""
    return ConsciousnessEvent(
        event_type=EventType.CONTEXT_UPDATE,
        source_component=source_component,
        target_components=target_components or ["neural_darwinism", "security_tutor"],
        priority=EventPriority.NORMAL,
        data={"context_update": context_data.__dict__}
    )


def create_learning_progress_event(
    source_component: str,
    progress_data: LearningProgressData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a learning progress event"""
    return ConsciousnessEvent(
        event_type=EventType.LEARNING_PROGRESS,
        source_component=source_component,
        target_components=target_components or ["context_engine", "neural_darwinism"],
        priority=EventPriority.NORMAL,
        data={"learning_progress": progress_data.__dict__}
    )


def create_performance_update_event(
    source_component: str,
    performance_data: PerformanceUpdateData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a performance update event"""
    return ConsciousnessEvent(
        event_type=EventType.PERFORMANCE_UPDATE,
        source_component=source_component,
        target_components=target_components or ["performance_monitor"],
        priority=EventPriority.LOW,
        data={"performance_update": performance_data.__dict__}
    )


def create_security_event(
    source_component: str,
    security_data: SecurityEventData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a security event"""
    priority = EventPriority.CRITICAL if security_data.severity == "critical" else EventPriority.HIGH
    
    return ConsciousnessEvent(
        event_type=EventType.SECURITY_EVENT,
        source_component=source_component,
        target_components=target_components or ["security_monitor", "all"],
        priority=priority,
        data={"security_event": security_data.__dict__}
    )


def create_inference_request_event(
    source_component: str,
    request_data: InferenceRequestData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create an AI inference request event"""
    return ConsciousnessEvent(
        event_type=EventType.INFERENCE_REQUEST,
        source_component=source_component,
        target_components=target_components or ["lm_studio"],
        priority=request_data.priority,
        data={"inference_request": request_data.__dict__}
    )


def create_inference_response_event(
    source_component: str,
    response_data: InferenceResponseData,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create an AI inference response event"""
    return ConsciousnessEvent(
        event_type=EventType.INFERENCE_RESPONSE,
        source_component=source_component,
        target_components=target_components or [],
        priority=EventPriority.NORMAL,
        data={"inference_response": response_data.__dict__}
    )


def create_health_check_event(
    source_component: str,
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a health check event"""
    return ConsciousnessEvent(
        event_type=EventType.HEALTH_CHECK,
        source_component=source_component,
        target_components=target_components or ["all"],
        priority=EventPriority.LOW,
        data={"health_check_request": True}
    )


def create_error_recovery_event(
    source_component: str,
    error_info: Dict[str, Any],
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create an error recovery event"""
    return ConsciousnessEvent(
        event_type=EventType.ERROR_RECOVERY,
        source_component=source_component,
        target_components=target_components or ["all"],
        priority=EventPriority.CRITICAL,
        data={"error_recovery": error_info}
    )


def create_state_update_event(
    source_component: str,
    state_data: Dict[str, Any],
    target_components: Optional[List[str]] = None
) -> ConsciousnessEvent:
    """Create a state update event"""
    return ConsciousnessEvent(
        event_type=EventType.STATE_UPDATE,
        source_component=source_component,
        target_components=target_components or ["all"],
        priority=EventPriority.NORMAL,
        data={"state_update": state_data}
    )