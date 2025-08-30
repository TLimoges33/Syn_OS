package core

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/syn-os/orchestrator/internal/config"
	"github.com/syn-os/orchestrator/internal/models"
	"github.com/syn-os/orchestrator/internal/storage"
	"github.com/syn-os/orchestrator/pkg/nats"
)

// Orchestrator is the main service orchestrator
type Orchestrator struct {
	config     *config.Config
	db         *storage.PostgresDB
	redis      *storage.RedisClient
	natsClient *nats.Client

	// Service management
	serviceManager *ServiceManager
	healthMonitor  *HealthMonitor
	eventRouter    *EventRouter

	// State
	isRunning bool
	mu        sync.RWMutex
	logger    *log.Logger

	// Background tasks
	ctx    context.Context
	cancel context.CancelFunc
}

// NewOrchestrator creates a new orchestrator instance
func NewOrchestrator(cfg *config.Config, db *storage.PostgresDB, redis *storage.RedisClient) (*Orchestrator, error) {
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	logger := log.Default()
	logger.SetPrefix("[Orchestrator] ")

	// Create NATS client
	natsConfig := nats.Config{
		URL:           cfg.NATS.URL,
		Username:      cfg.NATS.Username,
		Password:      cfg.NATS.Password,
		MaxReconnect:  cfg.NATS.MaxReconnect,
		ReconnectWait: 5 * time.Second,
		Timeout:       30 * time.Second,
	}

	natsClient, err := nats.NewClient(natsConfig, logger)
	if err != nil {
		return nil, fmt.Errorf("failed to create NATS client: %w", err)
	}

	orchestrator := &Orchestrator{
		config:     cfg,
		db:         db,
		redis:      redis,
		natsClient: natsClient,
		logger:     logger,
	}

	// Initialize components
	orchestrator.serviceManager = NewServiceManager(orchestrator)
	orchestrator.healthMonitor = NewHealthMonitor(orchestrator)
	orchestrator.eventRouter = NewEventRouter(orchestrator)

	return orchestrator, nil
}

// Start starts the orchestrator and all its components
func (o *Orchestrator) Start(ctx context.Context) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	if o.isRunning {
		return fmt.Errorf("orchestrator is already running")
	}

	o.ctx, o.cancel = context.WithCancel(ctx)
	o.logger.Println("Starting Syn_OS Service Orchestrator...")

	// Start service manager
	if err := o.serviceManager.Start(o.ctx); err != nil {
		return fmt.Errorf("failed to start service manager: %w", err)
	}

	// Start health monitor
	if err := o.healthMonitor.Start(o.ctx); err != nil {
		return fmt.Errorf("failed to start health monitor: %w", err)
	}

	// Start event router
	if err := o.eventRouter.Start(o.ctx); err != nil {
		return fmt.Errorf("failed to start event router: %w", err)
	}

	// Subscribe to consciousness events
	if err := o.subscribeToConsciousnessEvents(); err != nil {
		return fmt.Errorf("failed to subscribe to consciousness events: %w", err)
	}

	o.isRunning = true
	o.logger.Println("Service Orchestrator started successfully")

	return nil
}

// Stop stops the orchestrator and all its components
func (o *Orchestrator) Stop() {
	o.mu.Lock()
	defer o.mu.Unlock()

	if !o.isRunning {
		return
	}

	o.logger.Println("Stopping Service Orchestrator...")

	// Cancel context to stop all background tasks
	if o.cancel != nil {
		o.cancel()
	}

	// Stop components
	if o.eventRouter != nil {
		o.eventRouter.Stop()
	}
	if o.healthMonitor != nil {
		o.healthMonitor.Stop()
	}
	if o.serviceManager != nil {
		o.serviceManager.Stop()
	}

	// Close NATS connection
	if o.natsClient != nil {
		o.natsClient.Close()
	}

	o.isRunning = false
	o.logger.Println("Service Orchestrator stopped")
}

