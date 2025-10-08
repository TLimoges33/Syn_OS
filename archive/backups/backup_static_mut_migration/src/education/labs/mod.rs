/// Interactive Educational Labs Platform for SynOS
/// Provides hands-on cybersecurity training with AI guidance

pub mod sandbox;
pub mod scenarios;
pub mod progress_tracker;
pub mod ai_tutor;
pub mod vulnerable_apps;

use alloc::vec::Vec;
use alloc::collections::BTreeMap;
use alloc::string::String;

/// Lab difficulty levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum DifficultyLevel {
    Beginner = 1,
    Intermediate = 2,
    Advanced = 3,
    Expert = 4,
    Master = 5,
}

/// Lab categories
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LabCategory {
    WebSecurity,
    NetworkSecurity,
    CryptoAnalysis,
    ReverseEngineering,
    BinaryExploitation,
    PrivilegeEscalation,
    ForensicsAnalysis,
    MalwareAnalysis,
}

/// Lab status
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LabStatus {
    NotStarted,
    InProgress,
    Completed,
    Failed,
}

/// Educational lab
#[derive(Debug, Clone)]
pub struct EducationalLab {
    pub lab_id: u64,
    pub name: String,
    pub description: String,
    pub category: LabCategory,
    pub difficulty: DifficultyLevel,
    pub estimated_time_mins: u32,
    pub learning_objectives: Vec<String>,
    pub prerequisites: Vec<u64>, // Lab IDs
    pub hints_available: u32,
    pub points: u32,
}

/// Student progress
#[derive(Debug, Clone)]
pub struct StudentProgress {
    pub student_id: u64,
    pub labs_completed: Vec<u64>,
    pub labs_in_progress: Vec<u64>,
    pub total_points: u32,
    pub current_level: DifficultyLevel,
    pub hints_used: u32,
    pub achievements: Vec<Achievement>,
}

/// Achievement
#[derive(Debug, Clone)]
pub struct Achievement {
    pub achievement_id: u32,
    pub name: String,
    pub description: String,
    pub earned_timestamp: u64,
}

/// Interactive Educational Labs Manager
pub struct EducationalLabsManager {
    labs: BTreeMap<u64, EducationalLab>,
    student_progress: BTreeMap<u64, StudentProgress>,
    sandbox_manager: sandbox::SandboxManager,
    scenario_engine: scenarios::ScenarioEngine,
    progress_tracker: progress_tracker::ProgressTracker,
    ai_tutor: ai_tutor::AiTutor,
    next_lab_id: u64,
}

impl EducationalLabsManager {
    /// Create new educational labs manager
    pub fn new() -> Self {
        let mut manager = Self {
            labs: BTreeMap::new(),
            student_progress: BTreeMap::new(),
            sandbox_manager: sandbox::SandboxManager::new(),
            scenario_engine: scenarios::ScenarioEngine::new(),
            progress_tracker: progress_tracker::ProgressTracker::new(),
            ai_tutor: ai_tutor::AiTutor::new(),
            next_lab_id: 1,
        };

        // Load default labs
        manager.load_default_labs();

        manager
    }

    /// Load default educational labs
    fn load_default_labs(&mut self) {
        // Web Security Lab
        self.create_lab(
            "SQL Injection Fundamentals",
            "Learn to identify and exploit SQL injection vulnerabilities",
            LabCategory::WebSecurity,
            DifficultyLevel::Beginner,
            30,
            vec![
                "Understand SQL injection mechanisms".into(),
                "Identify vulnerable endpoints".into(),
                "Extract database contents".into(),
            ],
            vec![],
            3,
            100,
        );

        // Network Security Lab
        self.create_lab(
            "Network Traffic Analysis",
            "Analyze network packets to identify malicious activity",
            LabCategory::NetworkSecurity,
            DifficultyLevel::Intermediate,
            45,
            vec![
                "Use packet capture tools".into(),
                "Identify attack signatures".into(),
                "Extract indicators of compromise".into(),
            ],
            vec![],
            5,
            200,
        );

        // Binary Exploitation Lab
        self.create_lab(
            "Buffer Overflow Exploitation",
            "Exploit buffer overflow vulnerabilities to gain control",
            LabCategory::BinaryExploitation,
            DifficultyLevel::Advanced,
            60,
            vec![
                "Understand stack layout".into(),
                "Control return addresses".into(),
                "Bypass basic protections".into(),
            ],
            vec![1], // Requires first lab
            7,
            300,
        );

        // Cryptography Lab
        self.create_lab(
            "RSA Key Cracking",
            "Crack weak RSA implementations using mathematical attacks",
            LabCategory::CryptoAnalysis,
            DifficultyLevel::Expert,
            90,
            vec![
                "Understand RSA mathematics".into(),
                "Implement factorization attacks".into(),
                "Recover private keys".into(),
            ],
            vec![1, 2],
            10,
            500,
        );
    }

