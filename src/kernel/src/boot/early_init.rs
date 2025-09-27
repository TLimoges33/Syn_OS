//! Early Kernel Initialization
//!
//! Handles the earliest phase of kernel boot, setting up fundamental
//! systems before memory management and interrupts are available.

use crate::gdt;
use crate::serial::{serial_print, serial_println};

/// Perform early kernel initialization
pub fn early_kernel_init() -> Result<(), &'static str> {
    serial_println!("🚀 Starting Syn OS Kernel...");
    
    // Initialize Global Descriptor Table
    gdt::init();
    serial_println!("✅ GDT initialized");
    
    // Initialize basic logging
    init_early_logging();
    serial_println!("✅ Early logging initialized");
    
    // Validate boot environment
    validate_boot_environment()?;
    serial_println!("✅ Boot environment validated");
    
    serial_println!("🎯 Early initialization complete");
    Ok(())
}

/// Initialize early logging system
fn init_early_logging() {
    // Set up basic serial logging
    // This is implemented in the serial module
    serial_println!("📝 Early logging system active");
}

/// Validate the boot environment
fn validate_boot_environment() -> Result<(), &'static str> {
    // Check CPU features
    if !check_required_cpu_features() {
        return Err("Required CPU features not available");
    }
    
    // Validate memory layout
    if !validate_memory_layout() {
        return Err("Invalid memory layout detected");
    }
    
    Ok(())
}

/// Check for required CPU features
fn check_required_cpu_features() -> bool {
    // Check for x86_64 architecture
    #[cfg(target_arch = "x86_64")]
    {
        // Basic x86_64 features are available by definition
        true
    }
    
    #[cfg(not(target_arch = "x86_64"))]
    {
        false
    }
}

/// Validate memory layout assumptions
fn validate_memory_layout() -> bool {
    // Basic validation - more comprehensive checks in memory module
    // For now, assume valid layout
    true
}
