//! SynOS Compliance Assessment CLI

use clap::{Parser, Subcommand};
use compliance_runner::*;
use std::path::PathBuf;
use anyhow::Result;

#[derive(Parser)]
#[command(name = "synos-compliance")]
#[command(about = "Automated compliance framework assessment tool", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run compliance assessment for a framework
    Assess {
        /// Path to compliance framework YAML file
        #[arg(short, long)]
        framework: PathBuf,

        /// Output format (text, json, html)
        #[arg(short, long, default_value = "text")]
        format: String,

        /// Output file (default: stdout)
        #[arg(short, long)]
        output: Option<PathBuf>,
    },

    /// List available compliance frameworks
    List {
        /// Compliance config directory
        #[arg(short, long, default_value = "config/compliance")]
        dir: PathBuf,
    },

    /// Run assessment for all frameworks
    AssessAll {
        /// Compliance config directory
        #[arg(short, long, default_value = "config/compliance")]
        dir: PathBuf,

        /// Output directory for reports
        #[arg(short, long, default_value = "compliance-reports")]
        output: PathBuf,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Assess { framework, format, output } => {
            assess_framework(&framework, &format, output.as_ref())?;
        }

        Commands::List { dir } => {
            list_frameworks(&dir)?;
        }

        Commands::AssessAll { dir, output } => {
            assess_all_frameworks(&dir, &output)?;
        }
    }

    Ok(())
}

fn assess_framework(path: &PathBuf, format: &str, output: Option<&PathBuf>) -> Result<()> {
    println!("Loading framework: {:?}", path);

    let framework = load_framework(path)?;
    println!("Running assessment for: {}", framework.framework.name);

    let report = run_assessment(&framework)?;

    let output_content = match format {
        "json" => serde_json::to_string_pretty(&report)?,
        "html" => generate_html_report(&report),
        _ => generate_report(&report),
    };

    if let Some(out_path) = output {
        std::fs::write(out_path, &output_content)?;
        println!("\nReport written to: {:?}", out_path);
    } else {
        println!("{}", output_content);
    }

    Ok(())
}

fn list_frameworks(dir: &PathBuf) -> Result<()> {
    use colored::*;

    println!("\n{}", "Available Compliance Frameworks:".bold().underline());
    println!("{}", "=".repeat(80).bright_blue());

    let mut frameworks = Vec::new();

    if let Ok(entries) = std::fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("yaml") {
                if let Ok(fw) = load_framework(&path) {
                    frameworks.push((path.clone(), fw));
                }
            }
        }
    }

    if frameworks.is_empty() {
        println!("No frameworks found in {:?}", dir);
        return Ok(());
    }

    for (path, fw) in frameworks {
        println!("\n  {} v{}", fw.framework.name.bold().cyan(), fw.framework.version);
        println!("  └─ {}", fw.framework.description.dimmed());
        println!("     Path: {:?}", path);
    }

    println!("\n{}\n", "=".repeat(80).bright_blue());

    Ok(())
}

