// Phase 4.2: Advanced Multi-Level Logging System
// Comprehensive logging infrastructure with consciousness integration

use alloc::{collections::BTreeMap, format, string::String, vec, vec::Vec};
use core::fmt::{Debug, Write};
use lazy_static::lazy_static;
use serde::{Deserialize, Serialize};
use spin::Mutex;
use uart_16550::SerialPort;

use crate::consciousness_monitor::{
    log_consciousness_event, ConsciousnessEventType, EventSeverity,
};

/// Advanced logging levels with consciousness integration
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum LogLevel {
    Emergency = 0, // System is unusable
    Alert = 1,     // Action must be taken immediately
    Critical = 2,  // Critical conditions
    Error = 3,     // Error conditions
    Warning = 4,   // Warning conditions
    Notice = 5,    // Normal but significant condition
    Info = 6,      // Informational messages
    Debug = 7,     // Debug-level messages
    Trace = 8,     // Very detailed debugging
}

/// Log categories for filtering and organization
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum LogCategory {
    Kernel,
    Memory,
    Security,
    AI,
    Consciousness,
    Performance,
    Hardware,
    Network,
    FileSystem,
    UserSpace,
}

/// Log destination types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogDestination {
    Serial,
    Memory,
    Console,
    File,
    Network,
}

/// Individual log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub timestamp: u64,
    pub level: LogLevel,
    pub category: LogCategory,
    pub component: String,
    pub message: String,
    pub metadata: BTreeMap<String, String>,
    pub thread_id: Option<u32>,
    pub cpu_id: Option<u8>,
}

/// Log buffer for memory-based logging
#[derive(Debug)]
pub struct LogBuffer {
    entries: Vec<LogEntry>,
    max_entries: usize,
    dropped_count: usize,
}

impl LogBuffer {
    pub fn new(max_entries: usize) -> Self {
        Self {
            entries: Vec::with_capacity(max_entries),
            max_entries,
            dropped_count: 0,
        }
    }

    pub fn add_entry(&mut self, entry: LogEntry) {
        if self.entries.len() >= self.max_entries {
            self.entries.remove(0);
            self.dropped_count += 1;
        }
        self.entries.push(entry);
    }

    pub fn get_entries(&self) -> &[LogEntry] {
        &self.entries
    }

    pub fn get_filtered_entries(
        &self,
        level: LogLevel,
        category: Option<LogCategory>,
    ) -> Vec<&LogEntry> {
        self.entries
            .iter()
            .filter(|entry| {
                entry.level <= level && (category.is_none() || category == Some(entry.category))
            })
            .collect()
    }

    pub fn clear(&mut self) {
        self.entries.clear();
        self.dropped_count = 0;
    }

    pub fn dropped_count(&self) -> usize {
        self.dropped_count
    }
}

/// Advanced logging configuration
#[derive(Debug, Clone)]
pub struct LogConfig {
    pub min_level: LogLevel,
    pub destinations: Vec<LogDestination>,
    pub category_filters: BTreeMap<LogCategory, LogLevel>,
    pub buffer_size: usize,
    pub enable_consciousness_integration: bool,
    pub enable_performance_tracking: bool,
    pub enable_structured_logging: bool,
}

impl Default for LogConfig {
    fn default() -> Self {
        Self {
            min_level: LogLevel::Info,
            destinations: vec![LogDestination::Serial, LogDestination::Memory],
            category_filters: BTreeMap::new(),
            buffer_size: 10000,
            enable_consciousness_integration: true,
            enable_performance_tracking: true,
            enable_structured_logging: true,
        }
    }
}

/// Main advanced logging system
pub struct AdvancedLogger {
    config: LogConfig,
    memory_buffer: LogBuffer,
    serial_port: Option<uart_16550::SerialPort>,
    entry_counter: u64,
    performance_metrics: BTreeMap<String, LogPerformanceMetrics>,
    initialized: bool,
}

#[derive(Debug, Clone)]
pub struct LogPerformanceMetrics {
    pub total_logs: u64,
    pub logs_per_second: f64,
    pub average_processing_time_us: f64,
    pub last_update: u64,
}

impl AdvancedLogger {
    pub fn new() -> Self {
        Self {
            config: LogConfig::default(),
            memory_buffer: LogBuffer::new(10000),
            serial_port: None,
            entry_counter: 0,
            performance_metrics: BTreeMap::new(),
            initialized: false,
        }
    }

    /// Initialize the advanced logging system
    pub fn initialize(&mut self, config: LogConfig) -> Result<(), &'static str> {
        self.config = config;