// IsRunning returns true if the orchestrator is running
func (o *Orchestrator) IsRunning() bool {
	o.mu.RLock()
	defer o.mu.RUnlock()
	return o.isRunning
}

// Service management methods

// RegisterService registers a new service
func (o *Orchestrator) RegisterService(registration *models.ServiceRegistration) (*models.Service, error) {
	return o.serviceManager.RegisterService(registration)
}

// UnregisterService unregisters a service
func (o *Orchestrator) UnregisterService(serviceID string) error {
	return o.serviceManager.UnregisterService(serviceID)
}

// StartService starts a service
func (o *Orchestrator) StartService(serviceID string) error {
	return o.serviceManager.StartService(serviceID)
}

// StopService stops a service
func (o *Orchestrator) StopService(serviceID string) error {
	return o.serviceManager.StopService(serviceID)
}

// RestartService restarts a service
func (o *Orchestrator) RestartService(serviceID string) error {
	return o.serviceManager.RestartService(serviceID)
}

// GetService retrieves a service by ID
func (o *Orchestrator) GetService(serviceID string) (*models.Service, error) {
	return o.serviceManager.GetService(serviceID)
}

// ListServices lists all services with optional filtering
func (o *Orchestrator) ListServices(serviceType models.ServiceType, status models.ServiceStatus) ([]*models.Service, error) {
	return o.serviceManager.ListServices(serviceType, status)
}

// UpdateService updates a service
func (o *Orchestrator) UpdateService(serviceID string, update *models.ServiceUpdate) (*models.Service, error) {
	return o.serviceManager.UpdateService(serviceID, update)
}

// Health and monitoring methods

// GetServiceHealth gets health status for a service
func (o *Orchestrator) GetServiceHealth(serviceID string) (*models.HealthCheck, error) {
	return o.healthMonitor.GetServiceHealth(serviceID)
}

// GetSystemHealth gets overall system health
func (o *Orchestrator) GetSystemHealth() (map[string]interface{}, error) {
	return o.healthMonitor.GetSystemHealth()
}

// GetServiceMetrics gets metrics for a service
func (o *Orchestrator) GetServiceMetrics(serviceID string, since time.Time) ([]*models.ServiceMetrics, error) {
	return o.db.GetServiceMetrics(serviceID, since, 100)
}

// Event management methods

// PublishEvent publishes an event
func (o *Orchestrator) PublishEvent(event *models.Event) error {
	return o.eventRouter.PublishEvent(event)
}

// SubscribeToEvents subscribes to events
func (o *Orchestrator) SubscribeToEvents(filter models.EventFilter, handler func(*models.Event) error) (string, error) {
	return o.eventRouter.SubscribeToEvents(filter, handler)
}

// UnsubscribeFromEvents unsubscribes from events
func (o *Orchestrator) UnsubscribeFromEvents(subscriptionID string) error {
	return o.eventRouter.UnsubscribeFromEvents(subscriptionID)
}

// Configuration methods

// GetConfiguration gets service configuration
func (o *Orchestrator) GetConfiguration(serviceID string) (map[string]interface{}, error) {
	// Try cache first
	if config, err := o.redis.GetCachedConfiguration(serviceID); err == nil && config != nil {
		return config, nil
	}

	// Get from database
	service, err := o.db.GetService(serviceID)
	if err != nil {
		return nil, fmt.Errorf("failed to get service: %w", err)
	}
	if service == nil {
		return nil, fmt.Errorf("service not found")
	}

	// Cache the configuration
	o.redis.CacheConfiguration(serviceID, service.Config, 5*time.Minute)

	return service.Config, nil
}

