/// Progressive Hint System
/// Provides increasingly specific hints with cost/penalty

use alloc::vec::Vec;
use alloc::collections::BTreeMap;

pub struct HintSystem {
    hint_costs: BTreeMap<u64, Vec<u32>>, // challenge_id -> hint costs
    hints_used: BTreeMap<(u64, u64), Vec<usize>>, // (team_id, challenge_id) -> hint indices used
}

impl HintSystem {
    pub fn new() -> Self {
        Self {
            hint_costs: BTreeMap::new(),
            hints_used: BTreeMap::new(),
        }
    }

    /// Get hint cost (increases progressively)
    pub fn get_hint_cost(&self, hint_number: usize) -> u32 {
        match hint_number {
            0 => 10,  // First hint: 10 points
            1 => 25,  // Second hint: 25 points
            2 => 50,  // Third hint: 50 points
            _ => 100, // Further hints: 100 points each
        }
    }

    /// Request hint (returns hint and deducts points)
    pub fn request_hint(
        &mut self,
        team_id: u64,
        challenge_id: u64,
        hint_index: usize,
    ) -> Result<u32, &'static str> {
        let key = (team_id, challenge_id);

        // Check if hint already used
        let used_hints = self.hints_used.entry(key).or_insert_with(Vec::new);

        if used_hints.contains(&hint_index) {
            return Err("Hint already used");
        }

        // Record hint usage
        used_hints.push(hint_index);

        // Return cost
        Ok(self.get_hint_cost(hint_index))
    }

    /// Check if hint is already used
    pub fn is_hint_used(&self, team_id: u64, challenge_id: u64, hint_index: usize) -> bool {
        if let Some(used) = self.hints_used.get(&(team_id, challenge_id)) {
            used.contains(&hint_index)
        } else {
            false
        }
    }

    /// Get all hints used by team for challenge
    pub fn get_hints_used(&self, team_id: u64, challenge_id: u64) -> Vec<usize> {
        self.hints_used.get(&(team_id, challenge_id))
            .cloned()
            .unwrap_or_default()
    }

    /// Calculate total penalty for hints used
    pub fn calculate_hint_penalty(&self, team_id: u64, challenge_id: u64) -> u32 {
        let hints_used = self.get_hints_used(team_id, challenge_id);

        hints_used.iter()
            .map(|&idx| self.get_hint_cost(idx))
            .sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hint_costs() {
        let system = HintSystem::new();

        assert_eq!(system.get_hint_cost(0), 10);
        assert_eq!(system.get_hint_cost(1), 25);
        assert_eq!(system.get_hint_cost(2), 50);
        assert_eq!(system.get_hint_cost(3), 100);
    }

    #[test]
    fn test_hint_request() {
        let mut system = HintSystem::new();

        let cost = system.request_hint(1, 1, 0);
        assert!(cost.is_ok());
        assert_eq!(cost.unwrap(), 10);

        // Should fail on duplicate
        let cost2 = system.request_hint(1, 1, 0);
        assert!(cost2.is_err());
    }

    #[test]
    fn test_hint_penalty() {
        let mut system = HintSystem::new();

        system.request_hint(1, 1, 0).unwrap();
        system.request_hint(1, 1, 1).unwrap();

        let penalty = system.calculate_hint_penalty(1, 1);
        assert_eq!(penalty, 35); // 10 + 25
    }
}
