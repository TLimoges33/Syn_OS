//! SynOS HSM Integration CLI
//!
//! Command-line interface for hardware security module operations

use synos_hsm_integration::*;
use uuid::Uuid;

fn main() {
    println!("🔐 SynOS Hardware Security Module Integration");
    println!("==============================================\n");

    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        print_usage();
        return;
    }

    match args[1].as_str() {
        "demo" => run_comprehensive_demo(),
        "tpm" => demo_tpm(),
        "yubikey" => demo_yubikey(),
        "sgx" => demo_sgx(),
        "status" => show_hsm_status(),
        _ => print_usage(),
    }
}

fn print_usage() {
    println!("Usage: synos-hsm <command>");
    println!("\nCommands:");
    println!("  demo       - Run comprehensive HSM demo");
    println!("  tpm        - Demonstrate TPM 2.0 operations");
    println!("  yubikey    - Demonstrate YubiKey operations");
    println!("  sgx        - Demonstrate Intel SGX operations");
    println!("  status     - Show HSM device status");
}

fn run_comprehensive_demo() {
    println!("🎯 Running Comprehensive HSM Demo\n");

    show_hsm_status();
    println!();
    demo_tpm();
    println!();
    demo_yubikey();
    println!();
    demo_sgx();
    println!();
    demo_attestation();
    println!();

    println!("✅ Comprehensive demo complete!");
}

fn show_hsm_status() {
    println!("📊 HSM Device Status");
    println!("────────────────────");

    let mut manager = HSMManager::new();

    match manager.initialize_all() {
        Ok(status) => {
            println!("✅ TPM 2.0:       {}", if status.tpm_available { "Available" } else { "Not Available" });
            println!("✅ YubiKey:       {}", if status.yubikey_available { "Connected" } else { "Not Connected" });
            println!("✅ Intel SGX:     {}", if status.sgx_available { "Enabled" } else { "Not Available" });
            println!("✅ Secure Boot:   {}", if status.secure_boot_enabled { "Enabled" } else { "Disabled" });
        }
        Err(e) => println!("❌ Error: {}", e),
    }

    let stats = manager.get_statistics();
    println!("\n📈 Statistics:");
    println!("   Total Keys: {}", stats.total_keys);
    println!("   Attestations: {}", stats.attestations_performed);
}

fn demo_tpm() {
    println!("🔒 TPM 2.0 Operations");
    println!("─────────────────────");

    let mut manager = HSMManager::new();

    // Generate TPM key (emulated)
    println!("📌 Generating TPM-backed RSA key...");
    match manager.generate_key(KeyType::RSA2048, DeviceType::SoftwareEmulation) {
        Ok(key) => {
            println!("   ✅ Key generated: {}", key.id);
            println!("      Type: {:?}", key.key_type);
            println!("      HSM-backed: {}", key.hsm_backed);

            // Sign data
            let data = b"Important message to sign";
            println!("\n📝 Signing data...");
            match manager.sign(key.id, data, DeviceType::SoftwareEmulation) {
                Ok(signature) => {
                    println!("   ✅ Signature: {}...", hex::encode(&signature[..16]));
                }
                Err(e) => println!("   ❌ Sign error: {}", e),
            }
        }
        Err(e) => println!("   ❌ Key generation error: {}", e),
    }

    // Seal and unseal data
    println!("\n🔐 Sealing secret data...");
    let secret = b"super_secret_password_123";
    match manager.store_secret(secret, DeviceType::SoftwareEmulation) {
        Ok(secret_id) => {
            println!("   ✅ Secret sealed: {}", secret_id);

            println!("\n🔓 Unsealing secret...");
            match manager.retrieve_secret(secret_id, DeviceType::SoftwareEmulation) {
                Ok(unsealed) => {
                    println!("   ✅ Secret unsealed successfully");
                    println!("      Match: {}", unsealed == secret);
                }
                Err(e) => println!("   ❌ Unseal error: {}", e),
            }
        }
        Err(e) => println!("   ❌ Seal error: {}", e),
    }
}

