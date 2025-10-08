use anyhow::Result;
use std::collections::HashMap;
use std::process::Command;
use tracing::{info, warn};

pub struct ToolManager {
    tools: HashMap<String, ToolStatus>,
}

#[derive(Debug, Clone)]
struct ToolStatus {
    name: String,
    available: bool,
    last_check: std::time::Instant,
    version: Option<String>,
}

impl ToolManager {
    pub fn new(tool_names: Vec<String>) -> Result<Self> {
        info!("Initializing tool manager with {} tools", tool_names.len());

        let mut tools = HashMap::new();
        for name in tool_names {
            tools.insert(name.clone(), ToolStatus {
                name: name.clone(),
                available: false,
                last_check: std::time::Instant::now(),
                version: None,
            });
        }

        Ok(Self { tools })
    }

    pub async fn monitor_tools(&mut self) -> Result<()> {
        for (name, status) in &mut self.tools {
            // Check if tool is available
            let available = Command::new("which")
                .arg(name)
                .output()
                .map(|output| output.status.success())
                .unwrap_or(false);

            if available != status.available {
                if available {
                    info!("Tool {} is now available", name);
                } else {
                    warn!("Tool {} is no longer available", name);
                }
            }

            status.available = available;
            status.last_check = std::time::Instant::now();
        }

        Ok(())
    }

    pub fn get_active_count(&self) -> usize {
        self.tools.values().filter(|s| s.available).count()
    }

    #[allow(dead_code)]
    #[allow(dead_code)]
    pub fn is_tool_available(&self, name: &str) -> bool {
        self.tools.get(name).map(|s| s.available).unwrap_or(false)
    }
}
