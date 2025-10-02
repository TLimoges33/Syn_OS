#![no_main]

use libfuzzer_sys::fuzz_target;
use synos_fuzzable::*;

fuzz_target!(|data: &[u8]| {
    // Fuzz IPC message parser
    let _ = parse_ipc_message(data);

    // Fuzz command parser
    if let Ok(s) = std::str::from_utf8(data) {
        let _ = parse_command(s);
    }
});