// UpdateConfiguration updates service configuration
func (o *Orchestrator) UpdateConfiguration(serviceID string, config map[string]interface{}) error {
	service, err := o.db.GetService(serviceID)
	if err != nil {
		return fmt.Errorf("failed to get service: %w", err)
	}
	if service == nil {
		return fmt.Errorf("service not found")
	}

	// Update configuration
	service.Config = config
	if err := o.db.UpdateService(service); err != nil {
		return fmt.Errorf("failed to update service: %w", err)
	}

	// Invalidate cache
	o.redis.InvalidateServiceCache(serviceID)

	// Publish configuration change event
	event := models.NewEvent(models.EventTypeConfigurationChange, "orchestrator").
		WithData("service_id", serviceID).
		WithData("config", config).
		WithPriority(models.EventPriorityNormal)

	return o.PublishEvent(event)
}

// Status and information methods

// GetStatus returns the orchestrator status
func (o *Orchestrator) GetStatus() map[string]interface{} {
	o.mu.RLock()
	defer o.mu.RUnlock()

	status := map[string]interface{}{
		"running":    o.isRunning,
		"version":    "1.0.0",
		"start_time": time.Now().Format(time.RFC3339),
	}

	// Add component status
	if o.serviceManager != nil {
		status["service_manager"] = o.serviceManager.GetStatus()
	}
	if o.healthMonitor != nil {
		status["health_monitor"] = o.healthMonitor.GetStatus()
	}
	if o.eventRouter != nil {
		status["event_router"] = o.eventRouter.GetStatus()
	}

	// Add NATS connection status
	if o.natsClient != nil {
		status["nats"] = o.natsClient.GetConnectionStatus()
	}

	return status
}

// GetMetrics returns orchestrator metrics
func (o *Orchestrator) GetMetrics() (map[string]interface{}, error) {
	metrics := make(map[string]interface{})

	// Service metrics
	if o.serviceManager != nil {
		serviceMetrics, err := o.serviceManager.GetMetrics()
		if err == nil {
			metrics["services"] = serviceMetrics
		}
	}

	// Health metrics
	if o.healthMonitor != nil {
		healthMetrics, err := o.healthMonitor.GetMetrics()
		if err == nil {
			metrics["health"] = healthMetrics
		}
	}

	// Event metrics
	if o.eventRouter != nil {
		eventMetrics, err := o.eventRouter.GetMetrics()
		if err == nil {
			metrics["events"] = eventMetrics
		}
	}

	// NATS metrics
	if o.natsClient != nil {
		natsMetrics, err := o.natsClient.GetStreamInfo()
		if err == nil {
			metrics["nats"] = natsMetrics
		}
	}

	// System metrics
	systemHealth, err := o.db.GetSystemHealth()
	if err == nil {
		metrics["system"] = systemHealth
	}

	return metrics, nil
}

// Private methods

// subscribeToConsciousnessEvents subscribes to consciousness system events
func (o *Orchestrator) subscribeToConsciousnessEvents() error {
	_, err := o.natsClient.SubscribeToConsciousnessEvents(func(event *models.Event) error {
		o.logger.Printf("Received consciousness event: %s from %s", event.Type, event.Source)

		// Handle consciousness events
		switch event.Type {
		case models.EventTypeConsciousnessUpdate:
			return o.handleConsciousnessUpdate(event)
		case models.EventTypeNeuralEvolution:
			return o.handleNeuralEvolution(event)
		case models.EventTypeContextUpdate:
			return o.handleContextUpdate(event)
		case models.EventTypeLearningProgress:
			return o.handleLearningProgress(event)
		default:
			o.logger.Printf("Unknown consciousness event type: %s", event.Type)
		}

		return nil
	})

	if err != nil {
		return fmt.Errorf("failed to subscribe to consciousness events: %w", err)
	}

	o.logger.Println("Subscribed to consciousness events")
	return nil
}

// Event handlers for consciousness events

func (o *Orchestrator) handleConsciousnessUpdate(event *models.Event) error {
	// Handle consciousness level updates
	o.logger.Printf("Processing consciousness update: %v", event.Data)

	// Update service priorities based on consciousness level
	if consciousnessLevel, ok := event.Data["consciousness_level"].(float64); ok {
		return o.adjustServicePriorities(consciousnessLevel)
	}

	return nil
}

