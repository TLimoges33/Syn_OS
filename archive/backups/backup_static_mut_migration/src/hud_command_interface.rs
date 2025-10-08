//! # SynOS HUD Command Interface
//!
//! Interactive command-line interface that integrates with the HUD Tutorial Engine
//! to provide guided cybersecurity learning experiences.

extern crate alloc;
use alloc::{string::String, vec::Vec, format};
use crate::hud_tutorial_engine::*;
use crate::cybersecurity_tutorial_content::*;

/// HUD Command Interface for tutorial interactions
pub struct HUDCommandInterface {
    /// Current active tutorial session
    active_session: Option<String>,
    /// Current student identifier
    current_student: Option<String>,
    /// Tutorial engine reference
    tutorial_engine: Option<HUDTutorialEngine>,
    /// Command history for context
    command_history: Vec<String>,
}

/// Available HUD commands for cybersecurity learning
#[derive(Debug, Clone)]
pub enum HUDCommand {
    /// Start a specific tutorial
    StartTutorial(String),
    /// Show available tutorials
    ListTutorials,
    /// Get current tutorial progress
    Progress,
    /// Show contextual help
    Help(Option<String>),
    /// Show current step hints
    Hint,
    /// Skip to next step (if allowed)
    Next,
    /// Go back to previous step
    Previous,
    /// Show achievement status
    Achievements,
    /// Execute system command with tutorial context
    Execute(String),
    /// Show HUD overlay settings
    HUDSettings,
    /// Toggle HUD display elements
    ToggleHUD(String),
}

/// Command execution results
#[derive(Debug, Clone)]
pub enum CommandResult {
    Success(String),
    Error(String),
    TutorialAction(TutorialResponse),
    HUDUpdate(Vec<HUDElement>),
    Achievement(Achievement),
}

impl HUDCommandInterface {
    /// Create new HUD command interface
    pub fn new() -> Self {
        Self {
            active_session: None,
            current_student: None,
            tutorial_engine: None,
            command_history: Vec::new(),
        }
    }

    /// Initialize the HUD command interface
    pub fn initialize(&mut self, student_id: &str) -> Result<(), &'static str> {
        self.current_student = Some(student_id.to_string());
        
        // Initialize tutorial engine
        let mut engine = HUDTutorialEngine::new();
        engine.initialize()?;
        
        // Load cybersecurity tutorial content
        load_all_tutorial_content(&mut engine)?;
        
        self.tutorial_engine = Some(engine);
        
        self.show_welcome_message()?;
        
