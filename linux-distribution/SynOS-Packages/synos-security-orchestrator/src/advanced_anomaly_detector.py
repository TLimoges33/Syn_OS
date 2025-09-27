#!/usr/bin/env python3
"""
SynOS Advanced Anomaly Detection System
Dynamic baseline establishment and intelligent threat detection using multiple ML algorithms
"""

import asyncio
import json
import logging
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import threading
from collections import deque, defaultdict
import statistics

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
import joblib


class AnomalyType(Enum):
    STATISTICAL = "statistical"
    BEHAVIORAL = "behavioral"
    TEMPORAL = "temporal"
    NETWORK = "network"
    PROCESS = "process"
    FILESYSTEM = "filesystem"
    PERFORMANCE = "performance"
    SECURITY = "security"


class AnomalySeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MetricPoint:
    timestamp: datetime
    metric_name: str
    value: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BaselineProfile:
    metric_name: str
    time_window: str  # "hourly", "daily", "weekly"
    mean: float
    std: float
    median: float
    percentiles: Dict[int, float]  # 5th, 25th, 75th, 95th percentiles
    min_value: float
    max_value: float
    sample_count: int
    last_updated: datetime
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)


@dataclass
class AnomalyDetection:
    id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    metric_name: str
    observed_value: float
    expected_value: float
    deviation_score: float
    confidence: float
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    false_positive_probability: float = 0.0
    remediation_suggestions: List[str] = field(default_factory=list)


@dataclass
class DetectionModel:
    model_type: str
    model_name: str
    metric_patterns: List[str]
    model_object: Any
    scaler: Any
    training_accuracy: float
    last_trained: datetime
    feature_importance: Dict[str, float] = field(default_factory=dict)


class BaselineManager:
    """Manages dynamic baselines for different metrics and time windows"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.baselines: Dict[str, BaselineProfile] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.update_intervals = {
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1)
        }

    def add_metric_point(self, point: MetricPoint):
        """Add new metric point and update baseline if needed"""
        key = f"{point.metric_name}_{point.source}"
        self.metric_history[key].append(point)

        # Update baseline if enough new data
        if len(self.metric_history[key]) % 100 == 0:
            asyncio.create_task(self.update_baseline(point.metric_name, point.source))

    async def update_baseline(self, metric_name: str, source: str):
        """Update baseline profile for metric"""
        key = f"{metric_name}_{source}"
        history = list(self.metric_history[key])

        if len(history) < 30:  # Need minimum data points
            return

        # Calculate baseline for different time windows
        for window_name, window_duration in self.update_intervals.items():
            cutoff_time = datetime.now() - window_duration * 7  # 7 periods of data
            window_data = [p for p in history if p.timestamp >= cutoff_time]

            if len(window_data) < 10:
                continue

            values = [p.value for p in window_data]
            baseline = self._calculate_baseline_stats(values)
            baseline.metric_name = metric_name
            baseline.time_window = window_name
            baseline.last_updated = datetime.now()

            # Add seasonal patterns
            baseline.seasonal_patterns = self._detect_seasonal_patterns(window_data)

            # Store baseline
            baseline_key = f"{metric_name}_{source}_{window_name}"
            self.baselines[baseline_key] = baseline

            # Persist to database
            await self._store_baseline(baseline_key, baseline)

    def _calculate_baseline_stats(self, values: List[float]) -> BaselineProfile:
        """Calculate statistical baseline from values"""
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0.0
        median_val = statistics.median(values)

        percentiles = {
            5: np.percentile(values, 5),
            25: np.percentile(values, 25),
            75: np.percentile(values, 75),
            95: np.percentile(values, 95)
        }

        return BaselineProfile(
            metric_name="",  # Set by caller
            time_window="",  # Set by caller
            mean=mean_val,
            std=std_val,
            median=median_val,
            percentiles=percentiles,
            min_value=min(values),
            max_value=max(values),
            sample_count=len(values),
            last_updated=datetime.now()
        )

    def _detect_seasonal_patterns(self, data: List[MetricPoint]) -> Dict[str, float]:
        """Detect seasonal patterns in metric data"""
        patterns = {}

        if len(data) < 50:
            return patterns

        # Group by hour of day
        hourly_data = defaultdict(list)
        for point in data:
            hour = point.timestamp.hour
            hourly_data[hour].append(point.value)

        # Calculate hour-of-day pattern strength
        hourly_means = {hour: statistics.mean(values) for hour, values in hourly_data.items() if len(values) >= 3}
        if len(hourly_means) >= 12:
            overall_mean = statistics.mean(hourly_means.values())
            hourly_variance = statistics.variance(hourly_means.values())
            patterns["hourly_pattern_strength"] = hourly_variance / (overall_mean + 1e-8)

        # Group by day of week
        daily_data = defaultdict(list)
        for point in data:
            day = point.timestamp.weekday()
            daily_data[day].append(point.value)

        daily_means = {day: statistics.mean(values) for day, values in daily_data.items() if len(values) >= 3}
        if len(daily_means) >= 5:
            overall_mean = statistics.mean(daily_means.values())
            daily_variance = statistics.variance(daily_means.values())
            patterns["daily_pattern_strength"] = daily_variance / (overall_mean + 1e-8)

        return patterns

    def get_baseline(self, metric_name: str, source: str, time_window: str = "hourly") -> Optional[BaselineProfile]:
        """Get baseline profile for metric"""
        key = f"{metric_name}_{source}_{time_window}"
        return self.baselines.get(key)

    def is_baseline_stale(self, baseline: BaselineProfile) -> bool:
        """Check if baseline needs updating"""
        age = datetime.now() - baseline.last_updated
        window_duration = self.update_intervals.get(baseline.time_window, timedelta(hours=1))
        return age > window_duration * 2

    async def _store_baseline(self, key: str, baseline: BaselineProfile):
        """Store baseline in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO baselines
                    (key, metric_name, time_window, mean_val, std_val, median_val,
                     percentiles, min_val, max_val, sample_count, last_updated, seasonal_patterns)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key, baseline.metric_name, baseline.time_window,
                    baseline.mean, baseline.std, baseline.median,
                    json.dumps(baseline.percentiles), baseline.min_value, baseline.max_value,
                    baseline.sample_count, baseline.last_updated, json.dumps(baseline.seasonal_patterns)
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store baseline {key}: {e}")


