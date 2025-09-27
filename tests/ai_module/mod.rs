//! AI Module Integration Tests
//! 
//! Tests for the SynOS AI system functionality

#[cfg(test)]
mod tests {
    use syn_ai::{AIState, init, get_state};

    #[test]
    fn test_ai_initialization() {
        // Test AI module initialization
        init();
        let state = get_state();
        assert!(state.optimization_level > 0);
    }

    #[test]
    fn test_ai_state_retrieval() {
        // Test AI state retrieval
        let state = get_state();
        assert!(matches!(state.security_level, syn_ai::security::SecurityLevel::_));
    }

    #[test]
    fn test_ai_inference() {
        // Test basic AI inference
        let input = vec![1.0, 2.0, 3.0];
        let output = syn_ai::process_inference(&input);
        assert_eq!(output.len(), input.len());
    }
}
