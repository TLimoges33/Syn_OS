package core

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/syn-os/orchestrator/internal/models"
)

// EventRouter manages event routing and subscriptions
type EventRouter struct {
	orchestrator  *Orchestrator
	subscriptions map[string]*models.EventSubscription
	eventHistory  []models.Event
	mu            sync.RWMutex
	logger        *log.Logger

	// Configuration
	maxHistorySize int

	// Background tasks
	ctx    context.Context
	cancel context.CancelFunc
}

// NewEventRouter creates a new event router
func NewEventRouter(orchestrator *Orchestrator) *EventRouter {
	logger := log.Default()
	logger.SetPrefix("[EventRouter] ")

	return &EventRouter{
		orchestrator:   orchestrator,
		subscriptions:  make(map[string]*models.EventSubscription),
		eventHistory:   make([]models.Event, 0),
		logger:         logger,
		maxHistorySize: 1000,
	}
}

// Start starts the event router
func (er *EventRouter) Start(ctx context.Context) error {
	er.mu.Lock()
	defer er.mu.Unlock()

	er.ctx, er.cancel = context.WithCancel(ctx)
	er.logger.Println("Starting Event Router...")

	// Subscribe to all NATS events for routing
	if err := er.setupNATSSubscriptions(); err != nil {
		return fmt.Errorf("failed to setup NATS subscriptions: %w", err)
	}

	// Start background tasks
	go er.eventCleanupLoop()

	er.logger.Println("Event Router started")
	return nil
}

// Stop stops the event router
func (er *EventRouter) Stop() {
	er.mu.Lock()
	defer er.mu.Unlock()

	if er.cancel != nil {
		er.cancel()
	}

	er.logger.Println("Event Router stopped")
}

// PublishEvent publishes an event
func (er *EventRouter) PublishEvent(event *models.Event) error {
	er.mu.Lock()
	defer er.mu.Unlock()

	// Add to history
	er.addToHistory(*event)

	// Publish to NATS
	if err := er.orchestrator.natsClient.PublishEvent(event); err != nil {
		return fmt.Errorf("failed to publish event to NATS: %w", err)
	}

	er.logger.Printf("Published event: %s (type: %s, source: %s)",
		event.ID, event.Type, event.Source)

	return nil
}

// SubscribeToEvents subscribes to events matching the filter
func (er *EventRouter) SubscribeToEvents(filter models.EventFilter, handler func(*models.Event) error) (string, error) {
	er.mu.Lock()
	defer er.mu.Unlock()

	// Create subscription
	subscription := models.NewSubscription("orchestrator", filter)

	// Subscribe to NATS
	natsSubID, err := er.orchestrator.natsClient.SubscribeToEvents(filter, func(event *models.Event) error {
		// Update subscription metrics
		subscription.LastSeen = &event.Timestamp
		subscription.EventCount++

		// Call handler
		return handler(event)
	})
	if err != nil {
		return "", fmt.Errorf("failed to subscribe to NATS: %w", err)
	}

	subscription.Subject = natsSubID
	er.subscriptions[subscription.ID] = subscription

	er.logger.Printf("Created event subscription: %s", subscription.ID)
	return subscription.ID, nil
}

// UnsubscribeFromEvents unsubscribes from events
func (er *EventRouter) UnsubscribeFromEvents(subscriptionID string) error {
	er.mu.Lock()
	defer er.mu.Unlock()

	subscription, exists := er.subscriptions[subscriptionID]
	if !exists {
		return fmt.Errorf("subscription %s not found", subscriptionID)
	}

	// Unsubscribe from NATS
	if err := er.orchestrator.natsClient.Unsubscribe(subscription.Subject); err != nil {
		return fmt.Errorf("failed to unsubscribe from NATS: %w", err)
	}

	delete(er.subscriptions, subscriptionID)

	er.logger.Printf("Removed event subscription: %s", subscriptionID)
	return nil
}

// GetEventHistory returns recent events matching the filter
func (er *EventRouter) GetEventHistory(filter models.EventFilter) ([]*models.Event, error) {
	er.mu.RLock()
	defer er.mu.RUnlock()

	var matchingEvents []*models.Event
	count := 0

	// Search from most recent events
	for i := len(er.eventHistory) - 1; i >= 0 && count < filter.Limit; i-- {
		event := er.eventHistory[i]
		if filter.Matches(&event) {
			matchingEvents = append([]*models.Event{&event}, matchingEvents...)
			count++
		}
	}

	return matchingEvents, nil
}

