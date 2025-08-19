; Syn_OS Cybersecurity Education Kernel Bootloader  
; Multiboot-compliant bootloader for QEMU testing

MAGIC       equ 0x1BADB002          ; Multiboot magic number
FLAGS       equ (1<<0 | 1<<1)       ; Multiboot flags (align modules, mem info)
CHECKSUM    equ -(MAGIC + FLAGS)    ; Multiboot checksum

; Multiboot header
section .multiboot
align 4
    dd MAGIC
    dd FLAGS  
    dd CHECKSUM

; Reserve stack space
section .bss
align 16
stack_bottom:
    resb 16384 ; 16 KiB stack
stack_top:

; Kernel entry point
section .text
global _start
_start:
    ; Set up stack
    mov esp, stack_top
    
    ; Clear direction flag for string operations
    cld
    
    ; Call kernel main function  
    call kernel_main
    
    ; Disable interrupts and halt if kernel returns
    cli
.halt:
    hlt
    jmp .halt