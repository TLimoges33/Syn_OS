// Package errors provides standardized error handling for Syn_OS Go components
package errors

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"time"
)

// ErrorSeverity defines the severity levels for errors
type ErrorSeverity string

const (
	SeverityCritical ErrorSeverity = "CRITICAL" // System failure, requires immediate action
	SeverityHigh     ErrorSeverity = "HIGH"     // Service degradation, user impact
	SeverityMedium   ErrorSeverity = "MEDIUM"   // Functionality impaired, workaround available
	SeverityLow      ErrorSeverity = "LOW"      // Minor issues, no user impact
	SeverityInfo     ErrorSeverity = "INFO"     // Informational, no action required
)

// ErrorCategory defines the categories of errors
type ErrorCategory string

const (
	CategoryAuthentication ErrorCategory = "AUTHENTICATION"
	CategoryAuthorization  ErrorCategory = "AUTHORIZATION"
	CategoryValidation     ErrorCategory = "VALIDATION"
	CategoryNetwork        ErrorCategory = "NETWORK"
	CategoryDatabase       ErrorCategory = "DATABASE"
	CategoryFilesystem     ErrorCategory = "FILESYSTEM"
	CategoryConfiguration  ErrorCategory = "CONFIGURATION"
	CategoryConsciousness  ErrorCategory = "CONSCIOUSNESS"
	CategoryIntegration    ErrorCategory = "INTEGRATION"
	CategorySecurity       ErrorCategory = "SECURITY"
	CategoryPerformance    ErrorCategory = "PERFORMANCE"
	CategorySystem         ErrorCategory = "SYSTEM"
)

// ErrorContext provides additional context for errors
type ErrorContext map[string]interface{}

// SynOSError represents a standardized error in Syn_OS
type SynOSError struct {
	Message       string        `json:"message"`
	Category      ErrorCategory `json:"category"`
	Severity      ErrorSeverity `json:"severity"`
	ErrorCode     string        `json:"error_code"`
	Context       ErrorContext  `json:"context"`
	Timestamp     time.Time     `json:"timestamp"`
	Service       string        `json:"service"`
	StackTrace    string        `json:"stack_trace,omitempty"`
	OriginalError error         `json:"original_error,omitempty"`
}

// Error implements the error interface
func (e *SynOSError) Error() string {
	return fmt.Sprintf("[%s] %s: %s", e.ErrorCode, e.Service, e.Message)
}

// NewError creates a new SynOSError
func NewError(message string, category ErrorCategory, severity ErrorSeverity, service string) *SynOSError {
	errorCode := fmt.Sprintf("%s_%s", category, severity)

	// Get stack trace
	buf := make([]byte, 1024)
	runtime.Stack(buf, false)

	return &SynOSError{
		Message:    message,
		Category:   category,
		Severity:   severity,
		ErrorCode:  errorCode,
		Context:    make(ErrorContext),
		Timestamp:  time.Now().UTC(),
		Service:    service,
		StackTrace: string(buf),
	}
}

// WithContext adds context to the error
func (e *SynOSError) WithContext(key string, value interface{}) *SynOSError {
	e.Context[key] = value
	return e
}

// WithOriginalError adds the original error that caused this error
func (e *SynOSError) WithOriginalError(err error) *SynOSError {
	e.OriginalError = err
	if e.Context == nil {
		e.Context = make(ErrorContext)
	}
	e.Context["original_error"] = err.Error()
	return e
}

// IsCritical returns true if the error is critical
func (e *SynOSError) IsCritical() bool {
	return e.Severity == SeverityCritical
}

// ToJSON returns the error as a JSON string
func (e *SynOSError) ToJSON() string {
	jsonBytes, err := json.MarshalIndent(e, "", "  ")
	if err != nil {
		return fmt.Sprintf(`{"error": "Failed to marshal error to JSON: %s", "original_message": "%s"}`, err.Error(), e.Message)
	}
	return string(jsonBytes)
}

// ErrorHandler manages error handling and logging for a service
type ErrorHandler struct {
	ServiceName  string
	LogFile      *os.File
	ErrorStats   map[ErrorCategory]int64
	AlertChannel chan *SynOSError
}

