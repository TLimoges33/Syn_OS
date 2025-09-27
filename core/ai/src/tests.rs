use alloc::vec::Vec;
use alloc::vec;
use crate::security::SecurityLevel;
use crate::pattern_recognition::{Pattern, PatternType};
use crate::neural::NeuralState;
use crate::{get_state, process_inference, init};

// Custom sqrt function for no_std environment
fn approx_sqrt(x: f32) -> f32 {
    if x <= 0.0 {
        return 0.0;
    }
    
    let mut guess = x;
    for _ in 0..10 { // Newton's method iterations
        guess = 0.5 * (guess + x / guess);
    }
    guess
}

#[test]
fn test_ai_init() {
    init();
    // Test that init completes without panic
    assert!(true);
}

#[test]
fn test_ai_state() {
    init();
    let state = get_state();
    
    // Test that we can get AI state
    assert!(state.neural_activation() >= 0.0);
    assert!(state.pattern_count() >= 0);
    
    match state.security_level() {
        SecurityLevel::Low | SecurityLevel::Medium | SecurityLevel::High | SecurityLevel::Critical => {
            assert!(true);
        }
    }
}

#[test]
fn test_process_inference() {
    let input = vec![1.0, 2.0, 3.0];
    let output = process_inference(&input);
    
    assert_eq!(input.len(), output.len());
}

#[test]
fn test_pattern_creation() {
    use alloc::string::String;
    use alloc::collections::BTreeMap;
    
    let pattern = Pattern {
        id: String::from("test_pattern"),
        pattern_type: PatternType::Sequential,
        confidence: 0.8,
        features: vec![1.0, 2.0, 3.0],
        metadata: BTreeMap::new(),
    };
    
    assert_eq!(pattern.confidence, 0.8);
    assert_eq!(pattern.features.len(), 3);
}

#[test]
fn test_security_levels() {
    let levels = vec![
        SecurityLevel::Low,
        SecurityLevel::Medium,
        SecurityLevel::High,
        SecurityLevel::Critical,
    ];
    
    assert_eq!(levels.len(), 4);
}

#[test]
fn test_math_helpers() {
    // Test our custom sqrt function
    assert!((approx_sqrt(4.0) - 2.0).abs() < 0.001);
    assert!((approx_sqrt(9.0) - 3.0).abs() < 0.001);
    assert!((approx_sqrt(16.0) - 4.0).abs() < 0.001);
    
    // Edge cases
    assert_eq!(approx_sqrt(0.0), 0.0);
    assert_eq!(approx_sqrt(-1.0), 0.0);
}

#[test]
fn test_neural_state() {
    let state = NeuralState {
        activation_level: 0.7,
        pattern_count: 5,
        confidence: 0.85,
    };
    
    assert_eq!(state.activation_level, 0.7);
    assert_eq!(state.pattern_count, 5);
    assert_eq!(state.confidence, 0.85);
}

#[test]
fn test_vector_operations() {
    let v1 = vec![1.0, 2.0, 3.0];
    let v2 = vec![4.0, 5.0, 6.0];
    
    // Test basic vector operations
    assert_eq!(v1.len(), v2.len());
    
    let mut result = Vec::new();
    for (a, b) in v1.iter().zip(v2.iter()) {
        result.push(a + b);
    }
    
    assert_eq!(result, vec![5.0, 7.0, 9.0]);
}

#[test]
fn test_ai_module_integration() {
    // Test that all modules can be used together
    init();
    
    let input_data = vec![0.1, 0.2, 0.3];
    let output = process_inference(&input_data);
    
    let state = get_state();
    
    // Verify we got some output and state
    assert!(!output.is_empty());
    assert!(state.neural_activation() >= 0.0);
}

#[test]
fn test_pattern_types() {
    // Test that all pattern types are available
    let pattern_types = vec![
        PatternType::Sequential,
        PatternType::Spatial,
        PatternType::Temporal,
        PatternType::Anomaly,
        PatternType::Cluster,
    ];
    
    assert_eq!(pattern_types.len(), 5);
}

#[test]
fn test_ai_constants() {
    // Test that AI constants are accessible
    assert_eq!(crate::VERSION, "4.3.0");
}