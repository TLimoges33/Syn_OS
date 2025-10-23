//! SynOS Universal Command - Main Binary
//!
//! Command-line interface for the universal command orchestrator

use synos_universal_command::{SynOSUniversalCommand, UserIntent, ScanMode, ReportFormat, ReportStyle};
use std::env;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        print_usage();
        return Ok(());
    }

    let mut universal = SynOSUniversalCommand::new();

    match args[1].as_str() {
        "scan" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-universal scan <target> [mode]");
                return Ok(());
            }

            let target = args[2].clone();
            let mode = if args.len() > 3 {
                match args[3].as_str() {
                    "quick" => ScanMode::Quick,
                    "standard" => ScanMode::Standard,
                    "full" => ScanMode::Full,
                    "stealth" => ScanMode::Stealth,
                    _ => ScanMode::Standard,
                }
            } else {
                ScanMode::Standard
            };

            let intent = UserIntent::Scan { target, mode };
            let report = universal.execute(intent).await?;
            println!("📊 {}", report.title);
            println!("🎯 Target: {}", report.target);
            println!("📅 Generated: {}", report.generated_at);
            println!("🔍 Findings: {}", report.findings.len());
            for finding in &report.findings {
                println!("  • {} [{:?}] - {}", finding.title, finding.severity, finding.description);
            }
        }
        "enumerate" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-universal enumerate <target> [services]");
                return Ok(());
            }

            let target = args[2].clone();
            let services = if args.len() > 3 {
                args[3].split(',').map(|s| s.to_string()).collect()
            } else {
                vec![]
            };

            let intent = UserIntent::Enumerate { target, services };
            let report = universal.execute(intent).await?;
            println!("📊 {}", report.title);
            println!("🎯 Target: {}", report.target);
            println!("📅 Generated: {}", report.generated_at);
            println!("🔍 Findings: {}", report.findings.len());
        }
        "exploit" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-universal exploit <target> [auto]");
                return Ok(());
            }

            let target = args[2].clone();
            let auto_mode = args.len() > 3 && args[3] == "auto";

            let intent = UserIntent::Exploit { target, auto_exploit: auto_mode };
            let report = universal.execute(intent).await?;
            println!("📊 {}", report.title);
            println!("🎯 Target: {}", report.target);
            println!("📅 Generated: {}", report.generated_at);
            println!("🔍 Findings: {}", report.findings.len());
        }
        "report" => {
            let format = ReportFormat::Markdown;
            let style = ReportStyle::Technical;

            let intent = UserIntent::Report { format, style };
            let report = universal.execute(intent).await?;
            println!("📊 {}", report.title);
            println!("📅 Generated: {}", report.generated_at);
            println!("🔍 Total Findings: {}", report.findings.len());
        }
        "shell" => {
            let intent = UserIntent::Shell { target: "localhost".to_string() };
            let _report = universal.execute(intent).await?;
            println!("Interactive shell mode not implemented in CLI");
        }
        "demo" => {
            println!("🚀 SynOS Universal Command Demo");

            // Demo scan
            let demo_intent = UserIntent::Scan {
                target: "127.0.0.1".to_string(),
                mode: ScanMode::Quick
            };

            match universal.execute(demo_intent).await {
                Ok(report) => {
                    println!("✅ Demo scan completed");
                    println!("   Target: {}", report.target);
                    println!("   Findings: {}", report.findings.len());
                    println!("   Tools used: {}", report.tool_results.len());
                }
                Err(e) => {
                    println!("❌ Demo failed: {}", e);
                }
            }
        }
        "version" => {
            println!("SynOS Universal Command v{}", env!("CARGO_PKG_VERSION"));
        }
        "help" | "--help" | "-h" => {
            print_usage();
        }
        _ => {
            eprintln!("Unknown command: {}", args[1]);
            print_usage();
        }
    }

    Ok(())
}

fn print_usage() {
    println!("SynOS Universal Command - AI-powered security tool orchestrator");
    println!();
    println!("USAGE:");
    println!("    synos-universal <COMMAND> [OPTIONS]");
    println!();
    println!("COMMANDS:");
    println!("    scan <target> [mode]     Scan target with AI tool selection");
    println!("                             Modes: quick, standard, full, stealth");
    println!("    enumerate <target>       Enumerate services and information");
    println!("    exploit <target> [auto]  Attempt exploitation (use 'auto' for automated)");
    println!("    report [format] [style]  Generate comprehensive report");
    println!("    shell                    Interactive shell mode");
    println!("    demo                     Run demonstration");
    println!("    version                  Show version information");
    println!("    help                     Show this help message");
    println!();
    println!("EXAMPLES:");
    println!("    synos-universal scan 192.168.1.1 quick");
    println!("    synos-universal enumerate example.com");
    println!("    synos-universal exploit 192.168.1.100 auto");
    println!("    synos-universal report");
    println!();
    println!("For more information, see: https://github.com/TLimoges33/Syn_OS");
}
