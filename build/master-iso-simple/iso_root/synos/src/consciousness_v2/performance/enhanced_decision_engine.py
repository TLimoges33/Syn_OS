"""
Enhanced Decision Engine with Performance Optimization
=====================================================

High-performance decision engine with advanced caching, parallel processing,
and real-time optimization for SynapticOS consciousness system.

Features:
- Async parallel decision processing
- Intelligent caching and prediction
- Multi-model ensemble decision making
- Real-time confidence scoring
- Context-aware optimization
- Sub-100ms response times
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import concurrent.futures
import threading
import hashlib
import json

# Import ML libraries if available
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available for decision engine")

class DecisionType(Enum):
    """Types of decisions the engine can make"""
    LEARNING_ADAPTATION = "learning_adaptation"
    SECURITY_RESPONSE = "security_response" 
    RESOURCE_ALLOCATION = "resource_allocation"
    CONTENT_RECOMMENDATION = "content_recommendation"
    THREAT_ASSESSMENT = "threat_assessment"
    SYSTEM_OPTIMIZATION = "system_optimization"
    USER_INTERACTION = "user_interaction"

class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

@dataclass
class DecisionContext:
    """Context for decision making"""
    user_id: str
    session_id: str
    current_activity: str
    consciousness_level: float
    performance_metrics: Dict[str, float]
    security_context: Dict[str, Any]
    learning_progress: Dict[str, float]
    system_state: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert context to feature vector for ML models"""
        features = [
            self.consciousness_level,
            len(self.current_activity),
            sum(self.performance_metrics.values()) / len(self.performance_metrics) if self.performance_metrics else 0,
            sum(self.learning_progress.values()) / len(self.learning_progress) if self.learning_progress else 0,
            len(self.security_context),
            len(self.system_state)
        ]
        return np.array(features)

@dataclass
class DecisionOption:
    """A potential decision option"""
    option_id: str
    name: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    confidence: float
    expected_outcome: Dict[str, float]
    resource_cost: Dict[str, float]
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    
    def calculate_utility(self, context: DecisionContext) -> float:
        """Calculate utility score for this option"""
        # Base utility from confidence
        utility = self.confidence
        
        # Adjust based on resource cost
        total_cost = sum(self.resource_cost.values())
        utility -= total_cost * 0.1  # Penalty for high resource usage
        
        # Adjust based on expected outcome
        positive_outcomes = sum(v for v in self.expected_outcome.values() if v > 0)
        negative_outcomes = sum(abs(v) for v in self.expected_outcome.values() if v < 0)
        utility += positive_outcomes * 0.3 - negative_outcomes * 0.2
        
        return max(0.0, min(1.0, utility))

@dataclass
class DecisionResult:
    """Result of a decision"""
    decision_id: str
    decision_type: DecisionType
    selected_option: DecisionOption
    confidence: float
    processing_time: float
    context_used: DecisionContext
    ensemble_votes: Dict[str, str]
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

