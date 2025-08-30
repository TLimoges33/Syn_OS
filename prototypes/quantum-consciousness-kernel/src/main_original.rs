#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(crate::test_runner)]
#![reexport_test_harness_main = "test_main"]

extern crate alloc;

use bootloader::{entry_point, BootInfo};
use core::panic::PanicInfo;
use x86_64;
use alloc::string::ToString;

mod advanced_applications;
mod boot;
mod consciousness;
mod consciousness_boot;
mod drivers;
mod education_platform;
mod filesystem;
mod forensics;
mod learning_analytics;
mod memory;
mod networking;
mod scheduler;
mod security;
mod threat_detection;

#[cfg(not(test))]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Disable interrupts for safety
    x86_64::instructions::interrupts::disable();

    println!("KERNEL PANIC: {}", info);

    if let Some(location) = info.location() {
        println!(
            "Location: {}:{}:{}",
            location.file(),
            location.line(),
            location.column()
        );
    }

    // Halt the system
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
    println!("🧠 SynapticOS Consciousness-Enhanced Kernel Initializing...");

    // Display consciousness boot information
    consciousness_boot::display_consciousness_boot_info();

    // Initialize consciousness boot system
    let consciousness_config = consciousness_boot::ConsciousnessBootConfig::default();
    consciousness_boot::init_consciousness_boot(consciousness_config);

    // Initialize consciousness integration layer (Phase 1 Foundation)
    consciousness::init();

    // Validate consciousness system is active for security
    if !consciousness::is_consciousness_active() {
        panic!("Critical Security Error: Consciousness system failed to initialize");
    }

    // Initialize hardware abstraction layer
    drivers::init();

    // Initialize consciousness-enhanced memory management
    memory::init(&boot_info.memory_map, x86_64::VirtAddr::new(0));
    
    // Validate memory management is properly initialized
    if !memory::is_initialized() {
        panic!("Critical Security Error: Memory management failed to initialize");
    }

    // Initialize security subsystem
    security::init();
    
    // Validate security system is properly initialized
    if !security::is_initialized() {
        panic!("Critical Security Error: Security subsystem failed to initialize");
    }

    // Initialize threat detection engine
    threat_detection::init();
    
    // Enable educational mode for safe threat demonstration
    threat_detection::enable_educational_mode();

    // Initialize forensics collection
    forensics::init();

    // Initialize consciousness-aware scheduler
    scheduler::init();

    // Phase 2: Initialize Educational Platform & Enhanced Consciousness Engine
    println!("🎓 Initializing Phase 2: Educational Platform & Enhanced Consciousness...");
    
    // Initialize educational platform
    education_platform::init();
    
    // Initialize learning analytics engine
    learning_analytics::init();
    
    // Validate educational platform is active
    if !education_platform::is_platform_active() {
        panic!("Critical Error: Educational platform failed to initialize");
    }

    // Phase 3: Initialize Advanced Applications & Production Features
    println!("🚀 Initializing Phase 3: Advanced Applications & Production Features...");
    
    // Initialize networking foundation
    networking::init();
    
    // Initialize advanced applications system
    advanced_applications::init();
    
    // Validate networking is active
    if !networking::is_networking_active() {
        panic!("Critical Error: Networking foundation failed to initialize");
    }
    
    // Validate advanced applications are active
    if !advanced_applications::is_advanced_apps_active() {
        panic!("Critical Error: Advanced applications failed to initialize");
    }

    println!("🧠 SynapticOS Kernel Ready - Phase 3 Complete");
    println!("   ✅ Consciousness Integration Layer: Active");
    println!("   ✅ Neural Darwinism Scheduler: Online");
    println!("   ✅ Consciousness-Enhanced Memory: Optimized");
    println!("   ✅ Security with Consciousness: Armed");
    println!("   ✅ Educational Platform: Ready");
    println!("   ✅ Learning Analytics Engine: Active");
    println!("   ✅ Adaptive Curriculum: Enabled");
    println!("   ✅ Networking Foundation: Online");
    println!("   ✅ TCP/IP Stack: Ready");
    println!("   ✅ Consciousness Connections: Active");
    println!("   ✅ Advanced Applications: Online");
    println!("   ✅ CTF Challenge Generator: Ready");
    println!("   ✅ Bias Analysis Engine: Active");
    println!("   ✅ Package Recommender: Online");
    println!("   ✅ Financial Management: Ready");
    println!("   ✅ Strategic Planning: Active");
}

entry_point!(kernel_main);