class MLAnomalyDetector:
    """Machine learning based anomaly detection using multiple algorithms"""

    def __init__(self):
        self.models: Dict[str, DetectionModel] = {}
        self.feature_extractors: Dict[str, callable] = {}
        self.training_data: List[Dict[str, Any]] = []

    def register_feature_extractor(self, metric_pattern: str, extractor: callable):
        """Register feature extraction function for metric pattern"""
        self.feature_extractors[metric_pattern] = extractor

    async def train_models(self, training_data: List[Dict[str, Any]]):
        """Train multiple ML models for anomaly detection"""
        if len(training_data) < 100:
            logging.warning("Insufficient training data for ML models")
            return

        self.training_data = training_data
        df = pd.DataFrame(training_data)

        # Train different models for different metric types
        metric_groups = df.groupby('metric_type')

        for metric_type, group_df in metric_groups:
            if len(group_df) < 50:
                continue

            await self._train_model_group(metric_type, group_df)

    async def _train_model_group(self, metric_type: str, df: pd.DataFrame):
        """Train models for specific metric type"""
        try:
            # Extract features
            features = self._extract_ml_features(df)
            if len(features) == 0:
                return

            features_df = pd.DataFrame(features)

            # Isolation Forest for unsupervised anomaly detection
            iso_forest = IsolationForest(contamination=0.05, random_state=42)
            scaler = StandardScaler()

            scaled_features = scaler.fit_transform(features_df)
            iso_forest.fit(scaled_features)

            # Store model
            model_name = f"isolation_forest_{metric_type}"
            self.models[model_name] = DetectionModel(
                model_type="isolation_forest",
                model_name=model_name,
                metric_patterns=[metric_type],
                model_object=iso_forest,
                scaler=scaler,
                training_accuracy=0.95,  # Default for unsupervised
                last_trained=datetime.now()
            )

            # Train supervised model if we have labeled data
            if 'is_anomaly' in df.columns:
                await self._train_supervised_model(metric_type, features_df, df['is_anomaly'])

            logging.info(f"Trained ML models for metric type: {metric_type}")

        except Exception as e:
            logging.error(f"Failed to train models for {metric_type}: {e}")

    async def _train_supervised_model(self, metric_type: str, features_df: pd.DataFrame, labels: pd.Series):
        """Train supervised classification model"""
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, labels, test_size=0.2, random_state=42
            )

            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Random Forest Classifier
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)

            # Calculate accuracy
            accuracy = rf_model.score(X_test_scaled, y_test)

            # Feature importance
            feature_importance = dict(zip(
                features_df.columns,
                rf_model.feature_importances_
            ))

            model_name = f"random_forest_{metric_type}"
            self.models[model_name] = DetectionModel(
                model_type="random_forest",
                model_name=model_name,
                metric_patterns=[metric_type],
                model_object=rf_model,
                scaler=scaler,
                training_accuracy=accuracy,
                last_trained=datetime.now(),
                feature_importance=feature_importance
            )

        except Exception as e:
            logging.error(f"Failed to train supervised model for {metric_type}: {e}")

    def _extract_ml_features(self, df: pd.DataFrame) -> List[Dict[str, float]]:
        """Extract features for ML training"""
        features = []

        for _, row in df.iterrows():
            feature_dict = {
                'value': row.get('value', 0.0),
                'hour_of_day': row.get('timestamp', datetime.now()).hour,
                'day_of_week': row.get('timestamp', datetime.now()).weekday(),
                'value_log': math.log(max(abs(row.get('value', 0.0)), 1e-8)),
            }

            # Add custom features based on metric type
            metric_type = row.get('metric_type', 'unknown')
            if metric_type in self.feature_extractors:
                custom_features = self.feature_extractors[metric_type](row)
                feature_dict.update(custom_features)

            features.append(feature_dict)

        return features

    async def detect_anomaly(self, metric_point: MetricPoint, baseline: Optional[BaselineProfile] = None) -> Optional[AnomalyDetection]:
        """Detect anomaly using ML models"""
        # Find applicable models
        applicable_models = []
        for model in self.models.values():
            if any(pattern in metric_point.metric_name for pattern in model.metric_patterns):
                applicable_models.append(model)

        if not applicable_models:
            return None

        anomaly_scores = []

        for model in applicable_models:
            try:
                score = await self._score_with_model(metric_point, model, baseline)
                if score is not None:
                    anomaly_scores.append((model.model_name, score))
            except Exception as e:
                logging.debug(f"Model {model.model_name} failed: {e}")

        if not anomaly_scores:
            return None

        # Combine scores
        avg_score = statistics.mean([score for _, score in anomaly_scores])
        max_score = max([score for _, score in anomaly_scores])

        # Determine if anomalous
        threshold = 0.7
        if max_score > threshold:
            severity = self._determine_severity(max_score)

            return AnomalyDetection(
                id=f"ml_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.BEHAVIORAL,
                severity=severity,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=baseline.mean if baseline else metric_point.value,
                deviation_score=max_score,
                confidence=avg_score,
                description=f"ML anomaly detected with score {max_score:.2f}",
                context={
                    "model_scores": dict(anomaly_scores),
                    "baseline_available": baseline is not None
                }
            )

        return None

    async def _score_with_model(self, metric_point: MetricPoint, model: DetectionModel, baseline: Optional[BaselineProfile]) -> Optional[float]:
        """Score metric point with specific ML model"""
        # Create feature vector
        features = {
            'value': metric_point.value,
            'hour_of_day': metric_point.timestamp.hour,
            'day_of_week': metric_point.timestamp.weekday(),
            'value_log': math.log(max(abs(metric_point.value), 1e-8)),
        }

        # Add baseline-derived features
        if baseline:
            features.update({
                'deviation_from_mean': abs(metric_point.value - baseline.mean),
                'z_score': abs(metric_point.value - baseline.mean) / (baseline.std + 1e-8),
                'percentile_position': self._calculate_percentile_position(metric_point.value, baseline)
            })

        feature_vector = np.array([[features[col] for col in sorted(features.keys())]])

        # Scale features
        if model.scaler:
            feature_vector = model.scaler.transform(feature_vector)

        # Get anomaly score based on model type
        if model.model_type == "isolation_forest":
            # Isolation Forest returns -1 for anomalies, 1 for normal
            decision = model.model_object.decision_function(feature_vector)[0]
            # Convert to 0-1 score (higher = more anomalous)
            score = max(0, (0.5 - decision) * 2)
        elif model.model_type == "random_forest":
            # Get probability of being anomalous
            proba = model.model_object.predict_proba(feature_vector)[0]
            score = proba[1] if len(proba) > 1 else 0.0
        else:
            return None

        return min(1.0, max(0.0, score))

    def _calculate_percentile_position(self, value: float, baseline: BaselineProfile) -> float:
        """Calculate what percentile the value falls into"""
        if value <= baseline.percentiles[5]:
            return 0.05
        elif value <= baseline.percentiles[25]:
            return 0.25
        elif value <= baseline.percentiles[75]:
            return 0.75
        elif value <= baseline.percentiles[95]:
            return 0.95
        else:
            return 0.99

    def _determine_severity(self, score: float) -> AnomalySeverity:
        """Determine anomaly severity from score"""
        if score >= 0.9:
            return AnomalySeverity.CRITICAL
        elif score >= 0.8:
            return AnomalySeverity.HIGH
        elif score >= 0.7:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW


