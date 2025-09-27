//! SynOS Consciousness Module
//!
//! Provides consciousness and AI capabilities for the SynOS kernel, including
//! Neural Darwinism integration for advanced cybersecurity operations.

use core::fmt;

pub mod neural_darwinism_bridge;

#[cfg(feature = "userspace")]
pub use neural_darwinism_bridge::*;

/// Consciousness level enumeration
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ConsciousnessLevel {
    Dormant,
    Aware,
    Active,
    Enhanced,
    Critical,
}

/// Core consciousness state for kernel operations
#[derive(Debug)]
pub struct ConsciousnessState {
    level: ConsciousnessLevel,
    activation: f64,
    memory_coherence: f64,
    neural_synchrony: f64,
    quantum_coherence: f64,
    threat_assessment: f64,
}

impl ConsciousnessState {
    /// Create a new consciousness state
    pub fn new() -> Self {
        Self {
            level: ConsciousnessLevel::Dormant,
            activation: 0.0,
            memory_coherence: 0.0,
            neural_synchrony: 0.0,
            quantum_coherence: 0.0,
            threat_assessment: 0.0,
        }
    }

    /// Update consciousness level with multi-dimensional input
    pub fn update(&mut self, input_stimulus: f64, memory_input: f64, threat_input: f64) {
        // Update activation with weighted inputs
        self.activation = (self.activation * 0.8
            + input_stimulus * 0.1
            + memory_input * 0.05
            + threat_input * 0.05)
            .min(1.0);

        // Update memory coherence
        self.memory_coherence = (self.memory_coherence * 0.9 + memory_input * 0.1).min(1.0);

        // Update neural synchrony based on activation
        self.neural_synchrony = (self.activation + self.memory_coherence) / 2.0;

        // Update quantum coherence (advanced metric)
        self.quantum_coherence = (self.neural_synchrony * 0.8 + self.activation * 0.2).min(1.0);

        // Update threat assessment
        self.threat_assessment = (self.threat_assessment * 0.7 + threat_input * 0.3).min(1.0);

        // Determine consciousness level based on multiple factors
        let combined_metric =
            (self.activation * 0.4 + self.neural_synchrony * 0.3 + self.quantum_coherence * 0.3);

        self.level = match combined_metric {
            x if x > 0.9 => ConsciousnessLevel::Critical,
            x if x > 0.75 => ConsciousnessLevel::Enhanced,
            x if x > 0.6 => ConsciousnessLevel::Active,
            x if x > 0.3 => ConsciousnessLevel::Aware,
            _ => ConsciousnessLevel::Dormant,
        };
    }

    /// Get current consciousness level
    pub fn level(&self) -> ConsciousnessLevel {
        self.level
    }

    /// Get activation level
    pub fn activation(&self) -> f64 {
        self.activation
    }

    /// Get memory coherence
    pub fn memory_coherence(&self) -> f64 {
        self.memory_coherence
    }

    /// Get neural synchrony
    pub fn neural_synchrony(&self) -> f64 {
        self.neural_synchrony
    }

    /// Get quantum coherence
    pub fn quantum_coherence(&self) -> f64 {
        self.quantum_coherence
    }

    /// Get threat assessment level
    pub fn threat_assessment(&self) -> f64 {
        self.threat_assessment
    }

    /// Check if consciousness is enhanced enough for advanced operations
    pub fn is_enhanced(&self) -> bool {
        matches!(
            self.level,
            ConsciousnessLevel::Enhanced | ConsciousnessLevel::Critical
        )
    }

    /// Get consciousness metrics as a formatted string
    pub fn metrics_summary(&self) -> String {
        format!(
            "Level: {} | Activation: {:.3} | Synchrony: {:.3} | Quantum: {:.3} | Threat: {:.3}",
            self.level,
            self.activation,
            self.neural_synchrony,
            self.quantum_coherence,
            self.threat_assessment
        )
    }
}

impl fmt::Display for ConsciousnessLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConsciousnessLevel::Dormant => write!(f, "Dormant"),
            ConsciousnessLevel::Aware => write!(f, "Aware"),
            ConsciousnessLevel::Active => write!(f, "Active"),
            ConsciousnessLevel::Enhanced => write!(f, "Enhanced"),
            ConsciousnessLevel::Critical => write!(f, "Critical"),
        }
    }
}

/// Global consciousness state (for kernel-level awareness)
static mut GLOBAL_CONSCIOUSNESS: Option<ConsciousnessState> = None;

/// Initialize consciousness subsystem
pub fn init() {
    unsafe {
        GLOBAL_CONSCIOUSNESS = Some(ConsciousnessState::new());
    }
    println!("🧠 SynOS Consciousness subsystem initialized");
    println!("   - Neural Darwinism integration: Available");
    println!("   - Quantum coherence monitoring: Active");
    println!("   - Threat assessment engine: Ready");
}

/// Update global consciousness state
pub fn update_consciousness(input_stimulus: f64, memory_input: f64, threat_input: f64) {
    unsafe {
        if let Some(ref mut consciousness) = GLOBAL_CONSCIOUSNESS {
            consciousness.update(input_stimulus, memory_input, threat_input);
        }
    }
}

/// Get current global consciousness level
pub fn get_consciousness_level() -> ConsciousnessLevel {
    unsafe {
        GLOBAL_CONSCIOUSNESS
            .as_ref()
            .map(|c| c.level())
            .unwrap_or(ConsciousnessLevel::Dormant)
    }
}

/// Get consciousness metrics for monitoring
pub fn get_consciousness_metrics() -> Option<String> {
    unsafe { GLOBAL_CONSCIOUSNESS.as_ref().map(|c| c.metrics_summary()) }
}

/// Check if consciousness is enhanced for advanced operations
pub fn is_consciousness_enhanced() -> bool {
    unsafe {
        GLOBAL_CONSCIOUSNESS
            .as_ref()
            .map(|c| c.is_enhanced())
            .unwrap_or(false)
    }
}
