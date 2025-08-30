package api

import (
	"github.com/gin-gonic/gin"
	"github.com/syn-os/orchestrator/internal/api/handlers"
	"github.com/syn-os/orchestrator/internal/api/middleware"
	"github.com/syn-os/orchestrator/internal/core"
)

// SetupRoutes configures all API routes
func SetupRoutes(router *gin.Engine, orchestrator *core.Orchestrator) {
	// Create handlers
	serviceHandler := handlers.NewServiceHandler(orchestrator)
	healthHandler := handlers.NewHealthHandler(orchestrator)
	eventHandler := handlers.NewEventHandler(orchestrator)
	systemHandler := handlers.NewSystemHandler(orchestrator)

	// Add middleware
	router.Use(middleware.CORS())
	router.Use(middleware.RequestID())
	router.Use(middleware.Logger())

	// API v1 routes
	v1 := router.Group("/api/v1")
	{
		// Authentication middleware for protected routes
		protected := v1.Group("")
		protected.Use(middleware.Auth(orchestrator.GetConfig().Security))

		// System routes (public)
		v1.GET("/health", healthHandler.SystemHealth)
		v1.GET("/status", systemHandler.GetStatus)
		v1.GET("/version", systemHandler.GetVersion)

		// Service management routes (protected)
		services := protected.Group("/services")
		{
			services.GET("", serviceHandler.ListServices)
			services.POST("", serviceHandler.RegisterService)
			services.GET("/:id", serviceHandler.GetService)
			services.PUT("/:id", serviceHandler.UpdateService)
			services.DELETE("/:id", serviceHandler.UnregisterService)
			services.POST("/:id/start", serviceHandler.StartService)
			services.POST("/:id/stop", serviceHandler.StopService)
			services.POST("/:id/restart", serviceHandler.RestartService)
			services.GET("/:id/health", healthHandler.GetServiceHealth)
			services.GET("/:id/metrics", serviceHandler.GetServiceMetrics)
			services.GET("/:id/events", eventHandler.GetServiceEvents)
		}

		// Health monitoring routes (protected)
		health := protected.Group("/health")
		{
			health.GET("/system", healthHandler.SystemHealth)
			health.GET("/services", healthHandler.AllServicesHealth)
			health.GET("/services/:id", healthHandler.GetServiceHealth)
			health.POST("/services/:id/check", healthHandler.PerformHealthCheck)
		}

		// Event management routes (protected)
		events := protected.Group("/events")
		{
			events.GET("", eventHandler.GetEvents)
			events.POST("", eventHandler.PublishEvent)
			events.GET("/history", eventHandler.GetEventHistory)
			events.GET("/subscriptions", eventHandler.GetSubscriptions)
			events.POST("/subscriptions", eventHandler.CreateSubscription)
			events.DELETE("/subscriptions/:id", eventHandler.DeleteSubscription)
		}

		// System management routes (protected)
		system := protected.Group("/system")
		{
			system.GET("/status", systemHandler.GetStatus)
			system.GET("/metrics", systemHandler.GetMetrics)
			system.GET("/config", systemHandler.GetConfiguration)
			system.PUT("/config", systemHandler.UpdateConfiguration)
			system.POST("/shutdown", systemHandler.Shutdown)
		}

		// Consciousness integration routes (protected)
		consciousness := protected.Group("/consciousness")
		{
			consciousness.GET("/status", systemHandler.GetConsciousnessStatus)
			consciousness.POST("/events", eventHandler.PublishConsciousnessEvent)
			consciousness.GET("/events", eventHandler.GetConsciousnessEvents)
		}
	}

	// WebSocket routes for real-time updates
	router.GET("/ws/events", eventHandler.WebSocketEvents)
	router.GET("/ws/health", healthHandler.WebSocketHealth)
	router.GET("/ws/metrics", systemHandler.WebSocketMetrics)

	// Static files for dashboard (if enabled)
	router.Static("/static", "./web/static")
	router.StaticFile("/", "./web/index.html")
}
