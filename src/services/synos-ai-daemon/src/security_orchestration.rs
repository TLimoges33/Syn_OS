/// Security Orchestration - AI-Powered Security Tool Management
/// Orchestrates Parrot OS security tools with AI-driven decision making

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info, warn};

use crate::ai_runtime::AIRuntimeManager;
use crate::consciousness::ConsciousnessState;
use crate::SecurityConfig;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityTask {
    pub task_id: String,
    pub task_type: TaskType,
    pub target: String,
    pub priority: Priority,
    pub status: TaskStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskType {
    NetworkScan,
    VulnerabilityAssessment,
    PenetrationTest,
    ThreatHunting,
    IncidentResponse,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum Priority {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskStatus {
    Pending,
    Running,
    Completed,
    Failed,
}

#[derive(Debug)]
pub struct SecurityOrchestrator {
    config: SecurityConfig,
    ai_runtime: Arc<AIRuntimeManager>,
    active_tasks: Arc<RwLock<HashMap<String, SecurityTask>>>,
    tool_inventory: Arc<RwLock<Vec<String>>>,
    consciousness_priorities: Arc<RwLock<Option<ConsciousnessState>>>,
}

impl SecurityOrchestrator {
    pub async fn new(config: SecurityConfig, ai_runtime: Arc<AIRuntimeManager>) -> Result<Self> {
        info!("🛡️  Initializing Security Orchestrator");
        info!("  - AI Analysis: {}", config.ai_analysis);
        info!("  - Threat Intelligence: {}", config.threat_intelligence);

        let tool_inventory = config.tools.clone();

        Ok(Self {
            config,
            ai_runtime,
            active_tasks: Arc::new(RwLock::new(HashMap::new())),
            tool_inventory: Arc::new(RwLock::new(tool_inventory)),
            consciousness_priorities: Arc::new(RwLock::new(None)),
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("🚀 Security Orchestrator operational");

        loop {
            // Process security tasks
            self.process_tasks().await?;

            // Update threat intelligence
            if self.config.threat_intelligence {
                self.update_threat_intelligence().await?;
            }

            tokio::time::sleep(tokio::time::Duration::from_secs(15)).await;
        }
    }

    async fn process_tasks(&self) -> Result<()> {
        let mut tasks = self.active_tasks.write().await;

        // Process pending tasks
        let pending_tasks: Vec<_> = tasks
            .values()
            .filter(|t| matches!(t.status, TaskStatus::Pending))
            .cloned()
            .collect();

        for task in pending_tasks {
            info!("📋 Processing task: {} ({:?})", task.task_id, task.task_type);

            // Use AI to select best tool for task
            let tool = self.select_tool_for_task(&task).await?;

            info!("  ✓ Selected tool: {}", tool);

            // Update task status
            if let Some(t) = tasks.get_mut(&task.task_id) {
                t.status = TaskStatus::Running;
            }
        }

        Ok(())
    }

    async fn select_tool_for_task(&self, task: &SecurityTask) -> Result<String> {
        let tools = self.tool_inventory.read().await;

        if self.config.ai_analysis {
            // Use AI runtime for intelligent tool selection
            debug!("Using AI to select tool for {:?}", task.task_type);
        }

        // Default tool selection based on task type
        let tool = match task.task_type {
            TaskType::NetworkScan => "nmap",
            TaskType::VulnerabilityAssessment => "nessus",
            TaskType::PenetrationTest => "metasploit",
            TaskType::ThreatHunting => "wireshark",
            TaskType::IncidentResponse => "volatility",
        };

        // Verify tool is available
        if tools.contains(&tool.to_string()) {
            Ok(tool.to_string())
        } else {
            warn!("Tool {} not available, using fallback", tool);
            Ok(tools.first().cloned().unwrap_or_default())
        }
    }

    async fn update_threat_intelligence(&self) -> Result<()> {
        debug!("Updating threat intelligence feeds");

        // In production, this would:
        // 1. Fetch latest IOCs from threat feeds
        // 2. Update ML models with new threat patterns
        // 3. Correlate with consciousness insights

        Ok(())
    }

    pub async fn create_task(&self, task: SecurityTask) -> Result<()> {
        let mut tasks = self.active_tasks.write().await;

        info!("➕ Created security task: {} (Priority: {:?})", task.task_id, task.priority);
        tasks.insert(task.task_id.clone(), task);

        Ok(())
    }

    pub async fn update_consciousness_priorities(&self, state: ConsciousnessState) -> Result<()> {
        let mut priorities = self.consciousness_priorities.write().await;
        *priorities = Some(state);

        debug!("Updated consciousness-driven security priorities");
        Ok(())
    }

    pub async fn get_active_tasks(&self) -> Result<Vec<SecurityTask>> {
        let tasks = self.active_tasks.read().await;
        Ok(tasks.values().cloned().collect())
    }

    pub async fn health_check(&self) -> Result<()> {
        let tools = self.tool_inventory.read().await;

        if tools.is_empty() {
            warn!("No security tools available in inventory");
        }

        Ok(())
    }
}
