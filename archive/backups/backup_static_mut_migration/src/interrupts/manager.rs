use alloc::vec::Vec;
use core::fmt;
use spin::Mutex;
use lazy_static::lazy_static;

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
    
    pub fn unregister_handler(&mut self, vector: u8) -> Result<(), &'static str> {
        if vector as usize >= self.handlers.len() {
            return Err("Invalid interrupt vector");
        }
        
        self.handlers[vector as usize] = None;
        Ok(())
    }
    
    pub fn handle_interrupt(&self, vector: u8) -> Result<(), &'static str> {
        if !self.enabled {
            return Err("Interrupt manager disabled");
        }
        
        if let Some(handler) = self.handlers.get(vector as usize).and_then(|h| *h) {
            handler();
            Ok(())
        } else {
            Err("No handler registered for interrupt")
        }
    }
    
    pub fn enable(&mut self) {
        self.enabled = true;
    }
    
    pub fn disable(&mut self) {
        self.enabled = false;
    }
    
    pub fn is_enabled(&self) -> bool {
        self.enabled
    }
}

impl Default for InterruptManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Get global interrupt manager instance
pub fn interrupt_manager() -> &'static Mutex<InterruptManager> {
    &INTERRUPT_MANAGER
}