// GetSubscriptions returns all active subscriptions
func (er *EventRouter) GetSubscriptions() map[string]*models.EventSubscription {
	er.mu.RLock()
	defer er.mu.RUnlock()

	// Return a copy to prevent external modifications
	subscriptions := make(map[string]*models.EventSubscription)
	for id, sub := range er.subscriptions {
		subscriptions[id] = sub
	}

	return subscriptions
}

// GetStatus returns event router status
func (er *EventRouter) GetStatus() map[string]interface{} {
	er.mu.RLock()
	defer er.mu.RUnlock()

	return map[string]interface{}{
		"running":              er.ctx != nil,
		"active_subscriptions": len(er.subscriptions),
		"event_history_size":   len(er.eventHistory),
		"max_history_size":     er.maxHistorySize,
	}
}

// GetMetrics returns event router metrics
func (er *EventRouter) GetMetrics() (map[string]interface{}, error) {
	er.mu.RLock()
	defer er.mu.RUnlock()

	// Calculate event type distribution
	eventTypeCount := make(map[string]int)
	eventSourceCount := make(map[string]int)
	eventPriorityCount := make(map[string]int)

	for _, event := range er.eventHistory {
		eventTypeCount[string(event.Type)]++
		eventSourceCount[event.Source]++
		eventPriorityCount[fmt.Sprintf("priority_%d", event.Priority)]++
	}

	// Calculate subscription metrics
	var totalEventCount int64
	subscriptionMetrics := make(map[string]interface{})

	for id, sub := range er.subscriptions {
		totalEventCount += sub.EventCount
		subscriptionMetrics[id] = map[string]interface{}{
			"component_id": sub.ComponentID,
			"event_count":  sub.EventCount,
			"created_at":   sub.CreatedAt,
			"last_seen":    sub.LastSeen,
		}
	}

	metrics := map[string]interface{}{
		"total_events_processed":      totalEventCount,
		"active_subscriptions":        len(er.subscriptions),
		"event_history_size":          len(er.eventHistory),
		"event_type_distribution":     eventTypeCount,
		"event_source_distribution":   eventSourceCount,
		"event_priority_distribution": eventPriorityCount,
		"subscription_metrics":        subscriptionMetrics,
	}

	// Add NATS stream information
	if streamInfo, err := er.orchestrator.natsClient.GetStreamInfo(); err == nil {
		metrics["nats_streams"] = streamInfo
	}

	return metrics, nil
}

// RouteConsciousnessEvent routes consciousness events to appropriate handlers
func (er *EventRouter) RouteConsciousnessEvent(event *models.Event) error {
	er.logger.Printf("Routing consciousness event: %s from %s", event.Type, event.Source)

	// Add consciousness-specific routing logic
	switch event.Type {
	case models.EventTypeConsciousnessUpdate:
		return er.handleConsciousnessUpdate(event)
	case models.EventTypeNeuralEvolution:
		return er.handleNeuralEvolution(event)
	case models.EventTypeContextUpdate:
		return er.handleContextUpdate(event)
	case models.EventTypeLearningProgress:
		return er.handleLearningProgress(event)
	default:
		er.logger.Printf("Unknown consciousness event type: %s", event.Type)
	}

	return nil
}

// RouteServiceEvent routes service events to appropriate handlers
func (er *EventRouter) RouteServiceEvent(event *models.Event) error {
	er.logger.Printf("Routing service event: %s from %s", event.Type, event.Source)

	// Add service-specific routing logic
	switch event.Type {
	case models.EventTypeServiceRegistered:
		return er.handleServiceRegistered(event)
	case models.EventTypeServiceStarted:
		return er.handleServiceStarted(event)
	case models.EventTypeServiceStopped:
		return er.handleServiceStopped(event)
	case models.EventTypeServiceFailed:
		return er.handleServiceFailed(event)
	case models.EventTypeServiceHealthCheck:
		return er.handleServiceHealthCheck(event)
	default:
		er.logger.Printf("Unknown service event type: %s", event.Type)
	}

	return nil
}

