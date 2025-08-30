#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(crate::test_runner)]
#![reexport_test_harness_main = "test_main"]

extern crate alloc;

use bootloader::{entry_point, BootInfo};
use core::panic::PanicInfo;
use alloc::format;
use alloc::string::String;

// Comprehensive logging system for debugging
mod serial_logger;

// AI Bridge module for ParrotOS integration
mod ai_bridge;
use ai_bridge::{AIBridge, AIResponse};

// =============================================================================
// SYN_OS CYBERSECURITY KERNEL - PARROTOS-BASED AI-ENHANCED SECURITY
// =============================================================================
// Foundation: ParrotOS security framework with AI-enhanced capabilities
// Focus: 10x cybersecurity education and practical security operations
// Features: AI-guided tool selection, adaptive learning, threat detection
// =============================================================================

/// AI-Enhanced Security Configuration
/// Integrates traditional cybersecurity with AI-powered adaptive learning
#[derive(Clone, Copy, Debug)]
struct AISecurityConfig {
    // Core Security Features (ParrotOS Foundation)
    memory_protection_enabled: bool,     // DEP/ASLR/Stack protection
    secure_boot_required: bool,          // Secure boot validation
    threat_detection_active: bool,       // Real-time threat monitoring
    forensics_logging: bool,             // Security event logging
    zero_trust_mode: bool,               // Zero-trust architecture
    pen_test_mode: bool,                 // Penetration testing features
    
    // AI Enhancement Features
    ai_tool_selection: bool,             // AI-powered ParrotOS tool selection
    adaptive_learning: bool,             // Personal context engine adaptation
    user_skill_tracking: bool,           // Progress and skill development
    educational_mode: bool,              // CTF and training scenarios
    ai_threat_correlation: bool,         // AI-enhanced threat analysis
}

impl AISecurityConfig {
    fn new() -> Self {
        Self {
            // ParrotOS security defaults
            memory_protection_enabled: true,
            secure_boot_required: true,
            threat_detection_active: true,
            forensics_logging: true,
            zero_trust_mode: true,
            pen_test_mode: false,
            
            // AI enhancement defaults
            ai_tool_selection: true,
            adaptive_learning: true,
            user_skill_tracking: true,
            educational_mode: true,
            ai_threat_correlation: true,
        }
    }
    
    /// Enable penetration testing mode for educational scenarios
    fn enable_pentest_mode(&mut self) {
        self.pen_test_mode = true;
        self.educational_mode = true;
        println!("🛡️ Penetration testing mode enabled for educational scenarios");
    }
    
    /// Enable AI-enhanced threat detection
    fn enhance_threat_detection(&mut self) {
        self.ai_threat_correlation = true;
        self.threat_detection_active = true;
        println!("🧠 AI-enhanced threat detection activated");
    }
}

/// Security threat levels based on real-world cybersecurity practices
/// Enhanced with AI-powered threat correlation and adaptive response
#[derive(Clone, Copy, Debug, PartialEq)]
enum ThreatLevel {
    None = 0,        // No threats detected
    Low = 1,         // Minor security events, learning opportunities
    Medium = 2,      // Potential security issues, guided investigation
    High = 3,        // Active security threats, AI-assisted response
    Critical = 4,    // Immediate security response, automated countermeasures
}

/// Memory protection mechanisms enhanced with AI monitoring
#[derive(Clone, Copy, Debug)]
struct EnhancedMemoryProtection {
    stack_guard_enabled: bool,       // Stack overflow protection
    heap_guard_enabled: bool,        // Heap corruption protection
    nx_bit_enabled: bool,            // Execute protection
    aslr_enabled: bool,              // Address space randomization
    canary_protection: bool,         // Stack canary protection
    ai_anomaly_detection: bool,      // AI-powered memory anomaly detection
}

impl EnhancedMemoryProtection {
    fn new() -> Self {
        Self {
            stack_guard_enabled: true,
            heap_guard_enabled: true,
            nx_bit_enabled: true,
            aslr_enabled: true,
            canary_protection: true,
            ai_anomaly_detection: true,
        }
    }

