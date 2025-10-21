//! SynOS AI Engine
//!
//! This module provides the artificial intelligence engine for SynOS,
//! implementing decision making, pattern recognition, neural networks,
//! and intelligent system optimization.

#![no_std]
extern crate alloc;

use alloc::vec::Vec;

pub mod neural;
pub mod consciousness;
pub mod decision;
pub mod inference;
pub mod pattern_recognition;
pub mod security;

// Export main types for easier access
pub use consciousness::{ConsciousnessState, ConsciousnessLayer, LearningInsight, InsightType};
pub use decision::DecisionEngine;
pub use inference::InferenceEngine;
pub use pattern_recognition::PatternRecognizer;
pub use security::SecurityIntegration;

#[cfg(test)]
mod tests;

// Re-export commonly used items
pub use neural::{NeuralNetwork, NeuralState};
pub use decision::{Decision};
pub use pattern_recognition::{Pattern, PatternMatcher};

/// AI engine version
pub const VERSION: &str = "4.5.0";

/// AI system state
#[derive(Debug, Clone)]
pub struct AIState {
    pub neural: neural::NeuralState,
    pub security_level: security::SecurityLevel,
    pub active_patterns: usize,
    pub active_decisions: usize,
}

impl AIState {
    /// Get neural network activation level
    pub fn neural_activation(&self) -> f64 {
        self.neural.activation_level
    }

    /// Get number of active patterns
    pub fn pattern_count(&self) -> usize {
        self.active_patterns
    }

    /// Get security level
    pub fn security_level(&self) -> &security::SecurityLevel {
        &self.security_level
    }
}

/// Initialize the AI engine
pub fn init() {
    // Uncomment when println! is available or use alternative logging
    // println!("Initializing SynOS AI Engine v{}", VERSION);

    // Initialize components
    neural::init();
    pattern_recognition::init();
    security::init();
    decision::init();
    inference::init();

    // println!("AI Engine initialization complete.");
}

/// Update the AI system state
pub fn update() {
    // Update AI subsystems
    neural::update();
    // pattern_recognition and decision modules don't have update functions yet
}

/// Get the current AI state
pub fn get_state() -> AIState {
    AIState {
        neural: neural::get_state(),
        security_level: security::SecurityLevel::Medium, // Placeholder
        active_patterns: 0, // Placeholder
        active_decisions: 0, // Placeholder
    }
}

/// Process AI inference request
pub fn process_inference(input: &[f32]) -> Vec<f32> {
    // Basic inference placeholder - returns input for now
    input.to_vec()
}
