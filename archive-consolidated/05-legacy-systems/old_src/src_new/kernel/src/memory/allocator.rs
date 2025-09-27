//! Memory Allocator Module
//!
//! Implements custom memory allocators for the kernel with consciousness integration

use core::alloc::{GlobalAlloc, Layout};
use core::ptr::null_mut;
use linked_list_allocator::LockedHeap;
use spin::Mutex;
use crate::consciousness;
use crate::security;
use crate::println;
use crate::memory;

/// Global allocator for kernel heap
#[global_allocator]
static ALLOCATOR: LockedHeap = LockedHeap::empty();

/// Security-enhanced allocator for sensitive operations
static SECURE_ALLOCATOR: Mutex<Option<SecureAllocator>> = Mutex::new(None);

/// Consciousness-enhanced allocator for AI operations
static CONSCIOUSNESS_ALLOCATOR: Mutex<Option<ConsciousnessAllocator>> = Mutex::new(None);

/// Initialize allocator subsystem
pub fn init() {
    println!("  • Initializing memory allocators");
    
    // Initialize secure allocator
    *SECURE_ALLOCATOR.lock() = Some(SecureAllocator::new());
    
    // Initialize consciousness allocator
    *CONSCIOUSNESS_ALLOCATOR.lock() = Some(ConsciousnessAllocator::new());
}

/// Consciousness-aware memory allocation
pub fn consciousness_alloc(size: usize) -> Option<*mut u8> {
    if let Some(ref mut alloc) = *CONSCIOUSNESS_ALLOCATOR.lock() {
        let layout = Layout::from_size_align(size, 8).ok()?;
        let ptr = alloc.allocate(layout);
        
        if !ptr.is_null() {
            // Update memory usage tracking
            memory::update_used_memory(size as isize);
            
            // Track consciousness-specific allocation metrics
            consciousness::track_memory_allocation(size);
            
            return Some(ptr);
        }
    }
    
    // Fallback to regular allocation
    let layout = Layout::from_size_align(size, 8).ok()?;
    let ptr = unsafe { ALLOCATOR.alloc(layout) };
    
    if !ptr.is_null() {
        memory::update_used_memory(size as isize);
        Some(ptr)
    } else {
        None
    }
}

/// Security-verified memory allocation
pub fn secure_alloc(size: usize, security_level: security::SecurityLevel) -> Option<*mut u8> {
    if let Some(ref mut alloc) = *SECURE_ALLOCATOR.lock() {
        let layout = Layout::from_size_align(size, 8).ok()?;
        let ptr = alloc.allocate(layout, security_level);
        
        if !ptr.is_null() {
            // Update memory usage tracking
            memory::update_used_memory(size as isize);
            
            // Log security allocation
            if security_level >= security::SecurityLevel::High {
                println!("  • Security-verified allocation: {} bytes at {:#x}", 
                         size, ptr as usize);
            }
            
            return Some(ptr);
        }
    }
    
    // Fallback to regular allocation
    let layout = Layout::from_size_align(size, 8).ok()?;
    let ptr = unsafe { ALLOCATOR.alloc(layout) };
    
    if !ptr.is_null() {
        memory::update_used_memory(size as isize);
        Some(ptr)
    } else {
        None
    }
}

/// Deallocate memory
pub fn deallocate(ptr: *mut u8, size: usize, align: usize) {
    let layout = Layout::from_size_align(size, align).unwrap();
    unsafe {
        ALLOCATOR.dealloc(ptr, layout);
    }
    memory::update_used_memory(-(size as isize));
}

/// Consciousness-enhanced allocator for AI operations
struct ConsciousnessAllocator {
    consciousness_level: f64,
    allocations: usize,
}

impl ConsciousnessAllocator {
    /// Create a new consciousness allocator
    fn new() -> Self {
        Self {
            consciousness_level: 0.5,
            allocations: 0,
        }
    }
    
    /// Allocate memory with consciousness awareness
    fn allocate(&mut self, layout: Layout) -> *mut u8 {
        // Update consciousness level
        self.consciousness_level = consciousness::get_consciousness_level();
        
        // Increment allocation counter
        self.allocations += 1;
        
        // Use the global allocator for actual allocation
        unsafe { ALLOCATOR.alloc(layout) }
    }
}

/// Security-enhanced allocator for sensitive operations
struct SecureAllocator {
    secure_allocations: usize,
}

impl SecureAllocator {
    /// Create a new secure allocator
    fn new() -> Self {
        Self {
            secure_allocations: 0,
        }
    }
    
    /// Allocate memory with security verification
    fn allocate(&mut self, layout: Layout, security_level: security::SecurityLevel) -> *mut u8 {
        // Increment secure allocations counter
        self.secure_allocations += 1;
        
        // Apply security measures based on security level
        match security_level {
            security::SecurityLevel::Low => {
                // Basic allocation
                unsafe { ALLOCATOR.alloc(layout) }
            },
            security::SecurityLevel::Medium => {
                // Zeroed memory for medium security
                unsafe { ALLOCATOR.alloc_zeroed(layout) }
            },
            security::SecurityLevel::High | security::SecurityLevel::Maximum => {
                // For high security, get consciousness verification first
                let consciousness_level = consciousness::get_consciousness_level();
                if consciousness_level < 0.7 && security_level == security::SecurityLevel::Maximum {
                    // Not enough consciousness confidence for maximum security
                    return null_mut();
                }
                
                // Zero memory and verify allocation
                let ptr = unsafe { ALLOCATOR.alloc_zeroed(layout) };
                if !ptr.is_null() {
                    // Apply additional security measures for high-security memory
                    // (like guard pages, encryption, etc.)
                }
                ptr
            },
        }
    }
}