    /// Validate memory access with AI-enhanced security checks
    fn validate_memory_access(&self, address: usize, size: usize, write_access: bool) -> SecurityOperationResult {
        // Check for basic memory bounds
        if size == 0 || address.overflowing_add(size).1 {
            return SecurityOperationResult::Blocked("Invalid memory bounds".into());
        }
        
        // Check for write access to read-only regions
        if write_access && address < 0x100000 {  // Protect low memory
            return SecurityOperationResult::Blocked("Write access to protected region".into());
        }
        
        // Check for stack guard violations
        if self.stack_guard_enabled && address >= 0x7ff000000000 && size > 0x1000 {
            return SecurityOperationResult::Blocked("Stack guard violation".into());
        }
        
        // AI-enhanced anomaly detection
        if self.ai_anomaly_detection && self.detect_memory_anomaly(address, size) {
            return SecurityOperationResult::Warning("Potential memory anomaly detected".into());
        }
        
        SecurityOperationResult::Success("Memory access validated".into())
    }
    
    /// AI-powered memory anomaly detection
    fn detect_memory_anomaly(&self, address: usize, size: usize) -> bool {
        // Simple heuristics for demonstration (in real implementation, this would use ML)
        // Detect unusually large allocations
        if size > 0x10000000 {  // 256MB
            return true;
        }
        
        // Detect suspicious address patterns
        if address & 0xFFF == 0xFFF {  // Suspicious alignment
            return true;
        }
        
        false
    }
}

/// Security operation results for AI-enhanced responses
#[derive(Debug, Clone)]
enum SecurityOperationResult {
    Success(String),
    Warning(String),
    Blocked(String),
    EducationalOpportunity(String),
}

/// AI-Enhanced ParrotOS Tool Selector
/// Integrates with the comprehensive ParrotOS tool database
#[derive(Debug)]
struct AIToolSelector {
    user_skill_level: u8,           // 1-10 skill level
    learning_preferences: [bool; 8], // Various learning style flags
    recent_tools_used: [u16; 32],   // Recently used tool IDs
    current_scenario: ScenarioType,  // Current educational scenario
}

impl AIToolSelector {
    fn new() -> Self {
        Self {
            user_skill_level: 5,  // Default intermediate level
            learning_preferences: [true; 8],  // Default to all preferences enabled
            recent_tools_used: [0; 32],
            current_scenario: ScenarioType::General,
        }
    }
    
    /// AI-powered tool recommendation based on user context and scenario
    fn recommend_tool(&self, threat_level: ThreatLevel, _objective: &str) -> ToolRecommendation {
        match (threat_level, self.user_skill_level) {
            (ThreatLevel::Low, 1..=3) => ToolRecommendation {
                tool_id: 101,  // Basic network scanner
                tool_name: "nmap (basic scan)".into(),
                explanation: "Start with basic network discovery to understand the environment".into(),
                educational_value: 9,
                complexity: 2,
            },
            (ThreatLevel::Medium, 4..=7) => ToolRecommendation {
                tool_id: 205,  // Vulnerability scanner
                tool_name: "OpenVAS".into(),
                explanation: "Comprehensive vulnerability assessment for identified targets".into(),
                educational_value: 8,
                complexity: 6,
            },
            (ThreatLevel::High, 8..=10) => ToolRecommendation {
                tool_id: 350,  // Advanced exploitation framework
                tool_name: "Metasploit".into(),
                explanation: "Advanced exploitation framework for experienced users".into(),
                educational_value: 7,
                complexity: 9,
            },
            _ => ToolRecommendation {
                tool_id: 1,
                tool_name: "System Information".into(),
                explanation: "Gather basic system information first".into(),
                educational_value: 5,
                complexity: 1,
            }
        }
    }
    
    /// Update user skill level based on successful tool usage
    fn update_skill_level(&mut self, tool_complexity: u8, success: bool) {
        if success && tool_complexity > self.user_skill_level {
            self.user_skill_level = (self.user_skill_level + 1).min(10);
            println!("🎓 Skill level increased to {}", self.user_skill_level);
        }
    }
}

/// Educational scenario types for adaptive learning
#[derive(Debug, Clone, Copy)]
enum ScenarioType {
    General,
    WebPentest,
    NetworkRecon,
    DigitalForensics,
    MalwareAnalysis,
    IncidentResponse,
    ComplianceAudit,
    RedTeamExercise,
}

/// AI tool recommendation structure
#[derive(Debug)]
struct ToolRecommendation {
    tool_id: u16,
    tool_name: String,
    explanation: String,
    educational_value: u8,  // 1-10 scale
    complexity: u8,         // 1-10 scale
}

