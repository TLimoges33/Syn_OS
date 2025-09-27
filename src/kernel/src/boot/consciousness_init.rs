//! Consciousness System Initialization
//!
//! Integrates consciousness system startup into the kernel boot process,
//! bridging the kernel with the AI engine for consciousness-aware computing.

use alloc::vec::Vec;
use crate::ai::ConsciousnessKernel;
use crate::serial::{serial_print, serial_println};

/// Initialize consciousness system during boot
pub async fn init_consciousness() -> Result<(), &'static str> {
    serial_println!("🧠 Initializing Consciousness System...");
    
    // Initialize consciousness kernel bridge
    let consciousness_kernel = ConsciousnessKernel::new().await
        .map_err(|_| "Failed to initialize consciousness kernel")?;
    
    // Start consciousness processes
    consciousness_kernel.start_consciousness_processes().await
        .map_err(|_| "Failed to start consciousness processes")?;
    
    // Establish AI bridge
    establish_ai_bridge().await?;
    
    // Initialize neural darwinism
    init_neural_darwinism().await?;
    
    serial_println!("✅ Consciousness system initialized");
    Ok(())
}

/// Establish bridge to AI engine
async fn establish_ai_bridge() -> Result<(), &'static str> {
    serial_println!("🔗 Establishing AI bridge...");
    
    // Initialize AI bridge from ai_bridge.rs functionality
    crate::ai::bridge::initialize_ai_bridge().await
        .map_err(|_| "Failed to establish AI bridge")?;
    
    serial_println!("✅ AI bridge established");
    Ok(())
}

/// Initialize neural darwinism system
async fn init_neural_darwinism() -> Result<(), &'static str> {
    serial_println!("🧬 Initializing Neural Darwinism...");
    
    // Start neural population dynamics
    crate::ai::consciousness::start_neural_populations().await
        .map_err(|_| "Failed to start neural populations")?;
    
    // Initialize consciousness memory
    crate::ai::consciousness::init_consciousness_memory().await
        .map_err(|_| "Failed to initialize consciousness memory")?;
    
    serial_println!("✅ Neural Darwinism initialized");
    Ok(())
}

/// Validate consciousness system readiness
pub async fn validate_consciousness_readiness() -> Result<(), &'static str> {
    serial_println!("🔍 Validating consciousness readiness...");
    
    // Check AI engine connectivity
    if !crate::ai::bridge::is_ai_engine_connected().await {
        return Err("AI engine not connected");
    }
    
    // Check consciousness processes
    if !crate::ai::consciousness::are_processes_running().await {
        return Err("Consciousness processes not running");
    }
    
    serial_println!("✅ Consciousness system ready");
    Ok(())
}
