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
    COMPONENT_FAILED = 4
} component_state_t;

/* Consciousness Event Types */
typedef enum {
    EVENT_COMPONENT_REGISTERED = 1,
    EVENT_COMPONENT_STATE_CHANGE = 2,
    EVENT_CONSCIOUSNESS_LEVEL_CHANGE = 3,
    EVENT_HEALTH_CHECK = 4,
    EVENT_ERROR = 5,
    EVENT_WARNING = 6,
    EVENT_INFO = 7
} event_type_t;

/* Log Levels */
typedef enum {
    LOG_TRACE = 0,
    LOG_DEBUG = 1,
    LOG_INFO = 2,
    LOG_NOTICE = 3,
    LOG_WARNING = 4,
    LOG_ERROR = 5,
    LOG_CRITICAL = 6,
    LOG_ALERT = 7,
    LOG_EMERGENCY = 8
} log_level_t;

/* Log Categories */
typedef enum {
    CAT_CONSCIOUSNESS = 0,
    CAT_COMPONENT = 1,
    CAT_HEALTH = 2,
    CAT_PERFORMANCE = 3,
    CAT_SECURITY = 4,
    CAT_NETWORK = 5,
    CAT_STORAGE = 6,
    CAT_MEMORY = 7,
    CAT_PROCESS = 8,
    CAT_KERNEL = 9,
    CAT_USER = 10
} log_category_t;

/* Consciousness Component */
struct consciousness_component {
    char name[32];
    component_state_t state;
    u64 last_heartbeat;
    u32 health_score;
    u32 error_count;
    u32 warning_count;
    bool enabled;
    struct list_head list;
};

/* Consciousness Event */
struct consciousness_event {
    event_type_t type;
    u64 timestamp;
    u32 component_id;
    char description[128];
    u32 data[4];
    struct list_head list;
};

/* Advanced Log Entry */
struct log_entry {
    log_level_t level;
    log_category_t category;
    u64 timestamp;
    pid_t pid;
    char task_name[16];
    char message[256];
    struct list_head list;
};

/* System Metrics */
struct system_metrics {
    u64 total_events;
    u64 total_log_entries;
    u32 active_components;
    u32 failed_components;
    u32 current_consciousness_level;
    u64 uptime;
    u64 last_health_check;
};

/* Global State */
static struct {
    struct list_head components;
    struct list_head events;
    struct list_head log_entries;
    struct system_metrics metrics;
    struct task_struct *monitor_thread;
    bool monitoring_active;
    spinlock_t components_lock;
    spinlock_t events_lock;
    spinlock_t log_lock;
} consciousness_state;

/* Function Prototypes */
static int device_open(struct inode *inode, struct file *file);
static int device_release(struct inode *inode, struct file *file);
static ssize_t device_read(struct file *file, char __user *buffer, size_t len, loff_t *offset);
static ssize_t device_write(struct file *file, const char __user *buffer, size_t len, loff_t *offset);
static long device_ioctl(struct file *file, unsigned int cmd, unsigned long arg);

/* File Operations */
static struct file_operations fops = {
    .open = device_open,
    .read = device_read,
    .write = device_write,
    .release = device_release,
    .unlocked_ioctl = device_ioctl,
};

/* IOCTL Commands */
#define SYNOS_IOC_MAGIC 'S'
#define SYNOS_IOC_GET_STATUS        _IOR(SYNOS_IOC_MAGIC, 1, struct system_metrics)
#define SYNOS_IOC_REGISTER_COMPONENT _IOW(SYNOS_IOC_MAGIC, 2, struct consciousness_component)
#define SYNOS_IOC_UPDATE_HEALTH     _IOW(SYNOS_IOC_MAGIC, 3, struct consciousness_component)
#define SYNOS_IOC_LOG_EVENT         _IOW(SYNOS_IOC_MAGIC, 4, struct consciousness_event)
#define SYNOS_IOC_SET_LOG_LEVEL     _IOW(SYNOS_IOC_MAGIC, 5, int)

/* ==================== Core Functions ==================== */

static void consciousness_log(log_level_t level, log_category_t category, const char *format, ...) {
    struct log_entry *entry;
    va_list args;
    unsigned long flags;

    if (consciousness_state.metrics.total_log_entries >= MAX_LOG_ENTRIES) {
        /* Remove oldest entry to make room */
        struct log_entry *oldest = list_first_entry(&consciousness_state.log_entries,
                                                   struct log_entry, list);
        list_del(&oldest->list);
        kfree(oldest);
        consciousness_state.metrics.total_log_entries--;
    }

    entry = kmalloc(sizeof(struct log_entry), GFP_ATOMIC);
    if (!entry)
        return;

    entry->level = level;
    entry->category = category;
    entry->timestamp = ktime_get_real_ns();
    entry->pid = current->pid;
    strncpy(entry->task_name, current->comm, sizeof(entry->task_name) - 1);
    entry->task_name[sizeof(entry->task_name) - 1] = '\0';

    va_start(args, format);
    vsnprintf(entry->message, sizeof(entry->message), format, args);
    va_end(args);

    spin_lock_irqsave(&consciousness_state.log_lock, flags);
    list_add_tail(&entry->list, &consciousness_state.log_entries);
    consciousness_state.metrics.total_log_entries++;
    spin_unlock_irqrestore(&consciousness_state.log_lock, flags);

    /* Also print to kernel log for important messages */
    if (level >= LOG_WARNING) {
        printk(KERN_WARNING "SynOS: [%s] %s\n",
               current->comm, entry->message);
    }
}

