//! Natural Language OS Control System
//!
//! Voice and text-based natural language interfaces for controlling SynOS,
//! executing system commands, and managing OS functions through conversational AI.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::RwLock;

use crate::ai::mlops::MLOpsError;
use crate::ai::personal_context_engine::{UserContext, PersonalContextEngine};

/// Natural language command types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CommandType {
    SystemControl,
    FileManagement,
    ProcessManagement,
    NetworkConfiguration,
    SecurityOperation,
    ApplicationLaunch,
    SystemQuery,
    ConfigurationChange,
    Monitoring,
    Troubleshooting,
}

/// Natural language command with parsed intent
#[derive(Debug, Clone)]
pub struct NLCommand {
    pub command_id: String,
    pub user_id: String,
    pub raw_text: String,
    pub intent: CommandIntent,
    pub entities: Vec<CommandEntity>,
    pub confidence_score: f64,
    pub context: CommandContext,
    pub timestamp: u64,
}

/// Parsed command intent
#[derive(Debug, Clone)]
pub struct CommandIntent {
    pub intent_type: CommandType,
    pub action: String,
    pub target: String,
    pub parameters: BTreeMap<String, String>,
    pub safety_level: SafetyLevel,
}

/// Command entities (parameters, objects, values)
#[derive(Debug, Clone)]
pub struct CommandEntity {
    pub entity_type: EntityType,
    pub value: String,
    pub start_pos: usize,
    pub end_pos: usize,
    pub confidence: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EntityType {
    FileName,
    ProcessName,
    ServiceName,
    IPAddress,
    Port,
    Username,
    Permission,
    Directory,
    Command,
    Option,
    Number,
    Time,
}

/// Safety levels for command execution
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum SafetyLevel {
    Safe = 0,        // Read-only operations
    Low = 1,         // Minor system changes
    Medium = 2,      // Significant changes
    High = 3,        // Potentially dangerous
    Critical = 4,    // System-critical operations
}

/// Command execution context
#[derive(Debug, Clone)]
pub struct CommandContext {
    pub session_id: String,
    pub current_directory: String,
    pub environment: BTreeMap<String, String>,
    pub permissions: Vec<Permission>,
    pub previous_commands: Vec<String>,
    pub user_context: Option<UserContext>,
}

/// Permission types for command execution
#[derive(Debug, Clone)]
pub enum Permission {
    ReadFiles,
    WriteFiles,
    ExecuteFiles,
    ManageProcesses,
    NetworkAccess,
    SystemConfiguration,
    UserManagement,
    ServiceControl,
}

/// Command execution result
#[derive(Debug, Clone)]
pub struct CommandResult {
    pub command_id: String,
    pub status: ExecutionStatus,
    pub output: String,
    pub error_message: Option<String>,
    pub execution_time_ms: u64,
    pub system_changes: Vec<SystemChange>,
    pub suggestions: Vec<String>,
}

/// Command execution result for natural language processing
#[derive(Debug, Clone)]
pub struct CommandExecutionResult {
    pub success: bool,
    pub output: String,
    pub error_message: Option<String>,
    pub execution_time_ms: u64,
    pub system_changes: Vec<SystemChange>,
    pub suggestions: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExecutionStatus {
    Success,
    Failed,
    PartialSuccess,
    RequiresConfirmation,
    PermissionDenied,
    SafetyBlocked,
    NotSupported,
}

/// System changes made by commands
#[derive(Debug, Clone)]
pub struct SystemChange {
    pub change_type: ChangeType,
    pub target: String,
    pub old_value: Option<String>,
    pub new_value: String,
    pub reversible: bool,
}

#[derive(Debug, Clone, Copy)]
pub enum ChangeType {
    FileCreated,
    FileModified,
    FileDeleted,
    ProcessStarted,
    ProcessStopped,
    ServiceEnabled,
    ServiceDisabled,
    ConfigurationChanged,
    PermissionChanged,
    UserCreated,
    UserModified,
}

/// Voice interface configuration
#[derive(Debug, Clone)]
pub struct VoiceConfig {
    pub enabled: bool,
    pub language: String,
    pub voice_activation_phrase: String,
    pub confidence_threshold: f64,
    pub noise_reduction: bool,
    pub speaker_identification: bool,
    pub audio_feedback: bool,
}

/// Text processing configuration
#[derive(Debug, Clone)]
pub struct TextConfig {
    pub enabled: bool,
    pub auto_correction: bool,
    pub context_aware_parsing: bool,
    pub command_history_size: u32,
    pub suggestion_count: u32,
}

/// Natural Language Processing pipeline
pub struct NLProcessor {
    intent_classifier: IntentClassifier,
    entity_extractor: EntityExtractor,
    command_templates: RwLock<BTreeMap<String, CommandTemplate>>,
    safety_rules: RwLock<Vec<SafetyRule>>,
}

/// Intent classification model
struct IntentClassifier {
    model_loaded: bool,
    confidence_threshold: f64,
    supported_intents: Vec<CommandType>,
}

/// Named entity recognition model
struct EntityExtractor {
    model_loaded: bool,
    entity_patterns: BTreeMap<EntityType, Vec<String>>,
}

/// Command template for parsing
#[derive(Debug, Clone)]
pub struct CommandTemplate {
    pub template_id: String,
    pub intent_type: CommandType,
    pub patterns: Vec<String>,
    pub required_entities: Vec<EntityType>,
    pub optional_entities: Vec<EntityType>,
    pub safety_level: SafetyLevel,
    pub system_command: String,
}

/// Safety rule for command validation
#[derive(Debug, Clone)]
pub struct SafetyRule {
    pub rule_id: String,
    pub description: String,
    pub conditions: Vec<SafetyCondition>,
    pub action: SafetyAction,
}

#[derive(Debug, Clone)]
pub enum SafetyCondition {
    CommandType(CommandType),
    SafetyLevel(SafetyLevel),
    EntityValue(EntityType, String),
    UserPermission(Permission),
}

#[derive(Debug, Clone)]
pub enum SafetyAction {
    Block,
    RequireConfirmation,
    RequireElevation,
    LogOnly,
}

impl NLProcessor {
    /// Create new NL processor
    pub fn new() -> Self {
        let processor = Self {
            intent_classifier: IntentClassifier {
                model_loaded: true,
                confidence_threshold: 0.75,
                supported_intents: vec![
                    CommandType::SystemControl,
                    CommandType::FileManagement,
                    CommandType::ProcessManagement,
                    CommandType::ApplicationLaunch,
                    CommandType::SystemQuery,
                ],
            },
            entity_extractor: EntityExtractor {
                model_loaded: true,
                entity_patterns: BTreeMap::new(),
            },
            command_templates: RwLock::new(BTreeMap::new()),
            safety_rules: RwLock::new(Vec::new()),
        };

        processor.initialize_templates();
        processor.initialize_safety_rules();
        processor
    }

