/// Dynamic Scoring Engine
/// Points decrease as more teams solve (encourages early solves)

use libm::powf;

pub struct ScoringEngine {
    decay_factor: f32,
}

impl ScoringEngine {
    pub fn new() -> Self {
        Self {
            decay_factor: 0.95, // 5% decay per solve
        }
    }

    /// Calculate base points for difficulty
    pub fn calculate_base_points(&self, difficulty: crate::education::DifficultyLevel) -> u32 {
        match difficulty {
            crate::education::DifficultyLevel::Beginner => 100,
            crate::education::DifficultyLevel::Intermediate => 250,
            crate::education::DifficultyLevel::Advanced => 500,
            crate::education::DifficultyLevel::Expert => 750,
            crate::education::DifficultyLevel::Master => 1000,
        }
    }

    /// Calculate points for solve (with dynamic decay)
    pub fn calculate_solve_points(
        &self,
        difficulty: crate::education::DifficultyLevel,
        solves: u32,
    ) -> u32 {
        let base_points = self.calculate_base_points(difficulty) as f32;

        // Apply decay based on number of solves
        let decay_multiplier = powf(self.decay_factor, solves as f32);
        let final_points = (base_points * decay_multiplier).max(50.0); // Minimum 50 points

        final_points as u32
    }

    /// Calculate first blood bonus
    pub fn first_blood_bonus(&self, base_points: u32) -> u32 {
        (base_points as f32 * 0.2) as u32 // 20% bonus
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_base_points() {
        let engine = ScoringEngine::new();

        assert_eq!(engine.calculate_base_points(crate::education::DifficultyLevel::Beginner), 100);
        assert_eq!(engine.calculate_base_points(crate::education::DifficultyLevel::Master), 1000);
    }

    #[test]
    fn test_dynamic_scoring() {
        let engine = ScoringEngine::new();

        let points_0_solves = engine.calculate_solve_points(
            crate::education::DifficultyLevel::Intermediate,
            0,
        );

        let points_5_solves = engine.calculate_solve_points(
            crate::education::DifficultyLevel::Intermediate,
            5,
        );

        // Points should decrease with more solves
        assert!(points_0_solves > points_5_solves);
    }

    #[test]
    fn test_minimum_points() {
        let engine = ScoringEngine::new();

        // Even with many solves, should not go below minimum
        let points = engine.calculate_solve_points(
            crate::education::DifficultyLevel::Beginner,
            100,
        );

        assert!(points >= 50);
    }
}
