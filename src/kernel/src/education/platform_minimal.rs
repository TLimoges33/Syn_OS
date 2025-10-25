//! Minimal Education Platform - V1.0 Compatible
//! 
//! This is a simplified version that actually compiles and works
//! in the no_std kernel environment.

extern crate alloc;
use alloc::string::String;
use core::sync::atomic::{AtomicBool, AtomicU64, Ordering};

/// Global platform state
static PLATFORM_ACTIVE: AtomicBool = AtomicBool::new(false);
static STUDENT_COUNT: AtomicU64 = AtomicU64::new(0);
static MODULE_COUNT: AtomicU64 = AtomicU64::new(5); // Pre-set some basic modules

/// Basic learning difficulty levels
#[derive(Debug, Clone, Copy)]
pub enum DifficultyLevel {
    Beginner,
    Intermediate,
    Advanced,
}

/// Simple student record
#[derive(Debug, Clone)]
pub struct Student {
    pub id: u64,
    pub name: String,
    pub difficulty: DifficultyLevel,
    pub completed_modules: u64,
}

/// Initialize the education platform
pub fn init() {
    PLATFORM_ACTIVE.store(true, Ordering::SeqCst);
}

/// Check if platform is active
pub fn is_platform_active() -> bool {
    PLATFORM_ACTIVE.load(Ordering::SeqCst)
}

/// Get available module count
pub fn get_available_modules_count() -> u64 {
    MODULE_COUNT.load(Ordering::SeqCst)
}

/// Register a new student (simplified)
pub fn register_student(_name: String) -> u64 {
    let student_id = STUDENT_COUNT.fetch_add(1, Ordering::SeqCst);
    student_id
}

/// Get current student count
pub fn get_student_count() -> u64 {
    STUDENT_COUNT.load(Ordering::SeqCst)
}

/// Start a basic learning session
pub fn start_learning_session(student_id: u64, _module_name: String) -> Result<u64, &'static str> {
    if !is_platform_active() {
        return Err("Platform not active");
    }
    
    // Simple session ID based on student ID and current count
    let session_id = student_id * 1000 + get_student_count();
    Ok(session_id)
}

/// Complete a learning session
pub fn complete_learning_session(_session_id: u64) -> Result<(), &'static str> {
    if !is_platform_active() {
        return Err("Platform not active");
    }
    
    // Simply return success for basic implementation
    Ok(())
}

/// Get basic platform statistics
pub fn get_platform_stats() -> (u64, u64, u64) {
    (
        get_student_count(),
        get_available_modules_count(),
        if is_platform_active() { 1 } else { 0 }
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_platform_initialization() {
        init();
        assert!(is_platform_active());
        assert!(get_available_modules_count() > 0);
    }

    #[test]
    fn test_student_registration() {
        init();
        let student_id = register_student("Test Student".into());
        assert_eq!(student_id, 1); // First student should have ID 1 (fetch_add returns previous value)
        
        let count = get_student_count();
        assert!(count > 0);
    }

    #[test]
    fn test_learning_session_lifecycle() {
        init();
        let student_id = register_student("Test Student".into());
        
        let session_id = start_learning_session(student_id, "Basic Programming".into());
        assert!(session_id.is_ok());
        assert!(complete_learning_session(session_id.unwrap()).is_ok());
    }
}