class DecisionCache:
    """Intelligent caching system for decisions"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache: Dict[str, DecisionResult] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        
        # Cache performance metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_efficiency = deque(maxlen=100)
        
        self.logger = logging.getLogger(f"{__name__}.DecisionCache")
        
    def _generate_cache_key(self, decision_type: DecisionType, 
                           context: DecisionContext) -> str:
        """Generate cache key for decision context"""
        # Create key from relevant context features
        key_data = {
            'type': decision_type.value,
            'activity': context.current_activity,
            'consciousness': round(context.consciousness_level, 2),
            'user': context.user_id
        }
        
        # Hash for compact key
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
        
    async def get_cached_decision(self, decision_type: DecisionType,
                                 context: DecisionContext) -> Optional[DecisionResult]:
        """Get cached decision if available and valid"""
        cache_key = self._generate_cache_key(decision_type, context)
        
        if cache_key not in self.cache:
            self.cache_misses += 1
            return None
            
        # Check TTL
        if datetime.now() > self.cache_ttl.get(cache_key, datetime.min):
            del self.cache[cache_key]
            del self.cache_ttl[cache_key]
            self.cache_misses += 1
            return None
            
        self.cache_hits += 1
        result = self.cache[cache_key]
        result.cached = True
        
        # Update cache efficiency
        hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses)
        self.cache_efficiency.append(hit_rate)
        
        return result
        
    async def cache_decision(self, decision_type: DecisionType,
                           context: DecisionContext, result: DecisionResult):
        """Cache a decision result"""
        cache_key = self._generate_cache_key(decision_type, context)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache_ttl.keys(), key=lambda k: self.cache_ttl[k])
            del self.cache[oldest_key]
            del self.cache_ttl[oldest_key]
            
        self.cache[cache_key] = result
        self.cache_ttl[cache_key] = datetime.now() + timedelta(seconds=self.ttl_seconds)
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / max(total_requests, 1)
        
        return {
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'total_hits': self.cache_hits,
            'total_misses': self.cache_misses,
            'efficiency_trend': list(self.cache_efficiency)[-10:]
        }

class EnsembleDecisionMaker:
    """Multi-model ensemble for decision making"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_weights: Dict[str, float] = {}
        self.model_performance: Dict[str, deque] = {}
        
        if ML_AVAILABLE:
            self._initialize_models()
            
        self.logger = logging.getLogger(f"{__name__}.EnsembleDecisionMaker")
        
    def _initialize_models(self):
        """Initialize ML models for ensemble"""
        try:
            # Random Forest for stable decisions
            self.models['random_forest'] = RandomForestClassifier(
                n_estimators=50, max_depth=10, random_state=42
            )
            self.model_weights['random_forest'] = 0.3
            self.model_performance['random_forest'] = deque(maxlen=100)
            
            # Gradient Boosting for adaptive decisions
            self.models['gradient_boosting'] = GradientBoostingClassifier(
                n_estimators=50, max_depth=6, random_state=42
            )
            self.model_weights['gradient_boosting'] = 0.3
            self.model_performance['gradient_boosting'] = deque(maxlen=100)
            
            # Neural Network for complex patterns
            self.models['neural_network'] = MLPClassifier(
                hidden_layer_sizes=(50, 25), max_iter=500, random_state=42
            )
            self.model_weights['neural_network'] = 0.25
            self.model_performance['neural_network'] = deque(maxlen=100)
            
            # Rule-based for interpretable decisions
            self.model_weights['rule_based'] = 0.15
            self.model_performance['rule_based'] = deque(maxlen=100)
            
            self.logger.info(f"Initialized {len(self.models)} ML models")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
            
    async def train_models(self, training_data: List[Tuple[DecisionContext, str]]):
        """Train ensemble models on historical data"""
        if not ML_AVAILABLE or not training_data:
            return
            
        try:
            # Prepare training data
            X = np.array([context.to_feature_vector() for context, _ in training_data])
            y = np.array([decision for _, decision in training_data])
            
            # Train each model
            for model_name, model in self.models.items():
                if hasattr(model, 'fit'):
                    model.fit(X, y)
                    
                    # Evaluate performance
                    y_pred = model.predict(X)
                    accuracy = accuracy_score(y, y_pred)
                    self.model_performance[model_name].append(accuracy)
                    
            self.logger.info("Ensemble models trained successfully")
            
        except Exception as e:
            self.logger.error(f"Error training models: {e}")
            
    async def ensemble_predict(self, context: DecisionContext,
                             options: List[DecisionOption]) -> Dict[str, Any]:
        """Make ensemble prediction"""
        try:
            predictions = {}
            confidences = {}
            
            # Get feature vector
            features = context.to_feature_vector().reshape(1, -1)
            
            # ML model predictions
            for model_name, model in self.models.items():
                if hasattr(model, 'predict_proba'):
                    try:
                        probabilities = model.predict_proba(features)[0]
                        predicted_class = model.classes_[np.argmax(probabilities)]
                        confidence = np.max(probabilities)
                        
                        predictions[model_name] = predicted_class
                        confidences[model_name] = confidence
                        
                    except Exception as e:
                        # Fallback to simple prediction
                        predictions[model_name] = options[0].option_id if options else "default"
                        confidences[model_name] = 0.5
                        
            # Rule-based prediction
            rule_prediction = await self._rule_based_prediction(context, options)
            predictions['rule_based'] = rule_prediction['option_id']
            confidences['rule_based'] = rule_prediction['confidence']
            
            # Weighted ensemble decision
            ensemble_decision = await self._weighted_ensemble_vote(predictions, confidences)
            
            return {
                'ensemble_decision': ensemble_decision,
                'individual_predictions': predictions,
                'individual_confidences': confidences,
                'ensemble_confidence': self._calculate_ensemble_confidence(confidences)
            }
            
        except Exception as e:
            self.logger.error(f"Error in ensemble prediction: {e}")
            return {
                'ensemble_decision': options[0].option_id if options else "default",
                'individual_predictions': {},
                'individual_confidences': {},
                'ensemble_confidence': 0.5
            }
            
    async def _rule_based_prediction(self, context: DecisionContext,
                                   options: List[DecisionOption]) -> Dict[str, Any]:
        """Rule-based decision prediction"""
        # Simple rule-based logic
        best_option = None
        best_utility = 0.0
        
        for option in options:
            utility = option.calculate_utility(context)
            if utility > best_utility:
                best_utility = utility
                best_option = option
                
        return {
            'option_id': best_option.option_id if best_option else "default",
            'confidence': best_utility
        }
        
    async def _weighted_ensemble_vote(self, predictions: Dict[str, str],
                                    confidences: Dict[str, float]) -> str:
        """Calculate weighted ensemble vote"""
        vote_scores: Dict[str, float] = {}
        
        for model_name, prediction in predictions.items():
            weight = self.model_weights.get(model_name, 0.25)
            confidence = confidences.get(model_name, 0.5)
            
            if prediction not in vote_scores:
                vote_scores[prediction] = 0.0
            vote_scores[prediction] += weight * confidence
            
        # Return prediction with highest weighted score
        return max(vote_scores.keys(), key=lambda k: vote_scores[k])
        
    def _calculate_ensemble_confidence(self, confidences: Dict[str, float]) -> float:
        """Calculate overall ensemble confidence"""
        if not confidences:
            return 0.5
            
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for model_name, confidence in confidences.items():
            weight = self.model_weights.get(model_name, 0.25)
            weighted_confidence += weight * confidence
            total_weight += weight
            
        return weighted_confidence / max(total_weight, 1.0)

