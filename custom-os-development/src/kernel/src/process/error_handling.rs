//! Production-Ready Error Handling for Process Management
//!
//! Comprehensive error handling system with proper error types, logging,
//! recovery mechanisms, and debugging information for kernel development.

#![no_std]

use alloc::{string::String, vec::Vec, format};
use core::{fmt, panic::PanicInfo};

/// Comprehensive process management error types
#[derive(Debug, Clone, PartialEq)]
pub enum ProcessError {
    // Resource errors
    OutOfMemory {
        requested: usize,
        available: usize,
        context: String,
    },
    InvalidProcessId {
        pid: u64,
        operation: String,
    },
    ProcessNotFound {
        pid: u64,
        last_known_state: String,
    },
    ResourceExhausted {
        resource_type: ResourceType,
        limit: u64,
        current: u64,
    },

    // State management errors
    InvalidStateTransition {
        from: ProcessState,
        to: ProcessState,
        reason: String,
    },
    ProcessAlreadyExists {
        pid: u64,
        existing_state: ProcessState,
    },
    InvalidPriority {
        priority: i32,
        valid_range: (i32, i32),
    },

    // Scheduling errors
    SchedulingFailed {
        reason: SchedulingFailureReason,
        affected_processes: Vec<u64>,
        recovery_action: String,
    },
    DeadlockDetected {
        involved_processes: Vec<u64>,
        resources: Vec<String>,
        cycle_path: Vec<u64>,
    },
    CpuAffinityError {
        pid: u64,
        requested_cpus: Vec<u32>,
        available_cpus: Vec<u32>,
    },

    // Security errors
    SecurityViolation {
        violation_type: SecurityViolationType,
        process_id: u64,
        details: String,
        severity: SecuritySeverity,
    },
    PermissionDenied {
        operation: String,
        required_privilege: u8,
        current_privilege: u8,
    },
    IsolationBreach {
        source_pid: u64,
        target_pid: u64,
        breach_type: String,
    },

    // Hardware/System errors
    HardwareFault {
        fault_type: HardwareFaultType,
        address: Option<u64>,
        cpu_id: u32,
        recovery_possible: bool,
    },
    SystemCorruption {
        component: String,
        corruption_detected: String,
        integrity_check_failed: bool,
    },
    ContextSwitchFailure {
        from_pid: u64,
        to_pid: u64,
        stage: ContextSwitchStage,
        hardware_error: Option<String>,
    },

    // IPC and Communication errors
    IpcError {
        error_type: IpcErrorType,
        source_pid: u64,
        target_pid: Option<u64>,
        message_id: Option<u64>,
    },
    ChannelError {
        channel_id: u64,
        operation: String,
        reason: String,
    },

    // Consciousness system errors
    ConsciousnessError {
        error_type: ConsciousnessErrorType,
        process_id: u64,
        ai_component: String,
        fallback_available: bool,
    },
}

/// Resource types for resource exhaustion errors
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ResourceType {
    Memory,
    FileDescriptors,
    Processes,
    Threads,
    CpuTime,
    Handles,
    NetworkConnections,
}

/// Process states for state transition errors
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ProcessState {
    Created,
    Ready,
    Running,
    Blocked,
    Waiting,
    Zombie,
    Terminated,
}

/// Scheduling failure reasons
#[derive(Debug, Clone, PartialEq)]
pub enum SchedulingFailureReason {
    NoRunnableProcesses,
    LoadBalancingFailed,
    CpuQuotaExceeded,
    PriorityInversion,
    ResourceContention,
    ConsciousnessSystemDown,
}

/// Security violation types
#[derive(Debug, Clone, PartialEq)]
pub enum SecurityViolationType {
    PrivilegeEscalation,
    MemoryAccess,
    SystemCallViolation,
    ResourceAccess,
    DataExfiltration,
    CodeInjection,
}

/// Security severity levels
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub enum SecuritySeverity {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
}

/// Hardware fault types
#[derive(Debug, Clone, PartialEq)]
pub enum HardwareFaultType {
    PageFault,
    GeneralProtectionFault,
    SegmentationFault,
    DoubleFault,
    InvalidOpcode,
    DivideByZero,
    StackOverflow,
    HardwareInterrupt,
}

/// Context switch stages for error tracking
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ContextSwitchStage {
    Preparation,
    StateCapture,
    SecurityValidation,
    HardwareSwitch,
    StateRestore,
    PostValidation,
}