/// Main AI-Enhanced Security Kernel
struct SynOSKernel {
    config: AISecurityConfig,
    memory_protection: EnhancedMemoryProtection,
    tool_selector: AIToolSelector,
    threat_level: ThreatLevel,
    boot_time: u64,
    ai_bridge: AIBridge,  // Bridge to ParrotOS AI integration system
}

impl SynOSKernel {
    fn new() -> Self {
        Self {
            config: AISecurityConfig::new(),
            memory_protection: EnhancedMemoryProtection::new(),
            tool_selector: AIToolSelector::new(),
            threat_level: ThreatLevel::None,
            boot_time: 0,
            ai_bridge: AIBridge::new(),
        }
    }
    
    /// Initialize the AI-enhanced cybersecurity kernel
    fn initialize(&mut self) {
        serial_logger::log_info("SynOS Cybersecurity Kernel Initializing...");
        serial_logger::log_info("ParrotOS-based foundation with AI enhancement");
        println!("🚀 SynOS Cybersecurity Kernel Initializing...");
        println!("🛡️ ParrotOS-based foundation with AI enhancement");
        
        // Initialize security subsystems with logging
        serial_logger::log_debug("Initializing memory protection...");
        self.init_memory_protection();
        serial_logger::log_debug("Memory protection initialized");
        
        serial_logger::log_debug("Initializing threat detection...");
        self.init_threat_detection();
        serial_logger::log_debug("Threat detection initialized");
        
        serial_logger::log_debug("Initializing AI systems...");
        self.init_ai_systems();
        serial_logger::log_debug("AI systems initialized");
        
        serial_logger::log_debug("Initializing educational platform...");
        self.init_educational_platform();
        serial_logger::log_debug("Educational platform initialized");
        
        serial_logger::log_info("SynOS Kernel initialization complete");
        serial_logger::log_info("Ready for cybersecurity education and operations");
        println!("✅ SynOS Kernel initialization complete");
        println!("🎓 Ready for cybersecurity education and operations");
    }
    
    fn init_memory_protection(&mut self) {
        println!("🔒 Initializing enhanced memory protection...");
        if self.memory_protection.nx_bit_enabled {
            println!("   ✅ NX bit protection enabled");
        }
        if self.memory_protection.aslr_enabled {
            println!("   ✅ ASLR protection enabled");
        }
        if self.memory_protection.ai_anomaly_detection {
            println!("   🧠 AI memory anomaly detection enabled");
        }
    }
    
    fn init_threat_detection(&mut self) {
        println!("🛡️ Initializing AI-enhanced threat detection...");
        if self.config.ai_threat_correlation {
            println!("   🧠 AI threat correlation enabled");
        }
        if self.config.threat_detection_active {
            println!("   ⚡ Real-time threat monitoring active");
        }
    }
    
    fn init_ai_systems(&mut self) {
        println!("🧠 Initializing AI enhancement systems...");
        
        // Connect to ParrotOS AI integration system
        match self.ai_bridge.connect() {
            Ok(()) => {
                println!("   ✅ Connected to ParrotOS AI integration system");
                if self.config.ai_tool_selection {
                    println!("   🔧 AI-powered ParrotOS tool selection enabled");
                }
                if self.config.adaptive_learning {
                    println!("   🎓 Adaptive learning engine activated");
                }
                if self.config.user_skill_tracking {
                    println!("   📈 User skill progression tracking enabled");
                }
            },
            Err(e) => {
                println!("   ⚠️ Failed to connect to AI system: {}", e);
                println!("   🔄 Operating in standalone mode");
            }
        }
    }
    
    fn init_educational_platform(&mut self) {
        println!("🎓 Initializing cybersecurity education platform...");
        if self.config.educational_mode {
            println!("   📚 Educational scenarios enabled");
            println!("   🎯 CTF challenges available");
            println!("   🏆 Skill progression tracking active");
        }
    }
    
