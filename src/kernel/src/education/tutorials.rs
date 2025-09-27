//! Tutorial System
//!
//! Manages interactive tutorials for learning system operations.

use alloc::vec::Vec;
use alloc::string::String;
use alloc::collections::BTreeMap;
use core::sync::atomic::{AtomicU32, Ordering};
use crate::education::{ContentType, EducationLevel};

/// Global tutorial ID counter
static TUTORIAL_ID_COUNTER: AtomicU32 = AtomicU32::new(0);

/// Tutorial manager
#[derive(Debug)]
pub struct TutorialManager {
    tutorials: BTreeMap<u32, Tutorial>,
    active_tutorials: BTreeMap<u32, TutorialSession>,
    initialized: bool,
}

/// Individual tutorial
#[derive(Debug, Clone)]
pub struct Tutorial {
    pub id: u32,
    pub title: String,
    pub description: String,
    pub content_type: ContentType,
    pub difficulty: EducationLevel,
    pub steps: Vec<TutorialStep>,
    pub estimated_time: u32, // in minutes
}

/// Tutorial step
#[derive(Debug, Clone)]
pub struct TutorialStep {
    pub step_id: u32,
    pub title: String,
    pub description: String,
    pub instruction: String,
    pub expected_action: ExpectedAction,
    pub hint: Option<String>,
}

/// Expected action from user
#[derive(Debug, Clone, PartialEq)]
pub enum ExpectedAction {
    ReadAndContinue,
    ExecuteCommand(String),
    SelectOption(Vec<String>),
    EnterText(String),
    ObserveOutput,
    CompleteTask(String),
}

/// Active tutorial session
#[derive(Debug)]
pub struct TutorialSession {
    pub session_id: u32,
    pub tutorial_id: u32,
    pub current_step: u32,
    pub completed_steps: Vec<u32>,
    pub started_at: u64,
    pub progress: f32,
}

impl TutorialManager {
    /// Create new tutorial manager
    pub fn new() -> Self {
        Self {
            tutorials: BTreeMap::new(),
            active_tutorials: BTreeMap::new(),
            initialized: false,
        }
    }
    
    /// Initialize tutorial manager
    pub async fn initialize(&mut self) -> Result<(), &'static str> {
        if self.initialized {
            return Err("Tutorial manager already initialized");
        }
        
        // Load default tutorials
        self.load_default_tutorials().await?;
        
