use alloc::vec::Vec;
use core::fmt;

#[derive(Debug, Clone)]
pub struct InterruptSecurity {
    pub handler_id: u32,
    pub security_level: SecurityLevel,
    pub enabled: bool,
}

#[derive(Debug, Clone)]
pub enum SecurityLevel {
    Low,
    Medium,
    High,
    Critical,
}

impl InterruptSecurity {
    pub fn new(handler_id: u32, level: SecurityLevel) -> Self {
        Self {
            handler_id,
            security_level: level,
            enabled: true,
        }
    }
    
    pub fn validate_interrupt(&self, _interrupt_vector: u8) -> bool {
        // Basic interrupt validation
        self.enabled
    }
    
    pub fn enable(&mut self) {
        self.enabled = true;
    }
    
    pub fn disable(&mut self) {
        self.enabled = false;
    }
}

impl Default for InterruptSecurity {
    fn default() -> Self {
        Self::new(0, SecurityLevel::Medium)
    }
}

impl fmt::Display for SecurityLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SecurityLevel::Low => write!(f, "Low"),
            SecurityLevel::Medium => write!(f, "Medium"),
            SecurityLevel::High => write!(f, "High"),
            SecurityLevel::Critical => write!(f, "Critical"),
        }
    }
}
