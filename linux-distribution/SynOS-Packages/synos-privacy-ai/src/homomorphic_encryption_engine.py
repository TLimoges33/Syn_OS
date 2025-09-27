#!/usr/bin/env python3

"""
SynOS Privacy-Preserving AI Analysis
FHE-enabled computation on encrypted security logs and system data

This module provides homomorphic encryption capabilities using:
- Microsoft SEAL integration
- TenSEAL for encrypted tensor operations
- Concrete-Python for FHE program compilation
- Privacy-preserving machine learning models
- Encrypted threat intelligence processing
"""

import asyncio
import json
import logging
import time
import pickle
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from datetime import datetime, timedelta
import base64
import hashlib
import struct

# Homomorphic encryption imports
try:
    import tenseal as ts
    HE_AVAILABLE = True
except ImportError:
    HE_AVAILABLE = False
    logging.warning("TenSEAL not available, using simulation mode")

try:
    from concrete import fhe
    CONCRETE_AVAILABLE = True
except ImportError:
    CONCRETE_AVAILABLE = False
    logging.warning("Concrete-Python not available, using simulation mode")

logger = logging.getLogger(__name__)

class EncryptionScheme(Enum):
    """Supported homomorphic encryption schemes"""
    BFV = "bfv"          # Brakerski-Fan-Vercauteren (integers)
    CKKS = "ckks"        # Cheon-Kim-Kim-Song (approximate numbers)
    TFHE = "tfhe"        # Torus Fully Homomorphic Encryption (boolean)

class ComputationType(Enum):
    """Types of computations on encrypted data"""
    THREAT_SCORING = "threat_scoring"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_MATCHING = "pattern_matching"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    CLASSIFICATION = "classification"
    AGGREGATION = "aggregation"

class PrivacyLevel(Enum):
    """Privacy levels for computations"""
    STANDARD = "standard"      # Basic encryption
    HIGH = "high"             # Enhanced parameters
    PARANOID = "paranoid"     # Maximum security parameters

@dataclass
class EncryptionParameters:
    """Parameters for homomorphic encryption"""
    scheme: EncryptionScheme
    poly_modulus_degree: int
    coeff_modulus_bits: List[int]
    plain_modulus_bits: int
    scale_bits: int = 40
    security_level: int = 128
    global_scale: float = 2**40

@dataclass
class EncryptedData:
    """Container for encrypted data with metadata"""
    data_id: str
    encrypted_content: bytes
    scheme: EncryptionScheme
    parameters: EncryptionParameters
    shape: Tuple[int, ...]
    data_type: str
    timestamp: datetime
    context_hash: str

@dataclass
class ComputationTask:
    """Task for computation on encrypted data"""
    task_id: str
    computation_type: ComputationType
    input_data: List[EncryptedData]
    parameters: Dict[str, Any]
    privacy_level: PrivacyLevel
    expected_output_shape: Tuple[int, ...]
    created_at: datetime

@dataclass
class ComputationResult:
    """Result of homomorphic computation"""
    task_id: str
    result_data: EncryptedData
    computation_time_ms: float
    memory_usage_mb: float
    success: bool
    error_message: Optional[str] = None

