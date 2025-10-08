use alloc::vec::Vec;
use core::fmt;

/// Process/Thread identifier type
pub type CpuId = u32;

/// Simple CPU identifier for process scheduling
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Cpu {
    pub id: CpuId,
    pub core_count: u8,
    pub enabled: bool,
}

impl Cpu {
    pub fn new(id: CpuId) -> Self {
        Self {
            id,
            core_count: 1,
            enabled: true,
        }
    }
    
    pub fn current() -> CpuId {
        // Simplified - would normally read from hardware
        0
    }
}

impl Default for Cpu {
    fn default() -> Self {
        Self::new(0)
    }
}

impl fmt::Display for Cpu {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "CPU[id:{}, cores:{}, enabled:{}]", 
               self.id, self.core_count, self.enabled)
    }
}
