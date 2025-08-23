package models

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// EventType represents the type of event
type EventType string

const (
	// Service lifecycle events
	EventTypeServiceRegistered   EventType = "service.registered"
	EventTypeServiceStarted      EventType = "service.started"
	EventTypeServiceStopped      EventType = "service.stopped"
	EventTypeServiceFailed       EventType = "service.failed"
	EventTypeServiceHealthCheck  EventType = "service.health_check"
	
	// Consciousness events
	EventTypeConsciousnessUpdate EventType = "consciousness.update"
	EventTypeNeuralEvolution     EventType = "neural.evolution"
	EventTypeContextUpdate       EventType = "context.update"
	EventTypeLearningProgress    EventType = "learning.progress"
	
	// Security events
	EventTypeSecurityThreat      EventType = "security.threat"
	EventTypeSecurityAssessment  EventType = "security.assessment"
	EventTypeSecurityIncident    EventType = "security.incident"
	
	// System events
	EventTypeSystemMetrics       EventType = "system.metrics"
	EventTypeResourceAllocation  EventType = "resource.allocation"
	EventTypeConfigurationChange EventType = "configuration.change"
	
	// AI/LM Studio events
	EventTypeInferenceRequest    EventType = "inference.request"
	EventTypeInferenceResponse   EventType = "inference.response"
	EventTypeModelSwitch         EventType = "model.switch"
)

// EventPriority represents the priority of an event
type EventPriority int

const (
	EventPriorityLow      EventPriority = 1
	EventPriorityNormal   EventPriority = 5
	EventPriorityHigh     EventPriority = 8
	EventPriorityCritical EventPriority = 10
)

// Event represents a system event
type Event struct {
	ID               string                 `json:"id"`
	Type             EventType              `json:"type"`
	Source           string                 `json:"source"`
	TargetComponents []string               `json:"target_components,omitempty"`
	Priority         EventPriority          `json:"priority"`
	Timestamp        time.Time              `json:"timestamp"`
	Data             map[string]interface{} `json:"data,omitempty"`
	Metadata         map[string]string      `json:"metadata,omitempty"`
	CorrelationID    string                 `json:"correlation_id,omitempty"`
	RetryCount       int                    `json:"retry_count"`
	MaxRetries       int                    `json:"max_retries"`
}

// NewEvent creates a new event with default values
func NewEvent(eventType EventType, source string) *Event {
	return &Event{
		ID:        uuid.New().String(),
		Type:      eventType,
		Source:    source,
		Priority:  EventPriorityNormal,
		Timestamp: time.Now(),
		Data:      make(map[string]interface{}),
		Metadata:  make(map[string]string),
		MaxRetries: 3,
	}
}

// WithTargets sets the target components for the event
func (e *Event) WithTargets(targets ...string) *Event {
	e.TargetComponents = targets
	return e
}

// WithPriority sets the priority of the event
func (e *Event) WithPriority(priority EventPriority) *Event {
	e.Priority = priority
	return e
}

// WithData sets data for the event
func (e *Event) WithData(key string, value interface{}) *Event {
	e.Data[key] = value
	return e
}

// WithMetadata sets metadata for the event
func (e *Event) WithMetadata(key, value string) *Event {
	e.Metadata[key] = value
	return e
}

// WithCorrelationID sets the correlation ID for the event
func (e *Event) WithCorrelationID(correlationID string) *Event {
	e.CorrelationID = correlationID
	return e
}

// CanRetry returns true if the event can be retried
func (e *Event) CanRetry() bool {
	return e.RetryCount < e.MaxRetries
}

// IncrementRetry increments the retry count
func (e *Event) IncrementRetry() {
	e.RetryCount++
}

// ToJSON converts the event to JSON bytes
func (e *Event) ToJSON() ([]byte, error) {
	return json.Marshal(e)
}

// FromJSON creates an event from JSON bytes
func FromJSON(data []byte) (*Event, error) {
	var event Event
	err := json.Unmarshal(data, &event)
	return &event, err
}

// ServiceLifecycleEventData represents data for service lifecycle events
type ServiceLifecycleEventData struct {
	ServiceID   string        `json:"service_id"`
	ServiceName string        `json:"service_name"`
	Action      string        `json:"action"`
	Status      ServiceStatus `json:"status"`
	Error       string        `json:"error,omitempty"`
}

