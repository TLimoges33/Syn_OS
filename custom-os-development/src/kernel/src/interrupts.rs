// Syn OS Kernel - Interrupts Module
// Handles CPU interrupts for the kernel

use x86_64::structures::idt::{InterruptDescriptorTable, InterruptStackFrame, PageFaultErrorCode};
use lazy_static::lazy_static;
use crate::println;
use crate::gdt;

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
        
        idt
    };
}

// Initialize the IDT
pub fn init() {
    IDT.load();
    println!("🛡️ Interrupt handlers initialized");
}

// Breakpoint exception handler
extern "x86-interrupt" fn breakpoint_handler(stack_frame: InterruptStackFrame) {
    println!("EXCEPTION: BREAKPOINT\n{:#?}", stack_frame);
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
    
    println!("🔧 PAGE FAULT: Address {:?}, Error: {:?}", fault_address, error_code);
    
    // Try to handle the page fault with the global memory manager
    if let Some(memory_manager) = get_global_memory_manager() {
        let result = memory_manager.handle_page_fault(
            virtual_addr,
            error_code.bits(),
            stack_frame.instruction_pointer.as_u64(),
        );
        
        match result {
            Ok(()) => {
                println!("✅ Page fault handled successfully");
                // In a real implementation, we would return to user code here
                return;
            }
            Err(error) => {
                println!("❌ Page fault handling failed: {:?}", error);
                println!("   Instruction Pointer: {:?}", stack_frame.instruction_pointer);
                println!("   Error Code Bits: {:#b}", error_code.bits());
            }
        }
    } else {
        println!("⚠️  No global memory manager available");
    }
    
    // For now, halt on unrecoverable page fault
    println!("🚨 Page fault not recoverable - halting system");
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
