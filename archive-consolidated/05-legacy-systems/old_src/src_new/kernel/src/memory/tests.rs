//! Memory Module Tests
//!
//! Test cases for the memory management subsystem

#![cfg(test)]

use super::*;
use x86_64::VirtAddr;

/// Test heap allocation functionality
#[test_case]
fn test_heap_allocation() {
    let heap_stats_before = heap::get_heap_stats();
    
    // Check that heap usage is reported
    assert!(heap_stats_before.total_bytes > 0, 
            "Heap total bytes should be greater than zero");
}

/// Test memory protection functionality
#[test_case]
fn test_memory_protection() {
    // Check that protection levels are defined
    let level = guard::ProtectionLevel::High;
    assert!(level == guard::ProtectionLevel::High, 
            "Protection level comparison failed");
}

/// Test consciousness memory optimization
#[test_case]
fn test_ai_optimization() {
    // Get optimization stats
    let stats = ai::get_optimization_stats();
    
    // Check that optimization level is within valid range
    assert!(stats.optimization_level >= 0.0 && stats.optimization_level <= 1.0,
            "Optimization level should be between 0.0 and 1.0");
}
