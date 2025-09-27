//! Memory Management Module
//!
//! Handles memory management, paging, allocations, and memory protection with
//! consciousness integration for optimal memory usage and security.
//! 
//! This module implements Phase 4.3 memory integration with quantum consciousness
//! for enhanced security and optimization capabilities.

pub mod paging;
pub mod heap;
pub mod consciousness;
pub mod guard;
pub mod allocator;
pub mod frame;
#[cfg(test)]
mod tests;

use core::sync::atomic::{AtomicUsize, Ordering};
use bootloader::bootinfo::{MemoryMap, MemoryRegionType};
use bootloader::BootInfo;
use x86_64::{VirtAddr, PhysAddr};
use spin::Mutex;
use crate::println;
use crate::security;

/// Memory tracking
static TOTAL_MEMORY: AtomicUsize = AtomicUsize::new(0);
static USED_MEMORY: AtomicUsize = AtomicUsize::new(0);
static MEMORY_INITIALIZED: AtomicBool = AtomicBool::new(false);

/// Initialize the memory subsystem
pub fn init(boot_info: &'static BootInfo) {
    println!("Initializing memory subsystem...");
    
    // Calculate total available memory
    let memory_map = &boot_info.memory_map;
    let total_mem = calculate_total_memory(memory_map);
    TOTAL_MEMORY.store(total_mem, Ordering::SeqCst);
    
    // Set up page tables
    paging::init(boot_info);
    
    // Initialize heap allocator
    heap::init(boot_info);
    
    // Initialize memory allocator
    allocator::init();
    
    // Set up consciousness-enhanced memory optimization
    consciousness::init();
    
    // Initialize memory protection
    guard::init();
    
    // Set memory as initialized
    MEMORY_INITIALIZED.store(true, Ordering::SeqCst);
    
    println!("Memory initialization complete ({} MB total)", total_mem / 1024 / 1024);
}

/// Calculate total available memory
fn calculate_total_memory(memory_map: &MemoryMap) -> usize {
    memory_map
        .iter()
        .filter(|region| region.region_type == MemoryRegionType::Usable)
        .map(|region| region.range.end_addr() - region.range.start_addr())
        .sum::<u64>() as usize
}

/// Get memory status information
pub fn get_status() -> MemoryStatus {
    let total = TOTAL_MEMORY.load(Ordering::SeqCst);
    let used = USED_MEMORY.load(Ordering::SeqCst);
    let free = total.saturating_sub(used);
    
    MemoryStatus {
        total_memory: total,
        used_memory: used,
        free_memory: free,
        heap_stats: heap::get_heap_stats(),
        optimization_stats: consciousness::get_optimization_stats(),
        fragmentation_ratio: calculate_fragmentation_ratio(),
    }
}

/// Calculate memory fragmentation ratio (0.0-1.0)
fn calculate_fragmentation_ratio() -> f32 {
    // Implementation would calculate actual fragmentation
    // For now, return a simulated value based on heap stats
    let heap_stats = heap::get_heap_stats();
    let fragmentation_base = (heap_stats.used_bytes as f32) / (heap_stats.total_bytes as f32);
    (fragmentation_base * 0.3) + 0.1 // Simple simulation between 0.1-0.4
}

/// Update used memory counter (called by allocator)
pub fn update_used_memory(delta: isize) {
    if delta > 0 {
        USED_MEMORY.fetch_add(delta as usize, Ordering::SeqCst);
    } else {
        USED_MEMORY.fetch_sub(delta.abs() as usize, Ordering::SeqCst);
    }
}

/// Consciousness-aware memory allocation
pub fn consciousness_alloc(size: usize) -> Option<*mut u8> {
    allocator::consciousness_alloc(size)
}

/// Security-verified memory allocation
pub fn secure_alloc(size: usize, security_level: security::SecurityLevel) -> Option<*mut u8> {
    // Verify with security subsystem before allocation
    if !security::verify_memory_allocation(size, security_level) {
        return None;
    }
    
    allocator::secure_alloc(size, security_level)
}

/// Check if a memory region is accessible
pub fn validate_memory_access(addr: VirtAddr, size: usize, security_level: security::SecurityLevel) -> bool {
    // Check with paging and security modules
    let page_check = paging::is_region_mapped(addr, size);
    let guard_check = guard::check_access(addr.as_u64() as usize, size);
    let security_check = security::verify_memory_access(addr.as_u64() as usize, size, security_level);
    
    page_check && guard_check && security_check
}

/// Memory status information
pub struct MemoryStatus {
    /// Total physical memory in bytes
    pub total_memory: usize,
    /// Used physical memory in bytes
    pub used_memory: usize,
    /// Free physical memory in bytes
    pub free_memory: usize,
    /// Heap usage statistics
    pub heap_stats: heap::HeapStats,
    /// Memory optimization statistics
    pub optimization_stats: consciousness::OptimizationStats,
    /// Memory fragmentation ratio (0.0-1.0)
    pub fragmentation_ratio: f32,
}

/// Check if memory management is initialized
pub fn is_initialized() -> bool {
    MEMORY_INITIALIZED.load(Ordering::SeqCst)
}

// Required for the MEMORY_INITIALIZED static
use core::sync::atomic::AtomicBool;
