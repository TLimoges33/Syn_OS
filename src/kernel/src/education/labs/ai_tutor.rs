/// AI Tutor for Personalized Learning Guidance
/// Provides contextual hints and adaptive learning paths

use alloc::string::String;
use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Hint level
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HintLevel {
    Nudge,      // Gentle direction
    Guidance,   // More specific guidance
    Solution,   // Near-complete solution
}

/// Learning style
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LearningStyle {
    Visual,
    Verbal,
    HandsOn,
    Theoretical,
}

/// AI Tutor
pub struct AiTutor {
    hint_database: BTreeMap<u64, Vec<String>>, // lab_id -> hints
    student_profiles: BTreeMap<u64, StudentProfile>,
}

/// Student learning profile
#[derive(Debug, Clone)]
pub struct StudentProfile {
    pub student_id: u64,
    pub learning_style: LearningStyle,
    pub preferred_hint_level: HintLevel,
    pub comprehension_rate: f32, // 0.0-1.0
}

impl AiTutor {
    pub fn new() -> Self {
        let mut tutor = Self {
            hint_database: BTreeMap::new(),
            student_profiles: BTreeMap::new(),
        };

        tutor.load_hint_database();
        tutor
    }

    /// Load hint database
    fn load_hint_database(&mut self) {
        // SQL Injection lab hints
        self.hint_database.insert(1, vec![
            "Try looking at the login form parameters".into(),
            "SQL queries can be manipulated with special characters like ' and --".into(),
            "The username field might accept SQL commands. Try: admin' --".into(),
        ]);

        // Network Analysis lab hints
        self.hint_database.insert(2, vec![
            "Use Wireshark or tcpdump to capture network traffic".into(),
            "Look for unusual patterns in HTTP requests".into(),
            "Check for base64-encoded data in packet payloads".into(),
        ]);

        // Buffer Overflow lab hints
        self.hint_database.insert(3, vec![
            "Examine the binary's stack layout with GDB".into(),
            "Calculate the offset to overwrite the return address".into(),
            "Use pattern_create and pattern_offset to find exact offset".into(),
        ]);

        // RSA Cracking lab hints
        self.hint_database.insert(4, vec![
            "Check if the RSA modulus is small enough to factor".into(),
            "Use online factorization databases for known weak keys".into(),
            "Apply Fermat's factorization method for close primes".into(),
        ]);
    }

    /// Generate contextual hint
    pub fn generate_hint(&mut self, lab_id: u64, hint_number: u32) -> Result<String, &'static str> {
        let hints = self.hint_database.get(&lab_id)
            .ok_or("No hints available for this lab")?;

        let index = (hint_number as usize).saturating_sub(1);
        if index >= hints.len() {
            return Err("No more hints available");
        }

        Ok(hints[index].clone())
    }

    /// Analyze student performance and suggest next steps
    pub fn suggest_next_lab(&self, student_id: u64, completed_labs: &[u64], current_level: super::DifficultyLevel) -> String {
        // Get student profile
        let _profile = self.student_profiles.get(&student_id);

        // AI would analyze:
        // 1. Completion patterns
        // 2. Time spent per lab
        // 3. Hint usage frequency
        // 4. Success/failure rate

        // Simplified recommendation
        if completed_labs.len() < 3 {
            "Continue with beginner labs to build fundamentals".into()
        } else if current_level == super::DifficultyLevel::Beginner {
            "You're ready for intermediate challenges!".into()
        } else {
            "Try advanced labs to push your skills further".into()
        }
    }

    /// Provide personalized encouragement
    pub fn generate_encouragement(&self, progress: &super::StudentProgress) -> String {
        match progress.labs_completed.len() {
            0 => "Welcome! Every expert was once a beginner. Let's start learning!".into(),
            1..=2 => "Great start! You're building solid foundations.".into(),
            3..=5 => "You're making excellent progress! Keep up the momentum.".into(),
            6..=10 => "Impressive dedication! You're well on your way to mastery.".into(),
            _ => "Outstanding achievement! You're becoming an expert.".into(),
        }
    }

    /// Create student profile
    pub fn create_profile(&mut self, student_id: u64, learning_style: LearningStyle) {
        let profile = StudentProfile {
            student_id,
            learning_style,
            preferred_hint_level: HintLevel::Guidance,
            comprehension_rate: 0.5,
        };

        self.student_profiles.insert(student_id, profile);
    }

    /// Update comprehension rate based on performance
    pub fn update_comprehension(&mut self, student_id: u64, success: bool) {
        if let Some(profile) = self.student_profiles.get_mut(&student_id) {
            // Adaptive learning: adjust comprehension rate
            if success {
                profile.comprehension_rate = (profile.comprehension_rate + 0.05).min(1.0);
            } else {
                profile.comprehension_rate = (profile.comprehension_rate - 0.02).max(0.0);
            }
        }
    }

    /// Get adaptive hint based on student profile
    pub fn get_adaptive_hint(&self, student_id: u64, lab_id: u64, hint_number: u32) -> Result<String, &'static str> {
        let profile = self.student_profiles.get(&student_id);

        let hints = self.hint_database.get(&lab_id)
            .ok_or("No hints available")?;

        let index = (hint_number as usize).saturating_sub(1);
        if index >= hints.len() {
            return Err("No more hints available");
        }

        let mut hint = hints[index].clone();

        // Adapt hint based on learning style
        if let Some(p) = profile {
            match p.learning_style {
                LearningStyle::Visual => {
                    hint.push_str(" [Visual: Check diagrams in documentation]");
                }
                LearningStyle::HandsOn => {
                    hint.push_str(" [Try it: Experiment in the sandbox]");
                }
                LearningStyle::Theoretical => {
                    hint.push_str(" [Theory: Read about the underlying concepts]");
                }
                LearningStyle::Verbal => {
                    hint.push_str(" [Explanation: Ask for clarification if needed]");
                }
            }
        }

        Ok(hint)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hint_generation() {
        let mut tutor = AiTutor::new();

        let hint = tutor.generate_hint(1, 1);
        assert!(hint.is_ok());
    }

    #[test]
    fn test_profile_creation() {
        let mut tutor = AiTutor::new();

        tutor.create_profile(1, LearningStyle::HandsOn);
        assert!(tutor.student_profiles.contains_key(&1));
    }

    #[test]
    fn test_comprehension_update() {
        let mut tutor = AiTutor::new();

        tutor.create_profile(1, LearningStyle::Visual);

        let initial_rate = tutor.student_profiles.get(&1).unwrap().comprehension_rate;

        tutor.update_comprehension(1, true);

        let new_rate = tutor.student_profiles.get(&1).unwrap().comprehension_rate;
        assert!(new_rate > initial_rate);
    }

    #[test]
    fn test_adaptive_hints() {
        let mut tutor = AiTutor::new();

        tutor.create_profile(1, LearningStyle::HandsOn);

        let hint = tutor.get_adaptive_hint(1, 1, 1);
        assert!(hint.is_ok());
        assert!(hint.unwrap().contains("Try it"));
    }
}