    /// Create a new lab
    fn create_lab(
        &mut self,
        name: &str,
        description: &str,
        category: LabCategory,
        difficulty: DifficultyLevel,
        estimated_time_mins: u32,
        learning_objectives: Vec<String>,
        prerequisites: Vec<u64>,
        hints_available: u32,
        points: u32,
    ) -> u64 {
        let lab_id = self.next_lab_id;
        self.next_lab_id += 1;

        let lab = EducationalLab {
            lab_id,
            name: name.into(),
            description: description.into(),
            category,
            difficulty,
            estimated_time_mins,
            learning_objectives,
            prerequisites,
            hints_available,
            points,
        };

        self.labs.insert(lab_id, lab);
        lab_id
    }

    /// Start a lab for student
    pub fn start_lab(&mut self, student_id: u64, lab_id: u64) -> Result<(), &'static str> {
        // Verify lab exists
        let lab = self.labs.get(&lab_id)
            .ok_or("Lab not found")?;

        // Get or create student progress
        let progress = self.student_progress.entry(student_id)
            .or_insert_with(|| StudentProgress {
                student_id,
                labs_completed: Vec::new(),
                labs_in_progress: Vec::new(),
                total_points: 0,
                current_level: DifficultyLevel::Beginner,
                hints_used: 0,
                achievements: Vec::new(),
            });

        // Check prerequisites
        for prereq in &lab.prerequisites {
            if !progress.labs_completed.contains(prereq) {
                return Err("Prerequisites not met");
            }
        }

        // Add to in-progress labs
        if !progress.labs_in_progress.contains(&lab_id) {
            progress.labs_in_progress.push(lab_id);
        }

        // Create sandbox environment
        self.sandbox_manager.create_sandbox(student_id, lab_id)?;

        // Initialize scenario
        self.scenario_engine.initialize_scenario(lab_id)?;

