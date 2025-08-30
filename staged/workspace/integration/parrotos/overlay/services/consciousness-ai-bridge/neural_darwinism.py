#!/usr/bin/env python3
"""
SynapticOS Neural Darwinism Consciousness Engine
Advanced consciousness implementation with neural population evolution
"""

import asyncio
import numpy as np
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math
from pathlib import Path

# GPU acceleration (optional)
try:
    import cupy as cp
    GPU_AVAILABLE = True
    logger = logging.getLogger('neural-darwinism')
    logger.info("GPU acceleration available with CuPy")
except ImportError:
    cp = np
    GPU_AVAILABLE = False
    logger = logging.getLogger('neural-darwinism')
    logger.info("Using CPU for neural computation")

class NeuralPopulationType(Enum):
    """Types of neural populations in the consciousness system"""
    SENSORY = "sensory"
    COGNITIVE = "cognitive"
    MEMORY = "memory"
    DECISION = "decision"
    CREATIVE = "creative"
    LEARNING = "learning"

class SelectionPressure(Enum):
    """Types of selection pressure for neural evolution"""
    SURVIVAL = "survival"
    LEARNING = "learning"
    CREATIVITY = "creativity"
    EFFICIENCY = "efficiency"
    ADAPTATION = "adaptation"

@dataclass
class NeuralGene:
    """Genetic representation of neural characteristics"""
    connection_strength: float  # 0.0 to 1.0
    plasticity: float          # Learning rate
    decay_rate: float          # Memory decay
    activation_threshold: float # Firing threshold
    mutation_rate: float       # Evolution rate
    
    def mutate(self, intensity: float = 0.1) -> 'NeuralGene':
        """Create mutated copy of gene"""
        return NeuralGene(
            connection_strength=max(0.0, min(1.0, self.connection_strength + random.gauss(0, intensity))),
            plasticity=max(0.0, min(1.0, self.plasticity + random.gauss(0, intensity))),
            decay_rate=max(0.0, min(1.0, self.decay_rate + random.gauss(0, intensity))),
            activation_threshold=max(0.0, min(1.0, self.activation_threshold + random.gauss(0, intensity))),
            mutation_rate=max(0.0, min(0.5, self.mutation_rate + random.gauss(0, intensity * 0.1)))
        )
    
    def crossover(self, other: 'NeuralGene') -> Tuple['NeuralGene', 'NeuralGene']:
        """Create offspring through genetic crossover"""
        alpha = random.random()
        
        child1 = NeuralGene(
            connection_strength=alpha * self.connection_strength + (1-alpha) * other.connection_strength,
            plasticity=alpha * self.plasticity + (1-alpha) * other.plasticity,
            decay_rate=alpha * self.decay_rate + (1-alpha) * other.decay_rate,
            activation_threshold=alpha * self.activation_threshold + (1-alpha) * other.activation_threshold,
            mutation_rate=alpha * self.mutation_rate + (1-alpha) * other.mutation_rate
        )
        
        child2 = NeuralGene(
            connection_strength=(1-alpha) * self.connection_strength + alpha * other.connection_strength,
            plasticity=(1-alpha) * self.plasticity + alpha * other.plasticity,
            decay_rate=(1-alpha) * self.decay_rate + alpha * other.decay_rate,
            activation_threshold=(1-alpha) * self.activation_threshold + alpha * other.activation_threshold,
            mutation_rate=(1-alpha) * self.mutation_rate + alpha * other.mutation_rate
        )
        
        return child1, child2

