// Package manager consciousness integration
// Uses canonical consciousness from core/ai

pub use syn_ai::consciousness::*;

/// Package installation consciousness context
pub struct PackageConsciousness {
    state: ConsciousnessState,
}

impl PackageConsciousness {
    pub fn new() -> Self {
        Self {
            state: ConsciousnessState::new(),
        }
    }

    pub fn analyze_package(&mut self, _package_name: &str) {
        // Consciousness-aware package analysis
        self.state.update_awareness(0.8);
    }
}

impl Default for PackageConsciousness {
    fn default() -> Self {
        Self::new()
    }
}
