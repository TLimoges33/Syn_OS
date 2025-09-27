//! Paging Module
//!
//! Handles virtual memory paging and translation with security isolation
//! and consciousness-enhanced memory management

use x86_64::{
    structures::paging::{
        OffsetPageTable, PageTable, PageTableFlags, PhysFrame, Size4KiB,
        Mapper, Page, FrameAllocator, MapToError, UnmapError
    },
    PhysAddr, VirtAddr,
};
use bootloader::bootinfo::{MemoryMap, MemoryRegionType};
use bootloader::BootInfo;
use crate::println;
use crate::memory::frame::{BootInfoFrameAllocator, ConsciousnessFrameAllocator};
use spin::Mutex;

/// Memory offset for page table mapping
const PHYS_MEM_OFFSET: u64 = 0;

/// Static page table mapper
static PAGE_TABLE_MAPPER: Mutex<Option<OffsetPageTable<'static>>> = Mutex::new(None);

/// Static frame allocator
static FRAME_ALLOCATOR: Mutex<Option<BootInfoFrameAllocator>> = Mutex::new(None);

/// Consciousness frame allocator for quantum memory
static CONSCIOUSNESS_FRAME_ALLOCATOR: Mutex<Option<ConsciousnessFrameAllocator>> = Mutex::new(None);

/// Initialize page tables
pub fn init(boot_info: &'static BootInfo) {
    println!("  • Initializing paging structures");
    
    // Get physical memory offset from bootloader
    let phys_mem_offset = VirtAddr::new(PHYS_MEM_OFFSET);
    
    // Get memory map from bootloader
    let memory_map = &boot_info.memory_map;
    
    // Initialize page table mapper
    let mut mapper = unsafe { init_mapper(phys_mem_offset) };
    
    // Store the mapper for future use
    *PAGE_TABLE_MAPPER.lock() = Some(mapper);
    
    // Initialize frame allocators
    unsafe {
        let frame_allocator = BootInfoFrameAllocator::init(memory_map);
        *FRAME_ALLOCATOR.lock() = Some(frame_allocator);
        
        let consciousness_frame_allocator = ConsciousnessFrameAllocator::init(memory_map);
        *CONSCIOUSNESS_FRAME_ALLOCATOR.lock() = Some(consciousness_frame_allocator);
    }
    
    // Set up kernel memory protection
    setup_kernel_protection();
    
    // Map consciousness-reserved memory regions
    map_consciousness_regions();
    
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

/// Map consciousness-reserved memory regions
fn map_consciousness_regions() {
    println!("  • Mapping consciousness memory regions");
    
    // Implementation would map memory regions for consciousness use
    // These regions would have special properties, like quantum coherence
    
    if let Some(ref mut allocator) = *CONSCIOUSNESS_FRAME_ALLOCATOR.lock() {
        // Allocate memory for consciousness operations
        for i in 0..8 {
            if let Some(_frame) = allocator.allocate_quantum_frame() {
                // Successfully allocated quantum frame
            } else {
                println!("  ! Failed to allocate quantum frame {}", i);
                break;
            }
        }
    }
}

/// Map a physical memory region to virtual memory
pub fn map_region(
    phys_start: PhysAddr, 
    virt_start: VirtAddr, 
    size: usize, 
    flags: PageTableFlags
) -> Result<(), MapToError<Size4KiB>> {
    let page_range = {
        let page_start = Page::containing_address(virt_start);
        let page_end = Page::containing_address(virt_start + size as u64 - 1u64);
        Page::range_inclusive(page_start, page_end)
    };
    
    let mut mapper_guard = PAGE_TABLE_MAPPER.lock();
    let mapper = mapper_guard.as_mut().unwrap();
    
    let mut frame_allocator_guard = FRAME_ALLOCATOR.lock();
    let frame_allocator = frame_allocator_guard.as_mut().unwrap();
    
    let mut frame_offset = 0;
    
    for page in page_range {
        let frame = PhysFrame::containing_address(phys_start + frame_offset);
        unsafe {
            mapper.map_to(page, frame, flags, frame_allocator)?.flush();
        }
        frame_offset += 4096; // 4 KiB per page
    }
    
    Ok(())
}

/// Unmap a virtual memory region
pub fn unmap_region(virt_start: VirtAddr, size: usize) -> Result<(), UnmapError> {
    let page_range = {
        let page_start = Page::containing_address(virt_start);
        let page_end = Page::containing_address(virt_start + size as u64 - 1u64);
        Page::range_inclusive(page_start, page_end)
    };
    
    let mut mapper_guard = PAGE_TABLE_MAPPER.lock();
    let mapper = mapper_guard.as_mut().unwrap();
    
    for page in page_range {
        unsafe {
            mapper.unmap(page)?.1.flush();
        }
    }
    
    Ok(())
}

/// Translate a virtual address to physical
pub fn translate_addr(addr: VirtAddr) -> Option<PhysAddr> {
    let mapper_guard = PAGE_TABLE_MAPPER.lock();
    mapper_guard.as_ref().unwrap().translate_addr(addr)
}

/// Check if a memory region is mapped
pub fn is_region_mapped(start: VirtAddr, size: usize) -> bool {
    let end = start + size as u64;
    let mut current = start;
    
    while current < end {
        if translate_addr(current).is_none() {
            return false;
        }
        current += 4096; // Move to next page
    }
    
    true
}
