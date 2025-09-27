/// Hardware Abstraction Layer (HAL) Module for SynOS
/// Temporarily using minimal HAL for Phase 5 development

pub mod minimal_hal;

// Re-export minimal HAL as main HAL
pub use minimal_hal::*;
