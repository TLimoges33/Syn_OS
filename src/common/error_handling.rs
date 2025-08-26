// Syn_OS Standardized Error Handling Framework
// Provides unified error handling, logging, and recovery patterns for Rust components

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::error::Error as StdError;
use std::time::SystemTime;
use log::{error, warn, info, debug};

/// Standardized error severity levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ErrorSeverity {
    Critical,  // System failure, requires immediate action
    High,      // Service degradation, user impact
    Medium,    // Functionality impaired, workaround available
    Low,       // Minor issues, no user impact
    Info,      // Informational, no action required
}

/// Standardized error categories
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Hash)]
pub enum ErrorCategory {
    Authentication,
    Authorization,
    Validation,
    Network,
    Database,
    Filesystem,
    Configuration,
    Consciousness,
    Integration,
    Security,
    Performance,
    System,
}

/// Structured error context for additional information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorContext {
    pub data: HashMap<String, String>,
}

impl ErrorContext {
    pub fn new() -> Self {
        Self {
            data: HashMap::new(),
        }
    }
    
    pub fn with(mut self, key: &str, value: &str) -> Self {
        self.data.insert(key.to_string(), value.to_string());
        self
    }
    
    pub fn add(&mut self, key: &str, value: &str) {
        self.data.insert(key.to_string(), value.to_string());
    }
}

impl Default for ErrorContext {
    fn default() -> Self {
        Self::new()
    }
}

/// Main error structure for Syn_OS
#[derive(Debug, Serialize, Deserialize)]
pub struct SynOSError {
    pub message: String,
    pub category: ErrorCategory,
    pub severity: ErrorSeverity,
    pub error_code: String,
    pub context: ErrorContext,
    pub timestamp: u64,
    pub service: String,
}

impl SynOSError {
    pub fn new(
        message: &str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        service: &str,
    ) -> Self {
        let error_code = format!("{:?}_{:?}", category, severity).to_uppercase();
        let timestamp = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        Self {
            message: message.to_string(),
            category,
            severity,
            error_code,
            context: ErrorContext::new(),
            timestamp,
            service: service.to_string(),
        }
    }
    
    pub fn with_context(mut self, context: ErrorContext) -> Self {
        self.context = context;
        self
    }
    
    pub fn add_context(mut self, key: &str, value: &str) -> Self {
        self.context.add(key, value);
        self
    }
    
    /// Convert error to JSON for structured logging
    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(self).unwrap_or_else(|_| self.message.clone())
    }
    
    /// Check if error is critical and requires immediate attention
    pub fn is_critical(&self) -> bool {
        matches!(self.severity, ErrorSeverity::Critical)
    }
    
    /// Get appropriate log level for this error
    pub fn log_level(&self) -> log::Level {
        match self.severity {
            ErrorSeverity::Critical => log::Level::Error,
            ErrorSeverity::High => log::Level::Error,
            ErrorSeverity::Medium => log::Level::Warn,
            ErrorSeverity::Low => log::Level::Info,
            ErrorSeverity::Info => log::Level::Debug,
        }
    }
}

impl fmt::Display for SynOSError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}: {}", self.error_code, self.service, self.message)
    }
}

impl StdError for SynOSError {}

/// Result type alias for Syn_OS operations
pub type SynOSResult<T> = Result<T, SynOSError>;

/// Error handler for centralized error management
pub struct ErrorHandler {
    service_name: String,
    error_stats: HashMap<ErrorCategory, u64>,
}

impl ErrorHandler {
    pub fn new(service_name: &str) -> Self {
        Self {
            service_name: service_name.to_string(),
            error_stats: HashMap::new(),
        }
    }
    
    /// Handle and log error with appropriate severity
    pub fn handle_error(&mut self, error: &SynOSError) {
        // Update statistics
        *self.error_stats.entry(error.category).or_insert(0) += 1;
        
        // Log with appropriate level
        match error.severity {
            ErrorSeverity::Critical => error!("[CRITICAL] {}", error.to_json()),
            ErrorSeverity::High => error!("[HIGH] {}", error.to_json()),
            ErrorSeverity::Medium => warn!("[MEDIUM] {}", error.to_json()),
            ErrorSeverity::Low => info!("[LOW] {}", error.to_json()),
            ErrorSeverity::Info => debug!("[INFO] {}", error.to_json()),
        }
        
        // Send alerts for critical errors
        if error.is_critical() {
            self.send_critical_alert(error);
        }
    }
    
    /// Send critical error alerts
    fn send_critical_alert(&self, error: &SynOSError) {
        // In a real implementation, this would integrate with alerting systems
        // For now, log to a special critical alerts file
        use std::fs::OpenOptions;
        use std::io::Write;
        
        if let Ok(mut file) = OpenOptions::new()
            .create(true)
            .append(true)
            .open("/home/diablorain/Syn_OS/logs/errors/critical_alerts.log")
        {
            let alert = format!("CRITICAL ALERT: {}\n", error.to_json());
            let _ = file.write_all(alert.as_bytes());
        }
    }
    
    /// Get error statistics for monitoring
    pub fn get_error_statistics(&self) -> HashMap<ErrorCategory, u64> {
        self.error_stats.clone()
    }
    
    /// Reset error statistics
    pub fn reset_statistics(&mut self) {
        self.error_stats.clear();
    }
}

