/// Consciousness Engine - Neural Darwinism Implementation
/// Implements evolutionary algorithms for AI consciousness

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info};
use rand::Rng;

use crate::ConsciousnessConfig;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsciousnessState {
    pub generation: u64,
    pub population_fitness: f64,
    pub active_neurons: usize,
    pub learning_rate: f64,
    pub adaptation_score: f64,
}

#[derive(Debug, Clone)]
struct NeuronGroup {
    id: u64,
    fitness: f64,
    connections: Vec<u64>,
    activation_pattern: Vec<f64>,
}

#[derive(Debug)]
pub struct ConsciousnessEngine {
    config: ConsciousnessConfig,
    state: Arc<RwLock<ConsciousnessState>>,
    population: Arc<RwLock<Vec<NeuronGroup>>>,
    generation: Arc<RwLock<u64>>,
}

impl ConsciousnessEngine {
    pub async fn new(config: ConsciousnessConfig) -> Result<Self> {
        info!("🧠 Initializing Neural Darwinism consciousness engine");

        let mut population = Vec::new();
        let mut rng = rand::thread_rng();

        // Initialize population of neuron groups
        for i in 0..config.population_size {
            population.push(NeuronGroup {
                id: i as u64,
                fitness: rng.gen::<f64>(),
                connections: Vec::new(),
                activation_pattern: vec![0.0; 10],
            });
        }

        let state = ConsciousnessState {
            generation: 0,
            population_fitness: 0.0,
            active_neurons: config.population_size,
            learning_rate: 0.1,
            adaptation_score: 0.0,
        };

        Ok(Self {
            config,
            state: Arc::new(RwLock::new(state)),
            population: Arc::new(RwLock::new(population)),
            generation: Arc::new(RwLock::new(0)),
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("🚀 Starting consciousness evolution loop");

        loop {
            // Evolve population
            self.evolve_generation().await?;

            // Update state
            self.update_state().await?;

            // Sleep between generations
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
        }
    }

    async fn evolve_generation(&self) -> Result<()> {
        let mut population = self.population.write().await;
        let mut generation = self.generation.write().await;

        *generation += 1;

        // Selection: Remove low-fitness neurons
        population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());
        let survivors = (population.len() as f64 * self.config.selection_pressure) as usize;
        population.truncate(survivors.max(10));

        // Create RNG after awaits to avoid Send issues
        let mut rng = rand::thread_rng();

        // Reproduction: Create new neurons from survivors
        let target_size = self.config.population_size;
        while population.len() < target_size {
            if let Some(parent) = population.get(rng.gen_range(0..population.len())) {
                let mut child = parent.clone();
                child.id = population.len() as u64;

                // Mutation
                if rng.gen::<f64>() < self.config.mutation_rate {
                    child.fitness *= rng.gen_range(0.9..1.1);
                    for activation in &mut child.activation_pattern {
                        *activation += rng.gen_range(-0.1..0.1);
                    }
                }

                population.push(child);
            }
        }

        debug!("Generation {}: {} neurons evolved", *generation, population.len());
        Ok(())
    }

    async fn update_state(&self) -> Result<()> {
        let population = self.population.read().await;
        let generation = self.generation.read().await;
        let mut state = self.state.write().await;

        state.generation = *generation;
        state.population_fitness = population.iter().map(|n| n.fitness).sum::<f64>() / population.len() as f64;
        state.active_neurons = population.len();
        state.adaptation_score = state.population_fitness * (*generation as f64).ln().max(1.0);

        Ok(())
    }

    pub async fn get_state(&self) -> Result<ConsciousnessState> {
        Ok(self.state.read().await.clone())
    }

    pub async fn health_check(&self) -> Result<()> {
        let state = self.state.read().await;

        if state.active_neurons == 0 {
            anyhow::bail!("No active neurons in consciousness system");
        }

        if state.population_fitness < 0.1 {
            anyhow::bail!("Population fitness critically low");
        }

        Ok(())
    }
}
