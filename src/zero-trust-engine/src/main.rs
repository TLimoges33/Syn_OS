//! SynOS Zero-Trust Policy Engine CLI

use zero_trust::*;
use serde_json;
use chrono::Utc;
use uuid::Uuid;

#[tokio::main]
async fn main() -> Result<()> {
    // tracing_subscriber::fmt::init(); // Commented out - not a critical dependency

    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        print_usage();
        return Ok(());
    }

    match args[1].as_str() {
        "evaluate" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-zt-engine evaluate <context.json>");
                return Ok(());
            }
            evaluate_access_request(&args[2]).await?;
        },
        "create-policy" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-zt-engine create-policy <policy.json>");
                return Ok(());
            }
            create_policy(&args[2]).await?;
        },
        "create-segment" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-zt-engine create-segment <segment.json>");
                return Ok(());
            }
            create_segment(&args[2]).await?;
        },
        "demo" => {
            run_demo().await?;
        },
        "session" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-zt-engine session <command>");
                return Ok(());
            }
            match args[2].as_str() {
                "create" => create_session().await?,
                "list" => list_sessions().await?,
                _ => eprintln!("Unknown session command: {}", args[2]),
            }
        },
        _ => {
            print_usage();
        }
    }

    Ok(())
}

fn print_usage() {
    println!("SynOS Zero-Trust Policy Engine\n");
    println!("Usage:");
    println!("  synos-zt-engine evaluate <context.json>    - Evaluate access request");
    println!("  synos-zt-engine create-policy <policy.json> - Create policy rule");
    println!("  synos-zt-engine create-segment <segment.json> - Create micro-segment");
    println!("  synos-zt-engine session create            - Create new session");
    println!("  synos-zt-engine session list              - List active sessions");
    println!("  synos-zt-engine demo                      - Run demonstration");
}

async fn evaluate_access_request(context_file: &str) -> Result<()> {
    let content = std::fs::read_to_string(context_file)
        .map_err(|e| ZeroTrustError::InvalidContext(e.to_string()))?;

    let context: AccessContext = serde_json::from_str(&content)
        .map_err(|e| ZeroTrustError::InvalidContext(e.to_string()))?;

    let mut engine = ZeroTrustEngine::new();

    // Load policies (in production, load from database/config)
    load_default_policies(&mut engine);

    let decision = engine.evaluate_access(&context)?;

    println!("\n=== Zero-Trust Access Decision ===");
    println!("Decision: {:?}", decision.decision);
    println!("Trust Score: {:.1}", decision.trust_score);
    println!("Threat Level: {}", decision.threat_level);
    println!("Session ID: {}", decision.session_id);
    println!("\nReasoning:");
    for reason in &decision.reasoning {
        println!("  - {}", reason);
    }
    if let Some(rule) = &decision.matched_rule {
        println!("\nMatched Rule: {}", rule);
    }
    println!("\n{}", "=".repeat(35));

    Ok(())
}

async fn create_policy(policy_file: &str) -> Result<()> {
    let content = std::fs::read_to_string(policy_file)
        .map_err(|e| ZeroTrustError::InvalidContext(e.to_string()))?;

    let policy: PolicyRule = serde_json::from_str(&content)
        .map_err(|e| ZeroTrustError::InvalidContext(e.to_string()))?;

    println!("Created policy: {} (priority: {})", policy.name, policy.priority);
    println!("Action: {:?}", policy.action);
    println!("Min trust score: {}", policy.min_trust_score);
    println!("Requires MFA: {}", policy.require_mfa);

    Ok(())
}

async fn create_segment(segment_file: &str) -> Result<()> {
    let content = std::fs::read_to_string(segment_file)
        .map_err(|e| ZeroTrustError::InvalidContext(e.to_string()))?;

    let segment: MicroSegment = serde_json::from_str(&content)
        .map_err(|e| ZeroTrustError::InvalidContext(e.to_string()))?;

    println!("Created micro-segment: {}", segment.name);
    println!("Network: {}", segment.network_cidr);
    println!("Isolation level: {}", segment.isolation_level);
    println!("Ingress rules: {}", segment.ingress_rules.len());
    println!("Egress rules: {}", segment.egress_rules.len());

    Ok(())
}

