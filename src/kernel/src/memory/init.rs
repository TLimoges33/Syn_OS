/// Memory System Initialization for SynOS
/// Comprehensive setup of virtual memory, physical memory, and AI integration

use crate::memory::{
    BitmapFrameAllocator, init_global_memory_manager, 
    init_page_fault_handler, get_global_memory_manager_mut
};
use crate::ai_bridge;
use alloc::boxed::Box;
use alloc::vec;

/// Memory configuration
pub struct MemoryConfig {
    /// Total physical memory in bytes
    pub total_memory: usize,
    /// Memory map for frame allocation (will be managed by the system)
    pub memory_map_size: usize,
    /// Enable consciousness integration
    pub enable_consciousness: bool,
}

impl Default for MemoryConfig {
    fn default() -> Self {
        MemoryConfig {
            total_memory: 64 * 1024 * 1024, // 64MB default
            memory_map_size: 16384,         // 16KB bitmap for 64MB
            enable_consciousness: true,
        }
    }
}

/// Initialize the complete memory management system
pub fn init_memory_system(config: MemoryConfig) -> Result<(), &'static str> {
    crate::println!("🧠 Initializing SynOS memory management system...");
    
    // Step 1: Initialize page fault handler
    init_page_fault_handler();
    crate::println!("✅ Page fault handler initialized");
    
    // Step 2: Create memory map for frame allocator
    let memory_map = create_memory_map(config.memory_map_size)?;
    crate::println!("✅ Memory map created ({} bytes)", config.memory_map_size);
    
    // Step 3: Create frame allocator
    let max_frames = config.total_memory / 4096;
    let frame_allocator = unsafe { 
        BitmapFrameAllocator::new(memory_map, max_frames) 
    };
    crate::println!("✅ Frame allocator created ({} frames)", max_frames);
    
    // Step 4: Initialize global memory manager
    init_global_memory_manager(Box::new(frame_allocator), config.total_memory);
    crate::println!("✅ Global memory manager initialized");
    
    // Step 5: Set up AI integration if enabled
    if config.enable_consciousness {
        if let Ok(()) = setup_ai_integration() {
            if let Some(manager) = get_global_memory_manager_mut() {
                manager.init_with_ai();
                crate::println!("✅ AI integration enabled");
            }
        } else {
            crate::println!("⚠️  AI integration failed, continuing without it");
        }
    }
    
    crate::println!("🎉 Memory management system fully initialized!");
    print_memory_system_info();
    
    Ok(())
}

/// Create memory map for frame allocation
fn create_memory_map(size: usize) -> Result<&'static mut [u8], &'static str> {
    // Create a vector and leak it to get a static reference
    let memory_map = vec![0u8; size];
    let memory_map = Box::leak(memory_map.into_boxed_slice());
    
    Ok(memory_map)
}

/// Set up AI integration
fn setup_ai_integration() -> Result<(), &'static str> {
    // Initialize AI bridge for memory management integration
    ai_bridge::init();
    
    if ai_bridge::is_initialized() {
        crate::println!("� AI bridge initialized for memory management");
        Ok(())
    } else {
        Err("Failed to initialize AI bridge")
    }
}

/// Print memory system information
fn print_memory_system_info() {
    use crate::memory::get_global_memory_manager;
    
    if let Some(manager) = get_global_memory_manager() {
        crate::println!("📊 Memory System Information:");
        crate::println!("   Total Memory: {} MB", manager.total_memory() / (1024 * 1024));
        crate::println!("   Available Memory: {} MB", manager.available_memory() / (1024 * 1024));
        crate::println!("   Consciousness Integration: {}", 
                 if manager.test_consciousness_integration() { "✅ Enabled" } else { "❌ Disabled" });
        
        let stats = manager.get_stats();
        crate::println!("   Memory Statistics:");
        crate::println!("     Pages Allocated: {}", stats.pages_allocated);
        crate::println!("     Page Faults Handled: {}", stats.page_faults_handled);
        crate::println!("     Out of Memory Events: {}", stats.out_of_memory_events);
    }
}

/// Test the memory system
pub fn test_memory_system() -> Result<(), &'static str> {
    use crate::memory::{get_global_memory_manager, VirtualAddress, virtual_memory::PageTableFlags};
    
    crate::println!("🧪 Testing memory system...");
    
    let manager = get_global_memory_manager()
        .ok_or("Global memory manager not initialized")?;
    
    // Test 1: Basic page fault handling
    crate::println!("Test 1: Page fault handling...");
    let test_addr = VirtualAddress::new(0x10000);
    match manager.handle_page_fault(test_addr, 0, 0x400000) {
        Ok(()) => {
            crate::println!("✅ Page fault handling test passed");
        }
        Err(_e) => {
            crate::println!("❌ Page fault handling test failed: {:?}", _e);
        }
    }
    
    // Test 2: Virtual region allocation
    crate::println!("Test 2: Virtual region allocation...");
    let region_addr = VirtualAddress::new(0x20000);
    let flags = PageTableFlags::PRESENT | PageTableFlags::WRITABLE;
    match manager.allocate_virtual_region(region_addr, 8192, flags) {
        Ok(()) => {
            crate::println!("✅ Virtual region allocation test passed");
        }
        Err(_e) => {
            crate::println!("❌ Virtual region allocation test failed: {:?}", _e);
        }
    }
    
    // Test 3: Consciousness integration
    crate::println!("Test 3: Consciousness integration...");
    if manager.test_consciousness_integration() {
        match manager.optimize_memory_with_consciousness() {
            Ok(_swapped_pages) => {
                crate::println!("✅ Consciousness optimization test passed ({} pages)", _swapped_pages);
            }
            Err(_e) => {
                crate::println!("⚠️  Consciousness optimization test failed: {:?}", _e);
            }
        }
    } else {
        crate::println!("⚠️  Consciousness integration not available for testing");
    }
    
    // Print final statistics
    let _stats = manager.get_stats();
    crate::println!("📊 Final test statistics:");
    crate::println!("   Pages allocated: {}", _stats.pages_allocated);
    crate::println!("   Page faults handled: {}", _stats.page_faults_handled);
    
    crate::println!("🎉 Memory system testing completed!");
    Ok(())
}

/// Memory system health check
pub fn memory_health_check() -> Result<(), &'static str> {
    use crate::memory::get_global_memory_manager;
    
    let manager = get_global_memory_manager()
        .ok_or("Global memory manager not initialized")?;
    
    let stats = manager.get_stats();
    let available = manager.available_memory();
    
    // Check for critical memory conditions
    if available < (1024 * 1024) { // Less than 1MB available
        crate::println!("🚨 CRITICAL: Low memory warning - {} bytes available", available);
        return Err("Critical memory shortage");
    }
    
    if stats.out_of_memory_events > 10 {
        crate::println!("⚠️  WARNING: High out-of-memory event count: {}", stats.out_of_memory_events);
    }
    
    crate::println!("✅ Memory system health check passed");
    Ok(())
}