    /// Initialize command templates
    fn initialize_templates(&self) {
        let templates = vec![
            CommandTemplate {
                template_id: "list_files".to_string(),
                intent_type: CommandType::FileManagement,
                patterns: vec![
                    "list files in {directory}".to_string(),
                    "show me files in {directory}".to_string(),
                    "what files are in {directory}".to_string(),
                ],
                required_entities: vec![EntityType::Directory],
                optional_entities: Vec::new(),
                safety_level: SafetyLevel::Safe,
                system_command: "ls {directory}".to_string(),
            },
            CommandTemplate {
                template_id: "kill_process".to_string(),
                intent_type: CommandType::ProcessManagement,
                patterns: vec![
                    "kill process {process}".to_string(),
                    "stop {process}".to_string(),
                    "terminate {process}".to_string(),
                ],
                required_entities: vec![EntityType::ProcessName],
                optional_entities: Vec::new(),
                safety_level: SafetyLevel::High,
                system_command: "pkill {process}".to_string(),
            },
            CommandTemplate {
                template_id: "start_service".to_string(),
                intent_type: CommandType::SystemControl,
                patterns: vec![
                    "start {service} service".to_string(),
                    "enable {service}".to_string(),
                    "turn on {service}".to_string(),
                ],
                required_entities: vec![EntityType::ServiceName],
                optional_entities: Vec::new(),
                safety_level: SafetyLevel::Medium,
                system_command: "systemctl start {service}".to_string(),
            },
            CommandTemplate {
                template_id: "system_status".to_string(),
                intent_type: CommandType::SystemQuery,
                patterns: vec![
                    "show system status".to_string(),
                    "what's the system status".to_string(),
                    "check system health".to_string(),
                ],
                required_entities: Vec::new(),
                optional_entities: Vec::new(),
                safety_level: SafetyLevel::Safe,
                system_command: "systemctl status".to_string(),
            },
            CommandTemplate {
                template_id: "reboot_system".to_string(),
                intent_type: CommandType::SystemControl,
                patterns: vec![
                    "reboot system".to_string(),
                    "restart computer".to_string(),
                    "reboot now".to_string(),
                ],
                required_entities: Vec::new(),
                optional_entities: Vec::new(),
                safety_level: SafetyLevel::Critical,
                system_command: "reboot".to_string(),
            },
        ];

        let mut template_map = self.command_templates.write();
        for template in templates {
            template_map.insert(template.template_id.clone(), template);
        }
    }

