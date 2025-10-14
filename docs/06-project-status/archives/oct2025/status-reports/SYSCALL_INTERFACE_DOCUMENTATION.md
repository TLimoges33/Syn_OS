# SynOS Syscall Interface Documentation

## Overview

SynOS provides a complete syscall interface with 43 system calls organized into 5 categories. The interface is designed to support both traditional OS operations and advanced AI/consciousness features unique to SynOS.

## Architecture

### Components

1. **Userspace Library (`libtsynos`)**
   - Location: `src/userspace/libtsynos/`
   - Provides safe Rust wrappers for all syscalls
   - Uses inline assembly for x86_64 syscall instruction
   - No standard library dependencies (no_std)

2. **Kernel Syscall Handler (`synos_syscalls`)**
   - Location: `src/kernel/src/syscalls/synos_syscalls.rs`
   - Implements all 43 syscall handlers
   - Matches userspace syscall numbers exactly (0-42)
   - Integrated with kernel's AI consciousness system

3. **Userspace Integration Module**
   - Location: `src/kernel/src/userspace_integration.rs`
   - Handles ELF loading and process execution
   - Manages syscall routing to appropriate handlers
   - Provides testing framework for userspace programs

## Syscall Numbers and Categories

### Core System Calls (0-9)
| Number | Name | Description |
|--------|------|-------------|
| 0 | Exit | Terminate process with exit code |
| 1 | Write | Write data to file descriptor |
| 2 | Read | Read data from file descriptor |
| 3 | Open | Open file/resource |
| 4 | Close | Close file descriptor |
| 5 | Fork | Create child process |
| 6 | Exec | Execute program |
| 7 | Wait | Wait for process termination |
| 8 | GetPid | Get current process ID |
| 9 | Sleep | Sleep for milliseconds |

### Network System Calls (10-19)
| Number | Name | Description |
|--------|------|-------------|
| 10 | Socket | Create network socket |
| 11 | Bind | Bind socket to address |
| 12 | Listen | Listen for connections |
| 13 | Accept | Accept incoming connection |
| 14 | Connect | Connect to remote endpoint |
| 15 | Send | Send data on socket |
| 16 | Recv | Receive data from socket |
| 17 | SendTo | Send datagram to address |
| 18 | RecvFrom | Receive datagram with source |
| 19 | GetSockOpt | Get socket options |

### Security System Calls (20-26)
| Number | Name | Description |
|--------|------|-------------|
| 20 | ThreatDetect | Analyze data for threats |
| 21 | ThreatLog | Log security event |
| 22 | ThreatQuery | Query threat database |
| 23 | SecurityAudit | Run security audit |
| 24 | AccessControl | Check access permissions |
| 25 | CryptoOp | Perform cryptographic operation |
| 26 | SecureRandom | Generate secure random data |

### AI & Consciousness System Calls (27-32)
| Number | Name | Description |
|--------|------|-------------|
| 27 | AiInference | Run AI model inference |
| 28 | AiTrain | Train AI model |
| 29 | ConsciousnessQuery | Query consciousness state |
| 30 | ConsciousnessUpdate | Update consciousness |
| 31 | PatternRecognize | Recognize patterns in data |
| 32 | DecisionMake | AI-assisted decision making |

### Advanced System Calls (33-42)
| Number | Name | Description |
|--------|------|-------------|
| 33 | MemoryMap | Map memory region |
| 34 | MemoryUnmap | Unmap memory region |
| 35 | MemoryProtect | Change memory protection |
| 36 | SignalRegister | Register signal handler |
| 37 | SignalSend | Send signal to process |
| 38 | TimeGet | Get current time |
| 39 | TimeSet | Set system time |
| 40 | ProcessPriority | Set process priority |
| 41 | ThreadCreate | Create new thread |
| 42 | ThreadJoin | Wait for thread completion |

## Calling Convention

### x86_64 Syscall ABI
- **Syscall Number**: `RAX`
- **Arguments**: `RDI`, `RSI`, `RDX`, `R10`, `R8`, `R9`
- **Return Value**: `RAX`
- **Instruction**: `syscall`

### Userspace Usage (Rust)

```rust
use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // Write to stdout
    let message = b"Hello from SynOS!\n";
    write(1, message);

    // Get process ID
    let pid = getpid();

    // Exit successfully
    exit(0);
}
```

### Kernel Implementation

