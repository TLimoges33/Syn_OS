//! SynOS Advanced Threat Hunting Platform CLI
//!
//! Command-line interface for threat hunting operations

use synos_threat_hunting::*;
use chrono::Utc;

fn main() {
    println!("🔍 SynOS Advanced Threat Hunting Platform");
    println!("==========================================\n");

    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        print_usage();
        return;
    }

    match args[1].as_str() {
        "demo" => run_comprehensive_demo(),
        "yara" => demo_yara_scanning(),
        "sigma" => demo_sigma_detection(),
        "query" => demo_hunt_queries(),
        "ioc" => demo_ioc_scanning(),
        "timeline" => demo_timeline_analysis(),
        "profile" => demo_threat_profiling(),
        "hunt" => run_full_hunt(),
        _ => print_usage(),
    }
}

fn print_usage() {
    println!("Usage: synos-threat-hunting <command>");
    println!("\nCommands:");
    println!("  demo       - Run comprehensive demonstration");
    println!("  yara       - Demonstrate YARA rule scanning");
    println!("  sigma      - Demonstrate Sigma detection");
    println!("  query      - Demonstrate hunt query language");
    println!("  ioc        - Demonstrate IOC scanning");
    println!("  timeline   - Demonstrate timeline analysis");
    println!("  profile    - Demonstrate threat actor profiling");
    println!("  hunt       - Run full threat hunt simulation");
}

fn run_comprehensive_demo() {
    println!("🎯 Running Comprehensive Threat Hunting Demo\n");

    demo_yara_scanning();
    println!();
    demo_sigma_detection();
    println!();
    demo_hunt_queries();
    println!();
    demo_ioc_scanning();
    println!();
    demo_timeline_analysis();
    println!();
    demo_threat_profiling();

    println!("\n✅ Comprehensive demo complete!");
}

fn demo_yara_scanning() {
    println!("🔬 1. YARA Rule Scanning");
    println!("────────────────────────");

    let yara_engine = YaraEngine::new();

    println!("📋 Loaded YARA rules:");
    for rule in yara_engine.list_rules() {
        println!("   • {}", rule);
    }

    println!("\n🔍 Scanning for malware patterns...");

    // Create temporary test file
    let test_content = r#"
<?php
eval($_POST['cmd']);
system($_GET['exec']);
?>
    "#;

    std::fs::write("/tmp/suspicious.php", test_content).ok();

    match yara_engine.scan_path("/tmp/suspicious.php", &[]) {
        Ok(matches) => {
            if matches.is_empty() {
                println!("   ✅ No malware patterns detected");
            } else {
                for m in matches {
                    println!("   ⚠️  YARA Match: {}", m.rule_name);
                    println!("      File: {}", m.file_path);
                    println!("      Hash: {}", m.file_hash);
                    println!("      MITRE Tactics: {:?}", m.mitre_tactics);
                }
            }
        }
        Err(e) => println!("   ❌ Error: {}", e),
    }

    // Cleanup
    std::fs::remove_file("/tmp/suspicious.php").ok();
}

fn demo_sigma_detection() {
    println!("📊 2. Sigma Detection Rules");
    println!("───────────────────────────");

    let sigma_engine = SigmaDetectionEngine::new();

    println!("📋 Loaded Sigma rules:");
    for rule_id in sigma_engine.list_rules() {
        if let Some(rule) = sigma_engine.get_rule(&rule_id) {
            println!("   • {} - {}", rule.id, rule.title);
        }
    }

    println!("\n🔍 Analyzing security events...");

    let mock_logs = "CommandLine=sekurlsa::logonpasswords process=mimikatz.exe user=admin";

    match sigma_engine.detect(mock_logs, &[]) {
        Ok(detections) => {
            if detections.is_empty() {
                println!("   ✅ No suspicious activity detected");
            } else {
                for detection in detections {
                    println!("   🚨 Detection: {}", detection.title);
                    println!("      Severity: {:?}", detection.severity);
                    println!("      Confidence: {:.0}%", detection.confidence * 100.0);
                    println!("      MITRE: {:?}", detection.mitre_techniques);
                }
            }
        }
        Err(e) => println!("   ❌ Error: {}", e),
    }
}