    /// Initialize safety rules
    fn initialize_safety_rules(&self) {
        let rules = vec![
            SafetyRule {
                rule_id: "block_critical_without_confirmation".to_string(),
                description: "Block critical operations without explicit confirmation".to_string(),
                conditions: vec![SafetyCondition::SafetyLevel(SafetyLevel::Critical)],
                action: SafetyAction::RequireConfirmation,
            },
            SafetyRule {
                rule_id: "block_system_files".to_string(),
                description: "Block operations on system files".to_string(),
                conditions: vec![
                    SafetyCondition::CommandType(CommandType::FileManagement),
                    SafetyCondition::EntityValue(EntityType::Directory, "/sys".to_string()),
                ],
                action: SafetyAction::Block,
            },
            SafetyRule {
                rule_id: "require_elevation_for_services".to_string(),
                description: "Require elevation for service management".to_string(),
                conditions: vec![SafetyCondition::CommandType(CommandType::SystemControl)],
                action: SafetyAction::RequireElevation,
            },
        ];

        let mut safety_rules = self.safety_rules.write();
        *safety_rules = rules;
    }

    /// Process natural language command
    pub fn process_command(&self, raw_text: String, user_id: String, context: CommandContext) -> Result<NLCommand, MLOpsError> {
        let command_id = format!("nlcmd_{}", get_current_timestamp());

        // Extract intent
        let intent = self.classify_intent(&raw_text)?;

        // Extract entities
        let entities = self.extract_entities(&raw_text, &intent)?;

        // Calculate confidence score
        let confidence_score = self.calculate_confidence(&intent, &entities);

        let nl_command = NLCommand {
            command_id,
            user_id,
            raw_text,
            intent,
            entities,
            confidence_score,
            context,
            timestamp: get_current_timestamp(),
        };

        Ok(nl_command)
    }

    /// Classify user intent
    fn classify_intent(&self, text: &str) -> Result<CommandIntent, MLOpsError> {
        let templates = self.command_templates.read();

        // Simple pattern matching (in production, would use ML model)
        for template in templates.values() {
            for pattern in &template.patterns {
                if self.matches_pattern(text, pattern) {
                    return Ok(CommandIntent {
                        intent_type: template.intent_type.clone(),
                        action: self.extract_action(text, pattern),
                        target: self.extract_target(text, pattern),
                        parameters: BTreeMap::new(),
                        safety_level: template.safety_level,
                    });
                }
            }
        }

        // Default fallback
        Ok(CommandIntent {
            intent_type: CommandType::SystemQuery,
            action: "unknown".to_string(),
            target: text.to_string(),
            parameters: BTreeMap::new(),
            safety_level: SafetyLevel::Safe,
        })
    }