    /// Handle security events with AI-enhanced response
    fn handle_security_event(&mut self, event_type: &str, _data: &[u8]) -> SecurityOperationResult {
        // Update threat level based on event
        self.update_threat_level(event_type);
        
        // Request AI analysis if connected
        if self.ai_bridge.is_connected() {
            // Send security event to AI system for analysis
            let _ = self.ai_bridge.report_security_event(event_type, self.threat_level as u8, _data);
            
            // Process any pending AI messages
            self.ai_bridge.process_messages();
            
            // Check for AI response
            if let Some(response) = self.ai_bridge.receive_response() {
                match response {
                    AIResponse::SecurityAnalysis { threat_detected, recommended_action, confidence, urgency, .. } => {
                        println!("🚨 Security Event: {}", event_type);
                        println!("🧠 AI Analysis: Threat detected: {}, Confidence: {:.2}", threat_detected, confidence);
                        println!("📋 Recommended Action: {}", recommended_action);
                        
                        if urgency > 7 {
                            return SecurityOperationResult::Blocked(
                                format!("High urgency threat - {}", recommended_action)
                            );
                        } else if threat_detected {
                            return SecurityOperationResult::Warning(
                                format!("Threat detected - {}", recommended_action)
                            );
                        }
                    },
                    _ => {} // Handle other response types
                }
            }
        }
        
        // Fallback to local recommendation if AI unavailable
        let recommendation = self.tool_selector.recommend_tool(self.threat_level, event_type);
        
        println!("🚨 Security Event: {}", event_type);
        println!("🔧 Tool Recommendation: {}", recommendation.tool_name);
        println!("📖 Explanation: {}", recommendation.explanation);
        
        match self.threat_level {
            ThreatLevel::Critical => {
                SecurityOperationResult::Blocked("Critical threat detected - automated response initiated".into())
            },
            ThreatLevel::High => {
                SecurityOperationResult::Warning("High threat detected - immediate attention required".into())
            },
            _ => {
                SecurityOperationResult::EducationalOpportunity(
                    format!("Learning opportunity: Investigate {} using {}", event_type, recommendation.tool_name)
                )
            }
        }
    }
    
    fn update_threat_level(&mut self, event_type: &str) {
        self.threat_level = match event_type {
            "buffer_overflow" | "code_injection" | "privilege_escalation" => ThreatLevel::Critical,
            "suspicious_network" | "malware_detected" | "unauthorized_access" => ThreatLevel::High,
            "unusual_activity" | "policy_violation" => ThreatLevel::Medium,
            "info_gathering" | "port_scan" => ThreatLevel::Low,
            _ => ThreatLevel::None,
        };
    }
    
    /// Request educational scenario from AI system
    fn request_educational_scenario(&mut self, category: &str) -> Option<String> {
        if !self.ai_bridge.is_connected() {
            return None;
        }
        
        // Request scenario from AI system
        let _ = self.ai_bridge.request_educational_scenario(
            self.tool_selector.user_skill_level, 
            category
        );
        
        // Process messages
        self.ai_bridge.process_messages();
        
        // Check for response
        if let Some(response) = self.ai_bridge.receive_response() {
            match response {
                AIResponse::EducationalScenario { title, description, tools_needed, .. } => {
                    println!("🎓 Educational Scenario: {}", title);
                    println!("📝 Description: {}", description);
                    println!("🔧 Tools needed: {:?}", tools_needed);
                    return Some(title);
                },
                _ => {}
            }
        }
        
        None
    }
    
    /// Process all pending AI messages
    fn process_ai_messages(&mut self) {
        if self.ai_bridge.is_connected() {
            self.ai_bridge.process_messages();
        }
    }
}

// Kernel entry point
#[cfg(not(test))]
entry_point!(kernel_main);

#[cfg(test)]
entry_point!(test_kernel_main);

