package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/syn-os/orchestrator/internal/core"
	"github.com/syn-os/orchestrator/internal/models"
)

// SystemHandler handles system-related API requests
type SystemHandler struct {
	orchestrator *core.Orchestrator
}

// NewSystemHandler creates a new system handler
func NewSystemHandler(orchestrator *core.Orchestrator) *SystemHandler {
	return &SystemHandler{
		orchestrator: orchestrator,
	}
}

// GetStatus handles GET /api/v1/status
func (h *SystemHandler) GetStatus(c *gin.Context) {
	status := h.orchestrator.GetStatus()
	c.JSON(http.StatusOK, status)
}

// GetVersion handles GET /api/v1/version
func (h *SystemHandler) GetVersion(c *gin.Context) {
	version := gin.H{
		"version":    "1.0.0",
		"build_time": "2025-01-01T00:00:00Z",
		"git_commit": "unknown",
		"go_version": "1.21+",
		"service":    "syn-os-orchestrator",
	}
	c.JSON(http.StatusOK, version)
}

// GetMetrics handles GET /api/v1/system/metrics
func (h *SystemHandler) GetMetrics(c *gin.Context) {
	metrics, err := h.orchestrator.GetMetrics()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get system metrics",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"metrics": metrics,
	})
}

// GetConfiguration handles GET /api/v1/system/config
func (h *SystemHandler) GetConfiguration(c *gin.Context) {
	config := h.orchestrator.GetConfig()

	// Return a sanitized version of the configuration (remove sensitive data)
	sanitizedConfig := gin.H{
		"server": gin.H{
			"port":          config.Server.Port,
			"mode":          config.Server.Mode,
			"read_timeout":  config.Server.ReadTimeout,
			"write_timeout": config.Server.WriteTimeout,
		},
		"nats": gin.H{
			"url":           config.NATS.URL,
			"cluster_id":    config.NATS.ClusterID,
			"client_id":     config.NATS.ClientID,
			"max_reconnect": config.NATS.MaxReconnect,
		},
		"security": gin.H{
			"enable_auth":  config.Security.EnableAuth,
			"enable_tls":   config.Security.EnableTLS,
			"token_expiry": config.Security.TokenExpiry.String(),
		},
		"logging": gin.H{
			"level":  config.Logging.Level,
			"format": config.Logging.Format,
			"output": config.Logging.Output,
		},
	}

	c.JSON(http.StatusOK, gin.H{
		"configuration": sanitizedConfig,
	})
}

// UpdateConfiguration handles PUT /api/v1/system/config
func (h *SystemHandler) UpdateConfiguration(c *gin.Context) {
	var configUpdate map[string]interface{}
	if err := c.ShouldBindJSON(&configUpdate); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid configuration format",
			"details": err.Error(),
		})
		return
	}

	// In a real implementation, this would update the configuration
	// For now, we'll just acknowledge the request
	c.JSON(http.StatusOK, gin.H{
		"message": "Configuration update received",
		"note":    "Dynamic configuration updates not yet implemented",
		"updates": configUpdate,
	})
}

// Shutdown handles POST /api/v1/system/shutdown
func (h *SystemHandler) Shutdown(c *gin.Context) {
	var shutdownRequest struct {
		Force bool `json:"force"`
		Delay int  `json:"delay"` // seconds
	}

	if err := c.ShouldBindJSON(&shutdownRequest); err != nil {
		// Use defaults if no body provided
		shutdownRequest.Force = false
		shutdownRequest.Delay = 10
	}

	c.JSON(http.StatusAccepted, gin.H{
		"message":       "Shutdown initiated",
		"force":         shutdownRequest.Force,
		"delay_seconds": shutdownRequest.Delay,
	})

	// In a real implementation, this would initiate graceful shutdown
	// For now, we'll just log the request
	go func() {
		// Simulate shutdown process
		// time.Sleep(time.Duration(shutdownRequest.Delay) * time.Second)
		// h.orchestrator.Stop()
	}()
}

