//! Kernel Memory Management
//!
//! Comprehensive memory management system including physical memory,
//! virtual memory, heap allocation, and memory protection.

pub mod allocator;
pub mod physical;
pub mod virtual_memory;
pub mod manager;
pub mod init;
pub mod educational_memory_manager;

use crate::println;

// Re-export main components
pub use allocator::BumpAllocator;
pub use physical::{Frame, FrameAllocator, BitmapFrameAllocator};
pub use virtual_memory::{VirtualAddress, init_page_fault_handler};
pub use manager::{MemoryManager, init_global_memory_manager, get_global_memory_manager, get_global_memory_manager_mut};
pub use init::{MemoryConfig, init_memory_system, test_memory_system};

/// Initialize the memory management system
pub fn init() {
    println!("🧠 Starting SynOS memory management initialization...");
    
    // Use default configuration for now
    let config = MemoryConfig::default();
    
    match init_memory_system(config) {
        Ok(()) => {
            crate::println!("✅ Memory management system initialized successfully");
            
            // Run basic tests
            if let Err(_e) = test_memory_system() {
                crate::println!("⚠️  Memory system tests failed: {}", _e);
            }
        }
        Err(e) => {
            panic!("Failed to initialize memory management system: {}", e);
        }
    }
}

/// Memory layout constants for SynOS
pub mod layout {
    /// Kernel heap start address
    pub const HEAP_START: usize = 0xFFFF_8000_0000_0000;
    
    /// Kernel heap size (1 MB initially)
    pub const HEAP_SIZE: usize = 1024 * 1024;
    
    /// User space start address
    pub const USER_SPACE_START: usize = 0x0000_0000_0040_0000;
    
    /// User space end address
    pub const USER_SPACE_END: usize = 0x0000_7FFF_FFFF_F000;
    
    /// Kernel space start address
    pub const KERNEL_SPACE_START: usize = 0xFFFF_8000_0000_0000;
    
    /// Physical memory identity mapping start
    pub const PHYS_MEM_OFFSET: usize = 0xFFFF_8800_0000_0000;
}

/// Global memory statistics
pub struct MemoryStats {
    pub total_memory: usize,
    pub used_memory: usize,
    pub free_memory: usize,
    pub heap_usage: usize,
    pub page_tables: usize,
}

impl MemoryStats {
    /// Create new memory statistics
    pub fn new() -> Self {
        MemoryStats {
            total_memory: 0,
            used_memory: 0,
            free_memory: 0,
            heap_usage: 0,
            page_tables: 0,
        }
    }

    /// Update memory statistics
    pub fn update(&mut self, total: usize, used: usize) {
        self.total_memory = total;
        self.used_memory = used;
        self.free_memory = total - used;
    }

    /// Get memory usage percentage
    pub fn usage_percent(&self) -> u8 {
        if self.total_memory == 0 {
            0
        } else {
            ((self.used_memory * 100) / self.total_memory) as u8
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memory_stats() {
        let mut stats = MemoryStats::new();
        stats.update(1024, 512);
        assert_eq!(stats.usage_percent(), 50);
    }
}