fn demo_yubikey() {
    println!("🔑 YubiKey Operations");
    println!("─────────────────────");

    match YubiKeyInterface::initialize() {
        Ok(mut yk) => {
            println!("📱 YubiKey Status:");
            println!("   Serial: {}", yk.get_serial_number().unwrap_or("Unknown"));
            println!("   Connected: {}", yk.is_connected());

            // PIN verification (simulated)
            println!("\n🔢 Verifying PIN...");
            match yk.verify_pin("123456") {
                Ok(_) => println!("   ✅ PIN verified"),
                Err(e) => println!("   ❌ PIN error: {}", e),
            }

            // Challenge-Response
            println!("\n🎲 Challenge-Response...");
            let challenge = b"random_challenge_12345";
            match yk.challenge_response(challenge) {
                Ok(response) => {
                    println!("   ✅ Response: {}...", hex::encode(&response[..16]));
                }
                Err(e) => println!("   ❌ Error: {}", e),
            }

            // FIDO2 credential
            println!("\n🔐 FIDO2 Make Credential...");
            match yk.fido2_make_credential("example.com", b"user123", "testuser") {
                Ok((cred_id, pubkey)) => {
                    println!("   ✅ Credential created");
                    println!("      Cred ID: {}...", hex::encode(&cred_id[..16]));
                    println!("      PubKey: {}...", hex::encode(&pubkey[..16]));

                    println!("\n🔓 FIDO2 Get Assertion...");
                    match yk.fido2_get_assertion("example.com", &cred_id, b"client_data") {
                        Ok(assertion) => {
                            println!("   ✅ Assertion: {}...", hex::encode(&assertion[..16]));
                        }
                        Err(e) => println!("   ❌ Error: {}", e),
                    }
                }
                Err(e) => println!("   ❌ Error: {}", e),
            }
        }
        Err(e) => println!("❌ YubiKey initialization error: {}", e),
    }
}

fn demo_sgx() {
    println!("🛡️  Intel SGX Operations");
    println!("───────────────────────");

    match SGXEnclaveInterface::initialize() {
        Ok(mut sgx) => {
            println!("📊 SGX Status:");
            println!("   Enabled: {}", sgx.is_enabled());

            let report = sgx.get_enclave_report();
            println!("   MRENCLAVE: {}...", hex::encode(&report.mrenclave[..16]));
            println!("   MRSIGNER: {}...", hex::encode(&report.mrsigner[..16]));

            // Seal data
            println!("\n🔐 Sealing data in enclave...");
            let secret = b"enclave_protected_secret";
            let data_id = Uuid::new_v4();

            match sgx.seal_data(data_id, secret) {
                Ok(_) => {
                    println!("   ✅ Data sealed: {}", data_id);

                    println!("\n🔓 Unsealing data...");
                    match sgx.unseal_data(data_id) {
                        Ok(unsealed) => {
                            println!("   ✅ Data unsealed successfully");
                            println!("      Match: {}", unsealed == secret);
                        }
                        Err(e) => println!("   ❌ Unseal error: {}", e),
                    }
                }
                Err(e) => println!("   ❌ Seal error: {}", e),
            }

            // Key derivation
            println!("\n🔑 Deriving enclave key...");
            match sgx.derive_key("storage", b"context123") {
                Ok(key) => {
                    println!("   ✅ Derived key: {}...", hex::encode(&key[..16]));
                }
                Err(e) => println!("   ❌ Error: {}", e),
            }
        }
        Err(e) => println!("❌ SGX initialization error: {}", e),
    }
}

fn demo_attestation() {
    println!("🔐 Remote Attestation");
    println!("─────────────────────");

    let mut manager = HSMManager::new();

    // TPM attestation (emulated)
    println!("📋 Creating TPM attestation...");
    let nonce: Vec<u8> = (0..32).map(|_| rand::random::<u8>()).collect();

    match manager.attest(nonce.clone(), DeviceType::SoftwareEmulation) {
        Ok(record) => {
            println!("   ✅ Attestation created: {}", record.id);
            println!("      Device: {:?}", record.device_type);
            println!("      Timestamp: {}", record.timestamp);
            println!("      Measurement: {}...", hex::encode(&record.measurement[..16]));

            // Verify attestation
            println!("\n✅ Verifying attestation...");
            match manager.verify_attestation(&record) {
                Ok(valid) => {
                    println!("   {} Attestation is {}",
                        if valid { "✅" } else { "❌" },
                        if valid { "VALID" } else { "INVALID" }
                    );
                }
                Err(e) => println!("   ❌ Verification error: {}", e),
            }
        }
        Err(e) => println!("   ❌ Attestation error: {}", e),
    }

    // Show attestation log
    println!("\n📚 Attestation Log:");
    let log = manager.get_attestation_log();
    println!("   Total attestations: {}", log.len());
    for (i, record) in log.iter().enumerate().take(3) {
        println!("   {}. {} ({:?})", i + 1, record.id, record.device_type);
    }
}