// GetConsciousnessStatus handles GET /api/v1/consciousness/status
func (h *SystemHandler) GetConsciousnessStatus(c *gin.Context) {
	// Get consciousness-related services
	consciousnessServices, err := h.orchestrator.ListServices("consciousness", "")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get consciousness services",
			"details": err.Error(),
		})
		return
	}

	intelligenceServices, err := h.orchestrator.ListServices("intelligence", "")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get intelligence services",
			"details": err.Error(),
		})
		return
	}

	// Calculate consciousness system health
	var totalServices, runningServices, healthyServices int
	var totalHealthScore float64

	allServices := append(consciousnessServices, intelligenceServices...)
	for _, service := range allServices {
		totalServices++
		if service.IsRunning() {
			runningServices++
		}
		if service.IsHealthy() {
			healthyServices++
		}
		totalHealthScore += service.HealthScore
	}

	var avgHealthScore float64
	if totalServices > 0 {
		avgHealthScore = totalHealthScore / float64(totalServices)
	}

	// Get recent consciousness events
	consciousnessEvents, _ := h.orchestrator.GetEventRouter().GetEventHistory(
		models.EventFilter{
			Types: []models.EventType{
				models.EventTypeConsciousnessUpdate,
				models.EventTypeNeuralEvolution,
				models.EventTypeContextUpdate,
			},
			Limit: 10,
		},
	)

	status := gin.H{
		"consciousness_system": gin.H{
			"total_services":   totalServices,
			"running_services": runningServices,
			"healthy_services": healthyServices,
			"avg_health_score": avgHealthScore,
			"system_status": func() string {
				if healthyServices == totalServices && totalServices > 0 {
					return "optimal"
				} else if runningServices > 0 {
					return "degraded"
				} else {
					return "offline"
				}
			}(),
		},
		"services": gin.H{
			"consciousness": consciousnessServices,
			"intelligence":  intelligenceServices,
		},
		"recent_events": consciousnessEvents,
		"event_count":   len(consciousnessEvents),
	}

	c.JSON(http.StatusOK, status)
}

// WebSocketMetrics handles WebSocket connections for real-time metrics
func (h *SystemHandler) WebSocketMetrics(c *gin.Context) {
	// WebSocket implementation would go here
	// For now, return a placeholder
	c.JSON(http.StatusNotImplemented, gin.H{
		"error": "WebSocket metrics streaming not yet implemented",
	})
}

// GetResourceUsage handles GET /api/v1/system/resources
func (h *SystemHandler) GetResourceUsage(c *gin.Context) {
	// Get resource usage from all services
	services, err := h.orchestrator.ListServices("", "")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get services for resource calculation",
			"details": err.Error(),
		})
		return
	}

	var totalCPU float64
	var totalMemory int64
	var serviceCount int

	resourcesByService := make(map[string]gin.H)

	for _, service := range services {
		if service.IsRunning() {
			totalCPU += service.CPUUsage
			totalMemory += service.MemoryUsage
			serviceCount++

			resourcesByService[service.Name] = gin.H{
				"cpu_usage":    service.CPUUsage,
				"memory_usage": service.MemoryUsage,
				"status":       service.Status,
			}
		}
	}

	resources := gin.H{
		"summary": gin.H{
			"total_cpu_usage":    totalCPU,
			"total_memory_usage": totalMemory,
			"active_services":    serviceCount,
			"avg_cpu_per_service": func() float64 {
				if serviceCount > 0 {
					return totalCPU / float64(serviceCount)
				}
				return 0
			}(),
			"avg_memory_per_service": func() int64 {
				if serviceCount > 0 {
					return totalMemory / int64(serviceCount)
				}
				return 0
			}(),
		},
		"services": resourcesByService,
	}

	c.JSON(http.StatusOK, resources)
}

// GetSystemLogs handles GET /api/v1/system/logs
func (h *SystemHandler) GetSystemLogs(c *gin.Context) {
	// In a real implementation, this would return system logs
	// For now, return orchestrator events as system logs
	filter := models.EventFilter{
		Sources: []string{"orchestrator", "service_manager", "health_monitor", "event_router"},
		Limit:   100,
	}

	events, err := h.orchestrator.GetEventRouter().GetEventHistory(filter)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get system logs",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"logs":   events,
		"count":  len(events),
		"source": "orchestrator_events",
	})
}
