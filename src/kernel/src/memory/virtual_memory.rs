/// Virtual memory management for SynOS kernel
/// Handles virtual address space and page table management with AI integration
use crate::memory::physical::{Frame, PhysicalAddress, FrameAllocator};
use crate::ai_bridge;
use core::arch::asm;
use alloc::vec::Vec;

/// Size of a page (same as frame size on x86_64)
pub const PAGE_SIZE: usize = 4096;

/// Types of page faults
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PageFaultType {
    NotPresent,
    WriteToReadOnly,
    UserAccessKernel,
    ExecuteNonExecutable,
    ProtectionViolation,
    AISwap,
}

/// Page fault error information
#[derive(Debug)]
pub struct PageFaultError {
    pub fault_type: PageFaultType,
    pub virtual_address: VirtualAddress,
    pub physical_address: Option<PhysicalAddress>,
    pub error_code: u64,
    pub instruction_pointer: u64,
}

/// Virtual address wrapper
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct VirtualAddress(pub usize);

/// Page structure
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Page {
    pub address: VirtualAddress,
}

/// Page table entry flags
#[derive(Debug, Clone, Copy)]
pub struct PageTableFlags {
    bits: u64,
}

impl PageTableFlags {
    pub const PRESENT: PageTableFlags = PageTableFlags { bits: 1 << 0 };
    pub const WRITABLE: PageTableFlags = PageTableFlags { bits: 1 << 1 };
    pub const USER_ACCESSIBLE: PageTableFlags = PageTableFlags { bits: 1 << 2 };
    pub const WRITE_THROUGH: PageTableFlags = PageTableFlags { bits: 1 << 3 };
    pub const NO_CACHE: PageTableFlags = PageTableFlags { bits: 1 << 4 };
    pub const ACCESSED: PageTableFlags = PageTableFlags { bits: 1 << 5 };
    pub const DIRTY: PageTableFlags = PageTableFlags { bits: 1 << 6 };
    pub const HUGE_PAGE: PageTableFlags = PageTableFlags { bits: 1 << 7 };
    pub const NO_EXECUTE: PageTableFlags = PageTableFlags { bits: 1 << 63 };

    pub fn empty() -> Self {
        PageTableFlags { bits: 0 }
    }

    pub fn contains(&self, other: PageTableFlags) -> bool {
        (self.bits & other.bits) == other.bits
    }
}

impl core::ops::BitOr for PageTableFlags {
    type Output = Self;

    fn bitor(self, rhs: Self) -> Self::Output {
        PageTableFlags {
            bits: self.bits | rhs.bits,
        }
    }
}

/// Page table entry
#[derive(Debug, Clone, Copy)]
pub struct PageTableEntry {
    entry: u64,
}

impl PageTableEntry {
    /// Create a new page table entry
    pub fn new() -> Self {
        PageTableEntry { entry: 0 }
    }

    /// Check if the entry is present
    pub fn is_present(&self) -> bool {
        self.flags().contains(PageTableFlags::PRESENT)
    }

    /// Get the flags of this entry
    pub fn flags(&self) -> PageTableFlags {
        PageTableFlags {
            bits: self.entry & 0xfff,
        }
    }

    /// Get the physical frame this entry points to
    pub fn frame(&self) -> Option<Frame> {
        if self.is_present() {
            Some(Frame {
                address: PhysicalAddress(self.entry as usize & 0x000fffff_fffff000),
            })
        } else {
            None
        }
    }

    /// Set the frame and flags for this entry
    pub fn set(&mut self, frame: Frame, flags: PageTableFlags) {
        self.entry = (frame.start_address().0 as u64) | flags.bits;
    }

    /// Clear this entry
    pub fn clear(&mut self) {
        self.entry = 0;
    }
}

/// Page table with 512 entries
#[repr(align(4096))]
pub struct PageTable {
    entries: [PageTableEntry; 512],
}

