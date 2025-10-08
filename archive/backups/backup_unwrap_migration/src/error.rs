/// SynOS Kernel Error Types
///
/// Comprehensive error handling for all kernel subsystems.
/// Replaces unwrap() calls with proper Result-based error propagation.

use core::fmt;

/// Kernel-wide Result type
pub type KernelResult<T> = Result<T, KernelError>;

/// Comprehensive kernel error types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KernelError {
    // ===== Memory Management Errors =====
    /// Memory allocation failed (out of memory)
    OutOfMemory,
    /// Invalid memory address
    InvalidAddress(usize),
    /// Memory region not mapped
    NotMapped,
    /// Memory region already mapped
    AlreadyMapped,
    /// Page fault occurred
    PageFault(usize),
    /// Invalid page size
    InvalidPageSize,
    /// Frame allocation failed
    FrameAllocationFailed,

    // ===== Process Management Errors =====
    /// Process not found
    ProcessNotFound(u64),
    /// Invalid process ID
    InvalidProcessId,
    /// Process already exists
    ProcessAlreadyExists(u64),
    /// Maximum processes reached
    TooManyProcesses,
    /// Process creation failed
    ProcessCreationFailed,
    /// Scheduler error
    SchedulerError,
    /// Context switch failed
    ContextSwitchFailed,

    // ===== File System Errors =====
    /// File not found
    FileNotFound,
    /// Directory not found
    DirectoryNotFound,
    /// Invalid path
    InvalidPath,
    /// Permission denied
    PermissionDenied,
    /// File already exists
    FileAlreadyExists,
    /// Disk full
    DiskFull,
    /// I/O error
    IoError,
    /// Invalid file descriptor
    InvalidFileDescriptor,

    // ===== Network Errors =====
    /// Network device not found
    NetworkDeviceNotFound,
    /// Invalid network address
    InvalidNetworkAddress,
    /// Connection refused
    ConnectionRefused,
    /// Connection timeout
    ConnectionTimeout,
    /// Network unreachable
    NetworkUnreachable,
    /// Invalid packet
    InvalidPacket,
    /// Socket error
    SocketError,
    /// TCP state error
    TcpStateError,

    // ===== IPC Errors =====
    /// Message queue full
    MessageQueueFull,
    /// Message queue empty
    MessageQueueEmpty,
    /// Invalid IPC channel
    InvalidChannel,
    /// Shared memory error
    SharedMemoryError,
    /// Semaphore error
    SemaphoreError,
    /// Pipe error
    PipeError,
    /// Deadlock detected
    DeadlockDetected,

    // ===== Device Driver Errors =====
    /// Device not found
    DeviceNotFound,
    /// Device already in use
    DeviceInUse,
    /// Device not ready
    DeviceNotReady,
    /// Invalid device operation
    InvalidDeviceOperation,
    /// DMA error
    DmaError,
    /// Interrupt error
    InterruptError,

    // ===== Graphics Errors =====
    /// Graphics initialization failed
    GraphicsInitFailed,
    /// Invalid display mode
    InvalidDisplayMode,
    /// Framebuffer error
    FramebufferError,
    /// Window manager error
    WindowManagerError,

    // ===== AI/Consciousness Errors =====
    /// AI service not available
    AiServiceUnavailable,
    /// Consciousness framework error
    ConsciousnessError,
    /// Pattern recognition failed
    PatternRecognitionFailed,
    /// Decision engine error
    DecisionEngineError,
    /// Inference error
    InferenceError,

    // ===== Security Errors =====
    /// Access denied
    AccessDenied,
    /// Authentication failed
    AuthenticationFailed,
    /// Encryption error
    EncryptionError,
    /// Signature verification failed
    SignatureVerificationFailed,
    /// Security policy violation
    SecurityPolicyViolation,
    /// Threat detected
    ThreatDetected,

    // ===== Container Errors =====
    /// Container not found
    ContainerNotFound,
    /// Invalid namespace
    InvalidNamespace,
    /// Cgroup error
    CgroupError,
    /// Capability error
    CapabilityError,

    // ===== System Errors =====
    /// Invalid parameter
    InvalidParameter,
    /// Not implemented
    NotImplemented,
    /// Operation not supported
    NotSupported,
    /// System call error
    SyscallError,
    /// Timeout occurred
    Timeout,
    /// Resource busy
    ResourceBusy,
    /// Would block (non-blocking operation)
    WouldBlock,
    /// Interrupted
    Interrupted,
    /// Unknown error
    Unknown,
}

