package models

import (
	"time"
)

// ServiceStatus represents the current status of a service
type ServiceStatus string

const (
	ServiceStatusUnknown   ServiceStatus = "unknown"
	ServiceStatusStarting  ServiceStatus = "starting"
	ServiceStatusRunning   ServiceStatus = "running"
	ServiceStatusStopping  ServiceStatus = "stopping"
	ServiceStatusStopped   ServiceStatus = "stopped"
	ServiceStatusFailed    ServiceStatus = "failed"
	ServiceStatusDegraded  ServiceStatus = "degraded"
)

// ServiceType represents the type of service
type ServiceType string

const (
	ServiceTypeConsciousness ServiceType = "consciousness"
	ServiceTypeIntelligence  ServiceType = "intelligence"
	ServiceTypeIntegration   ServiceType = "integration"
	ServiceTypeInfrastructure ServiceType = "infrastructure"
)

// Service represents a service managed by the orchestrator
type Service struct {
	ID          string            `json:"id" db:"id"`
	Name        string            `json:"name" db:"name"`
	Type        ServiceType       `json:"type" db:"type"`
	Version     string            `json:"version" db:"version"`
	Status      ServiceStatus     `json:"status" db:"status"`
	HealthScore float64           `json:"health_score" db:"health_score"`
	
	// Configuration
	Config      map[string]interface{} `json:"config" db:"config"`
	Environment map[string]string      `json:"environment" db:"environment"`
	
	// Endpoints
	HealthURL   string   `json:"health_url" db:"health_url"`
	Endpoints   []string `json:"endpoints" db:"endpoints"`
	
	// Dependencies
	Dependencies []string `json:"dependencies" db:"dependencies"`
	
	// Metadata
	Metadata    map[string]string `json:"metadata" db:"metadata"`
	Labels      map[string]string `json:"labels" db:"labels"`
	
	// Timestamps
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
	StartedAt   *time.Time `json:"started_at,omitempty" db:"started_at"`
	LastSeen    *time.Time `json:"last_seen,omitempty" db:"last_seen"`
	
	// Runtime information
	ProcessID   *int    `json:"process_id,omitempty" db:"process_id"`
	ContainerID *string `json:"container_id,omitempty" db:"container_id"`
	
	// Performance metrics
	CPUUsage    float64 `json:"cpu_usage" db:"cpu_usage"`
	MemoryUsage int64   `json:"memory_usage" db:"memory_usage"`
	
	// Error tracking
	ErrorCount    int       `json:"error_count" db:"error_count"`
	LastError     *string   `json:"last_error,omitempty" db:"last_error"`
	LastErrorTime *time.Time `json:"last_error_time,omitempty" db:"last_error_time"`
}

// ServiceRegistration represents a service registration request
type ServiceRegistration struct {
	Name         string                 `json:"name" validate:"required"`
	Type         ServiceType            `json:"type" validate:"required"`
	Version      string                 `json:"version" validate:"required"`
	HealthURL    string                 `json:"health_url" validate:"required,url"`
	Endpoints    []string               `json:"endpoints"`
	Dependencies []string               `json:"dependencies"`
	Config       map[string]interface{} `json:"config"`
	Environment  map[string]string      `json:"environment"`
	Metadata     map[string]string      `json:"metadata"`
	Labels       map[string]string      `json:"labels"`
}

// ServiceUpdate represents a service update request
type ServiceUpdate struct {
	Status      *ServiceStatus         `json:"status,omitempty"`
	HealthScore *float64               `json:"health_score,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
	Environment map[string]string      `json:"environment,omitempty"`
	Metadata    map[string]string      `json:"metadata,omitempty"`
	Labels      map[string]string      `json:"labels,omitempty"`
	CPUUsage    *float64               `json:"cpu_usage,omitempty"`
	MemoryUsage *int64                 `json:"memory_usage,omitempty"`
}

// HealthCheck represents a health check result
type HealthCheck struct {
	ServiceID   string                 `json:"service_id"`
	Status      ServiceStatus          `json:"status"`
	HealthScore float64                `json:"health_score"`
	Timestamp   time.Time              `json:"timestamp"`
	Details     map[string]interface{} `json:"details,omitempty"`
	Error       *string                `json:"error,omitempty"`
}

// ServiceMetrics represents service performance metrics
type ServiceMetrics struct {
	ServiceID        string    `json:"service_id"`
	Timestamp        time.Time `json:"timestamp"`
	CPUUsage         float64   `json:"cpu_usage"`
	MemoryUsage      int64     `json:"memory_usage"`
	RequestCount     int64     `json:"request_count"`
	ErrorCount       int64     `json:"error_count"`
	ResponseTime     float64   `json:"response_time"`
	ThroughputPerSec float64   `json:"throughput_per_sec"`
}

// ServiceEvent represents a service lifecycle event
type ServiceEvent struct {
	ID        string                 `json:"id"`
	ServiceID string                 `json:"service_id"`
	Type      string                 `json:"type"`
	Action    string                 `json:"action"`
	Status    ServiceStatus          `json:"status"`
	Timestamp time.Time              `json:"timestamp"`
	Data      map[string]interface{} `json:"data,omitempty"`
	Error     *string                `json:"error,omitempty"`
}

// IsHealthy returns true if the service is considered healthy
func (s *Service) IsHealthy() bool {
	return s.Status == ServiceStatusRunning && s.HealthScore >= 0.7
}

// IsRunning returns true if the service is running
func (s *Service) IsRunning() bool {
	return s.Status == ServiceStatusRunning || s.Status == ServiceStatusDegraded
}

// CanStart returns true if the service can be started
func (s *Service) CanStart() bool {
	return s.Status == ServiceStatusStopped || s.Status == ServiceStatusFailed
}

// CanStop returns true if the service can be stopped
func (s *Service) CanStop() bool {
	return s.Status == ServiceStatusRunning || s.Status == ServiceStatusDegraded
}

// UpdateHealth updates the service health information
func (s *Service) UpdateHealth(healthScore float64, status ServiceStatus) {
	s.HealthScore = healthScore
	s.Status = status
	now := time.Now()
	s.LastSeen = &now
	s.UpdatedAt = now
}

// RecordError records an error for the service
func (s *Service) RecordError(err error) {
	s.ErrorCount++
	errorMsg := err.Error()
	s.LastError = &errorMsg
	now := time.Now()
	s.LastErrorTime = &now
	s.UpdatedAt = now
	
	// Degrade service if too many errors
	if s.ErrorCount > 5 && s.Status == ServiceStatusRunning {
		s.Status = ServiceStatusDegraded
	}
}

// ResetErrors resets the error count and clears error information
func (s *Service) ResetErrors() {
	s.ErrorCount = 0
	s.LastError = nil
	s.LastErrorTime = nil
	s.UpdatedAt = time.Now()
}