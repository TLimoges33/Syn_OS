package nats

import (
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/syn-os/orchestrator/internal/models"
)

// Client wraps NATS connection and provides high-level messaging operations
type Client struct {
	conn          *nats.Conn
	js            nats.JetStreamContext
	subscriptions map[string]*nats.Subscription
	mu            sync.RWMutex
	logger        *log.Logger
}

// Config holds NATS client configuration
type Config struct {
	URL           string
	Username      string
	Password      string
	MaxReconnect  int
	ReconnectWait time.Duration
	Timeout       time.Duration
}

// NewClient creates a new NATS client
func NewClient(config Config, logger *log.Logger) (*Client, error) {
	if logger == nil {
		logger = log.Default()
	}

	// Setup connection options
	opts := []nats.Option{
		nats.Name("synos-orchestrator"),
		nats.MaxReconnects(config.MaxReconnect),
		nats.ReconnectWait(config.ReconnectWait),
		nats.Timeout(config.Timeout),
		nats.DisconnectErrHandler(func(nc *nats.Conn, err error) {
			logger.Printf("NATS disconnected: %v", err)
		}),
		nats.ReconnectHandler(func(nc *nats.Conn) {
			logger.Printf("NATS reconnected to %v", nc.ConnectedUrl())
		}),
		nats.ClosedHandler(func(nc *nats.Conn) {
			logger.Printf("NATS connection closed")
		}),
	}

	// Add authentication if provided
	if config.Username != "" && config.Password != "" {
		opts = append(opts, nats.UserInfo(config.Username, config.Password))
	}

	// Connect to NATS
	conn, err := nats.Connect(config.URL, opts...)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}

	// Create JetStream context
	js, err := conn.JetStream()
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("failed to create JetStream context: %w", err)
	}

	client := &Client{
		conn:          conn,
		js:            js,
		subscriptions: make(map[string]*nats.Subscription),
		logger:        logger,
	}

	// Initialize streams
	if err := client.initializeStreams(); err != nil {
		client.Close()
		return nil, fmt.Errorf("failed to initialize streams: %w", err)
	}

	return client, nil
}

// Close closes the NATS connection and all subscriptions
func (c *Client) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Unsubscribe from all subscriptions
	for _, sub := range c.subscriptions {
		sub.Unsubscribe()
	}
	c.subscriptions = make(map[string]*nats.Subscription)

	// Close connection
	if c.conn != nil {
		c.conn.Close()
	}

	return nil
}

// initializeStreams creates necessary JetStream streams
func (c *Client) initializeStreams() error {
	streams := []struct {
		name     string
		subjects []string
		maxAge   time.Duration
	}{
		{
			name:     "CONSCIOUSNESS_EVENTS",
			subjects: []string{"consciousness.events.*"},
			maxAge:   24 * time.Hour,
		},
		{
			name:     "SERVICE_EVENTS",
			subjects: []string{"services.*"},
			maxAge:   7 * 24 * time.Hour,
		},
		{
			name:     "HEALTH_EVENTS",
			subjects: []string{"health.*"},
			maxAge:   1 * time.Hour,
		},
		{
			name:     "METRICS_EVENTS",
			subjects: []string{"metrics.*"},
			maxAge:   6 * time.Hour,
		},
		{
			name:     "SECURITY_EVENTS",
			subjects: []string{"security.*"},
			maxAge:   30 * 24 * time.Hour,
		},
	}

	for _, stream := range streams {
		_, err := c.js.StreamInfo(stream.name)
		if err != nil {
			// Stream doesn't exist, create it
			_, err = c.js.AddStream(&nats.StreamConfig{
				Name:     stream.name,
				Subjects: stream.subjects,
				MaxAge:   stream.maxAge,
				Storage:  nats.FileStorage,
				Replicas: 1,
			})
			if err != nil {
				return fmt.Errorf("failed to create stream %s: %w", stream.name, err)
			}
			c.logger.Printf("Created JetStream stream: %s", stream.name)
		}
	}

	return nil
}

// PublishEvent publishes an event to NATS
func (c *Client) PublishEvent(event *models.Event) error {
	subject := c.getSubjectForEvent(event)

	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	// Publish to JetStream for persistence
	_, err = c.js.Publish(subject, data)
	if err != nil {
		return fmt.Errorf("failed to publish event to %s: %w", subject, err)
	}

	c.logger.Printf("Published event %s to %s", event.ID, subject)
	return nil
}