    /// Extract entities from text
    fn extract_entities(&self, text: &str, intent: &CommandIntent) -> Result<Vec<CommandEntity>, MLOpsError> {
        let mut entities = Vec::new();

        // Simple entity extraction (in production, would use NER model)
        let words: Vec<&str> = text.split_whitespace().collect();

        for (i, word) in words.iter().enumerate() {
            // Directory detection
            if word.starts_with('/') || word.starts_with('~') {
                entities.push(CommandEntity {
                    entity_type: EntityType::Directory,
                    value: word.to_string(),
                    start_pos: i * 5, // Simplified position
                    end_pos: (i + 1) * 5,
                    confidence: 0.9,
                });
            }

            // Process name detection (simple heuristic)
            if intent.intent_type == CommandType::ProcessManagement && !word.contains('/') && word.len() > 2 {
                entities.push(CommandEntity {
                    entity_type: EntityType::ProcessName,
                    value: word.to_string(),
                    start_pos: i * 5,
                    end_pos: (i + 1) * 5,
                    confidence: 0.8,
                });
            }

            // Service name detection
            if intent.intent_type == CommandType::SystemControl && (word.ends_with("d") || word.ends_with(".service")) {
                entities.push(CommandEntity {
                    entity_type: EntityType::ServiceName,
                    value: word.to_string(),
                    start_pos: i * 5,
                    end_pos: (i + 1) * 5,
                    confidence: 0.85,
                });
            }
        }

        Ok(entities)
    }

    /// Simple pattern matching
    fn matches_pattern(&self, text: &str, pattern: &str) -> bool {
        let text_lower = text.to_lowercase();
        let pattern_parts: Vec<&str> = pattern.split('{').collect();

        if pattern_parts.is_empty() {
            return false;
        }

        text_lower.contains(&pattern_parts[0].to_lowercase())
    }

    /// Extract action from text
    fn extract_action(&self, text: &str, _pattern: &str) -> String {
        let words: Vec<&str> = text.split_whitespace().collect();
        if let Some(first_word) = words.first() {
            first_word.to_string()
        } else {
            "unknown".to_string()
        }
    }

    /// Extract target from text
    fn extract_target(&self, text: &str, _pattern: &str) -> String {
        let words: Vec<&str> = text.split_whitespace().collect();
        if words.len() > 1 {
            words[1..].join(" ")
        } else {
            "unknown".to_string()
        }
    }

    /// Calculate confidence score
    fn calculate_confidence(&self, intent: &CommandIntent, entities: &[CommandEntity]) -> f64 {
        let base_confidence = 0.7;
        let entity_bonus = entities.len() as f64 * 0.1;
        let safety_penalty = match intent.safety_level {
            SafetyLevel::Safe => 0.0,
            SafetyLevel::Low => -0.05,
            SafetyLevel::Medium => -0.1,
            SafetyLevel::High => -0.15,
            SafetyLevel::Critical => -0.2,
        };

        (base_confidence + entity_bonus + safety_penalty).min(1.0).max(0.0)
    }
}

/// Command execution engine
pub struct CommandExecutor {
    safety_checker: SafetyChecker,
    system_interface: SystemInterface,
    execution_history: RwLock<Vec<ExecutedCommand>>,
}

/// Safety checking system
struct SafetyChecker {
    rules: Vec<SafetyRule>,
    blocked_commands: Vec<String>,
}

/// System interface for command execution
struct SystemInterface {
    dry_run_mode: bool,
    execution_timeout_ms: u64,
}

/// Executed command record
#[derive(Debug, Clone)]
struct ExecutedCommand {
    pub command: NLCommand,
    pub result: CommandResult,
    pub timestamp: u64,
}

impl CommandExecutor {
    /// Create new command executor
    pub fn new() -> Self {
        Self {
            safety_checker: SafetyChecker {
                rules: Vec::new(),
                blocked_commands: vec![
                    "rm -rf /".to_string(),
                    "dd if=/dev/zero of=/dev/sda".to_string(),
                    ":(){ :|:& };:".to_string(), // Fork bomb
                ],
            },
            system_interface: SystemInterface {
                dry_run_mode: false,
                execution_timeout_ms: 30000, // 30 seconds
            },
            execution_history: RwLock::new(Vec::new()),
        }
    }

