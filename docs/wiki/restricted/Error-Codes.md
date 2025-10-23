# ⚠️ Error Codes Reference

**Complete error code listing for SynOS**

---

## Standard POSIX Errors

| Code | Name | Description |
|------|------|-------------|
| 1 | `EPERM` | Operation not permitted |
| 2 | `ENOENT` | No such file or directory |
| 3 | `ESRCH` | No such process |
| 4 | `EINTR` | Interrupted system call |
| 5 | `EIO` | I/O error |
| 11 | `EAGAIN` | Try again |
| 12 | `ENOMEM` | Out of memory |
| 13 | `EACCES` | Permission denied |
| 22 | `EINVAL` | Invalid argument |

---

## SynOS-Specific Errors

| Code | Name | Description |
|------|------|-------------|
| 1000 | `EAIINIT` | AI initialization failed |
| 1001 | `EAIMODEL` | Invalid AI model |
| 1002 | `EAIINFER` | Inference failed |
| 1003 | `EAITRAIN` | Training error |
| 1010 | `ESECPOL` | Security policy violation |
| 1011 | `ESECAUTH` | Authentication failed |
| 1012 | `ESECCAP` | Missing capability |

---

## HTTP API Errors

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Auth required |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## Troubleshooting

### ENOMEM (Out of Memory)

**Causes**:
- Insufficient RAM
- Memory leak
- Too many processes

**Solutions**:
```bash
# Check memory
free -h

# Increase swap
sudo swapon -s

# Kill processes
pkill -9 process_name
```

### EACCES (Permission Denied)

**Causes**:
- Wrong user
- Missing capabilities
- SELinux denial

**Solutions**:
```bash
# Check permissions
ls -l file

# Fix ownership
sudo chown user:group file

# Check SELinux
sudo ausearch -m avc
```

---

**For more**: See system logs (`journalctl -xe`)
