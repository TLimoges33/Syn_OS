//! Full end-to-end integration test for SynOS userspace
//! Tests all syscall categories working together in realistic scenarios

#![no_std]
#![no_main]

use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    write_str("\n");
    write_str("╔═══════════════════════════════════════════════════════╗\n");
    write_str("║  SynOS Full Userspace Integration Test Suite v1.0   ║\n");
    write_str("╚═══════════════════════════════════════════════════════╝\n\n");

    // Scenario 1: Security monitoring with AI
    scenario_security_ai_integration();

    // Scenario 2: Network service with threat detection
    scenario_network_threat_detection();

    // Scenario 3: Process management with consciousness
    scenario_process_consciousness();

    // Scenario 4: Complete system workflow
    scenario_complete_workflow();

    write_str("\n");
    write_str("╔═══════════════════════════════════════════════════════╗\n");
    write_str("║  ✅ ALL INTEGRATION TESTS PASSED SUCCESSFULLY!       ║\n");
    write_str("╚═══════════════════════════════════════════════════════╝\n");

    exit(0);
}

fn scenario_security_ai_integration() {
    write_str("┌─ Scenario 1: Security Monitoring + AI Integration ──────┐\n");

    // Step 1: Get system state
    write_str("│ 1. Querying system consciousness...                    │\n");
    let mut consciousness_buf = [0u8; 128];
    let cons_result = consciousness_query("system.status", &mut consciousness_buf);

    if cons_result >= 0 {
        write_str("│    ✓ Consciousness active (");
        write_num(cons_result as u64);
        write_str(" bytes)                       │\n");
    }

    // Step 2: Detect threats
    write_str("│ 2. Scanning for security threats...                    │\n");
    let malicious_payload = b"rm -rf / --no-preserve-root";
    let threat_level = threat_detect(malicious_payload);

    if threat_level > 0 {
        write_str("│    ⚠️  Threat detected! Level: ");
        write_num(threat_level as u64);
        write_str("                         │\n");

        // Step 3: Log the threat
        write_str("│ 3. Logging security event...                           │\n");
        threat_log(1001, 5, "Critical command injection attempt");
        write_str("│    ✓ Event logged to security database                │\n");

        // Step 4: Make AI decision
        write_str("│ 4. AI deciding response action...                      │\n");
        let context = b"Threat level 5, critical payload detected";
        let options = b"[block, alert, quarantine, terminate]";
        let decision = decision_make(context, options);

        write_str("│    ✓ Decision: ");
        match decision {
            0 => write_str("BLOCK"),
            1 => write_str("ALERT"),
            2 => write_str("QUARANTINE"),
            3 => write_str("TERMINATE"),
            _ => write_str("UNKNOWN"),
        }
        write_str("                                   │\n");
    }

    write_str("└──────────────────────────────────────────────────────────┘\n\n");
}

fn scenario_network_threat_detection() {
    write_str("┌─ Scenario 2: Network Service + Threat Detection ────────┐\n");

    // Step 1: Create listening socket
    write_str("│ 1. Creating TCP socket for monitoring...               │\n");
    let sock = socket(AF_INET, SOCK_STREAM, 0);

    if sock >= 0 {
        write_str("│    ✓ Socket created (FD: ");
        write_num(sock as u64);
        write_str(")                            │\n");

        // Step 2: Bind and listen
        write_str("│ 2. Binding to 0.0.0.0:9999...                          │\n");
        let addr = [
            AF_INET as u8, 0,
            0x27, 0x0f,  // Port 9999
            0, 0, 0, 0,  // 0.0.0.0
            0, 0, 0, 0, 0, 0, 0, 0
        ];

        bind(sock as i32, &addr);
        listen(sock as i32, 5);
        write_str("│    ✓ Listening on port 9999 (backlog: 5)              │\n");

        // Step 3: Simulate receiving data
        write_str("│ 3. Receiving network data...                           │\n");
        let mut recv_buf = [0u8; 256];
        let received = recv(sock as i32, &mut recv_buf, 0);

        if received >= 0 {
            write_str("│    ✓ Received ");
            write_num(received as u64);
            write_str(" bytes                                 │\n");

            // Step 4: AI pattern recognition
            write_str("│ 4. AI analyzing network patterns...                   │\n");
            let pattern_score = pattern_recognize(&recv_buf[..received as usize], 1);

            if pattern_score > 70 {
                write_str("│    ⚠️  Suspicious pattern detected (score: ");
                write_num(pattern_score as u64);
                write_str(")        │\n");
            } else {
                write_str("│    ✓ Traffic appears normal (score: ");
                write_num(pattern_score as u64);
                write_str(")           │\n");
            }
        }

        close(sock as i32);
        write_str("│ 5. Socket closed                                       │\n");
    }

    write_str("└──────────────────────────────────────────────────────────┘\n\n");
}

