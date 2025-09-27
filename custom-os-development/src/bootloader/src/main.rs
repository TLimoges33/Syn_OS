//! # SynOS UEFI Bootloader Binary Entry Point
//!
//! Main entry point for the SynOS UEFI bootloader with consciousness integration

#![no_std]
#![no_main]
#![allow(unused)]
#![allow(dead_code)]

extern crate alloc;
use alloc::{vec::Vec, string::String, format, vec};
use uefi::prelude::*;
use uefi::{Identify, Handle};
use uefi::table::boot::{BootServices, SearchType, OpenProtocolAttributes, OpenProtocolParams, MemoryType};
use uefi::proto::console::gop::GraphicsOutput;
use uefi::proto::media::fs::SimpleFileSystem;
use log::{info, warn, error};
use syn_bootloader::SynBootloader;

/// UEFI entry point
#[uefi::entry]
#[no_mangle]
#[allow(unsafe_code)]
pub fn main(
    _handle: uefi::Handle,
    mut system_table: SystemTable<uefi::table::Boot>,
) -> Status {
    // Initialize UEFI services
    uefi::helpers::init(&mut system_table).unwrap();
    
    info!("🚀 SynOS UEFI Bootloader Starting");
    info!("Consciousness-Enhanced Operating System");
    info!("======================================");
    
    // Create bootloader instance
    let mut bootloader = match SynBootloader::new() {
        Ok(bl) => {
            info!("✅ Bootloader instance created successfully");
            bl
        },
        Err(e) => {
            error!("❌ Failed to create bootloader: {}", e);
            return Status::ABORTED;
        }
    };
    
    // Initialize bootloader systems
    match bootloader.initialize(&system_table.boot_services()) {
        Ok(()) => {
            info!("✅ Bootloader systems initialized");
        },
        Err(e) => {
            error!("❌ Failed to initialize bootloader: {}", e);
            return Status::ABORTED;
        }
    }
    
    // Perform hardware detection and consciousness initialization
    match bootloader.detect_hardware(&system_table.boot_services()) {
        Ok(()) => {
            info!("✅ Hardware detection completed");
        },
        Err(e) => {
            warn!("⚠️ Hardware detection issues: {}", e);
            // Continue anyway
        }
    }
    
    // Initialize consciousness systems
    match bootloader.initialize_consciousness() {
        Ok(()) => {
            info!("✅ Consciousness systems online");
        },
        Err(e) => {
            warn!("⚠️ Consciousness initialization issues: {}", e);
            // Continue anyway
        }
    }
    
    // Set up graphics if available
    let mut graphics_initialized = false;
    if let Ok(gop_handles) = system_table.boot_services().find_handles::<GraphicsOutput>() {
        for handle in gop_handles {
            #[allow(unsafe_code)]
            if let Ok(mut gop) = unsafe { system_table.boot_services().open_protocol::<GraphicsOutput>(
                OpenProtocolParams {
                    handle,
                    agent: _handle,
                    controller: None,
                },
                OpenProtocolAttributes::GetProtocol,
            ) } {
                if let Ok(()) = bootloader.initialize_graphics(&mut gop) {
                    info!("✅ Graphics system initialized");
                    graphics_initialized = true;
                    break;
                }
            }
        }
    }
    
    if !graphics_initialized {
        warn!("⚠️ Graphics initialization failed, continuing in text mode");
    }
    
    // Initialize educational framework
    match bootloader.initialize_educational_framework() {
        Ok(()) => {
            info!("✅ Educational framework ready");
        },
        Err(e) => {
            warn!("⚠️ Educational framework issues: {}", e);
        }
    }
    
    // Detect and analyze storage devices
    match bootloader.detect_storage(&system_table.boot_services()) {
        Ok(()) => {
            info!("✅ Storage detection completed");
        },
        Err(e) => {
            error!("❌ Storage detection failed: {}", e);
            return Status::DEVICE_ERROR;
        }
    }
    
    // Load kernel and prepare for handoff
    info!("🔄 Preparing kernel handoff...");
    
    // Load consciousness-optimized kernel
    match bootloader.load_kernel(&system_table.boot_services()) {
        Ok(kernel_entry) => {
            info!("✅ Kernel loaded at address: {:?}", kernel_entry);
            
            // Show consciousness visualization if graphics available
            if graphics_initialized {
                let _ = bootloader.display_consciousness_transition();
            }
            
            // Exit boot services and transfer control
            info!("🎯 Exiting UEFI boot services...");
            
            // Get memory map before exiting boot services
            let memory_map = match system_table.boot_services().memory_map(MemoryType::LOADER_DATA) {
                Ok(map) => map,
                Err(e) => {
                    error!("❌ Failed to get memory map: {:?}", e);
                    return Status::ABORTED;
                }
            };
            
            // Exit boot services - The API returns a tuple directly
            let (_runtime_table, _memory_map) = unsafe { 
                system_table.exit_boot_services(MemoryType::LOADER_DATA)
            };
            
            info!("🚀 Transferring control to SynOS kernel...");
            info!("Welcome to the Future of Operating Systems!");
            
            // Transfer control to kernel
            bootloader.transfer_to_kernel(kernel_entry, core::iter::empty());
            
            // This should never be reached
            error!("❌ Kernel returned unexpectedly");
            Status::ABORTED
        },
        Err(e) => {
            error!("❌ Failed to load kernel: {}", e);
            Status::LOAD_ERROR
        }
    }
}

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    error!("PANIC in SynOS bootloader: {:?}", info);
    
    // Try to display panic information if graphics are available
    // In a real implementation, we'd try to show this on screen
    
    // Halt the system
    loop {
        #[allow(unsafe_code)]
        unsafe {
            core::arch::asm!("hlt");
        }
    }
}