impl PageTable {
    /// Create a new empty page table
    pub fn new() -> Self {
        PageTable {
            entries: [PageTableEntry::new(); 512],
        }
    }

    /// Get a reference to the entry at the given index
    pub fn entry(&self, index: usize) -> &PageTableEntry {
        &self.entries[index]
    }

    /// Get a mutable reference to the entry at the given index
    pub fn entry_mut(&mut self, index: usize) -> &mut PageTableEntry {
        &mut self.entries[index]
    }

    /// Clear all entries in this page table
    pub fn clear(&mut self) {
        for entry in self.entries.iter_mut() {
            entry.clear();
        }
    }
}

impl VirtualAddress {
    /// Create a new virtual address
    pub fn new(addr: usize) -> Self {
        VirtualAddress(addr)
    }

    /// Get the page containing this address
    pub fn containing_page(&self) -> Page {
        Page {
            address: VirtualAddress(self.0 & !(PAGE_SIZE - 1)),
        }
    }

    /// Get the page table indices for this address (4-level paging)
    pub fn page_table_indices(&self) -> [usize; 4] {
        let addr = self.0;
        [
            (addr >> 39) & 0x1ff, // PML4 index
            (addr >> 30) & 0x1ff, // PDP index
            (addr >> 21) & 0x1ff, // PD index
            (addr >> 12) & 0x1ff, // PT index
        ]
    }

    /// Get the offset within the page
    pub fn page_offset(&self) -> usize {
        self.0 & 0xfff
    }
}

impl Page {
    /// Get the starting address of this page
    pub fn start_address(&self) -> VirtualAddress {
        self.address
    }

    /// Get the page number
    pub fn number(&self) -> usize {
        self.address.0 / PAGE_SIZE
    }

    /// Create a range of pages
    pub fn range(start: Page, end: Page) -> PageRange {
        PageRange { start, end }
    }
}

/// Range of pages
pub struct PageRange {
    start: Page,
    end: Page,
}

impl Iterator for PageRange {
    type Item = Page;

    fn next(&mut self) -> Option<Self::Item> {
        if self.start.number() < self.end.number() {
            let page = self.start;
            self.start.address.0 += PAGE_SIZE;
            Some(page)
        } else {
            None
        }
    }
}

/// Memory mapper for managing virtual to physical address translation
pub struct MemoryMapper<'a> {
    p4_table: &'a mut PageTable,
    frame_allocator: &'a mut dyn crate::memory::physical::FrameAllocator,
}

impl<'a> MemoryMapper<'a> {
    /// Create a new memory mapper
    /// SAFETY: The caller must ensure the page table is valid
    pub unsafe fn new(
        p4_table: &'a mut PageTable,
        frame_allocator: &'a mut dyn FrameAllocator,
    ) -> Self {
        MemoryMapper {
            p4_table,
            frame_allocator,
        }
    }

    /// Map a page to a frame with the given flags
    pub fn map_page(
        &mut self,
        page: Page,
        frame: Frame,
        flags: PageTableFlags,
    ) -> Result<(), &'static str> {
        let indices = page.start_address().page_table_indices();

        // Navigate through 4-level page table hierarchy
        let mut current_table = &mut *self.p4_table;

        // Traverse PML4 -> PDP -> PD -> PT
        for (level, &index) in indices.iter().take(3).enumerate() {
            let entry = current_table.entry_mut(index);

            if !entry.is_present() {
                // Allocate new page table for next level
                if let Some(new_frame) = self.frame_allocator.allocate_frame() {
                    entry.set(
                        new_frame,
                        PageTableFlags::PRESENT | PageTableFlags::WRITABLE,
                    );

                    // Zero out the new page table for security
                    unsafe {
                        let page_table_ptr = new_frame.start_address().as_u64() as *mut u8;
                        core::ptr::write_bytes(page_table_ptr, 0, 4096);
                    }
                } else {
                    return Err("Failed to allocate frame for page table");
                }
            }

            // For levels 0-2, we need to get the next page table
            if level < 2 {
                // Get the frame that contains the next level page table
                let frame = entry.frame().unwrap();

                // In a real kernel with proper virtual memory, we would map the physical
                // frame to a known virtual address. For now, we use direct mapping
                // assuming we can access physical memory directly.
                //
                // SAFETY: This assumes identity mapping or direct access to physical memory
                // In a production kernel, this would need proper virtual address mapping
                unsafe {
                    let next_table_addr = frame.start_address().as_u64();
                    if next_table_addr == 0 {
                        return Err("Invalid page table frame address");
                    }
                    current_table = &mut *(next_table_addr as *mut PageTable);
                }
            }
        }