class StatisticalAnomalyDetector:
    """Statistical anomaly detection using z-scores, IQR, and other methods"""

    def __init__(self):
        self.detection_methods = {
            'z_score': self._z_score_detection,
            'iqr': self._iqr_detection,
            'modified_z_score': self._modified_z_score_detection,
            'grubbs_test': self._grubbs_test_detection
        }

    async def detect_anomaly(self, metric_point: MetricPoint, baseline: BaselineProfile) -> Optional[AnomalyDetection]:
        """Detect anomaly using statistical methods"""
        detections = []

        for method_name, method_func in self.detection_methods.items():
            try:
                detection = method_func(metric_point, baseline)
                if detection:
                    detections.append((method_name, detection))
            except Exception as e:
                logging.debug(f"Statistical method {method_name} failed: {e}")

        if not detections:
            return None

        # Use the highest severity detection
        detections.sort(key=lambda x: x[1].severity.value, reverse=True)
        best_detection = detections[0][1]

        # Add context about all methods
        best_detection.context['statistical_methods'] = {
            method: detection.deviation_score for method, detection in detections
        }

        return best_detection

    def _z_score_detection(self, metric_point: MetricPoint, baseline: BaselineProfile) -> Optional[AnomalyDetection]:
        """Z-score based anomaly detection"""
        if baseline.std == 0:
            return None

        z_score = abs(metric_point.value - baseline.mean) / baseline.std

        if z_score > 3.0:  # 3-sigma rule
            severity = AnomalySeverity.HIGH if z_score > 4.0 else AnomalySeverity.MEDIUM

            return AnomalyDetection(
                id=f"zscore_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.STATISTICAL,
                severity=severity,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=baseline.mean,
                deviation_score=z_score,
                confidence=min(1.0, z_score / 5.0),
                description=f"Z-score anomaly: {z_score:.2f} standard deviations from mean"
            )

        return None

    def _iqr_detection(self, metric_point: MetricPoint, baseline: BaselineProfile) -> Optional[AnomalyDetection]:
        """Interquartile Range based anomaly detection"""
        q1 = baseline.percentiles[25]
        q3 = baseline.percentiles[75]
        iqr = q3 - q1

        if iqr == 0:
            return None

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        if metric_point.value < lower_bound or metric_point.value > upper_bound:
            # Calculate how far outside the bounds
            if metric_point.value < lower_bound:
                deviation = (lower_bound - metric_point.value) / iqr
            else:
                deviation = (metric_point.value - upper_bound) / iqr

            severity = AnomalySeverity.HIGH if deviation > 2.0 else AnomalySeverity.MEDIUM

            return AnomalyDetection(
                id=f"iqr_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.STATISTICAL,
                severity=severity,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=(q1 + q3) / 2,
                deviation_score=deviation,
                confidence=min(1.0, deviation / 3.0),
                description=f"IQR anomaly: {deviation:.2f} IQRs outside normal range"
            )

        return None

    def _modified_z_score_detection(self, metric_point: MetricPoint, baseline: BaselineProfile) -> Optional[AnomalyDetection]:
        """Modified Z-score using median and MAD"""
        mad = statistics.median([abs(x - baseline.median) for x in [baseline.mean, baseline.min_value, baseline.max_value]])

        if mad == 0:
            return None

        modified_z_score = 0.6745 * (metric_point.value - baseline.median) / mad

        if abs(modified_z_score) > 3.5:
            severity = AnomalySeverity.HIGH if abs(modified_z_score) > 5.0 else AnomalySeverity.MEDIUM

            return AnomalyDetection(
                id=f"modified_zscore_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.STATISTICAL,
                severity=severity,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=baseline.median,
                deviation_score=abs(modified_z_score),
                confidence=min(1.0, abs(modified_z_score) / 6.0),
                description=f"Modified Z-score anomaly: {modified_z_score:.2f}"
            )

        return None

    def _grubbs_test_detection(self, metric_point: MetricPoint, baseline: BaselineProfile) -> Optional[AnomalyDetection]:
        """Grubbs test for outliers"""
        if baseline.std == 0 or baseline.sample_count < 7:
            return None

        z_score = abs(metric_point.value - baseline.mean) / baseline.std
        n = baseline.sample_count

        # Critical value for Grubbs test (approximate)
        from scipy import stats
        t_critical = stats.t.ppf(1 - 0.05/(2*n), n-2)
        grubbs_critical = ((n-1) / math.sqrt(n)) * math.sqrt(t_critical**2 / (n-2 + t_critical**2))

        if z_score > grubbs_critical:
            severity = AnomalySeverity.HIGH if z_score > grubbs_critical * 1.5 else AnomalySeverity.MEDIUM

            return AnomalyDetection(
                id=f"grubbs_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.STATISTICAL,
                severity=severity,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=baseline.mean,
                deviation_score=z_score,
                confidence=min(1.0, z_score / (grubbs_critical * 2)),
                description=f"Grubbs test outlier: score {z_score:.2f} > critical {grubbs_critical:.2f}"
            )

        return None


