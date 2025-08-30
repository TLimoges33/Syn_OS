package database

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	_ "github.com/lib/pq"
)

// OptimizedDB provides optimized database operations
type OptimizedDB struct {
	db           *sqlx.DB
	queryCache   map[string]*sql.Stmt
	enableCache  bool
	queryMetrics map[string]*QueryMetrics
}

// QueryMetrics tracks query performance
type QueryMetrics struct {
	QueryName    string
	ExecutionCount int64
	TotalTime    time.Duration
	AverageTime  time.Duration
	MaxTime      time.Duration
	MinTime      time.Duration
	ErrorCount   int64
}

// ServiceRecord represents optimized service data structure
type ServiceRecord struct {
	ID                string         `db:"id" json:"id"`
	Name             string         `db:"name" json:"name"`
	Type             string         `db:"type" json:"type"`
	Status           string         `db:"status" json:"status"`
	HealthScore      float64        `db:"health_score" json:"health_score"`
	LastHealthCheck  time.Time      `db:"last_health_check" json:"last_health_check"`
	ConfigData       map[string]interface{} `db:"config_data" json:"config_data"`
	MetricsData      map[string]interface{} `db:"metrics_data" json:"metrics_data"`
	CreatedAt        time.Time      `db:"created_at" json:"created_at"`
	UpdatedAt        time.Time      `db:"updated_at" json:"updated_at"`
	ConsciousnessLevel float64      `db:"consciousness_level" json:"consciousness_level"`
	Priority         int            `db:"priority" json:"priority"`
}

// EventRecord represents optimized event data structure
type EventRecord struct {
	ID           string                 `db:"id" json:"id"`
	Type         string                 `db:"type" json:"type"`
	Source       string                 `db:"source" json:"source"`
	Target       string                 `db:"target" json:"target"`
	EventData    map[string]interface{} `db:"event_data" json:"event_data"`
	Severity     string                 `db:"severity" json:"severity"`
	Status       string                 `db:"status" json:"status"`
	ProcessedAt  *time.Time             `db:"processed_at" json:"processed_at"`
	CreatedAt    time.Time              `db:"created_at" json:"created_at"`
	Priority     int                    `db:"priority" json:"priority"`
}

// NewOptimizedDB creates a new optimized database connection
func NewOptimizedDB(connectionString string) (*OptimizedDB, error) {
	// Configure connection pool for optimal performance
	db, err := sqlx.Connect("postgres", connectionString)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Optimize connection pool settings
	db.SetMaxOpenConns(25)          // Maximum open connections
	db.SetMaxIdleConns(10)          // Maximum idle connections
	db.SetConnMaxLifetime(5 * time.Minute) // Connection lifetime
	db.SetConnMaxIdleTime(2 * time.Minute) // Idle connection timeout

	optimizedDB := &OptimizedDB{
		db:           db,
		queryCache:   make(map[string]*sql.Stmt),
		enableCache:  true,
		queryMetrics: make(map[string]*QueryMetrics),
	}

	// Initialize database schema if needed
	if err := optimizedDB.initializeSchema(); err != nil {
		return nil, fmt.Errorf("failed to initialize database schema: %w", err)
	}

	// Create optimized indexes
	if err := optimizedDB.createOptimizedIndexes(); err != nil {
		log.Printf("Warning: Failed to create some indexes: %v", err)
	}

	return optimizedDB, nil
}

