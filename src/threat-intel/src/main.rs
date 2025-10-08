//! SynOS Threat Intelligence CLI

use threat_intel::*;
use threat_intel::misp_connector::MISPConnector;
use threat_intel::otx_connector::OTXConnector;
use threat_intel::abusech_connector::AbuseCHConnector;
use std::env;

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        print_usage();
        return Ok(());
    }

    let mut manager = IOCManager::new();

    match args[1].as_str() {
        "misp" => {
            if args.len() < 4 {
                eprintln!("Usage: synos-threat-intel misp <url> <api-key> [limit]");
                return Ok(());
            }
            fetch_misp(&args[2], &args[3], &mut manager)?;
        },
        "otx" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-threat-intel otx <api-key> [limit]");
                return Ok(());
            }
            fetch_otx(&args[2], &mut manager)?;
        },
        "abusech" => {
            fetch_abusech(&mut manager)?;
        },
        "search" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-threat-intel search <value>");
                return Ok(());
            }
            search_iocs(&args[2], &manager);
        },
        "stats" => {
            print_stats(&manager);
        },
        "correlate" => {
            manager.auto_correlate();
            println!("Auto-correlation complete");
            print_stats(&manager);
        },
        "demo" => {
            run_demo()?;
        },
        _ => {
            print_usage();
        }
    }

    Ok(())
}

fn print_usage() {
    println!("SynOS Threat Intelligence Feed Integration\n");
    println!("Usage:");
    println!("  synos-threat-intel misp <url> <api-key> [limit]  - Fetch from MISP");
    println!("  synos-threat-intel otx <api-key> [limit]         - Fetch from AlienVault OTX");
    println!("  synos-threat-intel abusech                       - Fetch from abuse.ch feeds");
    println!("  synos-threat-intel search <value>                - Search IOCs");
    println!("  synos-threat-intel stats                         - Show statistics");
    println!("  synos-threat-intel correlate                     - Auto-correlate IOCs");
    println!("  synos-threat-intel demo                          - Run demonstration");
}

fn fetch_misp(url: &str, api_key: &str, manager: &mut IOCManager) -> Result<()> {
    println!("Connecting to MISP at {}...", url);

    let connector = MISPConnector::new(url.to_string(), api_key.to_string());

    // In production, this would fetch real events
    println!("Fetching recent events...");
    println!("(Demo mode: would fetch from MISP API)");

    // Demo: Create sample IOCs
    let mut ioc = IOC::new(
        IOCType::IPAddress,
        "192.0.2.1".to_string(),
        "MISP".to_string()
    );
    ioc.severity = ThreatSeverity::High;
    ioc.tags.push("apt28".to_string());
    ioc.description = "Known APT28 C2 server".to_string();

    manager.add_ioc(ioc);

    println!("✓ Fetched and processed MISP events");
    Ok(())
}

fn fetch_otx(api_key: &str, manager: &mut IOCManager) -> Result<()> {
    println!("Connecting to AlienVault OTX...");

    let connector = OTXConnector::new(api_key.to_string());

    // In production, this would fetch real pulses
    println!("Fetching subscribed pulses...");
    println!("(Demo mode: would fetch from OTX API)");

    // Demo: Create sample IOCs
    let mut ioc = IOC::new(
        IOCType::Domain,
        "malware.example.com".to_string(),
        "OTX".to_string()
    );
    ioc.severity = ThreatSeverity::Medium;
    ioc.tags.push("malware".to_string());
    ioc.tags.push("phishing".to_string());
    ioc.description = "Phishing campaign infrastructure".to_string();

    manager.add_ioc(ioc);

    println!("✓ Fetched and processed OTX pulses");
    Ok(())
}

fn fetch_abusech(manager: &mut IOCManager) -> Result<()> {
    println!("Connecting to abuse.ch feeds...");

    let connector = AbuseCHConnector::new();

    // In production, this would fetch real feeds
    println!("Fetching URLhaus, Feodo, and SSL Blacklist...");
    println!("(Demo mode: would fetch from abuse.ch APIs)");

    // Demo: Create sample IOCs
    let mut ioc1 = IOC::new(
        IOCType::URL,
        "http://malicious.example.com/payload.exe".to_string(),
        "abuse.ch/URLhaus".to_string()
    );
    ioc1.severity = ThreatSeverity::Critical;
    ioc1.tags.push("malware".to_string());
    ioc1.tags.push("payload".to_string());
    ioc1.confidence = 0.9;

    let mut ioc2 = IOC::new(
        IOCType::IPAddress,
        "203.0.113.42".to_string(),
        "abuse.ch/Feodo".to_string()
    );
    ioc2.severity = ThreatSeverity::High;
    ioc2.tags.push("c2".to_string());
    ioc2.tags.push("botnet".to_string());
    ioc2.confidence = 0.9;

    manager.add_ioc(ioc1);
    manager.add_ioc(ioc2);

    println!("✓ Fetched and processed abuse.ch feeds");
    Ok(())
}

