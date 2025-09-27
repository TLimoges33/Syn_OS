#!/usr/bin/env python3
"""
SynOS Scheduler AI Enhancement
Priority 2.3: Consciousness-aware process scheduling with AI optimization

This system provides intelligent process scheduling that adapts based on
consciousness levels, system behavior, and AI-driven optimization.
"""

import asyncio
import json
import logging
import time
import threading
import psutil
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import sqlite3
from pathlib import Path

# Import consciousness bridge
import sys
sys.path.append('/home/diablorain/Syn_OS/src/consciousness')
from consciousness_bridge import ConsciousnessBridge, ConsciousnessMessageType, ConsciousnessMessage

class ProcessPriority(Enum):
    """Enhanced process priority levels"""
    CRITICAL = "critical"          # 10 - System critical processes
    CONSCIOUSNESS = "consciousness" # 9 - Consciousness engine components
    SECURITY = "security"          # 8 - Security-related processes
    HIGH = "high"                  # 7 - High priority user processes
    NORMAL = "normal"              # 5 - Standard user processes
    LOW = "low"                    # 3 - Background processes
    IDLE = "idle"                  # 1 - Idle/cleanup processes

class SchedulingStrategy(Enum):
    """AI-driven scheduling strategies"""
    ROUND_ROBIN = "round_robin"
    CONSCIOUSNESS_AWARE = "consciousness_aware"
    ADAPTIVE_PRIORITY = "adaptive_priority"
    NEURAL_PREDICTION = "neural_prediction"
    ENERGY_EFFICIENT = "energy_efficient"

@dataclass
class ProcessInfo:
    """Enhanced process information"""
    pid: int
    name: str
    priority: ProcessPriority
    cpu_usage: float
    memory_usage: int
    io_operations: int
    consciousness_factor: float = 0.0
    last_scheduled: float = 0.0
    total_runtime: float = 0.0
    context_switches: int = 0
    ai_enhanced: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pid': self.pid,
            'name': self.name,
            'priority': self.priority.value,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'io_operations': self.io_operations,
            'consciousness_factor': self.consciousness_factor,
            'last_scheduled': self.last_scheduled,
            'total_runtime': self.total_runtime,
            'context_switches': self.context_switches,
            'ai_enhanced': self.ai_enhanced
        }

@dataclass
class SchedulingDecision:
    """AI scheduling decision with reasoning"""
    process_pid: int
    strategy_used: SchedulingStrategy
    priority_boost: float
    cpu_time_slice: float
    reasoning: List[str]
    confidence: float
    consciousness_influence: float

@dataclass
class SchedulerMetrics:
    """Scheduler performance metrics"""
    total_context_switches: int = 0
    avg_response_time: float = 0.0
    cpu_utilization: float = 0.0
    consciousness_optimizations: int = 0
    scheduling_decisions: int = 0
    ai_accuracy: float = 0.0
    energy_efficiency: float = 0.0