// initializeSchema creates optimized database schema
func (odb *OptimizedDB) initializeSchema() error {
	ctx := context.Background()

	// Services table with optimizations
	servicesSchema := `
		CREATE TABLE IF NOT EXISTS services (
			id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
			name VARCHAR(255) NOT NULL,
			type VARCHAR(100) NOT NULL,
			status VARCHAR(50) NOT NULL DEFAULT 'unknown',
			health_score DECIMAL(3,2) DEFAULT 0.0,
			last_health_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
			config_data JSONB DEFAULT '{}',
			metrics_data JSONB DEFAULT '{}',
			created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
			updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
			consciousness_level DECIMAL(3,2) DEFAULT 0.0,
			priority INTEGER DEFAULT 5,
			CONSTRAINT valid_health_score CHECK (health_score >= 0.0 AND health_score <= 1.0),
			CONSTRAINT valid_consciousness CHECK (consciousness_level >= 0.0 AND consciousness_level <= 1.0),
			CONSTRAINT valid_priority CHECK (priority >= 1 AND priority <= 10)
		);
	`

	// Events table with partitioning for performance
	eventsSchema := `
		CREATE TABLE IF NOT EXISTS events (
			id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
			type VARCHAR(100) NOT NULL,
			source VARCHAR(255) NOT NULL,
			target VARCHAR(255),
			event_data JSONB DEFAULT '{}',
			severity VARCHAR(50) NOT NULL DEFAULT 'info',
			status VARCHAR(50) NOT NULL DEFAULT 'pending',
			processed_at TIMESTAMP WITH TIME ZONE,
			created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
			priority INTEGER DEFAULT 5,
			CONSTRAINT valid_priority CHECK (priority >= 1 AND priority <= 10)
		);
	`

	// Service metrics table for time-series data
	metricsSchema := `
		CREATE TABLE IF NOT EXISTS service_metrics (
			id BIGSERIAL PRIMARY KEY,
			service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
			metric_name VARCHAR(255) NOT NULL,
			metric_value DECIMAL(15,6) NOT NULL,
			timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
			tags JSONB DEFAULT '{}'
		);
	`

	// Consciousness states table
	consciousnessSchema := `
		CREATE TABLE IF NOT EXISTS consciousness_states (
			id BIGSERIAL PRIMARY KEY,
			service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
			consciousness_level DECIMAL(3,2) NOT NULL,
			awareness_score DECIMAL(3,2) NOT NULL,
			coherence_score DECIMAL(3,2) NOT NULL,
			state_data JSONB DEFAULT '{}',
			created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
			CONSTRAINT valid_consciousness CHECK (consciousness_level >= 0.0 AND consciousness_level <= 1.0),
			CONSTRAINT valid_awareness CHECK (awareness_score >= 0.0 AND awareness_score <= 1.0),
			CONSTRAINT valid_coherence CHECK (coherence_score >= 0.0 AND coherence_score <= 1.0)
		);
	`

	schemas := []string{servicesSchema, eventsSchema, metricsSchema, consciousnessSchema}

	for _, schema := range schemas {
		if _, err := odb.db.ExecContext(ctx, schema); err != nil {
			return fmt.Errorf("failed to create schema: %w", err)
		}
	}

	return nil
}