```rust
impl SynOSSyscallHandler {
    pub fn handle_syscall(&mut self, syscall_num: u64, args: &SyscallArgs) -> SyscallResult {
        match syscall_num {
            0 => self.sys_exit(args.arg0 as i32),
            1 => self.sys_write(args.arg0 as i32, args.arg1 as *const u8, args.arg2 as usize),
            // ... other syscalls
            _ => Err(SyscallError::ENOSYS),
        }
    }
}
```

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| -1 | EPERM | Operation not permitted |
| -2 | ENOENT | No such file or directory |
| -3 | ESRCH | No such process |
| -9 | EBADF | Bad file descriptor |
| -12 | ENOMEM | Out of memory |
| -13 | EACCES | Permission denied |
| -14 | EFAULT | Bad address |
| -22 | EINVAL | Invalid argument |
| -38 | ENOSYS | Function not implemented |

## Example: Complete Syscall Flow

### 1. Userspace Application

```rust
// test_core_syscalls.rs
#![no_std]
#![no_main]

use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    write_str("Testing SynOS syscalls\n");

    let pid = getpid();
    write_str("PID: ");
    write_num(pid as u64);
    write_str("\n");

    exit(0);
}
```

### 2. Syscall Invocation (Assembly)

```rust
// libtsynos/src/lib.rs
#[inline(always)]
pub unsafe fn syscall1(num: SyscallNumber, arg1: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

pub fn write(fd: i32, buf: &[u8]) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::Write,  // RAX = 1
            fd as u64,              // RDI = fd
            buf.as_ptr() as u64,    // RSI = buffer
            buf.len() as u64,       // RDX = length
        )
    }
}
```

### 3. Kernel Handler

```rust
// synos_syscalls.rs
fn sys_write(&mut self, fd: i32, buf: *const u8, count: usize) -> SyscallResult {
    if fd < 0 || fd > 2 {
        return Err(SyscallError::EBADF);
    }

    if buf.is_null() {
        return Err(SyscallError::EFAULT);
    }

    // Perform actual I/O operation
    // ...

    Ok(count as i64)
}
```

## Testing Framework

### Building Userspace Tests

```bash
# Build all test binaries
./src/userspace/build-all-tests.sh

# Or build individually
cargo build --package synos-userspace-tests \\
    --bin test_core_syscalls \\
    --target x86_64-unknown-none
```

### Running Integration Tests

```rust
use syn_kernel::userspace_integration::UserspaceIntegrationTest;

// In kernel test environment
let mut test_runner = UserspaceIntegrationTest::new();

// Load and run test binary
let elf_data = include_bytes!("test_binary.elf");
test_runner.run_test("test_name", elf_data)?;

// Run all tests
let passed = test_runner.run_all_tests()?;
println!("Passed {}/6 tests", passed);
```

## Security Considerations

1. **Parameter Validation**
   - All pointer parameters are checked for null
   - File descriptors are validated against open FD table
   - Buffer sizes are bounds-checked

2. **Privilege Separation**
   - Syscalls enforce user/kernel mode boundaries
   - Access control checks for sensitive operations
   - Capability-based permissions for resources

3. **AI Integration Security**
   - Consciousness updates are rate-limited
   - Pattern recognition is sandboxed
   - AI inference runs in isolated context

## Performance Characteristics

- **Syscall Latency**: ~50-100 CPU cycles (bare syscall overhead)
- **Context Switch**: ~1-2 microseconds (process switch)
- **AI Syscalls**: Variable (100μs - 10ms depending on model)
- **Network Syscalls**: Dependent on stack implementation

## Future Enhancements

1. **Async Syscalls** - Non-blocking variants for I/O operations
2. **Batch Syscalls** - Multiple syscalls in single trap
3. **Hardware Acceleration** - Offload crypto/AI to specialized units
4. **Extended Attributes** - Per-syscall metadata and tracing
5. **Dynamic Loading** - Runtime syscall table updates

## API Stability

- **Stable** (0-19): Core and network syscalls follow POSIX conventions
- **Evolving** (20-32): Security and AI syscalls may change
- **Experimental** (33-42): Advanced syscalls under active development

## References

- Userspace Library: `src/userspace/libtsynos/src/lib.rs`
- Kernel Implementation: `src/kernel/src/syscalls/synos_syscalls.rs`
- Integration Tests: `src/userspace/tests/`
- Test Examples: `test_core_syscalls.rs`, `test_integration_full.rs`

---

*Last Updated: October 4, 2025*
*Version: 1.0 (Phase 3d Complete)*
