//! SynOS Deception Technology CLI
//!
//! Command-line interface for deception asset deployment and management

use deception::*;
use deception::honey_tokens::{HoneyTokenGenerator, HoneyTokenValidator};
use deception::credential_deception::{CredentialDeceptionManager, CredentialUsageMonitor};
use deception::network_decoys::{DecoyDeploymentManager, ScanDetector};
use deception::ai_interaction::AIInteractionEngine;

fn main() {
    println!("🕷️  SynOS Deception Technology Framework");
    println!("==========================================\n");

    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        print_usage();
        return;
    }

    match args[1].as_str() {
        "demo" => run_demo(),
        "tokens" => demo_honey_tokens(),
        "credentials" => demo_fake_credentials(),
        "decoys" => demo_network_decoys(),
        "ai" => demo_ai_interaction(),
        "deploy" => demo_full_deployment(),
        _ => print_usage(),
    }
}

fn print_usage() {
    println!("Usage: synos-deception <command>");
    println!("\nCommands:");
    println!("  demo         - Run comprehensive demo");
    println!("  tokens       - Demonstrate honey token generation");
    println!("  credentials  - Demonstrate fake credential deployment");
    println!("  decoys       - Demonstrate network decoy deployment");
    println!("  ai           - Demonstrate AI-powered interaction");
    println!("  deploy       - Full deception deployment simulation");
}

fn run_demo() {
    println!("🎯 Running Comprehensive Deception Demo\n");

    demo_honey_tokens();
    println!();
    demo_fake_credentials();
    println!();
    demo_network_decoys();
    println!();
    demo_ai_interaction();
    println!();

    println!("✅ Comprehensive demo complete!");
}

