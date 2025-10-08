# SynOS Userspace Integration

## Overview

Complete userspace library and test suite for SynOS system calls. This provides a safe, ergonomic Rust interface for all 43 SynOS syscalls, enabling userspace applications to interact with the kernel.

---

## 📚 Components

### 1. **libtsynos** - Userspace Library
**Location:** `libtsynos/`

Safe Rust wrappers for all 43 SynOS system calls:
- **Core System Calls** (10): exit, write, read, open, close, fork, exec, wait, getpid, sleep
- **Networking** (10): socket, bind, listen, accept, connect, send, recv, sendto, recvfrom, getsockopt
- **Security & Threat Detection** (7): threat_detect, threat_log, threat_query, security_audit, access_control, crypto_op, secure_random
- **AI & Consciousness** (6): ai_inference, ai_train, consciousness_query, consciousness_update, pattern_recognize, decision_make
- **Advanced** (10): memory_map, memory_unmap, memory_protect, signal_register, signal_send, time_get, time_set, process_priority, thread_create, thread_join

### 2. **Test Programs** - Comprehensive Test Suite
**Location:** `tests/`

Six test programs covering all syscall categories:

1. **test_core_syscalls** - Core system call testing
2. **test_network_syscalls** - Networking operations
3. **test_security_syscalls** - Security & threat detection
4. **test_ai_syscalls** - AI & consciousness
5. **test_advanced_syscalls** - Advanced features
6. **test_integration_full** - End-to-end integration scenarios

---

## 🔧 Building

### Build the library:
```bash
cd libtsynos
cargo build --release
```

### Build all tests:
```bash
cd tests
cargo build --release
```

### Build specific test:
```bash
cd tests
cargo build --release --bin test_core_syscalls
```

---

## 🧪 Running Tests

### Run all tests:
```bash
cd tests

# Run each test binary
./target/release/test_core_syscalls
./target/release/test_network_syscalls
./target/release/test_security_syscalls
./target/release/test_ai_syscalls
./target/release/test_advanced_syscalls
./target/release/test_integration_full
```

### Expected Output:
Each test displays progress and results:
```
=== SynOS Core Syscalls Test ===

Test 1: getpid() - PASS (PID: 1234)
Test 2: write() - PASS
Test 3: open()/close() - PASS
Test 4: read()/write() file - PASS
Test 5: sleep(100ms) - PASS

✅ All core syscall tests passed!
```

---

## 📋 Integration Test Scenarios

The full integration test (`test_integration_full`) demonstrates four realistic scenarios:

### Scenario 1: Security Monitoring + AI Integration
- Query consciousness state
- Detect threats in data
- Log security events
- AI-driven decision making

### Scenario 2: Network Service + Threat Detection
- Create TCP socket
- Bind and listen
- Receive network data
- AI pattern recognition

### Scenario 3: Process Management + Consciousness
- Get process information
- Set process priority
- Update consciousness state
- Thread creation and joining

### Scenario 4: Complete System Workflow
- System initialization
- Secure key generation
- Data encryption
- Security auditing
- AI inference
- Access control
- Final status check

---

## 🏗️ Architecture

### Syscall Invocation Flow:

```
Userspace Application
        ↓
libtsynos Safe Wrapper
        ↓
Raw Syscall (asm!)
        ↓
x86_64 syscall Instruction
        ↓
SynOS Kernel Handler
        ↓
Return to Userspace
```

### Example Usage:

```rust
use libtsynos::*;

fn main() {
    // Get process ID
    let pid = getpid();

    // Write to stdout
    let message = b"Hello from SynOS!\n";
    write(1, message);

    // AI inference
    let input = b"network traffic data";
    let mut output = [0u8; 128];
    ai_inference(1, input, &mut output);

    // Threat detection
    let suspicious = b"eval($_POST['cmd'])";
    let threat_level = threat_detect(suspicious);

    if threat_level > 0 {
        threat_log(1001, 5, "PHP backdoor detected");
    }
}
```

---

## 🔐 Security Features

### Memory Safety
- All wrappers use safe Rust interfaces
- Bounds checking on all buffer operations
- No unsafe code in public API (except syscall invocation)

### Error Handling
- All syscalls return i64 (standard Linux convention)
- Negative values indicate errors
- Zero/positive values indicate success

### Type Safety
- Strong typing for all parameters
- Enum-based syscall numbers
- Const generics for buffer sizes

---

## 📊 Test Coverage

| Category | Syscalls | Test Program | Status |
|----------|----------|--------------|--------|
| Core System | 10 | test_core_syscalls | ✅ Complete |
| Networking | 10 | test_network_syscalls | ✅ Complete |
| Security | 7 | test_security_syscalls | ✅ Complete |
| AI & Consciousness | 6 | test_ai_syscalls | ✅ Complete |
| Advanced | 10 | test_advanced_syscalls | ✅ Complete |
| Integration | All | test_integration_full | ✅ Complete |

