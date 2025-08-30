package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/syn-os/orchestrator/internal/core"
)

// HealthHandler handles health-related API requests
type HealthHandler struct {
	orchestrator *core.Orchestrator
}

// NewHealthHandler creates a new health handler
func NewHealthHandler(orchestrator *core.Orchestrator) *HealthHandler {
	return &HealthHandler{
		orchestrator: orchestrator,
	}
}

// SystemHealth handles GET /api/v1/health
func (h *HealthHandler) SystemHealth(c *gin.Context) {
	health, err := h.orchestrator.GetSystemHealth()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get system health",
			"details": err.Error(),
		})
		return
	}

	// Determine HTTP status based on health
	status := http.StatusOK
	if overallStatus, ok := health["overall_status"].(string); ok {
		switch overallStatus {
		case "degraded":
			status = http.StatusServiceUnavailable
		case "warning":
			status = http.StatusPartialContent
		}
	}

	c.JSON(status, health)
}

// AllServicesHealth handles GET /api/v1/health/services
func (h *HealthHandler) AllServicesHealth(c *gin.Context) {
	services, err := h.orchestrator.ListServices("", "")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to list services",
			"details": err.Error(),
		})
		return
	}

	serviceHealth := make(map[string]interface{})
	var healthyCount, totalCount int

	for _, service := range services {
		totalCount++
		healthCheck, err := h.orchestrator.GetServiceHealth(service.ID)

		serviceInfo := gin.H{
			"service_id":   service.ID,
			"name":         service.Name,
			"status":       service.Status,
			"health_score": service.HealthScore,
			"is_healthy":   service.IsHealthy(),
		}

		if err == nil {
			serviceInfo["last_check"] = healthCheck.Timestamp
			serviceInfo["check_details"] = healthCheck.Details
			if healthCheck.Error != nil {
				serviceInfo["error"] = *healthCheck.Error
			}
		} else {
			serviceInfo["health_error"] = err.Error()
		}

		if service.IsHealthy() {
			healthyCount++
		}

		serviceHealth[service.Name] = serviceInfo
	}

	response := gin.H{
		"services": serviceHealth,
		"summary": gin.H{
			"total_services":    totalCount,
			"healthy_services":  healthyCount,
			"health_percentage": float64(healthyCount) / float64(totalCount) * 100,
		},
	}

	c.JSON(http.StatusOK, response)
}

// GetServiceHealth handles GET /api/v1/health/services/:id
func (h *HealthHandler) GetServiceHealth(c *gin.Context) {
	serviceID := c.Param("id")

	healthCheck, err := h.orchestrator.GetServiceHealth(serviceID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Failed to get service health",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"service_id":   serviceID,
		"health_check": healthCheck,
	})
}

// PerformHealthCheck handles POST /api/v1/health/services/:id/check
func (h *HealthHandler) PerformHealthCheck(c *gin.Context) {
	serviceID := c.Param("id")

	healthCheck, err := h.orchestrator.GetHealthMonitor().PerformHealthCheck(serviceID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to perform health check",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":      "Health check completed",
		"service_id":   serviceID,
		"health_check": healthCheck,
	})
}

// WebSocketHealth handles WebSocket connections for real-time health updates
func (h *HealthHandler) WebSocketHealth(c *gin.Context) {
	// WebSocket implementation would go here
	// For now, return a placeholder
	c.JSON(http.StatusNotImplemented, gin.H{
		"error": "WebSocket health monitoring not yet implemented",
	})
}
