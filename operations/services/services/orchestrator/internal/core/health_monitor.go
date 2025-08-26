package core

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/syn-os/orchestrator/internal/models"
)

// HealthMonitor monitors service health and performs health checks
type HealthMonitor struct {
	orchestrator *Orchestrator
	healthChecks map[string]*models.HealthCheck
	mu           sync.RWMutex
	logger       *log.Logger

	// Configuration
	checkInterval time.Duration
	timeout       time.Duration
	maxFailures   int

	// Background tasks
	ctx    context.Context
	cancel context.CancelFunc
}

// NewHealthMonitor creates a new health monitor
func NewHealthMonitor(orchestrator *Orchestrator) *HealthMonitor {
	logger := log.Default()
	logger.SetPrefix("[HealthMonitor] ")

	return &HealthMonitor{
		orchestrator:  orchestrator,
		healthChecks:  make(map[string]*models.HealthCheck),
		logger:        logger,
		checkInterval: 30 * time.Second,
		timeout:       10 * time.Second,
		maxFailures:   3,
	}
}

// Start starts the health monitor
func (hm *HealthMonitor) Start(ctx context.Context) error {
	hm.mu.Lock()
	defer hm.mu.Unlock()

	hm.ctx, hm.cancel = context.WithCancel(ctx)
	hm.logger.Println("Starting Health Monitor...")

	// Start background health check loop
	go hm.healthCheckLoop()

	hm.logger.Println("Health Monitor started")
	return nil
}

// Stop stops the health monitor
func (hm *HealthMonitor) Stop() {
	hm.mu.Lock()
	defer hm.mu.Unlock()

	if hm.cancel != nil {
		hm.cancel()
	}

	hm.logger.Println("Health Monitor stopped")
}

// GetServiceHealth gets the latest health status for a service
func (hm *HealthMonitor) GetServiceHealth(serviceID string) (*models.HealthCheck, error) {
	hm.mu.RLock()
	defer hm.mu.RUnlock()

	// Try cache first
	if healthCheck, exists := hm.healthChecks[serviceID]; exists {
		return healthCheck, nil
	}

	// Try Redis cache
	if healthCheck, err := hm.orchestrator.redis.GetCachedHealthCheck(serviceID); err == nil && healthCheck != nil {
		hm.healthChecks[serviceID] = healthCheck
		return healthCheck, nil
	}

	// Get from database (latest health check)
	healthHistory, err := hm.orchestrator.db.GetHealthHistory(serviceID, time.Now().Add(-1*time.Hour), 1)
	if err != nil {
		return nil, fmt.Errorf("failed to get health history: %w", err)
	}

	if len(healthHistory) == 0 {
		return nil, fmt.Errorf("no health check data found for service %s", serviceID)
	}

	healthCheck := healthHistory[0]
	hm.healthChecks[serviceID] = healthCheck

	return healthCheck, nil
}

// GetSystemHealth gets overall system health
func (hm *HealthMonitor) GetSystemHealth() (map[string]interface{}, error) {
	// Try cache first
	if health, err := hm.orchestrator.redis.GetCachedSystemHealth(); err == nil && health != nil {
		return health, nil
	}

	// Calculate system health
	services, err := hm.orchestrator.serviceManager.ListServices("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to list services: %w", err)
	}

	var totalServices, healthyServices, runningServices, failedServices int
	var totalHealthScore float64
	var healthyCount int

	serviceHealth := make(map[string]interface{})

	for _, service := range services {
		totalServices++

		switch service.Status {
		case models.ServiceStatusRunning:
			runningServices++
		case models.ServiceStatusFailed:
			failedServices++
		}

		if service.IsHealthy() {
			healthyServices++
		}

		if service.HealthScore > 0 {
			totalHealthScore += service.HealthScore
			healthyCount++
		}

		// Get detailed health for each service
		healthCheck, err := hm.GetServiceHealth(service.ID)
		if err == nil {
			serviceHealth[service.Name] = map[string]interface{}{
				"status":       service.Status,
				"health_score": service.HealthScore,
				"last_check":   healthCheck.Timestamp,
			}
		} else {
			serviceHealth[service.Name] = map[string]interface{}{
				"status":       service.Status,
				"health_score": service.HealthScore,
				"error":        err.Error(),
			}
		}
	}

	// Calculate overall health
	var avgHealthScore float64
	if healthyCount > 0 {
		avgHealthScore = totalHealthScore / float64(healthyCount)
	}

	var overallStatus string
	if failedServices > 0 {
		overallStatus = "degraded"
	} else if healthyServices == totalServices && totalServices > 0 {
		overallStatus = "healthy"
	} else {
		overallStatus = "warning"
	}

	systemHealth := map[string]interface{}{
		"overall_status":    overallStatus,
		"total_services":    totalServices,
		"healthy_services":  healthyServices,
		"running_services":  runningServices,
		"failed_services":   failedServices,
		"avg_health_score":  avgHealthScore,
		"health_percentage": float64(healthyServices) / float64(totalServices) * 100,
		"last_updated":      time.Now(),
		"services":          serviceHealth,
	}

	// Cache the result
	hm.orchestrator.redis.CacheSystemHealth(systemHealth, 1*time.Minute)

	return systemHealth, nil
}

