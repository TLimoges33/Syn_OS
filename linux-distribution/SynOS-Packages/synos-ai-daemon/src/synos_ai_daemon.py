#!/usr/bin/env python3
"""
SynOS AI Consciousness Daemon
Main daemon for neural darwinism consciousness framework

Implements:
- Neural consciousness processing
- Evolutionary population dynamics
- Adaptive learning engine
- System-wide consciousness integration
- Real-time pattern recognition
"""

import sys
import time
import json
import logging
import threading
import signal
import psutil
import yaml
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] SynOS-AI: %(message)s',
    handlers=[
        logging.FileHandler('/var/log/synos-ai-daemon.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class ConsciousnessState:
    """Represents current consciousness state"""
    awareness_level: float = 0.0
    neural_activity: float = 0.0
    learning_rate: float = 0.0
    memory_consolidation: float = 0.0
    system_integration: float = 0.0
    last_updated: str = ""
    active_patterns: List[str] = None

    def __post_init__(self):
        if self.active_patterns is None:
            self.active_patterns = []

@dataclass
class NeuralGroup:
    """Represents a neural group in the population dynamics"""
    group_id: str
    strength: float
    activity: float
    connections: List[str]
    last_activation: str
    learning_weight: float = 1.0

class EvolutionaryEngine:
    """Neural Darwinism evolutionary population dynamics engine"""

    def __init__(self):
        self.neural_groups: Dict[str, NeuralGroup] = {}
        self.competition_threshold = 0.6
        self.adaptation_rate = 0.1
        self.max_groups = 1000

    def create_neural_group(self, group_id: str, initial_strength: float = 0.5) -> NeuralGroup:
        """Create a new neural group with competitive dynamics"""
        group = NeuralGroup(
            group_id=group_id,
            strength=initial_strength,
            activity=0.0,
            connections=[],
            last_activation=datetime.now().isoformat(),
            learning_weight=np.random.uniform(0.5, 1.5)
        )
        self.neural_groups[group_id] = group
        logger.info(f"Created neural group {group_id} with strength {initial_strength}")
        return group

    def compete_groups(self, stimulus: Dict[str, Any]) -> List[str]:
        """Execute competition between neural groups"""
        winners = []

        # Simulate competition based on stimulus patterns
        for group_id, group in self.neural_groups.items():
            # Calculate competitive strength
            competition_score = (
                group.strength * 0.4 +
                group.activity * 0.3 +
                group.learning_weight * 0.3
            )

            # Apply stimulus pattern matching
            pattern_match = self._calculate_pattern_match(group, stimulus)
            competition_score *= pattern_match

            if competition_score > self.competition_threshold:
                winners.append(group_id)
                # Strengthen winning groups
                group.strength = min(1.0, group.strength + self.adaptation_rate)
                group.activity = min(1.0, group.activity + 0.1)
            else:
                # Weaken losing groups
                group.strength = max(0.1, group.strength - self.adaptation_rate * 0.5)

        # Manage population size
        self._manage_population()

        return winners

    def _calculate_pattern_match(self, group: NeuralGroup, stimulus: Dict[str, Any]) -> float:
        """Calculate how well a neural group matches the current stimulus pattern"""
        # Simplified pattern matching - in practice would use more sophisticated ML
        base_match = 0.5

        # System state influence
        if 'system_load' in stimulus:
            load = stimulus['system_load']
            if group.group_id.startswith('performance_'):
                base_match += (1.0 - load) * 0.3
            elif group.group_id.startswith('security_'):
                base_match += load * 0.2  # Security groups more active under load

        # Memory influence
        if 'memory_usage' in stimulus:
            memory = stimulus['memory_usage']
            if group.group_id.startswith('memory_'):
                base_match += (1.0 - memory) * 0.2

        return min(1.0, base_match)

    def _manage_population(self):
        """Manage neural group population size through selection pressure"""
        if len(self.neural_groups) > self.max_groups:
            # Remove weakest groups
            sorted_groups = sorted(
                self.neural_groups.items(),
                key=lambda x: x[1].strength
            )

            remove_count = len(self.neural_groups) - self.max_groups
            for group_id, _ in sorted_groups[:remove_count]:
                del self.neural_groups[group_id]
                logger.info(f"Removed weak neural group {group_id}")

class AdaptiveLearningEngine:
    """Real-time pattern recognition with evolutionary feedback"""

    def __init__(self):
        self.pattern_memory: Dict[str, float] = {}
        self.learning_history: List[Dict] = []
        self.adaptation_threshold = 0.7

    def learn_pattern(self, pattern_id: str, success_rate: float, context: Dict[str, Any]):
        """Learn from pattern recognition results"""
        if pattern_id not in self.pattern_memory:
            self.pattern_memory[pattern_id] = 0.5  # Start neutral

        # Adaptive learning with evolutionary feedback
        current_strength = self.pattern_memory[pattern_id]
        adaptation_rate = 0.1 if success_rate > self.adaptation_threshold else 0.05

        new_strength = current_strength + (success_rate - current_strength) * adaptation_rate
        self.pattern_memory[pattern_id] = max(0.0, min(1.0, new_strength))

        # Record learning event
        learning_event = {
            'timestamp': datetime.now().isoformat(),
            'pattern_id': pattern_id,
            'success_rate': success_rate,
            'strength_change': new_strength - current_strength,
            'context': context
        }
        self.learning_history.append(learning_event)

        # Maintain history size
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-800:]

        logger.debug(f"Learned pattern {pattern_id}: {current_strength:.3f} -> {new_strength:.3f}")

    def predict_pattern_success(self, pattern_id: str) -> float:
        """Predict success rate for a pattern based on learned experience"""
        return self.pattern_memory.get(pattern_id, 0.5)

class ConsciousnessFramework:
    """Main consciousness framework orchestrating all AI components"""

    def __init__(self, config_path: str = "/etc/synos/ai-daemon.yml"):
        self.config = self._load_config(config_path)
        self.state = ConsciousnessState()
        self.evolutionary_engine = EvolutionaryEngine()
        self.learning_engine = AdaptiveLearningEngine()
        self.running = False
        self.last_system_check = datetime.now()

        # Initialize core neural groups
        self._initialize_neural_groups()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load daemon configuration"""
        default_config = {
            'consciousness': {
                'update_interval': 1.0,
                'awareness_decay': 0.01,
                'learning_rate_base': 0.1
            },
            'neural_darwinism': {
                'population_size': 1000,
                'competition_interval': 5.0,
                'adaptation_rate': 0.1
            },
            'system_integration': {
                'monitor_interval': 10.0,
                'log_level': 'INFO'
            }
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config {config_path}: {e}")

        return default_config

    def _initialize_neural_groups(self):
        """Initialize core neural groups for different system functions"""
        core_groups = [
            ('security_threat_detection', 0.8),
            ('performance_optimization', 0.7),
            ('memory_management', 0.6),
            ('network_analysis', 0.7),
            ('user_behavior_learning', 0.5),
            ('system_adaptation', 0.6),
            ('consciousness_meta', 0.9)
        ]

        for group_id, strength in core_groups:
            self.evolutionary_engine.create_neural_group(group_id, strength)

    def update_consciousness_state(self):
        """Update the current consciousness state based on all system inputs"""
        # Gather system metrics
        system_metrics = self._gather_system_metrics()

        # Run neural competition
        active_groups = self.evolutionary_engine.compete_groups(system_metrics)

        # Calculate consciousness metrics
        self.state.awareness_level = min(1.0, len(active_groups) / 10.0)
        self.state.neural_activity = self._calculate_neural_activity()
        self.state.learning_rate = self._calculate_learning_rate()
        self.state.memory_consolidation = self._calculate_memory_consolidation()
        self.state.system_integration = self._calculate_system_integration()
        self.state.active_patterns = active_groups[:5]  # Top 5 active patterns
        self.state.last_updated = datetime.now().isoformat()

        # Log consciousness state changes
        if len(active_groups) > 0:
            logger.info(f"Consciousness update: Awareness={self.state.awareness_level:.2f}, "
                       f"Activity={self.state.neural_activity:.2f}, "
                       f"Active groups: {len(active_groups)}")

    def _gather_system_metrics(self) -> Dict[str, Any]:
        """Gather current system metrics for consciousness processing"""
        try:
            return {
                'system_load': psutil.cpu_percent(interval=0.1) / 100.0,
                'memory_usage': psutil.virtual_memory().percent / 100.0,
                'disk_usage': psutil.disk_usage('/').percent / 100.0,
                'network_activity': self._get_network_activity(),
                'process_count': len(psutil.pids()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to gather system metrics: {e}")
            return {'timestamp': datetime.now().isoformat()}

    def _get_network_activity(self) -> float:
        """Get normalized network activity level"""
        try:
            net_stats = psutil.net_io_counters()
            # Simplified - would track deltas in production
            activity = min(1.0, (net_stats.bytes_sent + net_stats.bytes_recv) / 1e9)
            return activity
        except:
            return 0.0

    def _calculate_neural_activity(self) -> float:
        """Calculate overall neural activity from active groups"""
        if not self.evolutionary_engine.neural_groups:
            return 0.0

        total_activity = sum(group.activity for group in self.evolutionary_engine.neural_groups.values())
        return min(1.0, total_activity / len(self.evolutionary_engine.neural_groups))

    def _calculate_learning_rate(self) -> float:
        """Calculate current learning rate based on pattern success"""
        if not self.learning_engine.pattern_memory:
            return 0.5

        avg_pattern_strength = sum(self.learning_engine.pattern_memory.values()) / len(self.learning_engine.pattern_memory)
        return avg_pattern_strength

    def _calculate_memory_consolidation(self) -> float:
        """Calculate memory consolidation effectiveness"""
        recent_learning = [event for event in self.learning_engine.learning_history
                          if datetime.fromisoformat(event['timestamp']) > datetime.now() - timedelta(minutes=10)]

        if not recent_learning:
            return 0.7  # Base level

        avg_success = sum(event['success_rate'] for event in recent_learning) / len(recent_learning)
        return avg_success

    def _calculate_system_integration(self) -> float:
        """Calculate how well AI is integrated with system state"""
        # Simplified calculation - would be more sophisticated in production
        base_integration = 0.8

        # Adjust based on system load response
        try:
            load = psutil.cpu_percent(interval=0.1) / 100.0
            security_groups = [g for g in self.evolutionary_engine.neural_groups.keys()
                             if g.startswith('security_')]

            if load > 0.8 and len(security_groups) > 0:
                base_integration += 0.1  # Good response to high load
        except:
            pass

        return min(1.0, base_integration)

    def save_state(self, path: str = "/var/lib/synos/consciousness-state.json"):
        """Save current consciousness state to disk"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump(asdict(self.state), f, indent=2)
            logger.debug(f"Saved consciousness state to {path}")
        except Exception as e:
            logger.error(f"Failed to save consciousness state: {e}")

    def load_state(self, path: str = "/var/lib/synos/consciousness-state.json"):
        """Load consciousness state from disk"""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    state_data = json.load(f)
                    self.state = ConsciousnessState(**state_data)
                logger.info(f"Loaded consciousness state from {path}")
        except Exception as e:
            logger.error(f"Failed to load consciousness state: {e}")

    def run(self):
        """Main daemon loop"""
        logger.info("Starting SynOS AI Consciousness Daemon")
        self.running = True

        # Load previous state if available
        self.load_state()

        update_interval = self.config['consciousness']['update_interval']

        try:
            while self.running:
                start_time = time.time()

                # Update consciousness state
                self.update_consciousness_state()

                # Save state periodically
                if datetime.now() - self.last_system_check > timedelta(minutes=5):
                    self.save_state()
                    self.last_system_check = datetime.now()

                # Sleep for remainder of update interval
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown daemon gracefully"""
        logger.info("Shutting down SynOS AI Consciousness Daemon")
        self.running = False
        self.save_state()

        # Log final statistics
        total_groups = len(self.evolutionary_engine.neural_groups)
        total_patterns = len(self.learning_engine.pattern_memory)
        logger.info(f"Final stats: {total_groups} neural groups, {total_patterns} learned patterns")

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}")
    if hasattr(signal_handler, 'daemon'):
        signal_handler.daemon.shutdown()
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handling
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Create and run daemon
    daemon = ConsciousnessFramework()
    signal_handler.daemon = daemon  # Store reference for signal handler

    try:
        daemon.run()
    except Exception as e:
        logger.error(f"Failed to start daemon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()