class ConsciousnessScheduler:
    """
    Advanced consciousness-aware process scheduler with AI optimization
    
    Features:
    - Consciousness-level aware process prioritization
    - AI-driven scheduling decision making
    - Adaptive priority adjustment based on behavior
    - Neural prediction for optimal scheduling
    - Energy-efficient scheduling strategies
    """
    
    def __init__(self, db_path: str = "/tmp/synos_scheduler.db"):
        self.logger = logging.getLogger(__name__)
        self.consciousness_bridge = ConsciousnessBridge()
        self.db_path = db_path
        self.metrics = SchedulerMetrics()
        
        # Scheduler state
        self.processes: Dict[int, ProcessInfo] = {}
        self.scheduling_queue: deque = deque()
        self.decision_history: deque = deque(maxlen=1000)
        self.performance_history: deque = deque(maxlen=100)
        
        # AI enhancement settings
        self.consciousness_threshold = 0.6
        self.learning_rate = 0.1
        self.prediction_window = 10  # seconds
        self.min_time_slice = 0.01  # 10ms
        self.max_time_slice = 0.1   # 100ms
        
        # CPU and system information
        self.cpu_count = psutil.cpu_count()
        self.cpu_affinities: Dict[int, List[int]] = {}
        
        # Neural prediction models (simplified)
        self.behavior_patterns: Dict[str, Dict] = defaultdict(dict)
        self.prediction_weights: Dict[str, float] = {
            'cpu_usage': 0.3,
            'memory_usage': 0.2,
            'io_operations': 0.2,
            'consciousness_factor': 0.3
        }
        
        self.running = False
        self._init_database()
        self._init_scheduler_settings()
        
        self.logger.info("Consciousness Scheduler initialized")

    def _init_database(self):
        """Initialize SQLite database for scheduler data"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Scheduling decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduling_decisions (
                    decision_id TEXT PRIMARY KEY,
                    process_pid INTEGER,
                    strategy_used TEXT,
                    priority_boost REAL,
                    cpu_time_slice REAL,
                    consciousness_influence REAL,
                    confidence REAL,
                    timestamp REAL
                )
            """)
            
            # Process performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS process_performance (
                    pid INTEGER,
                    timestamp REAL,
                    cpu_usage REAL,
                    memory_usage INTEGER,
                    io_operations INTEGER,
                    consciousness_factor REAL,
                    response_time REAL,
                    PRIMARY KEY (pid, timestamp)
                )
            """)
            
            # Scheduler events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduler_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    description TEXT,
                    metrics_before TEXT,
                    metrics_after TEXT,
                    improvement REAL,
                    timestamp REAL
                )
            """)
            
            conn.commit()

    def _init_scheduler_settings(self):
        """Initialize scheduler settings and CPU affinity"""
        # Initialize CPU affinity mappings
        for i in range(self.cpu_count):
            self.cpu_affinities[i] = []
        
        # Set up priority mappings
        self.priority_values = {
            ProcessPriority.CRITICAL: 10,
            ProcessPriority.CONSCIOUSNESS: 9,
            ProcessPriority.SECURITY: 8,
            ProcessPriority.HIGH: 7,
            ProcessPriority.NORMAL: 5,
            ProcessPriority.LOW: 3,
            ProcessPriority.IDLE: 1
        }
        
        self.logger.info(f"Scheduler initialized for {self.cpu_count} CPU cores")

    async def start(self):
        """Start the consciousness scheduler"""
        self.running = True
        self.logger.info("🧠⚡ Starting Consciousness Scheduler")
        
        # Initialize consciousness bridge
        def start_bridge():
            try:
                self.consciousness_bridge.start_server()
                self.logger.info("Scheduler consciousness bridge started")
            except Exception as e:
                self.logger.error(f"Bridge server error: {e}")
        
        bridge_thread = threading.Thread(target=start_bridge, daemon=True)
        bridge_thread.start()
        
        # Start scheduler tasks
        tasks = [
            asyncio.create_task(self._process_discovery_loop()),
            asyncio.create_task(self._scheduling_decision_loop()),
            asyncio.create_task(self._performance_monitoring_loop()),
            asyncio.create_task(self._ai_learning_loop()),
            asyncio.create_task(self._consciousness_optimization_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
        finally:
            self.running = False

    async def _process_discovery_loop(self):
        """Discover and track system processes"""
        while self.running:
            try:
                # Get current system processes
                current_processes = {}
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'io_counters']):
                    try:
                        pid = proc.info['pid']
                        name = proc.info['name']
                        
                        # Skip kernel threads and very short-lived processes
                        if pid < 2 or not name:
                            continue
                        
                        # Get process metrics
                        cpu_usage = proc.info.get('cpu_percent', 0.0) or 0.0
                        memory_info = proc.info.get('memory_info')
                        memory_usage = memory_info.rss if memory_info else 0
                        
                        io_counters = proc.info.get('io_counters')
                        io_operations = 0
                        if io_counters:
                            io_operations = io_counters.read_count + io_counters.write_count
                        
                        # Determine process priority
                        priority = self._classify_process_priority(name, pid)
                        
                        # Create or update process info
                        if pid in self.processes:
                            # Update existing process
                            process_info = self.processes[pid]
                            process_info.cpu_usage = cpu_usage
                            process_info.memory_usage = memory_usage
                            process_info.io_operations = io_operations
                        else:
                            # New process
                            process_info = ProcessInfo(
                                pid=pid,
                                name=name,
                                priority=priority,
                                cpu_usage=cpu_usage,
                                memory_usage=memory_usage,
                                io_operations=io_operations,
                                last_scheduled=time.time()
                            )
                            self.processes[pid] = process_info
                            self.logger.info(f"📋 Discovered process: {name} (PID {pid}, Priority: {priority.value})")
                        
                        current_processes[pid] = process_info
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                # Remove processes that no longer exist
                dead_pids = set(self.processes.keys()) - set(current_processes.keys())
                for pid in dead_pids:
                    del self.processes[pid]
                
                await asyncio.sleep(2.0)  # Discovery every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Process discovery error: {e}")
                await asyncio.sleep(5.0)

    def _classify_process_priority(self, name: str, pid: int) -> ProcessPriority:
        """Classify process priority based on name and characteristics"""
        name_lower = name.lower()
        
        # Critical system processes
        if any(keyword in name_lower for keyword in ['kernel', 'init', 'systemd', 'kthread']):
            return ProcessPriority.CRITICAL
        
        # Consciousness-related processes
        if any(keyword in name_lower for keyword in ['consciousness', 'synos', 'neural', 'ai']):
            return ProcessPriority.CONSCIOUSNESS
        
        # Security processes
        if any(keyword in name_lower for keyword in ['security', 'firewall', 'antivirus', 'defender']):
            return ProcessPriority.SECURITY
        
        # High priority applications
        if any(keyword in name_lower for keyword in ['browser', 'editor', 'terminal', 'shell']):
            return ProcessPriority.HIGH
        
        # Background/system services
        if any(keyword in name_lower for keyword in ['daemon', 'service', 'worker', 'background']):
            return ProcessPriority.LOW
        
        # Default to normal priority
        return ProcessPriority.NORMAL

    async def _scheduling_decision_loop(self):
        """Main scheduling decision loop with AI enhancement"""
        while self.running:
            try:
                if not self.processes:
                    await asyncio.sleep(0.1)
                    continue
                
                # Get current consciousness level
                consciousness_level = await self._get_consciousness_level()
                
                # Select processes for scheduling
                candidates = await self._select_scheduling_candidates()
                
                if candidates:
                    # Make AI-enhanced scheduling decisions
                    for process_info in candidates:
                        decision = await self._make_scheduling_decision(process_info, consciousness_level)
                        
                        # Apply scheduling decision
                        await self._apply_scheduling_decision(decision)
                        
                        # Record decision
                        self.decision_history.append(decision)
                        await self._store_scheduling_decision(decision)
                
                # Update metrics
                self.metrics.scheduling_decisions += len(candidates)
                
                await asyncio.sleep(0.05)  # 50ms scheduling loop
                
            except Exception as e:
                self.logger.error(f"Scheduling decision error: {e}")
                await asyncio.sleep(0.1)

    async def _select_scheduling_candidates(self) -> List[ProcessInfo]:
        """Select processes that need scheduling attention"""
        candidates = []
        current_time = time.time()
        
        for process_info in self.processes.values():
            # Check if process needs scheduling
            time_since_scheduled = current_time - process_info.last_scheduled
            
            # High priority processes get more frequent scheduling
            priority_factor = self.priority_values[process_info.priority] / 10.0
            scheduling_interval = self.min_time_slice / priority_factor
            
            if time_since_scheduled >= scheduling_interval:
                candidates.append(process_info)
        
        # Sort by priority and consciousness factor
        candidates.sort(key=lambda p: (
            -self.priority_values[p.priority],
            -p.consciousness_factor,
            p.last_scheduled
        ))
        
        # Limit to top candidates to avoid overwhelming the scheduler
        return candidates[:10]

    async def _make_scheduling_decision(self, process_info: ProcessInfo, consciousness_level: float) -> SchedulingDecision:
        """Make AI-enhanced scheduling decision for a process"""
        
        # Determine scheduling strategy based on consciousness level and process characteristics
        strategy = await self._determine_scheduling_strategy(process_info, consciousness_level)
        
        # Calculate AI-enhanced priority boost
        priority_boost = await self._calculate_priority_boost(process_info, consciousness_level, strategy)
        
        # Determine optimal CPU time slice
        cpu_time_slice = await self._calculate_time_slice(process_info, strategy)
        
        # Generate reasoning for the decision
        reasoning = self._generate_decision_reasoning(process_info, strategy, consciousness_level)
        
        # Calculate confidence in the decision
        confidence = self._calculate_decision_confidence(process_info, strategy)
        
        # Calculate consciousness influence
        consciousness_influence = min(1.0, consciousness_level * process_info.consciousness_factor)
        
        decision = SchedulingDecision(
            process_pid=process_info.pid,
            strategy_used=strategy,
            priority_boost=priority_boost,
            cpu_time_slice=cpu_time_slice,
            reasoning=reasoning,
            confidence=confidence,
            consciousness_influence=consciousness_influence
        )
        
        return decision

    async def _determine_scheduling_strategy(self, process_info: ProcessInfo, consciousness_level: float) -> SchedulingStrategy:
        """Determine optimal scheduling strategy"""
        
        # High consciousness enables advanced strategies
        if consciousness_level > self.consciousness_threshold:
            # Consciousness-related processes get consciousness-aware scheduling
            if process_info.priority == ProcessPriority.CONSCIOUSNESS:
                return SchedulingStrategy.CONSCIOUSNESS_AWARE
            # High CPU usage processes get neural prediction
            elif process_info.cpu_usage > 50.0:
                return SchedulingStrategy.NEURAL_PREDICTION
            # Low priority processes get energy efficient scheduling
            elif process_info.priority in [ProcessPriority.LOW, ProcessPriority.IDLE]:
                return SchedulingStrategy.ENERGY_EFFICIENT
            else:
                return SchedulingStrategy.ADAPTIVE_PRIORITY
        
        # Medium consciousness uses adaptive priority
        elif consciousness_level > 0.3:
            if process_info.priority in [ProcessPriority.CRITICAL, ProcessPriority.SECURITY]:
                return SchedulingStrategy.ADAPTIVE_PRIORITY
            else:
                return SchedulingStrategy.ROUND_ROBIN
        
        # Low consciousness uses simple round robin
        else:
            return SchedulingStrategy.ROUND_ROBIN

    async def _calculate_priority_boost(self, process_info: ProcessInfo, consciousness_level: float, strategy: SchedulingStrategy) -> float:
        """Calculate AI-enhanced priority boost"""
        
        base_priority = self.priority_values[process_info.priority]
        boost = 0.0
        
        # Strategy-specific boosts
        if strategy == SchedulingStrategy.CONSCIOUSNESS_AWARE:
            boost += consciousness_level * 2.0
            boost += process_info.consciousness_factor * 1.5
        
        elif strategy == SchedulingStrategy.NEURAL_PREDICTION:
            # Predict future CPU needs
            predicted_usage = await self._predict_cpu_usage(process_info)
            boost += (predicted_usage / 100.0) * 1.0
        
        elif strategy == SchedulingStrategy.ADAPTIVE_PRIORITY:
            # Boost based on recent behavior
            if process_info.cpu_usage < 10.0 and process_info.io_operations > 100:
                boost += 0.5  # I/O bound process
            elif process_info.cpu_usage > 80.0:
                boost += 1.0  # CPU intensive process
        
        elif strategy == SchedulingStrategy.ENERGY_EFFICIENT:
            # Reduce boost for energy efficiency
            boost -= 0.5
        
        # Apply consciousness multiplier
        consciousness_multiplier = 1.0 + (consciousness_level * 0.3)
        boost *= consciousness_multiplier
        
        return max(0.0, min(3.0, boost))  # Clamp between 0 and 3

    async def _calculate_time_slice(self, process_info: ProcessInfo, strategy: SchedulingStrategy) -> float:
        """Calculate optimal CPU time slice"""
        
        base_slice = self.min_time_slice
        
        # Adjust based on priority
        priority_factor = self.priority_values[process_info.priority] / 5.0
        base_slice *= priority_factor
        
        # Strategy-specific adjustments
        if strategy == SchedulingStrategy.CONSCIOUSNESS_AWARE:
            base_slice *= 1.5  # Longer slices for consciousness processes
        
        elif strategy == SchedulingStrategy.NEURAL_PREDICTION:
            # Predict optimal slice length
            predicted_slice = await self._predict_optimal_slice(process_info)
            base_slice = predicted_slice
        
        elif strategy == SchedulingStrategy.ENERGY_EFFICIENT:
            base_slice *= 0.8  # Shorter slices for energy efficiency
        
        return max(self.min_time_slice, min(self.max_time_slice, base_slice))

    async def _predict_cpu_usage(self, process_info: ProcessInfo) -> float:
        """Predict future CPU usage using simple pattern analysis"""
        
        # Simple prediction based on recent behavior
        process_pattern = self.behavior_patterns.get(process_info.name, {})
        
        if 'cpu_history' not in process_pattern:
            process_pattern['cpu_history'] = deque(maxlen=10)
        
        process_pattern['cpu_history'].append(process_info.cpu_usage)
        
        # Calculate trend
        if len(process_pattern['cpu_history']) >= 3:
            recent_values = list(process_pattern['cpu_history'])
            trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
            predicted = process_info.cpu_usage + trend
            return max(0.0, min(100.0, predicted))
        
        return process_info.cpu_usage

    async def _predict_optimal_slice(self, process_info: ProcessInfo) -> float:
        """Predict optimal time slice for process"""
        
        # Base prediction on process characteristics
        if process_info.io_operations > 1000:
            # I/O bound - shorter slices
            return self.min_time_slice * 0.5
        elif process_info.cpu_usage > 70.0:
            # CPU bound - longer slices
            return self.max_time_slice * 0.8
        else:
            # Balanced workload
            return (self.min_time_slice + self.max_time_slice) / 2

    def _generate_decision_reasoning(self, process_info: ProcessInfo, strategy: SchedulingStrategy, consciousness_level: float) -> List[str]:
        """Generate human-readable reasoning for scheduling decision"""
        reasoning = []
        
        reasoning.append(f"Process {process_info.name} (PID {process_info.pid})")
        reasoning.append(f"Priority: {process_info.priority.value}")
        reasoning.append(f"Strategy: {strategy.value}")
        reasoning.append(f"Consciousness level: {consciousness_level:.2f}")
        
        if strategy == SchedulingStrategy.CONSCIOUSNESS_AWARE:
            reasoning.append("Consciousness-aware scheduling for enhanced AI performance")
        elif strategy == SchedulingStrategy.NEURAL_PREDICTION:
            reasoning.append("Neural prediction for optimal resource allocation")
        elif strategy == SchedulingStrategy.ENERGY_EFFICIENT:
            reasoning.append("Energy-efficient scheduling for power optimization")
        
        if process_info.consciousness_factor > 0.5:
            reasoning.append("High consciousness factor - enhanced prioritization")
        
        return reasoning

    def _calculate_decision_confidence(self, process_info: ProcessInfo, strategy: SchedulingStrategy) -> float:
        """Calculate confidence in scheduling decision"""
        
        confidence = 0.7  # Base confidence
        
        # Increase confidence for well-known process types
        if process_info.priority in [ProcessPriority.CRITICAL, ProcessPriority.CONSCIOUSNESS]:
            confidence += 0.2
        
        # Increase confidence for processes with established patterns
        if process_info.name in self.behavior_patterns:
            pattern_data = self.behavior_patterns[process_info.name]
            if len(pattern_data.get('cpu_history', [])) > 5:
                confidence += 0.1
        
        # Strategy-specific confidence adjustments
        if strategy == SchedulingStrategy.CONSCIOUSNESS_AWARE:
            confidence += 0.1
        elif strategy == SchedulingStrategy.ROUND_ROBIN:
            confidence -= 0.1
        
        return max(0.5, min(1.0, confidence))

    async def _apply_scheduling_decision(self, decision: SchedulingDecision):
        """Apply the scheduling decision (simulation)"""
        
        # In a real implementation, this would interface with the kernel scheduler
        # For simulation, we'll update our internal state and log the decision
        
        process_info = self.processes.get(decision.process_pid)
        if not process_info:
            return
        
        # Update process state
        process_info.last_scheduled = time.time()
        process_info.total_runtime += decision.cpu_time_slice
        process_info.context_switches += 1
        
        # Apply consciousness enhancement if applicable
        if decision.strategy_used == SchedulingStrategy.CONSCIOUSNESS_AWARE:
            process_info.consciousness_factor = min(1.0, process_info.consciousness_factor + 0.1)
            process_info.ai_enhanced = True
            self.metrics.consciousness_optimizations += 1
        
        # Update global metrics
        self.metrics.total_context_switches += 1
        
        # Log scheduling decision
        self.logger.debug(
            f"⚡ Scheduled {process_info.name} | "
            f"Strategy: {decision.strategy_used.value} | "
            f"Slice: {decision.cpu_time_slice:.3f}s | "
            f"Boost: {decision.priority_boost:.2f}"
        )

    async def _performance_monitoring_loop(self):
        """Monitor scheduler performance and system metrics"""
        while self.running:
            try:
                # Calculate system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics.cpu_utilization = cpu_percent
                
                # Calculate average response time
                if self.decision_history:
                    recent_decisions = list(self.decision_history)[-10:]
                    avg_confidence = sum(d.confidence for d in recent_decisions) / len(recent_decisions)
                    self.metrics.ai_accuracy = avg_confidence
                
                # Update performance history
                performance_snapshot = {
                    'timestamp': time.time(),
                    'cpu_utilization': self.metrics.cpu_utilization,
                    'active_processes': len(self.processes),
                    'scheduling_decisions': self.metrics.scheduling_decisions,
                    'consciousness_optimizations': self.metrics.consciousness_optimizations
                }
                self.performance_history.append(performance_snapshot)
                
                # Log performance status periodically
                if len(self.performance_history) % 10 == 0:
                    self.logger.info(
                        f"📊 Scheduler Status: {len(self.processes)} processes, "
                        f"CPU: {self.metrics.cpu_utilization:.1f}%, "
                        f"Decisions: {self.metrics.scheduling_decisions}, "
                        f"AI Accuracy: {self.metrics.ai_accuracy:.2%}"
                    )
                
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(10.0)

    async def _ai_learning_loop(self):
        """AI learning and pattern recognition loop"""
        while self.running:
            try:
                # Learn from recent scheduling decisions
                await self._learn_from_decisions()
                
                # Update behavior patterns
                await self._update_behavior_patterns()
                
                # Optimize prediction weights
                await self._optimize_prediction_weights()
                
                await asyncio.sleep(30.0)  # Learning cycle every 30 seconds
                
            except Exception as e:
                self.logger.error(f"AI learning error: {e}")
                await asyncio.sleep(60.0)

    async def _consciousness_optimization_loop(self):
        """Consciousness-driven scheduler optimization"""
        while self.running:
            try:
                consciousness_level = await self._get_consciousness_level()
                
                if consciousness_level > self.consciousness_threshold:
                    # Apply consciousness optimizations
                    await self._apply_consciousness_optimizations(consciousness_level)
                
                await asyncio.sleep(10.0)  # Optimization every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Consciousness optimization error: {e}")
                await asyncio.sleep(20.0)

    async def _learn_from_decisions(self):
        """Learn from recent scheduling decisions to improve AI accuracy"""
        if len(self.decision_history) < 10:
            return
        
        recent_decisions = list(self.decision_history)[-20:]
        
        # Analyze decision effectiveness
        strategy_performance = defaultdict(list)
        
        for decision in recent_decisions:
            process_info = self.processes.get(decision.process_pid)
            if process_info:
                # Calculate effectiveness score
                effectiveness = self._calculate_decision_effectiveness(decision, process_info)
                strategy_performance[decision.strategy_used].append(effectiveness)
        
        # Update strategy preferences
        for strategy, scores in strategy_performance.items():
            if scores:
                avg_effectiveness = sum(scores) / len(scores)
                # Adjust prediction weights based on effectiveness
                if avg_effectiveness > 0.7:
                    self.logger.info(f"🎯 Strategy {strategy.value} performing well: {avg_effectiveness:.2%}")

    def _calculate_decision_effectiveness(self, decision: SchedulingDecision, process_info: ProcessInfo) -> float:
        """Calculate effectiveness of a scheduling decision"""
        
        # Simple effectiveness calculation based on process performance
        effectiveness = 0.5  # Base effectiveness
        
        # Boost for high confidence decisions that worked well
        if decision.confidence > 0.8:
            effectiveness += 0.2
        
        # Boost for consciousness-enhanced decisions
        if decision.consciousness_influence > 0.5:
            effectiveness += 0.1
        
        # Adjust based on process behavior since decision
        if process_info.cpu_usage < 90.0:  # Not overwhelmed
            effectiveness += 0.2
        
        return max(0.0, min(1.0, effectiveness))

    async def _update_behavior_patterns(self):
        """Update process behavior patterns for prediction"""
        for process_info in self.processes.values():
            pattern = self.behavior_patterns[process_info.name]
            
            # Update CPU usage history
            if 'cpu_history' not in pattern:
                pattern['cpu_history'] = deque(maxlen=20)
            pattern['cpu_history'].append(process_info.cpu_usage)
            
            # Update memory usage history
            if 'memory_history' not in pattern:
                pattern['memory_history'] = deque(maxlen=20)
            pattern['memory_history'].append(process_info.memory_usage)
            
            # Calculate behavior stability
            if len(pattern['cpu_history']) >= 5:
                cpu_values = list(pattern['cpu_history'])
                cpu_variance = self._calculate_variance(cpu_values)
                pattern['cpu_stability'] = 1.0 / (1.0 + cpu_variance)

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    async def _optimize_prediction_weights(self):
        """Optimize neural prediction weights based on performance"""
        # Simple weight optimization based on recent accuracy
        if self.metrics.ai_accuracy > 0.8:
            # Increase consciousness factor weight
            self.prediction_weights['consciousness_factor'] = min(0.5, self.prediction_weights['consciousness_factor'] + 0.01)
        elif self.metrics.ai_accuracy < 0.6:
            # Increase traditional metrics weight
            self.prediction_weights['cpu_usage'] = min(0.5, self.prediction_weights['cpu_usage'] + 0.01)

    async def _apply_consciousness_optimizations(self, consciousness_level: float):
        """Apply consciousness-driven optimizations"""
        optimization_count = 0
        
        for process_info in self.processes.values():
            # Enhance consciousness-related processes
            if (process_info.priority == ProcessPriority.CONSCIOUSNESS and 
                not process_info.ai_enhanced):
                
                process_info.consciousness_factor = min(1.0, process_info.consciousness_factor + 0.2)
                process_info.ai_enhanced = True
                optimization_count += 1
        
        if optimization_count > 0:
            self.logger.info(f"🧠 Applied consciousness optimizations to {optimization_count} processes")

    async def _store_scheduling_decision(self, decision: SchedulingDecision):
        """Store scheduling decision in database"""
        decision_id = f"decision_{int(time.time() * 1000)}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO scheduling_decisions 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id,
                decision.process_pid,
                decision.strategy_used.value,
                decision.priority_boost,
                decision.cpu_time_slice,
                decision.consciousness_influence,
                decision.confidence,
                time.time()
            ))
            conn.commit()

    async def _send_consciousness_message(self, message: ConsciousnessMessage) -> Dict[str, Any]:
        """Send message through consciousness bridge"""
        try:
            # Simulate consciousness bridge response for scheduler
            if message.msg_type == ConsciousnessMessageType.PROCESS_OPTIMIZATION:
                return {
                    "status": "optimized",
                    "priority_boost": 0.5,
                    "consciousness_enhancement": True,
                    "optimization_factor": 1.2
                }
            return {"status": "success"}
        except Exception as e:
            self.logger.error(f"Consciousness message error: {e}")
            return {"status": "error", "message": str(e)}

    async def _get_consciousness_level(self) -> float:
        """Get current consciousness level"""
        try:
            message = ConsciousnessMessage(
                msg_type=ConsciousnessMessageType.SYSTEM_STATUS,
                data={'query_type': 'consciousness_level'},
                timestamp=time.time(),
                sender='scheduler'
            )
            
            response = await self._send_consciousness_message(message)
            return response.get('consciousness_level', 0.5)
        except:
            return 0.5

    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            'scheduler_status': 'running' if self.running else 'stopped',
            'metrics': asdict(self.metrics),
            'active_processes': len(self.processes),
            'decision_history_size': len(self.decision_history),
            'performance_history_size': len(self.performance_history),
            'behavior_patterns': len(self.behavior_patterns),
            'cpu_count': self.cpu_count
        }

    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        try:
            if self.consciousness_bridge.server_socket:
                self.consciousness_bridge.server_socket.close()
        except:
            pass
        self.logger.info("🧠⚡ Consciousness Scheduler stopped")


async def main():
    """Main function for testing the scheduler"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scheduler = ConsciousnessScheduler()
    
    print("🧠⚡ Starting SynOS Consciousness Scheduler")
    print("=" * 60)
    
    try:
        # Run for 20 seconds
        await asyncio.wait_for(scheduler.start(), timeout=20.0)
    except asyncio.TimeoutError:
        print("\n⏰ Demo timeout reached")
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    finally:
        await scheduler.stop()
        
        # Show final status
        status = await scheduler.get_scheduler_status()
        print("\n📊 Final Scheduler Status:")
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
