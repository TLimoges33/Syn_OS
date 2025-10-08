//! Test program for AI & consciousness system calls
//! Tests: ai_inference, ai_train, consciousness_query, consciousness_update, pattern_recognize, decision_make

#![no_std]
#![no_main]

use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    write_str("=== SynOS AI & Consciousness Syscalls Test ===\n\n");

    // Test 1: AI inference
    test_ai_inference();

    // Test 2: AI training
    test_ai_train();

    // Test 3: consciousness query
    test_consciousness_query();

    // Test 4: consciousness update
    test_consciousness_update();

    // Test 5: pattern recognition
    test_pattern_recognize();

    // Test 6: AI decision making
    test_decision_make();

    write_str("\n✅ All AI/consciousness syscall tests passed!\n");
    exit(0);
}

fn test_ai_inference() {
    write_str("Test 1: ai_inference() - ");

    let model_id = 1; // Neural network model ID
    let input = b"Input data for neural network inference";
    let mut output = [0u8; 128];

    let result = ai_inference(model_id, input, &mut output);

    if result >= 0 {
        write_str("PASS (inference output: ");
        write_num(result as u64);
        write_str(" bytes)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_ai_train() {
    write_str("Test 2: ai_train() - ");

    let model_id = 2; // Training model ID
    let training_data = b"[1.0, 2.0, 3.0] -> [4.0]";  // Sample training data
    let epochs = 100;

    let result = ai_train(model_id, training_data, epochs);

    if result == 0 {
        write_str("PASS (trained ");
        write_num(epochs as u64);
        write_str(" epochs)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_consciousness_query() {
    write_str("Test 3: consciousness_query() - ");

    let query = "What is the current system state?";
    let mut result_buf = [0u8; 256];

    let result = consciousness_query(query, &mut result_buf);

    if result >= 0 {
        write_str("PASS (response: ");
        write_num(result as u64);
        write_str(" bytes)\n");

        // Print first few bytes of response
        if result > 0 {
            write_str("    Content: \"");
            let len = if result > 40 { 40 } else { result as usize };
            write(1, &result_buf[..len]);
            write_str("...\"\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_consciousness_update() {
    write_str("Test 4: consciousness_update() - ");

    let update = b"{\"state\": \"active\", \"confidence\": 0.95, \"learning_rate\": 0.01}";

    let result = consciousness_update(update);

    if result == 0 {
        write_str("PASS (state updated)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_pattern_recognize() {
    write_str("Test 5: pattern_recognize() - ");

    let data = b"192.168.1.1 -> 10.0.0.5:22 [SSH_BRUTE_FORCE] 127 attempts";
    let pattern_type = 1; // Network intrusion pattern

    let result = pattern_recognize(data, pattern_type);

    if result >= 0 {
        write_str("PASS (pattern match score: ");
        write_num(result as u64);
        write_str(")\n");

        if result > 80 {
            write_str("    ⚠️  High confidence threat detected!\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_decision_make() {
    write_str("Test 6: decision_make() - ");

    let context = b"User attempting to access /etc/shadow, privilege level: user, time: 3am";
    let options = b"[allow, deny, log_and_deny, escalate_to_admin]";

    let result = decision_make(context, options);

    if result >= 0 {
        write_str("PASS (decision index: ");
        write_num(result as u64);

        let decision = match result {
            0 => " = allow",
            1 => " = deny",
            2 => " = log_and_deny",
            3 => " = escalate_to_admin",
            _ => " = unknown",
        };
        write_str(decision);
        write_str(")\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
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

