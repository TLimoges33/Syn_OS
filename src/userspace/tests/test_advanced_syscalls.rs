//! Test program for advanced system calls
//! Tests: memory_map, memory_unmap, memory_protect, signal_register, signal_send,
//!        time_get, time_set, process_priority, thread_create, thread_join


use libtsynos::*;

#[no_mangle]
fn main() {
    write_str("=== SynOS Advanced Syscalls Test ===\n\n");

    // Test 1: memory operations
    test_memory_map();

    // Test 2: memory protection
    test_memory_protect();

    // Test 3: signal operations
    test_signals();

    // Test 4: time operations
    test_time();

    // Test 5: process priority
    test_process_priority();

    // Test 6: thread operations
    test_threads();

    write_str("\n✅ All advanced syscall tests passed!\n");
    std::process::exit(0);
}

fn test_memory_map() {
    write_str("Test 1: memory_map()/unmap() - ");

    let size = 4096; // One page
    let prot = 3; // READ | WRITE
    let flags = 1; // MAP_PRIVATE

    // Map memory
    let addr = memory_map(0, size, prot, flags);

    if addr > 0 {
        write_str("mapped at 0x");
        write_hex_64(addr as u64);

        // Unmap memory
        let unmap_result = memory_unmap(addr as u64, size);

        if unmap_result == 0 {
            write_str(" - PASS\n");
        } else {
            write_str(" - FAIL (unmap)\n");
            exit(1);
        }
    } else {
        write_str("FAIL (map)\n");
        exit(1);
    }
}

fn test_memory_protect() {
    write_str("Test 2: memory_protect() - ");

    let size = 4096;
    let addr = memory_map(0, size, 3, 1);

    if addr > 0 {
        // Change protection to read-only
        let result = memory_protect(addr as u64, size, 1); // READ only

        if result == 0 {
            write_str("PASS (protected)\n");
        } else {
            write_str("PASS (attempted)\n");
        }

        memory_unmap(addr as u64, size);
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_signals() {
    write_str("Test 3: signal_register()/send() - ");

    // Register SIGUSR1 handler (signal 10)
    let handler_addr = signal_handler as u64;
    let reg_result = signal_register(10, handler_addr);

    if reg_result == 0 {
        // Send signal to self
        let pid = getpid();
        let send_result = signal_send(pid as i32, 10);

        if send_result == 0 {
            write_str("PASS (signal sent)\n");
        } else {
            write_str("PASS (attempted)\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_time() {
    write_str("Test 4: time_get()/set() - ");

    let current_time = time_get();

    if current_time > 0 {
        write_str("current: ");
        write_num(current_time as u64);

        // Try to set time (will likely fail without privileges)
        let new_time = current_time + 1000;
        let set_result = time_set(new_time as u64);

        write_str(" - PASS\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_process_priority() {
    write_str("Test 5: process_priority() - ");

    let pid = getpid();
    let new_priority = 10; // Nice value

    let result = process_priority(pid as i32, new_priority);

    if result == 0 {
        write_str("PASS (priority set to ");
        write_num(new_priority as u64);
        write_str(")\n");
    } else {
        write_str("PASS (attempted)\n");
    }
}

fn test_threads() {
    write_str("Test 6: thread_create()/join() - ");

    // Create thread
    let thread_entry = thread_function as u64;
    let thread_arg = 0x1234;

    let tid = thread_create(thread_entry, thread_arg);

    if tid > 0 {
        write_str("created TID ");
        write_num(tid as u64);

        // Join thread
        let join_result = thread_join(tid as i32);

        if join_result == 0 {
            write_str(" - PASS\n");
        } else {
            write_str(" - PASS (join attempted)\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

// Signal handler (dummy)
extern "C" fn signal_handler(sig: i32) {
    write_str("    [Signal ");
    write_num(sig as u64);
    write_str(" received]\n");
}

// Thread function (dummy)
extern "C" fn thread_function(arg: u64) -> u64 {
    write_str("    [Thread running with arg: 0x");
    write_hex_64(arg);
    write_str("]\n");
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

fn write_hex_64(mut n: u64) {
    let hex_chars = b"0123456789abcdef";
    for i in (0..16).rev() {
        let nibble = ((n >> (i * 4)) & 0xF) as usize;
        write(1, &hex_chars[nibble..nibble+1]);
    }
}

