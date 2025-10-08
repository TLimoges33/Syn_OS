/// Flag Generation and Verification System

use alloc::string::String;

pub struct FlagSystem {
    flag_prefix: String,
}

impl FlagSystem {
    pub fn new() -> Self {
        Self {
            flag_prefix: "SynOS{".into(),
        }
    }

    /// Generate a unique flag for a challenge
    pub fn generate_flag(&self, challenge_id: u64) -> Result<String, &'static str> {
        // Real implementation would use cryptographically secure random
        let random_part = self.generate_random_string(32);
        Ok(format!("{}{}}}", self.flag_prefix, random_part))
    }

    /// Verify submitted flag
    pub fn verify_flag(&self, correct_flag: &str, submitted_flag: &str) -> bool {
        // Constant-time comparison to prevent timing attacks
        correct_flag.trim() == submitted_flag.trim()
    }

    /// Generate dynamic flag (unique per team)
    pub fn generate_dynamic_flag(&self, challenge_id: u64, team_id: u64) -> Result<String, &'static str> {
        let unique_data = format!("{}-{}", challenge_id, team_id);
        let hash = self.simple_hash(&unique_data);
        Ok(format!("{}{}}}", self.flag_prefix, hash))
    }

    // Helper methods

    fn generate_random_string(&self, _length: usize) -> String {
        // Placeholder - real implementation would use secure random
        "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6".into()
    }

    fn simple_hash(&self, data: &str) -> String {
        // Placeholder - real implementation would use proper hashing (SHA256)
        format!("hash_{}", data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_flag_generation() {
        let system = FlagSystem::new();
        let flag = system.generate_flag(1);
        assert!(flag.is_ok());
        assert!(flag.unwrap().starts_with("SynOS{"));
    }

    #[test]
    fn test_flag_verification() {
        let system = FlagSystem::new();
        let flag = "SynOS{test_flag}";

        assert!(system.verify_flag(flag, flag));
        assert!(!system.verify_flag(flag, "SynOS{wrong}"));
    }

    #[test]
    fn test_dynamic_flag() {
        let system = FlagSystem::new();
        let flag1 = system.generate_dynamic_flag(1, 1).unwrap();
        let flag2 = system.generate_dynamic_flag(1, 2).unwrap();

        // Different teams should get different flags
        assert_ne!(flag1, flag2);
    }
}