        // Set the final page table entry
        let pt_index = indices[3];
        current_table
            .entry_mut(pt_index)
            .set(frame, flags | PageTableFlags::PRESENT);

        // Flush TLB for this page
        unsafe {
            asm!("invlpg [{}]", in(reg) page.start_address().0, options(nostack, preserves_flags));
        }

        Ok(())
    }

    /// Unmap a page
    pub fn unmap_page(&mut self, page: Page) -> Result<Frame, &'static str> {
        let indices = page.start_address().page_table_indices();
        let p4_index = indices[0];

        let entry = self.p4_table.entry_mut(p4_index);
        if let Some(frame) = entry.frame() {
            entry.clear();
            Ok(frame)
        } else {
            Err("Page not mapped")
        }
    }

    /// Translate a virtual address to a physical address
    pub fn translate(&self, addr: VirtualAddress) -> Option<PhysicalAddress> {
        let _page = addr.containing_page();
        let indices = addr.page_table_indices();
        let p4_index = indices[0];

        // Simplified translation - in reality would traverse full page table hierarchy
        if let Some(frame) = self.p4_table.entry(p4_index).frame() {
            Some(PhysicalAddress::new(
                frame.start_address().0 + addr.page_offset(),
            ))
        } else {
            None
        }
    }
}

/// Page fault handler for AI-integrated virtual memory
pub struct PageFaultHandler {
    ai_enabled: bool,
    swapped_pages: Vec<(VirtualAddress, PhysicalAddress)>,
}

impl PageFaultHandler {
    /// Create a new page fault handler
    pub fn new() -> Self {
        PageFaultHandler {
            ai_enabled: false,
            swapped_pages: Vec::new(),
        }
    }

    /// Handle a page fault with AI integration
    pub fn handle_page_fault(
        &mut self,
        fault_address: VirtualAddress,
        error_code: u64,
        instruction_pointer: u64,
        mapper: &mut MemoryMapper,
    ) -> Result<(), PageFaultError> {
        let fault_type = self.determine_fault_type(error_code, fault_address);

        // Log AI integration data if enabled
        if self.ai_enabled {
            // AI bridge would log memory events here
            // In future: ai_bridge::log_memory_event(...);
        }

        match fault_type {
            PageFaultType::NotPresent => self.handle_not_present(fault_address, mapper),
            PageFaultType::AISwap => self.handle_ai_swap(fault_address, mapper),
            PageFaultType::ProtectionViolation => {
                Err(PageFaultError {
                    fault_type,
                    virtual_address: fault_address,
                    physical_address: None,
                    error_code,
                    instruction_pointer,
                })
            }
            _ => {
                // Other fault types require termination
                Err(PageFaultError {
                    fault_type,
                    virtual_address: fault_address,
                    physical_address: mapper.translate(fault_address),
                    error_code,
                    instruction_pointer,
                })
            }
        }
    }