    /// Execute natural language command
    pub fn execute_command(&self, command: NLCommand) -> Result<CommandResult, MLOpsError> {
        let start_time = get_current_timestamp();

        // Safety check
        let safety_check = self.safety_checker.check_command(&command);
        if !safety_check.allowed {
            return Ok(CommandResult {
                command_id: command.command_id,
                status: ExecutionStatus::SafetyBlocked,
                output: "Command blocked by safety rules".to_string(),
                error_message: Some(safety_check.reason),
                execution_time_ms: get_current_timestamp() - start_time,
                system_changes: Vec::new(),
                suggestions: safety_check.suggestions,
            });
        }

        // Convert NL command to system command
        let system_command = self.convert_to_system_command(&command)?;

        // Execute system command
        let execution_result = self.system_interface.execute(&system_command);
        let suggestions = self.generate_suggestions(&command, &execution_result);

        let result = CommandResult {
            command_id: command.command_id.clone(),
            status: if execution_result.success { ExecutionStatus::Success } else { ExecutionStatus::Failed },
            output: execution_result.output,
            error_message: execution_result.error,
            execution_time_ms: get_current_timestamp() - start_time,
            system_changes: execution_result.changes.clone(),
            suggestions,
        };

        // Store in history
        let executed_command = ExecutedCommand {
            command,
            result: result.clone(),
            timestamp: get_current_timestamp(),
        };

        let mut history = self.execution_history.write();
        history.push(executed_command);

        // Keep only last 1000 commands
        if history.len() > 1000 {
            history.remove(0);
        }

        Ok(result)
    }

    /// Convert NL command to system command
    fn convert_to_system_command(&self, command: &NLCommand) -> Result<String, MLOpsError> {
        match command.intent.intent_type {
            CommandType::FileManagement => {
                if command.intent.action == "list" {
                    let directory = command.entities.iter()
                        .find(|e| e.entity_type == EntityType::Directory)
                        .map(|e| e.value.clone())
                        .unwrap_or_else(|| ".".to_string());
                    Ok(format!("ls -la {}", directory))
                } else {
                    Ok("ls".to_string())
                }
            }
            CommandType::ProcessManagement => {
                if command.intent.action == "kill" {
                    if let Some(process) = command.entities.iter().find(|e| e.entity_type == EntityType::ProcessName) {
                        Ok(format!("pkill {}", process.value))
                    } else {
                        Err(MLOpsError::InvalidConfiguration)
                    }
                } else {
                    Ok("ps aux".to_string())
                }
            }
            CommandType::SystemControl => {
                if command.intent.action == "start" {
                    if let Some(service) = command.entities.iter().find(|e| e.entity_type == EntityType::ServiceName) {
                        Ok(format!("systemctl start {}", service.value))
                    } else {
                        Ok("systemctl status".to_string())
                    }
                } else if command.intent.action == "reboot" {
                    Ok("reboot".to_string())
                } else {
                    Ok("systemctl status".to_string())
                }
            }
            CommandType::SystemQuery => {
                Ok("uname -a && uptime && df -h".to_string())
            }
            _ => Ok("echo 'Command not supported'".to_string()),
        }
    }

