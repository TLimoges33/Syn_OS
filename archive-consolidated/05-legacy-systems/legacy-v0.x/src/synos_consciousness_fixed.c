/*
 * SynOS Consciousness Monitoring Kernel Module
 * Phase 4.2: Advanced Logging and Debugging Infrastructure
 * 
 * This kernel module provides the core consciousness monitoring functionality
 * that was originally implemented in our custom kernel, but now as a loadable
 * Linux kernel module for stability and compatibility.
 */

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/sched.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/timekeeping.h>
#include <linux/vmalloc.h>
#include <linux/device.h>

#define DEVICE_NAME "synos"
#define CLASS_NAME "synos_class"
#define PROC_ENTRY "synos_consciousness"
#define MAX_COMPONENTS 64
#define MAX_EVENTS 1000
#define MAX_LOG_ENTRIES 5000

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SynOS Team");
MODULE_DESCRIPTION("SynOS Consciousness Monitoring and Advanced Logging");
MODULE_VERSION("4.2.0");

static int major_number;
static struct class* synos_class = NULL;
static struct device* synos_device = NULL;
static struct mutex synos_mutex;
static struct proc_dir_entry *proc_entry;

/* ==================== Phase 4.2: Data Structures ==================== */

/* Consciousness Component State */
typedef enum {
    COMPONENT_INACTIVE = 0,
    COMPONENT_INITIALIZING = 1,
    COMPONENT_ACTIVE = 2,
    COMPONENT_DEGRADED = 3,
    COMPONENT_CRITICAL = 4,
    COMPONENT_FAILED = 5,
} ComponentState;

/* Consciousness Monitoring Level */
typedef enum {
    MONITORING_BASIC = 0,
    MONITORING_STANDARD = 1,
    MONITORING_DETAILED = 2,
    MONITORING_COMPREHENSIVE = 3,
} MonitoringLevel;

/* Log Levels (matching our advanced logger) */
typedef enum {
    SYNOS_LOG_EMERGENCY = 0,
    SYNOS_LOG_ALERT = 1,
    SYNOS_LOG_CRITICAL = 2,
    SYNOS_LOG_ERROR = 3,
    SYNOS_LOG_WARNING = 4,
    SYNOS_LOG_NOTICE = 5,
    SYNOS_LOG_INFO = 6,
    SYNOS_LOG_DEBUG = 7,
    SYNOS_LOG_TRACE = 8,
} LogLevel;

/* Log Categories (matching our advanced logger) */
typedef enum {
    SYNOS_LOG_KERNEL = 0,
    SYNOS_LOG_MEMORY = 1,
    SYNOS_LOG_SECURITY = 2,
    SYNOS_LOG_AI = 3,
    SYNOS_LOG_CONSCIOUSNESS = 4,
    SYNOS_LOG_PERFORMANCE = 5,
    SYNOS_LOG_DEBUG_CAT = 6,
    SYNOS_LOG_SYSTEM = 7,
    SYNOS_LOG_NETWORK = 8,
    SYNOS_LOG_STORAGE = 9,
    SYNOS_LOG_USER = 10,
} LogCategory;

/* Consciousness Component */
struct consciousness_component {
    char name[64];
    ComponentState state;
    u64 health_score;
    u64 last_update;
    u64 total_events;
    bool active;
};

/* Consciousness Event */
struct consciousness_event {
    u64 timestamp;
    LogLevel level;
    LogCategory category;
    char component[32];
    char event_type[32];
    char description[256];
    u32 data_size;
};

/* Log Entry */
struct log_entry {
    u64 timestamp;
    LogLevel level;
    LogCategory category;
    char component[32];
    char function[64];
    char message[512];
    pid_t pid;
};

/* System Metrics */
struct system_metrics {
    u64 total_components;
    u64 active_components;
    u64 total_events;
    u64 total_log_entries;
    u64 memory_allocated;
    u64 cpu_cycles;
    u64 consciousness_level;
    u64 last_update;
};

/* ==================== Global State ==================== */

static struct consciousness_component components[MAX_COMPONENTS];
static struct consciousness_event events[MAX_EVENTS];
static struct log_entry log_buffer[MAX_LOG_ENTRIES];
static struct system_metrics metrics = {0};

