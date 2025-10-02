// Fuzzable security-critical functions for SynOS
// These demonstrate the types of validation that would occur in the kernel

/// Parse and validate syscall number
/// Returns Ok(syscall_name) or Err(reason)
pub fn validate_syscall(syscall_num: u32) -> Result<&'static str, &'static str> {
    match syscall_num {
        0 => Ok("read"),
        1 => Ok("write"),
        2 => Ok("open"),
        3 => Ok("close"),
        4..=99 => Ok("valid_syscall"),
        100..=199 => Ok("privileged_syscall"),
        _ => Err("Invalid syscall number"),
    }
}

/// Validate memory address is within allowed range
pub fn validate_memory_address(addr: usize, size: usize) -> Result<(), &'static str> {
    const USER_SPACE_START: usize = 0x0000_0000_0000_0000;
    const USER_SPACE_END: usize = 0x0000_7FFF_FFFF_FFFF;

    // Check for integer overflow
    let end_addr = addr.checked_add(size).ok_or("Address overflow")?;

    // Check bounds
    if addr < USER_SPACE_START || end_addr > USER_SPACE_END {
        return Err("Address out of bounds");
    }

    Ok(())
}

/// Parse IPC message format: [type: 1 byte][length: 4 bytes][payload: n bytes]
pub fn parse_ipc_message(data: &[u8]) -> Result<(u8, Vec<u8>), &'static str> {
    if data.len() < 5 {
        return Err("Message too short");
    }

    let msg_type = data[0];
    let length = u32::from_le_bytes([data[1], data[2], data[3], data[4]]) as usize;

    // Validate message type
    if msg_type > 10 {
        return Err("Invalid message type");
    }

    // Check for buffer overflow
    if length > 4096 {
        return Err("Message too large");
    }

    if length > data.len() - 5 {
        return Err("Length exceeds available data");
    }

    let payload = data[5..5 + length].to_vec();
    Ok((msg_type, payload))
}

/// Parse command string safely (prevents command injection)
pub fn parse_command(input: &str) -> Result<Vec<String>, &'static str> {
    if input.is_empty() {
        return Err("Empty command");
    }

    if input.len() > 1024 {
        return Err("Command too long");
    }

    // Check for dangerous characters
    if input.contains(';') || input.contains('|') || input.contains('&') {
        return Err("Dangerous characters detected");
    }

    Ok(input.split_whitespace().map(|s| s.to_string()).collect())
}

/// Constant-time string comparison (prevents timing attacks)
pub fn constant_time_compare(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }

    let mut result = 0u8;
    for (x, y) in a.iter().zip(b.iter()) {
        result |= x ^ y;
    }
    result == 0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_syscall() {
        assert!(validate_syscall(0).is_ok());
        assert!(validate_syscall(1000).is_err());
    }

    #[test]
    fn test_validate_memory() {
        assert!(validate_memory_address(0x1000, 0x100).is_ok());
        assert!(validate_memory_address(usize::MAX, 1).is_err());
    }

    #[test]
    fn test_parse_ipc() {
        let msg = vec![1, 4, 0, 0, 0, b't', b'e', b's', b't'];
        assert!(parse_ipc_message(&msg).is_ok());
    }
}
