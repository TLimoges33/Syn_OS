/*
 * SynOS Kernel Configuration Header
 * Comprehensive configuration for consciousness-aware kernel
 */

#ifndef _SYNOS_KERNEL_CONFIG_H
#define _SYNOS_KERNEL_CONFIG_H

/* ==================== Core Kernel Configuration ==================== */

/* SynOS Version Information */
#define SYNOS_VERSION_MAJOR     1
#define SYNOS_VERSION_MINOR     0
#define SYNOS_VERSION_PATCH     0
#define SYNOS_VERSION_STRING    "1.0.0-consciousness-alpha"
#define SYNOS_BUILD_DATE        __DATE__
#define SYNOS_BUILD_TIME        __TIME__

/* Kernel Features */
#define CONFIG_SYNOS_CONSCIOUSNESS      1    /* Enable consciousness framework */
#define CONFIG_SYNOS_NEURAL_DARWINISM   1    /* Enable neural darwinism engine */
#define CONFIG_SYNOS_EDUCATIONAL        1    /* Enable educational features */
#define CONFIG_SYNOS_SECURITY_ENHANCED  1    /* Enhanced security features */
#define CONFIG_SYNOS_EBPF_FRAMEWORK     1    /* eBPF monitoring framework */

/* ==================== Consciousness Configuration ==================== */

/* Consciousness Engine Settings */
#define CONSCIOUSNESS_MAX_COMPONENTS    64      /* Maximum consciousness components */
#define CONSCIOUSNESS_UPDATE_INTERVAL   1000    /* Update interval in ms */
#define CONSCIOUSNESS_HEALTH_THRESHOLD  50      /* Health score threshold */
#define CONSCIOUSNESS_DEGRADATION_RATE  5       /* Points lost per missed heartbeat */

/* Neural Darwinism Settings */
#define NEURAL_POPULATION_SIZE          100     /* Neural population size */
#define NEURAL_LEARNING_RATE            0.1f    /* Learning rate */
#define NEURAL_MUTATION_RATE            0.05f   /* Mutation rate */
#define NEURAL_SELECTION_PRESSURE       0.8f    /* Selection pressure */

/* Consciousness Levels */
#define CONSCIOUSNESS_LEVEL_MINIMAL     25      /* Minimal awareness */
#define CONSCIOUSNESS_LEVEL_BASIC       50      /* Basic awareness */
#define CONSCIOUSNESS_LEVEL_ENHANCED    75      /* Enhanced awareness */
#define CONSCIOUSNESS_LEVEL_OPTIMAL     100     /* Optimal consciousness */

/* ==================== Security Configuration ==================== */

/* Enhanced Security Features */
#define CONFIG_SYNOS_THREAT_DETECTION   1    /* Real-time threat detection */
#define CONFIG_SYNOS_BEHAVIOR_ANALYSIS  1    /* Behavioral analysis */
#define CONFIG_SYNOS_ZERO_TRUST         1    /* Zero-trust architecture */
#define CONFIG_SYNOS_AI_SECURITY        1    /* AI-powered security */

/* eBPF Security Settings */
#define EBPF_MAX_PROGRAMS              32      /* Maximum eBPF programs */
#define EBPF_NETWORK_MONITORING         1      /* Network monitoring */
#define EBPF_PROCESS_MONITORING         1      /* Process monitoring */
#define EBPF_MEMORY_MONITORING          1      /* Memory monitoring */
#define EBPF_SECURITY_HOOKS             1      /* Security hooks */

/* Security Thresholds */
#define SECURITY_VIOLATION_THRESHOLD    10     /* Violations before action */
#define SECURITY_ANOMALY_THRESHOLD      5      /* Anomalies before alert */
#define SECURITY_QUARANTINE_TIMEOUT     300    /* Quarantine timeout (seconds) */

/* ==================== Educational Configuration ==================== */

/* Educational Framework */
#define CONFIG_EDUCATIONAL_FRAMEWORK    1    /* Enable educational features */
#define CONFIG_SKILL_TRACKING          1    /* Track learning progress */
#define CONFIG_ADAPTIVE_CURRICULUM      1    /* Adaptive learning paths */
#define CONFIG_CERTIFICATION_SUPPORT   1    /* Certification preparation */

/* Educational Settings */
#define MAX_STUDENTS_CONCURRENT         50     /* Maximum concurrent students */
#define LESSON_TIMEOUT                  3600   /* Lesson timeout (seconds) */
#define ASSESSMENT_RETRY_LIMIT          3      /* Assessment retry limit */
#define PROGRESS_SAVE_INTERVAL          60     /* Progress save interval (seconds) */

/* Educational Modes */
#define EDUCATIONAL_MODE_BEGINNER       1      /* Beginner mode */
#define EDUCATIONAL_MODE_INTERMEDIATE   2      /* Intermediate mode */
#define EDUCATIONAL_MODE_ADVANCED       3      /* Advanced mode */
#define EDUCATIONAL_MODE_PROFESSIONAL   4      /* Professional mode */

/* ==================== Performance Configuration ==================== */

/* Memory Management */
#define SYNOS_MAX_MEMORY_REGIONS        1024   /* Maximum memory regions */
#define SYNOS_MEMORY_POOL_SIZE          (16 * 1024 * 1024)  /* 16MB */
#define SYNOS_STACK_SIZE                (8 * 1024)          /* 8KB stack */

/* Process Management */
#define SYNOS_MAX_PROCESSES             256    /* Maximum processes */
#define SYNOS_TIME_SLICE                10     /* Time slice in ms */
#define SYNOS_PRIORITY_LEVELS           8      /* Priority levels */