// RouteSecurityEvent routes security events to appropriate handlers
func (er *EventRouter) RouteSecurityEvent(event *models.Event) error {
	er.logger.Printf("Routing security event: %s from %s", event.Type, event.Source)

	// Add security-specific routing logic
	switch event.Type {
	case models.EventTypeSecurityThreat:
		return er.handleSecurityThreat(event)
	case models.EventTypeSecurityAssessment:
		return er.handleSecurityAssessment(event)
	case models.EventTypeSecurityIncident:
		return er.handleSecurityIncident(event)
	default:
		er.logger.Printf("Unknown security event type: %s", event.Type)
	}

	return nil
}

// Private methods

// setupNATSSubscriptions sets up NATS subscriptions for event routing
func (er *EventRouter) setupNATSSubscriptions() error {
	// Subscribe to all consciousness events
	_, err := er.orchestrator.natsClient.SubscribeToConsciousnessEvents(func(event *models.Event) error {
		er.addToHistory(*event)
		return er.RouteConsciousnessEvent(event)
	})
	if err != nil {
		return fmt.Errorf("failed to subscribe to consciousness events: %w", err)
	}

	// Subscribe to all service events
	_, err = er.orchestrator.natsClient.SubscribeToServiceEvents("", func(event *models.Event) error {
		er.addToHistory(*event)
		return er.RouteServiceEvent(event)
	})
	if err != nil {
		return fmt.Errorf("failed to subscribe to service events: %w", err)
	}

	// Subscribe to security events
	filter := models.EventFilter{
		Types: []models.EventType{
			models.EventTypeSecurityThreat,
			models.EventTypeSecurityAssessment,
			models.EventTypeSecurityIncident,
		},
	}
	_, err = er.orchestrator.natsClient.SubscribeToEvents(filter, func(event *models.Event) error {
		er.addToHistory(*event)
		return er.RouteSecurityEvent(event)
	})
	if err != nil {
		return fmt.Errorf("failed to subscribe to security events: %w", err)
	}

	er.logger.Println("NATS subscriptions setup completed")
	return nil
}

// addToHistory adds an event to the history buffer
func (er *EventRouter) addToHistory(event models.Event) {
	er.eventHistory = append(er.eventHistory, event)

	// Maintain history size limit
	if len(er.eventHistory) > er.maxHistorySize {
		er.eventHistory = er.eventHistory[len(er.eventHistory)-er.maxHistorySize:]
	}
}

// eventCleanupLoop runs background cleanup of old events
func (er *EventRouter) eventCleanupLoop() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-er.ctx.Done():
			return
		case <-ticker.C:
			er.cleanupOldEvents()
		}
	}
}

// cleanupOldEvents removes old events from history
func (er *EventRouter) cleanupOldEvents() {
	er.mu.Lock()
	defer er.mu.Unlock()

	cutoff := time.Now().Add(-1 * time.Hour)
	var newHistory []models.Event

	for _, event := range er.eventHistory {
		if event.Timestamp.After(cutoff) {
			newHistory = append(newHistory, event)
		}
	}

	if len(newHistory) < len(er.eventHistory) {
		er.eventHistory = newHistory
		er.logger.Printf("Cleaned up old events, history size: %d", len(er.eventHistory))
	}
}

// Event handlers

func (er *EventRouter) handleConsciousnessUpdate(event *models.Event) error {
	// Handle consciousness update events
	er.logger.Printf("Processing consciousness update: %v", event.Data)

	// Forward to interested services
	if consciousnessLevel, ok := event.Data["consciousness_level"].(float64); ok {
		// Notify services that care about consciousness level changes
		services, err := er.orchestrator.serviceManager.ListServices(models.ServiceTypeIntelligence, models.ServiceStatusRunning)
		if err == nil {
			for _, service := range services {
				// Send consciousness update to service
				er.logger.Printf("Forwarding consciousness update (level: %.2f) to service: %s", consciousnessLevel, service.Name)
			}
		}
	}

	return nil
}

