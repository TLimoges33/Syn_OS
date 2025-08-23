package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/syn-os/orchestrator/internal/core"
	"github.com/syn-os/orchestrator/internal/models"
)

// EventHandler handles event-related API requests
type EventHandler struct {
	orchestrator *core.Orchestrator
}

// NewEventHandler creates a new event handler
func NewEventHandler(orchestrator *core.Orchestrator) *EventHandler {
	return &EventHandler{
		orchestrator: orchestrator,
	}
}

// GetEvents handles GET /api/v1/events
func (h *EventHandler) GetEvents(c *gin.Context) {
	// Parse query parameters for filtering
	filter := models.EventFilter{}

	if eventTypes := c.QueryArray("type"); len(eventTypes) > 0 {
		for _, t := range eventTypes {
			filter.Types = append(filter.Types, models.EventType(t))
		}
	}

	if sources := c.QueryArray("source"); len(sources) > 0 {
		filter.Sources = sources
	}

	if priorityStr := c.Query("min_priority"); priorityStr != "" {
		if priority, err := strconv.Atoi(priorityStr); err == nil {
			minPriority := models.EventPriority(priority)
			filter.MinPriority = &minPriority
		}
	}

	if sinceStr := c.Query("since"); sinceStr != "" {
		if since, err := time.Parse(time.RFC3339, sinceStr); err == nil {
			filter.Since = &since
		}
	}

	if limitStr := c.Query("limit"); limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil {
			filter.Limit = limit
		}
	} else {
		filter.Limit = 100 // Default limit
	}

	events, err := h.orchestrator.GetEventRouter().GetEventHistory(filter)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get events",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"events": events,
		"count":  len(events),
		"filter": filter,
	})
}

// PublishEvent handles POST /api/v1/events
func (h *EventHandler) PublishEvent(c *gin.Context) {
	var event models.Event
	if err := c.ShouldBindJSON(&event); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid event format",
			"details": err.Error(),
		})
		return
	}

	// Set source to orchestrator if not provided
	if event.Source == "" {
		event.Source = "api"
	}

	// Set timestamp if not provided
	if event.Timestamp.IsZero() {
		event.Timestamp = time.Now()
	}

	if err := h.orchestrator.PublishEvent(&event); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to publish event",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message":  "Event published successfully",
		"event_id": event.ID,
	})
}

// GetEventHistory handles GET /api/v1/events/history
func (h *EventHandler) GetEventHistory(c *gin.Context) {
	// This is similar to GetEvents but with different endpoint for clarity
	h.GetEvents(c)
}

// GetSubscriptions handles GET /api/v1/events/subscriptions
func (h *EventHandler) GetSubscriptions(c *gin.Context) {
	subscriptions := h.orchestrator.GetEventRouter().GetSubscriptions()

	c.JSON(http.StatusOK, gin.H{
		"subscriptions": subscriptions,
		"count":         len(subscriptions),
	})
}

// CreateSubscription handles POST /api/v1/events/subscriptions
func (h *EventHandler) CreateSubscription(c *gin.Context) {
	var request struct {
		Filter models.EventFilter `json:"filter" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid subscription request",
			"details": err.Error(),
		})
		return
	}

	// Create a simple handler that logs events (in real implementation, this would be more sophisticated)
	handler := func(event *models.Event) error {
		// Log the event or store it for the subscriber
		return nil
	}

	subscriptionID, err := h.orchestrator.SubscribeToEvents(request.Filter, handler)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to create subscription",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message":         "Subscription created successfully",
		"subscription_id": subscriptionID,
		"filter":          request.Filter,
	})
}

// DeleteSubscription handles DELETE /api/v1/events/subscriptions/:id
func (h *EventHandler) DeleteSubscription(c *gin.Context) {
	subscriptionID := c.Param("id")

	if err := h.orchestrator.UnsubscribeFromEvents(subscriptionID); err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Failed to delete subscription",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":         "Subscription deleted successfully",
		"subscription_id": subscriptionID,
	})
}

// GetServiceEvents handles GET /api/v1/services/:id/events
func (h *EventHandler) GetServiceEvents(c *gin.Context) {
	serviceID := c.Param("id")

	limitStr := c.DefaultQuery("limit", "50")
	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		limit = 50
	}

	events, err := h.orchestrator.GetDB().GetServiceEvents(serviceID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get service events",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"service_id": serviceID,
		"events":     events,
		"count":      len(events),
	})
}

// PublishConsciousnessEvent handles POST /api/v1/consciousness/events
func (h *EventHandler) PublishConsciousnessEvent(c *gin.Context) {
	var eventData struct {
		Type               models.EventType       `json:"type" binding:"required"`
		ConsciousnessLevel float64                `json:"consciousness_level"`
		NeuralPopulations  map[string]interface{} `json:"neural_populations"`
		ContextData        map[string]interface{} `json:"context_data"`
		UserID             string                 `json:"user_id"`
		Adaptations        []string               `json:"adaptations"`
	}

	if err := c.ShouldBindJSON(&eventData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid consciousness event format",
			"details": err.Error(),
		})
		return
	}

	// Create consciousness event
	event := models.NewEvent(eventData.Type, "consciousness_api").
		WithPriority(models.EventPriorityHigh).
		WithData("consciousness_level", eventData.ConsciousnessLevel).
		WithData("user_id", eventData.UserID)

	if eventData.NeuralPopulations != nil {
		event.WithData("neural_populations", eventData.NeuralPopulations)
	}
	if eventData.ContextData != nil {
		event.WithData("context_data", eventData.ContextData)
	}
	if len(eventData.Adaptations) > 0 {
		event.WithData("adaptations", eventData.Adaptations)
	}

	if err := h.orchestrator.PublishEvent(event); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to publish consciousness event",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message":  "Consciousness event published successfully",
		"event_id": event.ID,
		"type":     eventData.Type,
	})
}

// GetConsciousnessEvents handles GET /api/v1/consciousness/events
func (h *EventHandler) GetConsciousnessEvents(c *gin.Context) {
	// Filter for consciousness events only
	filter := models.EventFilter{
		Types: []models.EventType{
			models.EventTypeConsciousnessUpdate,
			models.EventTypeNeuralEvolution,
			models.EventTypeContextUpdate,
			models.EventTypeLearningProgress,
		},
		Limit: 100,
	}

	// Parse additional query parameters
	if limitStr := c.Query("limit"); limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil {
			filter.Limit = limit
		}
	}

	if userID := c.Query("user_id"); userID != "" {
		// In a real implementation, we'd filter by user_id in the event data
		filter.Sources = []string{userID}
	}

	events, err := h.orchestrator.GetEventRouter().GetEventHistory(filter)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get consciousness events",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"events": events,
		"count":  len(events),
		"filter": filter,
	})
}

// WebSocketEvents handles WebSocket connections for real-time event streaming
func (h *EventHandler) WebSocketEvents(c *gin.Context) {
	// WebSocket implementation would go here
	// For now, return a placeholder
	c.JSON(http.StatusNotImplemented, gin.H{
		"error": "WebSocket event streaming not yet implemented",
	})
}

// GetEventMetrics handles GET /api/v1/events/metrics
func (h *EventHandler) GetEventMetrics(c *gin.Context) {
	metrics, err := h.orchestrator.GetEventRouter().GetMetrics()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get event metrics",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"metrics": metrics,
	})
}
