# 📞 System Call Reference

**Quick Reference**: SynOS syscall interface  
**Full Documentation**: See [SYSCALL_INTERFACE_DOCUMENTATION.md](../SYSCALL_INTERFACE_DOCUMENTATION.md)

---

## Overview

SynOS implements 243 system calls:
- 200+ POSIX-compatible syscalls
- 43 SynOS-specific extensions

---

## Common Syscalls

### File Operations

| Syscall | Number | Description |
|---------|--------|-------------|
| `open` | 2 | Open file |
| `read` | 0 | Read from file descriptor |
| `write` | 1 | Write to file descriptor |
| `close` | 3 | Close file descriptor |
| `lseek` | 8 | Reposition file offset |

### Process Management

| Syscall | Number | Description |
|---------|--------|-------------|
| `fork` | 57 | Create child process |
| `exec` | 59 | Execute program |
| `exit` | 60 | Terminate process |
| `wait` | 61 | Wait for child |
| `getpid` | 39 | Get process ID |

### AI Operations (SynOS-specific)

| Syscall | Number | Description |
|---------|--------|-------------|
| `ai_init` | 400 | Initialize AI engine |
| `ai_infer` | 401 | Run inference |
| `ai_train` | 402 | Train model |
| `ai_eval` | 403 | Evaluate model |

---

## Usage Examples

### C Example

```c
#include <synos/syscall.h>

int main() {
    // Open file
    int fd = syscall(SYS_open, "/path/file", O_RDONLY);
    
    // Read data
    char buf[1024];
    ssize_t n = syscall(SYS_read, fd, buf, sizeof(buf));
    
    // AI inference
    ai_handle_t ai = syscall(SYS_ai_init, "model.onnx", 0);
    syscall(SYS_ai_infer, ai, input, output);
    
    return 0;
}
```

### Rust Example

```rust
use synos_sys::*;

fn main() {
    unsafe {
        let fd = syscall!(OPEN, c"/path/file", O_RDONLY);
        let mut buf = [0u8; 1024];
        let n = syscall!(READ, fd, buf.as_mut_ptr(), buf.len());
    }
}
```

---

## Full Documentation

For complete syscall documentation including:
- All 243 syscalls
- Parameters and return values
- Error codes
- Architecture-specific details
- Performance characteristics

See: [SYSCALL_INTERFACE_DOCUMENTATION.md](../SYSCALL_INTERFACE_DOCUMENTATION.md)

---

**Last Updated**: October 4, 2025
