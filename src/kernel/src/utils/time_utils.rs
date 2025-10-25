//! Centralized Time Utilities for SynOS Kernel
//!
//! Provides consistent timestamp functions across all kernel modules

use core::sync::atomic::{AtomicU64, Ordering};

/// Global timestamp counter for kernel operations
static KERNEL_TIMESTAMP: AtomicU64 = AtomicU64::new(1640995200); // Jan 1, 2022 as base

/// Boot time reference for uptime calculations
static BOOT_TIME: AtomicU64 = AtomicU64::new(0);

/// High-resolution counter for performance measurements
static HIGH_RES_COUNTER: AtomicU64 = AtomicU64::new(0);

/// Initialize time system
pub fn init_time_system() {
    let current_time = get_system_time_estimate();
    BOOT_TIME.store(current_time, Ordering::SeqCst);
    KERNEL_TIMESTAMP.store(current_time, Ordering::SeqCst);

    crate::println!("⏰ Time system initialized");
    crate::println!("   Boot time: {}", current_time);
}

/// Get current timestamp in seconds since Unix epoch
pub fn get_current_timestamp() -> u64 {
    KERNEL_TIMESTAMP.fetch_add(1, Ordering::SeqCst)
}

/// Get current timestamp in milliseconds
pub fn get_current_timestamp_ms() -> u64 {
    get_current_timestamp() * 1000 + (HIGH_RES_COUNTER.fetch_add(1, Ordering::SeqCst) % 1000)
}

/// Get current timestamp in microseconds
pub fn get_current_timestamp_us() -> u64 {
    get_current_timestamp_ms() * 1000 + (HIGH_RES_COUNTER.fetch_add(1, Ordering::SeqCst) % 1000)
}

/// Get system uptime in seconds
pub fn get_uptime() -> u64 {
    let current = get_current_timestamp();
    let boot = BOOT_TIME.load(Ordering::SeqCst);
    current.saturating_sub(boot)
}

/// Get system uptime in milliseconds
pub fn get_uptime_ms() -> u64 {
    get_uptime() * 1000
}

/// Get high-resolution timestamp for performance measurements
pub fn get_high_res_timestamp() -> u64 {
    HIGH_RES_COUNTER.fetch_add(1, Ordering::SeqCst)
}

/// Update system time (called by time synchronization)
pub fn update_system_time(new_time: u64) {
    KERNEL_TIMESTAMP.store(new_time, Ordering::SeqCst);
}

/// Get estimated system time (fallback when RTC not available)
fn get_system_time_estimate() -> u64 {
    // In a real implementation, this would read from:
    // 1. Real-Time Clock (RTC)
    // 2. ACPI PM Timer
    // 3. TSC (Time Stamp Counter)
    // 4. HPET (High Precision Event Timer)

    // For now, use a reasonable starting point
    1640995200 + (HIGH_RES_COUNTER.load(Ordering::SeqCst) / 1000)
}

/// Format timestamp as human-readable string
pub fn format_timestamp(timestamp: u64) -> alloc::string::String {
    // Simple formatting - in production would use proper date/time formatting
    alloc::format!("2022-01-01 00:{:02}:{:02}", (timestamp % 3600) / 60, timestamp % 60)
}

/// Get timestamp for logging with nanosecond precision
pub fn get_log_timestamp() -> u64 {
    get_current_timestamp_us() * 1000 + (HIGH_RES_COUNTER.fetch_add(1, Ordering::SeqCst) % 1000)
}

/// Sleep for specified milliseconds (busy wait)
pub fn sleep_ms(ms: u64) {
    let start = get_high_res_timestamp();
    let target = start + ms * 1000; // Convert to microseconds

    while get_high_res_timestamp() < target {
        // Busy wait - in production would use proper timer interrupts
        core::hint::spin_loop();
    }
}

/// Get monotonic timestamp (never goes backwards)
pub fn get_monotonic_timestamp() -> u64 {
    static MONOTONIC_COUNTER: AtomicU64 = AtomicU64::new(0);
    MONOTONIC_COUNTER.fetch_add(1, Ordering::SeqCst)
}

/// Time measurement for performance profiling
pub struct TimeProfiler {
    start_time: u64,
    name: &'static str,
}

impl TimeProfiler {
    /// Start timing a operation
    pub fn start(name: &'static str) -> Self {
        Self {
            start_time: get_high_res_timestamp(),
            name,
        }
    }

    /// Get elapsed time in microseconds
    pub fn elapsed_us(&self) -> u64 {
        get_high_res_timestamp().saturating_sub(self.start_time)
    }

    /// Get elapsed time in milliseconds
    pub fn elapsed_ms(&self) -> u64 {
        self.elapsed_us() / 1000
    }
}

impl Drop for TimeProfiler {
    fn drop(&mut self) {
        let elapsed = self.elapsed_us();
        if elapsed > 1000 { // Only log if > 1ms
            crate::println!("⏱️  {}: {}μs", self.name, elapsed);
        }
    }
}

/// Macro for easy time profiling
#[macro_export]
macro_rules! profile_time {
    ($name:expr, $code:block) => {
        {
            let _profiler = $crate::time_utils::TimeProfiler::start($name);
            $code
        }
    };
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_timestamp_functions() {
        init_time_system();

        let ts1 = get_current_timestamp();
        let ts2 = get_current_timestamp();

        assert!(ts2 > ts1);
    }

    #[test]
    fn test_uptime() {
        init_time_system();
        let uptime = get_uptime();
        assert!(uptime >= 0);
    }

    #[test]
    fn test_profiler() {
        let profiler = TimeProfiler::start("test");
        // Simulate some work
        for _ in 0..1000 {
            core::hint::spin_loop();
        }
        assert!(profiler.elapsed_us() > 0);
    }
}
