//! CPU management and identification
//! 
//! This module provides CPU-related functionality including:
//! - CPU identification
//! - Core management
//! - CPU feature detection

#![no_std]

use core::sync::atomic::{AtomicU32, Ordering};

/// Current CPU ID counter
static CURRENT_CPU: AtomicU32 = AtomicU32::new(0);

/// Initialize CPU management
pub fn init() {
    // Initialize CPU subsystem
    CURRENT_CPU.store(0, Ordering::SeqCst);
}

/// Get the current CPU ID
pub fn current_cpu_id() -> u32 {
    // In a single-core system, this is always 0
    // In multicore, this would read from APIC or similar
    CURRENT_CPU.load(Ordering::SeqCst)
}

/// Set the current CPU ID (used during SMP initialization)
pub fn set_current_cpu_id(cpu_id: u32) {
    CURRENT_CPU.store(cpu_id, Ordering::SeqCst);
}

/// Get the number of available CPU cores
pub fn cpu_count() -> u32 {
    // TODO: Implement proper CPU detection via ACPI/MP tables
    1 // Default to single core for now
}

/// CPU feature flags
#[derive(Debug, Clone, Copy)]
pub struct CpuFeatures {
    pub has_sse: bool,
    pub has_sse2: bool,
    pub has_avx: bool,
    pub has_avx2: bool,
    pub has_rdrand: bool,
    pub has_rdseed: bool,
}

impl Default for CpuFeatures {
    fn default() -> Self {
        Self {
            has_sse: false,
            has_sse2: false,
            has_avx: false,
            has_avx2: false,
            has_rdrand: false,
            has_rdseed: false,
        }
    }
}

/// Get CPU features
pub fn get_cpu_features() -> CpuFeatures {
    // TODO: Implement CPUID-based feature detection
    CpuFeatures::default()
}

/// CPU state information
#[derive(Debug, Clone)]
pub struct CpuState {
    pub id: u32,
    pub usage_percent: u32,
    pub temperature_celsius: u32,
    pub frequency_mhz: u32,
}

impl CpuState {
    pub fn current() -> Self {
        Self {
            id: current_cpu_id(),
            usage_percent: 0, // TODO: Implement CPU usage tracking
            temperature_celsius: 50, // Placeholder
            frequency_mhz: 2400, // Placeholder
        }
    }
}

/// Get current CPU state
pub fn get_cpu_state() -> CpuState {
    CpuState::current()
}

/// Halt the current CPU core
pub fn halt() {
    unsafe {
        x86_64::instructions::hlt();
    }
}

/// Disable interrupts on current CPU
pub fn disable_interrupts() {
    x86_64::instructions::interrupts::disable();
}

/// Enable interrupts on current CPU
pub fn enable_interrupts() {
    x86_64::instructions::interrupts::enable();
}

/// Check if interrupts are enabled
pub fn interrupts_enabled() -> bool {
    x86_64::instructions::interrupts::are_enabled()
}

/// Execute a closure with interrupts disabled
pub fn without_interrupts<F, R>(f: F) -> R
where
    F: FnOnce() -> R,
{
    x86_64::instructions::interrupts::without_interrupts(f)
}