    /// Determine the type of page fault
    fn determine_fault_type(&self, error_code: u64, fault_address: VirtualAddress) -> PageFaultType {
        // Bit 0: Present bit (0 = page not present, 1 = protection violation)
        if (error_code & 1) == 0 {
            // Check if this is an AI-managed swapped page
            if self.is_ai_swapped(fault_address) {
                return PageFaultType::AISwap;
            }
            return PageFaultType::NotPresent;
        }

        // Bit 1: Write bit (0 = read, 1 = write)
        if (error_code & 2) != 0 {
            return PageFaultType::WriteToReadOnly;
        }

        // Bit 2: User bit (0 = kernel, 1 = user)
        if (error_code & 4) != 0 {
            return PageFaultType::UserAccessKernel;
        }

        // Bit 4: Instruction fetch (1 = instruction fetch)
        if (error_code & 16) != 0 {
            return PageFaultType::ExecuteNonExecutable;
        }

        PageFaultType::ProtectionViolation
    }

    /// Handle page not present faults
    fn handle_not_present(
        &mut self,
        fault_address: VirtualAddress,
        mapper: &mut MemoryMapper,
    ) -> Result<(), PageFaultError> {
        // Allocate a new frame for the page
        if let Some(frame) = mapper.frame_allocator.allocate_frame() {
            let page = fault_address.containing_page();
            let flags = PageTableFlags::PRESENT | PageTableFlags::WRITABLE;

            // Map the page
            if let Err(_) = mapper.map_page(page, frame, flags) {
                return Err(PageFaultError {
                    fault_type: PageFaultType::NotPresent,
                    virtual_address: fault_address,
                    physical_address: None,
                    error_code: 0,
                    instruction_pointer: 0,
                });
            }

            // Log AI integration data if enabled  
            if self.ai_enabled {
                // AI bridge would log successful allocation here
                // In future: ai_bridge::log_allocation_success(...);
            }

            Ok(())
        } else {
            // Out of memory - trigger AI-aware page swapping
            self.handle_out_of_memory(fault_address, mapper)
        }
    }

    /// Handle AI-managed page swapping
    fn handle_ai_swap(
        &mut self,
        fault_address: VirtualAddress,
        mapper: &mut MemoryMapper,
    ) -> Result<(), PageFaultError> {
        // Find the swapped page
        if let Some(pos) = self.swapped_pages.iter().position(|(addr, _)| *addr == fault_address) {
            let (_, physical_addr) = self.swapped_pages.remove(pos);
            
            // Restore the page mapping
            let page = fault_address.containing_page();
            let frame = Frame { address: physical_addr };
            let flags = PageTableFlags::PRESENT | PageTableFlags::WRITABLE;

            if let Err(_) = mapper.map_page(page, frame, flags) {
                return Err(PageFaultError {
                    fault_type: PageFaultType::AISwap,
                    virtual_address: fault_address,
                    physical_address: Some(physical_addr),
                    error_code: 0,
                    instruction_pointer: 0,
                });
            }

                        // Log AI integration data for successful page restoration
            if self.ai_enabled {
                // AI bridge would log page restoration here
                // In future: ai_bridge::log_page_restore(...);
            }

            Ok(())
        } else {
            // Page was not in swap - treat as not present
            self.handle_not_present(fault_address, mapper)
        }
    }