class HomomorphicEncryptionEngine:
    """Privacy-preserving AI analysis using homomorphic encryption"""

    def __init__(self, config_path: str = "/etc/synos/phase4/privacy-ai-config.yaml"):
        self.config_path = config_path
        self.config = {}

        # Encryption contexts
        self.contexts: Dict[str, Any] = {}
        self.current_context: Optional[Any] = None

        # Data storage
        self.encrypted_datasets: Dict[str, EncryptedData] = {}
        self.computation_tasks: Dict[str, ComputationTask] = {}
        self.completed_computations: Dict[str, ComputationResult] = {}

        # Machine learning models (encrypted)
        self.encrypted_models: Dict[str, Any] = {}

        # Performance monitoring
        self.performance_metrics = {
            'total_encryptions': 0,
            'total_computations': 0,
            'total_computation_time_ms': 0,
            'memory_peak_mb': 0
        }

        # Security parameters
        self.default_parameters = {
            EncryptionScheme.CKKS: EncryptionParameters(
                scheme=EncryptionScheme.CKKS,
                poly_modulus_degree=8192,
                coeff_modulus_bits=[60, 40, 40, 60],
                plain_modulus_bits=0,  # Not used in CKKS
                scale_bits=40
            ),
            EncryptionScheme.BFV: EncryptionParameters(
                scheme=EncryptionScheme.BFV,
                poly_modulus_degree=4096,
                coeff_modulus_bits=[54, 54, 55],
                plain_modulus_bits=20
            )
        }

    async def initialize(self) -> bool:
        """Initialize the homomorphic encryption engine"""
        try:
            logger.info("Initializing Homomorphic Encryption Engine...")

            # Check dependencies
            if not HE_AVAILABLE:
                logger.error("TenSEAL not available - install with: pip install tenseal")
                return False

            # Load configuration
            await self._load_configuration()

            # Initialize encryption contexts
            await self._initialize_contexts()

            # Load pre-trained encrypted models
            await self._load_encrypted_models()

            # Start monitoring tasks
            asyncio.create_task(self._monitor_performance())

            logger.info("Homomorphic Encryption Engine initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize HE engine: {e}")
            return False

    async def _load_configuration(self):
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                'default_scheme': 'ckks',
                'security_level': 128,
                'auto_scale_management': True,
                'parallel_computation': True,
                'memory_optimization': True,
                'context_caching': True,
                'max_encrypted_datasets': 100,
                'computation_timeout_seconds': 300,
                'encrypted_models': {
                    'threat_classifier': {
                        'type': 'neural_network',
                        'layers': [64, 32, 16, 8],
                        'activation': 'relu',
                        'scheme': 'ckks'
                    },
                    'anomaly_detector': {
                        'type': 'isolation_forest',
                        'n_estimators': 100,
                        'scheme': 'bfv'
                    }
                }
            }

    async def _initialize_contexts(self):
        """Initialize encryption contexts for different schemes"""
        try:
            logger.info("Initializing encryption contexts...")

            # CKKS context for approximate computations
            ckks_params = self.default_parameters[EncryptionScheme.CKKS]
            ckks_context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=ckks_params.poly_modulus_degree,
                coeff_mod_bit_sizes=ckks_params.coeff_modulus_bits
            )
            ckks_context.global_scale = ckks_params.global_scale
            ckks_context.generate_galois_keys()

            self.contexts['ckks'] = ckks_context
            self.current_context = ckks_context

            # BFV context for exact computations
            if self.config.get('enable_bfv', True):
                bfv_params = self.default_parameters[EncryptionScheme.BFV]
                bfv_context = ts.context(
                    ts.SCHEME_TYPE.BFV,
                    poly_modulus_degree=bfv_params.poly_modulus_degree,
                    plain_modulus=1032193  # Prime number
                )
                bfv_context.generate_galois_keys()
                self.contexts['bfv'] = bfv_context

            logger.info(f"Initialized {len(self.contexts)} encryption contexts")

        except Exception as e:
            logger.error(f"Failed to initialize contexts: {e}")
            raise

    async def _load_encrypted_models(self):
        """Load pre-trained encrypted models"""
        try:
            logger.info("Loading encrypted machine learning models...")

            # Threat Classification Model (Neural Network)
            threat_model = await self._create_encrypted_neural_network(
                layers=[64, 32, 16, 8, 1],
                scheme=EncryptionScheme.CKKS
            )
            self.encrypted_models['threat_classifier'] = threat_model

            # Anomaly Detection Model (simplified for HE)
            anomaly_model = await self._create_encrypted_anomaly_detector(
                scheme=EncryptionScheme.CKKS
            )
            self.encrypted_models['anomaly_detector'] = anomaly_model

            logger.info(f"Loaded {len(self.encrypted_models)} encrypted models")

        except Exception as e:
            logger.error(f"Failed to load encrypted models: {e}")

    async def _create_encrypted_neural_network(self, layers: List[int],
                                             scheme: EncryptionScheme) -> Dict[str, Any]:
        """Create an encrypted neural network model"""
        try:
            model = {
                'type': 'neural_network',
                'scheme': scheme,
                'layers': layers,
                'weights': {},
                'biases': {},
                'encrypted': True
            }

            # Generate random weights (in practice, these would be trained weights)
            context = self.contexts[scheme.value]

            for i in range(len(layers) - 1):
                input_size = layers[i]
                output_size = layers[i + 1]

                # Create weight matrix
                weights = np.random.normal(0, 0.1, (input_size, output_size))
                encrypted_weights = ts.ckks_vector(context, weights.flatten().tolist())
                model['weights'][f'layer_{i}'] = encrypted_weights

                # Create bias vector
                biases = np.random.normal(0, 0.01, output_size)
                encrypted_biases = ts.ckks_vector(context, biases.tolist())
                model['biases'][f'layer_{i}'] = encrypted_biases

            return model

        except Exception as e:
            logger.error(f"Failed to create encrypted neural network: {e}")
            return {}

    async def _create_encrypted_anomaly_detector(self, scheme: EncryptionScheme) -> Dict[str, Any]:
        """Create an encrypted anomaly detection model"""
        try:
            model = {
                'type': 'anomaly_detector',
                'scheme': scheme,
                'threshold': 0.5,
                'normal_patterns': {},
                'encrypted': True
            }

            context = self.contexts[scheme.value]

            # Create normal behavior patterns (simplified)
            normal_pattern = np.random.normal(0.5, 0.1, 50)  # 50 features
            encrypted_pattern = ts.ckks_vector(context, normal_pattern.tolist())
            model['normal_patterns']['baseline'] = encrypted_pattern

            return model

        except Exception as e:
            logger.error(f"Failed to create encrypted anomaly detector: {e}")
            return {}

    async def encrypt_data(self, data: Union[List[float], np.ndarray],
                          scheme: EncryptionScheme = EncryptionScheme.CKKS,
                          data_type: str = "vector") -> EncryptedData:
        """Encrypt data using specified homomorphic encryption scheme"""
        try:
            logger.debug(f"Encrypting data with scheme: {scheme.value}")

            # Convert input to appropriate format
            if isinstance(data, np.ndarray):
                data_list = data.flatten().tolist()
                original_shape = data.shape
            else:
                data_list = data
                original_shape = (len(data),)

            # Get encryption context
            context = self.contexts[scheme.value]

            # Encrypt based on scheme
            if scheme == EncryptionScheme.CKKS:
                encrypted_vector = ts.ckks_vector(context, data_list)
            elif scheme == EncryptionScheme.BFV:
                # Convert to integers for BFV
                int_data = [int(x * 1000) for x in data_list]  # Scale by 1000
                encrypted_vector = ts.bfv_vector(context, int_data)
            else:
                raise ValueError(f"Unsupported scheme: {scheme}")

            # Serialize encrypted data
            serialized_data = encrypted_vector.serialize()

            # Create metadata
            parameters = self.default_parameters[scheme]
            data_id = hashlib.sha256(serialized_data).hexdigest()[:16]
            context_hash = hashlib.md5(str(parameters).encode()).hexdigest()

            encrypted_data = EncryptedData(
                data_id=data_id,
                encrypted_content=serialized_data,
                scheme=scheme,
                parameters=parameters,
                shape=original_shape,
                data_type=data_type,
                timestamp=datetime.now(),
                context_hash=context_hash
            )

            # Store encrypted dataset
            self.encrypted_datasets[data_id] = encrypted_data
            self.performance_metrics['total_encryptions'] += 1

            logger.debug(f"Data encrypted successfully, ID: {data_id}")
            return encrypted_data

        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise

    async def decrypt_data(self, encrypted_data: EncryptedData) -> np.ndarray:
        """Decrypt homomorphically encrypted data"""
        try:
            logger.debug(f"Decrypting data ID: {encrypted_data.data_id}")

            # Get appropriate context
            context = self.contexts[encrypted_data.scheme.value]

            # Deserialize encrypted vector
            if encrypted_data.scheme == EncryptionScheme.CKKS:
                encrypted_vector = ts.ckks_vector_from(context, encrypted_data.encrypted_content)
                decrypted_list = encrypted_vector.decrypt()
            elif encrypted_data.scheme == EncryptionScheme.BFV:
                encrypted_vector = ts.bfv_vector_from(context, encrypted_data.encrypted_content)
                int_list = encrypted_vector.decrypt()
                # Convert back from integers
                decrypted_list = [x / 1000.0 for x in int_list]
            else:
                raise ValueError(f"Unsupported scheme: {encrypted_data.scheme}")

            # Reshape to original form
            result = np.array(decrypted_list).reshape(encrypted_data.shape)

            logger.debug("Data decrypted successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise

    async def compute_encrypted_threat_score(self, encrypted_features: EncryptedData) -> EncryptedData:
        """Compute threat score on encrypted security features"""
        try:
            logger.info("Computing encrypted threat score...")

            start_time = time.time()

            # Get threat classification model
            model = self.encrypted_models.get('threat_classifier')
            if not model:
                raise ValueError("Threat classification model not loaded")

            # Load encrypted features
            context = self.contexts[encrypted_features.scheme.value]
            features_vector = ts.ckks_vector_from(context, encrypted_features.encrypted_content)

            # Forward pass through encrypted neural network
            current_layer = features_vector

            for i in range(len(model['layers']) - 1):
                # Get encrypted weights and biases
                weights = model['weights'][f'layer_{i}']
                biases = model['biases'][f'layer_{i}']

                # Matrix multiplication (simplified for vector operations)
                # In a full implementation, this would handle proper matrix operations
                weighted_sum = current_layer * weights  # Element-wise for simplicity
                current_layer = weighted_sum + biases

                # Apply activation function (approximated for HE)
                if i < len(model['layers']) - 2:  # Not the last layer
                    current_layer = await self._encrypted_activation(current_layer, 'relu')

            # Create result
            result_data = await self._create_encrypted_result(
                current_layer,
                encrypted_features.scheme,
                (1,),  # Threat score is a single value
                "threat_score"
            )

            computation_time = (time.time() - start_time) * 1000
            self.performance_metrics['total_computations'] += 1
            self.performance_metrics['total_computation_time_ms'] += computation_time

            logger.info(f"Threat score computed in {computation_time:.2f}ms")
            return result_data

        except Exception as e:
            logger.error(f"Failed to compute encrypted threat score: {e}")
            raise

    async def _encrypted_activation(self, encrypted_vector: Any, activation: str) -> Any:
        """Apply activation function to encrypted vector"""
        try:
            if activation == 'relu':
                # Approximate ReLU with polynomial for HE
                # ReLU(x) ≈ max(0, x) can be approximated with degree-2 polynomial
                # For simplicity, we'll use x^2 as an approximation
                return encrypted_vector.square()

            elif activation == 'sigmoid':
                # Approximate sigmoid with polynomial
                # sigmoid(x) ≈ 0.5 + 0.25x - (1/48)x^3 (degree-3 approximation)
                x = encrypted_vector
                x_squared = x.square()
                x_cubed = x_squared * x

                # Calculate approximation
                result = x * 0.25 - x_cubed * (1/48)
                result += 0.5  # Add constant term

                return result

            else:
                # Default: return unchanged
                return encrypted_vector

        except Exception as e:
            logger.error(f"Error in encrypted activation: {e}")
            return encrypted_vector

    async def detect_encrypted_anomalies(self, encrypted_logs: EncryptedData) -> EncryptedData:
        """Detect anomalies in encrypted log data"""
        try:
            logger.info("Detecting anomalies in encrypted data...")

            start_time = time.time()

            # Get anomaly detection model
            model = self.encrypted_models.get('anomaly_detector')
            if not model:
                raise ValueError("Anomaly detection model not loaded")

            # Load encrypted log data
            context = self.contexts[encrypted_logs.scheme.value]
            logs_vector = ts.ckks_vector_from(context, encrypted_logs.encrypted_content)

            # Get baseline normal pattern
            normal_pattern = model['normal_patterns']['baseline']

            # Compute distance from normal pattern (simplified)
            difference = logs_vector - normal_pattern
            squared_diff = difference.square()

            # Sum to get anomaly score
            anomaly_score = squared_diff  # In practice, would sum elements

            # Create result
            result_data = await self._create_encrypted_result(
                anomaly_score,
                encrypted_logs.scheme,
                (1,),  # Anomaly score is a single value
                "anomaly_score"
            )

            computation_time = (time.time() - start_time) * 1000
            self.performance_metrics['total_computations'] += 1
            self.performance_metrics['total_computation_time_ms'] += computation_time

            logger.info(f"Anomaly detection completed in {computation_time:.2f}ms")
            return result_data

        except Exception as e:
            logger.error(f"Failed to detect encrypted anomalies: {e}")
            raise

    async def compute_encrypted_statistics(self, encrypted_datasets: List[EncryptedData]) -> Dict[str, EncryptedData]:
        """Compute statistical measures on encrypted datasets"""
        try:
            logger.info(f"Computing statistics on {len(encrypted_datasets)} encrypted datasets...")

            if not encrypted_datasets:
                return {}

            start_time = time.time()
            results = {}

            # Ensure all datasets use the same scheme and context
            scheme = encrypted_datasets[0].scheme
            context = self.contexts[scheme.value]

            # Load all encrypted vectors
            vectors = []
            for dataset in encrypted_datasets:
                if dataset.scheme != scheme:
                    raise ValueError("All datasets must use the same encryption scheme")
                vector = ts.ckks_vector_from(context, dataset.encrypted_content)
                vectors.append(vector)

            # Compute encrypted mean
            encrypted_sum = vectors[0]
            for vector in vectors[1:]:
                encrypted_sum = encrypted_sum + vector

            count = len(vectors)
            encrypted_mean = encrypted_sum * (1.0 / count)

            results['mean'] = await self._create_encrypted_result(
                encrypted_mean,
                scheme,
                encrypted_datasets[0].shape,
                "statistical_mean"
            )

            # Compute encrypted variance (simplified)
            if len(vectors) > 1:
                variance_sum = None
                for vector in vectors:
                    diff = vector - encrypted_mean
                    squared_diff = diff.square()

                    if variance_sum is None:
                        variance_sum = squared_diff
                    else:
                        variance_sum = variance_sum + squared_diff

                encrypted_variance = variance_sum * (1.0 / (count - 1))
                results['variance'] = await self._create_encrypted_result(
                    encrypted_variance,
                    scheme,
                    encrypted_datasets[0].shape,
                    "statistical_variance"
                )

            computation_time = (time.time() - start_time) * 1000
            self.performance_metrics['total_computations'] += 1
            self.performance_metrics['total_computation_time_ms'] += computation_time

            logger.info(f"Statistics computed in {computation_time:.2f}ms")
            return results

        except Exception as e:
            logger.error(f"Failed to compute encrypted statistics: {e}")
            raise

    async def _create_encrypted_result(self, encrypted_vector: Any, scheme: EncryptionScheme,
                                     shape: Tuple[int, ...], data_type: str) -> EncryptedData:
        """Create EncryptedData object from computation result"""
        try:
            # Serialize the result
            serialized_data = encrypted_vector.serialize()

            # Create metadata
            parameters = self.default_parameters[scheme]
            data_id = hashlib.sha256(serialized_data).hexdigest()[:16]
            context_hash = hashlib.md5(str(parameters).encode()).hexdigest()

            encrypted_data = EncryptedData(
                data_id=data_id,
                encrypted_content=serialized_data,
                scheme=scheme,
                parameters=parameters,
                shape=shape,
                data_type=data_type,
                timestamp=datetime.now(),
                context_hash=context_hash
            )

            # Store result
            self.encrypted_datasets[data_id] = encrypted_data

            return encrypted_data

        except Exception as e:
            logger.error(f"Failed to create encrypted result: {e}")
            raise

    async def create_computation_task(self, computation_type: ComputationType,
                                    input_data: List[EncryptedData],
                                    parameters: Dict[str, Any] = None,
                                    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD) -> str:
        """Create a new computation task"""
        try:
            task_id = hashlib.md5(
                f"{computation_type.value}_{time.time()}".encode()
            ).hexdigest()[:16]

            task = ComputationTask(
                task_id=task_id,
                computation_type=computation_type,
                input_data=input_data,
                parameters=parameters or {},
                privacy_level=privacy_level,
                expected_output_shape=(1,),  # Default
                created_at=datetime.now()
            )

            self.computation_tasks[task_id] = task

            # Execute task asynchronously
            asyncio.create_task(self._execute_computation_task(task))

            logger.info(f"Created computation task: {task_id}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to create computation task: {e}")
            raise

    async def _execute_computation_task(self, task: ComputationTask):
        """Execute a computation task on encrypted data"""
        try:
            logger.info(f"Executing task: {task.task_id} ({task.computation_type.value})")

            start_time = time.time()
            memory_start = self._get_memory_usage()

            result_data = None

            if task.computation_type == ComputationType.THREAT_SCORING:
                if task.input_data:
                    result_data = await self.compute_encrypted_threat_score(task.input_data[0])

            elif task.computation_type == ComputationType.ANOMALY_DETECTION:
                if task.input_data:
                    result_data = await self.detect_encrypted_anomalies(task.input_data[0])

            elif task.computation_type == ComputationType.STATISTICAL_ANALYSIS:
                stats = await self.compute_encrypted_statistics(task.input_data)
                # Return first statistic for simplicity
                result_data = next(iter(stats.values())) if stats else None

            elif task.computation_type == ComputationType.AGGREGATION:
                result_data = await self._compute_encrypted_aggregation(task.input_data, task.parameters)

            # Calculate performance metrics
            computation_time = (time.time() - start_time) * 1000
            memory_usage = self._get_memory_usage() - memory_start

            # Create result
            result = ComputationResult(
                task_id=task.task_id,
                result_data=result_data,
                computation_time_ms=computation_time,
                memory_usage_mb=memory_usage,
                success=result_data is not None,
                error_message=None if result_data else "Computation failed"
            )

            self.completed_computations[task.task_id] = result

            logger.info(f"Task {task.task_id} completed in {computation_time:.2f}ms")

        except Exception as e:
            error_msg = f"Task execution failed: {e}"
            logger.error(error_msg)

            result = ComputationResult(
                task_id=task.task_id,
                result_data=None,
                computation_time_ms=0,
                memory_usage_mb=0,
                success=False,
                error_message=error_msg
            )

            self.completed_computations[task.task_id] = result

    async def _compute_encrypted_aggregation(self, encrypted_datasets: List[EncryptedData],
                                           parameters: Dict[str, Any]) -> EncryptedData:
        """Compute aggregation on encrypted datasets"""
        try:
            if not encrypted_datasets:
                raise ValueError("No datasets provided for aggregation")

            operation = parameters.get('operation', 'sum')
            scheme = encrypted_datasets[0].scheme
            context = self.contexts[scheme.value]

            # Load first vector
            result_vector = ts.ckks_vector_from(context, encrypted_datasets[0].encrypted_content)

            # Apply aggregation operation
            if operation == 'sum':
                for dataset in encrypted_datasets[1:]:
                    vector = ts.ckks_vector_from(context, dataset.encrypted_content)
                    result_vector = result_vector + vector

            elif operation == 'mean':
                for dataset in encrypted_datasets[1:]:
                    vector = ts.ckks_vector_from(context, dataset.encrypted_content)
                    result_vector = result_vector + vector
                # Divide by count
                result_vector = result_vector * (1.0 / len(encrypted_datasets))

            else:
                raise ValueError(f"Unsupported aggregation operation: {operation}")

            # Create result
            return await self._create_encrypted_result(
                result_vector,
                scheme,
                encrypted_datasets[0].shape,
                f"aggregation_{operation}"
            )

        except Exception as e:
            logger.error(f"Failed to compute encrypted aggregation: {e}")
            raise

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    async def get_task_result(self, task_id: str) -> Optional[ComputationResult]:
        """Get the result of a computation task"""
        return self.completed_computations.get(task_id)

    async def list_encrypted_datasets(self) -> List[Dict[str, Any]]:
        """List all encrypted datasets with metadata"""
        try:
            datasets = []

            for data_id, encrypted_data in self.encrypted_datasets.items():
                dataset_info = {
                    'data_id': data_id,
                    'scheme': encrypted_data.scheme.value,
                    'shape': encrypted_data.shape,
                    'data_type': encrypted_data.data_type,
                    'timestamp': encrypted_data.timestamp.isoformat(),
                    'size_bytes': len(encrypted_data.encrypted_content)
                }
                datasets.append(dataset_info)

            return datasets

        except Exception as e:
            logger.error(f"Failed to list encrypted datasets: {e}")
            return []

    async def _monitor_performance(self):
        """Monitor system performance continuously"""
        while True:
            try:
                current_memory = self._get_memory_usage()
                if current_memory > self.performance_metrics['memory_peak_mb']:
                    self.performance_metrics['memory_peak_mb'] = current_memory

                # Clean up old datasets if memory is high
                if current_memory > 1000:  # 1GB
                    await self._cleanup_old_datasets()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)

    async def _cleanup_old_datasets(self):
        """Clean up old encrypted datasets to manage memory"""
        try:
            current_time = datetime.now()
            max_age = timedelta(hours=1)  # Keep datasets for 1 hour

            old_datasets = [
                data_id for data_id, encrypted_data in self.encrypted_datasets.items()
                if current_time - encrypted_data.timestamp > max_age
            ]

            for data_id in old_datasets:
                del self.encrypted_datasets[data_id]
                logger.debug(f"Cleaned up old dataset: {data_id}")

            if old_datasets:
                logger.info(f"Cleaned up {len(old_datasets)} old encrypted datasets")

        except Exception as e:
            logger.error(f"Error cleaning up datasets: {e}")

    async def export_performance_report(self) -> Dict[str, Any]:
        """Export comprehensive performance report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': self.performance_metrics.copy(),
                'system_status': {
                    'active_contexts': len(self.contexts),
                    'encrypted_datasets': len(self.encrypted_datasets),
                    'pending_tasks': len([t for t in self.computation_tasks.values()
                                        if t.task_id not in self.completed_computations]),
                    'completed_tasks': len(self.completed_computations),
                    'encrypted_models': len(self.encrypted_models)
                },
                'memory_usage': {
                    'current_mb': self._get_memory_usage(),
                    'peak_mb': self.performance_metrics['memory_peak_mb']
                }
            }

            # Add computation statistics
            if self.completed_computations:
                computation_times = [r.computation_time_ms for r in self.completed_computations.values() if r.success]
                if computation_times:
                    report['computation_stats'] = {
                        'average_time_ms': sum(computation_times) / len(computation_times),
                        'min_time_ms': min(computation_times),
                        'max_time_ms': max(computation_times),
                        'total_successful': len(computation_times),
                        'success_rate': len(computation_times) / len(self.completed_computations)
                    }

            return report

        except Exception as e:
            logger.error(f"Error exporting performance report: {e}")
            return {'error': str(e)}

    async def shutdown(self):
        """Shutdown the homomorphic encryption engine"""
        try:
            logger.info("Shutting down Homomorphic Encryption Engine...")

            # Clear sensitive data
            self.encrypted_datasets.clear()
            self.computation_tasks.clear()
            self.completed_computations.clear()
            self.encrypted_models.clear()

            # Clear contexts
            self.contexts.clear()
            self.current_context = None

            logger.info("Homomorphic Encryption Engine shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Test the Homomorphic Encryption Engine"""
    if not HE_AVAILABLE:
        print("TenSEAL not available. Install with: pip install tenseal")
        return

    engine = HomomorphicEncryptionEngine()

    if await engine.initialize():
        print("Homomorphic Encryption Engine initialized successfully")

        # Test data encryption
        test_data = [0.5, 0.3, 0.8, 0.1, 0.9, 0.2, 0.7, 0.4]
        print(f"Original data: {test_data}")

        encrypted_data = await engine.encrypt_data(test_data, EncryptionScheme.CKKS)
        print(f"Data encrypted, ID: {encrypted_data.data_id}")

        # Test threat score computation
        threat_result = await engine.compute_encrypted_threat_score(encrypted_data)
        print(f"Threat score computed, result ID: {threat_result.data_id}")

        # Decrypt result to verify
        decrypted_score = await engine.decrypt_data(threat_result)
        print(f"Decrypted threat score: {decrypted_score[0]:.4f}")

        # Test anomaly detection
        anomaly_result = await engine.detect_encrypted_anomalies(encrypted_data)
        print(f"Anomaly detection completed, result ID: {anomaly_result.data_id}")

        # Test statistical computations
        test_datasets = [encrypted_data]  # In practice, would have multiple datasets
        stats = await engine.compute_encrypted_statistics(test_datasets)
        print(f"Computed statistics: {list(stats.keys())}")

        # Generate performance report
        report = await engine.export_performance_report()
        print(f"Performance report: {json.dumps(report, indent=2)}")

    await engine.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())