func (o *Orchestrator) handleNeuralEvolution(event *models.Event) error {
	// Handle neural evolution events
	o.logger.Printf("Processing neural evolution: %v", event.Data)

	// Potentially adjust resource allocation based on evolution
	return o.optimizeResourceAllocation(event)
}

func (o *Orchestrator) handleContextUpdate(event *models.Event) error {
	// Handle context updates
	o.logger.Printf("Processing context update: %v", event.Data)

	// Update service configurations based on context
	return o.updateServiceContexts(event)
}

func (o *Orchestrator) handleLearningProgress(event *models.Event) error {
	// Handle learning progress events
	o.logger.Printf("Processing learning progress: %v", event.Data)

	// Adjust security tutor difficulty or other learning-related services
	return o.adjustLearningServices(event)
}

// Helper methods for consciousness event handling

func (o *Orchestrator) adjustServicePriorities(consciousnessLevel float64) error {
	// Adjust service priorities based on consciousness level
	services, err := o.ListServices("", "")
	if err != nil {
		return err
	}

	for _, service := range services {
		// Higher consciousness level = higher priority for intelligence services
		if service.Type == models.ServiceTypeIntelligence {
			// Implement priority adjustment logic
			o.logger.Printf("Adjusting priority for service %s based on consciousness level %.2f",
				service.Name, consciousnessLevel)
		}
	}

	return nil
}

func (o *Orchestrator) optimizeResourceAllocation(event *models.Event) error {
	// Optimize resource allocation based on neural evolution
	o.logger.Printf("Optimizing resource allocation based on neural evolution")

	// Publish resource allocation event
	resourceEvent := models.NewEvent(models.EventTypeResourceAllocation, "orchestrator").
		WithData("trigger", "neural_evolution").
		WithData("optimization_data", event.Data).
		WithPriority(models.EventPriorityNormal)

	return o.PublishEvent(resourceEvent)
}

func (o *Orchestrator) updateServiceContexts(event *models.Event) error {
	// Update service contexts based on user context changes
	o.logger.Printf("Updating service contexts")

	// Find services that need context updates
	services, err := o.ListServices("", models.ServiceStatusRunning)
	if err != nil {
		return err
	}

	for _, service := range services {
		if service.Type == models.ServiceTypeConsciousness ||
			service.Type == models.ServiceTypeIntelligence {
			// Update service with new context
			update := &models.ServiceUpdate{
				Metadata: map[string]string{
					"last_context_update": time.Now().Format(time.RFC3339),
				},
			}
			o.UpdateService(service.ID, update)
		}
	}

	return nil
}

func (o *Orchestrator) adjustLearningServices(event *models.Event) error {
	// Adjust learning-related services based on progress
	o.logger.Printf("Adjusting learning services")

	// Find security tutor and other learning services
	services, err := o.ListServices("", models.ServiceStatusRunning)
	if err != nil {
		return err
	}

	for _, service := range services {
		if service.Name == "security_tutor" {
			// Adjust difficulty or content based on learning progress
			config := service.Config
			if config == nil {
				config = make(map[string]interface{})
			}

			config["last_progress_update"] = time.Now().Format(time.RFC3339)
			config["progress_data"] = event.Data

			return o.UpdateConfiguration(service.ID, config)
		}
	}

	return nil
}

// Getter methods for components (used by API handlers)

func (o *Orchestrator) GetServiceManager() *ServiceManager {
	return o.serviceManager
}

func (o *Orchestrator) GetHealthMonitor() *HealthMonitor {
	return o.healthMonitor
}

func (o *Orchestrator) GetEventRouter() *EventRouter {
	return o.eventRouter
}

func (o *Orchestrator) GetNATSClient() *nats.Client {
	return o.natsClient
}

func (o *Orchestrator) GetDB() *storage.PostgresDB {
	return o.db
}

func (o *Orchestrator) GetRedis() *storage.RedisClient {
	return o.redis
}

func (o *Orchestrator) GetConfig() *config.Config {
	return o.config
}
