/* Syn_OS Kernel Linker Script */
/* Links the cybersecurity education kernel for multiboot loading */

ENTRY(_start)

SECTIONS
{
    /* Kernel loaded at 1MB by bootloader */
    . = 1M;

    .boot :
    {
        /* Multiboot header first */
        *(.multiboot)
    }

    .text : ALIGN(4K)
    {
        *(.text)
    }

    .rodata : ALIGN(4K)
    {
        *(.rodata)
    }

    .data : ALIGN(4K)
    {
        *(.data)
    }

    .bss : ALIGN(4K)
    {
        *(COMMON)
        *(.bss)
    }
}