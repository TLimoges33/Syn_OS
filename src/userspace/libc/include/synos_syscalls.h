/*
 * SynOS System Call Interface Header
 * Provides system call definitions and wrapper functions
 */

#ifndef SYNOS_SYSCALLS_H
#define SYNOS_SYSCALLS_H

#include <stdint.h>
#include <stddef.h>
#include <sys/types.h>

// System call numbers (must match kernel definitions)
#define SYS_READ        0
#define SYS_WRITE       1
#define SYS_OPEN        2
#define SYS_CLOSE       3
#define SYS_STAT        4
#define SYS_FSTAT       5
#define SYS_LSTAT       6
#define SYS_POLL        7
#define SYS_LSEEK       8
#define SYS_MMAP        9
#define SYS_MPROTECT    10
#define SYS_MUNMAP      11
#define SYS_BRK         12
#define SYS_SBRK        214
#define SYS_FORK        57
#define SYS_EXECVE      59
#define SYS_EXIT        60
#define SYS_WAIT4       61
#define SYS_KILL        62
#define SYS_GETPID      39
#define SYS_GETPPID     110
#define SYS_MKDIR       83
#define SYS_RMDIR       84
#define SYS_UNLINK      87
#define SYS_CHMOD       90
#define SYS_CHOWN       92
#define SYS_GETCWD      79
#define SYS_CHDIR       80
#define SYS_TIME        201
#define SYS_GETTIMEOFDAY 96
#define SYS_NANOSLEEP   35

// System call wrappers (inline assembly for x86_64)
static inline long syscall0(long number) {
    long result;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number)
        : "rcx", "r11", "memory"
    );
    return result;
}

static inline long syscall1(long number, long arg1) {
    long result;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number), "D" (arg1)
        : "rcx", "r11", "memory"
    );
    return result;
}

static inline long syscall2(long number, long arg1, long arg2) {
    long result;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number), "D" (arg1), "S" (arg2)
        : "rcx", "r11", "memory"
    );
    return result;
}

static inline long syscall3(long number, long arg1, long arg2, long arg3) {
    long result;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number), "D" (arg1), "S" (arg2), "d" (arg3)
        : "rcx", "r11", "memory"
    );
    return result;
}

static inline long syscall4(long number, long arg1, long arg2, long arg3, long arg4) {
    long result;
    register long r10 __asm__("r10") = arg4;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number), "D" (arg1), "S" (arg2), "d" (arg3), "r" (r10)
        : "rcx", "r11", "memory"
    );
    return result;
}

static inline long syscall5(long number, long arg1, long arg2, long arg3, long arg4, long arg5) {
    long result;
    register long r10 __asm__("r10") = arg4;
    register long r8 __asm__("r8") = arg5;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number), "D" (arg1), "S" (arg2), "d" (arg3), "r" (r10), "r" (r8)
        : "rcx", "r11", "memory"
    );
    return result;
}

static inline long syscall6(long number, long arg1, long arg2, long arg3, long arg4, long arg5, long arg6) {
    long result;
    register long r10 __asm__("r10") = arg4;
    register long r8 __asm__("r8") = arg5;
    register long r9 __asm__("r9") = arg6;
    __asm__ volatile (
        "syscall"
        : "=a" (result)
        : "a" (number), "D" (arg1), "S" (arg2), "d" (arg3), "r" (r10), "r" (r8), "r" (r9)
        : "rcx", "r11", "memory"
    );
    return result;
}

#endif // SYNOS_SYSCALLS_H