    /// Generate helpful suggestions
    fn generate_suggestions(&self, command: &NLCommand, execution_result: &SystemExecutionResult) -> Vec<String> {
        let mut suggestions = Vec::new();

        if !execution_result.success {
            match command.intent.intent_type {
                CommandType::FileManagement => {
                    suggestions.push("Try using 'sudo' for permission-related issues".to_string());
                    suggestions.push("Check if the file or directory exists".to_string());
                }
                CommandType::ProcessManagement => {
                    suggestions.push("Use 'ps aux | grep <name>' to find the exact process name".to_string());
                    suggestions.push("Try 'killall <process_name>' instead".to_string());
                }
                CommandType::SystemControl => {
                    suggestions.push("Check service status with 'systemctl status <service>'".to_string());
                    suggestions.push("You may need sudo privileges".to_string());
                }
                _ => {
                    suggestions.push("Try rephrasing your command".to_string());
                }
            }
        }

        suggestions
    }
}

/// Safety check result
struct SafetyCheckResult {
    pub allowed: bool,
    pub reason: String,
    pub suggestions: Vec<String>,
}

impl SafetyChecker {
    /// Check if command is safe to execute
    fn check_command(&self, command: &NLCommand) -> SafetyCheckResult {
        // Check blocked commands
        for blocked in &self.blocked_commands {
            if command.raw_text.to_lowercase().contains(blocked) {
                return SafetyCheckResult {
                    allowed: false,
                    reason: "Command contains dangerous patterns".to_string(),
                    suggestions: vec!["Please use a safer alternative".to_string()],
                };
            }
        }

        // Check safety level
        match command.intent.safety_level {
            SafetyLevel::Critical => SafetyCheckResult {
                allowed: false,
                reason: "Critical operations require explicit confirmation".to_string(),
                suggestions: vec!["Add 'confirm' to your command or use the system interface".to_string()],
            },
            SafetyLevel::High => SafetyCheckResult {
                allowed: true, // Would require confirmation in production
                reason: "High-risk operation".to_string(),
                suggestions: vec!["Please be cautious with this operation".to_string()],
            },
            _ => SafetyCheckResult {
                allowed: true,
                reason: "Safe to execute".to_string(),
                suggestions: Vec::new(),
            },
        }
    }
}

/// System execution result
struct SystemExecutionResult {
    pub success: bool,
    pub output: String,
    pub error: Option<String>,
    pub changes: Vec<SystemChange>,
}

impl SystemInterface {
    /// Execute system command
    fn execute(&self, command: &str) -> SystemExecutionResult {
        crate::println!("Executing system command: {}", command);

        if self.dry_run_mode {
            return SystemExecutionResult {
                success: true,
                output: format!("DRY RUN: Would execute '{}'", command),
                error: None,
                changes: Vec::new(),
            };
        }

        // Simulate command execution
        match command {
            cmd if cmd.starts_with("ls") => SystemExecutionResult {
                success: true,
                output: "file1.txt  file2.txt  directory1/  directory2/".to_string(),
                error: None,
                changes: Vec::new(),
            },
            cmd if cmd.starts_with("ps") => SystemExecutionResult {
                success: true,
                output: "PID    COMMAND\n1234   synos-kernel\n5678   synos-ai-engine".to_string(),
                error: None,
                changes: Vec::new(),
            },
            cmd if cmd.starts_with("systemctl status") => SystemExecutionResult {
                success: true,
                output: "● synos-ai-engine.service - SynOS AI Engine\nLoaded: loaded\nActive: active (running)".to_string(),
                error: None,
                changes: Vec::new(),
            },
            cmd if cmd.starts_with("uname") => SystemExecutionResult {
                success: true,
                output: "SynOS 1.0.0 x86_64 GNU/Linux".to_string(),
                error: None,
                changes: Vec::new(),
            },
            _ => SystemExecutionResult {
                success: false,
                output: String::new(),
                error: Some("Command not found or not supported".to_string()),
                changes: Vec::new(),
            },
        }
    }
}

/// Main Natural Language Control System
pub struct NaturalLanguageControlSystem {
    nl_processor: NLProcessor,
    command_executor: CommandExecutor,
    voice_config: RwLock<VoiceConfig>,
    text_config: RwLock<TextConfig>,
    active_sessions: RwLock<BTreeMap<String, ControlSession>>,
}

/// Control session for maintaining context
#[derive(Debug, Clone)]
struct ControlSession {
    pub session_id: String,
    pub user_id: String,
    pub start_time: u64,
    pub last_activity: u64,
    pub command_count: u32,
    pub context: CommandContext,
}

impl NaturalLanguageControlSystem {
    /// Create new NL control system
    pub fn new() -> Self {
        let voice_config = VoiceConfig {
            enabled: true,
            language: "en-US".to_string(),
            voice_activation_phrase: "Hey SynOS".to_string(),
            confidence_threshold: 0.8,
            noise_reduction: true,
            speaker_identification: false,
            audio_feedback: true,
        };

        let text_config = TextConfig {
            enabled: true,
            auto_correction: true,
            context_aware_parsing: true,
            command_history_size: 100,
            suggestion_count: 5,
        };

        Self {
            nl_processor: NLProcessor::new(),
            command_executor: CommandExecutor::new(),
            voice_config: RwLock::new(voice_config),
            text_config: RwLock::new(text_config),
            active_sessions: RwLock::new(BTreeMap::new()),
        }
    }

    /// Process natural language input
    pub fn process_input(&self, input: String, user_id: String, session_id: String) -> Result<CommandResult, MLOpsError> {
        // Get or create session
        let context = self.get_or_create_session(&user_id, &session_id);

        // Process the command
        let nl_command = self.nl_processor.process_command(input, user_id, context)?;

        // Execute the command
        let result = self.command_executor.execute_command(nl_command)?;

        // Update session
        self.update_session(&session_id);

        Ok(result)
    }

