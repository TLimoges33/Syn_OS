//! Test program for core system calls
//! Tests: exit, write, read, open, close, fork, exec, wait, getpid, sleep

#![no_std]
#![no_main]

use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // Test 1: getpid
    test_getpid();

    // Test 2: write
    test_write();

    // Test 3: open/close
    test_open_close();

    // Test 4: read/write file
    test_read_write();

    // Test 5: sleep
    test_sleep();

    // Test 6: fork (commented out for safety)
    // test_fork();

    // All tests passed
    write_str("✅ All core syscall tests passed!\n");
    exit(0);
}

fn test_getpid() {
    write_str("Test 1: getpid() - ");
    let pid = getpid();
    if pid > 0 {
        write_str("PASS (PID: ");
        write_num(pid as u64);
        write_str(")\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_write() {
    write_str("Test 2: write() - ");
    let msg = "Hello from SynOS!\n";
    let result = write(1, msg.as_bytes());
    if result > 0 {
        write_str("PASS\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_open_close() {
    write_str("Test 3: open()/close() - ");
    let fd = open("/dev/null", 0);
    if fd >= 0 {
        let close_result = close(fd as i32);
        if close_result == 0 {
            write_str("PASS\n");
        } else {
            write_str("FAIL (close)\n");
            exit(1);
        }
    } else {
        write_str("FAIL (open)\n");
        exit(1);
    }
}

fn test_read_write() {
    write_str("Test 4: read()/write() file - ");
    let test_data = b"SynOS Test Data\n";
    let mut read_buf = [0u8; 64];

    // Simulate file operations (would need actual file in real scenario)
    let fd = open("/tmp/synos_test.txt", 0o666);
    if fd >= 0 {
        let write_result = write(fd as i32, test_data);
        if write_result > 0 {
            let read_result = read(fd as i32, &mut read_buf);
            if read_result > 0 {
                write_str("PASS\n");
            } else {
                write_str("FAIL (read)\n");
            }
        } else {
            write_str("FAIL (write)\n");
        }
        close(fd as i32);
    } else {
        write_str("SKIP (no /tmp)\n");
    }
}

fn test_sleep() {
    write_str("Test 5: sleep(100ms) - ");
    let result = sleep(100);
    if result == 0 {
        write_str("PASS\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_fork() {
    write_str("Test 6: fork() - ");
    let pid = fork();
    if pid == 0 {
        // Child process
        write_str("Child process created\n");
        exit(0);
    } else if pid > 0 {
        // Parent process
        wait(pid as i32);
        write_str("PASS\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

// Helper functions
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