func (er *EventRouter) handleNeuralEvolution(event *models.Event) error {
	// Handle neural evolution events
	er.logger.Printf("Processing neural evolution: %v", event.Data)

	// Update system resource allocation based on evolution
	resourceEvent := models.NewEvent(models.EventTypeResourceAllocation, "event_router").
		WithData("trigger", "neural_evolution").
		WithData("evolution_data", event.Data).
		WithPriority(models.EventPriorityNormal)

	return er.PublishEvent(resourceEvent)
}

func (er *EventRouter) handleContextUpdate(event *models.Event) error {
	// Handle context update events
	er.logger.Printf("Processing context update: %v", event.Data)

	// Forward to learning services
	services, err := er.orchestrator.serviceManager.ListServices("", models.ServiceStatusRunning)
	if err == nil {
		for _, service := range services {
			if service.Name == "security_tutor" || service.Type == models.ServiceTypeIntelligence {
				er.logger.Printf("Forwarding context update to service: %s", service.Name)
			}
		}
	}

	return nil
}

func (er *EventRouter) handleLearningProgress(event *models.Event) error {
	// Handle learning progress events
	er.logger.Printf("Processing learning progress: %v", event.Data)

	// Update learning-related services
	return nil
}

func (er *EventRouter) handleServiceRegistered(event *models.Event) error {
	// Handle service registration events
	serviceID, _ := event.Data["service_id"].(string)
	serviceName, _ := event.Data["service_name"].(string)

	er.logger.Printf("Service registered: %s (%s)", serviceName, serviceID)
	return nil
}

func (er *EventRouter) handleServiceStarted(event *models.Event) error {
	// Handle service started events
	serviceID, _ := event.Data["service_id"].(string)
	serviceName, _ := event.Data["service_name"].(string)

	er.logger.Printf("Service started: %s (%s)", serviceName, serviceID)
	return nil
}

func (er *EventRouter) handleServiceStopped(event *models.Event) error {
	// Handle service stopped events
	serviceID, _ := event.Data["service_id"].(string)
	serviceName, _ := event.Data["service_name"].(string)

	er.logger.Printf("Service stopped: %s (%s)", serviceName, serviceID)
	return nil
}

func (er *EventRouter) handleServiceFailed(event *models.Event) error {
	// Handle service failure events
	serviceID, _ := event.Data["service_id"].(string)
	serviceName, _ := event.Data["service_name"].(string)

	er.logger.Printf("Service failed: %s (%s)", serviceName, serviceID)

	// Publish critical alert
	alertEvent := models.NewEvent(models.EventTypeSecurityIncident, "event_router").
		WithData("type", "service_failure").
		WithData("service_id", serviceID).
		WithData("service_name", serviceName).
		WithPriority(models.EventPriorityCritical)

	return er.PublishEvent(alertEvent)
}

func (er *EventRouter) handleServiceHealthCheck(event *models.Event) error {
	// Handle health check events
	serviceID, _ := event.Data["service_id"].(string)
	healthScore, _ := event.Data["health_score"].(float64)

	if healthScore < 0.5 {
		er.logger.Printf("Service %s health degraded: %.2f", serviceID, healthScore)
	}

	return nil
}

func (er *EventRouter) handleSecurityThreat(event *models.Event) error {
	// Handle security threat events
	threatType, _ := event.Data["threat_type"].(string)
	severity, _ := event.Data["severity"].(string)

	er.logger.Printf("Security threat detected: %s (severity: %s)", threatType, severity)

	// Forward to security services
	services, err := er.orchestrator.serviceManager.ListServices("", models.ServiceStatusRunning)
	if err == nil {
		for _, service := range services {
			if service.Name == "security_tutor" || service.Type == models.ServiceTypeInfrastructure {
				er.logger.Printf("Forwarding security threat to service: %s", service.Name)
			}
		}
	}

	return nil
}

func (er *EventRouter) handleSecurityAssessment(event *models.Event) error {
	// Handle security assessment events
	er.logger.Printf("Processing security assessment: %v", event.Data)
	return nil
}

func (er *EventRouter) handleSecurityIncident(event *models.Event) error {
	// Handle security incident events
	incidentType, _ := event.Data["type"].(string)
	er.logger.Printf("Security incident: %s", incidentType)

	// Escalate critical incidents
	if event.Priority == models.EventPriorityCritical {
		er.logger.Printf("CRITICAL security incident requires immediate attention")
	}

	return nil
}
