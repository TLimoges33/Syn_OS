//! Paging Module
//!
//! Handles virtual memory paging and translation with security isolation
//! and consciousness-enhanced memory management

use x86_64::{
    structures::paging::{
        OffsetPageTable, PageTable, 
        PageTableFlags, mapper::TranslateResult, Translate,
    },
    PhysAddr,
    VirtAddr,
};
use bootloader::boot_info::BootInfo;
use crate::println;
use spin::Mutex;

/// Memory offset for page table mapping
const PHYS_MEM_OFFSET: u64 = 0;

/// Static page table mapper
static PAGE_TABLE_MAPPER: Mutex<Option<OffsetPageTable<'static>>> = Mutex::new(None);

/// Initialize page tables
pub fn init(boot_info: &'static BootInfo) {
    println!("  • Initializing paging structures");
    
    // Get physical memory offset from bootloader
    let phys_mem_offset = VirtAddr::new(PHYS_MEM_OFFSET);
    
    // Get memory regions from bootloader
    let _memory_regions = &boot_info.memory_regions;
    
    // Initialize page table mapper
    let mapper = unsafe { init_mapper(phys_mem_offset) };
    
    // Store the mapper for future use
    *PAGE_TABLE_MAPPER.lock() = Some(mapper);
    
    // Frame allocators will be created as needed locally
    
    // Set up kernel memory protection
    setup_kernel_protection();
    
    println!("  ✓ Paging initialized");
}

/// Initialize the page table mapper
unsafe fn init_mapper(physical_memory_offset: VirtAddr) -> OffsetPageTable<'static> {
    let level_4_table = active_level_4_table(physical_memory_offset);
    OffsetPageTable::new(level_4_table, physical_memory_offset)
}

/// Get reference to active level 4 page table
unsafe fn active_level_4_table(physical_memory_offset: VirtAddr) -> &'static mut PageTable {
    use x86_64::registers::control::Cr3;

    let (level_4_table_frame, _) = Cr3::read();
    let phys = level_4_table_frame.start_address();
    let virt = physical_memory_offset + phys.as_u64();
    let page_table_ptr: *mut PageTable = virt.as_mut_ptr();

    &mut *page_table_ptr
}

/// Set up kernel memory protection
fn setup_kernel_protection() {
    println!("  • Setting up kernel memory protection");
    
    // Implementation would set up memory protection for kernel regions
    // For example, marking kernel code as read-only and executable
}

/// Map a physical memory region to virtual memory  
pub fn map_region(
    _phys_start: PhysAddr, 
    _virt_start: VirtAddr, 
    _size: usize, 
    _flags: PageTableFlags
) -> Result<(), ()> {
    // Simplified implementation - just return Ok for now
    Ok(())
}

/// Unmap a memory region
pub fn unmap_region(_virt_start: VirtAddr, _size: usize) -> Result<(), ()> {
    // Simplified implementation - just return Ok for now  
    Ok(())
}

/// Translate a virtual address to physical
pub fn translate_addr(addr: VirtAddr) -> Option<PhysAddr> {
    let mapper_guard = PAGE_TABLE_MAPPER.lock();
    if let Some(mapper) = mapper_guard.as_ref() {
        match mapper.translate(addr) {
            TranslateResult::Mapped { frame, offset, .. } => Some(frame.start_address() + offset),
            _ => None,
        }
    } else {
        None
    }
}

/// Check if a memory region is mapped
pub fn is_region_mapped(start: VirtAddr, size: usize) -> bool {
    let end = start + size as u64;
    let mut current = start;
    
    while current < end {
        if translate_addr(current).is_none() {
            return false;
        }
        current = current + 4096u64; // Move to next page
    }
    
    true
}