// PerformHealthCheck performs a health check on a specific service
func (hm *HealthMonitor) PerformHealthCheck(serviceID string) (*models.HealthCheck, error) {
	service, err := hm.orchestrator.serviceManager.GetService(serviceID)
	if err != nil {
		return nil, fmt.Errorf("failed to get service: %w", err)
	}

	healthCheck := &models.HealthCheck{
		ServiceID: serviceID,
		Timestamp: time.Now(),
	}

	// Only check running services
	if !service.IsRunning() {
		healthCheck.Status = service.Status
		healthCheck.HealthScore = 0.0
		healthCheck.Details = map[string]interface{}{
			"reason": "service not running",
		}
		return healthCheck, nil
	}

	// Perform HTTP health check if health URL is provided
	if service.HealthURL != "" {
		if err := hm.performHTTPHealthCheck(service, healthCheck); err != nil {
			hm.logger.Printf("HTTP health check failed for %s: %v", service.Name, err)
			healthCheck.Status = models.ServiceStatusFailed
			healthCheck.HealthScore = 0.0
			errorMsg := err.Error()
			healthCheck.Error = &errorMsg
		}
	} else {
		// Basic health check based on service status
		healthCheck.Status = service.Status
		healthCheck.HealthScore = service.HealthScore
		healthCheck.Details = map[string]interface{}{
			"check_type": "basic",
			"status":     service.Status,
		}
	}

	// Save health check to database
	if err := hm.orchestrator.db.CreateHealthCheck(healthCheck); err != nil {
		hm.logger.Printf("Failed to save health check for %s: %v", service.Name, err)
	}

	// Cache health check
	hm.mu.Lock()
	hm.healthChecks[serviceID] = healthCheck
	hm.mu.Unlock()

	hm.orchestrator.redis.CacheHealthCheck(healthCheck, 5*time.Minute)

	// Publish health check event
	hm.orchestrator.natsClient.PublishHealthEvent(serviceID, healthCheck)

	// Update service health score if it changed
	if service.HealthScore != healthCheck.HealthScore {
		update := &models.ServiceUpdate{
			HealthScore: &healthCheck.HealthScore,
		}
		if healthCheck.Status != service.Status {
			update.Status = &healthCheck.Status
		}
		hm.orchestrator.serviceManager.UpdateService(serviceID, update)
	}

	return healthCheck, nil
}

// GetStatus returns health monitor status
func (hm *HealthMonitor) GetStatus() map[string]interface{} {
	hm.mu.RLock()
	defer hm.mu.RUnlock()

	return map[string]interface{}{
		"running":        hm.ctx != nil,
		"check_interval": hm.checkInterval.String(),
		"timeout":        hm.timeout.String(),
		"max_failures":   hm.maxFailures,
		"cached_checks":  len(hm.healthChecks),
	}
}

// GetMetrics returns health monitor metrics
func (hm *HealthMonitor) GetMetrics() (map[string]interface{}, error) {
	hm.mu.RLock()
	defer hm.mu.RUnlock()

	// Get system health for metrics
	systemHealth, err := hm.GetSystemHealth()
	if err != nil {
		return nil, fmt.Errorf("failed to get system health: %w", err)
	}

	metrics := map[string]interface{}{
		"total_health_checks":    len(hm.healthChecks),
		"system_health":          systemHealth,
		"check_interval_seconds": hm.checkInterval.Seconds(),
		"timeout_seconds":        hm.timeout.Seconds(),
	}

	// Add health check statistics
	var healthyChecks, unhealthyChecks int
	for _, check := range hm.healthChecks {
		if check.HealthScore >= 0.7 {
			healthyChecks++
		} else {
			unhealthyChecks++
		}
	}

	metrics["healthy_checks"] = healthyChecks
	metrics["unhealthy_checks"] = unhealthyChecks

	return metrics, nil
}

// Private methods

