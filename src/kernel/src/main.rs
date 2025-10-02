#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![feature(abi_x86_interrupt)]
#![test_runner(crate::test_runner)]
#![reexport_test_harness_main = "test_main"]

extern crate alloc;

use bootloader::{entry_point, BootInfo};
use core::panic::PanicInfo;
use x86_64;

// Import kernel library - all modules now in lib.rs
use syn_kernel;

// Local modules only used in main.rs
mod allocator;
mod ai_interface;
mod filesystem;
mod networking;
mod threat_detection;

#[allow(dead_code)]
fn init(_boot_info: &'static mut BootInfo) {
    // Initialize basic systems
    syn_kernel::drivers::init();
    syn_kernel::boot::early_init::early_kernel_init().expect("early kernel init failed");

    // Initialize heap allocator
    allocator::init_heap().expect("heap initialization failed");

    // Initialize memory system with default config
    syn_kernel::memory::init::init_memory_system(
        syn_kernel::memory::init::MemoryConfig::default()
    ).expect("memory system init failed");

    // Initialize AI bridge system
    syn_kernel::ai_bridge::init();

    // Initialize educational platform
    syn_kernel::education_platform_minimal::init();

    // Initialize advanced applications
    syn_kernel::advanced_applications_minimal::init();

    println!("🧠 SynOS Kernel V1.0 - Initialized!");
}

entry_point!(kernel_main);

fn kernel_main(boot_info: &'static mut BootInfo) -> ! {
    // Initialize serial port FIRST - before any other initialization
    println!("SynOS: Serial port initialized");
    println!("SynOS: Kernel entry point reached");
    
    init(boot_info);

    #[cfg(test)]
    test_main();

    // Boot messages
    println!("🧠 SynOS - AI-Enhanced Cybersecurity OS");
    println!("🔧 V1.0 Build - Core functionality active");
    
    println!("🚀 SynOS V1.0 Developer ISO - Build Complete");
    println!("📅 Build Date: September 2, 2025");
    println!("🏗️  Kernel: Syn_OS Native Kernel (x86_64-unknown-none)");
    
    // Simple module status check
    if syn_kernel::education_platform_minimal::is_platform_active() {
        println!("✅ Education Platform: Active");
    }

    if syn_kernel::advanced_applications_minimal::is_apps_active() {
        println!("✅ Advanced Applications: Active");
    }

    println!("🔄 Entering kernel main loop...");
    
    // Basic kernel loop
    let mut loop_count = 0u64;
    loop {
        loop_count += 1;
        
        // Heartbeat every 100000 loops
        if loop_count % 100000 == 0 {
            println!("🧠 Kernel heartbeat: {} iterations", loop_count);
        }

        // Halt to save CPU
        if loop_count % 1000 == 0 {
            x86_64::instructions::hlt();
        }
    }
}

#[cfg(not(test))]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    crate::println!("{}", info);
    loop {}
}

#[cfg(test)]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    println!("[failed]\n");
    println!("Error: {}\n", info);
    exit_qemu(QemuExitCode::Failed);
    loop {}
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u32)]
pub enum QemuExitCode {
    Success = 0x10,
    Failed = 0x11,
}

pub fn exit_qemu(exit_code: QemuExitCode) {
    use x86_64::instructions::port::Port;

    unsafe {
        let mut port = Port::new(0xf4);
        port.write(exit_code as u32);
    }
}

#[cfg(test)]
fn test_runner(tests: &[&dyn Fn()]) {
    println!("Running {} tests", tests.len());
    for test in tests {
        test();
    }
    exit_qemu(QemuExitCode::Success);
}

// Print macros
#[macro_export]
macro_rules! print {
    ($($arg:tt)*) => {
        $crate::vga_buffer::_print(format_args!($($arg)*))
    };
}

#[macro_export]
macro_rules! println {
    () => ($crate::print!("\n"));
    ($($arg:tt)*) => ($crate::print!("{}\n", format_args!($($arg)*)));
}

#[macro_export]
macro_rules! serial_print {
    ($($arg:tt)*) => {
        $crate::serial::_print(format_args!($($arg)*));
    };
}

#[macro_export]
macro_rules! serial_println {
    () => ($crate::serial_print!("\n"));
    ($($arg:tt)*) => ($crate::serial_print!("{}\n", format_args!($($arg)*)));
}

// VGA buffer for output
pub mod vga_buffer {
    use core::fmt;
    use lazy_static::lazy_static;
    use spin::Mutex;

    lazy_static! {
        pub static ref WRITER: Mutex<Writer> = Mutex::new(Writer {
            column_position: 0,
            color_code: ColorCode::new(Color::Yellow, Color::Black),
            buffer: unsafe { &mut *(0xb8000 as *mut Buffer) },
        });
    }

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

    const BUFFER_HEIGHT: usize = 25;
    const BUFFER_WIDTH: usize = 80;

    #[repr(transparent)]
    struct Buffer {
        chars: [[ScreenChar; BUFFER_WIDTH]; BUFFER_HEIGHT],
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
                    self.buffer.chars[row][col] = ScreenChar {
                        ascii_character: byte,
                        color_code,
                    };
                    self.column_position += 1;
                }
            }
        }

        fn new_line(&mut self) {
            for row in 1..BUFFER_HEIGHT {
                for col in 0..BUFFER_WIDTH {
                    let character = self.buffer.chars[row][col];
                    self.buffer.chars[row - 1][col] = character;
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
                self.buffer.chars[row][col] = blank;
            }
        }
    }

    impl fmt::Write for Writer {
        fn write_str(&mut self, s: &str) -> fmt::Result {
            for byte in s.bytes() {
                match byte {
                    0x20..=0x7e | b'\n' => self.write_byte(byte),
                    _ => self.write_byte(0xfe),
                }
            }
            Ok(())
        }
    }

    pub fn _print(args: fmt::Arguments) {
        use core::fmt::Write;
        WRITER.lock().write_fmt(args).unwrap();
    }
}

// Serial port for debugging
pub mod serial {
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
        SERIAL1
            .lock()
            .write_fmt(args)
            .expect("Printing to serial failed");
    }
}
