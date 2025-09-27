//! # Event System for SynOS Services
//! 
//! Defines event types, structures, and filtering capabilities for the service integration system.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Event types supported by the SynOS service system
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum EventType {
    // Service lifecycle events
    ServiceStarted,
    ServiceStopped,
    ServiceFailed,
    ServiceHealthCheck,
    ServiceRegistered,
    ServiceUnregistered,

    // AI system events
    AIUpdate,
    NeuralNetworkUpdate,
    ContextUpdate,
    LearningProgress,

    // Security events
    SecurityThreat,
    SecurityIncident,
    SecurityAssessment,

    // System events
    SystemMetrics,
    ResourceAllocation,
    ConfigurationChange,

    // Custom events
    Custom(String),
}

/// Event priority levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum EventPriority {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
}

/// Core event structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    /// Unique event identifier
    pub id: String,
    
    /// Event type
    pub event_type: EventType,
    
    /// Source service/component that generated the event
    pub source: String,
    
    /// Target service/component (optional)
    pub target: Option<String>,
    
    /// Event timestamp
    pub timestamp: DateTime<Utc>,
    
    /// Event priority
    pub priority: EventPriority,
    
    /// Event payload data
    pub data: HashMap<String, serde_json::Value>,
    
    /// Event metadata
    pub metadata: HashMap<String, String>,
    
    /// Correlation ID for request tracing
    pub correlation_id: Option<String>,
}

impl Event {
    /// Create a new event
    pub fn new(event_type: EventType, source: String) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            event_type,
            source,
            target: None,
            timestamp: Utc::now(),
            priority: EventPriority::Medium,
            data: HashMap::new(),
            metadata: HashMap::new(),
            correlation_id: None,
        }
    }

    /// Create a service lifecycle event
    pub fn service_lifecycle(
        event_type: EventType,
        service_id: String,
        status: crate::ServiceStatus,
    ) -> Self {
        let mut event = Self::new(event_type, service_id);
        event.data.insert("status".to_string(), serde_json::to_value(status).unwrap());
        event
    }

    /// Create a health check event
    pub fn health_check(service_id: String, healthy: bool, details: Option<String>) -> Self {
        let mut event = Self::new(EventType::ServiceHealthCheck, service_id);
        event.data.insert("healthy".to_string(), healthy.into());
        if let Some(details) = details {
            event.data.insert("details".to_string(), details.into());
        }
        event
    }

    /// Create an AI system update event
    pub fn ai_update(
        component: String,
        level: f64,
        metrics: HashMap<String, f64>,
    ) -> Self {
        let mut event = Self::new(EventType::AIUpdate, component);
        event.data.insert("ai_level".to_string(), level.into());
        event.data.insert("metrics".to_string(), serde_json::to_value(metrics).unwrap());
        event.priority = EventPriority::High;
        event
    }

    /// Create a security event
    pub fn security_threat(
        source: String,
        threat_type: String,
        severity: String,
        details: HashMap<String, serde_json::Value>,
    ) -> Self {
        let mut event = Self::new(EventType::SecurityThreat, source);
        event.data.insert("threat_type".to_string(), threat_type.into());
        event.data.insert("severity".to_string(), severity.into());
        event.data.extend(details);
        event.priority = EventPriority::Critical;
        event
    }

    /// Create a neural network update event
    pub fn neural_network_update(
        population_id: String,
        generation: u64,
        fitness_stats: HashMap<String, f64>,
    ) -> Self {
        let mut event = Self::new(EventType::NeuralNetworkUpdate, "neural-network".to_string());
        event.data.insert("population_id".to_string(), population_id.into());
        event.data.insert("generation".to_string(), generation.into());
        event.data.insert("fitness_stats".to_string(), serde_json::to_value(fitness_stats).unwrap());
        event.priority = EventPriority::High;
        event
    }

    /// Set event target
    pub fn with_target(mut self, target: String) -> Self {
        self.target = Some(target);
        self
    }

    /// Set event priority
    pub fn with_priority(mut self, priority: EventPriority) -> Self {
        self.priority = priority;
        self
    }

    /// Set correlation ID
    pub fn with_correlation_id(mut self, correlation_id: String) -> Self {
        self.correlation_id = Some(correlation_id);
        self
    }

    /// Add data field
    pub fn with_data(mut self, key: String, value: serde_json::Value) -> Self {
        self.data.insert(key, value);
        self
    }

    /// Add metadata field
    pub fn with_metadata(mut self, key: String, value: String) -> Self {
        self.metadata.insert(key, value);
        self
    }

    /// Get event age in seconds
    pub fn age_seconds(&self) -> i64 {
        (Utc::now() - self.timestamp).num_seconds()
    }

    /// Check if event has expired based on TTL
    pub fn is_expired(&self, ttl_seconds: i64) -> bool {
        self.age_seconds() > ttl_seconds
    }
}

/// Event filter for subscriptions
#[derive(Debug, Clone, Default)]
pub struct EventFilter {
    /// Event types to match
    pub event_types: Vec<EventType>,
    