// NewErrorHandler creates a new error handler
func NewErrorHandler(serviceName string) (*ErrorHandler, error) {
	// Create logs directory if it doesn't exist
	logDir := "/home/diablorain/Syn_OS/logs/errors"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create log directory: %w", err)
	}

	// Open log file
	logFile, err := os.OpenFile(
		filepath.Join(logDir, fmt.Sprintf("%s_errors.log", serviceName)),
		os.O_CREATE|os.O_WRONLY|os.O_APPEND,
		0644,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to open log file: %w", err)
	}

	handler := &ErrorHandler{
		ServiceName:  serviceName,
		LogFile:      logFile,
		ErrorStats:   make(map[ErrorCategory]int64),
		AlertChannel: make(chan *SynOSError, 100), // Buffered channel for alerts
	}

	// Start alert processor
	go handler.processAlerts()

	return handler, nil
}

// HandleError processes and logs an error
func (h *ErrorHandler) HandleError(err *SynOSError) {
	// Update statistics
	h.ErrorStats[err.Category]++

	// Log error
	logEntry := fmt.Sprintf("%s - %s\n", time.Now().UTC().Format(time.RFC3339), err.ToJSON())
	if _, writeErr := h.LogFile.WriteString(logEntry); writeErr != nil {
		log.Printf("Failed to write error to log file: %v", writeErr)
	}

	// Log to standard logger based on severity
	switch err.Severity {
	case SeverityCritical, SeverityHigh:
		log.Printf("ERROR: %s", err.Error())
	case SeverityMedium:
		log.Printf("WARN: %s", err.Error())
	case SeverityLow, SeverityInfo:
		log.Printf("INFO: %s", err.Error())
	}

	// Send alert for critical errors
	if err.IsCritical() {
		select {
		case h.AlertChannel <- err:
		default:
			log.Printf("Alert channel full, dropping critical alert: %s", err.Error())
		}
	}
}

// processAlerts handles critical error alerts
func (h *ErrorHandler) processAlerts() {
	alertFile, err := os.OpenFile(
		"/home/diablorain/Syn_OS/logs/errors/critical_alerts.log",
		os.O_CREATE|os.O_WRONLY|os.O_APPEND,
		0644,
	)
	if err != nil {
		log.Printf("Failed to open critical alerts file: %v", err)
		return
	}
	defer alertFile.Close()

	for alert := range h.AlertChannel {
		alertEntry := fmt.Sprintf("%s - CRITICAL ALERT: %s\n",
			time.Now().UTC().Format(time.RFC3339), alert.ToJSON())

		if _, err := alertFile.WriteString(alertEntry); err != nil {
			log.Printf("Failed to write critical alert: %v", err)
		}

		// Here you could integrate with external alerting systems
		// like PagerDuty, Slack, email, etc.
		log.Printf("🚨 CRITICAL ALERT: %s", alert.Error())
	}
}

// GetErrorStatistics returns error statistics
func (h *ErrorHandler) GetErrorStatistics() map[ErrorCategory]int64 {
	stats := make(map[ErrorCategory]int64)
	for category, count := range h.ErrorStats {
		stats[category] = count
	}
	return stats
}

// ResetStatistics resets error statistics
func (h *ErrorHandler) ResetStatistics() {
	h.ErrorStats = make(map[ErrorCategory]int64)
}

// Close closes the error handler and its resources
func (h *ErrorHandler) Close() error {
	close(h.AlertChannel)
	return h.LogFile.Close()
}

// Convenience functions for creating specific error types

// AuthenticationError creates an authentication error
func AuthenticationError(message, service string) *SynOSError {
	return NewError(message, CategoryAuthentication, SeverityHigh, service)
}

// AuthorizationError creates an authorization error
func AuthorizationError(message, service string) *SynOSError {
	return NewError(message, CategoryAuthorization, SeverityHigh, service)
}

// ValidationError creates a validation error
func ValidationError(message, service string) *SynOSError {
	return NewError(message, CategoryValidation, SeverityMedium, service)
}

// NetworkError creates a network error
func NetworkError(message, service string) *SynOSError {
	return NewError(message, CategoryNetwork, SeverityMedium, service)
}

