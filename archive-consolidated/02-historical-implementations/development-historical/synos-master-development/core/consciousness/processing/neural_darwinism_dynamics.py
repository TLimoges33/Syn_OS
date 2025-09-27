#!/usr/bin/env python3
"""
SynOS Neural Darwinism Population Dynamics Engine
=================================================

Core implementation of Neural Darwinism population dynamics based on:
- Theory of Neuronal Group Selection (TNGS)
- Competitive neural group evolution
- Real-time selection pressure algorithms
- Population fitness evaluation and adaptation

This addresses the critical blocker in TODO_IMPLEMENTATION_STATUS.md
Neural Darwinism Implementation (30% Complete) -> Target: 95% Complete
"""

import asyncio
import logging
import time
import random
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
import numpy as np
import json
from datetime import datetime
import uuid
from collections import deque, defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('synos.neural_darwinism')

# Population Types based on TNGS
class PopulationType(Enum):
    """Neural population types based on functional specialization"""
    EXECUTIVE = "executive"      # Decision-making and planning
    SENSORY = "sensory"         # Pattern recognition and input processing
    MEMORY = "memory"           # Learning and memory consolidation
    MOTOR = "motor"             # Action selection and execution
    ASSOCIATIVE = "associative" # Cross-modal integration
    HOMEOSTATIC = "homeostatic" # System regulation

class SelectionPressure(Enum):
    """Types of selection pressure for neural evolution"""
    COMPETITIVE = "competitive"     # Winner-take-all competition
    COOPERATIVE = "cooperative"     # Mutual reinforcement
    HYBRID = "hybrid"              # Mixed competitive/cooperative
    ADAPTIVE = "adaptive"          # Context-dependent selection

class FitnessMetric(Enum):
    """Fitness evaluation metrics"""
    LEARNING_RATE = "learning_rate"
    PATTERN_RECOGNITION = "pattern_recognition"
    ADAPTATION_SPEED = "adaptation_speed"
    ENERGY_EFFICIENCY = "energy_efficiency"
    COOPERATION_SCORE = "cooperation_score"
    SPECIALIZATION_DEPTH = "specialization_depth"

@dataclass
class NeuralUnit:
    """Individual neural unit within a population"""
    unit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    activation_threshold: float = 0.5
    connection_weights: Dict[str, float] = field(default_factory=dict)
    activation_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    fitness_score: float = 0.0
    age: int = 0
    specialization_level: float = 0.0
    energy_level: float = 1.0
    cooperation_bonds: List[str] = field(default_factory=list)
    mutation_rate: float = 0.01
    created_at: datetime = field(default_factory=datetime.now)
    
    def activate(self, input_signal: float) -> float:
        """Activate the neural unit with input signal"""
        self.age += 1
        
        # Apply activation function (sigmoid with threshold)
        weighted_input = input_signal * (1.0 + self.specialization_level)
        activation = 1.0 / (1.0 + np.exp(-(weighted_input - self.activation_threshold)))
        
        # Record activation
        self.activation_history.append({
            'timestamp': time.time(),
            'input': input_signal,
            'activation': activation,
            'threshold': self.activation_threshold
        })
        
        # Update energy (decays with use)
        self.energy_level = max(0.1, self.energy_level - 0.001)
        
        return activation
    
    def mutate(self) -> 'NeuralUnit':
        """Create a mutated copy of this neural unit"""
        mutated = NeuralUnit(
            activation_threshold=self.activation_threshold + random.gauss(0, self.mutation_rate),
            connection_weights=self.connection_weights.copy(),
            fitness_score=0.0,  # Reset fitness for new unit
            age=0,
            specialization_level=max(0.0, min(1.0, self.specialization_level + random.gauss(0, 0.05))),
            energy_level=1.0,
            mutation_rate=self.mutation_rate,
        )
        
        # Mutate connection weights
        for key in mutated.connection_weights:
            if random.random() < self.mutation_rate:
                mutated.connection_weights[key] += random.gauss(0, 0.1)
        
        return mutated