        self.initialized = true;
        Ok(())
    }
    
    /// Shutdown tutorial manager
    pub async fn shutdown(&mut self) -> Result<(), &'static str> {
        // End all active tutorials
        for (_, session) in self.active_tutorials.drain() {
            // Sessions automatically end when dropped
        }
        
        self.initialized = false;
        Ok(())
    }
    
    /// Start a tutorial
    pub async fn start_tutorial(&mut self, content_type: ContentType) -> Result<u32, &'static str> {
        if !self.initialized {
            return Err("Tutorial manager not initialized");
        }
        
        // Find tutorial for content type
        let tutorial_id = self.find_tutorial_for_content(&content_type)?;
        let session_id = TUTORIAL_ID_COUNTER.fetch_add(1, Ordering::AcqRel);
        
        let session = TutorialSession {
            session_id,
            tutorial_id,
            current_step: 0,
            completed_steps: Vec::new(),
            started_at: 0, // TODO: Get actual timestamp
            progress: 0.0,
        };
        
        self.active_tutorials.insert(session_id, session);
        Ok(session_id)
    }
    
    /// Get tutorial step
    pub fn get_current_step(&self, session_id: u32) -> Result<TutorialStep, &'static str> {
        let session = self.active_tutorials.get(&session_id)
            .ok_or("Tutorial session not found")?;
        
        let tutorial = self.tutorials.get(&session.tutorial_id)
            .ok_or("Tutorial not found")?;
        
        if let Some(step) = tutorial.steps.get(session.current_step as usize) {
            Ok(step.clone())
        } else {
            Err("Tutorial step not found")
        }
    }
    
    /// Advance to next step
    pub async fn next_step(&mut self, session_id: u32) -> Result<bool, &'static str> {
        let session = self.active_tutorials.get_mut(&session_id)
            .ok_or("Tutorial session not found")?;
        
        let tutorial = self.tutorials.get(&session.tutorial_id)
            .ok_or("Tutorial not found")?;
        
        // Mark current step as completed
        session.completed_steps.push(session.current_step);
        session.current_step += 1;
        
        // Update progress
        session.progress = session.completed_steps.len() as f32 / tutorial.steps.len() as f32;
        
        // Check if tutorial is complete
        Ok(session.current_step < tutorial.steps.len() as u32)
    }
    
    /// Complete tutorial
    pub async fn complete_tutorial(&mut self, session_id: u32) -> Result<(), &'static str> {
        if let Some(session) = self.active_tutorials.remove(&session_id) {
            // Award completion achievement
            // Update user progress
            Ok(())
        } else {
            Err("Tutorial session not found")
        }
    }
    
    /// List available tutorials
    pub fn list_tutorials(&self) -> Vec<(u32, String, ContentType)> {
        self.tutorials.iter()
            .map(|(id, tutorial)| (*id, tutorial.title.clone(), tutorial.content_type.clone()))
            .collect()
    }
    
    /// Get tutorial count
    pub fn get_tutorial_count(&self) -> usize {
        self.tutorials.len()
    }
    
    /// Get active session count
    pub fn get_active_session_count(&self) -> usize {
        self.active_tutorials.len()
    }
    
    // Private helper methods
    
    async fn load_default_tutorials(&mut self) -> Result<(), &'static str> {
        // Load system overview tutorial
        let system_tutorial = Tutorial {
            id: TUTORIAL_ID_COUNTER.fetch_add(1, Ordering::AcqRel),
            title: String::from("System Overview"),
            description: String::from("Learn about SynOS system architecture and AI consciousness"),
            content_type: ContentType::SystemOverview,
            difficulty: EducationLevel::Beginner,
            steps: vec![
                TutorialStep {
                    step_id: 1,
                    title: String::from("Welcome to SynOS"),
                    description: String::from("Introduction to the consciousness-aware operating system"),
                    instruction: String::from("Read about SynOS features and continue"),
                    expected_action: ExpectedAction::ReadAndContinue,
                    hint: Some(String::from("Take your time to understand the concepts")),
                },
                TutorialStep {
                    step_id: 2,
                    title: String::from("AI Consciousness System"),
                    description: String::from("Understanding the AI consciousness integration"),
                    instruction: String::from("Learn how AI consciousness enhances system operations"),
                    expected_action: ExpectedAction::ReadAndContinue,
                    hint: Some(String::from("The AI system learns and adapts to your usage patterns")),
                },
            ],
            estimated_time: 15,
        };
        
        // Load kernel basics tutorial
        let kernel_tutorial = Tutorial {
            id: TUTORIAL_ID_COUNTER.fetch_add(1, Ordering::AcqRel),
            title: String::from("Kernel Basics"),
            description: String::from("Understanding the SynOS kernel architecture"),
            content_type: ContentType::KernelBasics,
            difficulty: EducationLevel::Intermediate,
            steps: vec![
                TutorialStep {
                    step_id: 1,
                    title: String::from("Kernel Architecture"),
                    description: String::from("Overview of kernel components and modules"),
                    instruction: String::from("Explore the modular kernel design"),
                    expected_action: ExpectedAction::ReadAndContinue,
                    hint: Some(String::from("Note how modules interact with each other")),
                },
            ],
            estimated_time: 30,
        };
        
        // Add tutorials to collection
        self.tutorials.insert(system_tutorial.id, system_tutorial);
        self.tutorials.insert(kernel_tutorial.id, kernel_tutorial);
        
        Ok(())
    }
    
    fn find_tutorial_for_content(&self, content_type: &ContentType) -> Result<u32, &'static str> {
        for (id, tutorial) in &self.tutorials {
            if tutorial.content_type == *content_type {
                return Ok(*id);
            }
        }
        Err("No tutorial found for content type")
    }
}
