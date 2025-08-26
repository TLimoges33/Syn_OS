package core

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/syn-os/orchestrator/internal/models"
)

// ServiceManager manages service lifecycle and operations
type ServiceManager struct {
	orchestrator *Orchestrator
	services     map[string]*models.Service
	mu           sync.RWMutex
	logger       *log.Logger

	// Background tasks
	ctx    context.Context
	cancel context.CancelFunc
}

// NewServiceManager creates a new service manager
func NewServiceManager(orchestrator *Orchestrator) *ServiceManager {
	logger := log.Default()
	logger.SetPrefix("[ServiceManager] ")

	return &ServiceManager{
		orchestrator: orchestrator,
		services:     make(map[string]*models.Service),
		logger:       logger,
	}
}

// Start starts the service manager
func (sm *ServiceManager) Start(ctx context.Context) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	sm.ctx, sm.cancel = context.WithCancel(ctx)
	sm.logger.Println("Starting Service Manager...")

	// Load existing services from database
	if err := sm.loadServices(); err != nil {
		return fmt.Errorf("failed to load services: %w", err)
	}

	// Start background tasks
	go sm.serviceMonitorLoop()

	sm.logger.Printf("Service Manager started with %d services", len(sm.services))
	return nil
}

// Stop stops the service manager
func (sm *ServiceManager) Stop() {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	if sm.cancel != nil {
		sm.cancel()
	}

	sm.logger.Println("Service Manager stopped")
}

// RegisterService registers a new service
func (sm *ServiceManager) RegisterService(registration *models.ServiceRegistration) (*models.Service, error) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	// Check if service already exists
	existing, err := sm.orchestrator.db.GetServiceByName(registration.Name)
	if err != nil {
		return nil, fmt.Errorf("failed to check existing service: %w", err)
	}
	if existing != nil {
		return nil, fmt.Errorf("service with name %s already exists", registration.Name)
	}

	// Create new service
	service := &models.Service{
		ID:           uuid.New().String(),
		Name:         registration.Name,
		Type:         registration.Type,
		Version:      registration.Version,
		Status:       models.ServiceStatusStopped,
		HealthScore:  0.0,
		Config:       registration.Config,
		Environment:  registration.Environment,
		HealthURL:    registration.HealthURL,
		Endpoints:    registration.Endpoints,
		Dependencies: registration.Dependencies,
		Metadata:     registration.Metadata,
		Labels:       registration.Labels,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	// Save to database
	if err := sm.orchestrator.db.CreateService(service); err != nil {
		return nil, fmt.Errorf("failed to create service in database: %w", err)
	}

	// Add to local cache
	sm.services[service.ID] = service

	// Cache in Redis
	sm.orchestrator.redis.CacheService(service, 10*time.Minute)

	// Publish service registration event
	event := models.NewEvent(models.EventTypeServiceRegistered, "orchestrator").
		WithData("service_id", service.ID).
		WithData("service_name", service.Name).
		WithData("service_type", service.Type).
		WithPriority(models.EventPriorityNormal)

	sm.orchestrator.natsClient.PublishEvent(event)

	sm.logger.Printf("Registered service: %s (%s)", service.Name, service.ID)
	return service, nil
}

// UnregisterService unregisters a service
func (sm *ServiceManager) UnregisterService(serviceID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	service, exists := sm.services[serviceID]
	if !exists {
		return fmt.Errorf("service %s not found", serviceID)
	}

	// Stop service if running
	if service.IsRunning() {
		if err := sm.stopServiceInternal(service); err != nil {
			sm.logger.Printf("Failed to stop service %s during unregistration: %v", serviceID, err)
		}
	}

	// Remove from database
	if err := sm.orchestrator.db.DeleteService(serviceID); err != nil {
		return fmt.Errorf("failed to delete service from database: %w", err)
	}

	// Remove from cache
	delete(sm.services, serviceID)
	sm.orchestrator.redis.InvalidateServiceCache(serviceID)

	sm.logger.Printf("Unregistered service: %s (%s)", service.Name, serviceID)
	return nil
}

// StartService starts a service
func (sm *ServiceManager) StartService(serviceID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	service, exists := sm.services[serviceID]
	if !exists {
		return fmt.Errorf("service %s not found", serviceID)
	}

	if !service.CanStart() {
		return fmt.Errorf("service %s cannot be started (current status: %s)", serviceID, service.Status)
	}

	return sm.startServiceInternal(service)
}

// StopService stops a service
func (sm *ServiceManager) StopService(serviceID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	service, exists := sm.services[serviceID]
	if !exists {
		return fmt.Errorf("service %s not found", serviceID)
	}

	if !service.CanStop() {
		return fmt.Errorf("service %s cannot be stopped (current status: %s)", serviceID, service.Status)
	}

	return sm.stopServiceInternal(service)
}