// createOptimizedIndexes creates performance-optimized database indexes
func (odb *OptimizedDB) createOptimizedIndexes() error {
	ctx := context.Background()

	indexes := []string{
		// Services table indexes
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_name ON services (name)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_type ON services (type)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_status ON services (status)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_health_score ON services (health_score DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_consciousness ON services (consciousness_level DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_priority ON services (priority ASC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_updated_at ON services (updated_at DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_type_status ON services (type, status)",

		// Events table indexes
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_type ON events (type)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_source ON events (source)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_severity ON events (severity)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_status ON events (status)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_created_at ON events (created_at DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_priority ON events (priority ASC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_processed_at ON events (processed_at DESC) WHERE processed_at IS NOT NULL",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_unprocessed ON events (created_at ASC) WHERE processed_at IS NULL",

		// Service metrics indexes
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_metrics_service_id ON service_metrics (service_id)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_metrics_timestamp ON service_metrics (timestamp DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_metrics_name ON service_metrics (metric_name)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_metrics_service_time ON service_metrics (service_id, timestamp DESC)",

		// Consciousness states indexes
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consciousness_service_id ON consciousness_states (service_id)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consciousness_created_at ON consciousness_states (created_at DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consciousness_level ON consciousness_states (consciousness_level DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consciousness_service_time ON consciousness_states (service_id, created_at DESC)",

		// Composite indexes for common queries
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_services_health_priority ON services (health_score DESC, priority ASC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_severity_status ON events (severity, status, created_at DESC)",
	}

	for _, indexSQL := range indexes {
		if _, err := odb.db.ExecContext(ctx, indexSQL); err != nil {
			// Log warning but continue - some indexes might already exist
			log.Printf("Warning: Failed to create index: %v", err)
		}
	}

	return nil
}

// GetServiceByID retrieves a service by ID with optimized query
func (odb *OptimizedDB) GetServiceByID(ctx context.Context, serviceID string) (*ServiceRecord, error) {
	startTime := time.Now()
	queryName := "GetServiceByID"

	query := `
		SELECT id, name, type, status, health_score, last_health_check,
			   config_data, metrics_data, created_at, updated_at,
			   consciousness_level, priority
		FROM services 
		WHERE id = $1
	`

	var service ServiceRecord
	err := odb.db.GetContext(ctx, &service, query, serviceID)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("service not found: %s", serviceID)
		}
		return nil, fmt.Errorf("failed to get service: %w", err)
	}

	return &service, nil
}

// GetServicesByType retrieves services by type with optimized pagination
func (odb *OptimizedDB) GetServicesByType(ctx context.Context, serviceType string, limit, offset int) ([]*ServiceRecord, error) {
	startTime := time.Now()
	queryName := "GetServicesByType"

	query := `
		SELECT id, name, type, status, health_score, last_health_check,
			   config_data, metrics_data, created_at, updated_at,
			   consciousness_level, priority
		FROM services 
		WHERE type = $1
		ORDER BY consciousness_level DESC, health_score DESC, priority ASC
		LIMIT $2 OFFSET $3
	`

	var services []*ServiceRecord
	err := odb.db.SelectContext(ctx, &services, query, serviceType, limit, offset)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return nil, fmt.Errorf("failed to get services by type: %w", err)
	}

	return services, nil
}

// GetHealthyServices retrieves services with health score above threshold
func (odb *OptimizedDB) GetHealthyServices(ctx context.Context, minHealthScore float64, limit int) ([]*ServiceRecord, error) {
	startTime := time.Now()
	queryName := "GetHealthyServices"

	query := `
		SELECT id, name, type, status, health_score, last_health_check,
			   config_data, metrics_data, created_at, updated_at,
			   consciousness_level, priority
		FROM services 
		WHERE health_score >= $1 AND status = 'running'
		ORDER BY health_score DESC, consciousness_level DESC
		LIMIT $2
	`

	var services []*ServiceRecord
	err := odb.db.SelectContext(ctx, &services, query, minHealthScore, limit)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return nil, fmt.Errorf("failed to get healthy services: %w", err)
	}

	return services, nil
}

// UpdateServiceHealth updates service health with optimized query
func (odb *OptimizedDB) UpdateServiceHealth(ctx context.Context, serviceID string, healthScore float64, consciousnessLevel float64) error {
	startTime := time.Now()
	queryName := "UpdateServiceHealth"

	query := `
		UPDATE services 
		SET health_score = $2, 
			consciousness_level = $3,
			last_health_check = NOW(),
			updated_at = NOW()
		WHERE id = $1
	`

	result, err := odb.db.ExecContext(ctx, query, serviceID, healthScore, consciousnessLevel)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return fmt.Errorf("failed to update service health: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("service not found: %s", serviceID)
	}

	return nil
}

// CreateEvent creates a new event with optimized insert
func (odb *OptimizedDB) CreateEvent(ctx context.Context, event *EventRecord) error {
	startTime := time.Now()
	queryName := "CreateEvent"

	query := `
		INSERT INTO events (type, source, target, event_data, severity, status, priority)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id, created_at
	`

	err := odb.db.QueryRowContext(
		ctx, query,
		event.Type, event.Source, event.Target, event.EventData,
		event.Severity, event.Status, event.Priority,
	).Scan(&event.ID, &event.CreatedAt)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return fmt.Errorf("failed to create event: %w", err)
	}

	return nil
}

// GetUnprocessedEvents retrieves unprocessed events with priority ordering
func (odb *OptimizedDB) GetUnprocessedEvents(ctx context.Context, limit int) ([]*EventRecord, error) {
	startTime := time.Now()
	queryName := "GetUnprocessedEvents"

	query := `
		SELECT id, type, source, target, event_data, severity, status,
			   processed_at, created_at, priority
		FROM events 
		WHERE processed_at IS NULL
		ORDER BY priority ASC, created_at ASC
		LIMIT $1
	`

	var events []*EventRecord
	err := odb.db.SelectContext(ctx, &events, query, limit)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return nil, fmt.Errorf("failed to get unprocessed events: %w", err)
	}

	return events, nil
}

// BatchUpdateEventStatus updates multiple event statuses in a single transaction
func (odb *OptimizedDB) BatchUpdateEventStatus(ctx context.Context, eventIDs []string, status string) error {
	if len(eventIDs) == 0 {
		return nil
	}

	startTime := time.Now()
	queryName := "BatchUpdateEventStatus"

	tx, err := odb.db.BeginTxx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	query := `
		UPDATE events 
		SET status = $1, processed_at = NOW()
		WHERE id = ANY($2)
	`

	_, err = tx.ExecContext(ctx, query, status, pq.Array(eventIDs))
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return fmt.Errorf("failed to batch update event status: %w", err)
	}

	if err = tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	return nil
}

// RecordServiceMetrics records service metrics in batch for efficiency
func (odb *OptimizedDB) RecordServiceMetrics(ctx context.Context, serviceID string, metrics map[string]float64) error {
	if len(metrics) == 0 {
		return nil
	}

	startTime := time.Now()
	queryName := "RecordServiceMetrics"

	tx, err := odb.db.BeginTxx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	query := `
		INSERT INTO service_metrics (service_id, metric_name, metric_value, timestamp)
		VALUES ($1, $2, $3, NOW())
	`

	stmt, err := tx.PreparexContext(ctx, query)
	if err != nil {
		return fmt.Errorf("failed to prepare statement: %w", err)
	}
	defer stmt.Close()

	for metricName, metricValue := range metrics {
		if _, err := stmt.ExecContext(ctx, serviceID, metricName, metricValue); err != nil {
			return fmt.Errorf("failed to insert metric %s: %w", metricName, err)
		}
	}

	odb.recordQueryMetrics(queryName, startTime, nil)

	if err = tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	return nil
}

// GetServiceMetricsHistory retrieves service metrics history with time range
func (odb *OptimizedDB) GetServiceMetricsHistory(ctx context.Context, serviceID string, metricName string, since time.Time, limit int) ([]ServiceMetric, error) {
	startTime := time.Now()
	queryName := "GetServiceMetricsHistory"

	query := `
		SELECT metric_name, metric_value, timestamp, tags
		FROM service_metrics 
		WHERE service_id = $1 AND metric_name = $2 AND timestamp >= $3
		ORDER BY timestamp DESC
		LIMIT $4
	`

	type ServiceMetric struct {
		MetricName  string                 `db:"metric_name"`
		MetricValue float64                `db:"metric_value"`
		Timestamp   time.Time              `db:"timestamp"`
		Tags        map[string]interface{} `db:"tags"`
	}

	var metrics []ServiceMetric
	err := odb.db.SelectContext(ctx, &metrics, query, serviceID, metricName, since, limit)
	
	odb.recordQueryMetrics(queryName, startTime, err)
	
	if err != nil {
		return nil, fmt.Errorf("failed to get service metrics history: %w", err)
	}

	return metrics, nil
}

// CleanupOldData removes old data to maintain performance
func (odb *OptimizedDB) CleanupOldData(ctx context.Context, retentionDays int) error {
	startTime := time.Now()
	queryName := "CleanupOldData"

	cutoffDate := time.Now().AddDate(0, 0, -retentionDays)

	tx, err := odb.db.BeginTxx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Clean old processed events
	_, err = tx.ExecContext(ctx, `
		DELETE FROM events 
		WHERE processed_at IS NOT NULL AND processed_at < $1
	`, cutoffDate)
	if err != nil {
		return fmt.Errorf("failed to cleanup old events: %w", err)
	}

	// Clean old metrics data
	_, err = tx.ExecContext(ctx, `
		DELETE FROM service_metrics 
		WHERE timestamp < $1
	`, cutoffDate)
	if err != nil {
		return fmt.Errorf("failed to cleanup old metrics: %w", err)
	}

	// Clean old consciousness states
	_, err = tx.ExecContext(ctx, `
		DELETE FROM consciousness_states 
		WHERE created_at < $1
	`, cutoffDate)
	if err != nil {
		return fmt.Errorf("failed to cleanup old consciousness states: %w", err)
	}

	odb.recordQueryMetrics(queryName, startTime, nil)

	if err = tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit cleanup transaction: %w", err)
	}

	return nil
}

// recordQueryMetrics tracks query performance metrics
func (odb *OptimizedDB) recordQueryMetrics(queryName string, startTime time.Time, err error) {
	duration := time.Since(startTime)

	metrics, exists := odb.queryMetrics[queryName]
	if !exists {
		metrics = &QueryMetrics{
			QueryName: queryName,
			MinTime:   duration,
			MaxTime:   duration,
		}
		odb.queryMetrics[queryName] = metrics
	}

	metrics.ExecutionCount++
	metrics.TotalTime += duration

	if err != nil {
		metrics.ErrorCount++
	}

	if duration > metrics.MaxTime {
		metrics.MaxTime = duration
	}
	if duration < metrics.MinTime {
		metrics.MinTime = duration
	}

	metrics.AverageTime = time.Duration(int64(metrics.TotalTime) / metrics.ExecutionCount)
}

// GetQueryMetrics returns query performance metrics
func (odb *OptimizedDB) GetQueryMetrics() map[string]*QueryMetrics {
	return odb.queryMetrics
}

// GetPerformanceReport generates a database performance report
func (odb *OptimizedDB) GetPerformanceReport() map[string]interface{} {
	report := make(map[string]interface{})
	
	report["total_queries"] = len(odb.queryMetrics)
	
	var totalExecutions int64
	var totalTime time.Duration
	var slowestQuery string
	var slowestTime time.Duration

	queryDetails := make([]map[string]interface{}, 0, len(odb.queryMetrics))

	for _, metrics := range odb.queryMetrics {
		totalExecutions += metrics.ExecutionCount
		totalTime += metrics.TotalTime

		if metrics.AverageTime > slowestTime {
			slowestTime = metrics.AverageTime
			slowestQuery = metrics.QueryName
		}

		queryDetail := map[string]interface{}{
			"query_name":      metrics.QueryName,
			"execution_count": metrics.ExecutionCount,
			"average_time":    metrics.AverageTime.Milliseconds(),
			"max_time":        metrics.MaxTime.Milliseconds(),
			"min_time":        metrics.MinTime.Milliseconds(),
			"error_count":     metrics.ErrorCount,
			"error_rate":      float64(metrics.ErrorCount) / float64(metrics.ExecutionCount),
		}
		queryDetails = append(queryDetails, queryDetail)
	}

	report["total_executions"] = totalExecutions
	report["total_time_ms"] = totalTime.Milliseconds()
	report["slowest_query"] = slowestQuery
	report["slowest_average_time_ms"] = slowestTime.Milliseconds()
	report["query_details"] = queryDetails

	if totalExecutions > 0 {
		report["average_query_time_ms"] = (totalTime / time.Duration(totalExecutions)).Milliseconds()
	}

	return report
}

// Close closes the database connection
func (odb *OptimizedDB) Close() error {
	// Close prepared statements
	for _, stmt := range odb.queryCache {
		stmt.Close()
	}
	
	return odb.db.Close()
}