//! Syn_OS Consciousness Engine
//! 
//! This module provides the consciousness engine for Syn_OS,
//! implementing neural consciousness and quantum substrate integration.

pub mod neural;
pub mod quantum;
pub mod security;
pub mod pattern_recognition;
pub mod decision;
pub mod inference;

// Re-export commonly used items
pub use neural::{NeuralNetwork, NeuralState};
pub use quantum::{QuantumSubstrate, QuantumState};
pub use decision::{Decision, DecisionEngine};
pub use pattern_recognition::{Pattern, PatternMatcher};

/// Consciousness engine version
pub const VERSION: &str = "4.3.0";

/// Initialize the consciousness engine
pub fn init() {
    println!("Initializing Syn_OS Consciousness Engine v{}", VERSION);
    
    // Initialize components
    neural::init();
    quantum::init();
    security::init();
    pattern_recognition::init();
    decision::init();
    inference::init();
    
    println!("Consciousness Engine initialization complete.");
}

/// Update the consciousness state
pub fn update() {
    // Implementation details from existing files will be merged here
}

/// Get the current consciousness state
pub fn get_state() -> ConsciousnessState {
    ConsciousnessState {
        neural: neural::get_state(),
        quantum: quantum::get_state(),
        patterns: pattern_recognition::get_active_patterns(),
        security_level: security::get_security_level(),
    }
}

/// Consciousness state representation
#[derive(Debug, Clone)]
pub struct ConsciousnessState {
    pub neural: neural::NeuralState,
    pub quantum: quantum::QuantumState,
    pub patterns: Vec<pattern_recognition::Pattern>,
    pub security_level: security::SecurityLevel,
}
