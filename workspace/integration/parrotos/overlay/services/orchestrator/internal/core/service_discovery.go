package core

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/syn-os/orchestrator/internal/models"
	"github.com/syn-os/orchestrator/pkg/nats"
)

// ServiceDiscovery handles automatic service discovery and registration
type ServiceDiscovery struct {
	natsClient    *nats.Client
	services      map[string]*models.Service
	servicesMutex sync.RWMutex
	logger        *log.Logger
	ctx           context.Context
	cancel        context.CancelFunc
}

// NewServiceDiscovery creates a new service discovery instance
func NewServiceDiscovery(natsClient *nats.Client, logger *log.Logger) *ServiceDiscovery {
	ctx, cancel := context.WithCancel(context.Background())

	return &ServiceDiscovery{
		natsClient:    natsClient,
		services:      make(map[string]*models.Service),
		servicesMutex: sync.RWMutex{},
		logger:        logger,
		ctx:           ctx,
		cancel:        cancel,
	}
}

// Start begins the service discovery process
func (sd *ServiceDiscovery) Start() error {
	sd.logger.Println("Starting service discovery...")

	// Subscribe to service announcements
	if err := sd.subscribeToServiceAnnouncements(); err != nil {
		return fmt.Errorf("failed to subscribe to service announcements: %w", err)
	}

	// Start periodic service discovery broadcast
	go sd.periodicDiscoveryBroadcast()

	// Start service health monitoring
	go sd.monitorServiceHealth()

	sd.logger.Println("Service discovery started successfully")
	return nil
}

// Stop stops the service discovery process
func (sd *ServiceDiscovery) Stop() {
	sd.logger.Println("Stopping service discovery...")
	sd.cancel()
}

// RegisterService registers a service manually
func (sd *ServiceDiscovery) RegisterService(service *models.Service) {
	sd.servicesMutex.Lock()
	defer sd.servicesMutex.Unlock()

	sd.services[service.ID] = service
	sd.logger.Printf("Registered service: %s (%s)", service.Name, service.ID)

	// Announce service registration
	sd.announceServiceChange("registered", service)
}

// UnregisterService removes a service from discovery
func (sd *ServiceDiscovery) UnregisterService(serviceID string) {
	sd.servicesMutex.Lock()
	defer sd.servicesMutex.Unlock()

	if service, exists := sd.services[serviceID]; exists {
		delete(sd.services, serviceID)
		sd.logger.Printf("Unregistered service: %s (%s)", service.Name, service.ID)

		// Announce service removal
		sd.announceServiceChange("unregistered", service)
	}
}

// GetServices returns all discovered services
func (sd *ServiceDiscovery) GetServices() map[string]*models.Service {
	sd.servicesMutex.RLock()
	defer sd.servicesMutex.RUnlock()

	// Return a copy to avoid race conditions
	services := make(map[string]*models.Service)
	for id, service := range sd.services {
		services[id] = service
	}

	return services
}

// GetService returns a specific service by ID
func (sd *ServiceDiscovery) GetService(serviceID string) (*models.Service, bool) {
	sd.servicesMutex.RLock()
	defer sd.servicesMutex.RUnlock()

	service, exists := sd.services[serviceID]
	return service, exists
}

// GetServicesByType returns services of a specific type
func (sd *ServiceDiscovery) GetServicesByType(serviceType string) []*models.Service {
	sd.servicesMutex.RLock()
	defer sd.servicesMutex.RUnlock()

	var services []*models.Service
	for _, service := range sd.services {
		if service.Type == serviceType {
			services = append(services, service)
		}
	}

	return services
}

// subscribeToServiceAnnouncements subscribes to service announcement messages
func (sd *ServiceDiscovery) subscribeToServiceAnnouncements() error {
	// Subscribe to service announcements
	_, err := sd.natsClient.Subscribe("orchestrator.service.announce", func(subject, data string) {
		var announcement ServiceAnnouncement
		if err := json.Unmarshal([]byte(data), &announcement); err != nil {
			sd.logger.Printf("Failed to unmarshal service announcement: %v", err)
			return
		}

		sd.handleServiceAnnouncement(&announcement)
	})

	return err
}

// ServiceAnnouncement represents a service announcement message
type ServiceAnnouncement struct {
	Action    string          `json:"action"` // "register", "unregister", "heartbeat"
	Service   *models.Service `json:"service"`
	Timestamp time.Time       `json:"timestamp"`
}

// handleServiceAnnouncement processes incoming service announcements
func (sd *ServiceDiscovery) handleServiceAnnouncement(announcement *ServiceAnnouncement) {
	switch announcement.Action {
	case "register":
		sd.handleServiceRegistration(announcement.Service)
	case "unregister":
		sd.handleServiceUnregistration(announcement.Service.ID)
	case "heartbeat":
		sd.handleServiceHeartbeat(announcement.Service)
	default:
		sd.logger.Printf("Unknown service announcement action: %s", announcement.Action)
	}
}