fn demo_honey_tokens() {
    println!("🍯 1. Honey Token Generation");
    println!("────────────────────────────");

    let generator = HoneyTokenGenerator::new("tracking.synos.io".to_string());

    // Generate various token types
    match generator.generate_api_key("stripe") {
        Ok((token, asset)) => {
            println!("✅ API Key Generated:");
            println!("   Token: {}...", &token[..20]);
            println!("   Asset: {}", asset.name);
            println!("   Location: {}", asset.location);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    match generator.generate_aws_key() {
        Ok((access_key, secret_key, asset)) => {
            println!("\n✅ AWS Credentials Generated:");
            println!("   Access Key: {}", access_key);
            println!("   Secret Key: {}...", &secret_key[..20]);
            println!("   Deployment: {}", asset.location);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    match generator.generate_jwt_token("admin") {
        Ok((jwt, asset)) => {
            println!("\n✅ JWT Token Generated:");
            println!("   Token: {}...", &jwt[..50]);
            println!("   Subject: admin");
            println!("   Storage: {}", asset.location);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    match generator.generate_canary_token("Sensitive Document") {
        Ok((url, asset)) => {
            println!("\n✅ Canary Token Generated:");
            println!("   Tracking URL: {}", url);
            println!("   Description: {}", asset.description);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Token validation demo
    println!("\n🔍 Token Validation:");
    let mut validator = HoneyTokenValidator::new();
    let test_token = "sk_live_fake_token_12345";
    let asset_id = uuid::Uuid::new_v4();

    use sha2::{Sha256, Digest};
    let mut hasher = Sha256::new();
    hasher.update(test_token.as_bytes());
    let hash = format!("{:x}", hasher.finalize());

    validator.register_token(hash, asset_id);

    if let Some(alert) = validator.validate_token_usage(test_token) {
        println!("   {}", alert);
    }
}

fn demo_fake_credentials() {
    println!("🔐 2. Fake Credential Deployment");
    println!("─────────────────────────────────");

    let mut manager = CredentialDeceptionManager::new();

    // Generate SSH credentials
    match manager.generate_ssh_credential("prod-server-01") {
        Ok((cred, asset)) => {
            println!("✅ SSH Credentials Created:");
            println!("   Username: {}", cred.username);
            println!("   Password: {}...", &cred.password[..8]);
            println!("   Target: {}", cred.target_system);
            println!("   Deployment: {}", manager.render_deployment(&cred));
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Generate database credentials
    match manager.generate_db_credential("production_db", "postgres") {
        Ok((cred, asset)) => {
            println!("\n✅ Database Credentials Created:");
            println!("   Username: {}", cred.username);
            println!("   Password: {}...", &cred.password[..8]);
            println!("   Connection: {}", manager.render_deployment(&cred));
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Generate cloud credentials
    match manager.generate_cloud_credential("aws") {
        Ok((cred, asset)) => {
            println!("\n✅ AWS Credentials Created:");
            println!("   Access Key: {}", cred.username);
            println!("   Secret Key: {}...", &cred.password[..15]);
            println!("   Deployment: {}", cred.deployment_location);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Credential detection
    println!("\n🔍 Credential Detection:");
    let fake_creds = manager.list_credentials();
    if let Some(first_cred) = fake_creds.first() {
        if let Some(detected) = manager.is_fake_credential(&first_cred.username, &first_cred.password) {
            println!("   ⚠️  Fake credential detected!");
            println!("   Type: {:?}", detected.credential_type);
            println!("   Target: {}", detected.target_system);
        }
    }

    // Usage monitoring
    let mut monitor = CredentialUsageMonitor::new();
    monitor.record_usage(
        "admin_1234".to_string(),
        "10.0.0.5".to_string(),
        "ssh://prod-server".to_string(),
        false,
    );

    println!("\n📊 Usage Monitoring:");
    println!("   Suspicious attempts: {}", monitor.get_suspicious_usage().len());
}

fn demo_network_decoys() {
    println!("🌐 3. Network Decoy Deployment");
    println!("──────────────────────────────");

    let mut manager = DecoyDeploymentManager::new();

    // Deploy SSH decoy
    match manager.deploy_ssh_decoy("192.168.1.50") {
        Ok((decoy, asset)) => {
            println!("✅ SSH Honeypot Deployed:");
            println!("   IP: {}", decoy.listen_ip);
            println!("   Port: {}", decoy.listen_port);
            println!("   Banner: {}", decoy.banner.as_ref().unwrap().trim());
            println!("   Version: {}", decoy.service_version);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Deploy web decoy
    match manager.deploy_web_decoy("192.168.1.51", 8080, false) {
        Ok((decoy, asset)) => {
            println!("\n✅ Web Honeypot Deployed:");
            println!("   URL: http://{}:{}", decoy.listen_ip, decoy.listen_port);
            println!("   Server: {}", decoy.service_version);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Deploy database decoy
    match manager.deploy_database_decoy("192.168.1.52", "postgres") {
        Ok((decoy, asset)) => {
            println!("\n✅ Database Honeypot Deployed:");
            println!("   Address: {}:{}", decoy.listen_ip, decoy.listen_port);
            println!("   Type: PostgreSQL");
            println!("   Asset ID: {}", asset.id);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Deploy SMB decoy
    match manager.deploy_smb_decoy("192.168.1.53", "Finance") {
        Ok((decoy, asset)) => {
            println!("\n✅ SMB File Share Honeypot Deployed:");
            println!("   Share: \\\\{}\\Finance", decoy.listen_ip);
            println!("   Port: {}", decoy.listen_port);
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    // Scan detection
    let mut detector = ScanDetector::new();
    detector.record_scan(
        "10.0.0.5".to_string(),
        vec![22, 80, 443, 3389, 445, 5432],
        vec!["ssh_decoy".to_string(), "web_decoy".to_string(), "db_decoy".to_string()],
    );

    detector.record_scan(
        "10.0.0.5".to_string(),
        (1..=1000).collect(),
        vec!["ssh_decoy".to_string()],
    );

    println!("\n🔍 Scan Detection:");
    let alerts = detector.detect_reconnaissance();
    for alert in alerts {
        println!("   {}", alert);
    }

    println!("\n📊 Deployed Decoys: {}", manager.list_decoys().len());
}

fn demo_ai_interaction() {
    println!("🤖 4. AI-Powered Interaction");
    println!("────────────────────────────");

    let mut ai_engine = AIInteractionEngine::new();

    // Simulate SSH interaction
    let ssh_interaction = DeceptionInteraction::new(
        uuid::Uuid::new_v4(),
        "10.0.0.5".to_string(),
        12345,
        InteractionType::Authentication,
        "SSH login attempt".to_string(),
    );

    println!("✅ SSH Interaction:");
    let response = ai_engine.generate_response(&ssh_interaction, "login admin");
    println!("   Input: login admin");
    println!("   Response: {}", response.text.trim());
    println!("   Delay: {}ms", response.delay_ms);
    println!("   Believability: {:.1}%", response.believability_score * 100.0);

    // Simulate multiple interactions
    for i in 0..15 {
        let interaction = DeceptionInteraction::new(
            uuid::Uuid::new_v4(),
            "10.0.0.5".to_string(),
            12345 + i,
            InteractionType::Access,
            format!("File access attempt {}", i),
        );

        ai_engine.generate_response(&interaction, "ls /etc/shadow");
    }

    // Threat analysis
    let analysis = ai_engine.analyze_interaction_pattern("10.0.0.5");
    println!("\n🔍 Threat Analysis:");
    println!("   Source IP: {}", analysis.source_ip);
    println!("   Total Interactions: {}", analysis.total_interactions);
    println!("   Sophistication: {}", analysis.sophistication_level);
    println!("   Threat Level: {}", analysis.threat_level);
    println!("   Persistence Score: {:.2}", analysis.persistence_score);

    println!("\n💡 Recommendations:");
    for rec in analysis.recommendations {
        println!("   {}", rec);
    }

    // Believable errors
    println!("\n⚠️  Believable Error Messages:");
    println!("   SSH: {}", ai_engine.generate_believable_error("ssh").trim());
    println!("   HTTP: {}", ai_engine.generate_believable_error("http").trim());
    println!("   Database: {}", ai_engine.generate_believable_error("database").trim());

    let stats = ai_engine.get_statistics();
    println!("\n📊 AI Engine Stats:");
    for (key, value) in stats {
        println!("   {}: {}", key, value);
    }
}

fn demo_full_deployment() {
    println!("🚀 5. Full Deception Deployment");
    println!("────────────────────────────────");

    let mut deception_manager = DeceptionManager::new();

    // Deploy honey tokens
    let generator = HoneyTokenGenerator::new("tracking.synos.io".to_string());

    if let Ok((_, asset)) = generator.generate_api_key("production") {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed API Key Honey Token (ID: {})", id);
    }

    if let Ok((_, _, asset)) = generator.generate_aws_key() {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed AWS Credential Honey Token (ID: {})", id);
    }

    // Deploy fake credentials
    let mut cred_manager = CredentialDeceptionManager::new();

    if let Ok((_, asset)) = cred_manager.generate_ssh_credential("production-server") {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed SSH Fake Credential (ID: {})", id);
    }

    if let Ok((_, asset)) = cred_manager.generate_db_credential("prod_db", "postgres") {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed Database Fake Credential (ID: {})", id);
    }

    // Deploy network decoys
    let mut decoy_manager = DecoyDeploymentManager::new();

    if let Ok((_, asset)) = decoy_manager.deploy_ssh_decoy("192.168.1.50") {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed SSH Network Decoy (ID: {})", id);
    }

    if let Ok((_, asset)) = decoy_manager.deploy_web_decoy("192.168.1.51", 80, false) {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed Web Network Decoy (ID: {})", id);
    }

    if let Ok((_, asset)) = decoy_manager.deploy_database_decoy("192.168.1.52", "postgres") {
        let id = deception_manager.deploy_asset(asset);
        println!("✅ Deployed Database Network Decoy (ID: {})", id);
    }

    // Simulate interactions
    println!("\n🎭 Simulating Attacker Interactions...");

    let asset_ids: Vec<(uuid::Uuid, String)> = deception_manager.list_assets()
        .iter()
        .take(3)
        .map(|a| (a.id, a.name.clone()))
        .collect();

    for (i, (asset_id, asset_name)) in asset_ids.iter().enumerate() {
        let interaction = DeceptionInteraction::new(
            *asset_id,
            "10.0.0.5".to_string(),
            12345 + i as u16,
            InteractionType::Access,
            format!("Interaction with {}", asset_name),
        );

        deception_manager.record_interaction(interaction).unwrap();
        println!("   📝 Recorded interaction with {}", asset_name);
    }

    // Statistics
    let stats = deception_manager.get_statistics();
    println!("\n📊 Deployment Statistics:");
    println!("   Total Assets: {}", stats.total_assets);
    println!("   Total Interactions: {}", stats.total_interactions);

    println!("\n   Severity Distribution:");
    for (severity, count) in &stats.severity_counts {
        println!("      {}: {}", severity, count);
    }

    println!("\n   Interaction Types:");
    for (itype, count) in &stats.interaction_type_counts {
        println!("      {}: {}", itype, count);
    }

    // High severity interactions
    let high_severity = deception_manager.get_high_severity_interactions();
    if !high_severity.is_empty() {
        println!("\n⚠️  High Severity Interactions:");
        for interaction in high_severity.iter().take(3) {
            println!("      {} from {} - {:?}",
                interaction.details,
                interaction.source_ip,
                interaction.severity
            );
        }
    }

    println!("\n✅ Full deployment complete - {} assets active!", stats.total_assets);
}