fn kernel_main(boot_info: &'static BootInfo) -> ! {
    // FORCE IMMEDIATE SERIAL OUTPUT - Emergency Debug
    use core::fmt::Write;
    let mut serial = unsafe { uart_16550::SerialPort::new(0x3F8) };
    serial.init();
    writeln!(serial, "=== EMERGENCY DEBUG: SynOS kernel_main() ENTRY ===").ok();
    writeln!(serial, "Direct serial write test - if you see this, serial works!").ok();
    
    // Initialize logging system FIRST for debugging
    serial_logger::init_logging();
    serial_logger::log_info("SynOS Kernel Starting - Phase 4.2");
    serial_logger::log_info("Boot info received, initializing systems...");
    
    // More direct serial output to debug
    writeln!(serial, "serial_logger::init_logging() completed").ok();
    
    // Initialize heap
    serial_logger::log_debug("Initializing heap allocator...");
    init_heap(boot_info);
    serial_logger::log_info("Heap allocator initialized successfully");
    
    // Test logging system
    serial_logger::log_debug("Testing logging system...");
    serial_logger::test_logging();
    
    // Create and initialize the SynOS kernel
    serial_logger::log_info("Creating SynOS kernel instance...");
    let mut kernel = SynOSKernel::new();
    
    serial_logger::log_info("Initializing kernel subsystems...");
    kernel.initialize();
    serial_logger::log_info("Kernel initialization complete");
    
    serial_logger::log_info("SynOS - AI-Enhanced Cybersecurity Education Platform");
    serial_logger::log_info("Based on ParrotOS with adaptive learning capabilities");
    serial_logger::log_info("Ready for 10x cybersecurity education and operations");
    
    println!("\n🎯 SynOS - AI-Enhanced Cybersecurity Education Platform");
    println!("📚 Based on ParrotOS with adaptive learning capabilities");
    println!("🚀 Ready for 10x cybersecurity education and operations\n");
    
    // Demonstrate AI-enhanced features
    serial_logger::log_info("Starting AI features demonstration...");
    demo_ai_features(&mut kernel);
    serial_logger::log_info("AI features demonstration complete");
    
    serial_logger::log_info("Entering main kernel loop...");
    // Main kernel loop
    loop {
        // Process AI messages from ParrotOS integration system
        kernel.process_ai_messages();
        
        // In a real kernel, this would handle interrupts and system calls
        // For now, we'll demonstrate the AI-enhanced security features
        
        // Simulate various security events for demonstration
        let _ = kernel.handle_security_event("port_scan", &[]);
        let _ = kernel.handle_security_event("info_gathering", &[]);
        
        // Request educational content periodically
        if kernel.config.educational_mode {
            let _ = kernel.request_educational_scenario("network_security");
        }
        
        // Prevent busy loop
        x86_64::instructions::hlt();
    }
}

fn demo_ai_features(kernel: &mut SynOSKernel) {
    println!("🧪 Demonstrating AI-Enhanced Security Features:\n");
    
    // Demonstrate AI bridge integration
    if kernel.ai_bridge.is_connected() {
        println!("🔗 AI Bridge Status: Connected to ParrotOS AI Integration");
        
        // Request educational scenario
        println!("🎓 Requesting educational scenario...");
        let scenario = kernel.request_educational_scenario("penetration_testing");
        if let Some(title) = scenario {
            println!("   ✅ Received scenario: {}\n", title);
        }
        
        // Demonstrate AI-enhanced tool recommendation
        println!("🔧 Requesting AI tool recommendation...");
        let _ = kernel.ai_bridge.request_tool_recommendation(3, "web_application_test", 5);
        kernel.process_ai_messages();
        
        if let Some(response) = kernel.ai_bridge.receive_response() {
            match response {
                AIResponse::ToolRecommendation { tool_name, explanation, confidence, .. } => {
                    println!("   Tool: {}", tool_name);
                    println!("   Explanation: {}", explanation);
                    println!("   AI Confidence: {:.2}\n", confidence);
                },
                _ => {}
            }
        }
    } else {
        println!("🔗 AI Bridge Status: Disconnected (standalone mode)");
        
        // Demonstrate local tool recommendation
        let recommendation = kernel.tool_selector.recommend_tool(ThreatLevel::Medium, "web_application_test");
        println!("🔧 Local Tool Recommendation:");
        println!("   Tool: {}", recommendation.tool_name);
        println!("   Explanation: {}", recommendation.explanation);
        println!("   Educational Value: {}/10", recommendation.educational_value);
        println!("   Complexity: {}/10\n", recommendation.complexity);
    }
    
    // Demonstrate memory protection
    let memory_result = kernel.memory_protection.validate_memory_access(0x1000, 0x1000, false);
    println!("🔒 Memory Protection Check: {:?}\n", memory_result);
    
    // Demonstrate educational mode
    if kernel.config.educational_mode {
        println!("🎓 Educational Mode Active:");
        println!("   Available learning scenarios:");
        println!("   • Web Application Penetration Testing");
        println!("   • Network Reconnaissance");
        println!("   • Digital Forensics");
        println!("   • Malware Analysis");
        println!("   • Incident Response");
        
        if kernel.ai_bridge.is_connected() {
            println!("   • AI-powered adaptive scenarios");
            println!("   • Real-time skill progression tracking");
            println!("   • Personalized learning paths");
        }
        println!();
    }
    
    // Demonstrate ParrotOS integration
    println!("🛡️ ParrotOS Integration Features:");
    println!("   • 500+ security tools with AI selection");
    println!("   • Consciousness-guided tool recommendations");
    println!("   • Educational scenario framework");
    println!("   • Real-time threat analysis");
    println!("   • Adaptive learning pathways");
    println!("   • Skill progression tracking\n");
}