// healthCheckLoop runs the background health check loop
func (hm *HealthMonitor) healthCheckLoop() {
	ticker := time.NewTicker(hm.checkInterval)
	defer ticker.Stop()

	hm.logger.Printf("Starting health check loop with interval %v", hm.checkInterval)

	for {
		select {
		case <-hm.ctx.Done():
			hm.logger.Println("Health check loop stopped")
			return
		case <-ticker.C:
			hm.performAllHealthChecks()
		}
	}
}

// performAllHealthChecks performs health checks on all running services
func (hm *HealthMonitor) performAllHealthChecks() {
	services, err := hm.orchestrator.serviceManager.ListServices("", models.ServiceStatusRunning)
	if err != nil {
		hm.logger.Printf("Failed to list running services for health checks: %v", err)
		return
	}

	hm.logger.Printf("Performing health checks on %d running services", len(services))

	// Perform health checks concurrently
	var wg sync.WaitGroup
	semaphore := make(chan struct{}, 5) // Limit concurrent checks

	for _, service := range services {
		wg.Add(1)
		go func(serviceID string) {
			defer wg.Done()
			semaphore <- struct{}{}        // Acquire semaphore
			defer func() { <-semaphore }() // Release semaphore

			_, err := hm.PerformHealthCheck(serviceID)
			if err != nil {
				hm.logger.Printf("Health check failed for service %s: %v", serviceID, err)
			}
		}(service.ID)
	}

	wg.Wait()
	hm.logger.Printf("Completed health checks for %d services", len(services))
}

// performHTTPHealthCheck performs an HTTP-based health check
func (hm *HealthMonitor) performHTTPHealthCheck(service *models.Service, healthCheck *models.HealthCheck) error {
	client := &http.Client{
		Timeout: hm.timeout,
	}

	req, err := http.NewRequest("GET", service.HealthURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create health check request: %w", err)
	}

	// Add headers
	req.Header.Set("User-Agent", "SynOS-Orchestrator/1.0")
	req.Header.Set("Accept", "application/json")

	start := time.Now()
	resp, err := client.Do(req)
	duration := time.Since(start)

	if err != nil {
		healthCheck.Details = map[string]interface{}{
			"check_type":  "http",
			"url":         service.HealthURL,
			"error":       err.Error(),
			"duration_ms": duration.Milliseconds(),
		}
		return fmt.Errorf("HTTP request failed: %w", err)
	}
	defer resp.Body.Close()

	// Determine health based on status code
	var healthScore float64
	var status models.ServiceStatus

	switch {
	case resp.StatusCode >= 200 && resp.StatusCode < 300:
		healthScore = 1.0
		status = models.ServiceStatusRunning
	case resp.StatusCode >= 500:
		healthScore = 0.0
		status = models.ServiceStatusFailed
	default:
		healthScore = 0.5
		status = models.ServiceStatusDegraded
	}

	healthCheck.Status = status
	healthCheck.HealthScore = healthScore
	healthCheck.Details = map[string]interface{}{
		"check_type":   "http",
		"url":          service.HealthURL,
		"status_code":  resp.StatusCode,
		"duration_ms":  duration.Milliseconds(),
		"content_type": resp.Header.Get("Content-Type"),
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 400 {
		return fmt.Errorf("unhealthy status code: %d", resp.StatusCode)
	}

	return nil
}

// handleUnhealthyService handles services that fail health checks
func (hm *HealthMonitor) handleUnhealthyService(service *models.Service, healthCheck *models.HealthCheck) {
	hm.logger.Printf("Service %s is unhealthy (score: %.2f)", service.Name, healthCheck.HealthScore)

	// Record error
	if healthCheck.Error != nil {
		service.RecordError(fmt.Errorf(*healthCheck.Error))
	}

	// Check if service should be restarted
	if service.ErrorCount >= hm.maxFailures {
		hm.logger.Printf("Service %s has exceeded max failures (%d), attempting restart",
			service.Name, hm.maxFailures)

		// Attempt to restart the service
		if err := hm.orchestrator.serviceManager.RestartService(service.ID); err != nil {
			hm.logger.Printf("Failed to restart unhealthy service %s: %v", service.Name, err)

			// Publish service failure event
			event := models.NewEvent(models.EventTypeServiceFailed, "orchestrator").
				WithData("service_id", service.ID).
				WithData("service_name", service.Name).
				WithData("error", err.Error()).
				WithData("error_count", service.ErrorCount).
				WithPriority(models.EventPriorityCritical)

			hm.orchestrator.natsClient.PublishEvent(event)
		} else {
			// Reset error count after successful restart
			service.ResetErrors()
			hm.orchestrator.db.UpdateService(service)
		}
	}
}
