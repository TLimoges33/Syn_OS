package storage

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"github.com/syn-os/orchestrator/internal/models"
)

// PostgresDB wraps the database connection and provides service storage operations
type PostgresDB struct {
	db *sqlx.DB
}

// NewPostgresDB creates a new PostgreSQL database connection
func NewPostgresDB(databaseURL string) (*PostgresDB, error) {
	db, err := sqlx.Connect("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Test the connection
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	postgres := &PostgresDB{db: db}

	// Initialize database schema
	if err := postgres.initSchema(); err != nil {
		return nil, fmt.Errorf("failed to initialize schema: %w", err)
	}

	return postgres, nil
}

// Close closes the database connection
func (p *PostgresDB) Close() error {
	return p.db.Close()
}

// initSchema creates the necessary database tables
func (p *PostgresDB) initSchema() error {
	schema := `
	CREATE TABLE IF NOT EXISTS services (
		id VARCHAR(255) PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		type VARCHAR(50) NOT NULL,
		version VARCHAR(50) NOT NULL,
		status VARCHAR(50) NOT NULL DEFAULT 'unknown',
		health_score DECIMAL(3,2) DEFAULT 0.0,
		config JSONB,
		environment JSONB,
		health_url VARCHAR(500),
		endpoints JSONB,
		dependencies JSONB,
		metadata JSONB,
		labels JSONB,
		created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
		updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
		started_at TIMESTAMP WITH TIME ZONE,
		last_seen TIMESTAMP WITH TIME ZONE,
		process_id INTEGER,
		container_id VARCHAR(255),
		cpu_usage DECIMAL(5,2) DEFAULT 0.0,
		memory_usage BIGINT DEFAULT 0,
		error_count INTEGER DEFAULT 0,
		last_error TEXT,
		last_error_time TIMESTAMP WITH TIME ZONE
	);

	CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);
	CREATE INDEX IF NOT EXISTS idx_services_type ON services(type);
	CREATE INDEX IF NOT EXISTS idx_services_status ON services(status);
	CREATE INDEX IF NOT EXISTS idx_services_updated_at ON services(updated_at);

	CREATE TABLE IF NOT EXISTS service_events (
		id VARCHAR(255) PRIMARY KEY,
		service_id VARCHAR(255) NOT NULL,
		type VARCHAR(100) NOT NULL,
		action VARCHAR(100) NOT NULL,
		status VARCHAR(50) NOT NULL,
		timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
		data JSONB,
		error TEXT,
		FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
	);

	CREATE INDEX IF NOT EXISTS idx_service_events_service_id ON service_events(service_id);
	CREATE INDEX IF NOT EXISTS idx_service_events_type ON service_events(type);
	CREATE INDEX IF NOT EXISTS idx_service_events_timestamp ON service_events(timestamp);

	CREATE TABLE IF NOT EXISTS health_checks (
		id SERIAL PRIMARY KEY,
		service_id VARCHAR(255) NOT NULL,
		status VARCHAR(50) NOT NULL,
		health_score DECIMAL(3,2) NOT NULL,
		timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
		details JSONB,
		error TEXT,
		FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
	);

	CREATE INDEX IF NOT EXISTS idx_health_checks_service_id ON health_checks(service_id);
	CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON health_checks(timestamp);

	CREATE TABLE IF NOT EXISTS service_metrics (
		id SERIAL PRIMARY KEY,
		service_id VARCHAR(255) NOT NULL,
		timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
		cpu_usage DECIMAL(5,2),
		memory_usage BIGINT,
		request_count BIGINT,
		error_count BIGINT,
		response_time DECIMAL(10,3),
		throughput_per_sec DECIMAL(10,3),
		FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
	);

	CREATE INDEX IF NOT EXISTS idx_service_metrics_service_id ON service_metrics(service_id);
	CREATE INDEX IF NOT EXISTS idx_service_metrics_timestamp ON service_metrics(timestamp);
	`

	_, err := p.db.Exec(schema)
	return err
}

// CreateService creates a new service record
func (p *PostgresDB) CreateService(service *models.Service) error {
	query := `
		INSERT INTO services (
			id, name, type, version, status, health_score, config, environment,
			health_url, endpoints, dependencies, metadata, labels, created_at, updated_at
		) VALUES (
			:id, :name, :type, :version, :status, :health_score, :config, :environment,
			:health_url, :endpoints, :dependencies, :metadata, :labels, :created_at, :updated_at
		)`

	_, err := p.db.NamedExec(query, service)
	return err
}

// GetService retrieves a service by ID
func (p *PostgresDB) GetService(id string) (*models.Service, error) {
	var service models.Service
	query := `SELECT * FROM services WHERE id = $1`
	
	err := p.db.Get(&service, query, id)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	return &service, nil
}

// GetServiceByName retrieves a service by name
func (p *PostgresDB) GetServiceByName(name string) (*models.Service, error) {
	var service models.Service
	query := `SELECT * FROM services WHERE name = $1`
	
	err := p.db.Get(&service, query, name)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	return &service, nil
}

// UpdateService updates an existing service
func (p *PostgresDB) UpdateService(service *models.Service) error {
	service.UpdatedAt = time.Now()
	
	query := `
		UPDATE services SET
			name = :name, type = :type, version = :version, status = :status,
			health_score = :health_score, config = :config, environment = :environment,
			health_url = :health_url, endpoints = :endpoints, dependencies = :dependencies,
			metadata = :metadata, labels = :labels, updated_at = :updated_at,
			started_at = :started_at, last_seen = :last_seen, process_id = :process_id,
			container_id = :container_id, cpu_usage = :cpu_usage, memory_usage = :memory_usage,
			error_count = :error_count, last_error = :last_error, last_error_time = :last_error_time
		WHERE id = :id`

	_, err := p.db.NamedExec(query, service)
	return err
}

// DeleteService deletes a service by ID
func (p *PostgresDB) DeleteService(id string) error {
	query := `DELETE FROM services WHERE id = $1`
	_, err := p.db.Exec(query, id)
	return err
}

// ListServices retrieves all services with optional filtering
func (p *PostgresDB) ListServices(serviceType models.ServiceType, status models.ServiceStatus) ([]*models.Service, error) {
	var services []*models.Service
	var query string
	var args []interface{}

	query = `SELECT * FROM services WHERE 1=1`

	if serviceType != "" {
		query += ` AND type = $` + fmt.Sprintf("%d", len(args)+1)
		args = append(args, serviceType)
	}

	if status != "" {
		query += ` AND status = $` + fmt.Sprintf("%d", len(args)+1)
		args = append(args, status)
	}

	query += ` ORDER BY created_at DESC`

	err := p.db.Select(&services, query, args...)
	return services, err
}

// CreateServiceEvent creates a service event record
func (p *PostgresDB) CreateServiceEvent(event *models.ServiceEvent) error {
	query := `
		INSERT INTO service_events (id, service_id, type, action, status, timestamp, data, error)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`

	dataJSON, _ := json.Marshal(event.Data)
	
	_, err := p.db.Exec(query, event.ID, event.ServiceID, event.Type, event.Action,
		event.Status, event.Timestamp, dataJSON, event.Error)
	return err
}

// GetServiceEvents retrieves events for a service
func (p *PostgresDB) GetServiceEvents(serviceID string, limit int) ([]*models.ServiceEvent, error) {
	var events []*models.ServiceEvent
	query := `
		SELECT id, service_id, type, action, status, timestamp, data, error
		FROM service_events 
		WHERE service_id = $1 
		ORDER BY timestamp DESC 
		LIMIT $2`

	rows, err := p.db.Query(query, serviceID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var event models.ServiceEvent
		var dataJSON []byte
		
		err := rows.Scan(&event.ID, &event.ServiceID, &event.Type, &event.Action,
			&event.Status, &event.Timestamp, &dataJSON, &event.Error)
		if err != nil {
			return nil, err
		}

		if len(dataJSON) > 0 {
			json.Unmarshal(dataJSON, &event.Data)
		}

		events = append(events, &event)
	}

	return events, nil
}

// CreateHealthCheck creates a health check record
func (p *PostgresDB) CreateHealthCheck(healthCheck *models.HealthCheck) error {
	query := `
		INSERT INTO health_checks (service_id, status, health_score, timestamp, details, error)
		VALUES ($1, $2, $3, $4, $5, $6)`

	detailsJSON, _ := json.Marshal(healthCheck.Details)
	
	_, err := p.db.Exec(query, healthCheck.ServiceID, healthCheck.Status,
		healthCheck.HealthScore, healthCheck.Timestamp, detailsJSON, healthCheck.Error)
	return err
}

// GetHealthHistory retrieves health check history for a service
func (p *PostgresDB) GetHealthHistory(serviceID string, since time.Time, limit int) ([]*models.HealthCheck, error) {
	var healthChecks []*models.HealthCheck
	query := `
		SELECT service_id, status, health_score, timestamp, details, error
		FROM health_checks 
		WHERE service_id = $1 AND timestamp >= $2
		ORDER BY timestamp DESC 
		LIMIT $3`

	rows, err := p.db.Query(query, serviceID, since, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var healthCheck models.HealthCheck
		var detailsJSON []byte
		
		err := rows.Scan(&healthCheck.ServiceID, &healthCheck.Status,
			&healthCheck.HealthScore, &healthCheck.Timestamp, &detailsJSON, &healthCheck.Error)
		if err != nil {
			return nil, err
		}

		if len(detailsJSON) > 0 {
			json.Unmarshal(detailsJSON, &healthCheck.Details)
		}

		healthChecks = append(healthChecks, &healthCheck)
	}

	return healthChecks, nil
}

// CreateServiceMetrics creates a service metrics record
func (p *PostgresDB) CreateServiceMetrics(metrics *models.ServiceMetrics) error {
	query := `
		INSERT INTO service_metrics (
			service_id, timestamp, cpu_usage, memory_usage, request_count,
			error_count, response_time, throughput_per_sec
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`

	_, err := p.db.Exec(query, metrics.ServiceID, metrics.Timestamp,
		metrics.CPUUsage, metrics.MemoryUsage, metrics.RequestCount,
		metrics.ErrorCount, metrics.ResponseTime, metrics.ThroughputPerSec)
	return err
}

// GetServiceMetrics retrieves metrics for a service within a time range
func (p *PostgresDB) GetServiceMetrics(serviceID string, since time.Time, limit int) ([]*models.ServiceMetrics, error) {
	var metrics []*models.ServiceMetrics
	query := `
		SELECT service_id, timestamp, cpu_usage, memory_usage, request_count,
			   error_count, response_time, throughput_per_sec
		FROM service_metrics 
		WHERE service_id = $1 AND timestamp >= $2
		ORDER BY timestamp DESC 
		LIMIT $3`

	err := p.db.Select(&metrics, query, serviceID, since, limit)
	return metrics, err
}

// GetSystemHealth returns overall system health statistics
func (p *PostgresDB) GetSystemHealth() (map[string]interface{}, error) {
	var stats struct {
		TotalServices   int `db:"total_services"`
		RunningServices int `db:"running_services"`
		FailedServices  int `db:"failed_services"`
		AvgHealthScore  float64 `db:"avg_health_score"`
	}

	query := `
		SELECT 
			COUNT(*) as total_services,
			COUNT(CASE WHEN status = 'running' THEN 1 END) as running_services,
			COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_services,
			COALESCE(AVG(health_score), 0) as avg_health_score
		FROM services`

	err := p.db.Get(&stats, query)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"total_services":   stats.TotalServices,
		"running_services": stats.RunningServices,
		"failed_services":  stats.FailedServices,
		"avg_health_score": stats.AvgHealthScore,
		"system_health":    "healthy",
	}, nil
}