static u32 component_count = 0;
static u32 event_head = 0;
static u32 log_head = 0;
static MonitoringLevel monitoring_level = MONITORING_STANDARD;

/* Kernel thread for consciousness monitoring */
static struct task_struct *consciousness_thread;
static int thread_running = 0;

/* ==================== Helper Functions ==================== */

static u64 get_timestamp(void)
{
    return ktime_get_ns();
}

static int find_component(const char *name)
{
    int i;
    for (i = 0; i < component_count; i++) {
        if (strcmp(components[i].name, name) == 0) {
            return i;
        }
    }
    return -1;
}

static void add_event(LogLevel level, LogCategory category, 
                     const char *component, const char *event_type, 
                     const char *description)
{
    struct consciousness_event *event = &events[event_head];
    
    event->timestamp = get_timestamp();
    event->level = level;
    event->category = category;
    strncpy(event->component, component, sizeof(event->component) - 1);
    strncpy(event->event_type, event_type, sizeof(event->event_type) - 1);
    strncpy(event->description, description, sizeof(event->description) - 1);
    event->data_size = 0;
    
    event_head = (event_head + 1) % MAX_EVENTS;
    metrics.total_events++;
}

static void add_log(LogLevel level, LogCategory category, 
                   const char *component, const char *function, 
                   const char *message)
{
    struct log_entry *entry = &log_buffer[log_head];
    
    entry->timestamp = get_timestamp();
    entry->level = level;
    entry->category = category;
    strncpy(entry->component, component, sizeof(entry->component) - 1);
    strncpy(entry->function, function, sizeof(entry->function) - 1);
    strncpy(entry->message, message, sizeof(entry->message) - 1);
    entry->pid = current->pid;
    
    log_head = (log_head + 1) % MAX_LOG_ENTRIES;
    metrics.total_log_entries++;
}

/* ==================== Component Management ==================== */

static int register_component(const char *name)
{
    if (component_count >= MAX_COMPONENTS) {
        return -ENOMEM;
    }
    
    if (find_component(name) >= 0) {
        return -EEXIST;  /* Component already exists */
    }
    
    struct consciousness_component *comp = &components[component_count];
    strncpy(comp->name, name, sizeof(comp->name) - 1);
    comp->state = COMPONENT_INITIALIZING;
    comp->health_score = 100;
    comp->last_update = get_timestamp();
    comp->total_events = 0;
    comp->active = true;
    
    component_count++;
    metrics.total_components++;
    metrics.active_components++;
    
    add_event(SYNOS_LOG_INFO, SYNOS_LOG_CONSCIOUSNESS, name, "register", "Component registered");
    
    printk(KERN_INFO "SynOS: Registered consciousness component: %s\n", name);
    return 0;
}

/* ==================== Consciousness Monitoring Thread ==================== */

static u64 calculate_consciousness_level(void)
{
    if (metrics.total_components == 0) {
        return 0;
    }
    
    u64 total_health = 0;
    u64 active_ratio = (metrics.active_components * 100) / metrics.total_components;
    
    int i;
    for (i = 0; i < component_count; i++) {
        if (components[i].active) {
            total_health += components[i].health_score;
        }
    }
    
    u64 avg_health = total_health / component_count;
    
    /* Calculate consciousness level as combination of active ratio and health */
    return (active_ratio + avg_health) / 2;
}

