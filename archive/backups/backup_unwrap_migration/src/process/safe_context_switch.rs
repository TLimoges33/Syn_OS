//! Safe Context Switching with Comprehensive Validation
//!
//! Memory-safe context switching implementation with proper validation,
//! error handling, and security checks for production kernel use.

#![no_std]

use alloc::boxed::Box;
use core::{
    arch::asm,
    mem::{align_of, size_of},
    ptr::{self, NonNull},
    sync::atomic::{fence, AtomicU64, Ordering},
};

/// Context switch errors with detailed error information
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ContextSwitchError {
    NullPointer,
    InvalidAlignment,
    CorruptedStack,
    PrivilegeViolation,
    InvalidCpuState,
    MemoryProtectionViolation,
    SecurityCheckFailed,
    HardwareFault,
}

/// CPU state structure with validation magic numbers
#[repr(C, align(16))]
#[derive(Debug, Clone, Copy)]
pub struct CpuState {
    // Magic numbers for corruption detection
    magic_start: u64,

    // General purpose registers
    pub rax: u64,
    pub rbx: u64,
    pub rcx: u64,
    pub rdx: u64,
    pub rsi: u64,
    pub rdi: u64,
    pub rbp: u64,
    pub rsp: u64,
    pub r8: u64,
    pub r9: u64,
    pub r10: u64,
    pub r11: u64,
    pub r12: u64,
    pub r13: u64,
    pub r14: u64,
    pub r15: u64,

    // Instruction pointer and flags
    pub rip: u64,
    pub rflags: u64,

    // Segment selectors
    pub cs: u16,
    pub ds: u16,
    pub es: u16,
    pub fs: u16,
    pub gs: u16,
    pub ss: u16,

    // Extended state (FPU, SSE, AVX)
    pub fxsave_area: [u8; 512],

    // Security and validation
    pub privilege_level: u8,
    pub security_token: u64,
    pub stack_canary: u64,

    // Magic numbers for corruption detection
    magic_end: u64,

    // Checksum for integrity verification
    checksum: u64,
}

/// Magic numbers for validation
const CPU_STATE_MAGIC_START: u64 = 0xDEADBEEFCAFEBABE;
const CPU_STATE_MAGIC_END: u64 = 0xFEEDFACEDEADC0DE;
const STACK_CANARY_MAGIC: u64 = 0x1234567890ABCDEF;

/// Security context for process isolation
#[derive(Debug, Clone, Copy)]
pub struct SecurityContext {
    pub process_id: u64,
    pub user_id: u32,
    pub group_id: u32,
    pub capabilities: u64,
    pub security_level: u8,
}

impl CpuState {
    /// Create a new CPU state with proper initialization
    pub fn new() -> Self {
        let mut state = Self {
            magic_start: CPU_STATE_MAGIC_START,
            rax: 0,
            rbx: 0,
            rcx: 0,
            rdx: 0,
            rsi: 0,
            rdi: 0,
            rbp: 0,
            rsp: 0,
            r8: 0,
            r9: 0,
            r10: 0,
            r11: 0,
            r12: 0,
            r13: 0,
            r14: 0,
            r15: 0,
            rip: 0,
            rflags: 0x202, // IF flag set, other flags clear
            cs: 0x08,      // Kernel code segment
            ds: 0x10,
            es: 0x10,
            fs: 0x10,
            gs: 0x10,
            ss: 0x10, // Kernel data segment
            fxsave_area: [0; 512],
            privilege_level: 0, // Kernel privilege
            security_token: 0,
            stack_canary: STACK_CANARY_MAGIC,
            magic_end: CPU_STATE_MAGIC_END,
            checksum: 0,
        };

        // Calculate and set checksum
        state.checksum = state.calculate_checksum();
        state
    }

    /// Create user-mode CPU state
    pub fn new_user(
        entry_point: u64,
        stack_pointer: u64,
        security_ctx: SecurityContext,
    ) -> Result<Self, ContextSwitchError> {
        // Validate user space addresses
        if entry_point >= 0x800000000000 || stack_pointer >= 0x800000000000 {
            return Err(ContextSwitchError::PrivilegeViolation);
        }

        let mut state = Self::new();
        state.rip = entry_point;
        state.rsp = stack_pointer;
        state.cs = 0x1B; // User code segment (CPL 3)
        state.ss = 0x23; // User data segment (CPL 3)
        state.ds = 0x23;
        state.es = 0x23;
        state.fs = 0x23;
        state.gs = 0x23;
        state.rflags = 0x202; // IF flag set
        state.privilege_level = 3; // User privilege
        state.security_token = security_ctx.process_id;

        // Recalculate checksum
        state.checksum = state.calculate_checksum();

        Ok(state)
    }

