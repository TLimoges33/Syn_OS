// Universal Command Module - The One Command to Rule Them All
//
// This module provides a unified interface for orchestrating all security tools
// with AI-powered tool selection and parallel execution.

pub mod tool_orchestrator;

// Re-export main types
pub use tool_orchestrator::{
    SynOSUniversalCommand,
    UserIntent,
    ScanMode,
    ReportFormat,
    ReportStyle,
    ToolOrchestrator,
    AIToolSelector,
    ToolExecution,
    ExecutionStatus,
    ToolResult,
    Report,
    Finding,
    Severity,
};

/// Demo function showing universal command usage
pub async fn demo_universal_command() -> Result<(), String> {
    println!("🚀 SynOS Universal Command - V1.9 Demo");
    println!("=========================================\n");

    let mut universal = SynOSUniversalCommand::new();

    // Example 1: Quick network scan
    println!("📡 Example 1: Quick Network Scan");
    println!("Command: synos scan 192.168.1.1 --quick\n");

    let intent = UserIntent::Scan {
        target: "192.168.1.1".to_string(),
        mode: ScanMode::Quick,
    };

    match universal.execute(intent).await {
        Ok(report) => {
            println!("✅ Scan completed!");
            println!("   Tools used: {}", report.tool_results.len());
            println!("   Findings: {}", report.findings.len());
        }
        Err(e) => println!("❌ Scan failed: {}", e),
    }

    println!("\n🎉 Universal Command Demo Complete!");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_universal_command_creation() {
        let universal = SynOSUniversalCommand::new();
        assert!(universal.tool_selector.tools.len() > 0);
    }
}
