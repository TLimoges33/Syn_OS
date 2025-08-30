#!/usr/bin/env python3
"""
Neural Darwinism Engine
======================

Implements Neural Darwinism for consciousness computing using:
- Adaptive neural network populations
- Evolutionary selection mechanisms
- Competitive learning algorithms
- Emergent consciousness behaviors
"""

import time
import random
import logging
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger('consciousness.neural_darwinism')

@dataclass
class NeuralPopulation:
    """Neural population with evolutionary properties"""
    population_id: str
    size: int
    neurons: List[Dict[str, Any]] = field(default_factory=list)
    fitness_scores: List[float] = field(default_factory=list)
    generation: int = 0
    species_diversity: float = 1.0
    selection_pressure: float = 0.5
    mutation_rate: float = 0.1
    learning_rate: float = 0.01
    specialization: str = "general"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class NeuralGroup:
    """Competitive neural group in the Darwinian system"""
    group_id: str
    neurons: List[int]
    activity_level: float = 0.0
    competition_strength: float = 1.0
    cooperation_level: float = 0.5
    fitness: float = 0.0
    age: int = 0
    last_active: datetime = field(default_factory=datetime.now)

@dataclass
class SelectionEvent:
    """Neural selection event record"""
    event_id: str
    population_id: str
    selected_neurons: List[int]
    fitness_threshold: float
    selection_type: str  # 'competitive', 'cooperative', 'random'
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class NeuralDarwinismEngine:
    """
    Neural Darwinism Engine implementing evolutionary consciousness
    
    Based on Gerald Edelman's Theory of Neuronal Group Selection (TNGS)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.logger = logging.getLogger('consciousness.neural_darwinism')
        
        # Neural populations
        self.populations: Dict[str, NeuralPopulation] = {}
        self.neural_groups: Dict[str, NeuralGroup] = {}
        self.active_groups: List[str] = []
        
        # Evolutionary mechanisms
        self.selection_history: deque = deque(maxlen=10000)
        self.fitness_tracker: Dict[str, List[float]] = defaultdict(list)
        self.diversity_metrics: Dict[str, float] = {}
        
        # Competition and cooperation
        self.competition_matrix: np.ndarray = None
        self.cooperation_bonds: Dict[str, List[str]] = defaultdict(list)
        
        # Threading
        self.evolution_lock = threading.Lock()
        self.evolution_thread: Optional[threading.Thread] = None
        
        # Performance metrics
        self.evolution_cycles = 0
        self.successful_adaptations = 0
        self.consciousness_emergence_events = 0
        
    def initialize(self) -> bool:
        """Initialize the Neural Darwinism Engine"""
        try:
            self.logger.info("Initializing Neural Darwinism Engine...")
            
            # Create initial populations
            self._create_initial_populations()
            
            # Initialize competition matrices
            self._initialize_competition_matrices()
            
            # Setup evolutionary mechanisms
            self._setup_evolutionary_mechanisms()
            
            self.logger.info("Neural Darwinism Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Neural Darwinism Engine: {e}")
            return False
    
    def start(self) -> None:
        """Start the evolutionary engine"""
        if self.running:
            return
        
        self.running = True
        self.logger.info("Starting Neural Darwinism Engine...")
        
        # Start evolution thread
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()
        
        self.logger.info("Neural Darwinism Engine started")
    
    def stop(self) -> None:
        """Stop the evolutionary engine"""
        if not self.running:
            return
        
        self.logger.info("Stopping Neural Darwinism Engine...")
        self.running = False
        
        if self.evolution_thread:
            self.evolution_thread.join(timeout=5.0)
        
        self.logger.info("Neural Darwinism Engine stopped")
    
    def _create_initial_populations(self) -> None:
        """Create initial neural populations"""
        population_configs = self.config.get('populations', [])
        
        for pop_config in population_configs:
            pop_id = pop_config['id']
            pop_size = pop_config.get('size', 1000)
            specialization = pop_config.get('specialization', 'general')
            
            population = NeuralPopulation(
                population_id=pop_id,
                size=pop_size,
                specialization=specialization
            )
            
            # Create neurons for this population
            population.neurons = self._create_neurons(pop_size, specialization)
            population.fitness_scores = [0.0] * pop_size
            
            self.populations[pop_id] = population
            self.logger.info(f"Created population '{pop_id}' with {pop_size} neurons")
        
        # Create default population if none configured
        if not self.populations:
            default_pop = NeuralPopulation(
                population_id="default",
                size=1000,
                specialization="general"
            )
            default_pop.neurons = self._create_neurons(1000, "general")
            default_pop.fitness_scores = [0.0] * 1000
            self.populations["default"] = default_pop
    
    def _create_neurons(self, count: int, specialization: str) -> List[Dict[str, Any]]:
        """Create neurons with specified specialization"""
        neurons = []
        
        for i in range(count):
            neuron = {
                'id': f"{specialization}_{i}",
                'activation': 0.0,
                'threshold': random.uniform(0.3, 0.7),
                'connections': [],
                'weights': [],
                'plasticity': random.uniform(0.1, 0.9),
                'adaptation_rate': random.uniform(0.01, 0.1),
                'specialization': specialization,
                'age': 0,
                'activity_history': deque(maxlen=100),
                'fitness': 0.0
            }
            
            # Add specialization-specific properties
            if specialization == "sensory":
                neuron['sensitivity'] = random.uniform(0.5, 1.0)
                neuron['noise_tolerance'] = random.uniform(0.1, 0.3)
            elif specialization == "motor":
                neuron['response_speed'] = random.uniform(0.7, 1.0)
                neuron['precision'] = random.uniform(0.5, 0.9)
            elif specialization == "memory":
                neuron['retention_time'] = random.uniform(100, 1000)
                neuron['consolidation_rate'] = random.uniform(0.1, 0.5)
            elif specialization == "executive":
                neuron['decision_threshold'] = random.uniform(0.6, 0.9)
                neuron['integration_capacity'] = random.uniform(0.7, 1.0)
            
            neurons.append(neuron)
        
        return neurons
    
    def _initialize_competition_matrices(self) -> None:
        """Initialize competition matrices between neural groups"""
        total_neurons = sum(len(pop.neurons) for pop in self.populations.values())
        
        if total_neurons > 0:
            # Initialize competition matrix
            self.competition_matrix = np.random.uniform(0.1, 0.9, (total_neurons, total_neurons))
            # Make it symmetric
            self.competition_matrix = (self.competition_matrix + self.competition_matrix.T) / 2
            # Zero diagonal (neurons don't compete with themselves)
            np.fill_diagonal(self.competition_matrix, 0)
    
    def _setup_evolutionary_mechanisms(self) -> None:
        """Setup evolutionary selection mechanisms"""
        # Create neural groups for competition
        self._create_neural_groups()
        
        # Initialize selection pressures
        self._initialize_selection_pressures()
    
    def _create_neural_groups(self) -> None:
        """Create neural groups for competitive dynamics"""
        group_id = 0
        
        for pop_id, population in self.populations.items():
            # Create groups of 10-50 neurons each
            group_size = random.randint(10, 50)
            
            for i in range(0, len(population.neurons), group_size):
                neurons_in_group = list(range(i, min(i + group_size, len(population.neurons))))
                
                if len(neurons_in_group) >= 5:  # Minimum group size
                    group = NeuralGroup(
                        group_id=f"{pop_id}_group_{group_id}",
                        neurons=neurons_in_group,
                        competition_strength=random.uniform(0.3, 1.0),
                        cooperation_level=random.uniform(0.2, 0.8)
                    )
                    
                    self.neural_groups[group.group_id] = group
                    group_id += 1
        
        self.logger.info(f"Created {len(self.neural_groups)} neural groups")
    
    def _initialize_selection_pressures(self) -> None:
        """Initialize selection pressures for evolution"""
        for population in self.populations.values():
            # Set initial selection pressure based on specialization
            if population.specialization == "executive":
                population.selection_pressure = 0.8  # High pressure for decision-making
            elif population.specialization == "sensory":
                population.selection_pressure = 0.6  # Moderate pressure for perception
            elif population.specialization == "memory":
                population.selection_pressure = 0.4  # Lower pressure for storage
            else:
                population.selection_pressure = 0.5  # Default pressure
    
    def _evolution_loop(self) -> None:
        """Main evolutionary loop"""
        while self.running:
            try:
                # Execute one evolution cycle
                self._evolution_cycle()
                
                # Sleep based on configuration
                evolution_interval = self.config.get('evolution_interval', 1.0)
                time.sleep(evolution_interval)
                
            except Exception as e:
                self.logger.error(f"Error in evolution loop: {e}")
                time.sleep(5.0)
    
    def _evolution_cycle(self) -> None:
        """Execute one cycle of neural evolution"""
        with self.evolution_lock:
            try:
                # Update neural activities
                self._update_neural_activities()
                
                # Perform competitive selection
                self._competitive_selection()
                
                # Update fitness scores
                self._update_fitness_scores()
                
                # Perform adaptation
                self._neural_adaptation()
                
                # Check for consciousness emergence
                self._check_consciousness_emergence()
                
                # Update diversity metrics
                self._update_diversity_metrics()
                
                self.evolution_cycles += 1
                
                if self.evolution_cycles % 100 == 0:
                    self.logger.info(f"Evolution cycle {self.evolution_cycles} completed")
                
            except Exception as e:
                self.logger.error(f"Error in evolution cycle: {e}")
    
    def _update_neural_activities(self) -> None:
        """Update activities of all neurons"""
        for population in self.populations.values():
            for neuron in population.neurons:
                # Simulate neural activity based on inputs and connections
                activity = self._calculate_neural_activity(neuron)
                neuron['activation'] = activity
                neuron['activity_history'].append(activity)
                neuron['age'] += 1
    
    def _calculate_neural_activity(self, neuron: Dict[str, Any]) -> float:
        """Calculate neural activity for a neuron"""
        # Simplified neural activity calculation
        base_activity = random.uniform(0.0, 1.0)
        
        # Apply threshold
        if base_activity > neuron['threshold']:
            activity = base_activity * neuron['plasticity']
        else:
            activity = base_activity * 0.1
        
        # Add noise based on specialization
        if neuron['specialization'] == 'sensory':
            noise_level = neuron.get('noise_tolerance', 0.2)
            activity += random.uniform(-noise_level, noise_level)
        
        return max(0.0, min(1.0, activity))
    
    def _competitive_selection(self) -> None:
        """Perform competitive selection between neural groups"""
        for group_id, group in self.neural_groups.items():
            # Calculate group fitness
            group_fitness = self._calculate_group_fitness(group)
            group.fitness = group_fitness
            
            # Update competition strength based on fitness
            if group_fitness > 0.7:
                group.competition_strength = min(1.0, group.competition_strength + 0.1)
            elif group_fitness < 0.3:
                group.competition_strength = max(0.1, group.competition_strength - 0.1)
            
            # Record selection event
            if group_fitness > 0.8:  # High-performing group
                selection_event = SelectionEvent(
                    event_id=f"selection_{time.time()}",
                    population_id=group_id.split('_')[0],
                    selected_neurons=group.neurons.copy(),
                    fitness_threshold=0.8,
                    selection_type='competitive',
                    timestamp=datetime.now(),
                    metadata={'group_fitness': group_fitness}
                )
                self.selection_history.append(selection_event)
    
    def _calculate_group_fitness(self, group: NeuralGroup) -> float:
        """Calculate fitness for a neural group"""
        # Get neurons in this group
        total_activity = 0.0
        active_neurons = 0
        
        # Find the population this group belongs to
        population = None
        for pop in self.populations.values():
            if group.neurons[0] < len(pop.neurons):
                population = pop
                break
        
        if not population:
            return 0.0
        
        # Calculate average activity of neurons in group
        for neuron_idx in group.neurons:
            if neuron_idx < len(population.neurons):
                neuron = population.neurons[neuron_idx]
                if neuron['activation'] > 0.1:
                    total_activity += neuron['activation']
                    active_neurons += 1
        
        if active_neurons == 0:
            return 0.0
        
        average_activity = total_activity / active_neurons
        
        # Apply group-specific factors
        cooperation_bonus = group.cooperation_level * 0.2
        competition_penalty = group.competition_strength * 0.1
        age_factor = max(0.5, 1.0 - (group.age * 0.001))  # Gradual aging
        
        fitness = average_activity + cooperation_bonus - competition_penalty
        fitness *= age_factor
        
        return max(0.0, min(1.0, fitness))
    
    def _update_fitness_scores(self) -> None:
        """Update fitness scores for all neurons and populations"""
        for pop_id, population in self.populations.items():
            for i, neuron in enumerate(population.neurons):
                # Calculate individual neuron fitness
                activity_score = neuron['activation']
                plasticity_score = neuron['plasticity']
                age_factor = max(0.3, 1.0 - (neuron['age'] * 0.0001))
                
                # Specialization bonus
                specialization_bonus = 0.0
                if neuron['specialization'] == 'executive' and activity_score > 0.7:
                    specialization_bonus = 0.2
                elif neuron['specialization'] == 'sensory' and activity_score > 0.5:
                    specialization_bonus = 0.1
                
                fitness = (activity_score * 0.6 + plasticity_score * 0.4 + specialization_bonus) * age_factor
                neuron['fitness'] = fitness
                population.fitness_scores[i] = fitness
            
            # Track population fitness
            avg_fitness = sum(population.fitness_scores) / len(population.fitness_scores)
            self.fitness_tracker[pop_id].append(avg_fitness)
    
    def _neural_adaptation(self) -> None:
        """Perform neural adaptation based on fitness"""
        for population in self.populations.values():
            # Select top performers for reinforcement
            sorted_indices = sorted(range(len(population.fitness_scores)), 
                                  key=lambda i: population.fitness_scores[i], reverse=True)
            
            top_performers = sorted_indices[:int(len(sorted_indices) * 0.2)]  # Top 20%
            poor_performers = sorted_indices[-int(len(sorted_indices) * 0.1):]  # Bottom 10%
            
            # Strengthen top performers
            for idx in top_performers:
                neuron = population.neurons[idx]
                neuron['plasticity'] = min(1.0, neuron['plasticity'] + population.learning_rate)
                neuron['threshold'] *= 0.95  # Make more sensitive
            
            # Weaken or replace poor performers
            for idx in poor_performers:
                neuron = population.neurons[idx]
                if random.random() < population.mutation_rate:
                    # Mutate the neuron
                    neuron['threshold'] = random.uniform(0.3, 0.7)
                    neuron['plasticity'] = random.uniform(0.1, 0.9)
                    neuron['adaptation_rate'] = random.uniform(0.01, 0.1)
                    self.successful_adaptations += 1
    
    def _check_consciousness_emergence(self) -> None:
        """Check for consciousness emergence events"""
        # Look for synchronized activity across populations
        consciousness_threshold = self.config.get('consciousness_threshold', 0.8)
        
        high_activity_populations = 0
        total_activity = 0.0
        
        for population in self.populations.values():
            avg_activity = sum(neuron['activation'] for neuron in population.neurons) / len(population.neurons)
            total_activity += avg_activity
            
            if avg_activity > consciousness_threshold:
                high_activity_populations += 1
        
        # Check for consciousness emergence
        if (high_activity_populations >= len(self.populations) * 0.7 and 
            total_activity / len(self.populations) > consciousness_threshold):
            
            self.consciousness_emergence_events += 1
            self.logger.info(f"Consciousness emergence event #{self.consciousness_emergence_events} detected")
            
            # Create consciousness event record
            emergence_event = {
                'event_id': f"consciousness_{time.time()}",
                'timestamp': datetime.now(),
                'total_activity': total_activity / len(self.populations),
                'active_populations': high_activity_populations,
                'total_populations': len(self.populations),
                'emergence_strength': min(1.0, total_activity / len(self.populations))
            }
            
            # This could trigger higher-level consciousness processes
            self._handle_consciousness_emergence(emergence_event)
    
    def _handle_consciousness_emergence(self, event: Dict[str, Any]) -> None:
        """Handle consciousness emergence event"""
        # This is where higher-level consciousness behaviors would be triggered
        self.logger.info(f"Handling consciousness emergence with strength {event['emergence_strength']:.3f}")
        
        # Could trigger:
        # - Global workspace activation
        # - Attention focusing mechanisms
        # - Memory consolidation
        # - Decision making processes
    
    def _update_diversity_metrics(self) -> None:
        """Update diversity metrics for populations"""
        for pop_id, population in self.populations.items():
            # Calculate diversity based on neural properties
            thresholds = [neuron['threshold'] for neuron in population.neurons]
            plasticities = [neuron['plasticity'] for neuron in population.neurons]
            
            threshold_diversity = np.std(thresholds)
            plasticity_diversity = np.std(plasticities)
            
            # Combined diversity metric
            diversity = (threshold_diversity + plasticity_diversity) / 2
            self.diversity_metrics[pop_id] = diversity
            
            # Update population diversity
            population.species_diversity = diversity
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the Neural Darwinism Engine"""
        with self.evolution_lock:
            return {
                'running': self.running,
                'evolution_cycles': self.evolution_cycles,
                'successful_adaptations': self.successful_adaptations,
                'consciousness_emergence_events': self.consciousness_emergence_events,
                'populations': {
                    pop_id: {
                        'size': len(pop.neurons),
                        'generation': pop.generation,
                        'avg_fitness': sum(pop.fitness_scores) / len(pop.fitness_scores) if pop.fitness_scores else 0,
                        'diversity': pop.species_diversity,
                        'specialization': pop.specialization
                    }
                    for pop_id, pop in self.populations.items()
                },
                'neural_groups': len(self.neural_groups),
                'active_groups': len(self.active_groups),
                'diversity_metrics': self.diversity_metrics.copy()
            }
    
    def get_consciousness_level(self) -> float:
        """Get current consciousness level"""
        if not self.populations:
            return 0.0
        
        total_activity = 0.0
        for population in self.populations.values():
            avg_activity = sum(neuron['activation'] for neuron in population.neurons) / len(population.neurons)
            total_activity += avg_activity
        
        return total_activity / len(self.populations)
    
    def trigger_adaptation(self, trigger_type: str, metadata: Dict[str, Any] = None) -> None:
        """Trigger adaptive response to external stimulus"""
        with self.evolution_lock:
            self.logger.info(f"Triggering adaptation: {trigger_type}")
            
            # Increase selection pressure temporarily
            for population in self.populations.values():
                population.selection_pressure = min(1.0, population.selection_pressure + 0.2)
            
            # Force immediate adaptation cycle
            self._neural_adaptation()
            
            # Reset selection pressure
            for population in self.populations.values():
                population.selection_pressure = max(0.1, population.selection_pressure - 0.1)