/// Macro for creating specific error types
macro_rules! define_error_type {
    ($name:ident, $category:expr) => {
        pub fn $name(message: &str, service: &str) -> SynOSError {
            SynOSError::new(message, $category, ErrorSeverity::Medium, service)
        }
    };
}

// Define specific error constructors
define_error_type!(authentication_error, ErrorCategory::Authentication);
define_error_type!(authorization_error, ErrorCategory::Authorization);
define_error_type!(validation_error, ErrorCategory::Validation);
define_error_type!(network_error, ErrorCategory::Network);
define_error_type!(database_error, ErrorCategory::Database);
define_error_type!(filesystem_error, ErrorCategory::Filesystem);
define_error_type!(configuration_error, ErrorCategory::Configuration);
define_error_type!(consciousness_error, ErrorCategory::Consciousness);
define_error_type!(integration_error, ErrorCategory::Integration);
define_error_type!(security_error, ErrorCategory::Security);
define_error_type!(performance_error, ErrorCategory::Performance);
define_error_type!(system_error, ErrorCategory::System);

/// Trait for converting standard errors to SynOSError
pub trait IntoSynOSError {
    fn into_syn_os_error(self, category: ErrorCategory, service: &str) -> SynOSError;
}

impl<E: StdError> IntoSynOSError for E {
    fn into_syn_os_error(self, category: ErrorCategory, service: &str) -> SynOSError {
        SynOSError::new(&self.to_string(), category, ErrorSeverity::Medium, service)
            .add_context("original_error", &self.to_string())
    }
}

/// Extension trait for Result to add context and convert errors
pub trait ResultExt<T> {
    /// Add context to error if Result is Err
    fn with_context(self, key: &str, value: &str) -> SynOSResult<T>;
    
    /// Convert standard Result to SynOSResult with specified category
    fn to_syn_os_result(self, category: ErrorCategory, service: &str) -> SynOSResult<T>;
    
    /// Log error and continue with default value
    fn log_and_default(self, default: T, handler: &mut ErrorHandler) -> T;
}

impl<T, E: StdError> ResultExt<T> for Result<T, E> {
    fn with_context(self, key: &str, value: &str) -> SynOSResult<T> {
        self.map_err(|e| {
            e.into_syn_os_error(ErrorCategory::System, "unknown")
                .add_context(key, value)
        })
    }
    
    fn to_syn_os_result(self, category: ErrorCategory, service: &str) -> SynOSResult<T> {
        self.map_err(|e| e.into_syn_os_error(category, service))
    }
    
    fn log_and_default(self, default: T, handler: &mut ErrorHandler) -> T {
        match self {
            Ok(value) => value,
            Err(e) => {
                let syn_error = e.into_syn_os_error(ErrorCategory::System, "unknown");
                handler.handle_error(&syn_error);
                default
            }
        }
    }
}

impl<T> ResultExt<T> for SynOSResult<T> {
    fn with_context(self, key: &str, value: &str) -> SynOSResult<T> {
        self.map_err(|e| e.add_context(key, value))
    }
    
    fn to_syn_os_result(self, _category: ErrorCategory, _service: &str) -> SynOSResult<T> {
        self
    }
    
    fn log_and_default(self, default: T, handler: &mut ErrorHandler) -> T {
        match self {
            Ok(value) => value,
            Err(e) => {
                handler.handle_error(&e);
                default
            }
        }
    }
}

/// Safe execution function that catches panics and converts to errors
pub fn safe_execute<F, T>(f: F, service: &str) -> SynOSResult<T>
where
    F: FnOnce() -> T,
{
    match std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)) {
        Ok(result) => Ok(result),
        Err(_) => Err(system_error("Function panicked during execution", service)
            .add_context("panic", "true")),
    }
}

/// Convenience macro for error handling in functions
#[macro_export]
macro_rules! handle_error {
    ($result:expr, $handler:expr) => {
        match $result {
            Ok(val) => val,
            Err(e) => {
                $handler.handle_error(&e);
                return Err(e);
            }
        }
    };
}

/// Convenience macro for logging errors without returning
#[macro_export]
macro_rules! log_error {
    ($result:expr, $handler:expr) => {
        if let Err(e) = $result {
            $handler.handle_error(&e);
        }
    };
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_error_creation() {
        let error = validation_error("Invalid input", "test_service")
            .add_context("input", "invalid_data");
        
        assert_eq!(error.category, ErrorCategory::Validation);
        assert_eq!(error.severity, ErrorSeverity::Medium);
        assert!(error.context.data.contains_key("input"));
    }
    
    #[test]
    fn test_error_handler() {
        let mut handler = ErrorHandler::new("test");
        let error = system_error("Test error", "test");
        
        handler.handle_error(&error);
        let stats = handler.get_error_statistics();
        
        assert_eq!(stats[&ErrorCategory::System], 1);
    }
    
    #[test]
    fn test_result_extensions() {
        let result: Result<i32, std::io::Error> = Err(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "File not found"
        ));
        
        let syn_result = result.to_syn_os_result(ErrorCategory::Filesystem, "test");
        assert!(syn_result.is_err());
        
        if let Err(e) = syn_result {
            assert_eq!(e.category, ErrorCategory::Filesystem);
        }
    }
}
