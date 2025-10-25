//! Time management for the SynOS kernel
//! 
//! This module provides timing functionality including:
//! - System time tracking
//! - Timestamps
//! - Timer management

#![no_std]

use core::sync::atomic::{AtomicU64, Ordering};

/// Global system time counter in nanoseconds
static SYSTEM_TIME_NS: AtomicU64 = AtomicU64::new(0);

/// Initialize the time management system
pub fn init() {
    // Initialize timing subsystem
    SYSTEM_TIME_NS.store(0, Ordering::SeqCst);

    // Initialize Programmable Interval Timer (PIT)
    init_pit();

    // TODO: Initialize APIC timer if available for better precision
}

/// Initialize the Programmable Interval Timer (PIT)
fn init_pit() {
    use x86_64::instructions::port::Port;

    // PIT operates at 1.193182 MHz base frequency
    const PIT_FREQUENCY: u32 = 1193182;
    const TARGET_FREQUENCY: u32 = 1000; // 1kHz = 1ms intervals

    // Calculate divisor for desired frequency
    let divisor = (PIT_FREQUENCY / TARGET_FREQUENCY) as u16;

    // Send command byte: Channel 0, lobyte/hibyte, rate generator
    let mut command_port = Port::<u8>::new(0x43);
    unsafe { command_port.write(0x36) };

    // Send frequency divisor
    let mut data_port = Port::<u8>::new(0x40);
    unsafe {
        data_port.write((divisor & 0xFF) as u8); // Low byte
        data_port.write((divisor >> 8) as u8);    // High byte
    }
}

/// Get the current system time in nanoseconds since system boot
pub fn get_current_time() -> u64 {
    SYSTEM_TIME_NS.load(Ordering::SeqCst)
}

/// Update the system time (called from timer interrupt handler)
pub fn update_time(delta_ns: u64) {
    SYSTEM_TIME_NS.fetch_add(delta_ns, Ordering::SeqCst);
}

/// Get time in milliseconds
pub fn get_time_ms() -> u64 {
    get_current_time() / 1_000_000
}

/// Get time in seconds
pub fn get_time_seconds() -> u64 {
    get_current_time() / 1_000_000_000
}

/// A timestamp structure for tracking time
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Timestamp {
    pub nanoseconds: u64,
}

impl Timestamp {
    /// Create a new timestamp with the current time
    pub fn now() -> Self {
        Self {
            nanoseconds: get_current_time(),
        }
    }
    
    /// Create a timestamp from nanoseconds
    pub fn from_ns(nanoseconds: u64) -> Self {
        Self { nanoseconds }
    }
    
    /// Get elapsed time since this timestamp
    pub fn elapsed(&self) -> u64 {
        get_current_time().saturating_sub(self.nanoseconds)
    }
    
    /// Get elapsed time in milliseconds
    pub fn elapsed_ms(&self) -> u64 {
        self.elapsed() / 1_000_000
    }
}

/// Sleep for a specified number of milliseconds
/// Note: This is a busy-wait implementation and should be improved with proper timer interrupts
pub fn sleep_ms(milliseconds: u64) {
    let start_time = get_current_time();
    let target_time = start_time + (milliseconds * 1_000_000);
    
    while get_current_time() < target_time {
        // Busy wait - should be replaced with proper scheduling
        core::hint::spin_loop();
    }
}

/// Timer configuration
pub struct TimerConfig {
    pub frequency_hz: u32,
    pub enabled: bool,
}

impl Default for TimerConfig {
    fn default() -> Self {
        Self {
            frequency_hz: 1000, // 1kHz default
            enabled: true,
        }
    }
}

/// Initialize timer with specific configuration
pub fn init_with_config(config: TimerConfig) {
    init();

    if config.enabled {
        // Configure PIT with custom frequency if different from default
        if config.frequency_hz != 1000 {
            configure_pit_frequency(config.frequency_hz);
        }
        // Timer interrupts will be enabled via IDT setup in interrupts module
    }
}

/// Configure PIT with a specific frequency
fn configure_pit_frequency(frequency_hz: u32) {
    use x86_64::instructions::port::Port;

    const PIT_FREQUENCY: u32 = 1193182;
    let divisor = (PIT_FREQUENCY / frequency_hz).min(65535) as u16;

    let mut command_port = Port::<u8>::new(0x43);
    unsafe { command_port.write(0x36) };

    let mut data_port = Port::<u8>::new(0x40);
    unsafe {
        data_port.write((divisor & 0xFF) as u8);
        data_port.write((divisor >> 8) as u8);
    }
}

/// Timer interrupt handler - called from IDT timer interrupt
pub fn timer_tick() {
    // Update system time by 1ms (assuming 1kHz PIT frequency)
    update_time(1_000_000); // 1ms = 1,000,000 nanoseconds
}