    /// Source services to match
    pub sources: Vec<String>,
    
    /// Target services to match
    pub targets: Vec<String>,
    
    /// Minimum priority level
    pub min_priority: Option<EventPriority>,
    
    /// Maximum event age in seconds
    pub max_age_seconds: Option<i64>,
    
    /// Metadata filters (key-value pairs)
    pub metadata_filters: HashMap<String, String>,
}

impl EventFilter {
    /// Create a new empty filter
    pub fn new() -> Self {
        Self::default()
    }

    /// Filter by event types
    pub fn with_event_types(mut self, event_types: Vec<EventType>) -> Self {
        self.event_types = event_types;
        self
    }

    /// Filter by sources
    pub fn with_sources(mut self, sources: Vec<String>) -> Self {
        self.sources = sources;
        self
    }

    /// Filter by targets
    pub fn with_targets(mut self, targets: Vec<String>) -> Self {
        self.targets = targets;
        self
    }

    /// Filter by minimum priority
    pub fn with_min_priority(mut self, priority: EventPriority) -> Self {
        self.min_priority = Some(priority);
        self
    }

    /// Filter by maximum age
    pub fn with_max_age(mut self, max_age_seconds: i64) -> Self {
        self.max_age_seconds = Some(max_age_seconds);
        self
    }

    /// Add metadata filter
    pub fn with_metadata_filter(mut self, key: String, value: String) -> Self {
        self.metadata_filters.insert(key, value);
        self
    }

    /// Check if an event matches this filter
    pub fn matches(&self, event: &Event) -> bool {
        // Check event type
        if !self.event_types.is_empty() && !self.event_types.contains(&event.event_type) {
            return false;
        }

        // Check source
        if !self.sources.is_empty() && !self.sources.contains(&event.source) {
            return false;
        }

        // Check target
        if !self.targets.is_empty() {
            match &event.target {
                Some(target) => {
                    if !self.targets.contains(target) {
                        return false;
                    }
                }
                None => return false,
            }
        }

        // Check priority
        if let Some(min_priority) = self.min_priority {
            if event.priority < min_priority {
                return false;
            }
        }

        // Check age
        if let Some(max_age) = self.max_age_seconds {
            if event.age_seconds() > max_age {
                return false;
            }
        }

        // Check metadata filters
        for (key, value) in &self.metadata_filters {
            match event.metadata.get(key) {
                Some(event_value) => {
                    if event_value != value {
                        return false;
                    }
                }
                None => return false,
            }
        }

        true
    }
}

/// Event builder for convenient event creation
pub struct EventBuilder {
    event: Event,
}

impl EventBuilder {
    /// Create a new event builder
    pub fn new(event_type: EventType, source: String) -> Self {
        Self {
            event: Event::new(event_type, source),
        }
    }

    /// Set target
    pub fn target(mut self, target: String) -> Self {
        self.event.target = Some(target);
        self
    }

    /// Set priority
    pub fn priority(mut self, priority: EventPriority) -> Self {
        self.event.priority = priority;
        self
    }

    /// Add data
    pub fn data(mut self, key: String, value: serde_json::Value) -> Self {
        self.event.data.insert(key, value);
        self
    }

    /// Add metadata
    pub fn metadata(mut self, key: String, value: String) -> Self {
        self.event.metadata.insert(key, value);
        self
    }

    /// Set correlation ID
    pub fn correlation_id(mut self, correlation_id: String) -> Self {
        self.event.correlation_id = Some(correlation_id);
        self
    }

    /// Build the event
    pub fn build(self) -> Event {
        self.event
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_event_creation() {
        let event = Event::new(EventType::ServiceStarted, "test-service".to_string());
        
        assert_eq!(event.event_type, EventType::ServiceStarted);
        assert_eq!(event.source, "test-service");
        assert_eq!(event.priority, EventPriority::Medium);
        assert!(event.target.is_none());
    }

    #[test]
    fn test_event_filter_matching() {
        let event = Event::new(EventType::ServiceStarted, "test-service".to_string())
            .with_priority(EventPriority::High);

        let filter = EventFilter::new()
            .with_event_types(vec![EventType::ServiceStarted])
            .with_min_priority(EventPriority::Medium);

        assert!(filter.matches(&event));

        let filter_no_match = EventFilter::new()
            .with_event_types(vec![EventType::ServiceStopped]);

        assert!(!filter_no_match.matches(&event));
    }

    #[test]
    fn test_event_builder() {
        let event = EventBuilder::new(EventType::SecurityThreat, "security-monitor".to_string())
            .priority(EventPriority::Critical)
            .data("threat_type".to_string(), "malware".into())
            .metadata("severity".to_string(), "high".to_string())
            .build();

        assert_eq!(event.event_type, EventType::SecurityThreat);
        assert_eq!(event.priority, EventPriority::Critical);
        assert_eq!(event.data.get("threat_type").unwrap(), "malware");
        assert_eq!(event.metadata.get("severity").unwrap(), "high");
    }
}