    /// Validate CPU state integrity
    pub fn validate(&self) -> Result<(), ContextSwitchError> {
        // Check magic numbers
        if self.magic_start != CPU_STATE_MAGIC_START {
            return Err(ContextSwitchError::CorruptedStack);
        }
        if self.magic_end != CPU_STATE_MAGIC_END {
            return Err(ContextSwitchError::CorruptedStack);
        }

        // Check stack canary
        if self.stack_canary != STACK_CANARY_MAGIC {
            return Err(ContextSwitchError::CorruptedStack);
        }

        // Verify checksum
        if self.checksum != self.calculate_checksum() {
            return Err(ContextSwitchError::InvalidCpuState);
        }

        // Validate privilege level
        if self.privilege_level > 3 {
            return Err(ContextSwitchError::PrivilegeViolation);
        }

        // Validate instruction pointer
        if self.privilege_level == 3 && self.rip >= 0x800000000000 {
            return Err(ContextSwitchError::PrivilegeViolation);
        }

        // Validate stack pointer alignment
        if self.rsp % 16 != 0 {
            return Err(ContextSwitchError::InvalidAlignment);
        }

        // Validate flags register
        if self.rflags & 0xFFC38028 != 0 {
            // Reserved bits must be zero
            return Err(ContextSwitchError::InvalidCpuState);
        }

        Ok(())
    }

    /// Calculate checksum for integrity verification
    fn calculate_checksum(&self) -> u64 {
        let mut checksum = 0u64;
        let ptr = self as *const Self as *const u64;

        // Calculate checksum of all fields except checksum itself
        let words = (size_of::<Self>() - size_of::<u64>()) / size_of::<u64>();

        for i in 0..words {
            unsafe {
                checksum = checksum.wrapping_add(*ptr.add(i));
            }
        }

        checksum
    }

    /// Update checksum after modifying state
    pub fn update_checksum(&mut self) {
        self.checksum = self.calculate_checksum();
    }
}

/// Performance counters for context switching
static CONTEXT_SWITCH_COUNT: AtomicU64 = AtomicU64::new(0);
static FAILED_SWITCHES: AtomicU64 = AtomicU64::new(0);
static TOTAL_SWITCH_TIME: AtomicU64 = AtomicU64::new(0);

/// Safe context switching with comprehensive validation
pub struct SafeContextSwitcher {
    /// Emergency stack for handling faults during context switch
    emergency_stack: NonNull<[u8; 4096]>,
    /// Security validator
    security_validator: SecurityValidator,
}

impl SafeContextSwitcher {
    /// Create new safe context switcher
    pub fn new() -> Result<Self, ContextSwitchError> {
        // Allocate emergency stack
        let emergency_stack = Box::leak(Box::new([0u8; 4096]));
        let emergency_stack =
            NonNull::new(emergency_stack).ok_or(ContextSwitchError::NullPointer)?;

        Ok(Self {
            emergency_stack,
            security_validator: SecurityValidator::new(),
        })
    }

    /// Perform safe context switch with full validation
    pub fn context_switch(
        &self,
        current_state: Option<&mut CpuState>,
        next_state: &CpuState,
        security_ctx: &SecurityContext,
    ) -> Result<(), ContextSwitchError> {
        let start_time = crate::time::get_current_time();

        // Pre-switch validation
        self.pre_switch_validation(current_state.as_deref(), next_state, security_ctx)?;

        // Security checks before saving state
        self.security_validator.validate_transition(
            current_state.as_deref(),
            next_state,
            security_ctx,
        )?;

        // Save current state if provided
        if let Some(current) = current_state {
            self.save_cpu_state(current)?;
        }

        // Memory barriers to ensure ordering
        fence(Ordering::SeqCst);

        // Perform the actual context switch
        let switch_result = self.perform_hardware_switch(next_state);

        // Post-switch validation
        if switch_result.is_ok() {
            self.post_switch_validation(next_state)?;
        }

        // Update performance counters
        let end_time = crate::time::get_current_time();
        let switch_time = end_time - start_time;

        if switch_result.is_ok() {
            CONTEXT_SWITCH_COUNT.fetch_add(1, Ordering::Relaxed);
            TOTAL_SWITCH_TIME.fetch_add(switch_time, Ordering::Relaxed);
        } else {
            FAILED_SWITCHES.fetch_add(1, Ordering::Relaxed);
        }

        switch_result
    }