        // Initialize serial port if needed
        if self.config.destinations.contains(&LogDestination::Serial) {
            let mut serial = unsafe { uart_16550::SerialPort::new(0x3F8) };
            serial.init();
            self.serial_port = Some(serial);
        }

        // Resize memory buffer if needed
        if self.memory_buffer.max_entries != self.config.buffer_size {
            self.memory_buffer = LogBuffer::new(self.config.buffer_size);
        }

        self.initialized = true;

        // Log initialization
        self.log_internal(
            LogLevel::Info,
            LogCategory::Kernel,
            "advanced_logger",
            "Advanced logging system initialized",
            BTreeMap::new(),
        );

        Ok(())
    }

    /// Log a message with advanced features
    pub fn log(
        &mut self,
        level: LogLevel,
        category: LogCategory,
        component: &str,
        message: &str,
        metadata: BTreeMap<String, String>,
    ) {
        if !self.initialized {
            return;
        }

        // Check if we should log this entry
        if !self.should_log(level, category) {
            return;
        }

        self.log_internal(level, category, component, message, metadata);
    }

    fn log_internal(
        &mut self,
        level: LogLevel,
        category: LogCategory,
        component: &str,
        message: &str,
        metadata: BTreeMap<String, String>,
    ) {
        let start_time = self.get_current_time_us();

        self.entry_counter += 1;
        let entry = LogEntry {
            timestamp: self.get_current_time(),
            level,
            category,
            component: component.into(),
            message: message.into(),
            metadata,
            thread_id: None, // TODO: Implement thread ID tracking
            cpu_id: None,    // TODO: Implement CPU ID tracking
        };

        // Add to memory buffer
        if self.config.destinations.contains(&LogDestination::Memory) {
            self.memory_buffer.add_entry(entry.clone());
        }

        // Output to serial
        if self.config.destinations.contains(&LogDestination::Serial) {
            self.output_to_serial(&entry);
        }

        // Integrate with consciousness monitoring
        if self.config.enable_consciousness_integration {
            self.update_consciousness_monitoring(&entry);
        }

        // Update performance metrics
        if self.config.enable_performance_tracking {
            let processing_time = self.get_current_time_us() - start_time;
            self.update_performance_metrics(component, processing_time);
        }
    }

    fn should_log(&self, level: LogLevel, category: LogCategory) -> bool {
        // Check global minimum level
        if level > self.config.min_level {
            return false;
        }

        // Check category-specific filters
        if let Some(&category_level) = self.config.category_filters.get(&category) {
            if level > category_level {
                return false;
            }
        }

        true
    }

    fn output_to_serial(&mut self, entry: &LogEntry) {
        // Use the global serial port instead of the instance variable
        let level_str = match entry.level {
            LogLevel::Emergency => "EMERG",
            LogLevel::Alert => "ALERT",
            LogLevel::Critical => "CRIT",
            LogLevel::Error => "ERROR",
            LogLevel::Warning => "WARN",
            LogLevel::Notice => "NOTICE",
            LogLevel::Info => "INFO",
            LogLevel::Debug => "DEBUG",
            LogLevel::Trace => "TRACE",
        };

        let category_str = format!("{:?}", entry.category);

        // Structured log format
        if self.config.enable_structured_logging {
            let mut serial = SERIAL_PORT.lock();
            write!(
                serial,
                "[{}] [{}] [{}] [{}] {}\n",
                entry.timestamp, level_str, category_str, entry.component, entry.message
            )
            .ok();
        } else {
            // Simple format
            let mut serial = SERIAL_PORT.lock();
            write!(
                serial,
                "{}: [{}] {}\n",
                level_str, entry.component, entry.message
            )
            .ok();
        }
    }

    fn update_consciousness_monitoring(&self, entry: &LogEntry) {
        let consciousness_event_type = match entry.category {
            LogCategory::Security => ConsciousnessEventType::SecurityEvent,
            LogCategory::Performance => ConsciousnessEventType::PerformanceAlert,
            LogCategory::AI | LogCategory::Consciousness => ConsciousnessEventType::LearningEvent,
            _ => ConsciousnessEventType::SystemIntegration,
        };

        let severity = match entry.level {
            LogLevel::Emergency | LogLevel::Alert | LogLevel::Critical => EventSeverity::Critical,
            LogLevel::Error => EventSeverity::Error,
            LogLevel::Warning => EventSeverity::Warning,
            _ => EventSeverity::Info,
        };

        log_consciousness_event(
            consciousness_event_type,
            &entry.component,
            severity,
            &entry.message,
        );
    }

    fn update_performance_metrics(&mut self, component: &str, processing_time_us: u64) {
        let current_time = self.get_current_time();
        let metrics = self
            .performance_metrics
            .entry(component.into())
            .or_insert_with(|| LogPerformanceMetrics {
                total_logs: 0,
                logs_per_second: 0.0,
                average_processing_time_us: 0.0,
                last_update: current_time,
            });

        metrics.total_logs += 1;

        // Update average processing time
        metrics.average_processing_time_us =
            (metrics.average_processing_time_us + processing_time_us as f64) / 2.0;

        // Calculate logs per second (simplified)
        let time_diff = current_time - metrics.last_update;
        if time_diff > 0 {
            metrics.logs_per_second = 1000.0 / time_diff as f64; // Assuming timestamp is in ms
        }

        metrics.last_update = current_time;
    }

    /// Get recent log entries
    pub fn get_recent_logs(
        &self,
        count: usize,
        level: Option<LogLevel>,
        category: Option<LogCategory>,
    ) -> Vec<&LogEntry> {
        let entries = if let Some(level) = level {
            self.memory_buffer.get_filtered_entries(level, category)
        } else {
            self.memory_buffer.get_entries().iter().collect()
        };

        let start = if entries.len() > count {
            entries.len() - count
        } else {
            0
        };
        entries[start..].to_vec()
    }

    /// Get performance metrics for a component
    pub fn get_performance_metrics(&self, component: &str) -> Option<&LogPerformanceMetrics> {
        self.performance_metrics.get(component)
    }

    /// Get all performance metrics
    pub fn get_all_performance_metrics(&self) -> &BTreeMap<String, LogPerformanceMetrics> {
        &self.performance_metrics
    }

    /// Clear log buffer
    pub fn clear_logs(&mut self) {
        self.memory_buffer.clear();
    }

    /// Update logging configuration
    pub fn update_config(&mut self, config: LogConfig) {
        self.config = config;
    }

    fn get_current_time(&self) -> u64 {
        // TODO: Implement actual timestamp
        0
    }

    fn get_current_time_us(&self) -> u64 {
        // TODO: Implement actual microsecond timestamp
        0
    }
}

