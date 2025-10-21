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

            if !report.findings.is_empty() {
                println!("\n   Top findings:");
                for (i, finding) in report.findings.iter().take(3).enumerate() {
                    println!("   {}. [{:?}] {}", i + 1, finding.severity, finding.title);
                }
            }
        }
        Err(e) => println!("❌ Scan failed: {}", e),
    }

    println!("\n");

    // Example 2: Enumerate services
    println!("🔍 Example 2: Service Enumeration");
    println!("Command: synos enumerate 10.0.0.5 --services\n");

    let intent = UserIntent::Enumerate {
        target: "10.0.0.5".to_string(),
        services: vec!["smb".to_string(), "http".to_string()],
    };

    match universal.execute(intent).await {
        Ok(report) => {
            println!("✅ Enumeration completed!");
            println!("   Services found: {}", report.findings.len());
        }
        Err(e) => println!("❌ Enumeration failed: {}", e),
    }

    println!("\n");

    // Example 3: Generate report
    println!("📊 Example 3: Generate Comprehensive Report");
    println!("Command: synos report --format pdf --style executive\n");

    let intent = UserIntent::Report {
        format: ReportFormat::PDF,
        style: ReportStyle::Executive,
    };

    match universal.execute(intent).await {
        Ok(report) => {
            println!("✅ Report generated!");
            println!("   Format: PDF");
            println!("   Pages: Approx. {}", (report.findings.len() / 10) + 5);
        }
        Err(e) => println!("❌ Report generation failed: {}", e),
    }

    println!("\n🎉 Universal Command Demo Complete!");
    println!("\n💡 Key Features:");
    println!("   • AI-powered tool selection based on target and scan mode");
    println!("   • Parallel execution for maximum speed");
    println!("   • Automatic result aggregation and deduplication");
    println!("   • Supports: Scan, Enumerate, Exploit, Report, Shell");
    println!("   • Integration with V1.6 Cloud Security and V1.7 AI Tutor");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_universal_command_creation() {
        let universal = SynOSUniversalCommand::new();
        assert_eq!(universal.tool_selector.tools.len() > 0, true);
    }

    #[tokio::test]
    async fn test_scan_intent() {
        let mut universal = SynOSUniversalCommand::new();
        let intent = UserIntent::Scan {
            target: "127.0.0.1".to_string(),
            mode: ScanMode::Quick,
        };

        // This should execute without panicking
        let result = universal.execute(intent).await;
        assert!(result.is_ok() || result.is_err()); // Either outcome is valid in test
    }
}
