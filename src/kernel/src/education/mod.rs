//! Education Module
//!
//! Provides educational features, tutorials, and interactive learning
//! for users to understand system operations and AI consciousness.

use alloc::vec::Vec;
use alloc::string::String;
use alloc::collections::BTreeMap;
use core::sync::atomic::{AtomicU32, Ordering};

/// Education module components
pub mod tutorials;
pub mod interactive;
pub mod documentation;
pub mod assessments;

// Phase 5c: Interactive Educational Labs Platform
pub mod labs;

// Phase 6b: CTF Auto-Generation Engine
pub mod ctf;

// Newly organized modules
pub mod hud_tutorial_engine;
pub mod hud_command_interface;
pub mod cybersecurity_tutorial_content;
pub mod platform_minimal;
pub mod advanced_applications_minimal;

// Re-export key types
pub use tutorials::{Tutorial, TutorialManager};
pub use interactive::{InteractiveSession, InteractiveMode};
pub use documentation::{DocumentationSystem, HelpSystem};
pub use labs::{EducationalLabsManager, DifficultyLevel};

/// Global tutorial counter
static TUTORIAL_COUNTER: AtomicU32 = AtomicU32::new(0);

/// Education system manager
#[derive(Debug)]
pub struct EducationSystem {
    tutorials: TutorialManager,
    interactive_sessions: BTreeMap<u32, InteractiveSession>,
    documentation: DocumentationSystem,
    enabled: bool,
}

/// Education configuration
#[derive(Debug, Clone)]
pub struct EducationConfig {
    pub enable_tutorials: bool,
    pub enable_interactive_mode: bool,
    pub enable_assessments: bool,
    pub enable_documentation: bool,
    pub education_level: EducationLevel,
    pub language: String,
}

/// Education levels
#[derive(Debug, Clone, PartialEq)]
pub enum EducationLevel {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
}

/// Educational content types
#[derive(Debug, Clone, PartialEq)]
pub enum ContentType {
    SystemOverview,
    KernelBasics,
    AIConsciousness,
    SecurityConcepts,
    ProcessManagement,
    MemoryManagement,
    NetworkingBasics,
    Troubleshooting,
}

/// Learning progress
#[derive(Debug, Clone)]
pub struct LearningProgress {
    pub user_id: u32,
    pub completed_tutorials: Vec<u32>,
    pub current_level: EducationLevel,
    pub progress_score: f32,
    pub achievements: Vec<Achievement>,
}

/// Learning achievement
#[derive(Debug, Clone)]
pub struct Achievement {
    pub achievement_id: u32,
    pub name: String,
    pub description: String,
    pub earned_at: u64,
    pub points: u32,
}

impl Default for EducationConfig {
    fn default() -> Self {
        Self {
            enable_tutorials: true,
            enable_interactive_mode: true,
            enable_assessments: true,
            enable_documentation: true,
            education_level: EducationLevel::Beginner,
            language: String::from("en"),
        }
    }
}

impl EducationSystem {
    /// Create new education system
    pub fn new() -> Self {
        Self {
            tutorials: TutorialManager::new(),
            interactive_sessions: BTreeMap::new(),
            documentation: DocumentationSystem::new(),
            enabled: false,
        }
    }
    
    /// Initialize education system
    pub async fn initialize(&mut self, config: EducationConfig) -> Result<(), &'static str> {
        if self.enabled {
            return Err("Education system already initialized");
        }
        
        // Initialize tutorials
        if config.enable_tutorials {
            self.tutorials.initialize().await?;
        }
        
        // Initialize documentation system
        if config.enable_documentation {
            self.documentation.initialize().await?;
        }
        
        self.enabled = true;
        Ok(())
    }
    
    /// Shutdown education system
    pub async fn shutdown(&mut self) -> Result<(), &'static str> {
        if !self.enabled {
            return Ok(());
        }
        
        // Shutdown all interactive sessions
        let session_keys: Vec<_> = self.interactive_sessions.keys().cloned().collect();
        for key in session_keys {
            if let Some(mut session) = self.interactive_sessions.remove(&key) {
                session.end().await?;
            }
        }
        
        // Shutdown components
        self.tutorials.shutdown().await?;
        self.documentation.shutdown().await?;
        
        self.enabled = false;
        Ok(())
    }
    
    /// Start tutorial session
    pub async fn start_tutorial(&mut self, content_type: ContentType) -> Result<u32, &'static str> {
        if !self.enabled {
            return Err("Education system not enabled");
        }
        
        self.tutorials.start_tutorial(content_type).await
    }
    
    /// Start interactive session
    pub async fn start_interactive_session(&mut self, mode: InteractiveMode) -> Result<u32, &'static str> {
        if !self.enabled {
            return Err("Education system not enabled");
        }
        
        let session_id = TUTORIAL_COUNTER.fetch_add(1, Ordering::AcqRel);
        let session = InteractiveSession::new(session_id, mode);
        
        self.interactive_sessions.insert(session_id, session);
        Ok(session_id)
    }
    
    /// Get tutorial list
    pub fn get_available_tutorials(&self) -> Vec<(u32, String, ContentType)> {
        self.tutorials.list_tutorials()
    }
    
    /// Get help for topic
    pub async fn get_help(&self, topic: &str) -> Result<String, &'static str> {
        if !self.enabled {
            return Err("Education system not enabled");
        }
        
        self.documentation.get_help(topic).await
    }
    
    /// Search documentation
    pub async fn search_documentation(&self, query: &str) -> Result<Vec<String>, &'static str> {
        if !self.enabled {
            return Err("Education system not enabled");
        }
        
        self.documentation.search(query).await
    }
    
    /// Get learning progress
    pub fn get_progress(&self, user_id: u32) -> Option<LearningProgress> {
        // Simplified progress tracking
        // In a real implementation, this would be stored persistently
        Some(LearningProgress {
            user_id,
            completed_tutorials: Vec::new(),
            current_level: EducationLevel::Beginner,
            progress_score: 0.0,
            achievements: Vec::new(),
        })
    }
    
    /// Update learning progress
    pub async fn update_progress(&mut self, _user_id: u32, _tutorial_id: u32) -> Result<(), &'static str> {
        // Update user progress after completing tutorial
        // This would typically involve updating a database or persistent storage
        Ok(())
    }
    
    /// Show system status with educational context
    pub async fn show_educational_status(&self) -> Result<String, &'static str> {
        if !self.enabled {
            return Err("Education system not enabled");
        }
        
        let tutorial_count = self.tutorials.get_tutorial_count();
        let active_sessions = self.interactive_sessions.len();
        
        Ok(format!(
            "Education System Status:\n\
            - Available Tutorials: {}\n\
            - Active Interactive Sessions: {}\n\
            - Documentation System: Active\n\
            - Help System: Available",
            tutorial_count, active_sessions
        ))
    }
    
    /// Check if education system is enabled
    pub fn is_enabled(&self) -> bool {
        self.enabled
    }
}

/// Initialize global education system
pub async fn init_education_system(config: EducationConfig) -> Result<(), &'static str> {
    let mut education_system = EducationSystem::new();
    education_system.initialize(config).await?;
    
    // Store in global state (simplified)
    // In a real implementation, this would use proper global state management
    
    Ok(())
}

/// Initialize the education platform
pub fn init_education_platform() {
    // TODO: Initialize education platform with default configuration
    let _config = EducationConfig::default();
}