static int consciousness_monitor_thread(void *data)
{
    printk(KERN_INFO "SynOS: Consciousness monitoring thread started\n");
    
    while (!kthread_should_stop() && thread_running) {
        /* Update consciousness level */
        metrics.consciousness_level = calculate_consciousness_level();
        
        /* Update CPU cycles */
        metrics.cpu_cycles += 1000000; /* Approximate */
        
        /* Check component health */
        int i;
        for (i = 0; i < component_count; i++) {
            struct consciousness_component *comp = &components[i];
            if (comp->active) {
                u64 now = get_timestamp();
                u64 elapsed = now - comp->last_update;
                
                /* If component hasn't updated in 60 seconds, mark as degraded */
                if (elapsed > 60000000000ULL) {  /* 60 seconds in nanoseconds */
                    if (comp->state == COMPONENT_ACTIVE) {
                        comp->state = COMPONENT_DEGRADED;
                        comp->health_score = max(comp->health_score - 10, 0ULL);
                        add_event(SYNOS_LOG_WARNING, SYNOS_LOG_CONSCIOUSNESS, comp->name, 
                                 "degraded", "Component became unresponsive");
                    }
                }
            }
        }
        
        metrics.last_update = get_timestamp();
        
        /* Sleep for 5 seconds */
        msleep(5000);
    }
    
    printk(KERN_INFO "SynOS: Consciousness monitoring thread stopped\n");
    return 0;
}

/* ==================== Device Operations ==================== */

static int device_open(struct inode *inode, struct file *file)
{
    if (!mutex_trylock(&synos_mutex)) {
        printk(KERN_ALERT "SynOS: Device busy\n");
        return -EBUSY;
    }
    
    add_log(SYNOS_LOG_DEBUG, SYNOS_LOG_KERNEL, "device", "open", "Device opened");
    printk(KERN_INFO "SynOS: Device opened by PID %d\n", current->pid);
    return 0;
}

static int device_release(struct inode *inode, struct file *file)
{
    mutex_unlock(&synos_mutex);
    add_log(SYNOS_LOG_DEBUG, SYNOS_LOG_KERNEL, "device", "release", "Device closed");
    printk(KERN_INFO "SynOS: Device closed\n");
    return 0;
}

static ssize_t device_read(struct file *filp, char *buffer, size_t len, loff_t *offset)
{
    char message[2048];
    int bytes_read = 0;
    
    if (*offset > 0) {
        return 0;
    }
    
    /* Prepare consciousness status message */
    bytes_read = snprintf(message, sizeof(message),
        "=== SynOS Consciousness Status ===\n"
        "Phase: 4.2 (Advanced Logging & Debugging)\n"
        "Monitoring Level: %d\n"
        "Total Components: %llu\n"
        "Active Components: %llu\n"
        "Consciousness Level: %llu%%\n"
        "Total Events: %llu\n"
        "Total Log Entries: %llu\n"
        "Memory Allocated: %llu bytes\n"
        "CPU Cycles: %llu\n"
        "Last Update: %llu ns\n\n"
        "Recent Components:\n",
        monitoring_level,
        metrics.total_components,
        metrics.active_components,
        metrics.consciousness_level,
        metrics.total_events,
        metrics.total_log_entries,
        metrics.memory_allocated,
        metrics.cpu_cycles,
        metrics.last_update
    );
    
    /* Add component information */
    int i;
    for (i = 0; i < min(component_count, 10); i++) {
        int remaining = sizeof(message) - bytes_read;
        if (remaining > 0) {
            bytes_read += snprintf(message + bytes_read, remaining,
                "  %s: state=%d, health=%llu%%\n",
                components[i].name,
                components[i].state,
                components[i].health_score
            );
        }
    }
    
    if (bytes_read > len) {
        bytes_read = len;
    }
    
    if (copy_to_user(buffer, message, bytes_read)) {
        return -EFAULT;
    }
    
    *offset += bytes_read;
    return bytes_read;
}

static ssize_t device_write(struct file *filp, const char *buffer, size_t len, loff_t *offset)
{
    char kernel_buffer[512];
    
    if (len > sizeof(kernel_buffer) - 1) {
        return -EINVAL;
    }
    
    if (copy_from_user(kernel_buffer, buffer, len)) {
        return -EFAULT;
    }
    
    kernel_buffer[len] = '\0';
    
    /* Parse commands */
    if (strncmp(kernel_buffer, "REGISTER:", 9) == 0) {
        char *component_name = kernel_buffer + 9;
        /* Remove newline if present */
        char *newline = strchr(component_name, '\n');
        if (newline) *newline = '\0';
        
        int result = register_component(component_name);
        if (result == 0) {
            add_log(SYNOS_LOG_INFO, SYNOS_LOG_CONSCIOUSNESS, component_name, "register", 
                   "Component registered via device");
        }
    }
    else if (strncmp(kernel_buffer, "LOG:", 4) == 0) {
        char *log_msg = kernel_buffer + 4;
        add_log(SYNOS_LOG_INFO, SYNOS_LOG_USER, "device", "write", log_msg);
    }
    else if (strncmp(kernel_buffer, "EVENT:", 6) == 0) {
        char *event_msg = kernel_buffer + 6;
        add_event(SYNOS_LOG_INFO, SYNOS_LOG_USER, "device", "user_event", event_msg);
    }
    
    return len;
}

