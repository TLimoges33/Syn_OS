//! Safe Global State Management for Process System
//!
//! Replaces unsafe static mut globals with proper synchronization primitives
//! for production-ready kernel development.

#![no_std]

use alloc::boxed::Box;
use core::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use spin::{RwLock, Mutex, Once};
use super::{ProcessManager, scheduler::Scheduler};

/// Process system errors
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ProcessSystemError {
    NotInitialized,
    AlreadyInitialized,
    LockContention,
    InvalidOperation,
}

/// Safe global scheduler instance with proper synchronization
static SCHEDULER_INIT: Once = Once::new();
static SCHEDULER: RwLock<Option<Box<Scheduler>>> = RwLock::new(None);

/// Safe global process manager with proper synchronization
static PROCESS_MANAGER_INIT: Once = Once::new();
static PROCESS_MANAGER: RwLock<Option<Box<ProcessManager>>> = RwLock::new(None);

/// System initialization state
static SYSTEM_INITIALIZED: AtomicBool = AtomicBool::new(false);
static SYSTEM_UPTIME: AtomicU64 = AtomicU64::new(0);

/// Initialize the process management system safely
pub fn initialize_process_system() -> Result<(), ProcessSystemError> {
    if SYSTEM_INITIALIZED.load(Ordering::Acquire) {
        return Err(ProcessSystemError::AlreadyInitialized);
    }

    // Initialize scheduler with Once for thread safety
    SCHEDULER_INIT.call_once(|| {
        let scheduler = Box::new(Scheduler::new());
        *SCHEDULER.write() = Some(scheduler);
    });

    // Initialize process manager with Once for thread safety
    PROCESS_MANAGER_INIT.call_once(|| {
        let process_manager = Box::new(ProcessManager::new());
        *PROCESS_MANAGER.write() = Some(process_manager);
    });

    // Mark system as initialized
    SYSTEM_INITIALIZED.store(true, Ordering::Release);

    Ok(())
}

/// Safe access to global scheduler
pub fn with_scheduler<F, R>(f: F) -> Result<R, ProcessSystemError>
where
    F: FnOnce(&mut Scheduler) -> R,
{
    if !SYSTEM_INITIALIZED.load(Ordering::Acquire) {
        return Err(ProcessSystemError::NotInitialized);
    }

    let mut scheduler_guard = SCHEDULER.write();
    match scheduler_guard.as_mut() {
        Some(scheduler) => Ok(f(scheduler)),
        None => Err(ProcessSystemError::NotInitialized),
    }
}

/// Safe read-only access to global scheduler
pub fn with_scheduler_read<F, R>(f: F) -> Result<R, ProcessSystemError>
where
    F: FnOnce(&Scheduler) -> R,
{
    if !SYSTEM_INITIALIZED.load(Ordering::Acquire) {
        return Err(ProcessSystemError::NotInitialized);
    }

    let scheduler_guard = SCHEDULER.read();
    match scheduler_guard.as_ref() {
        Some(scheduler) => Ok(f(scheduler)),
        None => Err(ProcessSystemError::NotInitialized),
    }
}

/// Safe access to global process manager
pub fn with_process_manager<F, R>(f: F) -> Result<R, ProcessSystemError>
where
    F: FnOnce(&mut ProcessManager) -> R,
{
    if !SYSTEM_INITIALIZED.load(Ordering::Acquire) {
        return Err(ProcessSystemError::NotInitialized);
    }

    let mut manager_guard = PROCESS_MANAGER.write();
    match manager_guard.as_mut() {
        Some(manager) => Ok(f(manager)),
        None => Err(ProcessSystemError::NotInitialized),
    }
}

/// Safe read-only access to global process manager
pub fn with_process_manager_read<F, R>(f: F) -> Result<R, ProcessSystemError>
where
    F: FnOnce(&ProcessManager) -> R,
{
    if !SYSTEM_INITIALIZED.load(Ordering::Acquire) {
        return Err(ProcessSystemError::NotInitialized);
    }

    let manager_guard = PROCESS_MANAGER.read();
    match manager_guard.as_ref() {
        Some(manager) => Ok(f(manager)),
        None => Err(ProcessSystemError::NotInitialized),
    }
}

/// Get system uptime in ticks (thread-safe)
pub fn get_system_uptime() -> u64 {
    SYSTEM_UPTIME.load(Ordering::Relaxed)
}

/// Increment system uptime (called by timer interrupt)
pub fn increment_system_uptime() {
    SYSTEM_UPTIME.fetch_add(1, Ordering::Relaxed);
}

/// Check if process system is initialized
pub fn is_system_initialized() -> bool {
    SYSTEM_INITIALIZED.load(Ordering::Acquire)
}

/// Shutdown the process system safely
pub fn shutdown_process_system() -> Result<(), ProcessSystemError> {
    if !SYSTEM_INITIALIZED.load(Ordering::Acquire) {
        return Err(ProcessSystemError::NotInitialized);
    }

    // Clear scheduler
    {
        let mut scheduler_guard = SCHEDULER.write();
        *scheduler_guard = None;
    }

    // Clear process manager
    {
        let mut manager_guard = PROCESS_MANAGER.write();
        *manager_guard = None;
    }

    // Mark as shutdown
    SYSTEM_INITIALIZED.store(false, Ordering::Release);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_safe_initialization() {
        assert!(!is_system_initialized());

        initialize_process_system().expect("Should initialize successfully");
        assert!(is_system_initialized());

        // Second initialization should fail
        assert_eq!(
            initialize_process_system().unwrap_err(),
            ProcessSystemError::AlreadyInitialized
        );
    }

    #[test]
    fn test_safe_scheduler_access() {
        initialize_process_system().expect("Should initialize");

        let result = with_scheduler_read(|scheduler| {
            // Safe read access to scheduler
            true
        });

        assert!(result.is_ok());
    }

    #[test]
    fn test_uptime_tracking() {
        let initial = get_system_uptime();
        increment_system_uptime();
        assert_eq!(get_system_uptime(), initial + 1);
    }
}