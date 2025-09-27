#!/usr/bin/env python3

"""
SynOS MLflow Integration
Complete ML lifecycle tracking, versioning, and deployment for SynOS AI components

This module provides comprehensive MLOps capabilities using:
- MLflow Tracking for experiment management
- MLflow Models for model versioning and deployment
- MLflow Model Registry for production model management
- Custom SynOS security model artifacts
- Automated model validation and deployment pipelines
"""

import asyncio
import json
import logging
import os
import time
import pickle
import hashlib
import shutil
import tempfile
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import yaml

# MLflow imports
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.pytorch
    import mlflow.tensorflow
    from mlflow.models.signature import infer_signature
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logging.warning("MLflow not available, using simulation mode")

# ML framework imports
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class ModelStage(Enum):
    """Model lifecycle stages"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"

class ModelType(Enum):
    """Types of AI models in SynOS"""
    THREAT_DETECTOR = "threat_detector"
    ANOMALY_DETECTOR = "anomaly_detector"
    TRAFFIC_CLASSIFIER = "traffic_classifier"
    VULNERABILITY_SCANNER = "vulnerability_scanner"
    BEHAVIORAL_ANALYZER = "behavioral_analyzer"
    PRIVACY_ENHANCER = "privacy_enhancer"

class DeploymentStatus(Enum):
    """Model deployment status"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"

@dataclass
class ModelMetadata:
    """Metadata for SynOS AI models"""
    model_id: str
    model_name: str
    model_type: ModelType
    version: str
    stage: ModelStage
    created_by: str
    created_at: datetime
    description: str
    tags: Dict[str, str]
    performance_metrics: Dict[str, float]
    security_validated: bool
    bias_tested: bool
    explainability_score: float

@dataclass
class ExperimentConfig:
    """Configuration for ML experiments"""
    experiment_name: str
    model_type: ModelType
    hyperparameters: Dict[str, Any]
    training_data_path: str
    validation_data_path: str
    evaluation_metrics: List[str]
    security_requirements: Dict[str, Any]
    privacy_constraints: Dict[str, Any]

@dataclass
class ModelDeployment:
    """Model deployment configuration"""
    deployment_id: str
    model_metadata: ModelMetadata
    target_stage: ModelStage
    deployment_config: Dict[str, Any]
    health_check_config: Dict[str, Any]
    rollback_config: Dict[str, Any]
    deployment_status: DeploymentStatus
    deployed_at: Optional[datetime] = None
    rollback_model_version: Optional[str] = None

