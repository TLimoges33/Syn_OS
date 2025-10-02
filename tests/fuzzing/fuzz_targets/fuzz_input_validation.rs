#![no_main]

use libfuzzer_sys::fuzz_target;
use synos_fuzzable::*;

fuzz_target!(|data: &[u8]| {
    // Fuzz syscall validation
    if data.len() >= 4 {
        let syscall_num = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
        let _ = validate_syscall(syscall_num);
    }

    // Fuzz memory address validation
    if data.len() >= 16 {
        let addr = usize::from_le_bytes([
            data[0], data[1], data[2], data[3],
            data[4], data[5], data[6], data[7],
        ]);
        let size = usize::from_le_bytes([
            data[8], data[9], data[10], data[11],
            data[12], data[13], data[14], data[15],
        ]);
        let _ = validate_memory_address(addr, size);
    }

    // Fuzz constant-time comparison
    if data.len() >= 2 {
        let mid = data.len() / 2;
        let _ = constant_time_compare(&data[..mid], &data[mid..]);
    }
});
