/* Syn_OS Kernel Linker Script
 * Advanced AI-Powered Cybersecurity Education Kernel
 * Defines memory layout and section organization for multiboot compliance
 */

ENTRY(_start)

/* Define the target architecture */
OUTPUT_FORMAT(elf32-i386)
OUTPUT_ARCH(i386)

/* Memory layout for kernel loading */
SECTIONS
{
    /* Kernel is loaded at 1MB physical address by GRUB */
    . = 1M;

    /* Multiboot header must be at the beginning */
    .multiboot BLOCK(4K) : ALIGN(4K)
    {
        *(.multiboot)
    }

    /* Code section - contains executable instructions */
    .text BLOCK(4K) : ALIGN(4K)
    {
        *(.text)
        *(.text.*)
        
        /* Rust code sections */
        *(.text.unlikely)
        *(.text.startup)
        *(.text.hot)
        
        /* Keep important symbols */
        KEEP(*(.text._start))
        KEEP(*(.text.kernel_main))
    }

    /* Read-only data section */
    .rodata BLOCK(4K) : ALIGN(4K)
    {
        *(.rodata)
        *(.rodata.*)
        
        /* String literals and constants */
        *(.rodata.str1.1)
        *(.rodata.str1.4)
        *(.rodata.str1.8)
        
        /* Rust read-only data */
        *(.rodata.cst4)
        *(.rodata.cst8)
        *(.rodata.cst16)
    }

    /* Initialized data section */
    .data BLOCK(4K) : ALIGN(4K)
    {
        *(.data)
        *(.data.*)
        
        /* Global variables */
        *(.sdata)
        *(.sdata.*)
        
        /* Rust data sections */
        *(.data.rel.ro)
        *(.data.rel.ro.*)
    }

    /* Uninitialized data section (BSS) */
    .bss BLOCK(4K) : ALIGN(4K)
    {
        *(COMMON)
        *(.bss)
        *(.bss.*)
        *(.sbss)
        *(.sbss.*)
        
        /* Rust BSS sections */
        *(.dynbss)
    }

    /* Rust-specific sections for no_std environment */
    .got BLOCK(4K) : ALIGN(4K)
    {
        *(.got)
        *(.got.*)
    }

    .got.plt BLOCK(4K) : ALIGN(4K)
    {
        *(.got.plt)
    }

    /* Exception handling sections (for Rust panic handling) */
    .eh_frame BLOCK(4K) : ALIGN(4K)
    {
        *(.eh_frame)
        *(.eh_frame_hdr)
    }

    /* GCC exception handling */
    .gcc_except_table BLOCK(4K) : ALIGN(4K)
    {
        *(.gcc_except_table)
        *(.gcc_except_table.*)
    }

    /* Debug information sections (optional, for debugging) */
    .debug_info     0 : { *(.debug_info) }
    .debug_abbrev   0 : { *(.debug_abbrev) }
    .debug_line     0 : { *(.debug_line) }
    .debug_str      0 : { *(.debug_str) }
    .debug_ranges   0 : { *(.debug_ranges) }
    .debug_loc      0 : { *(.debug_loc) }

    /* Consciousness Engine specific sections */
    .consciousness BLOCK(4K) : ALIGN(4K)
    {
        __consciousness_start = .;
        *(.consciousness)
        *(.consciousness.*)
        __consciousness_end = .;
    }

    /* AI Integration sections */
    .ai_data BLOCK(4K) : ALIGN(4K)
    {
        __ai_data_start = .;
        *(.ai_data)
        *(.ai_data.*)
        __ai_data_end = .;
    }

    /* Security framework sections */
    .security BLOCK(4K) : ALIGN(4K)
    {
        __security_start = .;
        *(.security)
        *(.security.*)
        __security_end = .;
    }

    /* Educational framework sections */
    .educational BLOCK(4K) : ALIGN(4K)
    {
        __educational_start = .;
        *(.educational)
        *(.educational.*)
        __educational_end = .;
    }

    /* Neural Darwinism engine sections */
    .neural BLOCK(4K) : ALIGN(4K)
    {
        __neural_start = .;
        *(.neural)
        *(.neural.*)
        __neural_end = .;
    }

    /* Kernel module sections */
    .modules BLOCK(4K) : ALIGN(4K)
    {
        __modules_start = .;
        *(.modules)
        *(.modules.*)
        __modules_end = .;
    }

    /* Memory management sections */
    .memory BLOCK(4K) : ALIGN(4K)
    {
        __memory_start = .;
        *(.memory)
        *(.memory.*)
        __memory_end = .;
    }

    /* Define kernel boundaries for memory management */
    __kernel_start = 1M;
    __kernel_end = .;
    __kernel_size = __kernel_end - __kernel_start;

    /* Stack boundaries (defined in boot.asm) */
    PROVIDE(__stack_bottom = stack_bottom);
    PROVIDE(__stack_top = stack_top);

    /* Heap boundaries for dynamic allocation */
    __heap_start = ALIGN(4K);
    __heap_size = 16M;  /* 16MB heap */
    __heap_end = __heap_start + __heap_size;

    /* Consciousness engine memory pool */
    __consciousness_pool_start = __heap_end;
    __consciousness_pool_size = 32M;  /* 32MB for AI processing */
    __consciousness_pool_end = __consciousness_pool_start + __consciousness_pool_size;

    /* Security framework memory pool */
    __security_pool_start = __consciousness_pool_end;
    __security_pool_size = 16M;  /* 16MB for security operations */
    __security_pool_end = __security_pool_start + __security_pool_size;

    /* Educational framework memory pool */
    __educational_pool_start = __security_pool_end;
    __educational_pool_size = 8M;   /* 8MB for educational content */
    __educational_pool_end = __educational_pool_start + __educational_pool_size;

    /* Total kernel memory footprint */
    __total_kernel_memory = __educational_pool_end - __kernel_start;

    /* Discard unnecessary sections to reduce kernel size */
    /DISCARD/ :
    {
        *(.comment)
        *(.note)
        *(.note.*)
        *(.interp)
        *(.dynamic)
        *(.dynsym)
        *(.dynstr)
        *(.hash)
        *(.gnu.hash)
        *(.gnu.version)
        *(.gnu.version_d)
        *(.gnu.version_r)
        *(.rel.dyn)
        *(.rel.plt)
        *(.rela.dyn)
        *(.rela.plt)
        *(.init)
        *(.fini)
        *(.init_array)
        *(.fini_array)
        *(.ctors)
        *(.dtors)
        *(.jcr)
    }
}

/* Provide symbols for Rust kernel to access memory layout */
PROVIDE(__text_start = ADDR(.text));
PROVIDE(__text_end = ADDR(.text) + SIZEOF(.text));
PROVIDE(__rodata_start = ADDR(.rodata));
PROVIDE(__rodata_end = ADDR(.rodata) + SIZEOF(.rodata));
PROVIDE(__data_start = ADDR(.data));
PROVIDE(__data_end = ADDR(.data) + SIZEOF(.data));
PROVIDE(__bss_start = ADDR(.bss));
PROVIDE(__bss_end = ADDR(.bss) + SIZEOF(.bss));

/* Assert that kernel fits within reasonable memory bounds */
ASSERT(__kernel_size < 64M, "Kernel size exceeds 64MB limit")
ASSERT(__total_kernel_memory < 128M, "Total kernel memory exceeds 128MB limit")

/* Ensure proper alignment for all sections */
ASSERT((__text_start & 0xFFF) == 0, "Text section not page-aligned")
ASSERT((__data_start & 0xFFF) == 0, "Data section not page-aligned")
ASSERT((__bss_start & 0xFFF) == 0, "BSS section not page-aligned")