async fn create_session() -> Result<()> {
    let identity = Identity::new("demo_user".to_string(), "device_fingerprint_xyz".to_string());

    let mut engine = ZeroTrustEngine::new();
    let session_id = engine.update_session(identity.clone());

    println!("Created session: {}", session_id);
    println!("User: {}", identity.username);
    println!("Trust score: {:.1}", identity.trust_score);
    println!("MFA verified: {}", identity.mfa_verified);

    Ok(())
}

async fn list_sessions() -> Result<()> {
    println!("Active Zero-Trust Sessions:\n");
    // In production, load from shared state/database
    println!("No active sessions (demo mode)");

    Ok(())
}

async fn run_demo() -> Result<()> {
    println!("\n=== SynOS Zero-Trust Engine Demo ===\n");

    let mut engine = ZeroTrustEngine::new();

    // Demo policies
    load_default_policies(&mut engine);

    // Demo micro-segments
    create_demo_segments(&mut engine);

    // Demo scenarios
    println!("Scenario 1: Admin access to production database");
    let admin_identity = Identity {
        id: Uuid::new_v4(),
        username: "admin@synos.dev".to_string(),
        roles: vec!["admin".to_string(), "dba".to_string()],
        groups: vec!["operations".to_string()],
        mfa_verified: true,
        device_fingerprint: "trusted_device_001".to_string(),
        last_verified: Utc::now(),
        trust_score: 95.0,
        attributes: std::collections::HashMap::new(),
    };

    let context1 = AccessContext {
        identity: admin_identity,
        source_ip: "10.0.1.100".parse().unwrap(),
        destination_ip: "10.0.10.50".parse().unwrap(),
        destination_port: 5432,
        protocol: "postgresql".to_string(),
        resource_type: "database".to_string(),
        resource_id: "prod-db-01".to_string(),
        action: "SELECT".to_string(),
        time: Utc::now(),
        threat_indicators: vec![],
    };

    let decision1 = engine.evaluate_access(&context1)?;
    print_decision("Scenario 1", &decision1);

    // Scenario 2: User with suspicious behavior
    println!("\nScenario 2: User with suspicious login pattern");
    let suspicious_identity = Identity {
        id: Uuid::new_v4(),
        username: "user@synos.dev".to_string(),
        roles: vec!["developer".to_string()],
        groups: vec!["engineering".to_string()],
        mfa_verified: false,
        device_fingerprint: "unknown_device_999".to_string(),
        last_verified: Utc::now() - chrono::Duration::minutes(30),
        trust_score: 35.0,
        attributes: std::collections::HashMap::new(),
    };

    let context2 = AccessContext {
        identity: suspicious_identity,
        source_ip: "203.0.113.45".parse().unwrap(),
        destination_ip: "10.0.10.50".parse().unwrap(),
        destination_port: 5432,
        protocol: "postgresql".to_string(),
        resource_type: "database".to_string(),
        resource_id: "prod-db-01".to_string(),
        action: "DELETE".to_string(),
        time: Utc::now(),
        threat_indicators: vec![
            ThreatIndicator {
                indicator_type: "anomalous_login".to_string(),
                severity: "HIGH".to_string(),
                description: "Login from new geographic location".to_string(),
                confidence: 0.85,
                detected_at: Utc::now(),
            },
            ThreatIndicator {
                indicator_type: "unusual_time".to_string(),
                severity: "MEDIUM".to_string(),
                description: "Access outside normal hours".to_string(),
                confidence: 0.70,
                detected_at: Utc::now(),
            },
        ],
    };

    let decision2 = engine.evaluate_access(&context2)?;
    print_decision("Scenario 2", &decision2);

    // Scenario 3: Micro-segmentation check
    println!("\nScenario 3: Cross-segment communication");
    let segment_decision = engine.evaluate_segment_access(
        "web-tier",
        "database-tier",
        "postgresql",
        5432
    )?;
    println!("Decision: {:?}", segment_decision);

    println!("\n{}", "=".repeat(40));
    println!("Demo completed successfully!");
    println!("{}\n", "=".repeat(40));

    Ok(())
}