// ConsciousnessEventData represents data for consciousness events
type ConsciousnessEventData struct {
	UserID             string                 `json:"user_id,omitempty"`
	ConsciousnessLevel float64                `json:"consciousness_level"`
	NeuralPopulations  map[string]interface{} `json:"neural_populations,omitempty"`
	ContextData        map[string]interface{} `json:"context_data,omitempty"`
	Adaptations        []string               `json:"adaptations,omitempty"`
}

// SecurityEventData represents data for security events
type SecurityEventData struct {
	ThreatType    string                 `json:"threat_type"`
	Severity      string                 `json:"severity"`
	SourceIP      string                 `json:"source_ip,omitempty"`
	UserID        string                 `json:"user_id,omitempty"`
	Description   string                 `json:"description"`
	Indicators    map[string]interface{} `json:"indicators,omitempty"`
	Actions       []string               `json:"recommended_actions,omitempty"`
}

// MetricsEventData represents data for metrics events
type MetricsEventData struct {
	ComponentID   string                 `json:"component_id"`
	Metrics       map[string]float64     `json:"metrics"`
	ResourceUsage map[string]float64     `json:"resource_usage"`
	ResponseTimes map[string]float64     `json:"response_times"`
	ErrorRates    map[string]float64     `json:"error_rates"`
	Timestamp     time.Time              `json:"timestamp"`
}

// InferenceEventData represents data for AI inference events
type InferenceEventData struct {
	RequestID            string                 `json:"request_id"`
	ModelName            string                 `json:"model_name"`
	Prompt               string                 `json:"prompt,omitempty"`
	Response             string                 `json:"response,omitempty"`
	ConsciousnessContext map[string]interface{} `json:"consciousness_context,omitempty"`
	Parameters           map[string]interface{} `json:"parameters,omitempty"`
	TokensUsed           int                    `json:"tokens_used,omitempty"`
	ProcessingTimeMs     float64                `json:"processing_time_ms,omitempty"`
	ConfidenceScore      float64                `json:"confidence_score,omitempty"`
}

// EventFilter represents criteria for filtering events
type EventFilter struct {
	Types            []EventType `json:"types,omitempty"`
	Sources          []string    `json:"sources,omitempty"`
	MinPriority      *EventPriority `json:"min_priority,omitempty"`
	Since            *time.Time  `json:"since,omitempty"`
	Until            *time.Time  `json:"until,omitempty"`
	CorrelationID    string      `json:"correlation_id,omitempty"`
	Limit            int         `json:"limit,omitempty"`
}

// Matches returns true if the event matches the filter criteria
func (f *EventFilter) Matches(event *Event) bool {
	// Check event types
	if len(f.Types) > 0 {
		found := false
		for _, t := range f.Types {
			if t == event.Type {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}

	// Check sources
	if len(f.Sources) > 0 {
		found := false
		for _, s := range f.Sources {
			if s == event.Source {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}

	// Check minimum priority
	if f.MinPriority != nil && event.Priority < *f.MinPriority {
		return false
	}

	// Check time range
	if f.Since != nil && event.Timestamp.Before(*f.Since) {
		return false
	}
	if f.Until != nil && event.Timestamp.After(*f.Until) {
		return false
	}

	// Check correlation ID
	if f.CorrelationID != "" && event.CorrelationID != f.CorrelationID {
		return false
	}

	return true
}

// EventSubscription represents a subscription to events
type EventSubscription struct {
	ID          string      `json:"id"`
	ComponentID string      `json:"component_id"`
	Filter      EventFilter `json:"filter"`
	Subject     string      `json:"subject"`
	CreatedAt   time.Time   `json:"created_at"`
	LastSeen    *time.Time  `json:"last_seen,omitempty"`
	EventCount  int64       `json:"event_count"`
}

// NewSubscription creates a new event subscription
func NewSubscription(componentID string, filter EventFilter) *EventSubscription {
	return &EventSubscription{
		ID:          uuid.New().String(),
		ComponentID: componentID,
		Filter:      filter,
		CreatedAt:   time.Now(),
	}
}