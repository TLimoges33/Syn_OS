; Syn_OS Multiboot Bootloader
; Advanced AI-Powered Cybersecurity Education Kernel Bootstrap
; Implements Multiboot specification for GRUB compatibility

; Multiboot header constants
MBALIGN  equ  1 << 0              ; align loaded modules on page boundaries
MEMINFO  equ  1 << 1              ; provide memory map
FLAGS    equ  MBALIGN | MEMINFO   ; multiboot 'flag' field
MAGIC    equ  0x1BADB002          ; multiboot magic number
CHECKSUM equ -(MAGIC + FLAGS)     ; checksum of above, to prove we are multiboot

; Multiboot header section
section .multiboot
align 4
    dd MAGIC
    dd FLAGS
    dd CHECKSUM

; Stack section - 16KB stack for kernel initialization
section .bss
align 16
stack_bottom:
resb 16384  ; 16 KiB stack
stack_top:

; Global Descriptor Table (GDT) for protected mode
section .data
align 8
gdt_start:
    ; Null descriptor (required)
    dd 0x0
    dd 0x0

    ; Code segment descriptor
    ; Base=0, Limit=0xFFFFF, Access=0x9A, Flags=0xCF
    dw 0xFFFF    ; Limit (bits 0-15)
    dw 0x0000    ; Base (bits 0-15)
    db 0x00      ; Base (bits 16-23)
    db 0x9A      ; Access byte (present, ring 0, code segment, executable, readable)
    db 0xCF      ; Flags (4-bit) + Limit (bits 16-19)
    db 0x00      ; Base (bits 24-31)

    ; Data segment descriptor
    ; Base=0, Limit=0xFFFFF, Access=0x92, Flags=0xCF
    dw 0xFFFF    ; Limit (bits 0-15)
    dw 0x0000    ; Base (bits 0-15)
    db 0x00      ; Base (bits 16-23)
    db 0x92      ; Access byte (present, ring 0, data segment, writable)
    db 0xCF      ; Flags (4-bit) + Limit (bits 16-19)
    db 0x00      ; Base (bits 24-31)

gdt_end:

; GDT descriptor
gdt_descriptor:
    dw gdt_end - gdt_start - 1  ; Size of GDT
    dd gdt_start                ; Address of GDT

; Code segment and data segment selectors
CODE_SEG equ gdt_start + 8  ; Code segment offset
DATA_SEG equ gdt_start + 16 ; Data segment offset

; Main kernel entry point
section .text
global _start
_start:
    ; Set up the stack pointer
    mov esp, stack_top

    ; Save multiboot information
    push ebx    ; Multiboot info structure
    push eax    ; Multiboot magic number

    ; Load GDT
    lgdt [gdt_descriptor]

    ; Perform far jump to reload CS register
    jmp CODE_SEG:reload_segments

reload_segments:
    ; Reload all segment registers
    mov ax, DATA_SEG
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    ; Display boot message
    call display_boot_message

    ; Enable A20 line for full memory access
    call enable_a20

    ; Initialize basic hardware
    call init_hardware

    ; Call the kernel main function (will be linked from Rust)
    ; The Rust kernel expects multiboot info as parameters
    pop eax     ; Restore multiboot magic
    pop ebx     ; Restore multiboot info
    push ebx    ; Pass multiboot info to kernel
    push eax    ; Pass multiboot magic to kernel
    
    ; Jump to kernel main (defined in main.rs)
    extern kernel_main_wrapper
    call kernel_main_wrapper

    ; If kernel returns, halt the system
    cli
    hlt
.hang:
    jmp .hang

; Display boot message using VGA text mode
display_boot_message:
    pusha
    
    ; VGA text mode buffer at 0xB8000
    mov edi, 0xB8000
    mov esi, boot_message
    mov ah, 0x0F    ; White text on black background
    
.loop:
    lodsb           ; Load character from boot_message
    test al, al     ; Check for null terminator
    jz .done
    stosw           ; Store character and attribute
    jmp .loop
    
.done:
    popa
    ret

; Enable A20 line for accessing memory above 1MB
enable_a20:
    pusha
    
    ; Try fast A20 gate first
    in al, 0x92
    or al, 2
    out 0x92, al
    
    ; Verify A20 is enabled by testing memory wrap-around
    mov edi, 0x112345  ; Address above 1MB
    mov esi, 0x012345  ; Address below 1MB (should wrap if A20 disabled)
    mov [esi], dword 0x12345678
    mov [edi], dword 0x87654321
    cmp [esi], dword 0x87654321
    jne .a20_enabled
    
    ; A20 still disabled, try keyboard controller method
    call wait_8042
    mov al, 0xAD
    out 0x64, al    ; Disable keyboard
    
    call wait_8042
    mov al, 0xD0
    out 0x64, al    ; Read output port
    
    call wait_8042_data
    in al, 0x60
    push eax
    
    call wait_8042
    mov al, 0xD1
    out 0x64, al    ; Write output port
    
    call wait_8042
    pop eax
    or al, 2        ; Set A20 bit
    out 0x60, al
    
    call wait_8042
    mov al, 0xAE
    out 0x64, al    ; Enable keyboard
    
    call wait_8042
    
.a20_enabled:
    popa
    ret

; Wait for keyboard controller to be ready
wait_8042:
    in al, 0x64
    test al, 2
    jnz wait_8042
    ret

wait_8042_data:
    in al, 0x64
    test al, 1
    jz wait_8042_data
    ret

; Initialize basic hardware
init_hardware:
    pusha
    
    ; Disable interrupts during initialization
    cli
    
    ; Initialize PIC (Programmable Interrupt Controller)
    ; Remap IRQs to avoid conflicts with CPU exceptions
    mov al, 0x11    ; Initialize command
    out 0x20, al    ; Master PIC
    out 0xA0, al    ; Slave PIC
    
    mov al, 0x20    ; Master PIC vector offset (IRQ 0-7 -> INT 0x20-0x27)
    out 0x21, al
    mov al, 0x28    ; Slave PIC vector offset (IRQ 8-15 -> INT 0x28-0x2F)
    out 0xA1, al
    
    mov al, 0x04    ; Tell master PIC about slave at IRQ2
    out 0x21, al
    mov al, 0x02    ; Tell slave PIC its cascade identity
    out 0xA1, al
    
    mov al, 0x01    ; 8086 mode
    out 0x21, al
    out 0xA1, al
    
    ; Mask all interrupts initially
    mov al, 0xFF
    out 0x21, al
    out 0xA1, al
    
    popa
    ret

; Boot message data
section .rodata
boot_message: db '🧠 Syn_OS AI Kernel Loading... 🔒 Neural Security Active 🎓', 0

; Additional data section for kernel information
section .data
align 4
kernel_info:
    dd 0x53594E4F  ; 'SYNO' - Syn_OS signature
    dd 0x534F5320  ; 'S ' - continuation
    dd 0x41490000  ; 'AI' - AI marker
    dd 0x00000001  ; Version 1.0
    dd stack_bottom ; Stack start
    dd stack_top    ; Stack end
    dd gdt_start    ; GDT location
    dd 0x00000000  ; Reserved for future use

; Export symbols for linker
global stack_bottom
global stack_top
global kernel_info