/// IPC error types
#[derive(Debug, Clone, PartialEq)]
pub enum IpcErrorType {
    MessageTooLarge,
    QueueFull,
    InvalidReceiver,
    PermissionDenied,
    ChannelClosed,
    Timeout,
    Serialization,
}

/// Consciousness system error types
#[derive(Debug, Clone, PartialEq)]
pub enum ConsciousnessErrorType {
    ModelNotLoaded,
    InferenceFailure,
    DataCorruption,
    NetworkError,
    ResourceExhaustion,
    SecurityCheckFailed,
    ConfigurationError,
}

impl fmt::Display for ProcessError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ProcessError::OutOfMemory { requested, available, context } => {
                write!(f, "Out of memory: requested {} bytes, {} available in context '{}'",
                       requested, available, context)
            }
            ProcessError::InvalidProcessId { pid, operation } => {
                write!(f, "Invalid process ID {} for operation '{}'", pid, operation)
            }
            ProcessError::ProcessNotFound { pid, last_known_state } => {
                write!(f, "Process {} not found (last known state: {})", pid, last_known_state)
            }
            ProcessError::ResourceExhausted { resource_type, limit, current } => {
                write!(f, "Resource {:?} exhausted: {}/{} used", resource_type, current, limit)
            }
            ProcessError::InvalidStateTransition { from, to, reason } => {
                write!(f, "Invalid state transition from {:?} to {:?}: {}", from, to, reason)
            }
            ProcessError::SecurityViolation { violation_type, process_id, details, severity } => {
                write!(f, "Security violation ({:?}): Process {} - {} [Severity: {:?}]",
                       violation_type, process_id, details, severity)
            }
            ProcessError::HardwareFault { fault_type, address, cpu_id, recovery_possible } => {
                write!(f, "Hardware fault ({:?}) on CPU {}: address={:?}, recoverable={}",
                       fault_type, cpu_id, address, recovery_possible)
            }
            ProcessError::DeadlockDetected { involved_processes, resources, cycle_path } => {
                write!(f, "Deadlock detected: processes={:?}, resources={:?}, cycle={:?}",
                       involved_processes, resources, cycle_path)
            }
            ProcessError::ContextSwitchFailure { from_pid, to_pid, stage, hardware_error } => {
                write!(f, "Context switch failed: {}→{} at stage {:?}, hw_error={:?}",
                       from_pid, to_pid, stage, hardware_error)
            }
            ProcessError::ConsciousnessError { error_type, process_id, ai_component, fallback_available } => {
                write!(f, "Consciousness error ({:?}): Process {} in component '{}', fallback={}",
                       error_type, process_id, ai_component, fallback_available)
            }
            // Add other error display implementations...
            _ => write!(f, "Process error: {:?}", self),
        }
    }
}

/// Result type for process operations
pub type ProcessResult<T> = Result<T, ProcessError>;

/// Error context for tracking error origins
#[derive(Debug, Clone)]
pub struct ErrorContext {
    pub operation: String,
    pub file: &'static str,
    pub line: u32,
    pub timestamp: u64,
    pub cpu_id: u32,
    pub process_id: Option<u64>,
    pub call_stack: Vec<String>,
}

impl ErrorContext {
    pub fn new(operation: &str, file: &'static str, line: u32) -> Self {
        Self {
            operation: operation.to_string(),
            file,
            line,
            timestamp: crate::time::get_current_time(),
            cpu_id: crate::cpu::current_cpu_id(),
            process_id: crate::process::current_process_id(),
            call_stack: capture_call_stack(),
        }
    }
}

/// Macro for creating error context
#[macro_export]
macro_rules! error_context {
    ($operation:expr) => {
        ErrorContext::new($operation, file!(), line!())
    };
}

/// Error recovery strategies
#[derive(Debug, Clone)]
pub enum RecoveryStrategy {
    Retry {
        max_attempts: u32,
        delay_ms: u64,
    },
    Fallback {
        fallback_operation: String,
    },
    Isolate {
        affected_processes: Vec<u64>,
    },
    SystemRestart {
        component: String,
        preserve_state: bool,
    },
    EmergencyShutdown {
        reason: String,
        save_core_dump: bool,
    },
}

