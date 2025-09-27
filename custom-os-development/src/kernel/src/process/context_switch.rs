/// Context Switching for SynOS Phase 5
/// Handles CPU context switching between processes

use crate::process::pcb::{CpuContext, ProcessId};
use core::arch::asm;
use crate::println;

/// Context switch result
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ContextSwitchResult {
    Success,
    InvalidProcess,
    MemoryError,
    HardwareError,
}

/// Context switcher - handles low-level context switching
pub struct ContextSwitcher {
    current_context: Option<CpuContext>,
}

impl ContextSwitcher {
    /// Create a new context switcher
    pub fn new() -> Self {
        Self {
            current_context: None,
        }
    }

    /// Perform context switch from current process to target process
    pub fn switch_context(
        &mut self,
        from_context: &mut CpuContext,
        to_context: &CpuContext,
    ) -> ContextSwitchResult {
        // Save current context
        self.save_current_context(from_context);

        // Load new context
        self.load_new_context(to_context);

        ContextSwitchResult::Success
    }

    /// Save CPU registers to context structure
    fn save_current_context(&mut self, context: &mut CpuContext) {
        unsafe {
            // Save general purpose registers in smaller chunks to avoid register pressure
            
            // Save first batch
            asm!(
                "mov {}, rax",
                "mov {}, rbx", 
                "mov {}, rcx",
                "mov {}, rdx",
                out(reg) context.rax,
                out(reg) context.rbx,
                out(reg) context.rcx,
                out(reg) context.rdx,
                options(preserves_flags)
            );

            // Save second batch
            asm!(
                "mov {}, rsi",
                "mov {}, rdi",
                "mov {}, rbp",
                "mov {}, rsp",
                out(reg) context.rsi,
                out(reg) context.rdi,
                out(reg) context.rbp,
                out(reg) context.rsp,
                options(preserves_flags)
            );

            // Save third batch
            asm!(
                "mov {}, r8",
                "mov {}, r9",
                "mov {}, r10",
                "mov {}, r11",
                out(reg) context.r8,
                out(reg) context.r9,
                out(reg) context.r10,
                out(reg) context.r11,
                options(preserves_flags)
            );

            // Save final batch
            asm!(
                "mov {}, r12",
                "mov {}, r13",
                "mov {}, r14",
                "mov {}, r15",
                out(reg) context.r12,
                out(reg) context.r13,
                out(reg) context.r14,
                out(reg) context.r15,
                options(preserves_flags)
            );

            // Save flags register
            asm!(
                "pushfq",
                "pop {}",
                out(reg) context.rflags,
            );

            // Save segment registers
            asm!(
                "mov {}, cs",
                "mov {}, ss", 
                "mov {}, ds",
                "mov {}, es",
                "mov {}, fs",
                "mov {}, gs",
                out(reg) context.cs,
                out(reg) context.ss,
                out(reg) context.ds,
                out(reg) context.es,
                out(reg) context.fs,
                out(reg) context.gs,
            );
        }

        self.current_context = Some(*context);
    }

    /// Load CPU registers from context structure
    fn load_new_context(&mut self, context: &CpuContext) {
        unsafe {
            // Load segment registers first
            asm!(
                "mov ds, {}",
                "mov es, {}",
                "mov fs, {}",
                "mov gs, {}",
                in(reg) context.ds,
                in(reg) context.es,
                in(reg) context.fs,
                in(reg) context.gs,
            );

            // Load flags register
            asm!(
                "push {}",
                "popfq",
                in(reg) context.rflags,
            );

            // Load general purpose registers in smaller chunks to avoid register pressure
            
            // Load first batch of registers
            asm!(
                "mov rax, {}",
                "mov rbx, {}",
                "mov rcx, {}", 
                "mov rdx, {}",
                in(reg) context.rax,
                in(reg) context.rbx,
                in(reg) context.rcx,
                in(reg) context.rdx,
            );

            // Load second batch
            asm!(
                "mov rsi, {}",
                "mov rdi, {}",
                "mov rbp, {}",
                "mov r8, {}",
                in(reg) context.rsi,
                in(reg) context.rdi,
                in(reg) context.rbp,
                in(reg) context.r8,
            );

            // Load third batch
            asm!(
                "mov r9, {}",
                "mov r10, {}",
                "mov r11, {}",
                "mov r12, {}",
                in(reg) context.r9,
                in(reg) context.r10,
                in(reg) context.r11,
                in(reg) context.r12,
            );

            // Load final batch
            asm!(
                "mov r13, {}",
                "mov r14, {}",
                "mov r15, {}",
                in(reg) context.r13,
                in(reg) context.r14,
                in(reg) context.r15,
            );

            // Load stack pointer last
            asm!(
                "mov rsp, {}",
                in(reg) context.rsp,
            );
        }
    }

    /// Get current saved context
    pub fn get_current_context(&self) -> Option<&CpuContext> {
        self.current_context.as_ref()
    }
}

/// Architecture-specific context switching functions
pub mod arch {
    use super::*;