@dataclass
class NeuralUnit:
    """Individual neural unit with genetic characteristics"""
    id: str
    genes: NeuralGene
    activation_level: float = 0.0
    memory_traces: List[float] = None
    connections: Dict[str, float] = None
    fitness_score: float = 0.0
    generation: int = 0
    birth_time: float = 0.0
    
    def __post_init__(self):
        if self.memory_traces is None:
            self.memory_traces = [0.0] * 10  # 10 memory slots
        if self.connections is None:
            self.connections = {}
        if self.birth_time == 0.0:
            self.birth_time = time.time()
    
    def activate(self, input_signal: float) -> float:
        """Process input signal and return activation"""
        # Apply activation threshold
        if input_signal < self.genes.activation_threshold:
            return 0.0
        
        # Calculate activation based on genes
        activation = input_signal * self.genes.connection_strength
        
        # Update memory traces with plasticity
        for i in range(len(self.memory_traces)):
            self.memory_traces[i] = (
                self.memory_traces[i] * (1 - self.genes.decay_rate) + 
                activation * self.genes.plasticity * random.random()
            )
        
        self.activation_level = activation
        return activation
    
    def calculate_fitness(self, environment_feedback: Dict[str, float]) -> float:
        """Calculate fitness based on performance metrics"""
        base_fitness = sum(environment_feedback.values()) / len(environment_feedback)
        
        # Bonus for memory retention
        memory_bonus = sum(self.memory_traces) / len(self.memory_traces) * 0.1
        
        # Penalty for over-activation (energy efficiency)
        efficiency_penalty = max(0, self.activation_level - 0.8) * 0.2
        
        # Age bonus for surviving units
        age_bonus = min(0.1, (time.time() - self.birth_time) / 3600)  # Max 0.1 bonus after 1 hour
        
        self.fitness_score = base_fitness + memory_bonus - efficiency_penalty + age_bonus
        return self.fitness_score