/* I/O Configuration */
#define SYNOS_MAX_OPEN_FILES            1024   /* Maximum open files */
#define SYNOS_BUFFER_SIZE               4096   /* Default buffer size */
#define SYNOS_DMA_THRESHOLD             64     /* DMA threshold in KB */

/* ==================== Hardware Configuration ==================== */

/* CPU Architecture Support */
#define CONFIG_X86_64                   1      /* x86_64 support */
#define CONFIG_ARM64                    0      /* ARM64 support (future) */
#define CONFIG_RISC_V                   0      /* RISC-V support (future) */

/* Hardware Features */
#define CONFIG_SMP                      1      /* Symmetric multiprocessing */
#define CONFIG_NUMA                     1      /* NUMA support */
#define CONFIG_VIRTUALIZATION           1      /* Virtualization support */
#define CONFIG_HARDWARE_RANDOM          1      /* Hardware RNG support */

/* CPU Features */
#define CONFIG_AES_NI                   1      /* AES-NI acceleration */
#define CONFIG_AVX                      1      /* AVX instruction support */
#define CONFIG_TSX                      1      /* Intel TSX support */

/* ==================== Debugging Configuration ==================== */

/* Debug Features */
#define CONFIG_DEBUG_KERNEL             1      /* Kernel debugging */
#define CONFIG_DEBUG_CONSCIOUSNESS      1      /* Consciousness debugging */
#define CONFIG_DEBUG_SECURITY           1      /* Security debugging */
#define CONFIG_DEBUG_EDUCATIONAL        1      /* Educational debugging */

/* Debug Levels */
#define DEBUG_LEVEL_TRACE               0      /* Trace level */
#define DEBUG_LEVEL_DEBUG               1      /* Debug level */
#define DEBUG_LEVEL_INFO                2      /* Info level */
#define DEBUG_LEVEL_WARNING             3      /* Warning level */
#define DEBUG_LEVEL_ERROR               4      /* Error level */

/* Debug Settings */
#define DEBUG_BUFFER_SIZE               (1024 * 1024)  /* 1MB debug buffer */
#define DEBUG_MAX_ENTRIES               10000          /* Maximum debug entries */
#define DEBUG_RATE_LIMIT                100            /* Messages per second */

/* ==================== Network Configuration ==================== */

/* Network Stack */
#define CONFIG_NETWORK_STACK            1      /* Enable network stack */
#define CONFIG_IPV4                     1      /* IPv4 support */
#define CONFIG_IPV6                     1      /* IPv6 support */
#define CONFIG_TCP                      1      /* TCP support */
#define CONFIG_UDP                      1      /* UDP support */

/* Network Security */
#define CONFIG_FIREWALL                 1      /* Built-in firewall */
#define CONFIG_INTRUSION_DETECTION      1      /* IDS support */
#define CONFIG_PACKET_FILTERING         1      /* Packet filtering */
#define CONFIG_DPI                      1      /* Deep packet inspection */

/* ==================== File System Configuration ==================== */

/* File System Support */
#define CONFIG_EXT4                     1      /* ext4 support */
#define CONFIG_BTRFS                    1      /* Btrfs support */
#define CONFIG_ZFS                      0      /* ZFS support (future) */
#define CONFIG_TMPFS                    1      /* tmpfs support */

/* File System Security */
#define CONFIG_FILE_ENCRYPTION          1      /* File encryption */
#define CONFIG_ACCESS_CONTROL           1      /* Advanced access control */
#define CONFIG_AUDIT_LOGGING            1      /* Audit logging */

/* ==================== Device Driver Configuration ==================== */

/* Device Support */
#define CONFIG_PCI                      1      /* PCI support */
#define CONFIG_USB                      1      /* USB support */
#define CONFIG_SATA                     1      /* SATA support */
#define CONFIG_NVME                     1      /* NVMe support */

/* Graphics Support */
#define CONFIG_DRM                      1      /* Direct Rendering Manager */
#define CONFIG_FRAMEBUFFER              1      /* Framebuffer support */

/* ==================== Compatibility Configuration ==================== */

/* Linux Compatibility */
#define CONFIG_LINUX_SYSCALL_COMPAT    1      /* Linux syscall compatibility */
#define CONFIG_POSIX_COMPLIANCE         1      /* POSIX compliance */
#define CONFIG_GNU_EXTENSIONS           1      /* GNU extensions */

/* Application Support */
#define CONFIG_ELF_LOADER               1      /* ELF binary loader */
#define CONFIG_DYNAMIC_LINKING          1      /* Dynamic linking support */
#define CONFIG_SHARED_LIBRARIES         1      /* Shared library support */

/* ==================== Validation Macros ==================== */

/* Compile-time validation */
#if CONSCIOUSNESS_MAX_COMPONENTS > 128
#error "CONSCIOUSNESS_MAX_COMPONENTS cannot exceed 128"
#endif

#if NEURAL_POPULATION_SIZE < 10
#error "NEURAL_POPULATION_SIZE must be at least 10"
#endif

#if SYNOS_MAX_PROCESSES > 1024
#error "SYNOS_MAX_PROCESSES cannot exceed 1024"
#endif

/* Feature dependency validation */
#if CONFIG_SYNOS_CONSCIOUSNESS && !CONFIG_SYNOS_NEURAL_DARWINISM
#error "Consciousness requires Neural Darwinism engine"
#endif

#if CONFIG_SYNOS_EDUCATIONAL && !CONFIG_SYNOS_CONSCIOUSNESS
#error "Educational framework requires consciousness"
#endif

#if CONFIG_SYNOS_EBPF_FRAMEWORK && !CONFIG_SYNOS_SECURITY_ENHANCED
#error "eBPF framework requires enhanced security"
#endif

#endif /* _SYNOS_KERNEL_CONFIG_H */