fn demo_hunt_queries() {
    println!("💬 3. Hunt Query Language");
    println!("─────────────────────────");

    let query_engine = HuntQueryEngine::new();

    println!("📋 Available data sources:");
    for source in query_engine.list_data_sources() {
        println!("   • {}", source);
    }

    println!("\n🔍 Executing hunt queries...");

    let queries = vec![
        "HUNT processes WHERE user = SYSTEM",
        "HUNT network WHERE destination_port = 445",
        "HUNT processes WHERE commandline CONTAINS whoami",
    ];

    for query in queries {
        println!("\n   Query: {}", query);
        match query_engine.execute(query) {
            Ok(results) => {
                println!("   Results: {} findings", results.len());
                for (i, result) in results.iter().take(2).enumerate() {
                    println!("      {}. {} ({:?})", i + 1, result.description, result.severity);
                }
            }
            Err(e) => println!("   ❌ Error: {}", e),
        }
    }
}

fn demo_ioc_scanning() {
    println!("🔎 4. IOC System Scanning");
    println!("─────────────────────────");

    let ioc_scanner = IOCScanner::new();

    let stats = ioc_scanner.get_scan_stats();
    println!("📊 Scan configuration:");
    for (key, value) in stats {
        println!("   • {}: {}", key, value);
    }

    println!("\n🔍 Scanning for indicators...");

    let iocs = vec![
        "malware.exe".to_string(),
        "192.168.1.100".to_string(),
        "mimikatz".to_string(),
    ];

    match ioc_scanner.scan_system(&iocs) {
        Ok(matches) => {
            println!("   Found {} IOC matches", matches.len());
            for m in matches.iter().take(3) {
                println!("      • IOC: {}", m.ioc);
                println!("        Location: {}", m.location);
                println!("        Type: {:?}", m.artifact_type);
            }
        }
        Err(e) => println!("   ❌ Error: {}", e),
    }
}

fn demo_timeline_analysis() {
    println!("📅 5. Timeline Analysis");
    println!("──────────────────────");

    let mut platform = ThreatHuntingPlatform::new();
    let session_id = platform.create_hunt_session(
        "Timeline Analysis Demo".to_string(),
        "Demonstrating event correlation".to_string(),
    );

    println!("📋 Created hunt session: {}", session_id);

    // Simulate findings
    println!("\n🔍 Simulating attack chain...");

    // Initial access
    let _ = platform.sigma_detect(
        session_id,
        "CommandLine=powershell.exe DownloadString",
        vec!["sigma_002".to_string()],
    );

    // Credential access
    let _ = platform.sigma_detect(
        session_id,
        "CommandLine=sekurlsa::logonpasswords",
        vec!["sigma_001".to_string()],
    );

    // Lateral movement
    let _ = platform.sigma_detect(
        session_id,
        "DestinationPort=445 DestinationPath=\\\\*\\ADMIN$",
        vec!["sigma_003".to_string()],
    );

    println!("\n📊 Analyzing timeline...");

    match platform.analyze_timeline(
        session_id,
        Utc::now() - chrono::Duration::hours(1),
        Utc::now(),
    ) {
        Ok(findings) => {
            println!("   Found {} timeline correlations", findings.len());
            for finding in findings {
                println!("\n   🔗 Correlation: {}", finding.description);
                println!("      Severity: {:?}", finding.severity);
                println!("      Confidence: {:.0}%", finding.confidence_score * 100.0);
                println!("      MITRE Tactics: {:?}", finding.mitre_tactics);
            }
        }
        Err(e) => println!("   ❌ Error: {}", e),
    }
}

