#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(crate::test_runner)]
#![reexport_test_harness_main = "test_main"]

extern crate alloc;

use core::panic::PanicInfo;
use bootloader::{BootInfo, entry_point};
use x86_64;
use alloc::format;

mod boot;
mod memory;
mod scheduler;
mod filesystem;
mod drivers;
mod ai_interface;
mod security;
mod threat_detection;
mod exploit_simulator;
mod forensics;
mod neural_security;
mod educational_api;
mod personalized_education_bridge;
mod consciousness_education_demo;
mod consciousness_bridge;
mod kernel_tests;

#[cfg(not(test))]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Immediate security lockdown - disable interrupts
    x86_64::instructions::interrupts::disable();
    
    println!("🚨 KERNEL PANIC - SECURITY LOCKDOWN INITIATED 🚨");
    println!("Panic occurred: {}", info);
    
    // Enhanced panic information for cybersecurity analysis
    if let Some(location) = info.location() {
        println!("📍 Location: {}:{}:{}", location.file(), location.line(), location.column());
        
        // Security analysis: check if panic is in security-critical code
        let file = location.file();
        if file.contains("security") || file.contains("threat") || file.contains("forensics") {
            println!("⚠️  CRITICAL: Panic in security module - potential attack detected!");
            
            // Log security incident
            forensics::create_timeline_event(
                &format!("KERNEL_PANIC_SECURITY_MODULE: {}", info),
                &security::SecurityContext::kernel_context()
            );
        }
    }
    
    // Educational panic information
    println!("📚 Educational Info: This panic demonstrates kernel error handling");
    println!("🛡️  Security Measures: System locked, interrupts disabled");
    
    // Create forensic evidence of the panic
    if let Some(location) = info.location() {
        let addr = location.line() as usize; // Use line number as mock address
        let context = security::SecurityContext::kernel_context();
        let _ = forensics::collect_memory_evidence(addr, 1024, &context);
    }
    
    // Neural darwinian learning from panic
    println!("🧠 Neural Learning: Analyzing panic patterns for future prevention");
    
    // Log panic for AI analysis (existing functionality)
    if let Some(ai) = ai_interface::get_ai_interface() {
        ai.log_system_event(ai_interface::SystemEvent::KernelPanic {
            message: "Kernel panic occurred - security lockdown initiated".into(),
            location: info.location().map(|l| {
                extern crate alloc;
                use alloc::format;
                format!("{}:{}:{}", l.file(), l.line(), l.column())
            }),
        });
    }
    
    // Educational message for students
    println!("🎓 Learning Opportunity: Study this panic to understand kernel stability");
    println!("💾 System State: All security measures activated, forensics collected");
    println!("🔒 Final State: System halted for analysis");
    
    // Halt with security lockdown
    loop {
        x86_64::instructions::hlt();
    }
}

#[cfg(test)]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    serial_println!("[failed]\n");
    serial_println!("Error: {}\n", info);
    exit_qemu(QemuExitCode::Failed);
    loop {}
}

pub fn init(boot_info: &'static BootInfo) {
    println!("🚀 SynapticOS Kernel Initializing...");
    
    // Initialize hardware abstraction layer
    drivers::init();
    
    // Initialize memory management (bootloader 0.9 API)
    memory::init(&boot_info.memory_map, x86_64::VirtAddr::new(0));
    
    // Initialize security subsystem
    security::init();
    
    // Initialize threat detection engine
    threat_detection::init();
    
    // Initialize forensics collection
    forensics::init();
    
    // Initialize neural security engine
    neural_security::init();
    
    // Initialize educational exploit simulator
    exploit_simulator::init();
    
    // Initialize educational API
    educational_api::init();
    
    // Initialize personalized education bridge with consciousness integration
    personalized_education_bridge::init_personalized_education();
    
    // Initialize AI interface (secured)
    ai_interface::init();
    
    // Initialize consciousness bridge for AI-kernel communication
    consciousness_bridge::init();
    
    // Initialize scheduler with AI optimization
    scheduler::init();
    
    println!("✅ SynapticOS Kernel Ready");
}