impl KernelError {
    /// Get error code (for syscall returns)
    pub fn as_errno(&self) -> i32 {
        match self {
            // Memory errors: -1000 to -1099
            KernelError::OutOfMemory => -1000,
            KernelError::InvalidAddress(_) => -1001,
            KernelError::NotMapped => -1002,
            KernelError::AlreadyMapped => -1003,
            KernelError::PageFault(_) => -1004,
            KernelError::InvalidPageSize => -1005,
            KernelError::FrameAllocationFailed => -1006,

            // Process errors: -2000 to -2099
            KernelError::ProcessNotFound(_) => -2000,
            KernelError::InvalidProcessId => -2001,
            KernelError::ProcessAlreadyExists(_) => -2002,
            KernelError::TooManyProcesses => -2003,
            KernelError::ProcessCreationFailed => -2004,
            KernelError::SchedulerError => -2005,
            KernelError::ContextSwitchFailed => -2006,

            // File system errors: -3000 to -3099
            KernelError::FileNotFound => -3000,
            KernelError::DirectoryNotFound => -3001,
            KernelError::InvalidPath => -3002,
            KernelError::PermissionDenied => -3003,
            KernelError::FileAlreadyExists => -3004,
            KernelError::DiskFull => -3005,
            KernelError::IoError => -3006,
            KernelError::InvalidFileDescriptor => -3007,

            // Network errors: -4000 to -4099
            KernelError::NetworkDeviceNotFound => -4000,
            KernelError::InvalidNetworkAddress => -4001,
            KernelError::ConnectionRefused => -4002,
            KernelError::ConnectionTimeout => -4003,
            KernelError::NetworkUnreachable => -4004,
            KernelError::InvalidPacket => -4005,
            KernelError::SocketError => -4006,
            KernelError::TcpStateError => -4007,

            // IPC errors: -5000 to -5099
            KernelError::MessageQueueFull => -5000,
            KernelError::MessageQueueEmpty => -5001,
            KernelError::InvalidChannel => -5002,
            KernelError::SharedMemoryError => -5003,
            KernelError::SemaphoreError => -5004,
            KernelError::PipeError => -5005,
            KernelError::DeadlockDetected => -5006,

            // Device errors: -6000 to -6099
            KernelError::DeviceNotFound => -6000,
            KernelError::DeviceInUse => -6001,
            KernelError::DeviceNotReady => -6002,
            KernelError::InvalidDeviceOperation => -6003,
            KernelError::DmaError => -6004,
            KernelError::InterruptError => -6005,

            // Graphics errors: -7000 to -7099
            KernelError::GraphicsInitFailed => -7000,
            KernelError::InvalidDisplayMode => -7001,
            KernelError::FramebufferError => -7002,
            KernelError::WindowManagerError => -7003,

            // AI errors: -8000 to -8099
            KernelError::AiServiceUnavailable => -8000,
            KernelError::ConsciousnessError => -8001,
            KernelError::PatternRecognitionFailed => -8002,
            KernelError::DecisionEngineError => -8003,
            KernelError::InferenceError => -8004,

            // Security errors: -9000 to -9099
            KernelError::AccessDenied => -9000,
            KernelError::AuthenticationFailed => -9001,
            KernelError::EncryptionError => -9002,
            KernelError::SignatureVerificationFailed => -9003,
            KernelError::SecurityPolicyViolation => -9004,
            KernelError::ThreatDetected => -9005,

            // Container errors: -10000 to -10099
            KernelError::ContainerNotFound => -10000,
            KernelError::InvalidNamespace => -10001,
            KernelError::CgroupError => -10002,
            KernelError::CapabilityError => -10003,

            // System errors: -100 to -199
            KernelError::InvalidParameter => -100,
            KernelError::NotImplemented => -101,
            KernelError::NotSupported => -102,
            KernelError::SyscallError => -103,
            KernelError::Timeout => -104,
            KernelError::ResourceBusy => -105,
            KernelError::WouldBlock => -106,
            KernelError::Interrupted => -107,
            KernelError::Unknown => -1,
        }
    }