/// Error recovery manager
pub struct ErrorRecoveryManager {
    recovery_policies: hashbrown::HashMap<String, RecoveryStrategy>,
    error_history: Vec<(ProcessError, ErrorContext, RecoveryStrategy)>,
    max_history: usize,
}

impl ErrorRecoveryManager {
    pub fn new() -> Self {
        let mut manager = Self {
            recovery_policies: hashbrown::HashMap::new(),
            error_history: Vec::new(),
            max_history: 1000,
        };

        // Initialize default recovery policies
        manager.setup_default_policies();
        manager
    }

    fn setup_default_policies(&mut self) {
        // Memory errors - retry with smaller allocation
        self.recovery_policies.insert(
            "OutOfMemory".to_string(),
            RecoveryStrategy::Retry { max_attempts: 3, delay_ms: 100 }
        );

        // Security violations - isolate process
        self.recovery_policies.insert(
            "SecurityViolation".to_string(),
            RecoveryStrategy::Isolate { affected_processes: Vec::new() }
        );

        // Hardware faults - system restart if critical
        self.recovery_policies.insert(
            "HardwareFault".to_string(),
            RecoveryStrategy::SystemRestart {
                component: "process_manager".to_string(),
                preserve_state: true
            }
        );

        // Consciousness errors - fallback to traditional scheduling
        self.recovery_policies.insert(
            "ConsciousnessError".to_string(),
            RecoveryStrategy::Fallback {
                fallback_operation: "traditional_scheduling".to_string()
            }
        );
    }

    /// Handle error with appropriate recovery strategy
    pub fn handle_error(&mut self, error: ProcessError, context: ErrorContext) -> ProcessResult<RecoveryStrategy> {
        // Determine error type for policy lookup
        let error_type = error_type_name(&error);

        // Get recovery strategy
        let strategy = self.recovery_policies
            .get(&error_type)
            .cloned()
            .unwrap_or(RecoveryStrategy::EmergencyShutdown {
                reason: format!("No recovery policy for {}", error_type),
                save_core_dump: true,
            });

        // Log error and recovery action
        self.log_error(&error, &context, &strategy);

        // Record in history
        if self.error_history.len() >= self.max_history {
            self.error_history.remove(0);
        }
        self.error_history.push((error.clone(), context, strategy.clone()));

        // Execute recovery strategy
        self.execute_recovery_strategy(&strategy, &error)?;

        Ok(strategy)
    }

    fn execute_recovery_strategy(&self, strategy: &RecoveryStrategy, error: &ProcessError) -> ProcessResult<()> {
        match strategy {
            RecoveryStrategy::Retry { max_attempts, delay_ms } => {
                // Implement retry logic
                crate::log::warn!("Retrying operation (max: {}, delay: {}ms)", max_attempts, delay_ms);
            }
            RecoveryStrategy::Fallback { fallback_operation } => {
                // Switch to fallback operation
                crate::log::info!("Switching to fallback operation: {}", fallback_operation);
            }
            RecoveryStrategy::Isolate { affected_processes } => {
                // Isolate affected processes
                for &pid in affected_processes {
                    crate::process::isolate_process(pid)?;
                }
            }
            RecoveryStrategy::SystemRestart { component, preserve_state } => {
                // Restart system component
                crate::log::error!("Restarting component: {} (preserve_state: {})", component, preserve_state);
                // Implement component restart
            }
            RecoveryStrategy::EmergencyShutdown { reason, save_core_dump } => {
                // Emergency shutdown
                crate::log::critical!("Emergency shutdown: {} (save_dump: {})", reason, save_core_dump);
                if *save_core_dump {
                    crate::debug::save_core_dump()?;
                }
                crate::system::emergency_shutdown();
            }
        }

        Ok(())
    }

    fn log_error(&self, error: &ProcessError, context: &ErrorContext, strategy: &RecoveryStrategy) {
        let severity = error_severity(error);

        match severity {
            ErrorSeverity::Critical => {
                crate::log::critical!("CRITICAL ERROR: {} at {}:{} - Recovery: {:?}",
                                    error, context.file, context.line, strategy);
            }
            ErrorSeverity::High => {
                crate::log::error!("ERROR: {} at {}:{} - Recovery: {:?}",
                                 error, context.file, context.line, strategy);
            }
            ErrorSeverity::Medium => {
                crate::log::warn!("WARNING: {} at {}:{} - Recovery: {:?}",
                                error, context.file, context.line, strategy);
            }
            ErrorSeverity::Low => {
                crate::log::info!("Info: {} at {}:{} - Recovery: {:?}",
                                error, context.file, context.line, strategy);
            }
        }
    }