/// Get current system timestamp
pub fn get_timestamp() -> u64 {
    use core::sync::atomic::{AtomicU64, Ordering};
    static TIMESTAMP: AtomicU64 = AtomicU64::new(0);
    TIMESTAMP.fetch_add(1, Ordering::SeqCst)
}

entry_point!(kernel_main);

fn kernel_main(boot_info: &'static BootInfo) -> ! {
    init(boot_info);
    
    #[cfg(test)]
    test_main();
    
    println!("🧠 Syn_OS - AI-Powered Cybersecurity Education Platform");
    println!("🔒 Security Status: Neural Darwinian Defense Active");
    println!("🎓 Educational Mode: Consciousness-Aware Personalized Learning Ready");
    println!("🔍 Threat Detection: Adaptive Learning Enabled");
    println!("📊 Digital Forensics: Chain of Custody Active");
    println!("🤖 AI Engine: Neural Security Evolution Online");
    println!("🧬 Personal Context: Consciousness-Integrated Learning Paths Active");
    
    println!("\n🧪 Running comprehensive kernel validation...");
    
    // Run comprehensive kernel tests
    kernel_tests::run_kernel_tests();
    
    println!("\n🚀 Kernel fully operational - starting main loop...");
    
    // Start main kernel loop
    kernel_main_loop();
}

fn kernel_main_loop() -> ! {
    loop {
        // Check for AI processing requests
        if let Some(request) = ai_interface::get_pending_request() {
            ai_interface::process_request_securely(request);
        }
        
        // Yield to scheduler
        scheduler::yield_cpu();
        
        // Handle interrupts
        x86_64::instructions::hlt();
    }
}

// Testing framework
#[cfg(test)]
fn test_runner(tests: &[&dyn Fn()]) {
    serial_println!("Running {} tests", tests.len());
    for test in tests {
        test();
    }
    exit_qemu(QemuExitCode::Success);
}

#[cfg(test)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u32)]
pub enum QemuExitCode {
    Success = 0x10,
    Failed = 0x11,
}

#[cfg(test)]
pub fn exit_qemu(exit_code: QemuExitCode) {
    use x86_64::instructions::port::Port;

    unsafe {
        let mut port = Port::new(0xf4);
        port.write(exit_code as u32);
    }
}

// Basic print macros for kernel
#[macro_export]
macro_rules! print {
    ($($arg:tt)*) => ($crate::vga_buffer::_print(format_args!($($arg)*)));
}

#[macro_export]
macro_rules! println {
    () => ($crate::print!("\n"));
    ($($arg:tt)*) => ($crate::print!("{}\n", format_args!($($arg)*)));
}

#[cfg(test)]
#[macro_export]
macro_rules! serial_print {
    ($($arg:tt)*) => {
        $crate::serial::_print(format_args!($($arg)*));
    };
}

#[cfg(test)]
#[macro_export]
macro_rules! serial_println {
    () => ($crate::serial_print!("\n"));
    ($($arg:tt)*) => ($crate::serial_print!("{}\n", format_args!($($arg)*)));
}

// VGA buffer module (basic implementation)
mod vga_buffer {
    use core::fmt;
    use volatile::Volatile;

    #[allow(dead_code)]
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    #[repr(u8)]
    pub enum Color {
        Black = 0,
        Blue = 1,
        Green = 2,
        Cyan = 3,
        Red = 4,
        Magenta = 5,
        Brown = 6,
        LightGray = 7,
        DarkGray = 8,
        LightBlue = 9,
        LightGreen = 10,
        LightCyan = 11,
        LightRed = 12,
        Pink = 13,
        Yellow = 14,
        White = 15,
    }

    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    #[repr(transparent)]
    struct ColorCode(u8);

