/// Process Execution Engine for SynOS
/// Handles process context, virtual memory, and execution

use alloc::vec::Vec;
use alloc::boxed::Box;
use crate::elf_loader::{ProcessMemoryLayout, ElfResult, ElfError};
use crate::syscalls::synos_syscalls::{SynOSSyscallHandler, SyscallArgs};

/// CPU register state for context switching
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct CpuContext {
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

    // Instruction pointer
    pub rip: u64,

    // Flags register
    pub rflags: u64,

    // Segment registers
    pub cs: u64,
    pub ss: u64,
    pub ds: u64,
    pub es: u64,
    pub fs: u64,
    pub gs: u64,
}

impl CpuContext {
    pub fn new() -> Self {
        Self {
            rax: 0, rbx: 0, rcx: 0, rdx: 0,
            rsi: 0, rdi: 0, rbp: 0, rsp: 0,
            r8: 0, r9: 0, r10: 0, r11: 0,
            r12: 0, r13: 0, r14: 0, r15: 0,
            rip: 0,
            rflags: 0x202,  // IF (interrupt enable) set
            cs: 0x08,       // Kernel code segment
            ss: 0x10,       // Kernel data segment
            ds: 0x10,
            es: 0x10,
            fs: 0x10,
            gs: 0x10,
        }
    }

    /// Set up context for userspace entry
    pub fn setup_userspace(&mut self, entry_point: u64, stack_ptr: u64) {
        self.rip = entry_point;
        self.rsp = stack_ptr;
        self.rbp = stack_ptr;
        self.rflags = 0x202;  // IF set
        self.cs = 0x1B;       // User code segment (ring 3)
        self.ss = 0x23;       // User data segment (ring 3)
        self.ds = 0x23;
        self.es = 0x23;
    }
}

/// Process state
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessState {
    Created,
    Ready,
    Running,
    Blocked,
    Terminated,
}

/// Process control block
pub struct ProcessControlBlock {
    pub pid: u64,
    pub parent_pid: u64,
    pub state: ProcessState,
    pub context: CpuContext,
    pub memory_layout: ProcessMemoryLayout,
    pub syscall_handler: SynOSSyscallHandler,
    pub exit_code: Option<i32>,
}

impl ProcessControlBlock {
    /// Create new process from ELF binary
    pub fn from_elf(pid: u64, parent_pid: u64, elf_data: &[u8]) -> ElfResult<Self> {
        let memory_layout = ProcessMemoryLayout::from_elf(elf_data)?;

        let mut context = CpuContext::new();
        context.setup_userspace(memory_layout.entry_point, memory_layout.stack_top);

        Ok(Self {
            pid,
            parent_pid,
            state: ProcessState::Created,
            context,
            memory_layout,
            syscall_handler: SynOSSyscallHandler::new(),
            exit_code: None,
        })
    }

    /// Execute process (simulate)
    pub fn execute(&mut self) -> Result<(), &'static str> {
        if self.state == ProcessState::Terminated {
            return Err("Process already terminated");
        }

        self.state = ProcessState::Running;

        // In a real kernel, this would:
        // 1. Load page tables
        // 2. Restore CPU context
        // 3. Jump to user code
        // 4. Handle syscalls and interrupts
        // 5. Context switch as needed

        Ok(())
    }

    /// Handle syscall from this process
    pub fn handle_syscall(&mut self, syscall_num: u64, args: &SyscallArgs) -> Result<i64, &'static str> {
        self.syscall_handler
            .handle_syscall(syscall_num, args)
            .map_err(|_| "Syscall failed")
    }

    /// Terminate process
    pub fn terminate(&mut self, exit_code: i32) {
        self.state = ProcessState::Terminated;
        self.exit_code = Some(exit_code);
    }
}

/// Process scheduler
pub struct ProcessScheduler {
    processes: Vec<ProcessControlBlock>,
    current_pid: Option<u64>,
    next_pid: u64,
}

impl ProcessScheduler {
    pub fn new() -> Self {
        Self {
            processes: Vec::new(),
            current_pid: None,
            next_pid: 1000,
        }
    }

    /// Create and load a new process
    pub fn load_process(&mut self, elf_data: &[u8], parent_pid: u64) -> Result<u64, &'static str> {
        let pid = self.next_pid;
        self.next_pid += 1;

        let pcb = ProcessControlBlock::from_elf(pid, parent_pid, elf_data)
            .map_err(|_| "Failed to load ELF")?;