// DatabaseError creates a database error
func DatabaseError(message, service string) *SynOSError {
	return NewError(message, CategoryDatabase, SeverityHigh, service)
}

// FilesystemError creates a filesystem error
func FilesystemError(message, service string) *SynOSError {
	return NewError(message, CategoryFilesystem, SeverityMedium, service)
}

// ConfigurationError creates a configuration error
func ConfigurationError(message, service string) *SynOSError {
	return NewError(message, CategoryConfiguration, SeverityHigh, service)
}

// ConsciousnessError creates a consciousness error
func ConsciousnessError(message, service string) *SynOSError {
	return NewError(message, CategoryConsciousness, SeverityCritical, service)
}

// IntegrationError creates an integration error
func IntegrationError(message, service string) *SynOSError {
	return NewError(message, CategoryIntegration, SeverityMedium, service)
}

// SecurityError creates a security error
func SecurityError(message, service string) *SynOSError {
	return NewError(message, CategorySecurity, SeverityCritical, service)
}

// PerformanceError creates a performance error
func PerformanceError(message, service string) *SynOSError {
	return NewError(message, CategoryPerformance, SeverityLow, service)
}

// SystemError creates a system error
func SystemError(message, service string) *SynOSError {
	return NewError(message, CategorySystem, SeverityMedium, service)
}

// Wrap wraps a standard error into a SynOSError
func Wrap(err error, category ErrorCategory, service string) *SynOSError {
	if err == nil {
		return nil
	}

	synError := NewError(err.Error(), category, SeverityMedium, service)
	return synError.WithOriginalError(err)
}

// WrapWithMessage wraps a standard error with a custom message
func WrapWithMessage(err error, message string, category ErrorCategory, service string) *SynOSError {
	if err == nil {
		return nil
	}

	synError := NewError(message, category, SeverityMedium, service)
	return synError.WithOriginalError(err)
}

// Safe execution functions

// SafeExecute executes a function and converts any panic to a SynOSError
func SafeExecute(fn func() error, service string) (err *SynOSError) {
	defer func() {
		if r := recover(); r != nil {
			err = SystemError(fmt.Sprintf("Function panicked: %v", r), service).
				WithContext("panic", true)
		}
	}()

	if fnErr := fn(); fnErr != nil {
		if synErr, ok := fnErr.(*SynOSError); ok {
			return synErr
		}
		return Wrap(fnErr, CategorySystem, service)
	}

	return nil
}

// LogAndContinue logs an error and continues execution
func LogAndContinue(err error, handler *ErrorHandler, service string) {
	if err == nil {
		return
	}

	var synErr *SynOSError
	if se, ok := err.(*SynOSError); ok {
		synErr = se
	} else {
		synErr = Wrap(err, CategorySystem, service)
	}

	handler.HandleError(synErr)
}

// MustNotError panics if error is not nil (for initialization code)
func MustNotError(err error, message string) {
	if err != nil {
		panic(fmt.Sprintf("%s: %v", message, err))
	}
}

// Example usage and testing
func Example() {
	// Create error handler
	handler, err := NewErrorHandler("example_service")
	if err != nil {
		log.Fatal("Failed to create error handler:", err)
	}
	defer handler.Close()

	// Create and handle different types of errors
	authErr := AuthenticationError("Invalid credentials", "auth_service").
		WithContext("user_id", "12345").
		WithContext("ip_address", "192.168.1.100")

	handler.HandleError(authErr)

	// Wrap a standard error
	_, openErr := os.Open("/nonexistent/file")
	if openErr != nil {
		synErr := Wrap(openErr, CategoryFilesystem, "file_service").
			WithContext("operation", "open_file").
			WithContext("file_path", "/nonexistent/file")

		handler.HandleError(synErr)
	}

	// Safe execution example
	if execErr := SafeExecute(func() error {
		// This would panic
		panic("Something went wrong")
	}, "test_service"); execErr != nil {
		handler.HandleError(execErr)
	}

	// Print statistics
	stats := handler.GetErrorStatistics()
	for category, count := range stats {
		log.Printf("Category %s: %d errors", category, count)
	}
}
