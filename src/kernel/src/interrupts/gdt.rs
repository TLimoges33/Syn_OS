// Syn OS Kernel - GDT Module
// Handles the Global Descriptor Table for the kernel

use x86_64::structures::gdt::{Descriptor, GlobalDescriptorTable, SegmentSelector};
use x86_64::structures::tss::TaskStateSegment;
use x86_64::VirtAddr;
use lazy_static::lazy_static;

// Stack index for the double fault handler
pub const DOUBLE_FAULT_IST_INDEX: u16 = 0;

// Define the TSS
lazy_static! {
    static ref TSS: TaskStateSegment = {
        let mut tss = TaskStateSegment::new();
        
        // Set up the interrupt stack table
        tss.interrupt_stack_table[DOUBLE_FAULT_IST_INDEX as usize] = {
            const STACK_SIZE: usize = 4096 * 5; // 20 KiB
            
            // Create a static buffer for the double fault stack
            static mut STACK: [u8; STACK_SIZE] = [0; STACK_SIZE];
            
            // Get the address of the top of the stack
            let stack_start = VirtAddr::from_ptr(&raw const STACK);
            let stack_end = stack_start + STACK_SIZE;
            
            // Return the top of the stack
            stack_end
        };
        
        tss
    };
}

// Define the GDT
lazy_static! {
    static ref GDT: (GlobalDescriptorTable, Selectors) = {
        let mut gdt = GlobalDescriptorTable::new();
        
        // Add segments to the GDT
        let code_selector = gdt.add_entry(Descriptor::kernel_code_segment());
        let data_selector = gdt.add_entry(Descriptor::kernel_data_segment());
        let tss_selector = gdt.add_entry(Descriptor::tss_segment(&TSS));
        
        // Return the GDT and segment selectors
        (gdt, Selectors { 
            code_selector,
            data_selector,
            tss_selector 
        })
    };
}

// Store segment selectors
pub struct Selectors {
    pub code_selector: SegmentSelector,
    pub data_selector: SegmentSelector,
    pub tss_selector: SegmentSelector,
}

// Initialize the GDT
pub fn init() {
    use x86_64::instructions::tables::load_tss;
    use x86_64::instructions::segmentation::{CS, DS, SS, Segment};
    
    // Load the GDT
    GDT.0.load();
    
    // Update segment registers
    unsafe {
        CS::set_reg(GDT.1.code_selector);
        DS::set_reg(GDT.1.data_selector);
        SS::set_reg(GDT.1.data_selector);
        load_tss(GDT.1.tss_selector);
    }
    
    crate::println!("🔧 GDT initialized");
}
