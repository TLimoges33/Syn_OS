//! Kernel Boot System
//!
//! Handles the complete boot sequence from bootloader handoff to
//! full kernel initialization, including consciousness system startup.

pub mod early_init;
pub mod consciousness_init;
pub mod multiboot;
pub mod platform;

pub use early_init::early_kernel_init;
pub use consciousness_init::init_consciousness;

/// Boot sequence phases
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BootPhase {
    EarlyInit,
    MemorySetup,
    InterruptSetup,
    ConsciousnessInit,
    ServiceStart,
    Complete,
}

/// Boot configuration
#[derive(Debug, Clone)]
pub struct BootConfig {
    pub enable_consciousness: bool,
    pub enable_education: bool,
    pub debug_mode: bool,
    pub memory_limit_mb: Option<usize>,
}

impl Default for BootConfig {
    fn default() -> Self {
        Self {
            enable_consciousness: true,
            enable_education: true,
            debug_mode: cfg!(debug_assertions),
            memory_limit_mb: None,
        }
    }
}

/// Boot result information
#[derive(Debug, Clone)]
pub struct BootResult {
    pub phase: BootPhase,
    pub success: bool,
    pub message: &'static str,
}

/// Main boot sequence coordinator
pub async fn boot_kernel(config: BootConfig) -> Result<(), &'static str> {
    // Phase 1: Early initialization
    early_kernel_init()?;
    
    // Phase 2: Memory system setup
    crate::memory::init_memory_system(crate::memory::init::MemoryConfig::default())?;
    
    // Phase 3: Interrupt handling setup
    crate::interrupts::init_interrupts()?;
    
    // Phase 4: Consciousness initialization (if enabled)
    if config.enable_consciousness {
        init_consciousness().await?;
    }
    
    // Phase 5: Start kernel services
    start_kernel_services(&config).await?;
    
    Ok(())
}

/// Start essential kernel services
async fn start_kernel_services(config: &BootConfig) -> Result<(), &'static str> {
    // Start process scheduler
    crate::process::init_scheduler();
    
    // Start IPC system
    crate::ipc::init_ipc_system();
    
    // Start education platform if enabled
    if config.enable_education {
        crate::education::init_education_platform();
    }
    
    Ok(())
}