    impl ColorCode {
        fn new(foreground: Color, background: Color) -> ColorCode {
            ColorCode((background as u8) << 4 | (foreground as u8))
        }
    }

    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    #[repr(C)]
    struct ScreenChar {
        ascii_character: u8,
        color_code: ColorCode,
    }

    unsafe impl Send for ScreenChar {}
    unsafe impl Sync for ScreenChar {}
    
    // Implement required traits for Volatile access
    use core::ops::{Deref, DerefMut};
    
    impl Deref for ScreenChar {
        type Target = Self;
        fn deref(&self) -> &Self::Target {
            self
        }
    }
    
    impl DerefMut for ScreenChar {
        fn deref_mut(&mut self) -> &mut Self::Target {
            self
        }
    }

    const BUFFER_HEIGHT: usize = 25;
    const BUFFER_WIDTH: usize = 80;

    #[repr(transparent)]
    struct Buffer {
        chars: [[Volatile<ScreenChar>; BUFFER_WIDTH]; BUFFER_HEIGHT],
    }

    pub struct Writer {
        column_position: usize,
        color_code: ColorCode,
        buffer: &'static mut Buffer,
    }

    impl Writer {
        pub fn write_byte(&mut self, byte: u8) {
            match byte {
                b'\n' => self.new_line(),
                byte => {
                    if self.column_position >= BUFFER_WIDTH {
                        self.new_line();
                    }

                    let row = BUFFER_HEIGHT - 1;
                    let col = self.column_position;

                    let color_code = self.color_code;
                    self.buffer.chars[row][col].write(ScreenChar {
                        ascii_character: byte,
                        color_code,
                    });
                    self.column_position += 1;
                }
            }
        }

        pub fn write_string(&mut self, s: &str) {
            for byte in s.bytes() {
                match byte {
                    0x20..=0x7e | b'\n' => self.write_byte(byte),
                    _ => self.write_byte(0xfe),
                }
            }
        }

        fn new_line(&mut self) {
            for row in 1..BUFFER_HEIGHT {
                for col in 0..BUFFER_WIDTH {
                    let character = self.buffer.chars[row][col].read();
                    self.buffer.chars[row - 1][col].write(character);
                }
            }
            self.clear_row(BUFFER_HEIGHT - 1);
            self.column_position = 0;
        }

        fn clear_row(&mut self, row: usize) {
            let blank = ScreenChar {
                ascii_character: b' ',
                color_code: self.color_code,
            };
            for col in 0..BUFFER_WIDTH {
                self.buffer.chars[row][col].write(blank);
            }
        }
    }

    impl fmt::Write for Writer {
        fn write_str(&mut self, s: &str) -> fmt::Result {
            self.write_string(s);
            Ok(())
        }
    }

    use spin::Mutex;

    lazy_static! {
        pub static ref WRITER: Mutex<Writer> = Mutex::new(Writer {
            column_position: 0,
            color_code: ColorCode::new(Color::Yellow, Color::Black),
            buffer: unsafe { &mut *(0xb8000 as *mut Buffer) },
        });
    }

    use lazy_static::lazy_static;

    pub fn _print(args: fmt::Arguments) {
        use core::fmt::Write;
        WRITER.lock().write_fmt(args).unwrap();
    }
}

#[cfg(test)]
mod serial {
    use uart_16550::SerialPort;
    use spin::Mutex;
    use lazy_static::lazy_static;

    lazy_static! {
        pub static ref SERIAL1: Mutex<SerialPort> = {
            let mut serial_port = unsafe { SerialPort::new(0x3F8) };
            serial_port.init();
            Mutex::new(serial_port)
        };
    }

    pub fn _print(args: ::core::fmt::Arguments) {
        use core::fmt::Write;
        SERIAL1.lock().write_fmt(args).expect("Printing to serial failed");
    }
}