// PublishServiceEvent publishes a service lifecycle event
func (c *Client) PublishServiceEvent(serviceID, action string, status models.ServiceStatus, data map[string]interface{}) error {
	event := models.NewEvent(models.EventTypeServiceRegistered, "orchestrator").
		WithData("service_id", serviceID).
		WithData("action", action).
		WithData("status", status).
		WithPriority(models.EventPriorityNormal)

	if data != nil {
		for k, v := range data {
			event.WithData(k, v)
		}
	}

	return c.PublishEvent(event)
}

// PublishHealthEvent publishes a health check event
func (c *Client) PublishHealthEvent(serviceID string, healthCheck *models.HealthCheck) error {
	event := models.NewEvent(models.EventTypeServiceHealthCheck, "orchestrator").
		WithData("service_id", serviceID).
		WithData("status", healthCheck.Status).
		WithData("health_score", healthCheck.HealthScore).
		WithData("timestamp", healthCheck.Timestamp).
		WithPriority(models.EventPriorityLow)

	if healthCheck.Details != nil {
		event.WithData("details", healthCheck.Details)
	}

	if healthCheck.Error != nil {
		event.WithData("error", *healthCheck.Error)
		event.WithPriority(models.EventPriorityHigh)
	}

	return c.PublishEvent(event)
}

// SubscribeToEvents subscribes to events matching the filter
func (c *Client) SubscribeToEvents(filter models.EventFilter, handler func(*models.Event) error) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Generate subscription ID
	subID := fmt.Sprintf("sub_%d", time.Now().UnixNano())

	// Determine subject pattern based on filter
	subject := c.getSubjectPattern(filter)

	// Create subscription
	sub, err := c.js.Subscribe(subject, func(msg *nats.Msg) {
		var event models.Event
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			c.logger.Printf("Failed to unmarshal event: %v", err)
			msg.Nak()
			return
		}

		// Apply filter
		if !filter.Matches(&event) {
			msg.Ack()
			return
		}

		// Handle event
		if err := handler(&event); err != nil {
			c.logger.Printf("Event handler error: %v", err)
			msg.Nak()
			return
		}

		msg.Ack()
	}, nats.Durable(subID))

	if err != nil {
		return "", fmt.Errorf("failed to subscribe to %s: %w", subject, err)
	}

	c.subscriptions[subID] = sub
	c.logger.Printf("Created subscription %s for subject %s", subID, subject)

	return subID, nil
}

// SubscribeToServiceEvents subscribes to service lifecycle events
func (c *Client) SubscribeToServiceEvents(serviceID string, handler func(*models.Event) error) (string, error) {
	filter := models.EventFilter{
		Types: []models.EventType{
			models.EventTypeServiceRegistered,
			models.EventTypeServiceStarted,
			models.EventTypeServiceStopped,
			models.EventTypeServiceFailed,
		},
	}

	if serviceID != "" {
		filter.Sources = []string{serviceID}
	}

	return c.SubscribeToEvents(filter, handler)
}

// SubscribeToHealthEvents subscribes to health check events
func (c *Client) SubscribeToHealthEvents(serviceID string, handler func(*models.Event) error) (string, error) {
	filter := models.EventFilter{
		Types: []models.EventType{models.EventTypeServiceHealthCheck},
	}

	if serviceID != "" {
		filter.Sources = []string{serviceID}
	}

	return c.SubscribeToEvents(filter, handler)
}

// SubscribeToConsciousnessEvents subscribes to consciousness system events
func (c *Client) SubscribeToConsciousnessEvents(handler func(*models.Event) error) (string, error) {
	filter := models.EventFilter{
		Types: []models.EventType{
			models.EventTypeConsciousnessUpdate,
			models.EventTypeNeuralEvolution,
			models.EventTypeContextUpdate,
			models.EventTypeLearningProgress,
		},
	}

	return c.SubscribeToEvents(filter, handler)
}

// Unsubscribe removes a subscription
func (c *Client) Unsubscribe(subscriptionID string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	sub, exists := c.subscriptions[subscriptionID]
	if !exists {
		return fmt.Errorf("subscription %s not found", subscriptionID)
	}

	if err := sub.Unsubscribe(); err != nil {
		return fmt.Errorf("failed to unsubscribe %s: %w", subscriptionID, err)
	}

	delete(c.subscriptions, subscriptionID)
	c.logger.Printf("Unsubscribed from %s", subscriptionID)

	return nil
}

