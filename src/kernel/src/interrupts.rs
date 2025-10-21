// Syn OS Kernel - Interrupts Module
// Handles CPU interrupts for the kernel

use x86_64::structures::idt::{InterruptDescriptorTable, InterruptStackFrame, PageFaultErrorCode};
use lazy_static::lazy_static;
use crate::gdt;
use alloc::vec::Vec;
use spin::Mutex;

pub type InterruptHandler = fn();

/// Interrupt manager for kernel interrupt handling
#[derive(Debug)]
pub struct InterruptManager {
    pub handlers: Vec<Option<InterruptHandler>>,
    pub enabled: bool,
}

lazy_static! {
    pub static ref INTERRUPT_MANAGER: Mutex<InterruptManager> = {
        Mutex::new(InterruptManager::new())
    };
}

impl InterruptManager {
    pub fn new() -> Self {
        Self {
            handlers: vec![None; 256], // 256 possible interrupt vectors
            enabled: true,
        }
    }
    
    pub fn register_handler(&mut self, vector: u8, handler: InterruptHandler) -> Result<(), &'static str> {
        if !self.enabled {
            return Err("Interrupt manager disabled");
        }
        
        if vector as usize >= self.handlers.len() {
            return Err("Invalid interrupt vector");
        }
        
        self.handlers[vector as usize] = Some(handler);
        Ok(())
    }
}

// Lazy static IDT
lazy_static! {
    static ref IDT: InterruptDescriptorTable = {
        let mut idt = InterruptDescriptorTable::new();

        // Set up breakpoint handler
        idt.breakpoint.set_handler_fn(breakpoint_handler);

        // Set up page fault handler
        unsafe {
            idt.page_fault.set_handler_fn(page_fault_handler)
                .set_stack_index(gdt::DOUBLE_FAULT_IST_INDEX);
        }

        // Set up double fault handler
        unsafe {
            idt.double_fault.set_handler_fn(double_fault_handler)
                .set_stack_index(gdt::DOUBLE_FAULT_IST_INDEX);
        }

        // Set up system call handler (INT 0x80)
        // SAFETY: syscall_entry is a valid interrupt handler function
        unsafe {
            idt[0x80].set_handler_addr(
                x86_64::VirtAddr::new(crate::syscalls::asm::syscall_entry as u64)
            ).set_privilege_level(x86_64::PrivilegeLevel::Ring3);
        }

        idt
    };
}

// Initialize the IDT
pub fn init() {
    IDT.load();
    crate::println!("🛡️ Interrupt handlers initialized");
}

// Breakpoint exception handler
extern "x86-interrupt" fn breakpoint_handler(stack_frame: InterruptStackFrame) {
    crate::println!("EXCEPTION: BREAKPOINT\n{:#?}", stack_frame);
}

// Page fault handler with consciousness integration
extern "x86-interrupt" fn page_fault_handler(
    stack_frame: InterruptStackFrame,
    error_code: PageFaultErrorCode,
) {
    use x86_64::registers::control::Cr2;
    use crate::memory::{VirtualAddress, get_global_memory_manager};
    
    let fault_address = Cr2::read();
    let virtual_addr = VirtualAddress::new(fault_address.as_u64() as usize);
    
    crate::println!("🔧 PAGE FAULT: Address {:?}, Error: {:?}", fault_address, error_code);
    
    // Try to handle the page fault with the global memory manager
    if let Some(memory_manager) = get_global_memory_manager() {
        let result = memory_manager.handle_page_fault(
            virtual_addr,
            error_code.bits(),
            stack_frame.instruction_pointer.as_u64(),
        );
        
        match result {
            Ok(()) => {
                crate::println!("✅ Page fault handled successfully");
                // In a real implementation, we would return to user code here
                return;
            }
            Err(error) => {
                crate::println!("❌ Page fault handling failed: {:?}", error);
                crate::println!("   Instruction Pointer: {:?}", stack_frame.instruction_pointer);
                crate::println!("   Error Code Bits: {:#b}", error_code.bits());
            }
        }
    } else {
        crate::println!("⚠️  No global memory manager available");
    }
    
    // For now, halt on unrecoverable page fault
    crate::println!("🚨 Page fault not recoverable - halting system");
    loop {
        x86_64::instructions::hlt();
    }
}

// Double fault handler
extern "x86-interrupt" fn double_fault_handler(
    stack_frame: InterruptStackFrame,
    _error_code: u64,
) -> ! {
    panic!("EXCEPTION: DOUBLE FAULT\n{:#?}", stack_frame);
}

/// Register system call handler in the IDT
/// This allows userspace to make system calls via INT 0x80
pub fn register_syscall_handler() -> Result<(), &'static str> {
    // The syscall handler is already registered in the IDT static initialization
    // This function exists for explicit initialization ordering
    Ok(())
}

/// Initialize interrupt system
pub fn init_interrupts() -> Result<(), &'static str> {
    // Initialize IDT and interrupt handling
    IDT.load();
    crate::println!("🔧 Interrupt system initialized");
    crate::println!("   - INT 0x80: System call handler");
    crate::println!("   - Breakpoint, Page Fault, Double Fault handlers active");
    Ok(())
}