/* IOCTL definitions */
#define SYNOS_IOC_MAGIC 'S'
#define SYNOS_GET_CONSCIOUSNESS_LEVEL _IOR(SYNOS_IOC_MAGIC, 1, unsigned long)
#define SYNOS_RESET_METRICS _IO(SYNOS_IOC_MAGIC, 2)
#define SYNOS_GET_COMPONENT_COUNT _IOR(SYNOS_IOC_MAGIC, 3, unsigned long)
#define SYNOS_SET_MONITORING_LEVEL _IOW(SYNOS_IOC_MAGIC, 4, int)

static long device_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    switch (cmd) {
        case SYNOS_GET_CONSCIOUSNESS_LEVEL:
            if (copy_to_user((unsigned long *)arg, &metrics.consciousness_level, 
                            sizeof(unsigned long))) {
                return -EFAULT;
            }
            return 0;
            
        case SYNOS_RESET_METRICS:
            memset(&metrics, 0, sizeof(metrics));
            metrics.last_update = get_timestamp();
            add_log(SYNOS_LOG_INFO, SYNOS_LOG_SYSTEM, "device", "ioctl", "Metrics reset");
            return 0;
            
        case SYNOS_GET_COMPONENT_COUNT:
            {
                unsigned long count = component_count;
                if (copy_to_user((unsigned long *)arg, &count, sizeof(unsigned long))) {
                    return -EFAULT;
                }
                return 0;
            }
            
        case SYNOS_SET_MONITORING_LEVEL:
            {
                int level = (int)arg;
                if (level >= 0 && level <= MONITORING_COMPREHENSIVE) {
                    monitoring_level = level;
                    add_log(SYNOS_LOG_INFO, SYNOS_LOG_SYSTEM, "device", "ioctl", "Monitoring level changed");
                    return 0;
                }
                return -EINVAL;
            }
            
        default:
            return -EINVAL;
    }
}

/* File operations structure */
static struct file_operations fops = {
    .open = device_open,
    .read = device_read,
    .write = device_write,
    .release = device_release,
    .unlocked_ioctl = device_ioctl,
};

/* ==================== Proc Interface ==================== */

static int proc_show(struct seq_file *m, void *v)
{
    seq_printf(m, "=== SynOS Phase 4.2: Consciousness Monitoring ===\n\n");
    
    seq_printf(m, "System Metrics:\n");
    seq_printf(m, "  Monitoring Level: %d\n", monitoring_level);
    seq_printf(m, "  Total Components: %llu\n", metrics.total_components);
    seq_printf(m, "  Active Components: %llu\n", metrics.active_components);
    seq_printf(m, "  Consciousness Level: %llu%%\n", metrics.consciousness_level);
    seq_printf(m, "  Total Events: %llu\n", metrics.total_events);
    seq_printf(m, "  Total Log Entries: %llu\n", metrics.total_log_entries);
    seq_printf(m, "  Memory Allocated: %llu bytes\n", metrics.memory_allocated);
    seq_printf(m, "  CPU Cycles: %llu\n", metrics.cpu_cycles);
    seq_printf(m, "  Last Update: %llu ns\n", metrics.last_update);
    
    seq_printf(m, "\nRegistered Components:\n");
    int i;
    for (i = 0; i < component_count; i++) {
        struct consciousness_component *comp = &components[i];
        seq_printf(m, "  [%d] %s: state=%d, health=%llu%%, events=%llu, active=%s\n",
                   i, comp->name, comp->state, comp->health_score, 
                   comp->total_events, comp->active ? "yes" : "no");
    }
    
    seq_printf(m, "\nRecent Events (last 10):\n");
    for (i = 0; i < min(10, MAX_EVENTS); i++) {
        int idx = (event_head - 1 - i + MAX_EVENTS) % MAX_EVENTS;
        struct consciousness_event *event = &events[idx];
        if (event->timestamp > 0) {
            seq_printf(m, "  [%llu] %s.%s: %s\n",
                       event->timestamp, event->component, 
                       event->event_type, event->description);
        }
    }
    
    return 0;
}

