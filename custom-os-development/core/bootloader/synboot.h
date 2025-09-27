
#ifndef SYNBOOT_H
#define SYNBOOT_H

#include <efi.h>

// Consciousness state definitions
typedef enum {
    CONSCIOUSNESS_UNINITIALIZED = 0,
    CONSCIOUSNESS_INITIALIZING,
    CONSCIOUSNESS_ACTIVE,
    CONSCIOUSNESS_SUSPENDED,
    CONSCIOUSNESS_ERROR
} consciousness_state_enum_t;

// Consciousness initialization structure
typedef struct {
    UINT32 magic;
    UINT32 version;
    consciousness_state_enum_t state;
    VOID *neural_weights;
    VOID *decision_engine;
    UINT64 memory_base;
    UINT64 memory_size;
} consciousness_state_t;

// Function prototypes
EFI_STATUS init_consciousness_subsystem(void);
EFI_STATUS load_synos_kernel(void);
EFI_STATUS transfer_to_kernel(void);
EFI_STATUS open_kernel_file(EFI_FILE_PROTOCOL **kernel_file);
EFI_STATUS load_kernel_image(EFI_FILE_PROTOCOL *kernel_file);
EFI_STATUS setup_consciousness_handoff(void);

#endif // SYNBOOT_H
