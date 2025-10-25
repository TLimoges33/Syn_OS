//! Interrupt Handling Subsystem
//!
//! Manages interrupts, IDT (Interrupt Descriptor Table), and GDT (Global Descriptor Table)

pub mod interrupts;      // Main interrupt handlers
pub mod gdt;             // Global Descriptor Table
pub mod interrupt_security;  // Security for interrupt handling
pub mod manager;         // Interrupt manager

// Re-export specific items to avoid ambiguity
pub use gdt::{init as init_gdt};
pub use interrupt_security::*;

// Only re-export from interrupts module (not manager) to avoid duplication
pub use interrupts::{init, InterruptHandler};

// Re-export manager with specific name to avoid conflict
pub use manager::InterruptManager as InterruptManagerImpl;
