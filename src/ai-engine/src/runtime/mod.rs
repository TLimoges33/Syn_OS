//! AI Runtime Module
//!
//! Manages AI model execution, task scheduling, and performance monitoring
//! across multiple AI frameworks with hardware acceleration support.

pub mod engine; // Core runtime engine (moved from runtime.rs)
pub mod executor; // Task execution engine
pub mod monitor;
pub mod scheduler; // Task scheduling system // Performance monitoring

// Re-export main components
pub use engine::AIRuntime;
pub use executor::TaskExecutor;
pub use monitor::RuntimeMonitor;
pub use scheduler::{Task, TaskId, TaskPriority, TaskScheduler, TaskType};

/// Runtime configuration
#[derive(Debug, Clone)]
pub struct RuntimeConfig {
    pub max_concurrent_tasks: usize,
    pub memory_limit_mb: usize,
    pub enable_gpu: bool,
    pub enable_monitoring: bool,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            max_concurrent_tasks: 4,
            memory_limit_mb: 1024,
            enable_gpu: true,
            enable_monitoring: true,
        }
    }
}

/// Runtime metrics for monitoring
#[derive(Debug, Default, Clone)]
pub struct RuntimeMetrics {
    pub active_tasks: usize,
    pub completed_tasks: u64,
    pub failed_tasks: u64,
    pub memory_usage_mb: usize,
    pub cpu_usage_percent: f32,
    pub gpu_usage_percent: f32,
}

/// Runtime state
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum RuntimeState {
    Uninitialized,
    Initializing,
    Running,
    Paused,
    Stopping,
    Stopped,
    Error,
}

/// Initialize the runtime module
pub fn init() -> anyhow::Result<()> {
    tracing::info!("Initializing AI Runtime Module");
    Ok(())
}
