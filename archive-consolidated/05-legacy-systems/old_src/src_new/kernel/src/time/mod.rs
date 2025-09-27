//! Time Module
//!
//! Provides time-related functionality for the kernel

use core::sync::atomic::{AtomicU64, Ordering};
use x86_64::instructions::rdtsc;
use crate::println;

/// Global time counter (in milliseconds since boot)
static GLOBAL_TIME_MS: AtomicU64 = AtomicU64::new(0);
/// Tick frequency in MHz
static TICK_FREQUENCY_MHZ: AtomicU64 = AtomicU64::new(0);
/// CPU cycles at last calibration
static LAST_CYCLES: AtomicU64 = AtomicU64::new(0);
/// Time at last calibration in milliseconds
static LAST_TIME_MS: AtomicU64 = AtomicU64::new(0);

/// Initialize the time subsystem
pub fn init() {
    println!("  • Initializing time subsystem");
    
    // Reset counters
    GLOBAL_TIME_MS.store(0, Ordering::SeqCst);
    
    // Estimate CPU frequency (would be more accurate in real implementation)
    // For now we'll use a reasonable default of 2000 MHz
    TICK_FREQUENCY_MHZ.store(2000, Ordering::SeqCst);
    
    // Initialize cycle counter
    LAST_CYCLES.store(rdtsc(), Ordering::SeqCst);
    LAST_TIME_MS.store(0, Ordering::SeqCst);
    
    println!("  ✓ Time subsystem initialized");
}

/// Update the system time
pub fn update() {
    // Read current cycle count
    let current_cycles = rdtsc();
    let last_cycles = LAST_CYCLES.load(Ordering::SeqCst);
    let cycles_delta = current_cycles - last_cycles;
    
    // Convert cycles to milliseconds based on frequency
    let freq_mhz = TICK_FREQUENCY_MHZ.load(Ordering::SeqCst);
    let ms_delta = cycles_delta / (freq_mhz * 1000);
    
    if ms_delta > 0 {
        // Update time
        let last_time = LAST_TIME_MS.load(Ordering::SeqCst);
        let new_time = last_time + ms_delta;
        
        GLOBAL_TIME_MS.store(new_time, Ordering::SeqCst);
        LAST_TIME_MS.store(new_time, Ordering::SeqCst);
        LAST_CYCLES.store(current_cycles, Ordering::SeqCst);
    }
}

/// Get the current time in milliseconds since boot
pub fn now_ms() -> u64 {
    // Update time before returning
    update();
    GLOBAL_TIME_MS.load(Ordering::SeqCst)
}

/// Get the current time in seconds since boot
pub fn now_sec() -> u64 {
    now_ms() / 1000
}

/// A point in time
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Instant {
    /// Time in milliseconds
    time_ms: u64,
}

impl Instant {
    /// Get the current time as an instant
    pub fn now() -> Self {
        Self {
            time_ms: now_ms(),
        }
    }
    
    /// Get the elapsed time since this instant in milliseconds
    pub fn elapsed_ms(&self) -> u64 {
        now_ms().saturating_sub(self.time_ms)
    }
    
    /// Get the elapsed time since this instant in seconds
    pub fn elapsed_sec(&self) -> u64 {
        self.elapsed_ms() / 1000
    }
    
    /// Get the elapsed time as seconds with floating point precision
    pub fn as_secs_f32(&self) -> f32 {
        self.elapsed_ms() as f32 / 1000.0
    }
}

impl core::ops::Sub<Instant> for Instant {
    type Output = Duration;
    
    fn sub(self, other: Instant) -> Duration {
        if self.time_ms >= other.time_ms {
            Duration {
                millis: self.time_ms - other.time_ms,
            }
        } else {
            Duration {
                millis: 0,
            }
        }
    }
}

/// A duration of time
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Duration {
    /// Time in milliseconds
    millis: u64,
}

impl Duration {
    /// Create a new duration from milliseconds
    pub fn from_millis(millis: u64) -> Self {
        Self { millis }
    }
    
    /// Create a new duration from seconds
    pub fn from_secs(secs: u64) -> Self {
        Self { millis: secs * 1000 }
    }
    
    /// Get the duration in milliseconds
    pub fn as_millis(&self) -> u64 {
        self.millis
    }
    
    /// Get the duration in seconds
    pub fn as_secs(&self) -> u64 {
        self.millis / 1000
    }
    
    /// Get the duration in seconds as a floating point
    pub fn as_secs_f32(&self) -> f32 {
        self.millis as f32 / 1000.0
    }
}
