//! SynOS AI Runtime
//!
//! Native Rust AI inference runtime for kernel and userspace integration
//! Provides lightweight neural network inference without external dependencies

#![cfg_attr(not(feature = "std"), no_std)]

extern crate alloc;

// Core native inference engine
pub mod native_inference;

// Runtime implementations
pub mod tflite;
pub mod onnx;

// Re-export commonly used types
pub use native_inference::{
    NeuralNetwork,
    DenseLayer,
    Activation,
    ModelWeights,
    LayerWeights,
    QuantizedLayer,
};

pub use tflite::{
    TFLiteRuntime,
    AccelerationType,
    InferenceResult,
};