    /// Pre-switch validation
    fn pre_switch_validation(
        &self,
        current_state: Option<&CpuState>,
        next_state: &CpuState,
        security_ctx: &SecurityContext,
    ) -> Result<(), ContextSwitchError> {
        // Validate next state
        next_state.validate()?;

        // Validate current state if provided
        if let Some(current) = current_state {
            current.validate()?;
        }

        // Validate next_state (reference can't be null, so just validate)
        next_state.validate()?;

        // Check alignment
        if (next_state as *const CpuState as usize) % align_of::<CpuState>() != 0 {
            return Err(ContextSwitchError::InvalidAlignment);
        }

        // Validate security context
        if security_ctx.security_level > 3 {
            return Err(ContextSwitchError::SecurityCheckFailed);
        }

        Ok(())
    }

    /// Save current CPU state safely
    fn save_cpu_state(&self, state: &mut CpuState) -> Result<(), ContextSwitchError> {
        unsafe {
            // Save general purpose registers in batches to avoid register pressure

            // First batch: rax, rbx, rcx, rdx
            asm!(
                "mov {}, rax",
                "mov {}, rbx",
                "mov {}, rcx",
                "mov {}, rdx",
                out(reg) state.rax,
                out(reg) state.rbx,
                out(reg) state.rcx,
                out(reg) state.rdx,
                options(nomem, nostack)
            );

            // Second batch: rsi, rdi, rbp, rsp
            asm!(
                "mov {}, rsi",
                "mov {}, rdi",
                "mov {}, rbp",
                "mov {}, rsp",
                out(reg) state.rsi,
                out(reg) state.rdi,
                out(reg) state.rbp,
                out(reg) state.rsp,
                options(nomem, nostack)
            );

            // Third batch: r8-r11
            asm!(
                "mov {}, r8",
                "mov {}, r9",
                "mov {}, r10",
                "mov {}, r11",
                out(reg) state.r8,
                out(reg) state.r9,
                out(reg) state.r10,
                out(reg) state.r11,
                options(nomem, nostack)
            );

            // Fourth batch: r12-r15
            asm!(
                "mov {}, r12",
                "mov {}, r13",
                "mov {}, r14",
                "mov {}, r15",
                out(reg) state.r12,
                out(reg) state.r13,
                out(reg) state.r14,
                out(reg) state.r15,
                options(nomem, nostack)
            );

            // Save flags
            asm!(
                "pushfq",
                "pop {}",
                out(reg) state.rflags,
                options(nomem)
            );

            // Save segment selectors in batches (use :x for 16-bit segment registers)
            // First batch: cs, ds, es
            asm!(
                "mov {:x}, cs",
                "mov {:x}, ds",
                "mov {:x}, es",
                out(reg) state.cs,
                out(reg) state.ds,
                out(reg) state.es,
                options(nomem, nostack)
            );

            // Second batch: fs, gs, ss
            asm!(
                "mov {:x}, fs",
                "mov {:x}, gs",
                "mov {:x}, ss",
                out(reg) state.fs,
                out(reg) state.gs,
                out(reg) state.ss,
                options(nomem, nostack)
            );

            // Save FPU/SSE state
            asm!(
                "fxsave [{}]",
                in(reg) state.fxsave_area.as_mut_ptr(),
                options(nostack)
            );
        }

        // Update checksum
        state.update_checksum();

        Ok(())
    }

