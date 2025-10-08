use anyhow::Result;
use rand::Rng;
use tracing::{debug, info};

pub struct NeuralDarwinismEngine {
    population_size: usize,
    mutation_rate: f64,
    selection_pressure: f64,
    generation: u64,
    population: Vec<NeuralAgent>,
}

#[derive(Clone)]
struct NeuralAgent {
    weights: Vec<f64>,
    fitness: f64,
}

impl NeuralDarwinismEngine {
    pub fn new(population_size: usize, mutation_rate: f64, selection_pressure: f64) -> Result<Self> {
        info!("Initializing Neural Darwinism engine with population size: {}", population_size);

        let mut rng = rand::thread_rng();
        let population: Vec<NeuralAgent> = (0..population_size)
            .map(|_| NeuralAgent {
                weights: (0..100).map(|_| rng.gen_range(-1.0..1.0)).collect(),
                fitness: 0.0,
            })
            .collect();

        Ok(Self {
            population_size,
            mutation_rate,
            selection_pressure,
            generation: 0,
            population,
        })
    }

    pub async fn evolve_population(&mut self) -> Result<()> {
        // Evaluate fitness
        let fitnesses: Vec<f64> = self.population
            .iter()
            .map(|agent| self.calculate_fitness(&agent.weights))
            .collect();

        for (agent, fitness) in self.population.iter_mut().zip(fitnesses.iter()) {
            agent.fitness = *fitness;
        }

        // Sort by fitness
        self.population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

        // Selection and reproduction
        let elite_count = (self.population_size as f64 * self.selection_pressure) as usize;
        let elite = self.population[..elite_count].to_vec();

        // Create new generation
        let mut new_population = elite.clone();
        let mut rng = rand::thread_rng();

        while new_population.len() < self.population_size {
            let parent1 = &elite[rng.gen_range(0..elite.len())];
            let parent2 = &elite[rng.gen_range(0..elite.len())];

            let mut child = self.crossover(parent1, parent2);
            self.mutate(&mut child);

            new_population.push(child);
        }

        self.population = new_population;
        self.generation += 1;

        if self.generation % 100 == 0 {
            debug!("Generation {}: Best fitness = {:.4}", self.generation, self.population[0].fitness);
        }

        Ok(())
    }

    fn calculate_fitness(&self, weights: &[f64]) -> f64 {
        // Simple fitness function - maximize sum of positive weights
        weights.iter().filter(|&&w| w > 0.0).sum::<f64>() / weights.len() as f64
    }

    fn crossover(&self, parent1: &NeuralAgent, parent2: &NeuralAgent) -> NeuralAgent {
        let mut rng = rand::thread_rng();
        let crossover_point = rng.gen_range(0..parent1.weights.len());

        let mut weights = parent1.weights[..crossover_point].to_vec();
        weights.extend_from_slice(&parent2.weights[crossover_point..]);

        NeuralAgent { weights, fitness: 0.0 }
    }

    fn mutate(&self, agent: &mut NeuralAgent) {
        let mut rng = rand::thread_rng();
        for weight in &mut agent.weights {
            if rng.gen::<f64>() < self.mutation_rate {
                *weight += rng.gen_range(-0.1..0.1);
                *weight = weight.clamp(-1.0, 1.0);
            }
        }
    }

    pub fn get_generation(&self) -> u64 {
        self.generation
    }

    pub fn get_best_fitness(&self) -> f64 {
        self.population.first().map(|a| a.fitness).unwrap_or(0.0)
    }
}