static int proc_open(struct inode *inode, struct file *file)
{
    return single_open(file, proc_show, NULL);
}

static const struct proc_ops proc_fops = {
    .proc_open = proc_open,
    .proc_read = seq_read,
    .proc_lseek = seq_lseek,
    .proc_release = single_release,
};

/* ==================== Module Init/Exit ==================== */

static int __init synos_init(void)
{
    printk(KERN_INFO "SynOS: Initializing Phase 4.2 consciousness monitoring module\n");
    
    /* Initialize metrics */
    metrics.last_update = get_timestamp();
    
    /* Register character device */
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        printk(KERN_ALERT "SynOS: Failed to register device\n");
        return major_number;
    }
    
    /* Register device class - using newer API */
    synos_class = class_create(CLASS_NAME);
    if (IS_ERR(synos_class)) {
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "SynOS: Failed to register device class\n");
        return PTR_ERR(synos_class);
    }
    
    /* Register device driver */
    synos_device = device_create(synos_class, NULL, 
                                MKDEV(major_number, 0), NULL, DEVICE_NAME);
    if (IS_ERR(synos_device)) {
        class_destroy(synos_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "SynOS: Failed to create device\n");
        return PTR_ERR(synos_device);
    }
    
    /* Initialize mutex */
    mutex_init(&synos_mutex);
    
    /* Create proc entry */
    proc_entry = proc_create(PROC_ENTRY, 0444, NULL, &proc_fops);
    if (!proc_entry) {
        printk(KERN_WARNING "SynOS: Failed to create proc entry\n");
    }
    
    /* Register core kernel components */
    register_component("kernel_core");
    register_component("memory_manager");
    register_component("consciousness_monitor");
    register_component("advanced_logger");
    register_component("debug_infrastructure");
    
    /* Start consciousness monitoring thread */
    thread_running = 1;
    consciousness_thread = kthread_create(consciousness_monitor_thread, NULL, "synos_consciousness");
    if (IS_ERR(consciousness_thread)) {
        printk(KERN_WARNING "SynOS: Failed to create consciousness thread\n");
        consciousness_thread = NULL;
    } else {
        wake_up_process(consciousness_thread);
    }
    
    add_log(SYNOS_LOG_INFO, SYNOS_LOG_SYSTEM, "module", "init", "SynOS Phase 4.2 module loaded");
    
    printk(KERN_INFO "SynOS: Phase 4.2 consciousness monitoring module loaded successfully\n");
    printk(KERN_INFO "SynOS: Device: /dev/%s, Proc: /proc/%s\n", DEVICE_NAME, PROC_ENTRY);
    
    return 0;
}

static void __exit synos_exit(void)
{
    printk(KERN_INFO "SynOS: Shutting down Phase 4.2 consciousness monitoring module\n");
    
    /* Stop consciousness monitoring thread */
    thread_running = 0;
    if (consciousness_thread) {
        kthread_stop(consciousness_thread);
    }
    
    /* Remove proc entry */
    if (proc_entry) {
        proc_remove(proc_entry);
    }
    
    /* Clean up device */
    device_destroy(synos_class, MKDEV(major_number, 0));
    class_destroy(synos_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    
    mutex_destroy(&synos_mutex);
    
    add_log(SYNOS_LOG_INFO, SYNOS_LOG_SYSTEM, "module", "exit", "SynOS Phase 4.2 module unloaded");
    
    printk(KERN_INFO "SynOS: Phase 4.2 consciousness monitoring module unloaded\n");
}

module_init(synos_init);
module_exit(synos_exit);