// Global advanced logger instance
lazy_static! {
    pub static ref ADVANCED_LOGGER: Mutex<AdvancedLogger> = Mutex::new(AdvancedLogger::new());
}

// Global serial port for logging output
lazy_static! {
    pub static ref SERIAL_PORT: Mutex<SerialPort> = {
        let mut serial_port = unsafe { SerialPort::new(0x3F8) };
        serial_port.init();
        Mutex::new(serial_port)
    };
}

/// Initialize advanced logging
pub fn init_advanced_logging(config: LogConfig) -> Result<(), &'static str> {
    ADVANCED_LOGGER.lock().initialize(config)
}

/// Log a message with the advanced logging system
pub fn log_advanced(level: LogLevel, category: LogCategory, component: &str, message: &str) {
    ADVANCED_LOGGER
        .lock()
        .log(level, category, component, message, BTreeMap::new());
}

/// Log a message with metadata
pub fn log_advanced_with_metadata(
    level: LogLevel,
    category: LogCategory,
    component: &str,
    message: &str,
    metadata: BTreeMap<String, String>,
) {
    ADVANCED_LOGGER
        .lock()
        .log(level, category, component, message, metadata);
}

/// Convenience macros for different log levels
#[macro_export]
macro_rules! log_emergency {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Emergency,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_alert {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Alert,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_critical {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Critical,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_error {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Error,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_warning {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Warning,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_info {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Info,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_debug {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Debug,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

#[macro_export]
macro_rules! log_trace {
    ($category:expr, $component:expr, $($arg:tt)*) => {
        $crate::advanced_logger::log_advanced(
            $crate::advanced_logger::LogLevel::Trace,
            $category,
            $component,
            &alloc::format!($($arg)*),
        )
    };
}

/// Get recent logs
pub fn get_recent_logs(count: usize) -> Vec<LogEntry> {
    ADVANCED_LOGGER
        .lock()
        .get_recent_logs(count, None, None)
        .into_iter()
        .cloned()
        .collect()
}

/// Get performance metrics
pub fn get_logging_performance_metrics() -> BTreeMap<String, LogPerformanceMetrics> {
    ADVANCED_LOGGER.lock().get_all_performance_metrics().clone()
}
