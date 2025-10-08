//! Test program for security & threat detection system calls
//! Tests: threat_detect, threat_log, threat_query, security_audit, access_control, crypto_op, secure_random

#![no_std]
#![no_main]

use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    write_str("=== SynOS Security Syscalls Test ===\n\n");

    // Test 1: threat detection
    test_threat_detect();

    // Test 2: threat logging
    test_threat_log();

    // Test 3: threat query
    test_threat_query();

    // Test 4: security audit
    test_security_audit();

    // Test 5: access control
    test_access_control();

    // Test 6: cryptographic operations
    test_crypto_op();

    // Test 7: secure random
    test_secure_random();

    write_str("\n✅ All security syscall tests passed!\n");
    exit(0);
}

fn test_threat_detect() {
    write_str("Test 1: threat_detect() - ");

    let suspicious_data = b"eval(base64_decode($_POST['cmd']))"; // PHP backdoor
    let result = threat_detect(suspicious_data);

    if result >= 0 {
        write_str("PASS (threat level: ");
        write_num(result as u64);
        write_str(")\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_threat_log() {
    write_str("Test 2: threat_log() - ");

    let threat_id = 12345;
    let severity = 3; // High severity
    let message = "SQL injection attempt detected";

    let result = threat_log(threat_id, severity, message);

    if result == 0 {
        write_str("PASS (logged threat ID: ");
        write_num(threat_id);
        write_str(")\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_threat_query() {
    write_str("Test 3: threat_query() - ");

    let query = "SELECT * FROM threats WHERE severity > 2";
    let mut results = [0u8; 256];

    let result = threat_query(query, &mut results);

    if result >= 0 {
        write_str("PASS (found ");
        write_num(result as u64);
        write_str(" threats)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_security_audit() {
    write_str("Test 4: security_audit() - ");

    let target = "/etc/passwd";
    let audit_type = 1; // File integrity check

    let result = security_audit(target, audit_type);

    if result >= 0 {
        write_str("PASS (audit score: ");
        write_num(result as u64);
        write_str(")\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_access_control() {
    write_str("Test 5: access_control() - ");

    let resource = "/var/log/synos.log";
    let action = 2; // READ action
    let user = 1000; // UID 1000

    let result = access_control(resource, action, user);

    if result >= 0 {
        if result == 1 {
            write_str("PASS (access granted)\n");
        } else {
            write_str("PASS (access denied)\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_crypto_op() {
    write_str("Test 6: crypto_op() - ");

    let op = 1; // AES-256 encryption
    let data = b"Secret message for encryption";
    let key = b"ThisIsA32ByteAES256SecretKey!!!!";

    let result = crypto_op(op, data, key);

    if result >= 0 {
        write_str("PASS (encrypted ");
        write_num(data.len() as u64);
        write_str(" bytes)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_secure_random() {
    write_str("Test 7: secure_random() - ");

    let mut random_bytes = [0u8; 32];
    let result = secure_random(&mut random_bytes);

    if result == 32 {
        write_str("PASS (generated 32 bytes: ");
        for i in 0..4 {
            write_hex(random_bytes[i]);
            write_str(" ");
        }
        write_str("...)\n");
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

fn write_hex(n: u8) {
    let hex_chars = b"0123456789abcdef";
    write(1, &hex_chars[(n >> 4) as usize..(n >> 4) as usize + 1]);
    write(1, &hex_chars[(n & 0xF) as usize..(n & 0xF) as usize + 1]);
}