// RestartService restarts a service
func (sm *ServiceManager) RestartService(serviceID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	service, exists := sm.services[serviceID]
	if !exists {
		return fmt.Errorf("service %s not found", serviceID)
	}

	// Stop if running
	if service.IsRunning() {
		if err := sm.stopServiceInternal(service); err != nil {
			return fmt.Errorf("failed to stop service: %w", err)
		}

		// Wait a moment for clean shutdown
		time.Sleep(2 * time.Second)
	}

	// Start the service
	return sm.startServiceInternal(service)
}

// GetService retrieves a service by ID
func (sm *ServiceManager) GetService(serviceID string) (*models.Service, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	// Try local cache first
	if service, exists := sm.services[serviceID]; exists {
		return service, nil
	}

	// Try Redis cache
	if service, err := sm.orchestrator.redis.GetCachedService(serviceID); err == nil && service != nil {
		sm.services[serviceID] = service
		return service, nil
	}

	// Get from database
	service, err := sm.orchestrator.db.GetService(serviceID)
	if err != nil {
		return nil, fmt.Errorf("failed to get service from database: %w", err)
	}
	if service == nil {
		return nil, fmt.Errorf("service not found")
	}

	// Cache the service
	sm.services[serviceID] = service
	sm.orchestrator.redis.CacheService(service, 10*time.Minute)

	return service, nil
}

// ListServices lists all services with optional filtering
func (sm *ServiceManager) ListServices(serviceType models.ServiceType, status models.ServiceStatus) ([]*models.Service, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	// Try cache first
	cacheKey := fmt.Sprintf("%s_%s", serviceType, status)
	if services, err := sm.orchestrator.redis.GetCachedServiceList(cacheKey); err == nil && services != nil {
		return services, nil
	}

	// Get from database
	services, err := sm.orchestrator.db.ListServices(serviceType, status)
	if err != nil {
		return nil, fmt.Errorf("failed to list services: %w", err)
	}

	// Update local cache
	for _, service := range services {
		sm.services[service.ID] = service
	}

	// Cache the list
	sm.orchestrator.redis.CacheServiceList(services, cacheKey, 5*time.Minute)

	return services, nil
}

// UpdateService updates a service
func (sm *ServiceManager) UpdateService(serviceID string, update *models.ServiceUpdate) (*models.Service, error) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	service, exists := sm.services[serviceID]
	if !exists {
		return nil, fmt.Errorf("service %s not found", serviceID)
	}

	// Apply updates
	if update.Status != nil {
		service.Status = *update.Status
	}
	if update.HealthScore != nil {
		service.HealthScore = *update.HealthScore
	}
	if update.Config != nil {
		service.Config = update.Config
	}
	if update.Environment != nil {
		service.Environment = update.Environment
	}
	if update.Metadata != nil {
		service.Metadata = update.Metadata
	}
	if update.Labels != nil {
		service.Labels = update.Labels
	}
	if update.CPUUsage != nil {
		service.CPUUsage = *update.CPUUsage
	}
	if update.MemoryUsage != nil {
		service.MemoryUsage = *update.MemoryUsage
	}

	service.UpdatedAt = time.Now()

	// Save to database
	if err := sm.orchestrator.db.UpdateService(service); err != nil {
		return nil, fmt.Errorf("failed to update service in database: %w", err)
	}

	// Update cache
	sm.orchestrator.redis.CacheService(service, 10*time.Minute)

	sm.logger.Printf("Updated service: %s (%s)", service.Name, serviceID)
	return service, nil
}

// GetStatus returns service manager status
func (sm *ServiceManager) GetStatus() map[string]interface{} {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	statusCounts := make(map[string]int)
	typeCounts := make(map[string]int)

	for _, service := range sm.services {
		statusCounts[string(service.Status)]++
		typeCounts[string(service.Type)]++
	}

	return map[string]interface{}{
		"total_services": len(sm.services),
		"status_counts":  statusCounts,
		"type_counts":    typeCounts,
		"running":        sm.ctx != nil,
	}
}

// GetMetrics returns service manager metrics
func (sm *ServiceManager) GetMetrics() (map[string]interface{}, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	metrics := map[string]interface{}{
		"total_services":       len(sm.services),
		"services_by_status":   make(map[string]int),
		"services_by_type":     make(map[string]int),
		"average_health_score": 0.0,
		"total_cpu_usage":      0.0,
		"total_memory_usage":   int64(0),
	}

	var totalHealthScore float64
	var healthyServices int

	for _, service := range sm.services {
		// Count by status
		statusCounts := metrics["services_by_status"].(map[string]int)
		statusCounts[string(service.Status)]++

		// Count by type
		typeCounts := metrics["services_by_type"].(map[string]int)
		typeCounts[string(service.Type)]++

		// Aggregate health scores
		if service.HealthScore > 0 {
			totalHealthScore += service.HealthScore
			healthyServices++
		}

		// Aggregate resource usage
		metrics["total_cpu_usage"] = metrics["total_cpu_usage"].(float64) + service.CPUUsage
		metrics["total_memory_usage"] = metrics["total_memory_usage"].(int64) + service.MemoryUsage
	}

	// Calculate average health score
	if healthyServices > 0 {
		metrics["average_health_score"] = totalHealthScore / float64(healthyServices)
	}

	return metrics, nil
}

