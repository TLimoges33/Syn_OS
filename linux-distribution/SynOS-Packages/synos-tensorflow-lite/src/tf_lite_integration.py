#!/usr/bin/env python3
"""
SynOS TensorFlow Lite Integration
On-device inference with hardware acceleration for consciousness framework

Features:
- TensorFlow Lite model loading and inference
- Hardware acceleration delegates (GPU, NPU, TPU)
- Model security and integrity verification
- Real-time neural pattern recognition
- Consciousness state prediction
- Threat classification models
"""

import os
import sys
import json
import logging
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta

try:
    import tensorflow as tf
    import tflite_runtime.interpreter as tflite
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None
    tflite = None

logger = logging.getLogger(__name__)

class ModelSecurityValidator:
    """Validates TensorFlow Lite models for security and integrity"""

    def __init__(self):
        self.trusted_hashes = {}
        self.hash_file = "/etc/synos/model-hashes.json"
        self._load_trusted_hashes()

    def _load_trusted_hashes(self):
        """Load trusted model hashes from configuration"""
        try:
            if os.path.exists(self.hash_file):
                with open(self.hash_file, 'r') as f:
                    self.trusted_hashes = json.load(f)
                logger.info(f"Loaded {len(self.trusted_hashes)} trusted model hashes")
        except Exception as e:
            logger.warning(f"Failed to load trusted hashes: {e}")

    def calculate_model_hash(self, model_path: str) -> str:
        """Calculate SHA-256 hash of model file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(model_path, "rb") as f:
                # Read file in chunks to handle large models
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {model_path}: {e}")
            return ""

    def validate_model(self, model_path: str, model_name: str = None) -> bool:
        """Validate model integrity and authenticity"""
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False

        # Calculate current hash
        current_hash = self.calculate_model_hash(model_path)
        if not current_hash:
            return False

        # Check against trusted hashes if available
        model_name = model_name or os.path.basename(model_path)
        if model_name in self.trusted_hashes:
            expected_hash = self.trusted_hashes[model_name]
            if current_hash == expected_hash:
                logger.info(f"Model {model_name} hash validation passed")
                return True
            else:
                logger.error(f"Model {model_name} hash mismatch! Expected: {expected_hash}, Got: {current_hash}")
                return False

        # If no trusted hash, log warning but allow (for development)
        logger.warning(f"No trusted hash for model {model_name}, proceeding with caution")
        return True

    def add_trusted_hash(self, model_name: str, model_path: str):
        """Add a model to trusted hashes"""
        hash_value = self.calculate_model_hash(model_path)
        if hash_value:
            self.trusted_hashes[model_name] = hash_value
            self._save_trusted_hashes()
            logger.info(f"Added trusted hash for {model_name}")

    def _save_trusted_hashes(self):
        """Save trusted hashes to file"""
        try:
            os.makedirs(os.path.dirname(self.hash_file), exist_ok=True)
            with open(self.hash_file, 'w') as f:
                json.dump(self.trusted_hashes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save trusted hashes: {e}")

class HardwareAccelerationManager:
    """Manages hardware acceleration delegates for TensorFlow Lite"""

    def __init__(self):
        self.available_delegates = {}
        self._discover_delegates()

    def _discover_delegates(self):
        """Discover available hardware acceleration delegates"""
        if not TF_AVAILABLE:
            return

        # Check for GPU delegate
        try:
            gpu_delegate = tf.lite.experimental.load_delegate('libdelegate_gpu.so')
            self.available_delegates['gpu'] = gpu_delegate
            logger.info("GPU delegate available")
        except Exception:
            logger.debug("GPU delegate not available")

        # Check for EdgeTPU delegate
        try:
            edgetpu_delegate = tf.lite.experimental.load_delegate('libedgetpu.so')
            self.available_delegates['edgetpu'] = edgetpu_delegate
            logger.info("EdgeTPU delegate available")
        except Exception:
            logger.debug("EdgeTPU delegate not available")

        # Check for NPU delegates (vendor-specific)
        for npu_lib in ['libnpu_delegate.so', 'libvpu_delegate.so']:
            try:
                npu_delegate = tf.lite.experimental.load_delegate(npu_lib)
                self.available_delegates['npu'] = npu_delegate
                logger.info(f"NPU delegate available: {npu_lib}")
                break
            except Exception:
                continue

        logger.info(f"Available hardware delegates: {list(self.available_delegates.keys())}")

    def get_optimal_delegates(self, model_requirements: Dict[str, Any] = None) -> List[Any]:
        """Get optimal delegates for a model"""
        delegates = []

        # Prioritize based on performance and availability
        priority_order = ['edgetpu', 'npu', 'gpu']

        for delegate_type in priority_order:
            if delegate_type in self.available_delegates:
                delegates.append(self.available_delegates[delegate_type])
                logger.info(f"Using {delegate_type} acceleration")
                break

        return delegates

class TensorFlowLiteModel:
    """Wrapper for TensorFlow Lite model with SynOS consciousness integration"""

    def __init__(self, model_path: str, model_name: str = None):
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow Lite not available")

        self.model_path = model_path
        self.model_name = model_name or os.path.basename(model_path)
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.is_loaded = False

        # Security and acceleration
        self.security_validator = ModelSecurityValidator()
        self.hw_manager = HardwareAccelerationManager()

        # Performance tracking
        self.inference_count = 0
        self.total_inference_time = 0.0
        self.last_inference_time = 0.0

    def load_model(self, use_hardware_acceleration: bool = True) -> bool:
        """Load TensorFlow Lite model with optional hardware acceleration"""
        logger.info(f"Loading TensorFlow Lite model: {self.model_name}")

        # Validate model security
        if not self.security_validator.validate_model(self.model_path, self.model_name):
            logger.error(f"Model security validation failed: {self.model_name}")
            return False

        try:
            # Get hardware delegates if requested
            delegates = []
            if use_hardware_acceleration:
                delegates = self.hw_manager.get_optimal_delegates()

            # Create interpreter
            self.interpreter = tflite.Interpreter(
                model_path=self.model_path,
                experimental_delegates=delegates
            )

            # Allocate tensors
            self.interpreter.allocate_tensors()

            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            self.is_loaded = True
            logger.info(f"Model loaded successfully: {self.model_name}")

            # Log model details
            self._log_model_details()

            return True

        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            return False

    def _log_model_details(self):
        """Log model architecture details"""
        if not self.is_loaded:
            return

        logger.info(f"Model: {self.model_name}")
        logger.info(f"Input shape: {[detail['shape'] for detail in self.input_details]}")
        logger.info(f"Output shape: {[detail['shape'] for detail in self.output_details]}")

        # Log data types
        input_types = [detail['dtype'] for detail in self.input_details]
        output_types = [detail['dtype'] for detail in self.output_details]
        logger.info(f"Input types: {input_types}")
        logger.info(f"Output types: {output_types}")

    def predict(self, input_data: np.ndarray) -> Optional[np.ndarray]:
        """Run inference on input data"""
        if not self.is_loaded:
            logger.error("Model not loaded")
            return None

        start_time = time.time()

        try:
            # Prepare input data
            if len(self.input_details) != 1:
                logger.error("Model must have exactly one input")
                return None

            input_detail = self.input_details[0]
            input_shape = input_detail['shape']

            # Reshape if necessary
            if input_data.shape != tuple(input_shape):
                if input_data.size == np.prod(input_shape):
                    input_data = input_data.reshape(input_shape)
                else:
                    logger.error(f"Input shape mismatch: {input_data.shape} vs {input_shape}")
                    return None

            # Set input tensor
            self.interpreter.set_tensor(input_detail['index'], input_data)

            # Run inference
            self.interpreter.invoke()

            # Get output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

            # Update performance metrics
            inference_time = time.time() - start_time
            self.inference_count += 1
            self.total_inference_time += inference_time
            self.last_inference_time = inference_time

            return output_data

        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return None

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if self.inference_count == 0:
            return {}

        return {
            'model_name': self.model_name,
            'inference_count': self.inference_count,
            'average_inference_time': self.total_inference_time / self.inference_count,
            'last_inference_time': self.last_inference_time,
            'total_inference_time': self.total_inference_time
        }

class ConsciousnessPatternClassifier:
    """Neural pattern classification for consciousness states"""

    def __init__(self, model_path: str = "/usr/share/synos/models/consciousness_patterns.tflite"):
        self.model = TensorFlowLiteModel(model_path, "consciousness_patterns")
        self.pattern_labels = [
            "security_alert", "learning_active", "high_activity", "low_activity",
            "threat_detected", "normal_operation", "adaptation_mode", "evolution_active"
        ]

    def load(self) -> bool:
        """Load consciousness pattern classification model"""
        return self.model.load_model()

    def classify_consciousness_state(self, state_vector: np.ndarray) -> Dict[str, Any]:
        """Classify consciousness state from feature vector"""
        if not self.model.is_loaded:
            logger.error("Consciousness pattern model not loaded")
            return {}

        # Ensure input is float32
        if state_vector.dtype != np.float32:
            state_vector = state_vector.astype(np.float32)

        # Run inference
        predictions = self.model.predict(state_vector)

        if predictions is None:
            return {}

        # Convert to probabilities
        probabilities = tf.nn.softmax(predictions[0]).numpy() if TF_AVAILABLE else predictions[0]

        # Create classification results
        results = {
            'predictions': {},
            'top_pattern': None,
            'confidence': 0.0,
            'inference_time': self.model.last_inference_time
        }

        for i, label in enumerate(self.pattern_labels):
            if i < len(probabilities):
                results['predictions'][label] = float(probabilities[i])

        # Find top prediction
        if results['predictions']:
            top_pattern = max(results['predictions'].items(), key=lambda x: x[1])
            results['top_pattern'] = top_pattern[0]
            results['confidence'] = top_pattern[1]

        return results

class ThreatClassificationModel:
    """AI threat detection and classification"""

    def __init__(self, model_path: str = "/usr/share/synos/models/threat_classifier.tflite"):
        self.model = TensorFlowLiteModel(model_path, "threat_classifier")
        self.threat_types = [
            "benign", "malware", "phishing", "ddos", "intrusion",
            "anomaly", "suspicious", "critical"
        ]

    def load(self) -> bool:
        """Load threat classification model"""
        return self.model.load_model()

    def classify_threat(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        """Classify security threat from network/system features"""
        if not self.model.is_loaded:
            logger.error("Threat classification model not loaded")
            return {}

        # Ensure input is float32
        if feature_vector.dtype != np.float32:
            feature_vector = feature_vector.astype(np.float32)

        # Run inference
        predictions = self.model.predict(feature_vector)

        if predictions is None:
            return {}

        # Convert to probabilities
        probabilities = tf.nn.softmax(predictions[0]).numpy() if TF_AVAILABLE else predictions[0]

        # Create classification results
        results = {
            'threat_probabilities': {},
            'threat_type': None,
            'confidence': 0.0,
            'risk_level': 'low',
            'inference_time': self.model.last_inference_time
        }

        for i, threat_type in enumerate(self.threat_types):
            if i < len(probabilities):
                results['threat_probabilities'][threat_type] = float(probabilities[i])

        # Find top threat
        if results['threat_probabilities']:
            top_threat = max(results['threat_probabilities'].items(), key=lambda x: x[1])
            results['threat_type'] = top_threat[0]
            results['confidence'] = top_threat[1]

            # Determine risk level
            if results['confidence'] > 0.8 and results['threat_type'] in ['malware', 'intrusion', 'critical']:
                results['risk_level'] = 'high'
            elif results['confidence'] > 0.6 and results['threat_type'] not in ['benign']:
                results['risk_level'] = 'medium'
            else:
                results['risk_level'] = 'low'

        return results

class SynOSTensorFlowLite:
    """Main TensorFlow Lite integration for SynOS consciousness framework"""

    def __init__(self):
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow Lite not available - install tflite-runtime")

        self.consciousness_classifier = ConsciousnessPatternClassifier()
        self.threat_classifier = ThreatClassificationModel()
        self.custom_models = {}

        # Performance tracking
        self.inference_history = []
        self.max_history = 1000

    def initialize(self) -> bool:
        """Initialize all AI models"""
        logger.info("Initializing SynOS TensorFlow Lite integration")

        success = True

        # Load consciousness pattern classifier
        if not self.consciousness_classifier.load():
            logger.warning("Failed to load consciousness pattern classifier")
            success = False

        # Load threat classifier
        if not self.threat_classifier.load():
            logger.warning("Failed to load threat classifier")
            success = False

        if success:
            logger.info("TensorFlow Lite integration initialized successfully")
        else:
            logger.warning("TensorFlow Lite integration initialized with some failures")

        return success

    def predict_consciousness_pattern(self, awareness: float, neural_activity: float,
                                    learning_rate: float, system_load: float) -> Dict[str, Any]:
        """Predict consciousness pattern from state metrics"""
        # Create feature vector
        features = np.array([
            awareness, neural_activity, learning_rate, system_load
        ], dtype=np.float32).reshape(1, -1)

        result = self.consciousness_classifier.classify_consciousness_state(features)

        # Record inference
        self._record_inference("consciousness_pattern", result.get('inference_time', 0))

        return result

    def classify_security_threat(self, network_features: Dict[str, float]) -> Dict[str, Any]:
        """Classify security threat from network/system features"""
        # Convert features to vector (simplified example)
        feature_vector = np.array([
            network_features.get('packet_rate', 0.0),
            network_features.get('connection_count', 0.0),
            network_features.get('data_volume', 0.0),
            network_features.get('protocol_anomaly_score', 0.0),
            network_features.get('port_scan_indicator', 0.0),
            network_features.get('payload_entropy', 0.0)
        ], dtype=np.float32).reshape(1, -1)

        result = self.threat_classifier.classify_threat(feature_vector)

        # Record inference
        self._record_inference("threat_classification", result.get('inference_time', 0))

        return result

    def load_custom_model(self, model_path: str, model_name: str) -> bool:
        """Load a custom TensorFlow Lite model"""
        try:
            custom_model = TensorFlowLiteModel(model_path, model_name)
            if custom_model.load_model():
                self.custom_models[model_name] = custom_model
                logger.info(f"Loaded custom model: {model_name}")
                return True
            else:
                logger.error(f"Failed to load custom model: {model_name}")
                return False
        except Exception as e:
            logger.error(f"Error loading custom model {model_name}: {e}")
            return False

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all models"""
        summary = {
            'consciousness_classifier': self.consciousness_classifier.model.get_performance_stats(),
            'threat_classifier': self.threat_classifier.model.get_performance_stats(),
            'custom_models': {},
            'total_inferences': len(self.inference_history),
            'average_inference_time': 0.0
        }

        # Add custom model stats
        for name, model in self.custom_models.items():
            summary['custom_models'][name] = model.get_performance_stats()

        # Calculate overall average
        if self.inference_history:
            summary['average_inference_time'] = sum(self.inference_history) / len(self.inference_history)

        return summary

    def _record_inference(self, model_type: str, inference_time: float):
        """Record inference for performance tracking"""
        self.inference_history.append(inference_time)

        # Trim history if too long
        if len(self.inference_history) > self.max_history:
            self.inference_history = self.inference_history[-self.max_history//2:]

# Example usage and testing
def test_tensorflow_lite_integration():
    """Test TensorFlow Lite integration"""
    print("Testing SynOS TensorFlow Lite Integration...")

    if not TF_AVAILABLE:
        print("TensorFlow Lite not available - install tflite-runtime")
        return

    try:
        # Create integration instance
        tfl = SynOSTensorFlowLite()

        # Initialize (will warn if models not found - that's expected for testing)
        tfl.initialize()

        # Test consciousness pattern prediction (with dummy data)
        consciousness_result = tfl.predict_consciousness_pattern(
            awareness=0.75,
            neural_activity=0.82,
            learning_rate=0.68,
            system_load=0.45
        )
        print(f"Consciousness prediction: {consciousness_result}")

        # Test threat classification (with dummy data)
        network_features = {
            'packet_rate': 1000.0,
            'connection_count': 50.0,
            'data_volume': 2048.0,
            'protocol_anomaly_score': 0.3,
            'port_scan_indicator': 0.1,
            'payload_entropy': 0.7
        }
        threat_result = tfl.classify_security_threat(network_features)
        print(f"Threat classification: {threat_result}")

        # Show performance summary
        performance = tfl.get_performance_summary()
        print(f"Performance summary: {performance}")

        print("TensorFlow Lite integration test completed")

    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    import time
    test_tensorflow_lite_integration()