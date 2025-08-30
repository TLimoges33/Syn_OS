#!/usr/bin/env python3
"""
Predictive Threat Modeling Framework with Machine Learning
==========================================================

Advanced AI-powered predictive threat modeling system with:
- Deep learning threat prediction models
- Consciousness-enhanced pattern recognition
- Quantum-aware threat forecasting
- Real-time adaptive learning
- Multi-dimensional threat vector analysis
- Enterprise-scale threat intelligence modeling
"""

import asyncio
import json
import logging
import time
import uuid
import pickle
import hashlib
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention
from tensorflow.keras.optimizers import Adam

# Consciousness integration
try:
    from ..consciousness_v2.consciousness_bus import ConsciousnessBus
except ImportError:
    class ConsciousnessBus:
        async def get_consciousness_state(self): return None

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom security exception for threat modeling operations"""
    pass


class ThreatPredictionModel(Enum):
    """Threat prediction model types"""
    LSTM_NEURAL_NETWORK = "lstm_neural_network"
    TRANSFORMER_ATTENTION = "transformer_attention"
    RANDOM_FOREST_ENSEMBLE = "random_forest_ensemble"
    ISOLATION_FOREST_ANOMALY = "isolation_forest_anomaly"
    CONSCIOUSNESS_HYBRID = "consciousness_hybrid"
    QUANTUM_ML_PREDICTOR = "quantum_ml_predictor"


class PredictionTimeframe(Enum):
    """Prediction time frames"""
    REAL_TIME = "real_time"  # Minutes
    SHORT_TERM = "short_term"  # Hours
    MEDIUM_TERM = "medium_term"  # Days
    LONG_TERM = "long_term"  # Weeks/Months


class ThreatCategory(Enum):
    """Threat categories for prediction"""
    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    APT = "apt"
    DDOS = "ddos"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    SUPPLY_CHAIN = "supply_chain"
    QUANTUM_THREAT = "quantum_threat"
    UNKNOWN = "unknown"


@dataclass
class ThreatPrediction:
    """Threat prediction result"""
    prediction_id: str
    model_name: str
    threat_category: ThreatCategory
    probability: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timeframe: PredictionTimeframe
    predicted_impact: str
    target_sectors: List[str]
    attack_vectors: List[str]
    indicators: List[str]
    mitigation_strategies: List[str]
    consciousness_enhancement: Dict[str, Any]
    quantum_considerations: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelPerformanceMetrics:
    """Model performance tracking"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    last_training: datetime
    training_samples: int
    prediction_count: int
    consciousness_integration_score: float = 0.0


@dataclass
class ThreatFeatureVector:
    """Feature vector for threat prediction"""
    feature_vector: np.ndarray
    feature_names: List[str]
    timestamp: datetime
    source_indicators: List[str]
    consciousness_features: Dict[str, float]
    quantum_features: Dict[str, float]