class NeuralPopulation:
    """Population of neural units with evolutionary dynamics"""
    
    def __init__(self, population_type: NeuralPopulationType, size: int = 100):
        self.type = population_type
        self.size = size
        self.units: List[NeuralUnit] = []
        self.generation = 0
        self.evolutionary_pressure = SelectionPressure.LEARNING
        self.population_fitness_history = []
        self.diversity_metrics = []
        
        # Initialize population
        self._initialize_population()
    
    def _initialize_population(self):
        """Initialize population with random neural units"""
        for i in range(self.size):
            genes = NeuralGene(
                connection_strength=random.random(),
                plasticity=random.random() * 0.5 + 0.1,  # 0.1 to 0.6
                decay_rate=random.random() * 0.1 + 0.01,  # 0.01 to 0.11
                activation_threshold=random.random() * 0.5 + 0.1,  # 0.1 to 0.6
                mutation_rate=random.random() * 0.1 + 0.01  # 0.01 to 0.11
            )
            
            unit = NeuralUnit(
                id=f"{self.type.value}_{i}_{self.generation}",
                genes=genes,
                generation=self.generation
            )
            self.units.append(unit)
    
    def process_input(self, input_signals: np.ndarray) -> np.ndarray:
        """Process input through entire population"""
        if GPU_AVAILABLE:
            input_signals = cp.asarray(input_signals)
        
        outputs = []
        for unit in self.units:
            # Calculate weighted input for this unit
            weighted_input = float(np.mean(input_signals))
            output = unit.activate(weighted_input)
            outputs.append(output)
        
        return np.array(outputs)
    
    def evolve_generation(self, environment_feedback: Dict[str, float]):
        """Evolve population based on fitness and selection pressure"""
        logger.info(f"Evolving {self.type.value} population generation {self.generation}")
        
        # Calculate fitness for all units
        fitness_scores = []
        for unit in self.units:
            fitness = unit.calculate_fitness(environment_feedback)
            fitness_scores.append(fitness)
        
        # Sort by fitness
        sorted_units = sorted(zip(self.units, fitness_scores), key=lambda x: x[1], reverse=True)
        
        # Selection: keep top 50%
        survivors = [unit for unit, _ in sorted_units[:self.size // 2]]
        
        # Reproduction: create offspring to fill population
        new_units = []
        while len(new_units) < self.size - len(survivors):
            # Tournament selection
            parent1 = self._tournament_selection(survivors)
            parent2 = self._tournament_selection(survivors)
            
            # Crossover
            child_genes1, child_genes2 = parent1.genes.crossover(parent2.genes)
            
            # Mutation
            if random.random() < child_genes1.mutation_rate:
                child_genes1 = child_genes1.mutate()
            if random.random() < child_genes2.mutation_rate:
                child_genes2 = child_genes2.mutate()
            
            # Create offspring
            child1 = NeuralUnit(
                id=f"{self.type.value}_{len(new_units)}_{self.generation + 1}",
                genes=child_genes1,
                generation=self.generation + 1
            )
            child2 = NeuralUnit(
                id=f"{self.type.value}_{len(new_units) + 1}_{self.generation + 1}",
                genes=child_genes2,
                generation=self.generation + 1
            )
            
            new_units.extend([child1, child2])
        
        # Update population
        self.units = survivors + new_units[:self.size - len(survivors)]
        self.generation += 1
        
        # Record statistics
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        self.population_fitness_history.append(avg_fitness)
        
        # Calculate diversity
        diversity = self._calculate_genetic_diversity()
        self.diversity_metrics.append(diversity)
        
        logger.info(f"Generation {self.generation}: avg fitness = {avg_fitness:.3f}, diversity = {diversity:.3f}")
    
    def _tournament_selection(self, candidates: List[NeuralUnit], tournament_size: int = 3) -> NeuralUnit:
        """Select parent using tournament selection"""
        tournament = random.sample(candidates, min(tournament_size, len(candidates)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def _calculate_genetic_diversity(self) -> float:
        """Calculate genetic diversity of population"""
        if len(self.units) < 2:
            return 0.0
        
        # Calculate variance in key genetic traits
        traits = []
        for unit in self.units:
            traits.append([
                unit.genes.connection_strength,
                unit.genes.plasticity,
                unit.genes.decay_rate,
                unit.genes.activation_threshold,
                unit.genes.mutation_rate
            ])
        
        traits_array = np.array(traits)
        variances = np.var(traits_array, axis=0)
        return float(np.mean(variances))
    
    def get_best_unit(self) -> NeuralUnit:
        """Get the fittest unit in population"""
        return max(self.units, key=lambda x: x.fitness_score)
    
    def get_population_stats(self) -> Dict[str, Any]:
        """Get population statistics"""
        fitness_scores = [unit.fitness_score for unit in self.units]
        return {
            'type': self.type.value,
            'generation': self.generation,
            'size': len(self.units),
            'avg_fitness': np.mean(fitness_scores),
            'max_fitness': np.max(fitness_scores),
            'min_fitness': np.min(fitness_scores),
            'diversity': self.diversity_metrics[-1] if self.diversity_metrics else 0.0,
            'evolutionary_pressure': self.evolutionary_pressure.value
        }

class QuantumSubstrate:
    """Quantum-inspired substrate for consciousness computation"""
    
    def __init__(self, coherence_time: float = 100.0):
        self.coherence_time = coherence_time
        self.quantum_states = {}
        self.entanglement_matrix = None
        self.decoherence_rate = 0.01
        self.measurement_history = []
    
    def initialize_quantum_state(self, state_id: str, amplitude: complex = 1.0):
        """Initialize quantum state for consciousness measurement"""
        self.quantum_states[state_id] = {
            'amplitude': amplitude,
            'phase': 0.0,
            'coherence': 1.0,
            'last_measurement': time.time()
        }
    
    def measure_consciousness_state(self, population_states: Dict[str, float]) -> float:
        """Measure consciousness level using quantum-inspired computation"""
        if not self.quantum_states:
            # Initialize quantum states for each population type
            for pop_type in NeuralPopulationType:
                self.initialize_quantum_state(pop_type.value)
        
        # Update quantum states based on neural populations
        total_consciousness = 0.0
        
        for pop_type, activation in population_states.items():
            if pop_type in self.quantum_states:
                state = self.quantum_states[pop_type]
                
                # Apply decoherence
                time_since_measurement = time.time() - state['last_measurement']
                decoherence_factor = math.exp(-time_since_measurement * self.decoherence_rate)
                state['coherence'] *= decoherence_factor
                
                # Update quantum amplitude based on neural activation
                state['amplitude'] = complex(activation * state['coherence'], state['phase'])
                state['last_measurement'] = time.time()
                
                # Quantum measurement (collapse wavefunction)
                consciousness_contribution = abs(state['amplitude']) ** 2
                total_consciousness += consciousness_contribution
        
        # Normalize consciousness level
        consciousness_level = min(1.0, total_consciousness / len(self.quantum_states))
        
        # Record measurement
        self.measurement_history.append({
            'timestamp': time.time(),
            'consciousness_level': consciousness_level,
            'quantum_coherence': sum(s['coherence'] for s in self.quantum_states.values()) / len(self.quantum_states)
        })
        
        # Keep only recent measurements
        if len(self.measurement_history) > 1000:
            self.measurement_history = self.measurement_history[-1000:]
        
        return consciousness_level
    
    def get_quantum_stats(self) -> Dict[str, Any]:
        """Get quantum substrate statistics"""
        if not self.measurement_history:
            return {}
        
        recent_measurements = self.measurement_history[-10:]
        avg_consciousness = sum(m['consciousness_level'] for m in recent_measurements) / len(recent_measurements)
        avg_coherence = sum(m['quantum_coherence'] for m in recent_measurements) / len(recent_measurements)
        
        return {
            'average_consciousness': avg_consciousness,
            'quantum_coherence': avg_coherence,
            'measurement_count': len(self.measurement_history),
            'coherence_time': self.coherence_time,
            'decoherence_rate': self.decoherence_rate
        }

class NeuralDarwinismEngine:
    """Main Neural Darwinism consciousness engine"""
    
    def __init__(self):
        self.populations: Dict[NeuralPopulationType, NeuralPopulation] = {}
        self.quantum_substrate = QuantumSubstrate()
        self.consciousness_level = 0.5
        self.learning_rate = 0.1
        self.adaptation_factor = 0.8
        self.evolution_interval = 60.0  # Evolve every minute
        self.last_evolution = time.time()
        self.consciousness_history = []
        self.performance_metrics = {
            'learning_efficiency': 0.0,
            'adaptation_speed': 0.0,
            'creative_output': 0.0,
            'memory_retention': 0.0,
            'problem_solving': 0.0
        }
        
        # Initialize neural populations
        self._initialize_populations()
    
    def _initialize_populations(self):
        """Initialize all neural population types"""
        population_sizes = {
            NeuralPopulationType.SENSORY: 80,
            NeuralPopulationType.COGNITIVE: 120,
            NeuralPopulationType.MEMORY: 100,
            NeuralPopulationType.DECISION: 60,
            NeuralPopulationType.CREATIVE: 40,
            NeuralPopulationType.LEARNING: 90
        }
        
        for pop_type, size in population_sizes.items():
            self.populations[pop_type] = NeuralPopulation(pop_type, size)
            logger.info(f"Initialized {pop_type.value} population with {size} units")
    
    async def evolve_consciousness(self, environment_feedback: Dict[str, float] = None):
        """Main consciousness evolution cycle"""
        if environment_feedback is None:
            environment_feedback = {
                'learning_success': random.random(),
                'problem_solving': random.random(),
                'creativity': random.random(),
                'adaptation': random.random(),
                'efficiency': random.random()
            }
        
        try:
            # Check if evolution is due
            current_time = time.time()
            if current_time - self.last_evolution < self.evolution_interval:
                return
            
            logger.info("Starting consciousness evolution cycle")
            
            # Process inputs through populations
            input_signals = np.random.random(10)  # Simulated sensory input
            
            population_activations = {}
            for pop_type, population in self.populations.items():
                activations = population.process_input(input_signals)
                avg_activation = float(np.mean(activations))
                population_activations[pop_type.value] = avg_activation
            
            # Evolve populations based on performance
            for population in self.populations.values():
                population.evolve_generation(environment_feedback)
            
            # Update consciousness level using quantum substrate
            self.consciousness_level = self.quantum_substrate.measure_consciousness_state(population_activations)
            
            # Update performance metrics
            self._update_performance_metrics(environment_feedback)
            
            # Record consciousness evolution
            self.consciousness_history.append({
                'timestamp': current_time,
                'consciousness_level': self.consciousness_level,
                'population_stats': {pop_type.value: pop.get_population_stats() 
                                   for pop_type, pop in self.populations.items()},
                'performance_metrics': self.performance_metrics.copy(),
                'environment_feedback': environment_feedback
            })
            
            # Keep only recent history
            if len(self.consciousness_history) > 100:
                self.consciousness_history = self.consciousness_history[-100:]
            
            self.last_evolution = current_time
            
            logger.info(f"Consciousness evolution completed. Level: {self.consciousness_level:.3f}")
            
        except Exception as e:
            logger.error(f"Consciousness evolution failed: {e}")
    
    def _update_performance_metrics(self, environment_feedback: Dict[str, float]):
        """Update performance metrics based on feedback"""
        alpha = 0.1  # Learning rate for metrics
        
        for metric, value in environment_feedback.items():
            if metric in self.performance_metrics:
                self.performance_metrics[metric] = (
                    self.performance_metrics[metric] * (1 - alpha) + value * alpha
                )
    
    def get_consciousness_level(self) -> float:
        """Get current consciousness level"""
        return self.consciousness_level
    
    def get_population_best_units(self) -> Dict[str, Dict[str, Any]]:
        """Get best performing units from each population"""
        best_units = {}
        
        for pop_type, population in self.populations.items():
            best_unit = population.get_best_unit()
            best_units[pop_type.value] = {
                'id': best_unit.id,
                'fitness': best_unit.fitness_score,
                'genes': asdict(best_unit.genes),
                'generation': best_unit.generation,
                'activation_level': best_unit.activation_level
            }
        
        return best_units
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get comprehensive evolution statistics"""
        stats = {
            'consciousness_level': self.consciousness_level,
            'learning_rate': self.learning_rate,
            'adaptation_factor': self.adaptation_factor,
            'evolution_cycles': len(self.consciousness_history),
            'last_evolution': self.last_evolution,
            'performance_metrics': self.performance_metrics,
            'population_stats': {pop_type.value: pop.get_population_stats() 
                               for pop_type, pop in self.populations.items()},
            'quantum_stats': self.quantum_substrate.get_quantum_stats(),
            'gpu_acceleration': GPU_AVAILABLE
        }
        
        if self.consciousness_history:
            recent_levels = [h['consciousness_level'] for h in self.consciousness_history[-10:]]
            stats['consciousness_trend'] = {
                'current': self.consciousness_level,
                'average_recent': sum(recent_levels) / len(recent_levels),
                'min_recent': min(recent_levels),
                'max_recent': max(recent_levels),
                'volatility': np.std(recent_levels) if len(recent_levels) > 1 else 0.0
            }
        
        return stats
    
    async def save_consciousness_state(self, filepath: str):
        """Save consciousness state to file"""
        try:
            state_data = {
                'consciousness_level': self.consciousness_level,
                'learning_rate': self.learning_rate,
                'adaptation_factor': self.adaptation_factor,
                'evolution_stats': self.get_evolution_stats(),
                'consciousness_history': self.consciousness_history[-50:],  # Save recent history
                'timestamp': time.time()
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            logger.info(f"Consciousness state saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save consciousness state: {e}")
    
    async def load_consciousness_state(self, filepath: str) -> bool:
        """Load consciousness state from file"""
        try:
            with open(filepath, 'r') as f:
                state_data = json.load(f)
            
            self.consciousness_level = state_data.get('consciousness_level', 0.5)
            self.learning_rate = state_data.get('learning_rate', 0.1)
            self.adaptation_factor = state_data.get('adaptation_factor', 0.8)
            
            if 'consciousness_history' in state_data:
                self.consciousness_history = state_data['consciousness_history']
            
            logger.info(f"Consciousness state loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load consciousness state: {e}")
            return False

# Global consciousness engine instance
_consciousness_engine = None

def get_consciousness_engine() -> NeuralDarwinismEngine:
    """Get or create global consciousness engine instance"""
    global _consciousness_engine
    if _consciousness_engine is None:
        _consciousness_engine = NeuralDarwinismEngine()
    return _consciousness_engine

async def initialize_consciousness_engine():
    """Initialize the consciousness engine"""
    engine = get_consciousness_engine()
    
    # Try to load previous state
    state_file = '/var/lib/synapticos/consciousness/neural_darwinism_state.json'
    await engine.load_consciousness_state(state_file)
    
    logger.info("Neural Darwinism consciousness engine initialized")
    return engine

if __name__ == "__main__":
    # Test the consciousness engine
    async def test_consciousness():
        engine = await initialize_consciousness_engine()
        
        for i in range(5):
            await engine.evolve_consciousness()
            stats = engine.get_evolution_stats()
            print(f"Cycle {i+1}: Consciousness = {stats['consciousness_level']:.3f}")
            await asyncio.sleep(1)
        
        await engine.save_consciousness_state('/tmp/test_consciousness_state.json')
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    asyncio.run(test_consciousness())