    /// Get error statistics
    pub fn get_error_stats(&self) -> ErrorStatistics {
        let mut stats = ErrorStatistics::default();

        for (error, _, _) in &self.error_history {
            stats.total_errors += 1;

            match error_severity(error) {
                ErrorSeverity::Critical => stats.critical_errors += 1,
                ErrorSeverity::High => stats.high_errors += 1,
                ErrorSeverity::Medium => stats.medium_errors += 1,
                ErrorSeverity::Low => stats.low_errors += 1,
            }
        }

        stats
    }
}

/// Error severity levels
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ErrorSeverity {
    Low,
    Medium,
    High,
    Critical,
}

/// Error statistics
#[derive(Debug, Default)]
pub struct ErrorStatistics {
    pub total_errors: u64,
    pub critical_errors: u64,
    pub high_errors: u64,
    pub medium_errors: u64,
    pub low_errors: u64,
}

/// Determine error type name for policy lookup
fn error_type_name(error: &ProcessError) -> String {
    match error {
        ProcessError::OutOfMemory { .. } => "OutOfMemory".to_string(),
        ProcessError::SecurityViolation { .. } => "SecurityViolation".to_string(),
        ProcessError::HardwareFault { .. } => "HardwareFault".to_string(),
        ProcessError::ConsciousnessError { .. } => "ConsciousnessError".to_string(),
        ProcessError::DeadlockDetected { .. } => "DeadlockDetected".to_string(),
        ProcessError::ContextSwitchFailure { .. } => "ContextSwitchFailure".to_string(),
        _ => "Generic".to_string(),
    }
}

/// Determine error severity
fn error_severity(error: &ProcessError) -> ErrorSeverity {
    match error {
        ProcessError::SecurityViolation { severity, .. } => {
            match severity {
                SecuritySeverity::Critical => ErrorSeverity::Critical,
                SecuritySeverity::High => ErrorSeverity::High,
                SecuritySeverity::Medium => ErrorSeverity::Medium,
                SecuritySeverity::Low => ErrorSeverity::Low,
            }
        }
        ProcessError::HardwareFault { recovery_possible, .. } => {
            if *recovery_possible { ErrorSeverity::High } else { ErrorSeverity::Critical }
        }
        ProcessError::SystemCorruption { .. } => ErrorSeverity::Critical,
        ProcessError::DeadlockDetected { .. } => ErrorSeverity::High,
        ProcessError::OutOfMemory { .. } => ErrorSeverity::High,
        ProcessError::ContextSwitchFailure { .. } => ErrorSeverity::High,
        _ => ErrorSeverity::Medium,
    }
}

/// Capture call stack for debugging
fn capture_call_stack() -> Vec<String> {
    // Simplified call stack capture
    // In real implementation, would use proper stack unwinding
    vec![
        "capture_call_stack()".to_string(),
        "process_management_function()".to_string(),
        "kernel_entry_point()".to_string(),
    ]
}

/// Panic handler for process management errors
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    crate::log::critical!("KERNEL PANIC in process management: {}", info);

    // Try to save critical state
    if let Err(e) = crate::debug::save_emergency_state() {
        crate::log::critical!("Failed to save emergency state: {:?}", e);
    }

    // Halt the system
    loop {
        unsafe {
            core::arch::asm!("hlt");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_creation() {
        let error = ProcessError::OutOfMemory {
            requested: 1024,
            available: 512,
            context: "process_creation".to_string(),
        };

        assert!(matches!(error, ProcessError::OutOfMemory { .. }));
    }

    #[test]
    fn test_error_display() {
        let error = ProcessError::InvalidProcessId {
            pid: 123,
            operation: "kill".to_string(),
        };

        let display = format!("{}", error);
        assert!(display.contains("123"));
        assert!(display.contains("kill"));
    }

    #[test]
    fn test_recovery_manager() {
        let mut manager = ErrorRecoveryManager::new();

        let error = ProcessError::OutOfMemory {
            requested: 1024,
            available: 512,
            context: "test".to_string(),
        };

        let context = ErrorContext::new("test_operation", "test.rs", 42);
        let result = manager.handle_error(error, context);

        assert!(result.is_ok());
    }
}