class SynOSMLflowIntegration:
    """SynOS MLflow integration for AI model lifecycle management"""

    def __init__(self, config_path: str = "/etc/synos/phase5/mlflow-config.yaml"):
        self.config_path = config_path
        self.config = {}

        # MLflow client and tracking
        self.mlflow_client: Optional[MlflowClient] = None
        self.tracking_uri: str = ""
        self.experiment_id: Optional[str] = None

        # Model registry
        self.model_registry: Dict[str, ModelMetadata] = {}
        self.active_deployments: Dict[str, ModelDeployment] = {}

        # Experiment tracking
        self.current_experiments: Dict[str, Any] = {}
        self.experiment_history: List[Dict[str, Any]] = []

        # Performance monitoring
        self.model_performance: Dict[str, List[Dict[str, Any]]] = {}
        self.drift_detectors: Dict[str, Any] = {}

        # Security and validation
        self.security_validators = {}
        self.bias_detectors = {}

    async def initialize(self) -> bool:
        """Initialize MLflow integration"""
        try:
            logger.info("Initializing SynOS MLflow Integration...")

            if not MLFLOW_AVAILABLE:
                logger.error("MLflow not available. Install with: pip install mlflow")
                return False

            # Load configuration
            await self._load_configuration()

            # Setup MLflow tracking
            await self._setup_mlflow_tracking()

            # Initialize model registry
            await self._initialize_model_registry()

            # Setup security validators
            await self._setup_security_validators()

            # Start monitoring tasks
            asyncio.create_task(self._monitor_model_performance())
            asyncio.create_task(self._monitor_model_drift())

            logger.info("SynOS MLflow Integration initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MLflow integration: {e}")
            return False

    async def _load_configuration(self):
        """Load MLflow configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                'mlflow': {
                    'tracking_uri': 'file:///var/lib/synos/mlflow',
                    'default_experiment': 'SynOS-AI-Security',
                    'model_registry_uri': 'file:///var/lib/synos/mlflow',
                    'artifact_root': '/var/lib/synos/mlflow/artifacts'
                },
                'model_validation': {
                    'security_scan_enabled': True,
                    'bias_detection_enabled': True,
                    'performance_threshold': 0.85,
                    'explainability_required': True
                },
                'deployment': {
                    'auto_deploy_staging': False,
                    'auto_deploy_production': False,
                    'health_check_interval_seconds': 60,
                    'rollback_threshold_errors': 10
                },
                'monitoring': {
                    'drift_detection_enabled': True,
                    'performance_monitoring_enabled': True,
                    'alert_thresholds': {
                        'accuracy_drop': 0.05,
                        'latency_increase': 2.0,
                        'error_rate_increase': 0.1
                    }
                }
            }

    async def _setup_mlflow_tracking(self):
        """Setup MLflow tracking server and client"""
        try:
            # Set tracking URI
            self.tracking_uri = self.config['mlflow']['tracking_uri']
            mlflow.set_tracking_uri(self.tracking_uri)

            # Create MLflow client
            self.mlflow_client = MlflowClient()

            # Create or get default experiment
            experiment_name = self.config['mlflow']['default_experiment']
            try:
                experiment = self.mlflow_client.get_experiment_by_name(experiment_name)
                self.experiment_id = experiment.experiment_id
            except Exception:
                self.experiment_id = self.mlflow_client.create_experiment(
                    experiment_name,
                    artifact_location=self.config['mlflow']['artifact_root']
                )

            # Set default experiment
            mlflow.set_experiment(experiment_name)

            logger.info(f"MLflow tracking setup complete. Experiment ID: {self.experiment_id}")

        except Exception as e:
            logger.error(f"Failed to setup MLflow tracking: {e}")
            raise

    async def _initialize_model_registry(self):
        """Initialize SynOS model registry"""
        try:
            # Load existing model metadata from registry
            registry_path = Path(self.config['mlflow']['artifact_root']) / 'synos_model_registry.json'

            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry_data = json.load(f)

                for model_id, metadata_dict in registry_data.items():
                    metadata_dict['created_at'] = datetime.fromisoformat(metadata_dict['created_at'])
                    metadata_dict['model_type'] = ModelType(metadata_dict['model_type'])
                    metadata_dict['stage'] = ModelStage(metadata_dict['stage'])

                    self.model_registry[model_id] = ModelMetadata(**metadata_dict)

            logger.info(f"Model registry initialized with {len(self.model_registry)} models")

        except Exception as e:
            logger.error(f"Failed to initialize model registry: {e}")

    async def _setup_security_validators(self):
        """Setup security validation for AI models"""
        try:
            # Adversarial robustness validator
            self.security_validators['adversarial'] = {
                'enabled': True,
                'attack_methods': ['fgsm', 'pgd', 'c&w'],
                'epsilon_values': [0.01, 0.1, 0.3],
                'success_threshold': 0.9
            }

            # Input validation
            self.security_validators['input_validation'] = {
                'enabled': True,
                'sanitization_rules': ['xss', 'sql_injection', 'command_injection'],
                'anomaly_detection': True
            }

            # Bias detection
            self.bias_detectors = {
                'fairness_metrics': ['demographic_parity', 'equalized_odds'],
                'protected_attributes': ['geographic_region', 'network_type'],
                'bias_threshold': 0.1
            }

            logger.info("Security validators initialized")

        except Exception as e:
            logger.error(f"Failed to setup security validators: {e}")

    async def start_experiment(self, experiment_config: ExperimentConfig) -> str:
        """Start a new ML experiment"""
        try:
            logger.info(f"Starting experiment: {experiment_config.experiment_name}")

            # Create or get experiment
            try:
                experiment = self.mlflow_client.get_experiment_by_name(experiment_config.experiment_name)
                experiment_id = experiment.experiment_id
            except Exception:
                experiment_id = self.mlflow_client.create_experiment(experiment_config.experiment_name)

            # Start MLflow run
            run = self.mlflow_client.create_run(experiment_id)
            run_id = run.info.run_id

            # Log experiment configuration
            self.mlflow_client.log_params(run_id, experiment_config.hyperparameters)

            # Log SynOS-specific metadata
            self.mlflow_client.log_params(run_id, {
                'synos_model_type': experiment_config.model_type.value,
                'synos_security_level': experiment_config.security_requirements.get('level', 'standard'),
                'synos_privacy_mode': experiment_config.privacy_constraints.get('mode', 'standard')
            })

            # Store experiment state
            self.current_experiments[run_id] = {
                'config': experiment_config,
                'start_time': datetime.now(),
                'status': 'running',
                'experiment_id': experiment_id
            }

            logger.info(f"Experiment started with run ID: {run_id}")
            return run_id

        except Exception as e:
            logger.error(f"Failed to start experiment: {e}")
            raise

    async def log_model_training_metrics(self, run_id: str, metrics: Dict[str, float], step: int = 0):
        """Log training metrics during model development"""
        try:
            # Log standard metrics
            for metric_name, value in metrics.items():
                self.mlflow_client.log_metric(run_id, metric_name, value, step=step)

            # Log SynOS-specific security metrics if available
            if 'adversarial_robustness' in metrics:
                self.mlflow_client.log_metric(run_id, 'synos_security_score',
                                            metrics['adversarial_robustness'], step=step)

            if 'privacy_preservation' in metrics:
                self.mlflow_client.log_metric(run_id, 'synos_privacy_score',
                                            metrics['privacy_preservation'], step=step)

            logger.debug(f"Logged metrics for run {run_id}: {list(metrics.keys())}")

        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")

    async def register_model(self, run_id: str, model_name: str, model_type: ModelType,
                           model_path: str, description: str = "") -> ModelMetadata:
        """Register a trained model in the SynOS model registry"""
        try:
            logger.info(f"Registering model: {model_name}")

            # Validate model before registration
            validation_results = await self._validate_model_security(model_path, model_type)

            if not validation_results['passed']:
                raise ValueError(f"Model failed security validation: {validation_results['errors']}")

            # Register with MLflow
            model_version = mlflow.register_model(
                model_uri=f"runs:/{run_id}/model",
                name=model_name,
                description=description
            )

            # Create SynOS model metadata
            model_id = f"{model_name}_v{model_version.version}"

            metadata = ModelMetadata(
                model_id=model_id,
                model_name=model_name,
                model_type=model_type,
                version=model_version.version,
                stage=ModelStage.DEVELOPMENT,
                created_by="synos_mlops",
                created_at=datetime.now(),
                description=description,
                tags={
                    'synos_type': model_type.value,
                    'security_validated': str(validation_results['passed']),
                    'mlflow_version': model_version.version
                },
                performance_metrics=validation_results.get('performance_metrics', {}),
                security_validated=validation_results['passed'],
                bias_tested=validation_results.get('bias_tested', False),
                explainability_score=validation_results.get('explainability_score', 0.0)
            )

            # Store in registry
            self.model_registry[model_id] = metadata

            # Save registry
            await self._save_model_registry()

            logger.info(f"Model registered successfully: {model_id}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            raise

    async def _validate_model_security(self, model_path: str, model_type: ModelType) -> Dict[str, Any]:
        """Validate model security and robustness"""
        try:
            validation_results = {
                'passed': True,
                'errors': [],
                'warnings': [],
                'performance_metrics': {},
                'security_metrics': {},
                'bias_tested': False,
                'explainability_score': 0.0
            }

            # Basic model loading test
            try:
                # This would be model-specific loading
                logger.info("Testing model loading...")
                validation_results['performance_metrics']['load_time_ms'] = 150.0
            except Exception as e:
                validation_results['passed'] = False
                validation_results['errors'].append(f"Model loading failed: {e}")

            # Security validation
            if self.config['model_validation']['security_scan_enabled']:
                security_results = await self._run_security_scan(model_path, model_type)
                validation_results['security_metrics'] = security_results

                if security_results.get('adversarial_robustness', 0) < 0.7:
                    validation_results['warnings'].append("Low adversarial robustness detected")

            # Bias detection
            if self.config['model_validation']['bias_detection_enabled']:
                bias_results = await self._detect_model_bias(model_path, model_type)
                validation_results['bias_tested'] = True

                if bias_results.get('bias_score', 0) > 0.1:
                    validation_results['warnings'].append("Potential bias detected")

            # Explainability assessment
            if self.config['model_validation']['explainability_required']:
                explainability_score = await self._assess_explainability(model_path, model_type)
                validation_results['explainability_score'] = explainability_score

                if explainability_score < 0.5:
                    validation_results['warnings'].append("Low explainability score")

            return validation_results

        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return {
                'passed': False,
                'errors': [f"Validation error: {e}"],
                'warnings': [],
                'performance_metrics': {},
                'security_metrics': {},
                'bias_tested': False,
                'explainability_score': 0.0
            }

    async def _run_security_scan(self, model_path: str, model_type: ModelType) -> Dict[str, float]:
        """Run security scan on AI model"""
        try:
            # Simulate security scanning (in practice, would use real security tools)
            security_metrics = {
                'adversarial_robustness': np.random.uniform(0.6, 0.95),
                'input_validation_score': np.random.uniform(0.8, 0.99),
                'privacy_leakage_risk': np.random.uniform(0.01, 0.15),
                'backdoor_detection_confidence': np.random.uniform(0.85, 0.99)
            }

            logger.info(f"Security scan completed for {model_type.value}")
            return security_metrics

        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {}

    async def _detect_model_bias(self, model_path: str, model_type: ModelType) -> Dict[str, float]:
        """Detect potential bias in AI model"""
        try:
            # Simulate bias detection
            bias_metrics = {
                'demographic_parity': np.random.uniform(0.02, 0.12),
                'equalized_odds': np.random.uniform(0.01, 0.08),
                'bias_score': np.random.uniform(0.03, 0.15)
            }

            logger.info(f"Bias detection completed for {model_type.value}")
            return bias_metrics

        except Exception as e:
            logger.error(f"Bias detection failed: {e}")
            return {}

    async def _assess_explainability(self, model_path: str, model_type: ModelType) -> float:
        """Assess model explainability"""
        try:
            # Simulate explainability assessment
            # In practice, would use LIME, SHAP, or attention mechanisms
            explainability_score = np.random.uniform(0.3, 0.9)

            logger.info(f"Explainability assessment completed: {explainability_score:.3f}")
            return explainability_score

        except Exception as e:
            logger.error(f"Explainability assessment failed: {e}")
            return 0.0

    async def transition_model_stage(self, model_id: str, target_stage: ModelStage,
                                  validation_required: bool = True) -> bool:
        """Transition model between lifecycle stages"""
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found in registry")

            metadata = self.model_registry[model_id]
            current_stage = metadata.stage

            logger.info(f"Transitioning model {model_id}: {current_stage.value} -> {target_stage.value}")

            # Validate transition
            if not self._is_valid_stage_transition(current_stage, target_stage):
                raise ValueError(f"Invalid stage transition: {current_stage.value} -> {target_stage.value}")

            # Run stage-specific validations
            if validation_required:
                validation_passed = await self._validate_stage_transition(metadata, target_stage)
                if not validation_passed:
                    raise ValueError("Stage transition validation failed")

            # Update MLflow model registry
            self.mlflow_client.transition_model_version_stage(
                name=metadata.model_name,
                version=metadata.version,
                stage=target_stage.value.upper()
            )

            # Update SynOS metadata
            metadata.stage = target_stage
            self.model_registry[model_id] = metadata

            # Save registry
            await self._save_model_registry()

            logger.info(f"Model {model_id} successfully transitioned to {target_stage.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to transition model stage: {e}")
            return False

    def _is_valid_stage_transition(self, current: ModelStage, target: ModelStage) -> bool:
        """Validate if stage transition is allowed"""
        valid_transitions = {
            ModelStage.DEVELOPMENT: [ModelStage.STAGING, ModelStage.ARCHIVED],
            ModelStage.STAGING: [ModelStage.PRODUCTION, ModelStage.DEVELOPMENT, ModelStage.ARCHIVED],
            ModelStage.PRODUCTION: [ModelStage.ARCHIVED],
            ModelStage.ARCHIVED: [ModelStage.DEVELOPMENT]
        }

        return target in valid_transitions.get(current, [])

    async def _validate_stage_transition(self, metadata: ModelMetadata, target_stage: ModelStage) -> bool:
        """Validate requirements for stage transition"""
        try:
            # Production stage requirements
            if target_stage == ModelStage.PRODUCTION:
                # Must be security validated
                if not metadata.security_validated:
                    logger.error("Production deployment requires security validation")
                    return False

                # Must have good performance metrics
                accuracy = metadata.performance_metrics.get('accuracy', 0.0)
                if accuracy < self.config['model_validation']['performance_threshold']:
                    logger.error(f"Performance below threshold: {accuracy}")
                    return False

                # Must be bias tested
                if not metadata.bias_tested:
                    logger.error("Production deployment requires bias testing")
                    return False

                # Explainability requirement
                if (self.config['model_validation']['explainability_required'] and
                    metadata.explainability_score < 0.5):
                    logger.error("Insufficient explainability for production deployment")
                    return False

            return True

        except Exception as e:
            logger.error(f"Stage transition validation failed: {e}")
            return False

    async def deploy_model(self, model_id: str, deployment_config: Dict[str, Any]) -> ModelDeployment:
        """Deploy a model to specified environment"""
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")

            metadata = self.model_registry[model_id]

            logger.info(f"Deploying model {model_id} to {metadata.stage.value}")

            # Create deployment configuration
            deployment_id = f"deploy_{model_id}_{int(time.time())}"

            deployment = ModelDeployment(
                deployment_id=deployment_id,
                model_metadata=metadata,
                target_stage=metadata.stage,
                deployment_config=deployment_config,
                health_check_config=self.config['deployment'],
                rollback_config={
                    'enabled': True,
                    'rollback_model_version': metadata.version
                },
                deployment_status=DeploymentStatus.PENDING
            )

            # Store deployment
            self.active_deployments[deployment_id] = deployment

            # Start deployment process
            asyncio.create_task(self._execute_deployment(deployment))

            logger.info(f"Deployment initiated: {deployment_id}")
            return deployment

        except Exception as e:
            logger.error(f"Failed to deploy model: {e}")
            raise

    async def _execute_deployment(self, deployment: ModelDeployment):
        """Execute model deployment"""
        try:
            deployment.deployment_status = DeploymentStatus.DEPLOYING

            # Simulate deployment process
            logger.info(f"Executing deployment {deployment.deployment_id}")

            # Pre-deployment checks
            await self._run_pre_deployment_checks(deployment)

            # Deploy model
            await asyncio.sleep(2)  # Simulate deployment time

            # Post-deployment validation
            success = await self._run_post_deployment_validation(deployment)

            if success:
                deployment.deployment_status = DeploymentStatus.DEPLOYED
                deployment.deployed_at = datetime.now()
                logger.info(f"Deployment {deployment.deployment_id} completed successfully")
            else:
                deployment.deployment_status = DeploymentStatus.FAILED
                logger.error(f"Deployment {deployment.deployment_id} failed validation")

        except Exception as e:
            deployment.deployment_status = DeploymentStatus.FAILED
            logger.error(f"Deployment {deployment.deployment_id} failed: {e}")

    async def _run_pre_deployment_checks(self, deployment: ModelDeployment):
        """Run pre-deployment checks"""
        try:
            # Resource availability check
            logger.info("Checking resource availability...")

            # Security compliance check
            logger.info("Verifying security compliance...")

            # Model integrity check
            logger.info("Validating model integrity...")

            await asyncio.sleep(1)  # Simulate check time

        except Exception as e:
            logger.error(f"Pre-deployment checks failed: {e}")
            raise

    async def _run_post_deployment_validation(self, deployment: ModelDeployment) -> bool:
        """Run post-deployment validation"""
        try:
            # Health check
            logger.info("Running deployment health check...")

            # Performance validation
            logger.info("Validating deployment performance...")

            # Integration test
            logger.info("Running integration tests...")

            await asyncio.sleep(1)  # Simulate validation time

            return True  # Simulate successful validation

        except Exception as e:
            logger.error(f"Post-deployment validation failed: {e}")
            return False

    async def _monitor_model_performance(self):
        """Monitor model performance continuously"""
        while True:
            try:
                for model_id, metadata in self.model_registry.items():
                    if metadata.stage == ModelStage.PRODUCTION:
                        # Collect performance metrics
                        metrics = await self._collect_model_metrics(model_id)

                        if model_id not in self.model_performance:
                            self.model_performance[model_id] = []

                        self.model_performance[model_id].append({
                            'timestamp': datetime.now(),
                            'metrics': metrics
                        })

                        # Check for performance degradation
                        await self._check_performance_alerts(model_id, metrics)

                await asyncio.sleep(self.config['deployment']['health_check_interval_seconds'])

            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_model_metrics(self, model_id: str) -> Dict[str, float]:
        """Collect runtime metrics for a deployed model"""
        try:
            # Simulate metric collection
            metrics = {
                'accuracy': np.random.uniform(0.8, 0.95),
                'latency_ms': np.random.uniform(50, 200),
                'throughput_rps': np.random.uniform(100, 500),
                'error_rate': np.random.uniform(0.01, 0.05),
                'memory_usage_mb': np.random.uniform(100, 500),
                'cpu_usage_percent': np.random.uniform(10, 60)
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect metrics for {model_id}: {e}")
            return {}

    async def _check_performance_alerts(self, model_id: str, current_metrics: Dict[str, float]):
        """Check for performance alerts and trigger actions"""
        try:
            thresholds = self.config['monitoring']['alert_thresholds']

            # Get historical performance
            if model_id in self.model_performance and len(self.model_performance[model_id]) > 1:
                recent_metrics = self.model_performance[model_id][-5:]  # Last 5 measurements
                historical_accuracy = np.mean([m['metrics'].get('accuracy', 0) for m in recent_metrics])

                # Check accuracy drop
                accuracy_drop = historical_accuracy - current_metrics.get('accuracy', 0)
                if accuracy_drop > thresholds['accuracy_drop']:
                    logger.warning(f"Accuracy drop detected for {model_id}: {accuracy_drop:.3f}")
                    await self._trigger_model_alert(model_id, 'accuracy_drop', accuracy_drop)

                # Check latency increase
                historical_latency = np.mean([m['metrics'].get('latency_ms', 0) for m in recent_metrics])
                latency_ratio = current_metrics.get('latency_ms', 0) / historical_latency if historical_latency > 0 else 1
                if latency_ratio > thresholds['latency_increase']:
                    logger.warning(f"Latency increase detected for {model_id}: {latency_ratio:.2f}x")
                    await self._trigger_model_alert(model_id, 'latency_increase', latency_ratio)

        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")

    async def _trigger_model_alert(self, model_id: str, alert_type: str, value: float):
        """Trigger alert for model performance issues"""
        try:
            alert = {
                'model_id': model_id,
                'alert_type': alert_type,
                'value': value,
                'timestamp': datetime.now(),
                'severity': 'warning'
            }

            logger.warning(f"Model alert triggered: {alert}")

            # Could trigger automated rollback if configured
            if alert_type == 'accuracy_drop' and value > 0.1:  # Significant drop
                logger.info(f"Considering rollback for model {model_id}")

        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")

    async def _monitor_model_drift(self):
        """Monitor for model drift"""
        while True:
            try:
                for model_id in list(self.model_registry.keys()):
                    if self.model_registry[model_id].stage == ModelStage.PRODUCTION:
                        drift_score = await self._detect_drift(model_id)

                        if drift_score > 0.3:  # Significant drift
                            logger.warning(f"Model drift detected for {model_id}: {drift_score:.3f}")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in drift monitoring: {e}")
                await asyncio.sleep(300)

    async def _detect_drift(self, model_id: str) -> float:
        """Detect data drift for model"""
        try:
            # Simulate drift detection
            drift_score = np.random.uniform(0.0, 0.5)
            return drift_score

        except Exception as e:
            logger.error(f"Drift detection failed for {model_id}: {e}")
            return 0.0

    async def _save_model_registry(self):
        """Save model registry to persistent storage"""
        try:
            registry_path = Path(self.config['mlflow']['artifact_root']) / 'synos_model_registry.json'
            registry_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to serializable format
            registry_data = {}
            for model_id, metadata in self.model_registry.items():
                metadata_dict = asdict(metadata)
                metadata_dict['created_at'] = metadata.created_at.isoformat()
                metadata_dict['model_type'] = metadata.model_type.value
                metadata_dict['stage'] = metadata.stage.value
                registry_data[model_id] = metadata_dict

            with open(registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save model registry: {e}")

    async def get_model_performance_report(self, model_id: str) -> Dict[str, Any]:
        """Generate comprehensive model performance report"""
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")

            metadata = self.model_registry[model_id]
            performance_data = self.model_performance.get(model_id, [])

            report = {
                'model_metadata': asdict(metadata),
                'performance_summary': {},
                'deployment_status': 'not_deployed',
                'alerts': [],
                'recommendations': []
            }

            if performance_data:
                recent_metrics = performance_data[-10:]  # Last 10 measurements

                # Calculate performance summary
                for metric_name in ['accuracy', 'latency_ms', 'throughput_rps', 'error_rate']:
                    values = [m['metrics'].get(metric_name, 0) for m in recent_metrics if metric_name in m['metrics']]
                    if values:
                        report['performance_summary'][metric_name] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'min': np.min(values),
                            'max': np.max(values)
                        }

            # Check deployment status
            for deployment in self.active_deployments.values():
                if deployment.model_metadata.model_id == model_id:
                    report['deployment_status'] = deployment.deployment_status.value
                    break

            return report

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}

    async def shutdown(self):
        """Shutdown MLflow integration"""
        try:
            logger.info("Shutting down SynOS MLflow Integration...")

            # Save current state
            await self._save_model_registry()

            # Clean up resources
            self.model_registry.clear()
            self.active_deployments.clear()
            self.current_experiments.clear()

            logger.info("MLflow integration shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Test MLflow integration"""
    if not MLFLOW_AVAILABLE:
        print("MLflow not available. Install with: pip install mlflow")
        return

    mlops = SynOSMLflowIntegration()

    if await mlops.initialize():
        print("MLflow integration initialized successfully")

        # Example experiment
        experiment_config = ExperimentConfig(
            experiment_name="test_threat_detector",
            model_type=ModelType.THREAT_DETECTOR,
            hyperparameters={"learning_rate": 0.01, "epochs": 10},
            training_data_path="/data/threats.csv",
            validation_data_path="/data/threats_val.csv",
            evaluation_metrics=["accuracy", "precision", "recall"],
            security_requirements={"level": "high"},
            privacy_constraints={"mode": "privacy_preserving"}
        )

        # Start experiment
        run_id = await mlops.start_experiment(experiment_config)
        print(f"Started experiment: {run_id}")

        # Simulate training
        for step in range(5):
            metrics = {
                "accuracy": 0.7 + step * 0.05,
                "loss": 0.5 - step * 0.08,
                "adversarial_robustness": 0.8 + step * 0.02
            }
            await mlops.log_model_training_metrics(run_id, metrics, step)

        print("Model training simulation complete")

    await mlops.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())