    /// Get human-readable error message
    pub fn message(&self) -> &'static str {
        match self {
            KernelError::OutOfMemory => "Out of memory",
            KernelError::InvalidAddress(_) => "Invalid memory address",
            KernelError::NotMapped => "Memory region not mapped",
            KernelError::AlreadyMapped => "Memory region already mapped",
            KernelError::PageFault(_) => "Page fault",
            KernelError::InvalidPageSize => "Invalid page size",
            KernelError::FrameAllocationFailed => "Frame allocation failed",

            KernelError::ProcessNotFound(_) => "Process not found",
            KernelError::InvalidProcessId => "Invalid process ID",
            KernelError::ProcessAlreadyExists(_) => "Process already exists",
            KernelError::TooManyProcesses => "Maximum processes reached",
            KernelError::ProcessCreationFailed => "Process creation failed",
            KernelError::SchedulerError => "Scheduler error",
            KernelError::ContextSwitchFailed => "Context switch failed",

            KernelError::FileNotFound => "File not found",
            KernelError::DirectoryNotFound => "Directory not found",
            KernelError::InvalidPath => "Invalid path",
            KernelError::PermissionDenied => "Permission denied",
            KernelError::FileAlreadyExists => "File already exists",
            KernelError::DiskFull => "Disk full",
            KernelError::IoError => "I/O error",
            KernelError::InvalidFileDescriptor => "Invalid file descriptor",

            KernelError::NetworkDeviceNotFound => "Network device not found",
            KernelError::InvalidNetworkAddress => "Invalid network address",
            KernelError::ConnectionRefused => "Connection refused",
            KernelError::ConnectionTimeout => "Connection timeout",
            KernelError::NetworkUnreachable => "Network unreachable",
            KernelError::InvalidPacket => "Invalid packet",
            KernelError::SocketError => "Socket error",
            KernelError::TcpStateError => "TCP state error",

            KernelError::MessageQueueFull => "Message queue full",
            KernelError::MessageQueueEmpty => "Message queue empty",
            KernelError::InvalidChannel => "Invalid IPC channel",
            KernelError::SharedMemoryError => "Shared memory error",
            KernelError::SemaphoreError => "Semaphore error",
            KernelError::PipeError => "Pipe error",
            KernelError::DeadlockDetected => "Deadlock detected",

            KernelError::DeviceNotFound => "Device not found",
            KernelError::DeviceInUse => "Device already in use",
            KernelError::DeviceNotReady => "Device not ready",
            KernelError::InvalidDeviceOperation => "Invalid device operation",
            KernelError::DmaError => "DMA error",
            KernelError::InterruptError => "Interrupt error",

            KernelError::GraphicsInitFailed => "Graphics initialization failed",
            KernelError::InvalidDisplayMode => "Invalid display mode",
            KernelError::FramebufferError => "Framebuffer error",
            KernelError::WindowManagerError => "Window manager error",

            KernelError::AiServiceUnavailable => "AI service unavailable",
            KernelError::ConsciousnessError => "Consciousness framework error",
            KernelError::PatternRecognitionFailed => "Pattern recognition failed",
            KernelError::DecisionEngineError => "Decision engine error",
            KernelError::InferenceError => "Inference error",

            KernelError::AccessDenied => "Access denied",
            KernelError::AuthenticationFailed => "Authentication failed",
            KernelError::EncryptionError => "Encryption error",
            KernelError::SignatureVerificationFailed => "Signature verification failed",
            KernelError::SecurityPolicyViolation => "Security policy violation",
            KernelError::ThreatDetected => "Threat detected",

            KernelError::ContainerNotFound => "Container not found",
            KernelError::InvalidNamespace => "Invalid namespace",
            KernelError::CgroupError => "Cgroup error",
            KernelError::CapabilityError => "Capability error",

            KernelError::InvalidParameter => "Invalid parameter",
            KernelError::NotImplemented => "Not implemented",
            KernelError::NotSupported => "Operation not supported",
            KernelError::SyscallError => "System call error",
            KernelError::Timeout => "Operation timed out",
            KernelError::ResourceBusy => "Resource busy",
            KernelError::WouldBlock => "Operation would block",
            KernelError::Interrupted => "Operation interrupted",
            KernelError::Unknown => "Unknown error",
        }
    }
}

impl fmt::Display for KernelError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{} (error code: {})", self.message(), self.as_errno())
    }
}

/// Helper trait for converting Option to KernelResult
pub trait OptionExt<T> {
    /// Convert Option to Result with default error
    fn ok_or_kernel(self, err: KernelError) -> KernelResult<T>;
}

impl<T> OptionExt<T> for Option<T> {
    fn ok_or_kernel(self, err: KernelError) -> KernelResult<T> {
        self.ok_or(err)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_codes() {
        assert_eq!(KernelError::OutOfMemory.as_errno(), -1000);
        assert_eq!(KernelError::ProcessNotFound(42).as_errno(), -2000);
        assert_eq!(KernelError::FileNotFound.as_errno(), -3000);
    }

    #[test]
    fn test_error_messages() {
        assert_eq!(KernelError::OutOfMemory.message(), "Out of memory");
        assert!(KernelError::ProcessNotFound(1).message().contains("Process"));
    }
}