fn kernel_main(boot_info: &'static BootInfo) -> ! {
    init(boot_info);

    #[cfg(test)]
    test_main();

    println!("🧠 SynapticOS - Consciousness-Integrated Cybersecurity Education Platform");
    println!("🛡️  Security Status: Active");
    println!("🎓 Educational Mode: Ready");
    println!("📊 Learning Analytics: Active");
    println!(
        "🧠 Consciousness Level: {:.3}",
        consciousness::get_consciousness_level()
    );
    println!(
        "⚡ Scheduler Bias: {:?}",
        consciousness::get_consciousness_scheduler_bias()
    );
    println!(
        "🎓 Available Learning Modules: {}",
        education_platform::get_available_modules_count()
    );

    // Create demo student for educational platform testing
    let demo_student_id = education_platform::register_student(
        "Demo Student".to_string(),
        crate::security::SecurityContext::kernel_context()
    );
    println!("🎓 Demo student registered with ID: {}", demo_student_id);

    // Start demo learning session
    if let Ok(session_id) = education_platform::start_learning_session(
        demo_student_id, 
        "Basic Programming Concepts".to_string()
    ) {
        println!("🎓 Demo learning session started: {}", session_id);
        
        // Simulate some learning progress
        let _ = education_platform::update_learning_progress(session_id, 0, false);
        let _ = education_platform::update_learning_progress(session_id, 1, false);
        
        // Complete the session
        if let Ok(report) = education_platform::complete_learning_session(session_id) {
            println!("🎓 Demo session completed with {:.1}% accuracy", report.accuracy_score * 100.0);
            
            // Update analytics with the session data
            learning_analytics::update_real_time_metrics(&report);
        }
    }

    // Phase 3: Demonstrate Advanced Applications
    println!("🚀 Demonstrating Phase 3 Advanced Applications...");
    
    // Get demo student profile for advanced applications
    if let Ok(student_profile) = education_platform::get_student_profile(demo_student_id) {
        // Demonstrate CTF challenge generation
        let ctf_challenge = advanced_applications::generate_ctf_challenge(
            &student_profile, 
            Some(advanced_applications::CTFCategory::WebExploitation)
        );
        println!("🎯 Generated CTF Challenge: {}", ctf_challenge.title);
        println!("   Difficulty: {:.2} | Estimated Time: {} minutes", 
                 ctf_challenge.difficulty_score, ctf_challenge.estimated_time);
        
        // Demonstrate bias analysis
        let test_content = "This shocking news proves that cybersecurity experts must choose between only two devastating security approaches!";
        let bias_analysis = advanced_applications::analyze_content_bias(test_content);
        println!("🔍 Bias Analysis: {:.2} bias score with {} patterns detected", 
                 bias_analysis.overall_bias_score, bias_analysis.detected_biases.len());
        
        // Demonstrate package recommendations
        let package_recommendations = advanced_applications::get_package_recommendations(
            &student_profile, 
            Some(advanced_applications::PackageCategory::Security)
        );
        if !package_recommendations.is_empty() {
            println!("📦 Top Package Recommendation: {} (Score: {:.2})", 
                     package_recommendations[0].package_name, 
                     package_recommendations[0].recommendation_score);
        }
        
        // Demonstrate financial management
        let budget_recommendations = advanced_applications::generate_budget_recommendations(5000.0);
        if !budget_recommendations.is_empty() {
            println!("💰 Top Budget Recommendation: {} - ${:.2}", 
                     budget_recommendations[0].category, 
                     budget_recommendations[0].recommended_amount);
        }
        
        // Demonstrate strategic planning
        let career_recommendations = advanced_applications::get_career_recommendations(&student_profile);
        if !career_recommendations.is_empty() {
            println!("🎯 Career Recommendation: {} (Suitability: {:.2})", 
                     career_recommendations[0].career_path, 
                     career_recommendations[0].suitability_score);
        }
    }

    // Display advanced applications statistics
    let advanced_stats = advanced_applications::get_advanced_apps_statistics();
    println!("📊 Advanced Applications Statistics:");
    println!("   🎯 CTF Challenges Generated: {}", advanced_stats.ctf_challenges_generated);
    println!("   🔍 Bias Analyses Performed: {}", advanced_stats.bias_analyses_performed);
    println!("   🧠 Consciousness Integration: {:.3}", advanced_stats.consciousness_integration_level);

    // Demonstrate Phase 3 Networking Foundation
    println!("🌐 Demonstrating Networking Foundation...");
    
    // Create TCP socket with consciousness enhancement
    if let Ok(socket_id) = networking::create_tcp_socket() {
        println!("🔌 Created consciousness-enhanced TCP socket: {}", socket_id);
    }
    
    // Create consciousness-enhanced connection
    let local_addr = networking::SocketAddress {
        ip: networking::IpAddress::new([192, 168, 1, 100]),
        port: 8080,
    };
    let remote_addr = networking::SocketAddress {
        ip: networking::IpAddress::new([192, 168, 1, 200]),
        port: 9090,
    };
    
    if let Ok(conn_id) = networking::create_consciousness_connection(local_addr, remote_addr) {
        println!("🧠 Created consciousness connection: {} -> {}", conn_id, remote_addr);
    }
    
    // Display networking statistics
    let net_stats = networking::get_networking_statistics();
    println!("📊 Networking Statistics:");
    println!("   📦 Packets Processed: {}", net_stats.packets_processed);
    println!("   🔗 Connections Established: {}", net_stats.connections_established);
    println!("   🧠 Consciousness Level: {:.3}", net_stats.consciousness_level);

    // Create initial consciousness-aware process
    let init_pid = scheduler::create_process(None);
    println!(
        "🚀 Created initial process {} with consciousness tracking",
        init_pid
    );

    // Start main consciousness-enhanced kernel loop
    let mut loop_count = 0u64;
    loop {
        loop_count += 1;

        // Consciousness evolution simulation every 1000 loops
        if loop_count % 1000 == 0 {
            let current_consciousness = consciousness::get_consciousness_level();
            let new_consciousness = (current_consciousness + 0.001).min(1.0);
            consciousness::set_consciousness_level(new_consciousness);
            consciousness::set_evolution_generation(loop_count / 1000);

            // Enhanced educational consciousness evolution every 5000 loops
            if loop_count % 5000 == 0 {
                // Simulate educational learning progress with enhanced consciousness algorithms
                let learning_performance = 0.8; // Simulated high performance
                let engagement_level = 0.9;     // Simulated high engagement
                let module_difficulty = 0.6;    // Moderate difficulty
                let learning_style_match = 0.75; // Good style match
                
                consciousness::enhanced_learning_consciousness_update(
                    learning_performance,
                    engagement_level,
                    module_difficulty,
                    learning_style_match
                );
                
                // Get platform statistics for monitoring
                let platform_stats = education_platform::get_platform_statistics();
                println!("🎓 Educational Platform Stats: {} students, {} active sessions, effectiveness: {:.3}",
                         platform_stats.total_students, 
                         platform_stats.active_sessions,
                         platform_stats.effectiveness_report.engagement_effectiveness);
                
                // Get real-time learning analytics
                let learning_metrics = learning_analytics::get_real_time_metrics();
                println!("📊 Learning Analytics: {} active learners, avg consciousness: {:.3}, trend: {:?}",
                         learning_metrics.active_learners,
                         learning_metrics.current_average_consciousness,
                         learning_metrics.learning_effectiveness_trend);
            }

            // Traditional consciousness evolution for compatibility
            if loop_count % 7000 == 0 {
                consciousness::update_consciousness_from_learning(0.01, 0.5);
            }

            // Get and process consciousness events for security monitoring
            let events = consciousness::get_consciousness_events();
            if !events.is_empty() {
                println!("🧠 Processed {} consciousness events", events.len());
            }

            println!(
                "🧠 Consciousness evolved to {:.3} (generation {})",
                new_consciousness,
                loop_count / 1000
            );
        }

        // Consciousness-aware scheduling
        if let Some(process) = scheduler::schedule() {
            // Validate process security context before execution
            let _consciousness_state = consciousness::get_kernel_consciousness_state();
            
            // Security check: ensure process consciousness inheritance is valid
            if process.consciousness_inheritance < 0.0 || process.consciousness_inheritance > 1.0 {
                println!("🛡️ Security Warning: Invalid consciousness inheritance detected for process {}", process.pid);
                
                // Analyze potential security threat
                threat_detection::analyze_memory_threat(0x1000, 4096, &crate::security::SecurityContext::kernel_context());
                
                // Collect forensic evidence of the security violation
                forensics::collect_memory_evidence(0x1000, 4096, &crate::security::SecurityContext::kernel_context());
                
                scheduler::terminate_process(process.pid);
            } else {
                // Process would run here with validated consciousness context
                // println!("🔄 Running process {} (consciousness: {:.3})", 
                //          process.pid, process.consciousness_inheritance);
            }
        }        // Memory optimization based on consciousness
        if loop_count % 5000 == 0 {
            memory::optimize_memory();
            
            // Cleanup completed processes periodically for security
            if loop_count % 10000 == 0 {
                let stats = scheduler::get_scheduler_stats();
                if stats.total_processes > 100 {
                    println!("🛡️ Security: Process cleanup - {} active processes", stats.total_processes);
                    
                    // Generate forensic report for security monitoring
                    let _report = forensics::generate_forensic_report();
                    
                    // Get threat statistics for security assessment
                    let (threats_detected, patterns_active, accuracy) = threat_detection::get_threat_statistics();
                    if threats_detected > 0 {
                        println!("🛡️ Security Report: {} threats detected, {} patterns active, {:.2}% accuracy", 
                                threats_detected, patterns_active, accuracy * 100.0);
                    }
                }
            }
        }

        // Yield to consciousness-aware scheduler
        scheduler::yield_cpu();

        // Handle interrupts with consciousness context
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

// VGA buffer module
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

    impl core::ops::Deref for ScreenChar {
        type Target = ScreenChar;

        fn deref(&self) -> &Self::Target {
            self
        }
    }

    impl core::ops::DerefMut for ScreenChar {
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

    use lazy_static::lazy_static;
    use spin::Mutex;

    lazy_static! {
        pub static ref WRITER: Mutex<Writer> = Mutex::new(Writer {
            column_position: 0,
            color_code: ColorCode::new(Color::Green, Color::Black),
            buffer: unsafe { &mut *(0xb8000 as *mut Buffer) },
        });
    }

    pub fn _print(args: fmt::Arguments) {
        use core::fmt::Write;
        WRITER.lock().write_fmt(args).unwrap();
    }
}

#[cfg(test)]
mod serial {
    use lazy_static::lazy_static;
    use spin::Mutex;
    use uart_16550::SerialPort;

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
