"""
NATS Resilience Module
=====================

Provides resilience patterns, circuit breakers, message persistence,
recovery mechanisms, and monitoring for NATS communication.
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    NATSResilienceManager,
    resilience_manager,
    with_circuit_breaker
)

from .message_persistence import (
    MessagePersistenceStore,
    MessageReplayManager,
    PersistedMessage,
    MessageStatus,
    MessagePriority
)

from .monitoring import (
    NATSMonitor,
    MetricsCollector,
    AlertManager,
    Alert,
    AlertSeverity,
    Metric,
    MetricType,
    nats_monitor
)

__all__ = [
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerConfig',
    'CircuitBreakerOpenError',
    'NATSResilienceManager',
    'resilience_manager',
    'with_circuit_breaker',
    
    # Message Persistence
    'MessagePersistenceStore',
    'MessageReplayManager',
    'PersistedMessage',
    'MessageStatus',
    'MessagePriority',
    
    # Monitoring
    'NATSMonitor',
    'MetricsCollector',
    'AlertManager',
    'Alert',
    'AlertSeverity',
    'Metric',
    'MetricType',
    'nats_monitor'
]