    /// Perform low-level context switch with page table switching
    pub unsafe fn switch_context_with_page_table(
        from_context: *mut CpuContext,
        to_context: *const CpuContext,
        page_table_phys: u64,
    ) {
        // This would be implemented in assembly for optimal performance
        // For now, we'll use the high-level context switcher

        asm!(
            // Save current context
            "push rax",
            "push rbx", 
            "push rcx",
            "push rdx",
            "push rsi",
            "push rdi",
            "push rbp",
            "push r8",
            "push r9",
            "push r10",
            "push r11",
            "push r12",
            "push r13",
            "push r14",
            "push r15",
            "pushfq",

            // Switch page table
            "mov cr3, {}",

            // Load new context
            "popfq",
            "pop r15",
            "pop r14", 
            "pop r13",
            "pop r12",
            "pop r11",
            "pop r10",
            "pop r9",
            "pop r8",
            "pop rbp",
            "pop rdi",
            "pop rsi",
            "pop rdx",
            "pop rcx",
            "pop rbx",
            "pop rax",

            in(reg) page_table_phys,
            options(preserves_flags)
        );
    }

    /// Switch to user mode
    pub unsafe fn switch_to_user_mode(
        user_stack: u64,
        user_code: u64,
        user_data_segment: u16,
        user_code_segment: u16,
    ) {
        // For now, use a simplified user mode switch
        // This is a placeholder implementation that doesn't actually switch to user mode
        // In a real kernel, this would set up proper segment descriptors and privilege levels
        
        // TODO: Implement proper user mode switching with GDT segments
        println!("Warning: switch_to_user_mode not fully implemented");
        println!("Would switch to user code at 0x{:x} with stack at 0x{:x}", user_code, user_stack);
    }

    /// Return from user mode to kernel mode
    pub unsafe fn return_to_kernel_mode() {
        // This would be called from an interrupt handler
        // The interrupt handling mechanism would save user context
        // and restore kernel context
    }
}

/// High-level context switching interface
pub struct ProcessContextSwitcher {
    switcher: ContextSwitcher,
    current_pid: Option<ProcessId>,
}

impl ProcessContextSwitcher {
    /// Create new process context switcher
    pub fn new() -> Self {
        Self {
            switcher: ContextSwitcher::new(),
            current_pid: None,
        }
    }

    /// Switch from one process to another
    pub fn switch_processes(
        &mut self,
        from_pid: ProcessId,
        to_pid: ProcessId,
        from_context: &mut CpuContext,
        to_context: &CpuContext,
    ) -> ContextSwitchResult {
        // Perform the actual context switch
        let result = self.switcher.switch_context(from_context, to_context);

        if result == ContextSwitchResult::Success {
            self.current_pid = Some(to_pid);
        }

        result
    }

    /// Get currently running process ID
    pub fn current_process(&self) -> Option<ProcessId> {
        self.current_pid
    }

    /// Idle CPU (no process running)
    pub fn idle(&mut self) {
        self.current_pid = None;
        // Could put CPU in low power state here
    }
}

/// Global context switcher instances (one per CPU core)
static mut CONTEXT_SWITCHERS: Option<alloc::vec::Vec<ProcessContextSwitcher>> = None;

/// Initialize context switchers for all CPU cores
pub fn init_context_switchers(num_cores: usize) {
    unsafe {
        let mut switchers = alloc::vec::Vec::with_capacity(num_cores);
        for _ in 0..num_cores {
            switchers.push(ProcessContextSwitcher::new());
        }
        CONTEXT_SWITCHERS = Some(switchers);
    }
}

/// Get context switcher for specific CPU core
pub fn get_context_switcher(core_id: usize) -> Option<&'static mut ProcessContextSwitcher> {
    unsafe {
        if let Some(ref mut switchers) = CONTEXT_SWITCHERS {
            switchers.get_mut(core_id)
        } else {
            None
        }
    }
}

/// Perform context switch on current CPU core
pub fn switch_context(
    core_id: usize,
    from_pid: ProcessId,
    to_pid: ProcessId,
    from_context: &mut CpuContext,
    to_context: &CpuContext,
) -> ContextSwitchResult {
    if let Some(switcher) = get_context_switcher(core_id) {
        switcher.switch_processes(from_pid, to_pid, from_context, to_context)
    } else {
        ContextSwitchResult::InvalidProcess
    }
}

/// Timer interrupt handler for preemptive scheduling
pub fn timer_interrupt_handler(core_id: usize) {
    // This would be called by the timer interrupt
    // It would:
    // 1. Save current process context
    // 2. Call scheduler to get next process
    // 3. Perform context switch if needed
    
    // For now, this is a placeholder
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_context_switcher_creation() {
        let switcher = ContextSwitcher::new();
        assert!(switcher.current_context.is_none());
    }

    #[test]
    fn test_process_context_switcher() {
        let mut switcher = ProcessContextSwitcher::new();
        assert!(switcher.current_process().is_none());
        
        switcher.idle();
        assert!(switcher.current_process().is_none());
    }

    #[test]
    fn test_context_switcher_initialization() {
        init_context_switchers(4);
        
        // Test that we can get switchers for valid core IDs
        assert!(get_context_switcher(0).is_some());
        assert!(get_context_switcher(3).is_some());
        assert!(get_context_switcher(4).is_none());
    }
}