// handleServiceRegistration handles service registration announcements
func (sd *ServiceDiscovery) handleServiceRegistration(service *models.Service) {
	sd.servicesMutex.Lock()
	defer sd.servicesMutex.Unlock()

	// Update service information
	service.LastSeen = time.Now()
	service.Status = "healthy"
	sd.services[service.ID] = service

	sd.logger.Printf("Discovered service: %s (%s) at %s", service.Name, service.Type, service.Endpoint)
}

// handleServiceUnregistration handles service unregistration announcements
func (sd *ServiceDiscovery) handleServiceUnregistration(serviceID string) {
	sd.servicesMutex.Lock()
	defer sd.servicesMutex.Unlock()

	if service, exists := sd.services[serviceID]; exists {
		delete(sd.services, serviceID)
		sd.logger.Printf("Service unregistered: %s (%s)", service.Name, service.ID)
	}
}

// handleServiceHeartbeat handles service heartbeat messages
func (sd *ServiceDiscovery) handleServiceHeartbeat(service *models.Service) {
	sd.servicesMutex.Lock()
	defer sd.servicesMutex.Unlock()

	if existingService, exists := sd.services[service.ID]; exists {
		// Update last seen time and status
		existingService.LastSeen = time.Now()
		existingService.Status = service.Status
		existingService.Health = service.Health
	} else {
		// New service discovered via heartbeat
		service.LastSeen = time.Now()
		sd.services[service.ID] = service
		sd.logger.Printf("New service discovered via heartbeat: %s (%s)", service.Name, service.ID)
	}
}

// periodicDiscoveryBroadcast sends periodic discovery requests
func (sd *ServiceDiscovery) periodicDiscoveryBroadcast() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sd.ctx.Done():
			return
		case <-ticker.C:
			sd.broadcastDiscoveryRequest()
		}
	}
}

// broadcastDiscoveryRequest broadcasts a service discovery request
func (sd *ServiceDiscovery) broadcastDiscoveryRequest() {
	request := map[string]interface{}{
		"action":    "discover",
		"timestamp": time.Now(),
		"requester": "orchestrator",
	}

	data, err := json.Marshal(request)
	if err != nil {
		sd.logger.Printf("Failed to marshal discovery request: %v", err)
		return
	}

	if err := sd.natsClient.Publish("orchestrator.service.discover", string(data)); err != nil {
		sd.logger.Printf("Failed to broadcast discovery request: %v", err)
	}
}

// monitorServiceHealth monitors the health of discovered services
func (sd *ServiceDiscovery) monitorServiceHealth() {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sd.ctx.Done():
			return
		case <-ticker.C:
			sd.checkServiceHealth()
		}
	}
}

// checkServiceHealth checks the health of all registered services
func (sd *ServiceDiscovery) checkServiceHealth() {
	sd.servicesMutex.Lock()
	defer sd.servicesMutex.Unlock()

	now := time.Now()
	staleThreshold := 5 * time.Minute

	for serviceID, service := range sd.services {
		// Check if service is stale (no heartbeat for too long)
		if now.Sub(service.LastSeen) > staleThreshold {
			sd.logger.Printf("Service %s (%s) appears to be stale, marking as unhealthy", service.Name, serviceID)
			service.Status = "unhealthy"
			service.Health.Status = "unhealthy"
			service.Health.LastCheck = now
			service.Health.Message = "No heartbeat received"

			// Announce service health change
			sd.announceServiceChange("health_changed", service)
		}
	}
}

// announceServiceChange announces service changes to other components
func (sd *ServiceDiscovery) announceServiceChange(action string, service *models.Service) {
	announcement := ServiceAnnouncement{
		Action:    action,
		Service:   service,
		Timestamp: time.Now(),
	}

	data, err := json.Marshal(announcement)
	if err != nil {
		sd.logger.Printf("Failed to marshal service change announcement: %v", err)
		return
	}

	subject := fmt.Sprintf("orchestrator.service.%s", action)
	if err := sd.natsClient.Publish(subject, string(data)); err != nil {
		sd.logger.Printf("Failed to announce service change: %v", err)
	}
}

// GetServiceStats returns statistics about discovered services
func (sd *ServiceDiscovery) GetServiceStats() map[string]interface{} {
	sd.servicesMutex.RLock()
	defer sd.servicesMutex.RUnlock()

	stats := map[string]interface{}{
		"total_services":     len(sd.services),
		"healthy_services":   0,
		"unhealthy_services": 0,
		"service_types":      make(map[string]int),
	}

	for _, service := range sd.services {
		// Count by health status
		if service.Status == "healthy" {
			stats["healthy_services"] = stats["healthy_services"].(int) + 1
		} else {
			stats["unhealthy_services"] = stats["unhealthy_services"].(int) + 1
		}

		// Count by service type
		serviceTypes := stats["service_types"].(map[string]int)
		serviceTypes[service.Type]++
	}

	return stats
}
