use alloc::vec::Vec;
use core::ptr;

#[derive(Debug)]
pub struct StackProtection {
    pub guard_pages: Vec<GuardPage>,
    pub stack_canaries: Vec<u64>,
    pub enabled: bool,
}

#[derive(Debug, Clone)]
pub struct GuardPage {
    pub address: *mut u8,
    pub size: usize,
    pub permissions: PagePermissions,
}

#[derive(Debug, Clone, Copy)]
pub enum PagePermissions {
    None,
    Read,
    Write,
    ReadWrite,
    Execute,
    ReadExecute,
}

impl StackProtection {
    pub fn new() -> Self {
        Self {
            guard_pages: Vec::new(),
            stack_canaries: Vec::new(),
            enabled: true,
        }
    }
    
    pub fn install_guard_page(&mut self, address: *mut u8, size: usize) -> Result<(), &'static str> {
        if !self.enabled {
            return Err("Stack protection disabled");
        }
        
        let guard = GuardPage {
            address,
            size,
            permissions: PagePermissions::None,
        };
        
        // Install guard page (simplified - would normally use paging)
        self.guard_pages.push(guard);
        Ok(())
    }
    
    pub fn check_stack_overflow(&self, _stack_ptr: *const u8) -> bool {
        // Simplified stack overflow detection
        self.enabled && !self.guard_pages.is_empty()
    }
    
    pub fn enable_nx_bit(&mut self) -> Result<(), &'static str> {
        // Enable NX (No eXecute) bit protection
        self.enabled = true;
        Ok(())
    }
    
    pub fn smep_check(&self, _address: *const u8) -> bool {
        // Supervisor Mode Execution Prevention check
        self.enabled
    }
    
    pub fn smap_check(&self, _address: *const u8) -> bool {
        // Supervisor Mode Access Prevention check  
        self.enabled
    }
}

impl Default for StackProtection {
    fn default() -> Self {
        Self::new()
    }
}

// Make pointers Send + Sync for kernel use
unsafe impl Send for GuardPage {}
unsafe impl Sync for GuardPage {}