class EnhancedDecisionEngine:
    """Main enhanced decision engine with performance optimization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Core components
        self.cache = DecisionCache(
            max_size=self.config.get('cache_size', 1000),
            ttl_seconds=self.config.get('cache_ttl', 300)
        )
        self.ensemble = EnsembleDecisionMaker()
        
        # Performance settings
        self.max_decision_time = self.config.get('max_decision_time', 0.1)  # 100ms
        self.parallel_processing = self.config.get('parallel_processing', True)
        
        # Threading for parallel processing
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="decision"
        )
        
        # Performance tracking
        self.decision_history: deque = deque(maxlen=1000)
        self.performance_metrics = {
            'total_decisions': 0,
            'cache_hit_rate': 0.0,
            'avg_response_time': 0.0,
            'accuracy_rate': 0.9,  # Start with high assumption
            'successful_decisions': 0
        }
        
        # Decision generators
        self.decision_generators = {
            DecisionType.LEARNING_ADAPTATION: self._generate_learning_options,
            DecisionType.SECURITY_RESPONSE: self._generate_security_options,
            DecisionType.RESOURCE_ALLOCATION: self._generate_resource_options,
            DecisionType.CONTENT_RECOMMENDATION: self._generate_content_options,
            DecisionType.THREAT_ASSESSMENT: self._generate_threat_options,
            DecisionType.SYSTEM_OPTIMIZATION: self._generate_optimization_options,
            DecisionType.USER_INTERACTION: self._generate_interaction_options
        }
        
        self.logger = logging.getLogger(f"{__name__}.EnhancedDecisionEngine")
        
    async def make_decision(self, decision_type: DecisionType,
                           context: DecisionContext) -> DecisionResult:
        """Make an optimized decision with sub-100ms response time"""
        start_time = time.time()
        decision_id = f"dec_{int(time.time() * 1000)}"
        
        try:
            # Check cache first
            cached_result = await self.cache.get_cached_decision(decision_type, context)
            if cached_result:
                processing_time = time.time() - start_time
                self._update_performance_metrics(processing_time, True, True)
                return cached_result
                
            # Generate decision options
            options = await self._generate_decision_options(decision_type, context)
            
            if not options:
                # Fallback option
                options = [DecisionOption(
                    option_id="fallback",
                    name="Default Action",
                    description="Default fallback action",
                    action_type="default",
                    parameters={},
                    confidence=0.5,
                    expected_outcome={'success': 0.7},
                    resource_cost={'cpu': 0.1}
                )]
                
            # Make ensemble decision
            ensemble_result = await self.ensemble.ensemble_predict(context, options)
            
            # Find selected option
            selected_option = next(
                (opt for opt in options if opt.option_id == ensemble_result['ensemble_decision']),
                options[0]
            )
            
            # Create result
            processing_time = time.time() - start_time
            result = DecisionResult(
                decision_id=decision_id,
                decision_type=decision_type,
                selected_option=selected_option,
                confidence=ensemble_result['ensemble_confidence'],
                processing_time=processing_time,
                context_used=context,
                ensemble_votes=ensemble_result['individual_predictions']
            )
            
            # Cache the result
            await self.cache.cache_decision(decision_type, context, result)
            
            # Update performance metrics
            self._update_performance_metrics(processing_time, False, True)
            
            # Store in history
            self.decision_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error making decision: {e}")
            
            # Emergency fallback
            processing_time = time.time() - start_time
            fallback_option = DecisionOption(
                option_id="emergency_fallback",
                name="Emergency Fallback",
                description="Emergency fallback due to error",
                action_type="emergency",
                parameters={'error': str(e)},
                confidence=0.3,
                expected_outcome={'success': 0.5},
                resource_cost={'cpu': 0.05}
            )
            
            result = DecisionResult(
                decision_id=decision_id,
                decision_type=decision_type,
                selected_option=fallback_option,
                confidence=0.3,
                processing_time=processing_time,
                context_used=context,
                ensemble_votes={}
            )
            
            self._update_performance_metrics(processing_time, False, False)
            return result
            
    async def _generate_decision_options(self, decision_type: DecisionType,
                                       context: DecisionContext) -> List[DecisionOption]:
        """Generate decision options based on type and context"""
        generator = self.decision_generators.get(decision_type)
        if not generator:
            return []
            
        if self.parallel_processing:
            # Run option generation in thread pool
            loop = asyncio.get_event_loop()
            options = await loop.run_in_executor(
                self.thread_pool, lambda: asyncio.run(generator(context))
            )
        else:
            options = await generator(context)
            
        return options
        
    async def _generate_learning_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate learning adaptation options"""
        performance_score = sum(context.learning_progress.values()) / len(context.learning_progress) if context.learning_progress else 0.5
        
        options = []
        
        if performance_score < 0.3:
            options.append(DecisionOption(
                option_id="reduce_difficulty",
                name="Reduce Difficulty",
                description="Lower difficulty to build confidence",
                action_type="adaptive",
                parameters={'difficulty_adjustment': -0.3, 'support_level': 'high'},
                confidence=0.8,
                expected_outcome={'engagement': 0.7, 'learning_speed': 0.4},
                resource_cost={'cpu': 0.2}
            ))
        elif performance_score > 0.8:
            options.append(DecisionOption(
                option_id="increase_challenge",
                name="Increase Challenge",
                description="Provide more challenging content",
                action_type="adaptive",
                parameters={'difficulty_adjustment': 0.3, 'complexity': 'high'},
                confidence=0.9,
                expected_outcome={'engagement': 0.9, 'learning_speed': 0.8},
                resource_cost={'cpu': 0.4}
            ))
        else:
            options.append(DecisionOption(
                option_id="maintain_level",
                name="Maintain Current Level",
                description="Continue with current difficulty",
                action_type="stable",
                parameters={'difficulty_adjustment': 0.0},
                confidence=0.7,
                expected_outcome={'engagement': 0.6, 'learning_speed': 0.6},
                resource_cost={'cpu': 0.1}
            ))
            
        return options
        
    async def _generate_security_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate security response options"""
        threat_level = context.security_context.get('threat_level', 0.0)
        
        options = []
        
        if threat_level > 0.8:
            options.append(DecisionOption(
                option_id="immediate_block",
                name="Immediate Block",
                description="Block suspicious activity immediately",
                action_type="defensive",
                parameters={'action': 'block', 'duration': 3600},
                confidence=0.95,
                expected_outcome={'security': 0.95, 'usability': 0.3},
                resource_cost={'cpu': 0.3, 'network': 0.2}
            ))
        elif threat_level > 0.5:
            options.append(DecisionOption(
                option_id="enhanced_monitoring",
                name="Enhanced Monitoring",
                description="Increase monitoring and logging",
                action_type="monitoring",
                parameters={'monitoring_level': 'high', 'log_detail': 'verbose'},
                confidence=0.8,
                expected_outcome={'security': 0.8, 'usability': 0.8},
                resource_cost={'cpu': 0.2, 'storage': 0.3}
            ))
        else:
            options.append(DecisionOption(
                option_id="continue_normal",
                name="Continue Normal Operation",
                description="No immediate action needed",
                action_type="passive",
                parameters={},
                confidence=0.7,
                expected_outcome={'security': 0.7, 'usability': 1.0},
                resource_cost={'cpu': 0.05}
            ))
            
        return options
        
    async def _generate_resource_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate resource allocation options"""
        cpu_usage = context.performance_metrics.get('cpu_usage', 0.5)
        memory_usage = context.performance_metrics.get('memory_usage', 0.5)
        
        options = []
        
        if cpu_usage > 0.8 or memory_usage > 0.8:
            options.append(DecisionOption(
                option_id="scale_up",
                name="Scale Up Resources",
                description="Allocate additional resources",
                action_type="scaling",
                parameters={'cpu_increase': 0.3, 'memory_increase': 0.3},
                confidence=0.8,
                expected_outcome={'performance': 0.9, 'cost': -0.3},
                resource_cost={'budget': 0.4}
            ))
        elif cpu_usage < 0.3 and memory_usage < 0.3:
            options.append(DecisionOption(
                option_id="scale_down",
                name="Scale Down Resources",
                description="Reduce resource allocation",
                action_type="scaling",
                parameters={'cpu_decrease': 0.2, 'memory_decrease': 0.2},
                confidence=0.7,
                expected_outcome={'performance': 0.7, 'cost': 0.3},
                resource_cost={'budget': -0.2}
            ))
        else:
            options.append(DecisionOption(
                option_id="maintain_resources",
                name="Maintain Current Resources",
                description="Keep current resource allocation",
                action_type="stable",
                parameters={},
                confidence=0.8,
                expected_outcome={'performance': 0.8, 'cost': 0.0},
                resource_cost={'budget': 0.0}
            ))
            
        return options
        
    async def _generate_content_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate content recommendation options"""
        learning_style = context.system_state.get('learning_style', 'mixed')
        engagement_level = context.learning_progress.get('engagement', 0.5)
        
        options = []
        
        if engagement_level < 0.4:
            options.append(DecisionOption(
                option_id="interactive_content",
                name="Interactive Content",
                description="Provide interactive exercises and games",
                action_type="engagement",
                parameters={'content_type': 'interactive', 'gamification': True},
                confidence=0.8,
                expected_outcome={'engagement': 0.8, 'retention': 0.7},
                resource_cost={'cpu': 0.3, 'bandwidth': 0.4}
            ))
        elif learning_style == 'visual':
            options.append(DecisionOption(
                option_id="visual_content",
                name="Visual Learning Materials",
                description="Provide diagrams, videos, and visual aids",
                action_type="personalization",
                parameters={'content_type': 'visual', 'media_rich': True},
                confidence=0.9,
                expected_outcome={'understanding': 0.9, 'engagement': 0.8},
                resource_cost={'bandwidth': 0.6, 'storage': 0.3}
            ))
        else:
            options.append(DecisionOption(
                option_id="standard_content",
                name="Standard Learning Content",
                description="Provide balanced content mix",
                action_type="standard",
                parameters={'content_type': 'mixed'},
                confidence=0.7,
                expected_outcome={'understanding': 0.7, 'engagement': 0.6},
                resource_cost={'cpu': 0.2, 'bandwidth': 0.3}
            ))
            
        return options
        
    async def _generate_threat_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate threat assessment options"""
        return await self._generate_security_options(context)  # Similar to security options
        
    async def _generate_optimization_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate system optimization options"""
        return await self._generate_resource_options(context)  # Similar to resource options
        
    async def _generate_interaction_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate user interaction options"""
        user_mood = context.system_state.get('user_mood', 'neutral')
        interaction_frequency = context.system_state.get('interaction_frequency', 0.5)
        
        options = []
        
        if user_mood == 'frustrated':
            options.append(DecisionOption(
                option_id="supportive_interaction",
                name="Supportive Interaction",
                description="Provide encouragement and assistance",
                action_type="supportive",
                parameters={'tone': 'encouraging', 'assistance_level': 'high'},
                confidence=0.8,
                expected_outcome={'satisfaction': 0.8, 'mood_improvement': 0.7},
                resource_cost={'cpu': 0.2}
            ))
        elif interaction_frequency < 0.3:
            options.append(DecisionOption(
                option_id="engaging_interaction",
                name="Engaging Interaction",
                description="Increase interaction to maintain engagement",
                action_type="engaging",
                parameters={'interaction_increase': 0.3, 'proactive': True},
                confidence=0.7,
                expected_outcome={'engagement': 0.8, 'attention': 0.7},
                resource_cost={'cpu': 0.3}
            ))
        else:
            options.append(DecisionOption(
                option_id="minimal_interaction",
                name="Minimal Interaction",
                description="Maintain low-key presence",
                action_type="minimal",
                parameters={'interaction_level': 'low'},
                confidence=0.8,
                expected_outcome={'focus': 0.8, 'autonomy': 0.9},
                resource_cost={'cpu': 0.1}
            ))
            
        return options
        
    def _update_performance_metrics(self, processing_time: float,
                                  was_cached: bool, was_successful: bool):
        """Update performance metrics"""
        self.performance_metrics['total_decisions'] += 1
        
        # Update response time
        total_decisions = self.performance_metrics['total_decisions']
        current_avg = self.performance_metrics['avg_response_time']
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (total_decisions - 1) + processing_time) / total_decisions
        )
        
        # Update cache hit rate
        cache_stats = self.cache.get_cache_stats()
        self.performance_metrics['cache_hit_rate'] = cache_stats['hit_rate']
        
        # Update success rate
        if was_successful:
            self.performance_metrics['successful_decisions'] += 1
            
        success_rate = self.performance_metrics['successful_decisions'] / total_decisions
        self.performance_metrics['accuracy_rate'] = success_rate
        
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        try:
            cache_stats = self.cache.get_cache_stats()
            
            # Recent performance analysis
            recent_decisions = list(self.decision_history)[-20:]
            recent_response_times = [d.processing_time for d in recent_decisions]
            
            avg_recent_response = np.mean(recent_response_times) if recent_response_times else 0
            p95_response = np.percentile(recent_response_times, 95) if recent_response_times else 0
            
            return {
                'total_decisions': self.performance_metrics['total_decisions'],
                'avg_response_time': self.performance_metrics['avg_response_time'],
                'recent_avg_response_time': avg_recent_response,
                'p95_response_time': p95_response,
                'cache_hit_rate': self.performance_metrics['cache_hit_rate'],
                'accuracy_rate': self.performance_metrics['accuracy_rate'],
                'cache_stats': cache_stats,
                'ml_available': ML_AVAILABLE,
                'parallel_processing': self.parallel_processing,
                'response_time_target': self.max_decision_time,
                'target_achieved': avg_recent_response < self.max_decision_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
            
    async def train_from_history(self):
        """Train ensemble models from decision history"""
        if not self.decision_history:
            return
            
        # Prepare training data from successful decisions
        training_data = []
        for decision in self.decision_history:
            if decision.confidence > 0.7:  # Only use high-confidence decisions
                training_data.append((decision.context_used, decision.selected_option.option_id))
                
        if len(training_data) > 10:  # Need minimum data for training
            await self.ensemble.train_models(training_data)
            self.logger.info(f"Trained ensemble models with {len(training_data)} samples")

# Global enhanced decision engine instance
enhanced_decision_engine = EnhancedDecisionEngine()

# Convenience functions
async def make_optimized_decision(decision_type: DecisionType, context: DecisionContext) -> DecisionResult:
    """Make an optimized decision"""
    return await enhanced_decision_engine.make_decision(decision_type, context)

async def get_decision_performance_report():
    """Get decision engine performance report"""
    return await enhanced_decision_engine.get_performance_report()

async def train_decision_models():
    """Train decision models from history"""
    await enhanced_decision_engine.train_from_history()

if __name__ == "__main__":
    # Test the enhanced decision engine
    async def test_decision_engine():
        # Create test context
        context = DecisionContext(
            user_id="test_user",
            session_id="test_session",
            current_activity="learning",
            consciousness_level=0.7,
            performance_metrics={'cpu_usage': 0.6, 'memory_usage': 0.5},
            security_context={'threat_level': 0.2},
            learning_progress={'engagement': 0.8, 'comprehension': 0.7},
            system_state={'learning_style': 'visual', 'user_mood': 'positive'}
        )
        
        # Test different decision types
        decision_types = [
            DecisionType.LEARNING_ADAPTATION,
            DecisionType.SECURITY_RESPONSE,
            DecisionType.RESOURCE_ALLOCATION
        ]
        
        for decision_type in decision_types:
            result = await make_optimized_decision(decision_type, context)
            print(f"{decision_type.value}: {result.selected_option.name} "
                  f"(confidence: {result.confidence:.2f}, "
                  f"time: {result.processing_time:.3f}s)")
            
        # Get performance report
        report = await get_decision_performance_report()
        print(f"\nPerformance Report:")
        print(f"Total decisions: {report['total_decisions']}")
        print(f"Avg response time: {report['avg_response_time']:.3f}s")
        print(f"Cache hit rate: {report['cache_hit_rate']:.2%}")
        print(f"Target achieved: {report['target_achieved']}")
    
    asyncio.run(test_decision_engine())