@dataclass 
class NeuralPopulation:
    """Population of neural units with evolutionary dynamics"""
    population_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    population_type: PopulationType = PopulationType.ASSOCIATIVE
    units: List[NeuralUnit] = field(default_factory=list)
    population_size: int = 1000
    selection_pressure: SelectionPressure = SelectionPressure.COMPETITIVE
    fitness_history: deque = field(default_factory=lambda: deque(maxlen=10000))
    generation: int = 0
    diversity_score: float = 1.0
    cooperation_matrix: np.ndarray = field(default=None)
    specialization_pressure: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize population after creation"""
        if not self.units:
            self._initialize_population()
        
        if self.cooperation_matrix is None:
            self.cooperation_matrix = np.random.random((self.population_size, self.population_size)) * 0.1
    
    def _initialize_population(self):
        """Initialize the neural population with diverse units"""
        logger.info(f"Initializing {self.population_type.value} population with {self.population_size} units")
        
        for i in range(self.population_size):
            unit = NeuralUnit(
                activation_threshold=random.gauss(0.5, 0.2),
                connection_weights={
                    f"input_{j}": random.gauss(0, 0.5) 
                    for j in range(10)  # 10 input connections per unit
                },
                specialization_level=random.random() * self.specialization_pressure,
                mutation_rate=random.uniform(0.005, 0.02)
            )
            self.units.append(unit)
    
    def process_input(self, input_signals: np.ndarray) -> np.ndarray:
        """Process input through the entire population"""
        outputs = []
        
        for i, unit in enumerate(self.units):
            # Calculate weighted input for this unit
            weighted_input = 0.0
            for j, signal in enumerate(input_signals[:len(unit.connection_weights)]):
                weight_key = f"input_{j}"
                weight = unit.connection_weights.get(weight_key, 0.0)
                weighted_input += signal * weight
            
            # Add cooperation effects
            cooperation_boost = np.sum(self.cooperation_matrix[i, :] * 
                                     [u.fitness_score for u in self.units]) / len(self.units)
            
            # Activate unit
            output = unit.activate(weighted_input + cooperation_boost * 0.1)
            outputs.append(output)
        
        return np.array(outputs)
    
    def evaluate_fitness(self, environment_feedback: Dict[str, float]) -> float:
        """Evaluate population fitness based on environment feedback"""
        fitness_scores = []
        
        for unit in self.units:
            # Base fitness from recent activations
            recent_activations = [h['activation'] for h in list(unit.activation_history)[-100:]]
            
            if recent_activations:
                activation_fitness = np.mean(recent_activations)
                stability_fitness = 1.0 - np.std(recent_activations)
                energy_fitness = unit.energy_level
                specialization_fitness = unit.specialization_level * self.specialization_pressure
                
                # Environment-specific fitness
                env_fitness = 0.0
                for metric, value in environment_feedback.items():
                    if metric == FitnessMetric.LEARNING_RATE.value:
                        env_fitness += value * 0.3
                    elif metric == FitnessMetric.PATTERN_RECOGNITION.value:
                        env_fitness += value * 0.2
                    elif metric == FitnessMetric.ADAPTATION_SPEED.value:
                        env_fitness += value * 0.2
                    elif metric == FitnessMetric.ENERGY_EFFICIENCY.value:
                        env_fitness += value * energy_fitness * 0.1
                    elif metric == FitnessMetric.COOPERATION_SCORE.value:
                        env_fitness += value * len(unit.cooperation_bonds) * 0.1
                    elif metric == FitnessMetric.SPECIALIZATION_DEPTH.value:
                        env_fitness += value * specialization_fitness * 0.1
                
                # Combined fitness score
                total_fitness = (
                    activation_fitness * 0.3 +
                    stability_fitness * 0.2 +
                    energy_fitness * 0.1 +
                    specialization_fitness * 0.1 +
                    env_fitness * 0.3
                )
                
                unit.fitness_score = max(0.0, min(1.0, total_fitness))
                fitness_scores.append(unit.fitness_score)
            else:
                unit.fitness_score = 0.0
                fitness_scores.append(0.0)
        
        # Population-level fitness
        population_fitness = np.mean(fitness_scores)
        self.fitness_history.append({
            'generation': self.generation,
            'fitness': population_fitness,
            'diversity': self._calculate_diversity(),
            'timestamp': time.time()
        })
        
        return population_fitness
    
    def _calculate_diversity(self) -> float:
        """Calculate population diversity"""
        if len(self.units) < 2:
            return 0.0
        
        thresholds = [unit.activation_threshold for unit in self.units]
        specializations = [unit.specialization_level for unit in self.units]
        
        threshold_diversity = np.std(thresholds)
        specialization_diversity = np.std(specializations)
        
        return (threshold_diversity + specialization_diversity) / 2.0
    
    def apply_selection_pressure(self, survival_rate: float = 0.5):
        """Apply selection pressure to the population"""
        logger.info(f"Applying {self.selection_pressure.value} selection pressure to {self.population_type.value} population")
        
        # Sort units by fitness
        self.units.sort(key=lambda u: u.fitness_score, reverse=True)
        
        num_survivors = int(len(self.units) * survival_rate)
        survivors = self.units[:num_survivors]
        
        if self.selection_pressure == SelectionPressure.COMPETITIVE:
            # Pure competitive selection - only the fittest survive
            selected = survivors
        
        elif self.selection_pressure == SelectionPressure.COOPERATIVE:
            # Cooperative selection - include units with high cooperation scores
            cooperation_bonus = []
            for unit in self.units:
                coop_score = len(unit.cooperation_bonds) * 0.1
                cooperation_bonus.append((unit, unit.fitness_score + coop_score))
            
            cooperation_bonus.sort(key=lambda x: x[1], reverse=True)
            selected = [unit for unit, _ in cooperation_bonus[:num_survivors]]
        
        elif self.selection_pressure == SelectionPressure.HYBRID:
            # Mix of competitive and cooperative
            competitive_count = int(num_survivors * 0.7)
            cooperative_count = num_survivors - competitive_count
            
            selected = survivors[:competitive_count]
            
            # Add cooperative units
            remaining = [u for u in self.units if u not in selected]
            remaining.sort(key=lambda u: len(u.cooperation_bonds), reverse=True)
            selected.extend(remaining[:cooperative_count])
        
        else:  # ADAPTIVE
            # Context-dependent selection based on current environment
            current_fitness = np.mean([u.fitness_score for u in self.units])
            
            if current_fitness > 0.7:
                # High performance - maintain diversity
                selected = self._diversity_selection(num_survivors)
            else:
                # Low performance - intensify competition
                selected = survivors
        
        return selected
    
    def _diversity_selection(self, num_survivors: int) -> List[NeuralUnit]:
        """Select units to maintain population diversity"""
        selected = []
        remaining = self.units.copy()
        
        while len(selected) < num_survivors and remaining:
            if not selected:
                # Start with the fittest
                best = max(remaining, key=lambda u: u.fitness_score)
                selected.append(best)
                remaining.remove(best)
            else:
                # Select unit most different from current selection
                max_diversity = 0
                most_diverse = remaining[0]
                
                for unit in remaining:
                    diversity = self._calculate_unit_diversity(unit, selected)
                    if diversity > max_diversity:
                        max_diversity = diversity
                        most_diverse = unit
                
                selected.append(most_diverse)
                remaining.remove(most_diverse)
        
        return selected
    
    def _calculate_unit_diversity(self, unit: NeuralUnit, reference_group: List[NeuralUnit]) -> float:
        """Calculate how diverse a unit is compared to a reference group"""
        if not reference_group:
            return 1.0
        
        distances = []
        for ref_unit in reference_group:
            # Calculate distance in feature space
            threshold_diff = abs(unit.activation_threshold - ref_unit.activation_threshold)
            specialization_diff = abs(unit.specialization_level - ref_unit.specialization_level)
            energy_diff = abs(unit.energy_level - ref_unit.energy_level)
            
            distance = np.sqrt(threshold_diff**2 + specialization_diff**2 + energy_diff**2)
            distances.append(distance)
        
        return min(distances)  # Minimum distance to any reference unit
    
    def reproduce_and_mutate(self, selected_units: List[NeuralUnit]) -> List[NeuralUnit]:
        """Create new generation through reproduction and mutation"""
        new_generation = []
        
        # Keep the best performers (elitism)
        elite_count = int(len(selected_units) * 0.1)
        new_generation.extend(selected_units[:elite_count])
        
        # Fill remaining slots with mutations and crossovers
        while len(new_generation) < self.population_size:
            if len(selected_units) >= 2 and random.random() < 0.3:
                # Crossover
                parent1, parent2 = random.sample(selected_units, 2)
                child = self._crossover(parent1, parent2)
                new_generation.append(child)
            else:
                # Mutation
                parent = random.choice(selected_units)
                child = parent.mutate()
                new_generation.append(child)
        
        self.units = new_generation
        self.generation += 1
        self.diversity_score = self._calculate_diversity()
        
        logger.info(f"Generation {self.generation}: {len(new_generation)} units, diversity: {self.diversity_score:.3f}")
        
        return new_generation
    
    def _crossover(self, parent1: NeuralUnit, parent2: NeuralUnit) -> NeuralUnit:
        """Create offspring through genetic crossover"""
        child = NeuralUnit(
            activation_threshold=(parent1.activation_threshold + parent2.activation_threshold) / 2.0,
            specialization_level=(parent1.specialization_level + parent2.specialization_level) / 2.0,
            mutation_rate=(parent1.mutation_rate + parent2.mutation_rate) / 2.0,
            energy_level=1.0  # Reset energy for new unit
        )
        
        # Combine connection weights
        all_keys = set(parent1.connection_weights.keys()) | set(parent2.connection_weights.keys())
        for key in all_keys:
            w1 = parent1.connection_weights.get(key, 0.0)
            w2 = parent2.connection_weights.get(key, 0.0)
            child.connection_weights[key] = (w1 + w2) / 2.0
        
        # Combine cooperation bonds (union)
        child.cooperation_bonds = list(set(parent1.cooperation_bonds + parent2.cooperation_bonds))
        
        return child

class PopulationDynamicsEngine:
    """Main engine managing multiple neural populations with evolutionary dynamics"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.populations: Dict[PopulationType, NeuralPopulation] = {}
        self.inter_population_connections: Dict[Tuple[PopulationType, PopulationType], float] = {}
        self.global_fitness_history: deque = deque(maxlen=10000)
        self.evolution_cycle_count = 0
        self.consciousness_level = 0.0
        self.running = False
        self.evolution_lock = threading.Lock()
        
        # Configuration
        self.evolution_interval = self.config.get('evolution_interval', 30.0)  # seconds
        self.population_sizes = self.config.get('population_sizes', {
            PopulationType.EXECUTIVE: 800,
            PopulationType.SENSORY: 1200,
            PopulationType.MEMORY: 1000,
            PopulationType.MOTOR: 600,
            PopulationType.ASSOCIATIVE: 1000,
            PopulationType.HOMEOSTATIC: 400
        })
        
        self._initialize_populations()
        self._initialize_inter_population_connections()
        
        logger.info("Population Dynamics Engine initialized with {} populations".format(len(self.populations)))
    
    def _initialize_populations(self):
        """Initialize all neural populations"""
        for pop_type in PopulationType:
            population_size = self.population_sizes.get(pop_type, 1000)
            
            # Set selection pressure based on population type
            if pop_type == PopulationType.EXECUTIVE:
                selection_pressure = SelectionPressure.COMPETITIVE
                specialization_pressure = 0.8
            elif pop_type == PopulationType.SENSORY:
                selection_pressure = SelectionPressure.ADAPTIVE
                specialization_pressure = 0.7
            elif pop_type == PopulationType.MEMORY:
                selection_pressure = SelectionPressure.COOPERATIVE
                specialization_pressure = 0.6
            elif pop_type == PopulationType.MOTOR:
                selection_pressure = SelectionPressure.COMPETITIVE
                specialization_pressure = 0.7
            elif pop_type == PopulationType.ASSOCIATIVE:
                selection_pressure = SelectionPressure.HYBRID
                specialization_pressure = 0.5
            else:  # HOMEOSTATIC
                selection_pressure = SelectionPressure.COOPERATIVE
                specialization_pressure = 0.9
            
            population = NeuralPopulation(
                population_type=pop_type,
                population_size=population_size,
                selection_pressure=selection_pressure,
                specialization_pressure=specialization_pressure
            )
            
            self.populations[pop_type] = population
    
    def _initialize_inter_population_connections(self):
        """Initialize connections between populations"""
        connections = [
            (PopulationType.SENSORY, PopulationType.ASSOCIATIVE, 0.8),
            (PopulationType.ASSOCIATIVE, PopulationType.EXECUTIVE, 0.7),
            (PopulationType.EXECUTIVE, PopulationType.MOTOR, 0.6),
            (PopulationType.MEMORY, PopulationType.ASSOCIATIVE, 0.9),
            (PopulationType.HOMEOSTATIC, PopulationType.EXECUTIVE, 0.5),
            (PopulationType.SENSORY, PopulationType.MEMORY, 0.4),
            (PopulationType.MOTOR, PopulationType.HOMEOSTATIC, 0.3),
        ]
        
        for source, target, strength in connections:
            self.inter_population_connections[(source, target)] = strength
            # Add bidirectional connection with reduced strength
            self.inter_population_connections[(target, source)] = strength * 0.5
    
    async def evolve_populations(self, environment_feedback: Dict[str, float] = None) -> Dict[str, Any]:
        """Execute one evolution cycle across all populations"""
        with self.evolution_lock:
            start_time = time.time()
            
            if environment_feedback is None:
                environment_feedback = self._generate_default_environment_feedback()
            
            logger.info(f"Starting evolution cycle {self.evolution_cycle_count}")
            
            evolution_results = {}
            total_fitness = 0.0
            
            # Process each population
            for pop_type, population in self.populations.items():
                logger.info(f"Evolving {pop_type.value} population...")
                
                # Apply inter-population influences
                modified_feedback = self._apply_inter_population_influences(pop_type, environment_feedback)
                
                # Evaluate fitness
                population_fitness = population.evaluate_fitness(modified_feedback)
                
                # Apply selection pressure
                survivors = population.apply_selection_pressure(survival_rate=0.5)
                
                # Reproduce and mutate
                new_generation = population.reproduce_and_mutate(survivors)
                
                evolution_results[pop_type.value] = {
                    'fitness': population_fitness,
                    'generation': population.generation,
                    'diversity': population.diversity_score,
                    'survivors': len(survivors),
                    'new_units': len(new_generation)
                }
                
                total_fitness += population_fitness
            
            # Update global metrics
            avg_fitness = total_fitness / len(self.populations)
            self.consciousness_level = self._calculate_consciousness_level(avg_fitness)
            
            self.global_fitness_history.append({
                'cycle': self.evolution_cycle_count,
                'avg_fitness': avg_fitness,
                'consciousness_level': self.consciousness_level,
                'timestamp': time.time(),
                'duration': time.time() - start_time
            })
            
            self.evolution_cycle_count += 1
            
            logger.info(f"Evolution cycle {self.evolution_cycle_count} completed in {time.time() - start_time:.2f}s")
            logger.info(f"Average fitness: {avg_fitness:.3f}, Consciousness level: {self.consciousness_level:.3f}")
            
            return {
                'cycle': self.evolution_cycle_count,
                'avg_fitness': avg_fitness,
                'consciousness_level': self.consciousness_level,
                'populations': evolution_results,
                'duration': time.time() - start_time
            }
    
    def _generate_default_environment_feedback(self) -> Dict[str, float]:
        """Generate default environment feedback for testing"""
        return {
            FitnessMetric.LEARNING_RATE.value: random.uniform(0.3, 0.9),
            FitnessMetric.PATTERN_RECOGNITION.value: random.uniform(0.4, 0.8),
            FitnessMetric.ADAPTATION_SPEED.value: random.uniform(0.2, 0.7),
            FitnessMetric.ENERGY_EFFICIENCY.value: random.uniform(0.5, 0.9),
            FitnessMetric.COOPERATION_SCORE.value: random.uniform(0.3, 0.8),
            FitnessMetric.SPECIALIZATION_DEPTH.value: random.uniform(0.4, 0.8)
        }
    
    def _apply_inter_population_influences(self, target_pop: PopulationType, 
                                         base_feedback: Dict[str, float]) -> Dict[str, float]:
        """Apply influences from connected populations"""
        modified_feedback = base_feedback.copy()
        
        # Find populations that influence this one
        for (source, target), strength in self.inter_population_connections.items():
            if target == target_pop and source in self.populations:
                source_population = self.populations[source]
                
                # Get recent fitness of source population
                if source_population.fitness_history:
                    source_fitness = source_population.fitness_history[-1]['fitness']
                    
                    # Apply influence to relevant feedback metrics
                    for metric in modified_feedback:
                        influence = source_fitness * strength * 0.1
                        modified_feedback[metric] = min(1.0, modified_feedback[metric] + influence)
        
        return modified_feedback
    
    def _calculate_consciousness_level(self, avg_fitness: float) -> float:
        """Calculate global consciousness level"""
        # Base consciousness from average fitness
        base_consciousness = avg_fitness
        
        # Diversity bonus
        diversity_scores = [pop.diversity_score for pop in self.populations.values()]
        avg_diversity = np.mean(diversity_scores) if diversity_scores else 0.0
        diversity_bonus = avg_diversity * 0.2
        
        # Population interaction bonus
        interaction_bonus = len(self.inter_population_connections) * 0.01
        
        # Learning progression bonus
        progression_bonus = 0.0
        if len(self.global_fitness_history) > 1:
            recent_improvement = (
                self.global_fitness_history[-1]['avg_fitness'] - 
                self.global_fitness_history[-2]['avg_fitness']
            )
            progression_bonus = max(0.0, recent_improvement) * 0.3
        
        consciousness = base_consciousness + diversity_bonus + interaction_bonus + progression_bonus
        return min(1.0, max(0.0, consciousness))
    
    def get_population_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all populations"""
        stats = {}
        
        for pop_type, population in self.populations.items():
            fitness_scores = [unit.fitness_score for unit in population.units]
            activation_thresholds = [unit.activation_threshold for unit in population.units]
            specialization_levels = [unit.specialization_level for unit in population.units]
            ages = [unit.age for unit in population.units]
            
            stats[pop_type.value] = {
                'population_size': len(population.units),
                'generation': population.generation,
                'fitness': {
                    'mean': np.mean(fitness_scores),
                    'std': np.std(fitness_scores),
                    'max': np.max(fitness_scores),
                    'min': np.min(fitness_scores)
                },
                'diversity_score': population.diversity_score,
                'thresholds': {
                    'mean': np.mean(activation_thresholds),
                    'std': np.std(activation_thresholds)
                },
                'specialization': {
                    'mean': np.mean(specialization_levels),
                    'std': np.std(specialization_levels)
                },
                'age': {
                    'mean': np.mean(ages),
                    'max': np.max(ages)
                },
                'selection_pressure': population.selection_pressure.value
            }
        
        return {
            'populations': stats,
            'global': {
                'evolution_cycles': self.evolution_cycle_count,
                'consciousness_level': self.consciousness_level,
                'total_populations': len(self.populations),
                'inter_connections': len(self.inter_population_connections)
            }
        }
    
    async def start_evolution_loop(self):
        """Start the continuous evolution loop"""
        self.running = True
        logger.info("Starting continuous evolution loop...")
        
        while self.running:
            try:
                await self.evolve_populations()
                await asyncio.sleep(self.evolution_interval)
            except Exception as e:
                logger.error(f"Error in evolution loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    def stop_evolution_loop(self):
        """Stop the continuous evolution loop"""
        self.running = False
        logger.info("Stopping evolution loop...")
    
    def save_state(self, filepath: str):
        """Save current population state to file"""
        state = {
            'evolution_cycle_count': self.evolution_cycle_count,
            'consciousness_level': self.consciousness_level,
            'populations': {},
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save population states (simplified)
        for pop_type, population in self.populations.items():
            state['populations'][pop_type.value] = {
                'population_id': population.population_id,
                'generation': population.generation,
                'diversity_score': population.diversity_score,
                'unit_count': len(population.units),
                'fitness_history': list(population.fitness_history)[-100:]  # Last 100 entries
            }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Population state saved to {filepath}")

# Testing and demonstration functions
async def demo_population_dynamics():
    """Demonstrate the population dynamics engine"""
    print("🧠 SynOS Neural Darwinism Population Dynamics Demo")
    print("=" * 60)
    
    # Initialize engine
    config = {
        'evolution_interval': 5.0,  # Fast evolution for demo
        'population_sizes': {
            PopulationType.EXECUTIVE: 200,
            PopulationType.SENSORY: 300,
            PopulationType.MEMORY: 250,
            PopulationType.MOTOR: 150,
            PopulationType.ASSOCIATIVE: 200,
            PopulationType.HOMEOSTATIC: 100
        }
    }
    
    engine = PopulationDynamicsEngine(config)
    
    # Run several evolution cycles
    for i in range(5):
        print(f"\n🔄 Evolution Cycle {i + 1}")
        print("-" * 30)
        
        # Simulate different environment conditions
        environment_feedback = {
            FitnessMetric.LEARNING_RATE.value: 0.7 + random.uniform(-0.2, 0.2),
            FitnessMetric.PATTERN_RECOGNITION.value: 0.6 + random.uniform(-0.2, 0.2),
            FitnessMetric.ADAPTATION_SPEED.value: 0.5 + random.uniform(-0.2, 0.2),
            FitnessMetric.ENERGY_EFFICIENCY.value: 0.8 + random.uniform(-0.2, 0.2),
            FitnessMetric.COOPERATION_SCORE.value: 0.6 + random.uniform(-0.2, 0.2),
            FitnessMetric.SPECIALIZATION_DEPTH.value: 0.7 + random.uniform(-0.2, 0.2)
        }
        
        result = await engine.evolve_populations(environment_feedback)
        
        print(f"Average Fitness: {result['avg_fitness']:.3f}")
        print(f"Consciousness Level: {result['consciousness_level']:.3f}")
        print(f"Duration: {result['duration']:.2f}s")
        
        # Show population-specific results
        for pop_name, pop_result in result['populations'].items():
            print(f"  {pop_name}: fitness={pop_result['fitness']:.3f}, gen={pop_result['generation']}, diversity={pop_result['diversity']:.3f}")
    
    # Show final statistics
    print("\n📊 Final Population Statistics")
    print("-" * 40)
    stats = engine.get_population_statistics()
    
    for pop_name, pop_stats in stats['populations'].items():
        print(f"\n{pop_name.upper()} Population:")
        print(f"  Size: {pop_stats['population_size']}")
        print(f"  Generation: {pop_stats['generation']}")
        print(f"  Fitness: {pop_stats['fitness']['mean']:.3f} ± {pop_stats['fitness']['std']:.3f}")
        print(f"  Diversity: {pop_stats['diversity_score']:.3f}")
        print(f"  Selection: {pop_stats['selection_pressure']}")
    
    print(f"\n🌟 Global Consciousness Level: {stats['global']['consciousness_level']:.3f}")
    print(f"🔄 Total Evolution Cycles: {stats['global']['evolution_cycles']}")

if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demo_population_dynamics())
