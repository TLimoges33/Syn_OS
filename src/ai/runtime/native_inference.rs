//! Native Rust Inference Engine
//!
//! Lightweight neural network inference without external dependencies
//! Suitable for embedded/kernel environments

extern crate alloc;
use alloc::vec;
use alloc::vec::Vec;

/// Activation functions
#[derive(Debug, Clone, Copy)]
pub enum Activation {
    Linear,
    ReLU,
    Sigmoid,
    Tanh,
    Softmax,
}

impl Activation {
    pub fn apply(&self, x: f32) -> f32 {
        match self {
            Activation::Linear => x,
            Activation::ReLU => if x > 0.0 { x } else { 0.0 },
            Activation::Sigmoid => {
                // Sigmoid approximation using rational function
                if x >= 0.0 {
                    1.0 / (1.0 + Self::fast_exp(-x))
                } else {
                    let exp_x = Self::fast_exp(x);
                    exp_x / (1.0 + exp_x)
                }
            },
            Activation::Tanh => {
                // Tanh approximation: tanh(x) ≈ x * (27 + x²) / (27 + 9x²)
                let x2 = x * x;
                x * (27.0 + x2) / (27.0 + 9.0 * x2)
            },
            Activation::Softmax => x, // Applied layer-wise, not element-wise
        }
    }

    /// Fast exponential approximation for no_std
    fn fast_exp(x: f32) -> f32 {
        // Pade approximation: e^x ≈ (1 + x/2) / (1 - x/2) for small x
        if x < -5.0 { return 0.0; }
        if x > 5.0 { return 148.413; } // e^5
        let x_half = x / 2.0;
        (1.0 + x_half) / (1.0 - x_half)
    }

    pub fn apply_softmax(inputs: &mut [f32]) {
        let max_val = inputs.iter().fold(f32::NEG_INFINITY, |a, &b| a.max(b));

        // Subtract max for numerical stability and apply exp
        for val in inputs.iter_mut() {
            *val = Self::fast_exp(*val - max_val);
        }

        let sum: f32 = inputs.iter().sum();
        for val in inputs.iter_mut() {
            *val /= sum;
        }
    }
}

/// Dense (fully connected) layer
#[derive(Debug, Clone)]
pub struct DenseLayer {
    pub weights: Vec<Vec<f32>>,  // [output_size][input_size]
    pub biases: Vec<f32>,         // [output_size]
    pub activation: Activation,
}

impl DenseLayer {
    pub fn new(input_size: usize, output_size: usize, activation: Activation) -> Self {
        Self {
            weights: vec![vec![0.0; input_size]; output_size],
            biases: vec![0.0; output_size],
            activation,
        }
    }

    pub fn forward(&self, input: &[f32]) -> Vec<f32> {
        let mut output = Vec::with_capacity(self.biases.len());

        for (weights_row, &bias) in self.weights.iter().zip(self.biases.iter()) {
            let mut sum = bias;
            for (&w, &x) in weights_row.iter().zip(input.iter()) {
                sum += w * x;
            }
            output.push(self.activation.apply(sum));
        }

        if matches!(self.activation, Activation::Softmax) {
            Activation::apply_softmax(&mut output);
        }

        output
    }
}

/// Simple feedforward neural network
#[derive(Debug)]
pub struct NeuralNetwork {
    pub layers: Vec<DenseLayer>,
    pub input_size: usize,
    pub output_size: usize,
}

impl NeuralNetwork {
    pub fn new(input_size: usize, output_size: usize) -> Self {
        Self {
            layers: Vec::new(),
            input_size,
            output_size,
        }
    }

    pub fn add_layer(&mut self, output_size: usize, activation: Activation) {
        let input_size = if self.layers.is_empty() {
            self.input_size
        } else {
            self.layers.last().unwrap().biases.len()
        };

        self.layers.push(DenseLayer::new(input_size, output_size, activation));
    }

    pub fn forward(&self, mut input: Vec<f32>) -> Vec<f32> {
        for layer in &self.layers {
            input = layer.forward(&input);
        }
        input
    }

    pub fn predict(&self, input: &[f32]) -> Vec<f32> {
        self.forward(input.to_vec())
    }
}