// Private methods

// loadServices loads services from database into memory
func (sm *ServiceManager) loadServices() error {
	services, err := sm.orchestrator.db.ListServices("", "")
	if err != nil {
		return fmt.Errorf("failed to load services from database: %w", err)
	}

	for _, service := range services {
		sm.services[service.ID] = service
	}

	sm.logger.Printf("Loaded %d services from database", len(services))
	return nil
}

// startServiceInternal starts a service (internal method, assumes lock is held)
func (sm *ServiceManager) startServiceInternal(service *models.Service) error {
	sm.logger.Printf("Starting service: %s (%s)", service.Name, service.ID)

	// Check dependencies
	if err := sm.checkDependencies(service); err != nil {
		return fmt.Errorf("dependency check failed: %w", err)
	}

	// Update status
	service.Status = models.ServiceStatusStarting
	now := time.Now()
	service.StartedAt = &now
	service.UpdatedAt = now

	// Save to database
	if err := sm.orchestrator.db.UpdateService(service); err != nil {
		return fmt.Errorf("failed to update service status: %w", err)
	}

	// Publish service started event
	event := models.NewEvent(models.EventTypeServiceStarted, "orchestrator").
		WithData("service_id", service.ID).
		WithData("service_name", service.Name).
		WithPriority(models.EventPriorityNormal)

	sm.orchestrator.natsClient.PublishEvent(event)

	// Simulate service startup (in real implementation, this would start the actual service)
	go func() {
		time.Sleep(2 * time.Second) // Simulate startup time

		sm.mu.Lock()
		service.Status = models.ServiceStatusRunning
		service.HealthScore = 1.0
		service.UpdatedAt = time.Now()
		sm.orchestrator.db.UpdateService(service)
		sm.mu.Unlock()

		sm.logger.Printf("Service started successfully: %s (%s)", service.Name, service.ID)
	}()

	return nil
}

// stopServiceInternal stops a service (internal method, assumes lock is held)
func (sm *ServiceManager) stopServiceInternal(service *models.Service) error {
	sm.logger.Printf("Stopping service: %s (%s)", service.Name, service.ID)

	// Update status
	service.Status = models.ServiceStatusStopping
	service.UpdatedAt = time.Now()

	// Save to database
	if err := sm.orchestrator.db.UpdateService(service); err != nil {
		return fmt.Errorf("failed to update service status: %w", err)
	}

	// Publish service stopped event
	event := models.NewEvent(models.EventTypeServiceStopped, "orchestrator").
		WithData("service_id", service.ID).
		WithData("service_name", service.Name).
		WithPriority(models.EventPriorityNormal)

	sm.orchestrator.natsClient.PublishEvent(event)

	// Simulate service shutdown (in real implementation, this would stop the actual service)
	go func() {
		time.Sleep(1 * time.Second) // Simulate shutdown time

		sm.mu.Lock()
		service.Status = models.ServiceStatusStopped
		service.HealthScore = 0.0
		service.StartedAt = nil
		service.UpdatedAt = time.Now()
		sm.orchestrator.db.UpdateService(service)
		sm.mu.Unlock()

		sm.logger.Printf("Service stopped successfully: %s (%s)", service.Name, service.ID)
	}()

	return nil
}

// checkDependencies checks if service dependencies are satisfied
func (sm *ServiceManager) checkDependencies(service *models.Service) error {
	for _, depName := range service.Dependencies {
		depService, err := sm.orchestrator.db.GetServiceByName(depName)
		if err != nil {
			return fmt.Errorf("failed to check dependency %s: %w", depName, err)
		}
		if depService == nil {
			return fmt.Errorf("dependency %s not found", depName)
		}
		if !depService.IsRunning() {
			return fmt.Errorf("dependency %s is not running (status: %s)", depName, depService.Status)
		}
	}
	return nil
}

// serviceMonitorLoop monitors services in the background
func (sm *ServiceManager) serviceMonitorLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sm.ctx.Done():
			return
		case <-ticker.C:
			sm.monitorServices()
		}
	}
}

// monitorServices performs periodic service monitoring
func (sm *ServiceManager) monitorServices() {
	sm.mu.RLock()
	services := make([]*models.Service, 0, len(sm.services))
	for _, service := range sm.services {
		services = append(services, service)
	}
	sm.mu.RUnlock()

	for _, service := range services {
		if service.IsRunning() {
			// Check if service is still responsive
			// In real implementation, this would ping the service health endpoint
			sm.logger.Printf("Monitoring service: %s", service.Name)
		}
	}
}