fn assess_all_frameworks(dir: &PathBuf, output_dir: &PathBuf) -> Result<()> {
    use colored::*;

    println!("\n{}", "Running All Compliance Assessments".bold().underline());
    println!("{}\n", "=".repeat(80).bright_blue());

    // Create output directory
    std::fs::create_dir_all(output_dir)?;

    let mut frameworks = Vec::new();

    if let Ok(entries) = std::fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("yaml") {
                if let Ok(fw) = load_framework(&path) {
                    frameworks.push((path.clone(), fw));
                }
            }
        }
    }

    let mut summary = Vec::new();

    for (path, fw) in frameworks {
        println!("Assessing: {} ...", fw.framework.name.bold());

        let report = run_assessment(&fw)?;

        // Generate output files
        let base_name = path.file_stem().unwrap().to_str().unwrap();

        // Text report
        let text_path = output_dir.join(format!("{}_report.txt", base_name));
        std::fs::write(&text_path, generate_report(&report))?;

        // JSON report
        let json_path = output_dir.join(format!("{}_report.json", base_name));
        std::fs::write(&json_path, serde_json::to_string_pretty(&report)?)?;

        // HTML report
        let html_path = output_dir.join(format!("{}_report.html", base_name));
        std::fs::write(&html_path, generate_html_report(&report))?;

        let status_color = if report.compliance_score >= 80.0 { "green" } else { "red" };
        println!("  ✓ Score: {} - {}\n",
            format!("{:.1}%", report.compliance_score).color(status_color).bold(),
            report.compliance_level.color(status_color)
        );

        summary.push((fw.framework.name.clone(), report.compliance_score, report.compliance_level.clone()));
    }

    // Print summary
    println!("{}", "=".repeat(80).bright_blue());
    println!("{}\n", "Assessment Summary:".bold().underline());

    for (name, score, level) in summary {
        let color = if score >= 80.0 { "green" } else { "red" };
        println!("  {} - {:.1}% ({})",
            name.bold(),
            score.to_string().color(color),
            level.color(color)
        );
    }

    println!("\n{}", format!("Reports saved to: {:?}", output_dir).bright_green());
    println!("{}\n", "=".repeat(80).bright_blue());

    Ok(())
}

fn generate_html_report(report: &AssessmentReport) -> String {
    format!(r#"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{} - Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .score {{ font-size: 48px; font-weight: bold; text-align: center; margin: 20px 0; }}
        .score.pass {{ color: #27ae60; }}
        .score.fail {{ color: #e74c3c; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 6px; text-align: center; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; }}
        .stat-card .label {{ color: #7f8c8d; margin-top: 10px; }}
        .control {{ background: #fff; border-left: 4px solid #ddd; padding: 12px; margin: 8px 0; }}
        .control.pass {{ border-color: #27ae60; }}
        .control.fail {{ border-color: #e74c3c; }}
        .control.manual {{ border-color: #f39c12; }}
        .severity {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .severity.CRITICAL {{ background: #e74c3c; color: white; }}
        .severity.HIGH {{ background: #e67e22; color: white; }}
        .severity.MEDIUM {{ background: #f39c12; color: white; }}
        .severity.LOW {{ background: #95a5a6; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{} Compliance Assessment</h1>
        <p><strong>Version:</strong> {} | <strong>Date:</strong> {}</p>

        <div class="score {}">{:.1}%</div>
        <p style="text-align: center; font-size: 20px; color: #7f8c8d;">{}</p>

        <div class="stats">
            <div class="stat-card">
                <div class="value" style="color: #3498db;">{}</div>
                <div class="label">Total Controls</div>
            </div>
            <div class="stat-card">
                <div class="value" style="color: #27ae60;">{}</div>
                <div class="label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="value" style="color: #e74c3c;">{}</div>
                <div class="label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="value" style="color: #f39c12;">{}</div>
                <div class="label">Manual Review</div>
            </div>
        </div>

        <h2>Control Results</h2>
        <div class="controls">
            {}
        </div>
    </div>
</body>
</html>"#,
        report.framework_name,
        report.framework_name,
        report.framework_version,
        report.assessment_date,
        if report.compliance_score >= 80.0 { "pass" } else { "fail" },
        report.compliance_score,
        report.compliance_level,
        report.total_controls,
        report.passed,
        report.failed,
        report.manual_review,
        report.control_results.iter().map(|c| {
            format!(r#"<div class="control {}">
                <span class="severity {}">{}</span>
                <strong>[{}]</strong> {}
                <div style="color: #7f8c8d; margin-top: 8px; font-size: 14px;">{}</div>
            </div>"#,
                match c.status {
                    ControlStatus::Pass => "pass",
                    ControlStatus::Fail => "fail",
                    _ => "manual",
                },
                c.severity,
                c.severity,
                c.control_id,
                c.control_title,
                c.check_output.chars().take(200).collect::<String>()
            )
        }).collect::<Vec<_>>().join("\n")
    )
}