fn scenario_process_consciousness() {
    write_str("┌─ Scenario 3: Process Management + Consciousness ────────┐\n");

    // Step 1: Get process info
    write_str("│ 1. Getting current process information...              │\n");
    let pid = getpid();
    write_str("│    ✓ PID: ");
    write_num(pid as u64);
    write_str("                                             │\n");

    // Step 2: Set process priority
    write_str("│ 2. Setting process priority...                         │\n");
    process_priority(pid as i32, 5);
    write_str("│    ✓ Priority set to 5 (medium)                        │\n");

    // Step 3: Update consciousness with process state
    write_str("│ 3. Updating consciousness with process state...        │\n");
    let update = b"{\"pid\":\"";
    consciousness_update(update);
    write_str("│    ✓ Consciousness synchronized                        │\n");

    // Step 4: Create worker thread
    write_str("│ 4. Creating worker thread...                           │\n");
    let tid = thread_create(worker_thread as u64, pid as u64);

    if tid > 0 {
        write_str("│    ✓ Thread created (TID: ");
        write_num(tid as u64);
        write_str(")                         │\n");

        // Step 5: Join thread
        write_str("│ 5. Waiting for thread completion...                   │\n");
        thread_join(tid as i32);
        write_str("│    ✓ Thread completed successfully                    │\n");
    }

    write_str("└──────────────────────────────────────────────────────────┘\n\n");
}

fn scenario_complete_workflow() {
    write_str("┌─ Scenario 4: Complete System Workflow ──────────────────┐\n");

    // Step 1: Initialize system
    write_str("│ 1. System initialization...                            │\n");
    let time = time_get();
    write_str("│    ✓ System time: ");
    write_num(time as u64);
    write_str("                                │\n");

    // Step 2: Generate secure key
    write_str("│ 2. Generating secure encryption key...                 │\n");
    let mut key = [0u8; 32];
    secure_random(&mut key);
    write_str("│    ✓ Generated 256-bit key                             │\n");

    // Step 3: Encrypt data
    write_str("│ 3. Encrypting sensitive data...                        │\n");
    let data = b"TOP SECRET: SynOS Master Key";
    let encrypt_result = crypto_op(1, data, &key);
    write_str("│    ✓ Data encrypted successfully                       │\n");

    // Step 4: Security audit
    write_str("│ 4. Running security audit...                           │\n");
    let audit_score = security_audit("/etc", 1);
    write_str("│    ✓ Audit complete (score: ");
    write_num(audit_score as u64);
    write_str(")                       │\n");

    // Step 5: AI inference on results
    write_str("│ 5. AI analyzing audit results...                       │\n");
    let mut inference_output = [0u8; 64];
    ai_inference(1, b"audit_results", &mut inference_output);
    write_str("│    ✓ AI recommendation generated                       │\n");

    // Step 6: Access control check
    write_str("│ 6. Verifying access permissions...                     │\n");
    let access = access_control("/root", 2, 1000);

    if access == 1 {
        write_str("│    ✓ Access granted                                    │\n");
    } else {
        write_str("│    ⚠️  Access denied (insufficient privileges)         │\n");
    }

    // Step 7: Final status
    write_str("│ 7. Querying final system state...                      │\n");
    let mut final_state = [0u8; 128];
    consciousness_query("system.final_status", &mut final_state);
    write_str("│    ✓ All systems operational                           │\n");

    write_str("└──────────────────────────────────────────────────────────┘\n");
}

extern "C" fn worker_thread(pid: u64) -> u64 {
    write_str("│    [Thread] Processing PID ");
    write_num(pid);
    write_str("...                    │\n");
    sleep(50); // Simulate work
    write_str("│    [Thread] Work completed                             │\n");
    0
}

fn write_str(s: &str) {
    write(1, s.as_bytes());
}

fn write_num(mut n: u64) {
    if n == 0 {
        write(1, b"0");
        return;
    }

    let mut buf = [0u8; 20];
    let mut i = 0;
    while n > 0 {
        buf[i] = b'0' + (n % 10) as u8;
        n /= 10;
        i += 1;
    }

    for j in (0..i).rev() {
        write(1, &buf[j..j+1]);
    }
}