        Ok(())
    }

    /// Process a command input from the user
    pub fn process_command(&mut self, input: &str) -> Result<CommandResult, &'static str> {
        // Add to command history
        self.command_history.push(input.to_string());

        // Parse the command
        let command = self.parse_command(input)?;

        // Execute the command
        match command {
            HUDCommand::StartTutorial(module_id) => self.start_tutorial(&module_id),
            HUDCommand::ListTutorials => self.list_available_tutorials(),
            HUDCommand::Progress => self.show_progress(),
            HUDCommand::Help(topic) => self.show_help(topic),
            HUDCommand::Hint => self.show_current_hint(),
            HUDCommand::Next => self.advance_tutorial(),
            HUDCommand::Previous => self.go_back_tutorial(),
            HUDCommand::Achievements => self.show_achievements(),
            HUDCommand::Execute(cmd) => self.execute_with_tutorial_context(&cmd),
            HUDCommand::HUDSettings => self.show_hud_settings(),
            HUDCommand::ToggleHUD(element) => self.toggle_hud_element(&element),
        }
    }

    /// Parse command string into HUDCommand enum
    fn parse_command(&self, input: &str) -> Result<HUDCommand, &'static str> {
        let parts: Vec<&str> = input.trim().split_whitespace().collect();
        
        if parts.is_empty() {
            return Err("Empty command");
        }

        match parts[0].to_lowercase().as_str() {
            "tutorial" | "start" => {
                if parts.len() > 1 {
                    Ok(HUDCommand::StartTutorial(parts[1..].join(" ")))
                } else {
                    Ok(HUDCommand::ListTutorials)
                }
            },
            "list" | "tutorials" => Ok(HUDCommand::ListTutorials),
            "progress" | "status" => Ok(HUDCommand::Progress),
            "help" => {
                let topic = if parts.len() > 1 { Some(parts[1..].join(" ")) } else { None };
                Ok(HUDCommand::Help(topic))
            },
            "hint" | "hints" => Ok(HUDCommand::Hint),
            "next" | "continue" => Ok(HUDCommand::Next),
            "back" | "previous" => Ok(HUDCommand::Previous),
            "achievements" | "badges" => Ok(HUDCommand::Achievements),
            "hud" => {
                if parts.len() > 1 {
                    match parts[1] {
                        "settings" => Ok(HUDCommand::HUDSettings),
                        "toggle" => {
                            if parts.len() > 2 {
                                Ok(HUDCommand::ToggleHUD(parts[2].to_string()))
                            } else {
                                Err("Specify HUD element to toggle")
                            }
                        },
                        _ => Err("Unknown HUD command")
                    }
                } else {
                    Ok(HUDCommand::HUDSettings)
                }
            },
            // Execute system commands with tutorial context
            "synos" | "hal" | "net" | "security" | "fs" => {
                Ok(HUDCommand::Execute(input.to_string()))
            },
            _ => Err("Unknown command - try 'help' for available commands"),
        }
    }

    /// Start a specific tutorial module
    fn start_tutorial(&mut self, module_id: &str) -> Result<CommandResult, &'static str> {
        let student_id = self.current_student.as_ref().ok_or("No student logged in")?;
        
        if let Some(ref mut engine) = self.tutorial_engine {
            let session_id = engine.start_tutorial(module_id, student_id)?;
            self.active_session = Some(session_id.clone());
            
            Ok(CommandResult::Success(format!(
                "🎯 Tutorial '{}' started! Session ID: {}\n\
                Use 'hint' for guidance and 'help' for assistance.",
                module_id, session_id
            )))
        } else {
            Err("Tutorial engine not initialized")
        }
    }

    /// List all available tutorials
    fn list_available_tutorials(&self) -> Result<CommandResult, &'static str> {
        let tutorials = format!(
            "📚 Available Cybersecurity Tutorials:\n\n\
            🔰 Phase 1 - Foundations:\n\
            • phase1_it_fundamentals - IT Fundamentals with SynOS (45 min)\n\
            • phase1_networking_fundamentals - Networking & OSI Model (35 min)\n\
            • phase1_security_principles - CIA Triad & Risk Management (40 min)\n\
            • phase1_os_fundamentals - Operating Systems & SynOS Architecture (50 min)\n\n\
            🛠️ Phase 2 - Core Tools (Coming Soon):\n\
            • phase2_wireshark_analysis - Network Packet Analysis\n\
            • phase2_nmap_scanning - Network Discovery & Scanning\n\
            • phase2_siem_basics - Security Information & Event Management\n\n\
            🎯 Phase 3 - Penetration Testing (Coming Soon):\n\
            • phase3_methodology - Pentest Frameworks & Planning\n\
            • phase3_reconnaissance - Information Gathering\n\
            • phase3_exploitation - Vulnerability Exploitation\n\n\
            🚀 Phase 4 - Advanced Topics (Coming Soon):\n\
            • phase4_cloud_security - Cloud Security Fundamentals\n\
            • phase4_ai_cybersecurity - AI in Cybersecurity\n\n\
            💡 Usage: 'tutorial phase1_it_fundamentals' to start a tutorial"
        );
        
        Ok(CommandResult::Success(tutorials))
    }

    /// Show current tutorial progress
    fn show_progress(&self) -> Result<CommandResult, &'static str> {
        let student_id = self.current_student.as_ref().ok_or("No student logged in")?;
        
        if let Some(ref engine) = self.tutorial_engine {
            if let Ok(progress) = engine.get_tutorial_progress(student_id) {
                let progress_text = format!(
                    "📊 Learning Progress for {}:\n\n\
                    ✅ Completed Modules: {}\n\
                    🎯 Current Module: {}\n\
                    ⭐ Total Points: {}\n\
                    🏆 Achievements: {}\n\
                    ⏱️ Time Spent: {} minutes\n\n\
                    Recent Modules:\n{}",
                    student_id,
                    progress.completed_modules.len(),
                    progress.current_module.as_deref().unwrap_or("None"),
                    progress.total_points,
                    progress.achievements.len(),
                    progress.time_spent_minutes,
                    progress.completed_modules.iter()
                        .take(5)
                        .map(|m| format!("• {}", m))
                        .collect::<Vec<_>>()
                        .join("\n")
                );
                
                Ok(CommandResult::Success(progress_text))
            } else {
                Ok(CommandResult::Success("No tutorial progress found. Start with 'tutorial phase1_it_fundamentals'!".to_string()))
            }
        } else {
            Err("Tutorial engine not initialized")
        }
    }

    /// Show contextual help
    fn show_help(&self, topic: Option<String>) -> Result<CommandResult, &'static str> {
        let help_text = match topic {
            Some(ref topic_str) => {
                match topic_str.as_str() {
                    "commands" => {
                        "🔧 Available Commands:\n\
                        • tutorial <module_id> - Start a specific tutorial\n\
                        • list - Show all available tutorials\n\
                        • progress - Show your learning progress\n\
                        • hint - Get hints for current tutorial step\n\
                        • next - Advance to next tutorial step\n\
                        • back - Go back to previous step\n\
                        • achievements - Show earned achievements\n\
                        • hud settings - Configure HUD display\n\
                        • synos <command> - Execute SynOS commands with tutorial context\n\
                        • help <topic> - Get help on specific topics".to_string()
                    },
                    "hud" => {
                        "📺 HUD (Heads-Up Display) Help:\n\
                        The HUD provides real-time tutorial guidance while you work.\n\n\
                        • Overlays show hints and instructions\n\
                        • Arrows point to relevant interface elements\n\
                        • Progress indicators track your advancement\n\
                        • Achievement notifications celebrate milestones\n\n\
                        Commands:\n\
                        • hud settings - View/change HUD configuration\n\
                        • hud toggle <element> - Show/hide HUD elements".to_string()
                    },
                    "tutorials" => {
                        "📚 Tutorial System Help:\n\
                        SynOS tutorials provide interactive, hands-on cybersecurity education.\n\n\
                        • Phase-based progression from basics to advanced topics\n\
                        • Real-time guidance with HUD overlays\n\
                        • Practical exercises using actual SynOS tools\n\
                        • Achievement system for motivation\n\
                        • Adaptive difficulty based on performance\n\n\
                        Start with Phase 1 foundations and work your way up!".to_string()
                    },
                    _ => {
                        if let Some(ref session) = self.active_session {
                            generate_adaptive_help(&topic_str, "general_help")
                        } else {
                            "Topic not found. Try 'help commands', 'help hud', or 'help tutorials'".to_string()
                        }
                    }
                }
            },
            None => {
                "🎓 SynOS Cybersecurity Learning Platform\n\n\
                Welcome to the interactive cybersecurity education platform!\n\
                This system provides guided, hands-on learning experiences.\n\n\
                Quick Start:\n\
                1. Type 'list' to see available tutorials\n\
                2. Start with 'tutorial phase1_it_fundamentals'\n\
                3. Follow the HUD guidance and use 'hint' when stuck\n\
                4. Track progress with 'progress' command\n\n\
                For detailed help:\n\
                • help commands - Available commands\n\
                • help hud - HUD system information\n\
                • help tutorials - Tutorial system overview\n\n\
                💡 The HUD overlays will guide you through each step!".to_string()
            }
        };
        
        Ok(CommandResult::Success(help_text))
    }

    /// Show current tutorial step hints
    fn show_current_hint(&self) -> Result<CommandResult, &'static str> {
        if let Some(ref session) = self.active_session {
            // Generate contextual hints based on current tutorial step
            let hint = "💡 Current Step Hint:\n\
                      Look for the highlighted elements in the HUD overlay.\n\
                      The blue arrows point to important interface elements.\n\
                      Yellow text shows what commands to try next.\n\n\
                      Stuck? Try 'help <topic>' for more detailed assistance!";
            
            Ok(CommandResult::Success(hint.to_string()))
        } else {
            Ok(CommandResult::Success(
                "No active tutorial. Start one with 'tutorial <module_id>' or see 'list' for available tutorials.".to_string()
            ))
        }
    }

    /// Execute system command with tutorial context
    fn execute_with_tutorial_context(&mut self, cmd: &str) -> Result<CommandResult, &'static str> {
        // Process the command in tutorial context
        if let Some(ref session) = self.active_session {
            if let Some(ref mut engine) = self.tutorial_engine {
                // Process user action for tutorial validation
                match engine.process_user_action(session, cmd) {
                    Ok(response) => {
                        // Simulate command execution result
                        let output = self.simulate_synos_command(cmd);
                        let result = format!("Command executed: {}\n\n{}", cmd, output);
                        Ok(CommandResult::TutorialAction(response))
                    },
                    Err(e) => {
                        // Still execute the command but note tutorial context
                        let output = self.simulate_synos_command(cmd);
                        let result = format!("Command executed: {}\nOutput: {}\n\n⚠️ Tutorial note: {}", cmd, output, e);
                        Ok(CommandResult::Success(result))
                    }
                }
            } else {
                // Execute without tutorial context
                let output = self.simulate_synos_command(cmd);
                Ok(CommandResult::Success(format!("Command executed: {}\nOutput: {}", cmd, output)))
            }
        } else {
            // No active tutorial - execute normally
            let output = self.simulate_synos_command(cmd);
            Ok(CommandResult::Success(format!("Command executed: {}\nOutput: {}", cmd, output)))
        }
    }

    /// Simulate SynOS command execution (placeholder for actual implementation)
    fn simulate_synos_command(&self, cmd: &str) -> String {
        match cmd {
            cmd if cmd.contains("hal info cpu") => {
                "CPU Vendor: Intel\nCPU Model: Core i7-12700K\nCores: 12\nThreads: 20\nFrequency: 3.6 GHz\nFeatures: SSE4.2, AVX2, Virtualization\nAI Consciousness Level: 0.85".to_string()
            },
            cmd if cmd.contains("hal info memory") => {
                "Memory Controller: DDR4 Dual Channel\nTotal Memory: 32 GB\nECC Support: Enabled\nMemory Speed: 3200 MHz\nNUMA Nodes: 1\nAI Memory Optimization: Active".to_string()
            },
            cmd if cmd.contains("net interfaces") => {
                "Interface: eth0 (Ethernet)\nMAC: 00:1A:2B:3C:4D:5E\nStatus: Connected\nSpeed: 1 Gbps\n\nInterface: wlan0 (Wireless)\nMAC: 00:1F:2E:3D:4C:5B\nStatus: Available\nSecurity: WPA3".to_string()
            },
            cmd if cmd.contains("security status") => {
                "Security Level: HIGH\nThreat Detection: Active\nFirewall: Enabled\nEncryption: AES-256\nAI Security Analysis: 94% Confidence\nLast Scan: 2 minutes ago".to_string()
            },
            _ => {
                format!("SynOS command '{}' executed successfully.\n(Simulated output - actual implementation would provide real system data)", cmd)
            }
        }
    }

    /// Show welcome message on initialization
    fn show_welcome_message(&self) -> Result<(), &'static str> {
        crate::println!("🎓 Welcome to SynOS Cybersecurity Learning Platform!");
        crate::println!("═══════════════════════════════════════════════════");
        crate::println!("Interactive tutorials with real-time HUD guidance");
        crate::println!("Start your cybersecurity journey today!");
        crate::println!("");
        crate::println!("💡 Quick start: Type 'help' for guidance or 'list' to see tutorials");
        crate::println!("🎯 HUD overlays will guide you through each step");
        Ok(())
    }

    /// Placeholder implementations for remaining methods
    fn advance_tutorial(&mut self) -> Result<CommandResult, &'static str> {
        Ok(CommandResult::Success("Advanced to next tutorial step".to_string()))
    }

    fn go_back_tutorial(&mut self) -> Result<CommandResult, &'static str> {
        Ok(CommandResult::Success("Returned to previous tutorial step".to_string()))
    }

    fn show_achievements(&self) -> Result<CommandResult, &'static str> {
        Ok(CommandResult::Success("🏆 No achievements yet - complete tutorials to earn them!".to_string()))
    }

    fn show_hud_settings(&self) -> Result<CommandResult, &'static str> {
        Ok(CommandResult::Success("HUD Settings: All overlays enabled".to_string()))
    }

    fn toggle_hud_element(&mut self, element: &str) -> Result<CommandResult, &'static str> {
        Ok(CommandResult::Success(format!("Toggled HUD element: {}", element)))
    }
}

/// Initialize the HUD command interface for a student
pub fn init_hud_interface(student_id: &str) -> Result<HUDCommandInterface, &'static str> {
    let mut interface = HUDCommandInterface::new();
    interface.initialize(student_id)?;
    Ok(interface)
}

/// Process a tutorial command and return the result
pub fn process_tutorial_command(interface: &mut HUDCommandInterface, command: &str) -> Result<CommandResult, &'static str> {
    interface.process_command(command)
}