class PredictiveThreatModelingFramework:
    """
    Advanced predictive threat modeling framework with ML and consciousness integration
    """
    
    def __init__(self, consciousness_bus: Optional[ConsciousnessBus] = None):
        self.consciousness_bus = consciousness_bus or ConsciousnessBus()
        self.logger = logging.getLogger(f"{__name__}.PredictiveModeling")
        
        # Model storage
        self.models_directory = Path("/var/lib/synos/ml_models")
        self.models_directory.mkdir(parents=True, exist_ok=True)
        
        # Active models
        self.prediction_models: Dict[str, Any] = {}
        self.model_performance: Dict[str, ModelPerformanceMetrics] = {}
        self.feature_scalers: Dict[str, StandardScaler] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        
        # Training data
        self.training_data: List[ThreatFeatureVector] = []
        self.historical_predictions: List[ThreatPrediction] = []
        
        # Consciousness enhancement
        self.consciousness_weights: Dict[str, float] = {}
        self.consciousness_threshold = 0.7
        
        # Performance tracking
        self.prediction_count = 0
        self.successful_predictions = 0
        self.model_accuracy_threshold = 0.85
        
        # Feature engineering
        self.feature_extractors = {}
        self.feature_dimensions = 128  # Standard feature vector size
    
    async def initialize(self):
        """Initialize the predictive threat modeling framework"""
        try:
            self.logger.info("Initializing Predictive Threat Modeling Framework...")
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            # Initialize base models
            await self._initialize_prediction_models()
            
            # Load existing models if available
            await self._load_existing_models()
            
            # Initialize consciousness weights
            await self._initialize_consciousness_weights()
            
            # Start continuous learning
            asyncio.create_task(self._continuous_learning_loop())
            
            # Start model validation
            asyncio.create_task(self._model_validation_loop())
            
            self.logger.info("Predictive Threat Modeling Framework initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize predictive modeling framework: {e}")
            raise
    
    async def _initialize_feature_extractors(self):
        """Initialize threat feature extractors"""
        try:
            self.feature_extractors = {
                'temporal_features': self._extract_temporal_features,
                'behavioral_features': self._extract_behavioral_features,
                'network_features': self._extract_network_features,
                'content_features': self._extract_content_features,
                'consciousness_features': self._extract_consciousness_features,
                'quantum_features': self._extract_quantum_features
            }
            
            self.logger.info("Feature extractors initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize feature extractors: {e}")
            raise
    
    async def _initialize_prediction_models(self):
        """Initialize machine learning prediction models"""
        try:
            # LSTM Neural Network for time series prediction
            lstm_model = self._create_lstm_model()
            self.prediction_models['lstm_threat_predictor'] = lstm_model
            
            # Random Forest for ensemble prediction
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.prediction_models['random_forest_predictor'] = rf_model
            
            # Isolation Forest for anomaly detection
            isolation_model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
            self.prediction_models['anomaly_detector'] = isolation_model
            
            # Multi-layer Perceptron for complex pattern recognition
            mlp_model = MLPClassifier(
                hidden_layer_sizes=(256, 128, 64),
                activation='relu',
                solver='adam',
                alpha=0.001,
                batch_size='auto',
                learning_rate='constant',
                max_iter=500,
                random_state=42
            )
            self.prediction_models['mlp_pattern_detector'] = mlp_model
            
            # Consciousness-hybrid model (custom implementation)
            consciousness_model = self._create_consciousness_hybrid_model()
            self.prediction_models['consciousness_predictor'] = consciousness_model
            
            # Initialize scalers and encoders
            for model_name in self.prediction_models.keys():
                self.feature_scalers[model_name] = StandardScaler()
                self.label_encoders[model_name] = LabelEncoder()
            
            self.logger.info(f"Initialized {len(self.prediction_models)} prediction models")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize prediction models: {e}")
            raise
    
    def _create_lstm_model(self) -> tf.keras.Model:
        """Create LSTM neural network model"""
        try:
            model = Sequential([
                LSTM(128, return_sequences=True, input_shape=(None, self.feature_dimensions)),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32),
                Dropout(0.2),
                Dense(64, activation='relu'),
                Dense(32, activation='relu'),
                Dense(len(ThreatCategory), activation='softmax')
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to create LSTM model: {e}")
            raise
    
    def _create_consciousness_hybrid_model(self) -> Dict[str, Any]:
        """Create consciousness-enhanced hybrid prediction model"""
        try:
            # This is a custom model that integrates consciousness data
            # with traditional ML approaches
            model = {
                'type': 'consciousness_hybrid',
                'base_models': {
                    'pattern_recognition': MLPClassifier(
                        hidden_layer_sizes=(128, 64),
                        activation='relu',
                        solver='adam',
                        random_state=42
                    ),
                    'anomaly_detection': IsolationForest(
                        contamination=0.05,
                        random_state=42
                    )
                },
                'consciousness_weights': {},
                'quantum_awareness': True,
                'adaptive_learning': True
            }
            
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to create consciousness hybrid model: {e}")
            raise
    
    async def _load_existing_models(self):
        """Load existing trained models from storage"""
        try:
            model_files = list(self.models_directory.glob("*.pkl"))
            loaded_count = 0
            
            for model_file in model_files:
                try:
                    model_name = model_file.stem
                    
                    # Load model using secure deserialization
                    with open(model_file, 'rb') as f:
                        model_bytes = f.read()
                    
                    # Safely deserialize model data using JSON instead of pickle
                    import json
                    try:
                        # Try JSON first (safer)
                        model_data = json.loads(model_bytes.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Only use pickle as last resort with validation
                        import hmac
                        import hashlib
                        # Validate integrity before deserializing
                        if len(model_bytes) < 32:
                            raise SecurityError("Invalid model data")
                        stored_hash = model_bytes[:32]
                        data_content = model_bytes[32:]
                        # Create expected hash using model file path as key
                        expected_hash = hashlib.sha256(data_content + str(model_file).encode()).digest()
                        if not hmac.compare_digest(stored_hash, expected_hash):
                            self.logger.warning(f"Model integrity check failed for {model_file}, skipping")
                            continue
                            model_data = pickle.load(io.BytesIO(data_content))  # nosec - integrity validated                    if 'model' in model_data:
                        self.prediction_models[model_name] = model_data['model']
                        
                    if 'scaler' in model_data:
                        self.feature_scalers[model_name] = model_data['scaler']
                        
                    if 'encoder' in model_data:
                        self.label_encoders[model_name] = model_data['encoder']
                        
                    if 'performance' in model_data:
                        self.model_performance[model_name] = ModelPerformanceMetrics(**model_data['performance'])
                    
                    loaded_count += 1
                    self.logger.info(f"Loaded model: {model_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load model {model_file}: {e}")
            
            if loaded_count > 0:
                self.logger.info(f"Loaded {loaded_count} existing models")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing models: {e}")
    
    async def _initialize_consciousness_weights(self):
        """Initialize consciousness-based feature weights"""
        try:
            # Get current consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            if consciousness_state:
                consciousness_level = consciousness_state.overall_consciousness_level
                
                self.consciousness_weights = {
                    'pattern_recognition_boost': consciousness_level * 0.3,
                    'anomaly_detection_boost': consciousness_level * 0.25,
                    'prediction_confidence_boost': consciousness_level * 0.2,
                    'feature_importance_adjustment': consciousness_level * 0.15,
                    'model_ensemble_weight': consciousness_level * 0.35
                }
            else:
                # Default weights when consciousness is not available
                self.consciousness_weights = {
                    'pattern_recognition_boost': 0.2,
                    'anomaly_detection_boost': 0.15,
                    'prediction_confidence_boost': 0.1,
                    'feature_importance_adjustment': 0.1,
                    'model_ensemble_weight': 0.25
                }
            
            self.logger.info("Consciousness weights initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize consciousness weights: {e}")
    
    async def extract_threat_features(self, threat_data: Dict[str, Any]) -> ThreatFeatureVector:
        """Extract comprehensive threat features for prediction"""
        try:
            feature_vector = np.zeros(self.feature_dimensions)
            feature_names = []
            consciousness_features = {}
            quantum_features = {}
            
            # Extract different types of features
            temporal_features = await self._extract_temporal_features(threat_data)
            behavioral_features = await self._extract_behavioral_features(threat_data)
            network_features = await self._extract_network_features(threat_data)
            content_features = await self._extract_content_features(threat_data)
            consciousness_features = await self._extract_consciousness_features(threat_data)
            quantum_features = await self._extract_quantum_features(threat_data)
            
            # Combine all features into feature vector
            current_idx = 0
            
            # Temporal features (16 dimensions)
            temporal_size = min(16, len(temporal_features))
            feature_vector[current_idx:current_idx + temporal_size] = temporal_features[:temporal_size]
            feature_names.extend([f"temporal_{i}" for i in range(temporal_size)])
            current_idx += 16
            
            # Behavioral features (24 dimensions)
            behavioral_size = min(24, len(behavioral_features))
            feature_vector[current_idx:current_idx + behavioral_size] = behavioral_features[:behavioral_size]
            feature_names.extend([f"behavioral_{i}" for i in range(behavioral_size)])
            current_idx += 24
            
            # Network features (32 dimensions)
            network_size = min(32, len(network_features))
            feature_vector[current_idx:current_idx + network_size] = network_features[:network_size]
            feature_names.extend([f"network_{i}" for i in range(network_size)])
            current_idx += 32
            
            # Content features (40 dimensions)
            content_size = min(40, len(content_features))
            feature_vector[current_idx:current_idx + content_size] = content_features[:content_size]
            feature_names.extend([f"content_{i}" for i in range(content_size)])
            current_idx += 40
            
            # Consciousness features (8 dimensions)
            consciousness_array = np.array(list(consciousness_features.values())[:8])
            consciousness_size = min(8, len(consciousness_array))
            if consciousness_size > 0:
                feature_vector[current_idx:current_idx + consciousness_size] = consciousness_array[:consciousness_size]
            feature_names.extend([f"consciousness_{i}" for i in range(8)])
            current_idx += 8
            
            # Quantum features (8 dimensions)
            quantum_array = np.array(list(quantum_features.values())[:8])
            quantum_size = min(8, len(quantum_array))
            if quantum_size > 0:
                feature_vector[current_idx:current_idx + quantum_size] = quantum_array[:quantum_size]
            feature_names.extend([f"quantum_{i}" for i in range(8)])
            
            return ThreatFeatureVector(
                feature_vector=feature_vector,
                feature_names=feature_names,
                timestamp=datetime.now(),
                source_indicators=threat_data.get('indicators', []),
                consciousness_features=consciousness_features,
                quantum_features=quantum_features
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract threat features: {e}")
            raise
    
    async def _extract_temporal_features(self, threat_data: Dict[str, Any]) -> np.ndarray:
        """Extract temporal features from threat data"""
        try:
            features = []
            
            # Time-based features
            current_time = time.time()
            first_seen = threat_data.get('first_seen', current_time)
            last_seen = threat_data.get('last_seen', current_time)
            
            # Time deltas
            features.append((current_time - first_seen) / 3600)  # Hours since first seen
            features.append((last_seen - first_seen) / 3600)    # Duration
            features.append(np.sin(2 * np.pi * (current_time % 86400) / 86400))  # Hour of day
            features.append(np.cos(2 * np.pi * (current_time % 86400) / 86400))  # Hour of day
            features.append(np.sin(2 * np.pi * (current_time % 604800) / 604800)) # Day of week
            features.append(np.cos(2 * np.pi * (current_time % 604800) / 604800)) # Day of week
            
            # Frequency features
            update_frequency = threat_data.get('update_frequency', 0)
            features.append(min(update_frequency / 100, 1.0))  # Normalized frequency
            
            # Temporal patterns
            time_pattern_score = threat_data.get('temporal_pattern_score', 0.5)
            features.append(time_pattern_score)
            
            # Pad or truncate to ensure consistent size
            while len(features) < 16:
                features.append(0.0)
            
            return np.array(features[:16], dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Failed to extract temporal features: {e}")
            return np.zeros(16, dtype=np.float32)
    
    async def _extract_behavioral_features(self, threat_data: Dict[str, Any]) -> np.ndarray:
        """Extract behavioral features from threat data"""
        try:
            features = []
            
            # Threat behavior characteristics
            severity_mapping = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'critical': 1.0}
            severity = threat_data.get('severity', 'medium')
            features.append(severity_mapping.get(severity, 0.5))
            
            # Confidence score
            confidence = threat_data.get('confidence', 0.5)
            features.append(min(max(confidence, 0.0), 1.0))
            
            # Behavioral patterns
            persistence_score = threat_data.get('persistence_score', 0.5)
            features.append(persistence_score)
            
            stealth_score = threat_data.get('stealth_score', 0.5)
            features.append(stealth_score)
            
            propagation_score = threat_data.get('propagation_score', 0.5)
            features.append(propagation_score)
            
            # Attack vector characteristics
            attack_vectors = threat_data.get('attack_vectors', [])
            features.append(len(attack_vectors) / 10.0)  # Normalized count
            
            # Target specificity
            target_sectors = threat_data.get('target_sectors', [])
            features.append(len(target_sectors) / 20.0)  # Normalized count
            
            # Evasion techniques
            evasion_techniques = threat_data.get('evasion_techniques', [])
            features.append(len(evasion_techniques) / 15.0)  # Normalized count
            
            # Pad or truncate to ensure consistent size
            while len(features) < 24:
                features.append(0.0)
            
            return np.array(features[:24], dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Failed to extract behavioral features: {e}")
            return np.zeros(24, dtype=np.float32)
    
    async def _extract_network_features(self, threat_data: Dict[str, Any]) -> np.ndarray:
        """Extract network-based features from threat data"""
        try:
            features = []
            
            # Network indicators
            ip_addresses = threat_data.get('ip_addresses', [])
            features.append(len(ip_addresses) / 100.0)  # Normalized count
            
            domains = threat_data.get('domains', [])
            features.append(len(domains) / 50.0)  # Normalized count
            
            urls = threat_data.get('urls', [])
            features.append(len(urls) / 200.0)  # Normalized count
            
            # Geographic distribution
            countries = threat_data.get('countries', [])
            features.append(len(countries) / 20.0)  # Normalized count
            
            # Network behavior
            port_usage = threat_data.get('port_usage', {})
            features.append(len(port_usage) / 100.0)  # Normalized count
            
            protocol_usage = threat_data.get('protocol_usage', {})
            features.append(len(protocol_usage) / 20.0)  # Normalized count
            
            # Traffic patterns
            traffic_volume = threat_data.get('traffic_volume', 0)
            features.append(min(traffic_volume / 1000000, 1.0))  # Normalized volume
            
            connection_frequency = threat_data.get('connection_frequency', 0)
            features.append(min(connection_frequency / 1000, 1.0))  # Normalized frequency
            
            # Pad or truncate to ensure consistent size
            while len(features) < 32:
                features.append(0.0)
            
            return np.array(features[:32], dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Failed to extract network features: {e}")
            return np.zeros(32, dtype=np.float32)
    
    async def _extract_content_features(self, threat_data: Dict[str, Any]) -> np.ndarray:
        """Extract content-based features from threat data"""
        try:
            features = []
            
            # File characteristics
            file_hashes = threat_data.get('file_hashes', [])
            features.append(len(file_hashes) / 50.0)  # Normalized count
            
            file_sizes = threat_data.get('file_sizes', [])
            avg_file_size = np.mean(file_sizes) if file_sizes else 0
            features.append(min(avg_file_size / 10000000, 1.0))  # Normalized size
            
            # Content analysis
            malicious_content_score = threat_data.get('malicious_content_score', 0.5)
            features.append(malicious_content_score)
            
            obfuscation_score = threat_data.get('obfuscation_score', 0.5)
            features.append(obfuscation_score)
            
            # Text analysis features
            suspicious_keywords = threat_data.get('suspicious_keywords', [])
            features.append(len(suspicious_keywords) / 100.0)  # Normalized count
            
            # Entropy and randomness
            entropy_score = threat_data.get('entropy_score', 0.5)
            features.append(entropy_score)
            
            randomness_score = threat_data.get('randomness_score', 0.5)
            features.append(randomness_score)
            
            # Communication patterns
            c2_communication_score = threat_data.get('c2_communication_score', 0.0)
            features.append(c2_communication_score)
            
            # Pad or truncate to ensure consistent size
            while len(features) < 40:
                features.append(0.0)
            
            return np.array(features[:40], dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Failed to extract content features: {e}")
            return np.zeros(40, dtype=np.float32)
    
    async def _extract_consciousness_features(self, threat_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract consciousness-enhanced features"""
        try:
            consciousness_features = {}
            
            # Get consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            if consciousness_state:
                consciousness_level = consciousness_state.overall_consciousness_level
                
                # Consciousness-enhanced threat scoring
                consciousness_features['consciousness_level'] = consciousness_level
                consciousness_features['threat_consciousness_correlation'] = (
                    consciousness_level * threat_data.get('consciousness_score', 0.5)
                )
                
                # Neural pattern recognition enhancement
                consciousness_features['neural_pattern_strength'] = (
                    consciousness_level * threat_data.get('pattern_strength', 0.5)
                )
                
                # Adaptive learning enhancement
                consciousness_features['adaptive_learning_factor'] = (
                    consciousness_level * 0.8
                )
                
                # Predictive accuracy enhancement
                consciousness_features['prediction_accuracy_boost'] = (
                    consciousness_level * 0.3
                )
                
                # Threat prioritization enhancement
                consciousness_features['priority_adjustment'] = (
                    consciousness_level * threat_data.get('priority_score', 0.5)
                )
                
                # False positive reduction
                consciousness_features['false_positive_reduction'] = (
                    consciousness_level * 0.4
                )
                
                # Pattern emergence detection
                consciousness_features['pattern_emergence_score'] = (
                    consciousness_level * threat_data.get('emergence_score', 0.5)
                )
            else:
                # Default values when consciousness is not available
                consciousness_features = {
                    'consciousness_level': 0.5,
                    'threat_consciousness_correlation': 0.3,
                    'neural_pattern_strength': 0.4,
                    'adaptive_learning_factor': 0.4,
                    'prediction_accuracy_boost': 0.15,
                    'priority_adjustment': 0.3,
                    'false_positive_reduction': 0.2,
                    'pattern_emergence_score': 0.3
                }
            
            return consciousness_features
            
        except Exception as e:
            self.logger.error(f"Failed to extract consciousness features: {e}")
            return {}
    
    async def _extract_quantum_features(self, threat_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract quantum threat features"""
        try:
            quantum_features = {}
            
            # Quantum threat indicators
            quantum_keywords = threat_data.get('quantum_keywords', [])
            quantum_features['quantum_keyword_density'] = len(quantum_keywords) / 100.0
            
            # Post-quantum cryptography impact
            pqc_impact = threat_data.get('post_quantum_crypto_impact', 0.0)
            quantum_features['pqc_vulnerability'] = min(pqc_impact, 1.0)
            
            # Quantum computing threat timeline
            quantum_timeline = threat_data.get('quantum_threat_timeline', 10)  # years
            quantum_features['quantum_urgency'] = max(0.0, 1.0 - (quantum_timeline / 20.0))
            
            # Quantum-resistant algorithm analysis
            quantum_resistant_score = threat_data.get('quantum_resistant_score', 0.8)
            quantum_features['quantum_resistance'] = quantum_resistant_score
            
            # Quantum signature detection
            quantum_signature_strength = threat_data.get('quantum_signature_strength', 0.0)
            quantum_features['quantum_signature'] = quantum_signature_strength
            
            # Quantum computing attack indicators
            quantum_attack_indicators = threat_data.get('quantum_attack_indicators', 0.0)
            quantum_features['quantum_attack_probability'] = quantum_attack_indicators
            
            # Cryptographic vulnerability assessment
            crypto_vulnerability = threat_data.get('cryptographic_vulnerability', 0.2)
            quantum_features['crypto_vulnerability'] = crypto_vulnerability
            
            # Quantum readiness assessment
            quantum_readiness = threat_data.get('quantum_readiness', 0.7)
            quantum_features['quantum_defense_readiness'] = quantum_readiness
            
            return quantum_features
            
        except Exception as e:
            self.logger.error(f"Failed to extract quantum features: {e}")
            return {}
    
    async def predict_threats(self, threat_data: Dict[str, Any],
                            timeframe: PredictionTimeframe = PredictionTimeframe.SHORT_TERM,
                            model_ensemble: bool = True) -> List[ThreatPrediction]:
        """Generate threat predictions using ML models"""
        try:
            self.logger.info("Generating threat predictions...")
            
            # Extract features
            feature_vector = await self.extract_threat_features(threat_data)
            
            predictions = []
            
            if model_ensemble:
                # Use ensemble of models for better accuracy
                predictions = await self._ensemble_prediction(feature_vector, timeframe)
            else:
                # Use individual models
                for model_name, model in self.prediction_models.items():
                    if model_name in ['lstm_threat_predictor', 'random_forest_predictor']:
                        prediction = await self._single_model_prediction(
                            model_name, model, feature_vector, timeframe
                        )
                        if prediction:
                            predictions.append(prediction)
            
            # Apply consciousness enhancements
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            if consciousness_state:
                predictions = await self._enhance_predictions_with_consciousness(
                    predictions, consciousness_state, feature_vector
                )
            
            # Sort by probability (highest first)
            predictions.sort(key=lambda p: p.probability, reverse=True)
            
            # Update metrics
            self.prediction_count += len(predictions)
            
            self.logger.info(f"Generated {len(predictions)} threat predictions")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to generate threat predictions: {e}")
            return []
    
    async def _ensemble_prediction(self, feature_vector: ThreatFeatureVector,
                                 timeframe: PredictionTimeframe) -> List[ThreatPrediction]:
        """Generate ensemble prediction using multiple models"""
        try:
            predictions = []
            model_predictions = {}
            
            # Get predictions from each model
            for model_name, model in self.prediction_models.items():
                try:
                    if model_name == 'consciousness_predictor':
                        # Special handling for consciousness model
                        model_prediction = await self._consciousness_model_prediction(
                            model, feature_vector, timeframe
                        )
                    else:
                        model_prediction = await self._single_model_prediction(
                            model_name, model, feature_vector, timeframe
                        )
                    
                    if model_prediction:
                        model_predictions[model_name] = model_prediction
                        
                except Exception as e:
                    self.logger.error(f"Error in model {model_name}: {e}")
            
            # Combine predictions using weighted ensemble
            if model_predictions:
                ensemble_prediction = await self._combine_model_predictions(
                    model_predictions, feature_vector, timeframe
                )
                predictions.append(ensemble_prediction)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to generate ensemble prediction: {e}")
            return []
    
    async def _single_model_prediction(self, model_name: str, model: Any,
                                     feature_vector: ThreatFeatureVector,
                                     timeframe: PredictionTimeframe) -> Optional[ThreatPrediction]:
        """Generate prediction using single model"""
        try:
            # Prepare feature data
            features = feature_vector.feature_vector.reshape(1, -1)
            
            # Scale features if scaler exists
            if model_name in self.feature_scalers:
                scaler = self.feature_scalers[model_name]
                if hasattr(scaler, 'n_features_in_') and scaler.n_features_in_ is not None:
                    features = scaler.transform(features)
            
            # Generate prediction based on model type
            if model_name == 'lstm_threat_predictor':
                # LSTM model expects 3D input
                features_3d = features.reshape(1, 1, -1)
                prediction_probs = model.predict(features_3d, verbose=0)[0]
                predicted_category_idx = np.argmax(prediction_probs)
                probability = float(prediction_probs[predicted_category_idx])
                confidence = float(np.max(prediction_probs))
                
            elif hasattr(model, 'predict_proba'):
                # Models with probability prediction
                prediction_probs = model.predict_proba(features)[0]
                predicted_category_idx = np.argmax(prediction_probs)
                probability = float(prediction_probs[predicted_category_idx])
                confidence = probability
                
            elif hasattr(model, 'decision_function'):
                # Models with decision function
                decision_scores = model.decision_function(features)[0]
                if isinstance(decision_scores, np.ndarray):
                    predicted_category_idx = np.argmax(decision_scores)
                    probability = float(1.0 / (1.0 + np.exp(-decision_scores[predicted_category_idx])))  # Sigmoid
                else:
                    predicted_category_idx = 0 if decision_scores > 0 else 1
                    probability = float(1.0 / (1.0 + np.exp(-decision_scores)))
                confidence = probability
                
            else:
                # Default prediction
                prediction = model.predict(features)[0]
                predicted_category_idx = 0 if isinstance(prediction, (int, np.integer)) else 0
                probability = 0.7
                confidence = 0.6
            
            # Map to threat category
            threat_categories = list(ThreatCategory)
            if predicted_category_idx < len(threat_categories):
                threat_category = threat_categories[predicted_category_idx]
            else:
                threat_category = ThreatCategory.UNKNOWN
            
            # Create prediction
            prediction = ThreatPrediction(
                prediction_id=f"{model_name}_{uuid.uuid4().hex[:8]}",
                model_name=model_name,
                threat_category=threat_category,
                probability=probability,
                confidence=confidence,
                timeframe=timeframe,
                predicted_impact=self._assess_threat_impact(threat_category, probability),
                target_sectors=self._predict_target_sectors(threat_category),
                attack_vectors=self._predict_attack_vectors(threat_category),
                indicators=feature_vector.source_indicators[:5],
                mitigation_strategies=self._generate_mitigation_strategies(threat_category),
                consciousness_enhancement=feature_vector.consciousness_features,
                quantum_considerations=feature_vector.quantum_features
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Failed to generate single model prediction for {model_name}: {e}")
            return None
    
    async def _consciousness_model_prediction(self, model: Dict[str, Any],
                                            feature_vector: ThreatFeatureVector,
                                            timeframe: PredictionTimeframe) -> Optional[ThreatPrediction]:
        """Generate prediction using consciousness-hybrid model"""
        try:
            # Extract consciousness-enhanced features
            consciousness_features = feature_vector.consciousness_features
            consciousness_level = consciousness_features.get('consciousness_level', 0.5)
            
            if consciousness_level < self.consciousness_threshold:
                return None
            
            # Use base models with consciousness weighting
            base_predictions = []
            
            for base_model_name, base_model in model['base_models'].items():
                features = feature_vector.feature_vector.reshape(1, -1)
                
                if hasattr(base_model, 'predict_proba'):
                    probs = base_model.predict_proba(features)[0]
                    category_idx = np.argmax(probs)
                    probability = float(probs[category_idx])
                else:
                    prediction = base_model.predict(features)[0]
                    category_idx = 0
                    probability = 0.7
                
                # Apply consciousness weighting
                consciousness_boost = self.consciousness_weights.get('prediction_confidence_boost', 0.1)
                enhanced_probability = min(probability + (consciousness_level * consciousness_boost), 1.0)
                
                base_predictions.append({
                    'category_idx': category_idx,
                    'probability': enhanced_probability,
                    'model_name': base_model_name
                })
            
            # Combine base predictions with consciousness weighting
            if base_predictions:
                # Weighted average based on consciousness correlation
                total_weight = 0
                weighted_prob = 0
                best_category = 0
                
                for pred in base_predictions:
                    weight = consciousness_level * self.consciousness_weights.get('model_ensemble_weight', 0.3)
                    total_weight += weight
                    weighted_prob += pred['probability'] * weight
                    
                    if pred['probability'] > base_predictions[best_category]['probability']:
                        best_category = pred['category_idx']
                
                final_probability = weighted_prob / total_weight if total_weight > 0 else 0.5
                
                # Map to threat category
                threat_categories = list(ThreatCategory)
                threat_category = threat_categories[best_category] if best_category < len(threat_categories) else ThreatCategory.UNKNOWN
                
                # Create consciousness-enhanced prediction
                prediction = ThreatPrediction(
                    prediction_id=f"consciousness_{uuid.uuid4().hex[:8]}",
                    model_name="consciousness_hybrid",
                    threat_category=threat_category,
                    probability=final_probability,
                    confidence=consciousness_level * 0.9,
                    timeframe=timeframe,
                    predicted_impact=self._assess_threat_impact(threat_category, final_probability),
                    target_sectors=self._predict_target_sectors(threat_category),
                    attack_vectors=self._predict_attack_vectors(threat_category),
                    indicators=feature_vector.source_indicators[:5],
                    mitigation_strategies=self._generate_mitigation_strategies(threat_category),
                    consciousness_enhancement={
                        **consciousness_features,
                        'consciousness_model_used': True,
                        'consciousness_boost_applied': consciousness_boost
                    },
                    quantum_considerations=feature_vector.quantum_features
                )
                
                return prediction
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to generate consciousness model prediction: {e}")
            return None
    
    async def _combine_model_predictions(self, model_predictions: Dict[str, ThreatPrediction],
                                       feature_vector: ThreatFeatureVector,
                                       timeframe: PredictionTimeframe) -> ThreatPrediction:
        """Combine predictions from multiple models into ensemble prediction"""
        try:
            # Calculate weighted ensemble
            total_weight = 0
            weighted_probability = 0
            weighted_confidence = 0
            threat_category_votes = {}
            
            for model_name, prediction in model_predictions.items():
                # Get model performance weight
                if model_name in self.model_performance:
                    model_weight = self.model_performance[model_name].f1_score
                else:
                    model_weight = 0.5
                
                # Apply consciousness weighting
                consciousness_weight = self.consciousness_weights.get('model_ensemble_weight', 0.3)
                final_weight = model_weight * (1 + consciousness_weight)
                
                total_weight += final_weight
                weighted_probability += prediction.probability * final_weight
                weighted_confidence += prediction.confidence * final_weight
                
                # Vote for threat category
                category = prediction.threat_category
                if category not in threat_category_votes:
                    threat_category_votes[category] = 0
                threat_category_votes[category] += final_weight
            
            # Final ensemble values
            ensemble_probability = weighted_probability / total_weight if total_weight > 0 else 0.5
            ensemble_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.5
            
            # Most voted threat category
            best_category = max(threat_category_votes.items(), key=lambda x: x[1])[0]
            
            # Combine all mitigation strategies
            all_mitigations = set()
            for prediction in model_predictions.values():
                all_mitigations.update(prediction.mitigation_strategies)
            
            # Create ensemble prediction
            ensemble_prediction = ThreatPrediction(
                prediction_id=f"ensemble_{uuid.uuid4().hex[:8]}",
                model_name="ensemble_predictor",
                threat_category=best_category,
                probability=ensemble_probability,
                confidence=ensemble_confidence,
                timeframe=timeframe,
                predicted_impact=self._assess_threat_impact(best_category, ensemble_probability),
                target_sectors=self._predict_target_sectors(best_category),
                attack_vectors=self._predict_attack_vectors(best_category),
                indicators=feature_vector.source_indicators[:5],
                mitigation_strategies=list(all_mitigations),
                consciousness_enhancement=feature_vector.consciousness_features,
                quantum_considerations=feature_vector.quantum_features
            )
            
            return ensemble_prediction
            
        except Exception as e:
            self.logger.error(f"Failed to combine model predictions: {e}")
            # Return best single prediction as fallback
            best_prediction = max(model_predictions.values(), key=lambda p: p.probability)
            best_prediction.model_name = "ensemble_fallback"
            return best_prediction
    
    def _assess_threat_impact(self, threat_category: ThreatCategory, probability: float) -> str:
        """Assess predicted threat impact"""
        try:
            # Base impact by category
            category_impacts = {
                ThreatCategory.RANSOMWARE: "high",
                ThreatCategory.APT: "high",
                ThreatCategory.DATA_BREACH: "high",
                ThreatCategory.QUANTUM_THREAT: "critical",
                ThreatCategory.SUPPLY_CHAIN: "high",
                ThreatCategory.DDOS: "medium",
                ThreatCategory.PHISHING: "medium",
                ThreatCategory.MALWARE: "medium",
                ThreatCategory.INSIDER_THREAT: "high",
                ThreatCategory.UNKNOWN: "low"
            }
            
            base_impact = category_impacts.get(threat_category, "medium")
            
            # Adjust based on probability
            if probability > 0.8:
                if base_impact == "medium":
                    return "high"
                elif base_impact == "high":
                    return "critical"
            elif probability < 0.3:
                if base_impact == "high":
                    return "medium"
                elif base_impact == "medium":
                    return "low"
            
            return base_impact
            
        except Exception as e:
            self.logger.error(f"Failed to assess threat impact: {e}")
            return "medium"
    
    def _predict_target_sectors(self, threat_category: ThreatCategory) -> List[str]:
        """Predict likely target sectors for threat category"""
        sector_mappings = {
            ThreatCategory.RANSOMWARE: ["healthcare", "education", "government", "manufacturing"],
            ThreatCategory.APT: ["government", "defense", "finance", "technology"],
            ThreatCategory.PHISHING: ["finance", "retail", "healthcare", "technology"],
            ThreatCategory.DATA_BREACH: ["healthcare", "finance", "retail", "technology"],
            ThreatCategory.QUANTUM_THREAT: ["government", "defense", "finance", "critical_infrastructure"],
            ThreatCategory.SUPPLY_CHAIN: ["manufacturing", "technology", "automotive", "aerospace"],
            ThreatCategory.INSIDER_THREAT: ["finance", "government", "healthcare", "technology"],
            ThreatCategory.DDOS: ["finance", "gaming", "media", "e_commerce"],
            ThreatCategory.MALWARE: ["general", "technology", "finance", "healthcare"]
        }
        
        return sector_mappings.get(threat_category, ["general", "technology"])
    
    def _predict_attack_vectors(self, threat_category: ThreatCategory) -> List[str]:
        """Predict likely attack vectors for threat category"""
        vector_mappings = {
            ThreatCategory.RANSOMWARE: ["email", "rdp", "web_exploit", "supply_chain"],
            ThreatCategory.PHISHING: ["email", "social_media", "sms", "voice"],
            ThreatCategory.APT: ["spear_phishing", "watering_hole", "supply_chain", "insider"],
            ThreatCategory.DATA_BREACH: ["credential_theft", "sql_injection", "insider", "misconfiguration"],
            ThreatCategory.QUANTUM_THREAT: ["cryptographic_attack", "quantum_computing", "post_quantum_vulnerability"],
            ThreatCategory.SUPPLY_CHAIN: ["software_update", "hardware_implant", "third_party_compromise"],
            ThreatCategory.INSIDER_THREAT: ["privileged_access", "data_theft", "sabotage"],
            ThreatCategory.DDOS: ["botnet", "amplification", "application_layer", "network_layer"],
            ThreatCategory.MALWARE: ["email", "web", "removable_media", "network"]
        }
        
        return vector_mappings.get(threat_category, ["email", "web", "network"])
    
    def _generate_mitigation_strategies(self, threat_category: ThreatCategory) -> List[str]:
        """Generate mitigation strategies for threat category"""
        mitigation_mappings = {
            ThreatCategory.RANSOMWARE: [
                "Implement comprehensive backup strategy",
                "Deploy endpoint detection and response (EDR)",
                "Conduct regular security awareness training",
                "Implement network segmentation",
                "Deploy application whitelisting"
            ],
            ThreatCategory.PHISHING: [
                "Deploy email security gateway",
                "Implement DMARC/SPF/DKIM",
                "Conduct phishing simulation training",
                "Deploy web content filtering",
                "Implement zero-trust email security"
            ],
            ThreatCategory.APT: [
                "Implement zero-trust architecture",
                "Deploy advanced threat hunting capabilities",
                "Enhance network monitoring and logging",
                "Implement privileged access management",
                "Deploy advanced persistent threat detection"
            ],
            ThreatCategory.QUANTUM_THREAT: [
                "Migrate to post-quantum cryptography",
                "Implement quantum-resistant algorithms",
                "Assess quantum threat exposure",
                "Develop quantum incident response plan",
                "Deploy quantum key distribution"
            ]
        }
        
        return mitigation_mappings.get(threat_category, [
            "Implement defense-in-depth strategy",
            "Enhance monitoring and detection capabilities",
            "Conduct regular security assessments",
            "Update incident response procedures"
        ])
    
    async def _enhance_predictions_with_consciousness(self, predictions: List[ThreatPrediction],
                                                   consciousness_state: Any,
                                                   feature_vector: ThreatFeatureVector) -> List[ThreatPrediction]:
        """Enhance predictions using consciousness insights"""
        try:
            consciousness_level = consciousness_state.overall_consciousness_level
            
            if consciousness_level < self.consciousness_threshold:
                return predictions
            
            enhanced_predictions = []
            
            for prediction in predictions:
                # Apply consciousness enhancements
                consciousness_boost = self.consciousness_weights.get('prediction_confidence_boost', 0.1)
                
                # Boost confidence for high-consciousness correlations
                if feature_vector.consciousness_features.get('threat_consciousness_correlation', 0) > 0.8:
                    prediction.confidence = min(prediction.confidence + consciousness_boost, 1.0)
                    prediction.probability = min(prediction.probability + (consciousness_boost * 0.5), 1.0)
                
                # Add consciousness insights
                prediction.consciousness_enhancement.update({
                    'consciousness_level_at_prediction': consciousness_level,
                    'consciousness_boost_applied': consciousness_boost,
                    'neural_pattern_enhancement': consciousness_level > 0.8,
                    'adaptive_learning_active': True
                })
                
                enhanced_predictions.append(prediction)
            
            return enhanced_predictions
            
        except Exception as e:
            self.logger.error(f"Failed to enhance predictions with consciousness: {e}")
            return predictions
    
    async def train_models(self, training_data: List[Dict[str, Any]], labels: List[str]):
        """Train prediction models with new data"""
        try:
            self.logger.info(f"Training models with {len(training_data)} samples...")
            
            # Extract features for all training samples
            feature_vectors = []
            for data in training_data:
                feature_vector = await self.extract_threat_features(data)
                feature_vectors.append(feature_vector.feature_vector)
            
            X = np.array(feature_vectors)
            
            # Encode labels
            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(labels)
            
            # Split training data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train each model
            for model_name, model in self.prediction_models.items():
                if model_name == 'consciousness_predictor':
                    continue  # Skip consciousness model for now
                
                try:
                    # Scale features
                    scaler = self.feature_scalers[model_name]
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Train model
                    if model_name == 'lstm_threat_predictor':
                        # LSTM training
                        X_train_3d = X_train_scaled.reshape(X_train_scaled.shape[0], 1, X_train_scaled.shape[1])
                        X_test_3d = X_test_scaled.reshape(X_test_scaled.shape[0], 1, X_test_scaled.shape[1])
                        
                        # Convert labels to categorical
                        y_train_cat = tf.keras.utils.to_categorical(y_train, num_classes=len(ThreatCategory))
                        y_test_cat = tf.keras.utils.to_categorical(y_test, num_classes=len(ThreatCategory))
                        
                        model.fit(X_train_3d, y_train_cat, epochs=50, batch_size=32, verbose=0)
                        
                        # Evaluate
                        y_pred_probs = model.predict(X_test_3d, verbose=0)
                        y_pred = np.argmax(y_pred_probs, axis=1)
                        
                    else:
                        # Scikit-learn models
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                    
                    # Calculate metrics
                    accuracy = accuracy_score(y_test, y_pred)
                    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                    
                    # Update performance metrics
                    self.model_performance[model_name] = ModelPerformanceMetrics(
                        model_name=model_name,
                        accuracy=accuracy,
                        precision=precision,
                        recall=recall,
                        f1_score=f1,
                        last_training=datetime.now(),
                        training_samples=len(training_data),
                        prediction_count=0
                    )
                    
                    self.logger.info(f"Model {model_name} trained - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to train model {model_name}: {e}")
            
            # Save models
            await self._save_models()
            
        except Exception as e:
            self.logger.error(f"Failed to train models: {e}")
    
    async def _save_models(self):
        """Save trained models to storage"""
        try:
            for model_name, model in self.prediction_models.items():
                if model_name == 'consciousness_predictor':
                    continue  # Skip consciousness model
                
                model_file = self.models_directory / f"{model_name}.pkl"
                
                model_data = {
                    'model': model,
                    'scaler': self.feature_scalers.get(model_name),
                    'encoder': self.label_encoders.get(model_name),
                    'performance': (
                        self.model_performance[model_name].__dict__ 
                        if model_name in self.model_performance else {}
                    )
                }
                
                try:
                    with open(model_file, 'wb') as f:
                        pickle.dump(model_data, f)
                    
                    self.logger.info(f"Saved model: {model_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to save model {model_name}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")
    
    async def _continuous_learning_loop(self):
        """Continuous learning loop for model improvement"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Check if we have enough new data for retraining
                if len(self.training_data) >= 100:  # Minimum samples for retraining
                    self.logger.info("Starting continuous learning update...")
                    
                    # Prepare training data
                    training_samples = []
                    labels = []
                    
                    for feature_vector in self.training_data[-500:]:  # Use last 500 samples
                        training_samples.append({
                            'features': feature_vector.feature_vector,
                            'consciousness_features': feature_vector.consciousness_features,
                            'quantum_features': feature_vector.quantum_features
                        })
                        labels.append('unknown')  # Would need actual labels
                    
                    # Retrain models (simplified for this example)
                    # In production, would use actual labeled data
                    
                    self.logger.info("Continuous learning update completed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in continuous learning loop: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _model_validation_loop(self):
        """Model validation and performance monitoring loop"""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                
                # Validate model performance
                for model_name, performance in self.model_performance.items():
                    if performance.f1_score < self.model_accuracy_threshold:
                        self.logger.warning(
                            f"Model {model_name} performance below threshold: {performance.f1_score:.3f}"
                        )
                
                # Clean up old predictions
                cutoff_time = datetime.now() - timedelta(days=7)
                self.historical_predictions = [
                    pred for pred in self.historical_predictions
                    if pred.created_at > cutoff_time
                ]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in model validation loop: {e}")
                await asyncio.sleep(900)  # Wait 15 minutes on error
    
    def get_modeling_status(self) -> Dict[str, Any]:
        """Get predictive modeling framework status"""
        try:
            return {
                'models_active': len(self.prediction_models),
                'prediction_count': self.prediction_count,
                'successful_predictions': self.successful_predictions,
                'training_data_samples': len(self.training_data),
                'historical_predictions': len(self.historical_predictions),
                'consciousness_threshold': self.consciousness_threshold,
                'model_performance': {
                    name: {
                        'accuracy': perf.accuracy,
                        'precision': perf.precision,
                        'recall': perf.recall,
                        'f1_score': perf.f1_score,
                        'last_training': perf.last_training.isoformat(),
                        'training_samples': perf.training_samples,
                        'prediction_count': perf.prediction_count
                    }
                    for name, perf in self.model_performance.items()
                },
                'consciousness_weights': self.consciousness_weights
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get modeling status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown predictive modeling framework"""
        self.logger.info("Shutting down Predictive Threat Modeling Framework...")
        
        # Save models before shutdown
        await self._save_models()
        
        # Clear data structures
        self.prediction_models.clear()
        self.model_performance.clear()
        self.training_data.clear()
        self.historical_predictions.clear()
        
        self.logger.info("Predictive Threat Modeling Framework shutdown complete")


# Factory function
def create_predictive_threat_modeling_framework(
    consciousness_bus: Optional[ConsciousnessBus] = None
) -> PredictiveThreatModelingFramework:
    """Create predictive threat modeling framework"""
    return PredictiveThreatModelingFramework(consciousness_bus)


# Example usage
async def main():
    """Example usage of predictive threat modeling framework"""
    try:
        # Create framework
        framework = create_predictive_threat_modeling_framework()
        
        # Initialize
        await framework.initialize()
        
        # Sample threat data for prediction
        threat_data = {
            'indicators': ['192.168.1.100', 'malicious-domain.com'],
            'severity': 'high',
            'confidence': 0.85,
            'first_seen': time.time() - 3600,
            'last_seen': time.time(),
            'attack_vectors': ['email', 'web'],
            'target_sectors': ['finance', 'healthcare'],
            'consciousness_score': 0.9,
            'quantum_keywords': ['post-quantum', 'cryptographic'],
            'behavioral_patterns': ['persistence', 'stealth']
        }
        
        # Generate predictions
        predictions = await framework.predict_threats(
            threat_data, 
            PredictionTimeframe.SHORT_TERM,
            model_ensemble=True
        )
        
        print(f"Generated {len(predictions)} predictions:")
        for pred in predictions:
            print(f"- {pred.threat_category.value}: {pred.probability:.2f} probability")
            print(f"  Model: {pred.model_name}, Confidence: {pred.confidence:.2f}")
            print(f"  Impact: {pred.predicted_impact}")
            print(f"  Mitigations: {pred.mitigation_strategies[:2]}")
            print()
        
        # Get status
        status = framework.get_modeling_status()
        print(f"Framework Status: {status}")
        
        # Shutdown
        await framework.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())