static int consciousness_monitor_thread(void *data) {
    struct consciousness_component *component, *tmp;
    u64 current_time;
    unsigned long flags;

    consciousness_log(LOG_INFO, CAT_CONSCIOUSNESS, "Consciousness monitor thread started");

    while (!kthread_should_stop() && consciousness_state.monitoring_active) {
        current_time = ktime_get_real_ns();

        /* Health check for all components */
        spin_lock_irqsave(&consciousness_state.components_lock, flags);
        list_for_each_entry_safe(component, tmp, &consciousness_state.components, list) {
            if (component->enabled && component->state == COMPONENT_ACTIVE) {
                /* Check for component timeout (5 seconds) */
                if (current_time - component->last_heartbeat > 5000000000ULL) {
                    component->state = COMPONENT_DEGRADED;
                    component->health_score = max(0, (int)component->health_score - 20);
                    consciousness_log(LOG_WARNING, CAT_HEALTH,
                                    "Component %s degraded due to timeout", component->name);
                }

                /* Update overall system consciousness level */
                if (component->health_score < 50) {
                    consciousness_state.metrics.current_consciousness_level =
                        max(0, (int)consciousness_state.metrics.current_consciousness_level - 5);
                }
            }
        }
        spin_unlock_irqrestore(&consciousness_state.components_lock, flags);

        consciousness_state.metrics.last_health_check = current_time;
        consciousness_state.metrics.uptime = current_time;

        /* Sleep for 1 second */
        msleep(1000);
    }

    consciousness_log(LOG_INFO, CAT_CONSCIOUSNESS, "Consciousness monitor thread stopped");
    return 0;
}

/* ==================== File Operations ==================== */

static int device_open(struct inode *inode, struct file *file) {
    if (!mutex_trylock(&synos_mutex)) {
        consciousness_log(LOG_WARNING, CAT_KERNEL, "Device busy, open failed");
        return -EBUSY;
    }

    consciousness_log(LOG_INFO, CAT_KERNEL, "Device opened successfully");
    return 0;
}

static int device_release(struct inode *inode, struct file *file) {
    mutex_unlock(&synos_mutex);
    consciousness_log(LOG_INFO, CAT_KERNEL, "Device closed");
    return 0;
}

static ssize_t device_read(struct file *file, char __user *buffer, size_t len, loff_t *offset) {
    struct system_metrics metrics;
    size_t copy_len;

    if (*offset >= sizeof(metrics))
        return 0;

    metrics = consciousness_state.metrics;
    copy_len = min(len, sizeof(metrics) - (size_t)*offset);

    if (copy_to_user(buffer, ((char*)&metrics) + *offset, copy_len)) {
        consciousness_log(LOG_ERROR, CAT_KERNEL, "Failed to copy metrics to user");
        return -EFAULT;
    }

    *offset += copy_len;
    consciousness_log(LOG_DEBUG, CAT_KERNEL, "Read %zu bytes of metrics", copy_len);
    return copy_len;
}

static ssize_t device_write(struct file *file, const char __user *buffer, size_t len, loff_t *offset) {
    consciousness_log(LOG_INFO, CAT_KERNEL, "Write operation received (%zu bytes)", len);
    return len;
}

static long device_ioctl(struct file *file, unsigned int cmd, unsigned long arg) {
    struct consciousness_component component;
    struct consciousness_event event;
    struct system_metrics metrics;
    unsigned long flags;
    int retval = 0;

    switch (cmd) {
    case SYNOS_IOC_GET_STATUS:
        metrics = consciousness_state.metrics;
        if (copy_to_user((void __user *)arg, &metrics, sizeof(metrics))) {
            consciousness_log(LOG_ERROR, CAT_KERNEL, "IOCTL: Failed to copy status to user");
            retval = -EFAULT;
        } else {
            consciousness_log(LOG_DEBUG, CAT_KERNEL, "IOCTL: Status retrieved");
        }
        break;

    case SYNOS_IOC_REGISTER_COMPONENT:
        if (copy_from_user(&component, (void __user *)arg, sizeof(component))) {
            consciousness_log(LOG_ERROR, CAT_KERNEL, "IOCTL: Failed to copy component from user");
            retval = -EFAULT;
        } else {
            struct consciousness_component *new_comp =
                kmalloc(sizeof(struct consciousness_component), GFP_KERNEL);
            if (new_comp) {
                *new_comp = component;
                new_comp->last_heartbeat = ktime_get_real_ns();
                INIT_LIST_HEAD(&new_comp->list);

                spin_lock_irqsave(&consciousness_state.components_lock, flags);
                list_add_tail(&new_comp->list, &consciousness_state.components);
                consciousness_state.metrics.active_components++;
                spin_unlock_irqrestore(&consciousness_state.components_lock, flags);

                consciousness_log(LOG_INFO, CAT_COMPONENT,
                                "Component registered: %s", new_comp->name);
            } else {
                retval = -ENOMEM;
            }
        }
        break;

    default:
        consciousness_log(LOG_WARNING, CAT_KERNEL, "IOCTL: Unknown command: %u", cmd);
        retval = -ENOTTY;
    }

    return retval;
}

