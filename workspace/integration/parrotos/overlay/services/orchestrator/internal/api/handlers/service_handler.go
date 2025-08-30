package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/syn-os/orchestrator/internal/core"
	"github.com/syn-os/orchestrator/internal/models"
)

// ServiceHandler handles service-related API requests
type ServiceHandler struct {
	orchestrator *core.Orchestrator
}

// NewServiceHandler creates a new service handler
func NewServiceHandler(orchestrator *core.Orchestrator) *ServiceHandler {
	return &ServiceHandler{
		orchestrator: orchestrator,
	}
}

// ListServices handles GET /api/v1/services
func (h *ServiceHandler) ListServices(c *gin.Context) {
	// Parse query parameters
	serviceType := models.ServiceType(c.Query("type"))
	status := models.ServiceStatus(c.Query("status"))

	services, err := h.orchestrator.ListServices(serviceType, status)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to list services",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"services": services,
		"count":    len(services),
	})
}

// RegisterService handles POST /api/v1/services
func (h *ServiceHandler) RegisterService(c *gin.Context) {
	var registration models.ServiceRegistration
	if err := c.ShouldBindJSON(&registration); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request body",
			"details": err.Error(),
		})
		return
	}

	service, err := h.orchestrator.RegisterService(&registration)
	if err != nil {
		c.JSON(http.StatusConflict, gin.H{
			"error":   "Failed to register service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"service": service,
		"message": "Service registered successfully",
	})
}

// GetService handles GET /api/v1/services/:id
func (h *ServiceHandler) GetService(c *gin.Context) {
	serviceID := c.Param("id")

	service, err := h.orchestrator.GetService(serviceID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Service not found",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"service": service,
	})
}

// UpdateService handles PUT /api/v1/services/:id
func (h *ServiceHandler) UpdateService(c *gin.Context) {
	serviceID := c.Param("id")

	var update models.ServiceUpdate
	if err := c.ShouldBindJSON(&update); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request body",
			"details": err.Error(),
		})
		return
	}

	service, err := h.orchestrator.UpdateService(serviceID, &update)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to update service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"service": service,
		"message": "Service updated successfully",
	})
}

// UnregisterService handles DELETE /api/v1/services/:id
func (h *ServiceHandler) UnregisterService(c *gin.Context) {
	serviceID := c.Param("id")

	if err := h.orchestrator.UnregisterService(serviceID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to unregister service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Service unregistered successfully",
	})
}

// StartService handles POST /api/v1/services/:id/start
func (h *ServiceHandler) StartService(c *gin.Context) {
	serviceID := c.Param("id")

	if err := h.orchestrator.StartService(serviceID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to start service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Service start initiated",
	})
}

// StopService handles POST /api/v1/services/:id/stop
func (h *ServiceHandler) StopService(c *gin.Context) {
	serviceID := c.Param("id")

	if err := h.orchestrator.StopService(serviceID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to stop service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Service stop initiated",
	})
}

// RestartService handles POST /api/v1/services/:id/restart
func (h *ServiceHandler) RestartService(c *gin.Context) {
	serviceID := c.Param("id")

	if err := h.orchestrator.RestartService(serviceID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to restart service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Service restart initiated",
	})
}

// GetServiceMetrics handles GET /api/v1/services/:id/metrics
func (h *ServiceHandler) GetServiceMetrics(c *gin.Context) {
	serviceID := c.Param("id")

	// Parse query parameters
	sinceStr := c.DefaultQuery("since", "1h")
	since, err := time.ParseDuration(sinceStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid 'since' parameter",
			"details": "Use duration format like '1h', '30m', '24h'",
		})
		return
	}

	sinceTime := time.Now().Add(-since)
	metrics, err := h.orchestrator.GetServiceMetrics(serviceID, sinceTime)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get service metrics",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"metrics":    metrics,
		"service_id": serviceID,
		"since":      sinceTime,
		"count":      len(metrics),
	})
}

// GetServiceConfiguration handles GET /api/v1/services/:id/config
func (h *ServiceHandler) GetServiceConfiguration(c *gin.Context) {
	serviceID := c.Param("id")

	config, err := h.orchestrator.GetConfiguration(serviceID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Failed to get service configuration",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"service_id":    serviceID,
		"configuration": config,
	})
}

// UpdateServiceConfiguration handles PUT /api/v1/services/:id/config
func (h *ServiceHandler) UpdateServiceConfiguration(c *gin.Context) {
	serviceID := c.Param("id")

	var config map[string]interface{}
	if err := c.ShouldBindJSON(&config); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid configuration format",
			"details": err.Error(),
		})
		return
	}

	if err := h.orchestrator.UpdateConfiguration(serviceID, config); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to update service configuration",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":    "Service configuration updated successfully",
		"service_id": serviceID,
	})
}

// GetServiceStatus handles GET /api/v1/services/:id/status
func (h *ServiceHandler) GetServiceStatus(c *gin.Context) {
	serviceID := c.Param("id")

	service, err := h.orchestrator.GetService(serviceID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Service not found",
			"details": err.Error(),
		})
		return
	}

	// Get additional status information
	healthCheck, _ := h.orchestrator.GetServiceHealth(serviceID)

	status := gin.H{
		"service_id":   serviceID,
		"name":         service.Name,
		"type":         service.Type,
		"status":       service.Status,
		"health_score": service.HealthScore,
		"is_running":   service.IsRunning(),
		"is_healthy":   service.IsHealthy(),
		"started_at":   service.StartedAt,
		"last_seen":    service.LastSeen,
		"error_count":  service.ErrorCount,
		"last_error":   service.LastError,
		"cpu_usage":    service.CPUUsage,
		"memory_usage": service.MemoryUsage,
	}

	if healthCheck != nil {
		status["last_health_check"] = healthCheck.Timestamp
		status["health_details"] = healthCheck.Details
	}

	c.JSON(http.StatusOK, status)
}

// GetServiceLogs handles GET /api/v1/services/:id/logs
func (h *ServiceHandler) GetServiceLogs(c *gin.Context) {
	serviceID := c.Param("id")

	// Parse query parameters
	limitStr := c.DefaultQuery("limit", "100")
	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		limit = 100
	}

	// In a real implementation, this would fetch actual service logs
	// For now, we'll return service events as a proxy for logs
	events, err := h.orchestrator.GetDB().GetServiceEvents(serviceID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get service logs",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"service_id": serviceID,
		"logs":       events,
		"count":      len(events),
	})
}

// ScaleService handles POST /api/v1/services/:id/scale
func (h *ServiceHandler) ScaleService(c *gin.Context) {
	serviceID := c.Param("id")

	var scaleRequest struct {
		Replicas int `json:"replicas" binding:"required,min=0,max=10"`
	}

	if err := c.ShouldBindJSON(&scaleRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid scale request",
			"details": err.Error(),
		})
		return
	}

	// In a real implementation, this would scale the service
	// For now, we'll just update the metadata
	service, err := h.orchestrator.GetService(serviceID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Service not found",
			"details": err.Error(),
		})
		return
	}

	if service.Metadata == nil {
		service.Metadata = make(map[string]string)
	}
	service.Metadata["replicas"] = strconv.Itoa(scaleRequest.Replicas)
	service.Metadata["scaled_at"] = time.Now().Format(time.RFC3339)

	update := &models.ServiceUpdate{
		Metadata: service.Metadata,
	}

	_, err = h.orchestrator.UpdateService(serviceID, update)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to scale service",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":    "Service scaling initiated",
		"service_id": serviceID,
		"replicas":   scaleRequest.Replicas,
	})
}