// Request sends a request and waits for a response
func (c *Client) Request(subject string, data []byte, timeout time.Duration) (*nats.Msg, error) {
	return c.conn.Request(subject, data, timeout)
}

// RequestEvent sends an event as a request and waits for a response
func (c *Client) RequestEvent(event *models.Event, timeout time.Duration) (*models.Event, error) {
	subject := c.getSubjectForEvent(event)

	data, err := json.Marshal(event)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal event: %w", err)
	}

	msg, err := c.conn.Request(subject, data, timeout)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %w", err)
	}

	var response models.Event
	if err := json.Unmarshal(msg.Data, &response); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &response, nil
}

// GetConnectionStatus returns the current connection status
func (c *Client) GetConnectionStatus() map[string]interface{} {
	status := map[string]interface{}{
		"connected":          c.conn.IsConnected(),
		"reconnecting":       c.conn.IsReconnecting(),
		"closed":             c.conn.IsClosed(),
		"servers":            c.conn.Servers(),
		"discovered_servers": c.conn.DiscoveredServers(),
	}

	if c.conn.IsConnected() {
		status["connected_url"] = c.conn.ConnectedUrl()
		status["connected_server_id"] = c.conn.ConnectedServerId()
	}

	c.mu.RLock()
	status["active_subscriptions"] = len(c.subscriptions)
	c.mu.RUnlock()

	return status
}

// GetStreamInfo returns information about JetStream streams
func (c *Client) GetStreamInfo() (map[string]interface{}, error) {
	streams := make(map[string]interface{})

	streamNames := []string{
		"CONSCIOUSNESS_EVENTS",
		"SERVICE_EVENTS",
		"HEALTH_EVENTS",
		"METRICS_EVENTS",
		"SECURITY_EVENTS",
	}

	for _, name := range streamNames {
		info, err := c.js.StreamInfo(name)
		if err != nil {
			streams[name] = map[string]interface{}{
				"error": err.Error(),
			}
			continue
		}

		streams[name] = map[string]interface{}{
			"messages":  info.State.Msgs,
			"bytes":     info.State.Bytes,
			"first_seq": info.State.FirstSeq,
			"last_seq":  info.State.LastSeq,
			"consumers": info.State.Consumers,
			"subjects":  info.Config.Subjects,
			"max_age":   info.Config.MaxAge,
			"storage":   info.Config.Storage.String(),
		}
	}

	return streams, nil
}

// Helper methods

// getSubjectForEvent determines the NATS subject for an event
func (c *Client) getSubjectForEvent(event *models.Event) string {
	switch event.Type {
	case models.EventTypeServiceRegistered, models.EventTypeServiceStarted,
		models.EventTypeServiceStopped, models.EventTypeServiceFailed:
		return fmt.Sprintf("services.lifecycle.%s", event.Source)
	case models.EventTypeServiceHealthCheck:
		return fmt.Sprintf("health.%s", event.Source)
	case models.EventTypeConsciousnessUpdate, models.EventTypeNeuralEvolution,
		models.EventTypeContextUpdate, models.EventTypeLearningProgress:
		return fmt.Sprintf("consciousness.events.%s", event.Type)
	case models.EventTypeSecurityThreat, models.EventTypeSecurityAssessment,
		models.EventTypeSecurityIncident:
		return fmt.Sprintf("security.%s", event.Type)
	case models.EventTypeSystemMetrics, models.EventTypeResourceAllocation:
		return fmt.Sprintf("metrics.%s", event.Source)
	default:
		return fmt.Sprintf("events.%s", event.Type)
	}
}

// getSubjectPattern determines the NATS subject pattern for a filter
func (c *Client) getSubjectPattern(filter models.EventFilter) string {
	if len(filter.Types) == 1 {
		// Single event type, use specific subject
		event := &models.Event{Type: filter.Types[0]}
		if len(filter.Sources) == 1 {
			event.Source = filter.Sources[0]
		}
		return c.getSubjectForEvent(event)
	}

	// Multiple types or no specific type, use wildcard
	return ">"
}
