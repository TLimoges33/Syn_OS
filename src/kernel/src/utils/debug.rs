//! Debug utilities for the SynOS kernel
//! 
//! This module provides debugging functionality including:
//! - Core dump generation
//! - Debug logging
//! - Emergency state saving

#![no_std]

use alloc::vec::Vec;
use alloc::string::String;
use core::fmt::Write;

/// Debug error types
#[derive(Debug, Clone)]
pub enum DebugError {
    IoError(&'static str),
    InsufficientMemory,
    InvalidState,
}

impl core::fmt::Display for DebugError {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        match self {
            DebugError::IoError(msg) => write!(f, "IO Error: {}", msg),
            DebugError::InsufficientMemory => write!(f, "Insufficient memory for debug operation"),
            DebugError::InvalidState => write!(f, "Invalid system state for debug operation"),
        }
    }
}

/// Core dump information
#[derive(Debug, Clone)]
pub struct CoreDump {
    pub timestamp: u64,
    pub cpu_state: crate::cpu::CpuState,
    pub memory_usage: u64,
    pub process_count: u32,
    pub debug_info: String,
}

impl CoreDump {
    pub fn new() -> Self {
        Self {
            timestamp: crate::time::get_current_time(),
            cpu_state: crate::cpu::get_cpu_state(),
            memory_usage: 0, // TODO: Get actual memory usage
            process_count: 0, // TODO: Get actual process count
            debug_info: String::new(),
        }
    }
}

/// Save a core dump to memory/storage
pub fn save_core_dump() -> Result<(), DebugError> {
    let core_dump = CoreDump::new();
    
    // TODO: Implement actual core dump saving to storage
    // For now, just log the core dump information
    crate::println!("Core dump saved at timestamp: {}", core_dump.timestamp);
    crate::println!("CPU ID: {}, Usage: {}%", 
        core_dump.cpu_state.id, core_dump.cpu_state.usage_percent);
    
    Ok(())
}

/// Emergency state information
#[derive(Debug, Clone)]
pub struct EmergencyState {
    pub timestamp: u64,
    pub error_code: u32,
    pub cpu_registers: Vec<u64>,
    pub stack_trace: Vec<u64>,
    pub memory_map: Vec<(u64, u64)>, // (address, size) pairs
}

impl EmergencyState {
    pub fn capture() -> Self {
        Self {
            timestamp: crate::time::get_current_time(),
            error_code: 0xDEADBEEF,
            cpu_registers: Vec::new(), // TODO: Capture actual register state
            stack_trace: Vec::new(),   // TODO: Capture actual stack trace
            memory_map: Vec::new(),    // TODO: Capture actual memory map
        }
    }
}

/// Save emergency system state
pub fn save_emergency_state() -> Result<(), DebugError> {
    let emergency_state = EmergencyState::capture();
    
    crate::println!("Emergency state saved at: {}", emergency_state.timestamp);
    crate::println!("Error code: 0x{:X}", emergency_state.error_code);
    
    Ok(())
}

/// Debug log entry
#[derive(Debug, Clone)]
pub struct DebugLogEntry {
    pub timestamp: u64,
    pub level: DebugLevel,
    pub module: &'static str,
    pub message: String,
}

#[derive(Debug, Clone, Copy)]
pub enum DebugLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
    Critical,
}

impl core::fmt::Display for DebugLevel {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        match self {
            DebugLevel::Trace => write!(f, "TRACE"),
            DebugLevel::Debug => write!(f, "DEBUG"),
            DebugLevel::Info => write!(f, "INFO"),
            DebugLevel::Warn => write!(f, "WARN"),
            DebugLevel::Error => write!(f, "ERROR"),
            DebugLevel::Critical => write!(f, "CRITICAL"),
        }
    }
}

/// Debug logger
pub struct DebugLogger;

impl DebugLogger {
    pub fn log(level: DebugLevel, module: &'static str, message: &str) {
        let timestamp = crate::time::get_current_time();
        crate::println!("[{}] [{:>8}] [{}] {}", 
            timestamp, level, module, message);
    }
}

/// Macro for debug logging
#[macro_export]
macro_rules! debug_log {
    ($level:expr, $module:expr, $($arg:tt)*) => {
        $crate::debug::DebugLogger::log($level, $module, &format!($($arg)*));
    };
}

/// Initialize debug subsystem
pub fn init() {
    DebugLogger::log(DebugLevel::Info, "debug", "Debug subsystem initialized");
}

/// Print system state for debugging
pub fn print_system_state() {
    let cpu_state = crate::cpu::get_cpu_state();
    let current_time = crate::time::get_current_time();
    
    crate::println!("=== System State Debug ===");
    crate::println!("Time: {} ns", current_time);
    crate::println!("CPU ID: {}", cpu_state.id);
    crate::println!("CPU Usage: {}%", cpu_state.usage_percent);
    crate::println!("CPU Temp: {}°C", cpu_state.temperature_celsius);
    crate::println!("CPU Freq: {} MHz", cpu_state.frequency_mhz);
    crate::println!("========================");
}

/// Breakpoint for debugging
#[inline]
pub fn breakpoint() {
    unsafe {
        core::arch::asm!("int3");
    }
}