**Total:** 43/43 syscalls tested (100% coverage)

---

## 🚀 Performance

### Syscall Overhead:
- Direct `syscall` instruction (minimal overhead)
- No dynamic dispatch
- Inlined wrappers for hot paths
- Zero-cost abstractions

### Benchmarks (estimated):
- Simple syscall (getpid): ~50-100ns
- Network syscall (send/recv): ~1-5μs
- AI syscall (inference): ~100μs-1ms (depending on model)
- Security syscall (threat_detect): ~10-100μs

---

## 📖 API Documentation

### Core System Calls

```rust
pub fn exit(code: i32) -> !
pub fn write(fd: i32, buf: &[u8]) -> i64
pub fn read(fd: i32, buf: &mut [u8]) -> i64
pub fn open(path: &str, flags: u64) -> i64
pub fn close(fd: i32) -> i64
pub fn fork() -> i64
pub fn exec(path: &str, args: &[&str]) -> i64
pub fn wait(pid: i32) -> i64
pub fn getpid() -> i64
pub fn sleep(ms: u64) -> i64
```

### Networking

```rust
pub fn socket(domain: u32, socket_type: u32, protocol: u32) -> i64
pub fn bind(sockfd: i32, addr: &[u8]) -> i64
pub fn listen(sockfd: i32, backlog: i32) -> i64
pub fn accept(sockfd: i32) -> i64
pub fn connect(sockfd: i32, addr: &[u8]) -> i64
pub fn send(sockfd: i32, buf: &[u8], flags: u32) -> i64
pub fn recv(sockfd: i32, buf: &mut [u8], flags: u32) -> i64
pub fn sendto(sockfd: i32, buf: &[u8], flags: u32, addr: &[u8]) -> i64
pub fn recvfrom(sockfd: i32, buf: &mut [u8], flags: u32, addr: &mut [u8]) -> i64
pub fn getsockopt(sockfd: i32, level: u32, optname: u32) -> i64
```

### Security & Threat Detection

```rust
pub fn threat_detect(data: &[u8]) -> i64
pub fn threat_log(threat_id: u64, severity: u32, message: &str) -> i64
pub fn threat_query(query: &str, results: &mut [u8]) -> i64
pub fn security_audit(target: &str, audit_type: u32) -> i64
pub fn access_control(resource: &str, action: u32, user: u32) -> i64
pub fn crypto_op(op: u32, data: &[u8], key: &[u8]) -> i64
pub fn secure_random(buf: &mut [u8]) -> i64
```

### AI & Consciousness

```rust
pub fn ai_inference(model_id: u64, input: &[u8], output: &mut [u8]) -> i64
pub fn ai_train(model_id: u64, training_data: &[u8], epochs: u32) -> i64
pub fn consciousness_query(query: &str, result: &mut [u8]) -> i64
pub fn consciousness_update(update: &[u8]) -> i64
pub fn pattern_recognize(data: &[u8], pattern_type: u32) -> i64
pub fn decision_make(context: &[u8], options: &[u8]) -> i64
```

### Advanced Features

```rust
pub fn memory_map(addr: u64, length: u64, prot: u32, flags: u32) -> i64
pub fn memory_unmap(addr: u64, length: u64) -> i64
pub fn memory_protect(addr: u64, length: u64, prot: u32) -> i64
pub fn signal_register(signal: u32, handler: u64) -> i64
pub fn signal_send(pid: i32, signal: u32) -> i64
pub fn time_get() -> i64
pub fn time_set(time: u64) -> i64
pub fn process_priority(pid: i32, priority: i32) -> i64
pub fn thread_create(entry: u64, arg: u64) -> i64
pub fn thread_join(tid: i32) -> i64
```

---

## 🔬 Development

### Adding New Syscalls:

1. Add to `SyscallNumber` enum in `libtsynos/src/lib.rs`
2. Implement safe wrapper function
3. Add test in appropriate test program
4. Update this README

### Debugging:

Enable verbose output:
```bash
RUST_LOG=debug cargo run --bin test_integration_full
```

Trace syscalls:
```bash
strace -e trace=all ./target/release/test_integration_full
```

---

## 📈 Status

**Phase 3c: Userspace Integration - COMPLETE** ✅

- ✅ libtsynos library created (all 43 syscalls)
- ✅ 6 comprehensive test programs
- ✅ End-to-end integration testing
- ✅ Full syscall coverage (100%)
- ✅ Documentation complete

**Next:** Phase 4 - System Integration & Boot

---

## 🎯 Future Enhancements

- [ ] Async versions of blocking syscalls
- [ ] Higher-level abstractions (File, Socket, Process types)
- [ ] C FFI bindings for C/C++ applications
- [ ] Python bindings (ctypes/cffi)
- [ ] Performance benchmarking suite
- [ ] Fuzzing harness for syscall interface
- [ ] Documentation examples for each syscall

---

**Built with ❤️ for SynOS - The AI-Enhanced Cybersecurity OS**