    /// Get or create control session
    fn get_or_create_session(&self, user_id: &str, session_id: &str) -> CommandContext {
        let mut sessions = self.active_sessions.write();

        if let Some(session) = sessions.get_mut(session_id) {
            session.last_activity = get_current_timestamp();
            session.context.clone()
        } else {
            let context = CommandContext {
                session_id: session_id.to_string(),
                current_directory: "/home/user".to_string(),
                environment: BTreeMap::new(),
                permissions: vec![Permission::ReadFiles, Permission::WriteFiles],
                previous_commands: Vec::new(),
                user_context: None,
            };

            let session = ControlSession {
                session_id: session_id.to_string(),
                user_id: user_id.to_string(),
                start_time: get_current_timestamp(),
                last_activity: get_current_timestamp(),
                command_count: 0,
                context: context.clone(),
            };

            sessions.insert(session_id.to_string(), session);
            context
        }
    }

    /// Update session after command
    fn update_session(&self, session_id: &str) {
        let mut sessions = self.active_sessions.write();
        if let Some(session) = sessions.get_mut(session_id) {
            session.command_count += 1;
            session.last_activity = get_current_timestamp();
        }
    }

    /// Generate system status report
    pub fn generate_report(&self) -> String {
        let sessions = self.active_sessions.read();
        let voice_config = self.voice_config.read();
        let text_config = self.text_config.read();

        let mut report = String::new();

        report.push_str("=== SYNOS NATURAL LANGUAGE CONTROL REPORT ===\n\n");

        // Configuration
        report.push_str("=== CONFIGURATION ===\n");
        report.push_str(&format!("Voice Control: {}\n", if voice_config.enabled { "Enabled" } else { "Disabled" }));
        report.push_str(&format!("Text Control: {}\n", if text_config.enabled { "Enabled" } else { "Disabled" }));
        report.push_str(&format!("Voice Language: {}\n", voice_config.language));
        report.push_str(&format!("Activation Phrase: {}\n", voice_config.voice_activation_phrase));

        // Active sessions
        report.push_str("\n=== ACTIVE SESSIONS ===\n");
        report.push_str(&format!("Total Sessions: {}\n", sessions.len()));

        for session in sessions.values() {
            report.push_str(&format!("Session: {} (User: {})\n", session.session_id, session.user_id));
            report.push_str(&format!("  Commands: {}\n", session.command_count));
            report.push_str(&format!("  Directory: {}\n", session.context.current_directory));
            report.push_str(&format!("  Permissions: {} granted\n", session.context.permissions.len()));
        }

        report
    }
}

/// Global natural language control system
pub static NL_CONTROL_SYSTEM: RwLock<Option<NaturalLanguageControlSystem>> = RwLock::new(None);

/// Initialize natural language control system
pub fn init_natural_language_control() -> Result<(), MLOpsError> {
    let system = NaturalLanguageControlSystem::new();
    *NL_CONTROL_SYSTEM.write() = Some(system);
    Ok(())
}

/// Get NL control system report
pub fn get_nl_control_report() -> Result<String, MLOpsError> {
    if let Some(system) = NL_CONTROL_SYSTEM.read().as_ref() {
        Ok(system.generate_report())
    } else {
        Err(MLOpsError::InvalidConfiguration)
    }
}

/// Helper function to get current timestamp
fn get_current_timestamp() -> u64 {
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    COUNTER.fetch_add(1, Ordering::SeqCst)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_nl_control_system_creation() {
        let system = NaturalLanguageControlSystem::new();
        let voice_config = system.voice_config.read();
        assert!(voice_config.enabled);
        assert_eq!(voice_config.language, "en-US");
    }

    #[test]
    fn test_intent_classification() {
        let processor = NLProcessor::new();
        let intent = processor.classify_intent("list files in /home").unwrap();
        assert_eq!(intent.intent_type, CommandType::FileManagement);
    }

    #[test]
    fn test_entity_extraction() {
        let processor = NLProcessor::new();
        let intent = CommandIntent {
            intent_type: CommandType::FileManagement,
            action: "list".to_string(),
            target: "/home".to_string(),
            parameters: BTreeMap::new(),
            safety_level: SafetyLevel::Safe,
        };
        let entities = processor.extract_entities("list files in /home", &intent).unwrap();
        assert!(!entities.is_empty());
        assert_eq!(entities[0].entity_type, EntityType::Directory);
        assert_eq!(entities[0].value, "/home");
    }
}