fn load_default_policies(engine: &mut ZeroTrustEngine) {
    // Policy 1: Admin database access
    engine.add_policy(PolicyRule {
        id: "policy-admin-db".to_string(),
        name: "Admin Database Access".to_string(),
        priority: 10,
        conditions: vec![
            PolicyCondition {
                field: "identity.role".to_string(),
                operator: ConditionOperator::Equals,
                value: "admin".to_string(),
            },
            PolicyCondition {
                field: "resource_type".to_string(),
                operator: ConditionOperator::Equals,
                value: "database".to_string(),
            },
        ],
        action: PolicyAction::Allow,
        min_trust_score: 80.0,
        require_mfa: true,
        allowed_locations: vec!["US".to_string(), "EU".to_string()],
        time_restrictions: None,
    });

    // Policy 2: Developer read-only access
    engine.add_policy(PolicyRule {
        id: "policy-dev-readonly".to_string(),
        name: "Developer Read-Only Access".to_string(),
        priority: 20,
        conditions: vec![
            PolicyCondition {
                field: "identity.role".to_string(),
                operator: ConditionOperator::Equals,
                value: "developer".to_string(),
            },
            PolicyCondition {
                field: "action".to_string(),
                operator: ConditionOperator::Equals,
                value: "SELECT".to_string(),
            },
        ],
        action: PolicyAction::Allow,
        min_trust_score: 60.0,
        require_mfa: false,
        allowed_locations: vec![],
        time_restrictions: Some(TimeRestriction {
            allowed_days: vec!["Monday".to_string(), "Tuesday".to_string(), "Wednesday".to_string(), "Thursday".to_string(), "Friday".to_string()],
            allowed_hours_start: 9,
            allowed_hours_end: 18,
        }),
    });

    // Policy 3: Block destructive operations with low trust
    engine.add_policy(PolicyRule {
        id: "policy-block-destructive".to_string(),
        name: "Block Destructive Operations".to_string(),
        priority: 5,
        conditions: vec![
            PolicyCondition {
                field: "action".to_string(),
                operator: ConditionOperator::Contains,
                value: "DELETE".to_string(),
            },
        ],
        action: PolicyAction::Deny,
        min_trust_score: 90.0,
        require_mfa: true,
        allowed_locations: vec![],
        time_restrictions: None,
    });
}

fn create_demo_segments(engine: &mut ZeroTrustEngine) {
    // Web tier segment
    engine.add_segment(MicroSegment {
        id: "web-tier".to_string(),
        name: "Web Application Tier".to_string(),
        network_cidr: "10.0.1.0/24".to_string(),
        allowed_protocols: vec!["https".to_string(), "http".to_string()],
        allowed_ports: vec![80, 443],
        isolation_level: "MEDIUM".to_string(),
        member_identities: vec![],
        ingress_rules: vec![
            SegmentRule {
                source_segment: None,
                destination_segment: Some("web-tier".to_string()),
                protocol: "https".to_string(),
                port_range: (443, 443),
                action: PolicyAction::Allow,
            },
        ],
        egress_rules: vec![
            SegmentRule {
                source_segment: Some("web-tier".to_string()),
                destination_segment: Some("database-tier".to_string()),
                protocol: "postgresql".to_string(),
                port_range: (5432, 5432),
                action: PolicyAction::Allow,
            },
        ],
    });

    // Database tier segment
    engine.add_segment(MicroSegment {
        id: "database-tier".to_string(),
        name: "Database Tier".to_string(),
        network_cidr: "10.0.10.0/24".to_string(),
        allowed_protocols: vec!["postgresql".to_string(), "mysql".to_string()],
        allowed_ports: vec![5432, 3306],
        isolation_level: "HIGH".to_string(),
        member_identities: vec![],
        ingress_rules: vec![
            SegmentRule {
                source_segment: Some("web-tier".to_string()),
                destination_segment: Some("database-tier".to_string()),
                protocol: "postgresql".to_string(),
                port_range: (5432, 5432),
                action: PolicyAction::Allow,
            },
        ],
        egress_rules: vec![],
    });
}

fn print_decision(scenario: &str, decision: &PolicyDecision) {
    println!("\n{}", "=".repeat(50));
    println!("{}", scenario);
    println!("{}", "-".repeat(50));
    println!("Decision: {:?}", decision.decision);
    println!("Trust Score: {:.1}", decision.trust_score);
    println!("Threat Level: {}", decision.threat_level);
    if let Some(rule) = &decision.matched_rule {
        println!("Matched Rule: {}", rule);
    }
    println!("\nReasoning:");
    for reason in &decision.reasoning {
        println!("  • {}", reason);
    }
    println!("{}", "=".repeat(50));
}