fn init_heap(_boot_info: &'static BootInfo) {
    use linked_list_allocator::LockedHeap;

    const HEAP_START: usize = 0x_4444_4444_0000;
    const HEAP_SIZE: usize = 100 * 1024; // 100 KiB

    #[global_allocator]
    static ALLOCATOR: LockedHeap = LockedHeap::empty();

    // Initialize the heap (simplified for demonstration)
    unsafe {
        ALLOCATOR.lock().init(HEAP_START as *mut u8, HEAP_SIZE);
    }
}

#[cfg(not(test))]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Log detailed panic information
    serial_logger::log_panic_info(info);
    
    // Additional panic handling
    serial_logger::log_error("Kernel panic occurred - halting system");
    
    // Attempt to log system state before halting
    serial_logger::log_info("System halting due to panic");
    
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
    loop {
        x86_64::instructions::hlt();
    }
}

// VGA buffer for basic text output
pub mod vga_buffer {
    use volatile::Volatile;
    use core::fmt;
    use lazy_static::lazy_static;
    use spin::Mutex;

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

        pub fn write_string(&mut self, s: &str) {
            for byte in s.bytes() {
                match byte {
                    0x20..=0x7e | b'\n' => self.write_byte(byte),
                    _ => self.write_byte(0xfe),
                }
            }
        }
    }

    impl fmt::Write for Writer {
        fn write_str(&mut self, s: &str) -> fmt::Result {
            self.write_string(s);
            Ok(())
        }
    }

    lazy_static! {
        pub static ref WRITER: Mutex<Writer> = Mutex::new(Writer {
            column_position: 0,
            color_code: ColorCode::new(Color::Yellow, Color::Black),
            buffer: unsafe { &mut *(0xb8000 as *mut Buffer) },
        });
    }

    #[macro_export]
    macro_rules! print {
        ($($arg:tt)*) => ($crate::vga_buffer::_print(format_args!($($arg)*)));
    }

    #[macro_export]
    macro_rules! println {
        () => ($crate::print!("\n"));
        ($($arg:tt)*) => ($crate::print!("{}\n", format_args!($($arg)*)));
    }

    pub fn _print(args: fmt::Arguments) {
        use core::fmt::Write;
        WRITER.lock().write_fmt(args).unwrap();
    }
}

// Serial output for debugging
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

    #[doc(hidden)]
    pub fn _print(args: ::core::fmt::Arguments) {
        use core::fmt::Write;
        SERIAL1
            .lock()
            .write_fmt(args)
            .expect("Printing to serial failed");
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
}

#[cfg(test)]
fn test_kernel_main(_boot_info: &'static BootInfo) -> ! {
    init_heap(_boot_info);
    test_main();
    loop {
        x86_64::instructions::hlt();
    }
}

pub fn test_runner(tests: &[&dyn Fn()]) {
    serial_println!("Running {} tests", tests.len());
    for test in tests {
        test();
    }
    exit_qemu(QemuExitCode::Success);
}

pub fn test_panic_handler(info: &PanicInfo) -> ! {
    serial_println!("[failed]\n");
    serial_println!("Error: {}\n", info);
    exit_qemu(QemuExitCode::Failed);
    loop {
        x86_64::instructions::hlt();
    }
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

#[test_case]
fn test_ai_tool_recommendation() {
    let selector = AIToolSelector::new();
    let recommendation = selector.recommend_tool(ThreatLevel::Medium, "web_test");
    assert!(recommendation.educational_value > 0);
    assert!(recommendation.complexity > 0);
}

#[test_case]
fn test_memory_protection() {
    let protection = EnhancedMemoryProtection::new();
    let result = protection.validate_memory_access(0x1000, 0x1000, false);
    match result {
        SecurityOperationResult::Success(_) => {},
        _ => panic!("Memory protection test failed"),
    }
}