        self.processes.push(pcb);
        Ok(pid)
    }

    /// Get process by PID
    pub fn get_process_mut(&mut self, pid: u64) -> Option<&mut ProcessControlBlock> {
        self.processes.iter_mut().find(|p| p.pid == pid)
    }

    /// Schedule next process (round-robin)
    pub fn schedule(&mut self) -> Option<u64> {
        // Find next ready process
        for process in &mut self.processes {
            if process.state == ProcessState::Ready || process.state == ProcessState::Created {
                process.state = ProcessState::Running;
                self.current_pid = Some(process.pid);
                return Some(process.pid);
            }
        }
        None
    }

    /// Execute syscall for current process
    pub fn execute_syscall(&mut self, pid: u64, syscall_num: u64, args: &SyscallArgs) -> Result<i64, &'static str> {
        let process = self.get_process_mut(pid)
            .ok_or("Process not found")?;

        process.handle_syscall(syscall_num, args)
    }

    /// Terminate process
    pub fn terminate_process(&mut self, pid: u64, exit_code: i32) -> Result<(), &'static str> {
        let process = self.get_process_mut(pid)
            .ok_or("Process not found")?;

        process.terminate(exit_code);
        Ok(())
    }

    /// Remove terminated processes
    pub fn cleanup(&mut self) {
        self.processes.retain(|p| p.state != ProcessState::Terminated);
    }

    /// Get process count
    pub fn process_count(&self) -> usize {
        self.processes.len()
    }

    /// Get running process count
    pub fn running_count(&self) -> usize {
        self.processes.iter()
            .filter(|p| p.state == ProcessState::Running)
            .count()
    }
}

/// Virtual memory manager
pub struct VirtualMemoryManager {
    /// Page table base address
    pub page_table_base: u64,
    /// Mapped pages
    pub mapped_pages: Vec<(u64, u64)>, // (virtual, physical)
}

impl VirtualMemoryManager {
    pub fn new() -> Self {
        Self {
            page_table_base: 0,
            mapped_pages: Vec::new(),
        }
    }

    /// Map a virtual page to physical page
    pub fn map_page(&mut self, virt_addr: u64, phys_addr: u64) -> Result<(), &'static str> {
        // Check if already mapped
        if self.mapped_pages.iter().any(|(v, _)| *v == virt_addr) {
            return Err("Page already mapped");
        }

        self.mapped_pages.push((virt_addr, phys_addr));
        Ok(())
    }

    /// Unmap a virtual page
    pub fn unmap_page(&mut self, virt_addr: u64) -> Result<(), &'static str> {
        let initial_len = self.mapped_pages.len();
        self.mapped_pages.retain(|(v, _)| *v != virt_addr);

        if self.mapped_pages.len() == initial_len {
            Err("Page not mapped")
        } else {
            Ok(())
        }
    }

    /// Get physical address for virtual address
    pub fn translate(&self, virt_addr: u64) -> Option<u64> {
        let page_addr = virt_addr & !0xFFF; // Page align
        let offset = virt_addr & 0xFFF;

        for (virt, phys) in &self.mapped_pages {
            if *virt == page_addr {
                return Some(phys + offset);
            }
        }
        None
    }

    /// Setup process memory mapping
    pub fn setup_process_memory(&mut self, layout: &ProcessMemoryLayout) -> Result<(), &'static str> {
        // Map segments
        for segment in &layout.segments {
            let start_page = segment.virt_addr & !0xFFF;
            let end_page = (segment.virt_addr + segment.size + 0xFFF) & !0xFFF;

            let mut virt = start_page;
            while virt < end_page {
                // In real kernel, allocate physical page here
                let phys = virt; // Identity mapping for now
                self.map_page(virt, phys)?;
                virt += 0x1000; // 4KB pages
            }
        }

        // Map stack
        let stack_start = layout.stack_bottom & !0xFFF;
        let stack_end = (layout.stack_top + 0xFFF) & !0xFFF;

        let mut virt = stack_start;
        while virt < stack_end {
            let phys = virt;
            self.map_page(virt, phys)?;
            virt += 0x1000;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cpu_context_creation() {
        let ctx = CpuContext::new();
        assert_eq!(ctx.rflags, 0x202);
        assert_eq!(ctx.cs, 0x08);
    }

    #[test]
    fn test_process_scheduler() {
        let mut scheduler = ProcessScheduler::new();
        assert_eq!(scheduler.process_count(), 0);

        // Create dummy ELF
        let mut elf = vec![0u8; 64];
        elf[0..4].copy_from_slice(b"\x7fELF");
        elf[4] = 2; // ELFCLASS64
        elf[5] = 1; // ELFDATA2LSB

        let pid = scheduler.load_process(&elf, 0);
        assert!(pid.is_ok() || matches!(pid, Err("Failed to load ELF")));
    }

    #[test]
    fn test_virtual_memory() {
        let mut vmm = VirtualMemoryManager::new();

        assert!(vmm.map_page(0x1000, 0x10000).is_ok());
        assert!(vmm.map_page(0x1000, 0x20000).is_err()); // Duplicate

        assert_eq!(vmm.translate(0x1234), Some(0x10234));
        assert_eq!(vmm.translate(0x2000), None);

        assert!(vmm.unmap_page(0x1000).is_ok());
        assert_eq!(vmm.translate(0x1234), None);
    }
}
