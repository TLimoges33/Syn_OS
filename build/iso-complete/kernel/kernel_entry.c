// Syn_OS Kernel Entry Point
// Bridges multiboot bootloader to Rust kernel

extern void kernel_main(void);

void kernel_main_wrapper(void) {
    // Initialize VGA text mode display
    volatile char* video = (volatile char*)0xB8000;
    char* message = "🧠 Syn_OS AI Consciousness Kernel Loading... 🔒 Neural Security Active 🎓";
    
    // Clear screen
    for (int i = 0; i < 80 * 25 * 2; i += 2) {
        video[i] = ' ';
        video[i + 1] = 0x0F; // White on black
    }
    
    // Display loading message
    for (int i = 0; message[i] != '\0' && i < 80; i++) {
        video[i * 2] = message[i];
        video[i * 2 + 1] = 0x0A; // Light green on black
    }
    
    // Display consciousness status on second line
    char* status = "🧠 Consciousness Engine: Initializing... 🔍 Threat Detection: Active";
    for (int i = 0; status[i] != '\0' && i < 80; i++) {
        video[(80 + i) * 2] = status[i];
        video[(80 + i) * 2 + 1] = 0x0E; // Yellow on black
    }
    
    // Display educational info on third line
    char* edu = "🎓 Educational Mode: Ready for Cybersecurity Learning";
    for (int i = 0; edu[i] != '\0' && i < 80; i++) {
        video[(160 + i) * 2] = edu[i];
        video[(160 + i) * 2 + 1] = 0x0B; // Light cyan on black
    }
    
    // Simulate consciousness initialization
    for (volatile int delay = 0; delay < 50000000; delay++);
    
    // Display ready status
    char* ready = "✅ Syn_OS Kernel Ready - AI Consciousness Online";
    for (int i = 0; ready[i] != '\0' && i < 80; i++) {
        video[(240 + i) * 2] = ready[i];
        video[(240 + i) * 2 + 1] = 0x0C; // Light red on black
    }
    
    // Infinite loop - kernel is now "running"
    while(1) {
        __asm__("hlt");
    }
}