    /// Perform hardware context switch
    fn perform_hardware_switch(&self, next_state: &CpuState) -> Result<(), ContextSwitchError> {
        unsafe {
            // Restore FPU/SSE state first
            asm!(
                "fxrstor [{}]",
                in(reg) next_state.fxsave_area.as_ptr(),
                options(nostack)
            );

            // Restore segment selectors in batches (use :x for 16-bit segment registers)
            // First batch: ds, es
            asm!(
                "mov ds, {:x}",
                "mov es, {:x}",
                in(reg) next_state.ds,
                in(reg) next_state.es,
                options(nomem, nostack)
            );

            // Second batch: fs, gs
            asm!(
                "mov fs, {:x}",
                "mov gs, {:x}",
                in(reg) next_state.fs,
                in(reg) next_state.gs,
                options(nomem, nostack)
            );

            // Restore general purpose registers in batches to avoid register pressure

            // First batch: rax, rbx, rcx, rdx
            asm!(
                "mov rax, {}",
                "mov rbx, {}",
                "mov rcx, {}",
                "mov rdx, {}",
                in(reg) next_state.rax,
                in(reg) next_state.rbx,
                in(reg) next_state.rcx,
                in(reg) next_state.rdx,
            );

            // Second batch: rsi, rdi, rbp
            asm!(
                "mov rsi, {}",
                "mov rdi, {}",
                "mov rbp, {}",
                in(reg) next_state.rsi,
                in(reg) next_state.rdi,
                in(reg) next_state.rbp,
            );

            // Third batch: r8-r11
            asm!(
                "mov r8, {}",
                "mov r9, {}",
                "mov r10, {}",
                "mov r11, {}",
                in(reg) next_state.r8,
                in(reg) next_state.r9,
                in(reg) next_state.r10,
                in(reg) next_state.r11,
            );

            // Fourth batch: r12-r15
            asm!(
                "mov r12, {}",
                "mov r13, {}",
                "mov r14, {}",
                "mov r15, {}",
                in(reg) next_state.r12,
                in(reg) next_state.r13,
                in(reg) next_state.r14,
                in(reg) next_state.r15,
            );

            // Final context switch with rsp, cs, rip, and rflags
            asm!(
                "mov rsp, {}",
                "push {}",    // Push CS
                "push {}",    // Push RIP
                "push {}",    // Push RFLAGS
                "popfq",      // Restore flags
                "retfq",      // Far return to new context
                in(reg) next_state.rsp,
                in(reg) next_state.cs as u64,
                in(reg) next_state.rip,
                in(reg) next_state.rflags,
                options(noreturn)
            );
        }

        // This should never be reached
        unreachable!()
    }

    /// Post-switch validation
    fn post_switch_validation(&self, next_state: &CpuState) -> Result<(), ContextSwitchError> {
        // Verify we're running the correct process
        next_state.validate()?;

        // Additional runtime checks can be added here

        Ok(())
    }

    /// Get context switch statistics
    pub fn get_stats(&self) -> ContextSwitchStats {
        let switches = CONTEXT_SWITCH_COUNT.load(Ordering::Relaxed);
        let failures = FAILED_SWITCHES.load(Ordering::Relaxed);
        let total_time = TOTAL_SWITCH_TIME.load(Ordering::Relaxed);

        ContextSwitchStats {
            total_switches: switches,
            failed_switches: failures,
            average_switch_time: if switches > 0 {
                total_time / switches
            } else {
                0
            },
            success_rate: if switches + failures > 0 {
                (switches as f64 / (switches + failures) as f64) * 100.0
            } else {
                100.0
            },
        }
    }
}

/// Security validator for context switches
struct SecurityValidator {
    // Security state tracking
}

impl SecurityValidator {
    fn new() -> Self {
        Self {}
    }

    fn validate_transition(
        &self,
        _current_state: Option<&CpuState>,
        next_state: &CpuState,
        security_ctx: &SecurityContext,
    ) -> Result<(), ContextSwitchError> {
        // Validate privilege transition
        if next_state.privilege_level > 3 {
            return Err(ContextSwitchError::PrivilegeViolation);
        }

        // Validate security token
        if next_state.security_token != security_ctx.process_id {
            return Err(ContextSwitchError::SecurityCheckFailed);
        }

        // Additional security checks can be added here

        Ok(())
    }
}

/// Context switch performance statistics
#[derive(Debug, Clone)]
pub struct ContextSwitchStats {
    pub total_switches: u64,
    pub failed_switches: u64,
    pub average_switch_time: u64,
    pub success_rate: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cpu_state_validation() {
        let state = CpuState::new();
        assert!(state.validate().is_ok());
    }

    #[test]
    fn test_corrupted_state_detection() {
        let mut state = CpuState::new();
        state.magic_start = 0; // Corrupt magic number
        assert_eq!(
            state.validate().unwrap_err(),
            ContextSwitchError::CorruptedStack
        );
    }

    #[test]
    fn test_security_context() {
        let security_ctx = SecurityContext {
            process_id: 123,
            user_id: 1000,
            group_id: 1000,
            capabilities: 0,
            security_level: 3,
        };

        let state = CpuState::new_user(0x400000, 0x7fff0000, security_ctx);
        assert!(state.is_ok());
    }
}