/// Model storage format
#[derive(Debug)]
pub struct ModelWeights {
    pub layers: Vec<LayerWeights>,
}

#[derive(Debug)]
pub struct LayerWeights {
    pub weights: Vec<Vec<f32>>,
    pub biases: Vec<f32>,
    pub activation: Activation,
}

impl ModelWeights {
    pub fn to_network(&self, input_size: usize, output_size: usize) -> NeuralNetwork {
        let mut network = NeuralNetwork::new(input_size, output_size);

        for layer_weights in &self.layers {
            let layer = DenseLayer {
                weights: layer_weights.weights.clone(),
                biases: layer_weights.biases.clone(),
                activation: layer_weights.activation,
            };
            network.layers.push(layer);
        }

        network
    }

    pub fn from_network(network: &NeuralNetwork) -> Self {
        let layers = network.layers.iter().map(|layer| {
            LayerWeights {
                weights: layer.weights.clone(),
                biases: layer.biases.clone(),
                activation: layer.activation,
            }
        }).collect();

        Self { layers }
    }
}

/// Quantized int8 inference for efficiency
#[derive(Debug)]
pub struct QuantizedLayer {
    pub weights: Vec<Vec<i8>>,
    pub biases: Vec<i32>,
    pub scale: f32,
    pub zero_point: i8,
    pub activation: Activation,
}

impl QuantizedLayer {
    pub fn from_dense(layer: &DenseLayer) -> Self {
        // Find min/max for quantization
        let mut min_val = f32::INFINITY;
        let mut max_val = f32::NEG_INFINITY;

        for row in &layer.weights {
            for &w in row {
                min_val = min_val.min(w);
                max_val = max_val.max(w);
            }
        }

        let scale = (max_val - min_val) / 255.0;
        let zero_point = ((-min_val / scale) as i8).clamp(-128, 127);

        let weights = layer.weights.iter().map(|row| {
            row.iter().map(|&w| {
                ((w / scale) as i32 + zero_point as i32).clamp(-128, 127) as i8
            }).collect()
        }).collect();

        let biases = layer.biases.iter().map(|&b| {
            (b / scale) as i32
        }).collect();

        Self {
            weights,
            biases,
            scale,
            zero_point,
            activation: layer.activation,
        }
    }

    pub fn forward(&self, input: &[f32]) -> Vec<f32> {
        let mut output = Vec::with_capacity(self.biases.len());

        for (weights_row, &bias) in self.weights.iter().zip(self.biases.iter()) {
            let mut sum: i32 = bias;
            for (&w, &x) in weights_row.iter().zip(input.iter()) {
                let x_quant = ((x / self.scale) as i32 + self.zero_point as i32).clamp(-128, 127);
                sum += (w as i32) * x_quant;
            }
            let dequantized = (sum as f32) * self.scale;
            output.push(self.activation.apply(dequantized));
        }

        if matches!(self.activation, Activation::Softmax) {
            Activation::apply_softmax(&mut output);
        }

        output
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_activation_functions() {
        assert_eq!(Activation::Linear.apply(5.0), 5.0);
        assert_eq!(Activation::ReLU.apply(-5.0), 0.0);
        assert!(Activation::Sigmoid.apply(0.0) > 0.49 && Activation::Sigmoid.apply(0.0) < 0.51);
    }

    #[test]
    fn test_dense_layer() {
        let mut layer = DenseLayer::new(2, 3, Activation::ReLU);
        layer.weights = vec![
            vec![1.0, 0.0],
            vec![0.0, 1.0],
            vec![1.0, 1.0],
        ];
        layer.biases = vec![0.0, 0.0, 0.0];

        let output = layer.forward(&[2.0, 3.0]);
        assert_eq!(output, vec![2.0, 3.0, 5.0]);
    }

    #[test]
    fn test_neural_network() {
        let mut network = NeuralNetwork::new(2, 1);
        network.add_layer(3, Activation::ReLU);
        network.add_layer(1, Activation::Linear);

        let output = network.predict(&[1.0, 2.0]);
        assert_eq!(output.len(), 1);
    }
}