fn demo_threat_profiling() {
    println!("👤 6. Threat Actor Profiling");
    println!("────────────────────────────");

    let profiler = ThreatActorProfiler::new();

    println!("📋 Known threat actors:");
    for actor in profiler.list_known_actors() {
        println!("   • {}", actor);
    }

    println!("\n🔍 Searching by country...");
    let russian_actors = profiler.search_by_country("Russia");
    println!("   Russian-attributed actors: {:?}", russian_actors);

    println!("\n🔍 Searching by sector...");
    let financial_actors = profiler.search_by_sector("Financial");
    println!("   Financial sector threats: {:?}", financial_actors);

    println!("\n🎯 Getting actor details...");
    if let Some(info) = profiler.get_actor_info("APT28") {
        println!("   Actor: {}", info.name);
        println!("   Aliases: {}", info.aliases.join(", "));
        println!("   Country: {}", info.country.unwrap_or("Unknown".to_string()));
        println!("   Motivation: {}", info.motivation.join(", "));
        println!("   Signature TTPs:");
        for ttp in info.signature_ttps.iter().take(3) {
            println!("      • {}", ttp);
        }
    }
}

fn run_full_hunt() {
    println!("🚀 Full Threat Hunt Simulation");
    println!("===============================\n");

    let mut platform = ThreatHuntingPlatform::new();

    // Create hunt session
    let session_id = platform.create_hunt_session(
        "APT Investigation".to_string(),
        "Investigating potential APT activity based on alerts".to_string(),
    );

    println!("✅ Created hunt session: {}\n", session_id);

    // Step 1: YARA scanning
    println!("Step 1: Scanning for malware patterns...");
    std::fs::write("/tmp/test_malware.txt", "MZ header malicious payload").ok();
    let _ = platform.yara_scan(session_id, "/tmp", vec![]);
    std::fs::remove_file("/tmp/test_malware.txt").ok();

    // Step 2: Sigma detection
    println!("Step 2: Analyzing security events...");
    let _ = platform.sigma_detect(
        session_id,
        "CommandLine=sekurlsa::logonpasswords process=mimikatz.exe",
        vec![],
    );

    // Step 3: Custom queries
    println!("Step 3: Executing hunt queries...");
    let _ = platform.execute_hunt_query(session_id, "HUNT processes WHERE user = SYSTEM");

    // Step 4: IOC scanning
    println!("Step 4: Scanning for IOCs...");
    let _ = platform.scan_iocs(
        session_id,
        vec!["192.168.1.100".to_string(), "malware.exe".to_string()],
    );

    // Step 5: Timeline analysis
    println!("Step 5: Analyzing attack timeline...");
    let correlations = platform.analyze_timeline(
        session_id,
        Utc::now() - chrono::Duration::hours(24),
        Utc::now(),
    ).unwrap_or_default();

    println!("   Found {} timeline correlations", correlations.len());

    // Step 6: Threat profiling
    println!("Step 6: Profiling threat actor...");
    match platform.profile_threat_actor(session_id) {
        Ok(profile) => {
            println!("   Attribution: {}", profile.name);
            println!("   Confidence: {:.0}%", profile.confidence * 100.0);
            println!("   Attribution Score: {:.2}", profile.attribution_score);
        }
        Err(_) => println!("   Unable to profile threat actor"),
    }

    // Get session statistics
    println!("\n📊 Hunt Session Statistics:");
    match platform.get_session_stats(session_id) {
        Ok(stats) => {
            println!("   Total Findings: {}", stats.total_findings);
            println!("   Queries Executed: {}", stats.queries_executed);
            println!("   IOCs Searched: {}", stats.iocs_searched);
            println!("   Highest Severity: {:?}", stats.highest_severity);

            println!("\n   Severity Distribution:");
            for (severity, count) in &stats.severity_distribution {
                println!("      {}: {}", severity, count);
            }

            println!("\n   Finding Types:");
            for (ftype, count) in &stats.finding_type_distribution {
                println!("      {}: {}", ftype, count);
            }
        }
        Err(e) => println!("   ❌ Error: {}", e),
    }

    // Close session
    let _ = platform.close_session(session_id);
    println!("\n✅ Hunt session complete!");
}