fn search_iocs(value: &str, manager: &IOCManager) {
    println!("\nSearching for: {}", value);

    let results = manager.search_by_value(value);

    if results.is_empty() {
        println!("No IOCs found matching '{}'", value);
        return;
    }

    println!("Found {} IOC(s):\n", results.len());

    for ioc in results {
        println!("  Type:     {:?}", ioc.ioc_type);
        println!("  Value:    {}", ioc.value);
        println!("  Severity: {:?}", ioc.severity);
        println!("  Source:   {}", ioc.source);
        println!("  Tags:     {}", ioc.tags.join(", "));
        println!("  Desc:     {}", ioc.description);
        println!();
    }
}

fn print_stats(manager: &IOCManager) {
    let stats = manager.get_stats();

    println!("\n=== Threat Intelligence Statistics ===");
    println!("\nTotal IOCs: {}", stats.total_iocs);
    println!("Total Correlations: {}", stats.total_correlations);

    println!("\nBy Type:");
    for (ioc_type, count) in &stats.by_type {
        println!("  {}: {}", ioc_type, count);
    }

    println!("\nBy Severity:");
    for (severity, count) in &stats.by_severity {
        println!("  {}: {}", severity, count);
    }

    println!("\nBy Source:");
    for (source, count) in &stats.by_source {
        println!("  {}: {}", source, count);
    }
    println!();
}

fn run_demo() -> Result<()> {
    println!("\n=== SynOS Threat Intelligence Demo ===\n");

    let mut manager = IOCManager::new();

    // Create diverse IOCs
    println!("Creating sample threat intelligence...");

    let mut ioc1 = IOC::new(
        IOCType::IPAddress,
        "198.51.100.10".to_string(),
        "MISP".to_string()
    );
    ioc1.severity = ThreatSeverity::Critical;
    ioc1.tags.push("apt29".to_string());
    ioc1.tags.push("c2".to_string());
    ioc1.description = "APT29 Command and Control server".to_string();
    ioc1.confidence = 0.95;

    let mut ioc2 = IOC::new(
        IOCType::Domain,
        "apt29-infrastructure.example.com".to_string(),
        "MISP".to_string()
    );
    ioc2.severity = ThreatSeverity::Critical;
    ioc2.tags.push("apt29".to_string());
    ioc2.tags.push("infrastructure".to_string());
    ioc2.description = "APT29 infrastructure domain".to_string();
    ioc2.confidence = 0.90;

    let mut ioc3 = IOC::new(
        IOCType::FileHash,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855".to_string(),
        "OTX".to_string()
    );
    ioc3.severity = ThreatSeverity::High;
    ioc3.tags.push("malware".to_string());
    ioc3.tags.push("ransomware".to_string());
    ioc3.description = "Ransomware payload hash".to_string();
    ioc3.confidence = 0.85;

    let mut ioc4 = IOC::new(
        IOCType::URL,
        "http://phishing.example.com/login".to_string(),
        "abuse.ch/URLhaus".to_string()
    );
    ioc4.severity = ThreatSeverity::Medium;
    ioc4.tags.push("phishing".to_string());
    ioc4.description = "Credential harvesting page".to_string();
    ioc4.confidence = 0.80;

    manager.add_ioc(ioc1);
    manager.add_ioc(ioc2);
    manager.add_ioc(ioc3);
    manager.add_ioc(ioc4);

    println!("✓ Created 4 sample IOCs\n");

    // Auto-correlate
    println!("Running auto-correlation...");
    manager.auto_correlate();
    println!("✓ Correlation complete\n");

    // Show stats
    print_stats(&manager);

    // Search demo
    println!("=== Search Demo ===");
    search_iocs("apt29", &manager);

    // Show correlations
    println!("=== Correlation Demo ===");
    for (hash, ioc) in manager.get_iocs() {
        let related = manager.get_related_iocs(hash);
        if !related.is_empty() {
            println!("\nIOC: {} ({})", ioc.value, ioc.source);
            println!("Related IOCs:");
            for (related_ioc, corr) in related {
                println!("  → {} ({:?}, confidence: {:.2})",
                    related_ioc.value,
                    corr.correlation_type,
                    corr.confidence
                );
            }
        }
    }

    println!("\n=== Demo Complete ===\n");
    Ok(())
}