        Ok(())
    }

    /// Complete a lab
    pub fn complete_lab(&mut self, student_id: u64, lab_id: u64) -> Result<(), &'static str> {
        let lab_points = {
            let lab = self.labs.get(&lab_id)
                .ok_or("Lab not found")?;
            lab.points
        };

        let progress = self.student_progress.get_mut(&student_id)
            .ok_or("Student not found")?;

        // Remove from in-progress
        progress.labs_in_progress.retain(|id| *id != lab_id);

        // Add to completed
        if !progress.labs_completed.contains(&lab_id) {
            progress.labs_completed.push(lab_id);
            progress.total_points += lab_points;

            // Update level based on points (inline)
            progress.current_level = match progress.total_points {
                0..=299 => DifficultyLevel::Beginner,
                300..=799 => DifficultyLevel::Intermediate,
                800..=1499 => DifficultyLevel::Advanced,
                1500..=2499 => DifficultyLevel::Expert,
                _ => DifficultyLevel::Master,
            };

            // Check for achievements (fully inlined)
            // First lab completed
            if progress.labs_completed.len() == 1 {
                progress.achievements.push(Achievement {
                    achievement_id: 1,
                    name: "First Steps".into(),
                    description: "Complete your first lab".into(),
                    earned_timestamp: 0,
                });
            }

            // 10 labs completed
            if progress.labs_completed.len() == 10 {
                progress.achievements.push(Achievement {
                    achievement_id: 2,
                    name: "Dedicated Learner".into(),
                    description: "Complete 10 labs".into(),
                    earned_timestamp: 0,
                });
            }

            // No hints used for 5 labs
            let recent_no_hints = progress.labs_completed.len() >= 5 && progress.hints_used == 0;
            if recent_no_hints {
                progress.achievements.push(Achievement {
                    achievement_id: 3,
                    name: "Self-Taught".into(),
                    description: "Complete 5 labs without hints".into(),
                    earned_timestamp: 0,
                });
            }
        }

        // Clean up sandbox
        self.sandbox_manager.destroy_sandbox(student_id, lab_id)?;

        Ok(())
    }

    /// Get hint for lab
    pub fn get_hint(&mut self, student_id: u64, lab_id: u64, hint_number: u32) -> Result<String, &'static str> {
        let lab = self.labs.get(&lab_id)
            .ok_or("Lab not found")?;

        if hint_number > lab.hints_available {
            return Err("No more hints available");
        }

        let progress = self.student_progress.get_mut(&student_id)
            .ok_or("Student not found")?;

        progress.hints_used += 1;

        // Use AI tutor to generate contextual hint
        self.ai_tutor.generate_hint(lab_id, hint_number)
    }

    /// Get student progress report
    pub fn get_progress(&self, student_id: u64) -> Option<&StudentProgress> {
        self.student_progress.get(&student_id)
    }

    /// Get available labs for student
    pub fn get_available_labs(&self, student_id: u64) -> Vec<&EducationalLab> {
        let progress = match self.student_progress.get(&student_id) {
            Some(p) => p,
            None => return self.labs.values().collect(),
        };

        self.labs.values()
            .filter(|lab| {
                // Check if prerequisites are met
                lab.prerequisites.iter()
                    .all(|prereq| progress.labs_completed.contains(prereq))
            })
            .collect()
    }

    /// Get labs by category
    pub fn get_labs_by_category(&self, category: LabCategory) -> Vec<&EducationalLab> {
        self.labs.values()
            .filter(|lab| lab.category == category)
            .collect()
    }

    /// Get statistics
    pub fn get_statistics(&self) -> LabStatistics {
        LabStatistics {
            total_labs: self.labs.len(),
            total_students: self.student_progress.len(),
            total_completions: self.student_progress.values()
                .map(|p| p.labs_completed.len())
                .sum(),
            active_sandboxes: self.sandbox_manager.active_count(),
        }
    }
}

/// Lab platform statistics
#[derive(Debug, Clone)]
pub struct LabStatistics {
    pub total_labs: usize,
    pub total_students: usize,
    pub total_completions: usize,
    pub active_sandboxes: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lab_creation() {
        let manager = EducationalLabsManager::new();
        assert!(manager.labs.len() >= 4); // At least default labs
    }

    #[test]
    fn test_student_progress() {
        let mut manager = EducationalLabsManager::new();

        let student_id = 1;
        let lab_id = 1;

        assert!(manager.start_lab(student_id, lab_id).is_ok());
        assert!(manager.complete_lab(student_id, lab_id).is_ok());

        let progress = manager.get_progress(student_id).unwrap();
        assert_eq!(progress.labs_completed.len(), 1);
    }

    #[test]
    fn test_prerequisites() {
        let mut manager = EducationalLabsManager::new();

        let student_id = 1;
        let lab_with_prereqs = 3; // Buffer overflow lab requires lab 1

        // Should fail without prerequisites
        assert!(manager.start_lab(student_id, lab_with_prereqs).is_err());

        // Complete prerequisite
        manager.start_lab(student_id, 1).unwrap();
        manager.complete_lab(student_id, 1).unwrap();

        // Should now succeed
        assert!(manager.start_lab(student_id, lab_with_prereqs).is_ok());
    }

    #[test]
    fn test_hint_system() {
        let mut manager = EducationalLabsManager::new();

        let student_id = 1;
        let lab_id = 1;

        manager.start_lab(student_id, lab_id).unwrap();

        let hint = manager.get_hint(student_id, lab_id, 1);
        assert!(hint.is_ok());
    }

    #[test]
    fn test_achievements() {
        let mut manager = EducationalLabsManager::new();

        let student_id = 1;

        // Complete first lab
        manager.start_lab(student_id, 1).unwrap();
        manager.complete_lab(student_id, 1).unwrap();

        let progress = manager.get_progress(student_id).unwrap();
        assert!(progress.achievements.len() > 0);
    }
}