/* ==================== Module Init/Exit ==================== */

static int __init synos_consciousness_init(void) {
    consciousness_log(LOG_INFO, CAT_CONSCIOUSNESS, "SynOS Consciousness Module initializing...");

    /* Initialize data structures */
    INIT_LIST_HEAD(&consciousness_state.components);
    INIT_LIST_HEAD(&consciousness_state.events);
    INIT_LIST_HEAD(&consciousness_state.log_entries);
    spin_lock_init(&consciousness_state.components_lock);
    spin_lock_init(&consciousness_state.events_lock);
    spin_lock_init(&consciousness_state.log_lock);
    mutex_init(&synos_mutex);

    /* Initialize metrics */
    memset(&consciousness_state.metrics, 0, sizeof(consciousness_state.metrics));
    consciousness_state.metrics.current_consciousness_level = 100;
    consciousness_state.monitoring_active = true;

    /* Register character device */
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        consciousness_log(LOG_ERROR, CAT_KERNEL, "Failed to register device");
        return major_number;
    }

    /* Create device class */
    synos_class = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR(synos_class)) {
        unregister_chrdev(major_number, DEVICE_NAME);
        consciousness_log(LOG_ERROR, CAT_KERNEL, "Failed to create device class");
        return PTR_ERR(synos_class);
    }

    /* Create device */
    synos_device = device_create(synos_class, NULL, MKDEV(major_number, 0), NULL, DEVICE_NAME);
    if (IS_ERR(synos_device)) {
        class_destroy(synos_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        consciousness_log(LOG_ERROR, CAT_KERNEL, "Failed to create device");
        return PTR_ERR(synos_device);
    }

    /* Start monitoring thread */
    consciousness_state.monitor_thread = kthread_run(consciousness_monitor_thread,
                                                   NULL, "synos_monitor");
    if (IS_ERR(consciousness_state.monitor_thread)) {
        device_destroy(synos_class, MKDEV(major_number, 0));
        class_destroy(synos_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        consciousness_log(LOG_ERROR, CAT_KERNEL, "Failed to create monitor thread");
        return PTR_ERR(consciousness_state.monitor_thread);
    }

    consciousness_log(LOG_INFO, CAT_CONSCIOUSNESS,
                     "SynOS Consciousness Module loaded successfully (major: %d)", major_number);

    printk(KERN_INFO "SynOS: Consciousness monitoring active with advanced logging\n");
    return 0;
}

static void __exit synos_consciousness_exit(void) {
    struct consciousness_component *component, *comp_tmp;
    struct consciousness_event *event, *event_tmp;
    struct log_entry *log, *log_tmp;
    unsigned long flags;

    consciousness_log(LOG_INFO, CAT_CONSCIOUSNESS, "SynOS Consciousness Module unloading...");

    /* Stop monitoring */
    consciousness_state.monitoring_active = false;
    if (consciousness_state.monitor_thread) {
        kthread_stop(consciousness_state.monitor_thread);
    }

    /* Cleanup device */
    device_destroy(synos_class, MKDEV(major_number, 0));
    class_destroy(synos_class);
    unregister_chrdev(major_number, DEVICE_NAME);

    /* Free all allocated memory */
    spin_lock_irqsave(&consciousness_state.components_lock, flags);
    list_for_each_entry_safe(component, comp_tmp, &consciousness_state.components, list) {
        list_del(&component->list);
        kfree(component);
    }
    spin_unlock_irqrestore(&consciousness_state.components_lock, flags);

    spin_lock_irqsave(&consciousness_state.events_lock, flags);
    list_for_each_entry_safe(event, event_tmp, &consciousness_state.events, list) {
        list_del(&event->list);
        kfree(event);
    }
    spin_unlock_irqrestore(&consciousness_state.events_lock, flags);

    spin_lock_irqsave(&consciousness_state.log_lock, flags);
    list_for_each_entry_safe(log, log_tmp, &consciousness_state.log_entries, list) {
        list_del(&log->list);
        kfree(log);
    }
    spin_unlock_irqrestore(&consciousness_state.log_lock, flags);

    printk(KERN_INFO "SynOS: Consciousness Module unloaded\n");
}

module_init(synos_consciousness_init);
module_exit(synos_consciousness_exit);