class AdvancedAnomalyDetector:
    """Main advanced anomaly detection system combining multiple approaches"""

    def __init__(self, db_path: str = "/var/lib/synos/anomaly_detector.db"):
        self.db_path = Path(db_path)
        self.baseline_manager = BaselineManager(str(self.db_path))
        self.ml_detector = MLAnomalyDetector()
        self.statistical_detector = StatisticalAnomalyDetector()

        self.recent_anomalies: deque = deque(maxlen=1000)
        self.false_positive_tracker: Dict[str, int] = defaultdict(int)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    source TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    key TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    time_window TEXT NOT NULL,
                    mean_val REAL NOT NULL,
                    std_val REAL NOT NULL,
                    median_val REAL NOT NULL,
                    percentiles TEXT NOT NULL,
                    min_val REAL NOT NULL,
                    max_val REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    seasonal_patterns TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS anomaly_detections (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    observed_value REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    deviation_score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT,
                    context TEXT,
                    false_positive BOOLEAN DEFAULT FALSE,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_models (
                    model_name TEXT PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    metric_patterns TEXT NOT NULL,
                    model_data BLOB,
                    scaler_data BLOB,
                    training_accuracy REAL,
                    last_trained TIMESTAMP,
                    feature_importance TEXT
                )
            """)

            conn.commit()

    async def add_metric(self, metric_point: MetricPoint):
        """Add new metric point and check for anomalies"""
        # Store metric
        await self._store_metric(metric_point)

        # Update baseline
        self.baseline_manager.add_metric_point(metric_point)

        # Detect anomalies
        anomalies = await self.detect_anomalies(metric_point)

        # Process detected anomalies
        for anomaly in anomalies:
            await self._process_anomaly(anomaly)

        return anomalies

    async def detect_anomalies(self, metric_point: MetricPoint) -> List[AnomalyDetection]:
        """Detect anomalies using all available methods"""
        anomalies = []

        # Get baseline for statistical analysis
        baseline = self.baseline_manager.get_baseline(
            metric_point.metric_name,
            metric_point.source
        )

        # Statistical detection
        if baseline and not self.baseline_manager.is_baseline_stale(baseline):
            statistical_anomaly = await self.statistical_detector.detect_anomaly(metric_point, baseline)
            if statistical_anomaly:
                anomalies.append(statistical_anomaly)

        # ML-based detection
        ml_anomaly = await self.ml_detector.detect_anomaly(metric_point, baseline)
        if ml_anomaly:
            anomalies.append(ml_anomaly)

        # Additional domain-specific detections
        domain_anomalies = await self._detect_domain_specific_anomalies(metric_point, baseline)
        anomalies.extend(domain_anomalies)

        return anomalies

    async def _detect_domain_specific_anomalies(self, metric_point: MetricPoint, baseline: Optional[BaselineProfile]) -> List[AnomalyDetection]:
        """Detect domain-specific anomalies based on metric type"""
        anomalies = []

        # Network-specific anomalies
        if 'network' in metric_point.metric_name.lower():
            anomaly = await self._detect_network_anomaly(metric_point, baseline)
            if anomaly:
                anomalies.append(anomaly)

        # Performance-specific anomalies
        if any(keyword in metric_point.metric_name.lower() for keyword in ['cpu', 'memory', 'disk', 'latency']):
            anomaly = await self._detect_performance_anomaly(metric_point, baseline)
            if anomaly:
                anomalies.append(anomaly)

        # Security-specific anomalies
        if any(keyword in metric_point.metric_name.lower() for keyword in ['failed_login', 'privilege', 'suspicious']):
            anomaly = await self._detect_security_anomaly(metric_point, baseline)
            if anomaly:
                anomalies.append(anomaly)

        return anomalies

    async def _detect_network_anomaly(self, metric_point: MetricPoint, baseline: Optional[BaselineProfile]) -> Optional[AnomalyDetection]:
        """Detect network-specific anomalies"""
        # Example: Sudden spike in connection count
        if 'connection_count' in metric_point.metric_name and baseline:
            if metric_point.value > baseline.mean + 5 * baseline.std:
                return AnomalyDetection(
                    id=f"network_anomaly_{int(time.time() * 1000)}",
                    timestamp=metric_point.timestamp,
                    anomaly_type=AnomalyType.NETWORK,
                    severity=AnomalySeverity.HIGH,
                    metric_name=metric_point.metric_name,
                    observed_value=metric_point.value,
                    expected_value=baseline.mean,
                    deviation_score=(metric_point.value - baseline.mean) / baseline.std,
                    confidence=0.9,
                    description="Unusual network connection spike detected",
                    remediation_suggestions=["Check for DDoS attack", "Verify network configuration"]
                )
        return None

    async def _detect_performance_anomaly(self, metric_point: MetricPoint, baseline: Optional[BaselineProfile]) -> Optional[AnomalyDetection]:
        """Detect performance-specific anomalies"""
        # Example: CPU usage > 95%
        if 'cpu' in metric_point.metric_name and metric_point.value > 95.0:
            return AnomalyDetection(
                id=f"performance_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.PERFORMANCE,
                severity=AnomalySeverity.CRITICAL,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=baseline.mean if baseline else 50.0,
                deviation_score=metric_point.value / 100.0,
                confidence=0.95,
                description="Critical CPU usage detected",
                remediation_suggestions=["Identify resource-intensive processes", "Scale up resources"]
            )
        return None

    async def _detect_security_anomaly(self, metric_point: MetricPoint, baseline: Optional[BaselineProfile]) -> Optional[AnomalyDetection]:
        """Detect security-specific anomalies"""
        # Example: Multiple failed login attempts
        if 'failed_login' in metric_point.metric_name and metric_point.value > 10:
            return AnomalyDetection(
                id=f"security_anomaly_{int(time.time() * 1000)}",
                timestamp=metric_point.timestamp,
                anomaly_type=AnomalyType.SECURITY,
                severity=AnomalySeverity.HIGH,
                metric_name=metric_point.metric_name,
                observed_value=metric_point.value,
                expected_value=baseline.mean if baseline else 0.0,
                deviation_score=metric_point.value,
                confidence=0.9,
                description="Multiple failed login attempts detected",
                remediation_suggestions=["Investigate potential brute force attack", "Enable account lockout"]
            )
        return None

    async def _process_anomaly(self, anomaly: AnomalyDetection):
        """Process detected anomaly"""
        # Check for false positives
        anomaly.false_positive_probability = self._calculate_false_positive_probability(anomaly)

        # Store anomaly
        await self._store_anomaly(anomaly)

        # Add to recent anomalies
        self.recent_anomalies.append(anomaly)

        # Log based on severity
        if anomaly.severity == AnomalySeverity.CRITICAL:
            logging.critical(f"CRITICAL ANOMALY: {anomaly.description}")
        elif anomaly.severity == AnomalySeverity.HIGH:
            logging.error(f"HIGH ANOMALY: {anomaly.description}")
        elif anomaly.severity == AnomalySeverity.MEDIUM:
            logging.warning(f"MEDIUM ANOMALY: {anomaly.description}")
        else:
            logging.info(f"LOW ANOMALY: {anomaly.description}")

    def _calculate_false_positive_probability(self, anomaly: AnomalyDetection) -> float:
        """Calculate probability that this is a false positive"""
        # Simple heuristic based on historical false positives
        metric_key = f"{anomaly.metric_name}_{anomaly.anomaly_type.value}"
        historical_fps = self.false_positive_tracker.get(metric_key, 0)

        # Base false positive rate
        base_rate = 0.1

        # Adjust based on historical data
        if historical_fps > 5:
            base_rate += 0.3
        elif historical_fps > 2:
            base_rate += 0.1

        # Adjust based on confidence
        confidence_adjustment = (1.0 - anomaly.confidence) * 0.2

        return min(0.9, base_rate + confidence_adjustment)

    async def train_ml_models(self):
        """Train ML models using historical data"""
        # Load training data from database
        training_data = await self._load_training_data()

        if len(training_data) > 100:
            await self.ml_detector.train_models(training_data)
            await self._save_ml_models()
            logging.info("ML models trained and saved")
        else:
            logging.warning("Insufficient training data for ML models")

    async def _load_training_data(self) -> List[Dict[str, Any]]:
        """Load historical data for training"""
        training_data = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT m.timestamp, m.metric_name, m.value, m.source, m.metadata,
                           a.id IS NOT NULL as is_anomaly
                    FROM metrics m
                    LEFT JOIN anomaly_detections a ON m.metric_name = a.metric_name
                        AND ABS(JULIANDAY(m.timestamp) - JULIANDAY(a.timestamp)) < 0.0007  -- Within 1 minute
                    ORDER BY m.timestamp DESC
                    LIMIT 10000
                """)

                for row in cursor.fetchall():
                    timestamp_str, metric_name, value, source, metadata_str, is_anomaly = row

                    # Determine metric type from name
                    metric_type = self._classify_metric_type(metric_name)

                    training_data.append({
                        'timestamp': datetime.fromisoformat(timestamp_str),
                        'metric_name': metric_name,
                        'metric_type': metric_type,
                        'value': value,
                        'source': source,
                        'metadata': json.loads(metadata_str or '{}'),
                        'is_anomaly': bool(is_anomaly)
                    })

        except Exception as e:
            logging.error(f"Failed to load training data: {e}")

        return training_data

    def _classify_metric_type(self, metric_name: str) -> str:
        """Classify metric type from name"""
        name_lower = metric_name.lower()

        if any(keyword in name_lower for keyword in ['network', 'connection', 'bandwidth']):
            return 'network'
        elif any(keyword in name_lower for keyword in ['cpu', 'memory', 'disk', 'performance']):
            return 'performance'
        elif any(keyword in name_lower for keyword in ['security', 'login', 'auth', 'privilege']):
            return 'security'
        elif any(keyword in name_lower for keyword in ['process', 'thread', 'pid']):
            return 'process'
        elif any(keyword in name_lower for keyword in ['file', 'directory', 'filesystem']):
            return 'filesystem'
        else:
            return 'generic'

    async def _save_ml_models(self):
        """Save trained ML models to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for model_name, model in self.ml_detector.models.items():
                    model_data = joblib.dumps(model.model_object)
                    scaler_data = joblib.dumps(model.scaler) if model.scaler else None

                    conn.execute("""
                        INSERT OR REPLACE INTO ml_models
                        (model_name, model_type, metric_patterns, model_data, scaler_data,
                         training_accuracy, last_trained, feature_importance)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        model_name, model.model_type, json.dumps(model.metric_patterns),
                        model_data, scaler_data, model.training_accuracy,
                        model.last_trained, json.dumps(model.feature_importance)
                    ))

                conn.commit()
        except Exception as e:
            logging.error(f"Failed to save ML models: {e}")

    async def _store_metric(self, metric_point: MetricPoint):
        """Store metric point in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO metrics (timestamp, metric_name, value, source, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metric_point.timestamp, metric_point.metric_name, metric_point.value,
                    metric_point.source, json.dumps(metric_point.metadata)
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store metric: {e}")

    async def _store_anomaly(self, anomaly: AnomalyDetection):
        """Store anomaly detection in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO anomaly_detections
                    (id, timestamp, anomaly_type, severity, metric_name, observed_value,
                     expected_value, deviation_score, confidence, description, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    anomaly.id, anomaly.timestamp, anomaly.anomaly_type.value,
                    anomaly.severity.value, anomaly.metric_name, anomaly.observed_value,
                    anomaly.expected_value, anomaly.deviation_score, anomaly.confidence,
                    anomaly.description, json.dumps(anomaly.context)
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store anomaly: {e}")

    def mark_false_positive(self, anomaly_id: str):
        """Mark anomaly as false positive"""
        for anomaly in self.recent_anomalies:
            if anomaly.id == anomaly_id:
                metric_key = f"{anomaly.metric_name}_{anomaly.anomaly_type.value}"
                self.false_positive_tracker[metric_key] += 1
                break

        # Update database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE anomaly_detections SET false_positive = TRUE WHERE id = ?
                """, (anomaly_id,))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to mark false positive: {e}")

    def get_recent_anomalies(self, limit: int = 50) -> List[AnomalyDetection]:
        """Get recent anomaly detections"""
        return list(self.recent_anomalies)[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        recent = list(self.recent_anomalies)

        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)

        for anomaly in recent:
            severity_counts[anomaly.severity.name] += 1
            type_counts[anomaly.anomaly_type.name] += 1

        return {
            'total_anomalies': len(recent),
            'severity_distribution': dict(severity_counts),
            'type_distribution': dict(type_counts),
            'baselines_count': len(self.baseline_manager.baselines),
            'ml_models_count': len(self.ml_detector.models),
            'false_positive_rate': sum(self.false_positive_tracker.values()) / max(1, len(recent))
        }


async def main():
    """Example usage of Advanced Anomaly Detection System"""
    logging.basicConfig(level=logging.INFO)

    detector = AdvancedAnomalyDetector()

    # Simulate some metrics
    print("Simulating metrics and detecting anomalies...")

    for i in range(100):
        # Normal CPU usage
        normal_cpu = MetricPoint(
            timestamp=datetime.now() - timedelta(minutes=i),
            metric_name="cpu_usage_percent",
            value=20 + 10 * math.sin(i * 0.1) + np.random.normal(0, 2),
            source="system_monitor"
        )

        anomalies = await detector.add_metric(normal_cpu)

        # Add some anomalous points
        if i == 50:
            anomalous_cpu = MetricPoint(
                timestamp=datetime.now(),
                metric_name="cpu_usage_percent",
                value=95.0,  # Spike
                source="system_monitor"
            )
            anomalies = await detector.add_metric(anomalous_cpu)
            if anomalies:
                print(f"Detected {len(anomalies)} anomalies for CPU spike")

    # Train ML models
    await detector.train_ml_models()

    # Show statistics
    stats = detector.get_statistics()
    print(f"Detection Statistics: {stats}")

    # Show recent anomalies
    recent_anomalies = detector.get_recent_anomalies(10)
    print(f"Recent anomalies: {len(recent_anomalies)}")
    for anomaly in recent_anomalies:
        print(f"  - {anomaly.severity.name}: {anomaly.description}")


if __name__ == "__main__":
    asyncio.run(main())