    /// Handle out of memory situations with AI-driven swapping
    fn handle_out_of_memory(
        &mut self,
        fault_address: VirtualAddress,
        mapper: &mut MemoryMapper,
    ) -> Result<(), PageFaultError> {
        // Use simple LRU algorithm for page selection if AI is enabled
        if self.ai_enabled && !self.swapped_pages.is_empty() {
            // In a real implementation, AI would help select the best victim page
            // For now, use simple FIFO
            if let Some((victim_addr, _)) = self.swapped_pages.get(0).cloned() {
                // Swap out the victim page
                if let Some(physical_addr) = mapper.translate(victim_addr) {
                    // Update swapped pages list
                    self.swapped_pages.remove(0);
                    self.swapped_pages.push((victim_addr, physical_addr));
                    
                    // Unmap the victim page
                    let victim_page = victim_addr.containing_page();
                    if let Ok(freed_frame) = mapper.unmap_page(victim_page) {
                        // Use the freed frame for the new page
                        let new_page = fault_address.containing_page();
                        let flags = PageTableFlags::PRESENT | PageTableFlags::WRITABLE;
                        
                        if let Err(_) = mapper.map_page(new_page, freed_frame, flags) {
                            return Err(PageFaultError {
                                fault_type: PageFaultType::NotPresent,
                                virtual_address: fault_address,
                                physical_address: None,
                                error_code: 0,
                                instruction_pointer: 0,
                            });
                        }

                        if let Some(bridge) = ai_bridge::get_bridge() {
                            // Convert page data to bytes for AI reporting
                            let event_data = [
                                (fault_address.0 & 0xFF) as u8,
                                ((fault_address.0 >> 8) & 0xFF) as u8, 
                                (victim_page.address.0 & 0xFF) as u8,
                                ((victim_page.address.0 >> 8) & 0xFF) as u8,
                            ];
                            let _ = bridge.report_security_event(
                                "ai_swap",
                                1, // Low severity for routine swapping
                                &event_data,
                            );
                        }

                        return Ok(());
                    }
                }
            }
        }

        // Fallback: traditional page replacement
        self.handle_traditional_swap(fault_address, mapper)
    }

    /// Traditional page replacement when consciousness is not available
    fn handle_traditional_swap(
        &mut self,
        _fault_address: VirtualAddress,
        _mapper: &mut MemoryMapper,
    ) -> Result<(), PageFaultError> {
        // Implement LRU or other traditional page replacement algorithm
        // For now, return out of memory error
        Err(PageFaultError {
            fault_type: PageFaultType::NotPresent,
            virtual_address: _fault_address,
            physical_address: None,
            error_code: 0,
            instruction_pointer: 0,
        })
    }

    /// Check if a page is AI-swapped
    fn is_ai_swapped(&self, fault_address: VirtualAddress) -> bool {
        self.swapped_pages.iter().any(|(addr, _)| *addr == fault_address)
    }

    /// Enable AI integration
    pub fn enable_ai(&mut self) {
        self.ai_enabled = true;
    }

    /// Get statistics about page faults
    pub fn get_stats(&self) -> PageFaultStats {
        PageFaultStats {
            swapped_pages_count: self.swapped_pages.len(),
            consciousness_enabled: self.ai_enabled,
        }
    }
}

/// Page fault statistics
#[derive(Debug)]
pub struct PageFaultStats {
    pub swapped_pages_count: usize,
    pub consciousness_enabled: bool,
}

/// Global page fault handler
static mut PAGE_FAULT_HANDLER: Option<PageFaultHandler> = None;

/// Initialize the page fault handler
pub fn init_page_fault_handler() {
    unsafe {
        PAGE_FAULT_HANDLER = Some(PageFaultHandler::new());
    }
}

/// Get the global page fault handler
pub fn get_page_fault_handler() -> Option<&'static mut PageFaultHandler> {
    unsafe { PAGE_FAULT_HANDLER.as_mut() }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_virtual_address_page() {
        let addr = VirtualAddress::new(0x1000);
        let page = addr.containing_page();
        assert_eq!(page.start_address().0, 0x1000);
    }

    #[test]
    fn test_page_table_indices() {
        let addr = VirtualAddress::new(0x1ff_1ff_1ff_1ff_000);
        let indices = addr.page_table_indices();
        assert_eq!(indices, [0x1ff, 0x1ff, 0x1ff, 0x1ff]);
    }

    #[test]
    fn test_page_fault_type_determination() {
        let handler = PageFaultHandler::new();
        
        // Test not present fault
        assert_eq!(handler.determine_fault_type(0, VirtualAddress::new(0x1000)), PageFaultType::NotPresent);
        
        // Test write to read-only fault
        assert_eq!(handler.determine_fault_type(3, VirtualAddress::new(0x1000)), PageFaultType::WriteToReadOnly);
    }
}
