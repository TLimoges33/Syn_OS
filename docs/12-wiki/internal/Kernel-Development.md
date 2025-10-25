# 🔧 Kernel Development Guide

**Complexity**: Advanced  
**Audience**: System Developers, Kernel Hackers  
**Prerequisites**: C, assembly, OS concepts, Linux internals

Learn to develop custom kernel modules, device drivers, and extend the SynOS kernel.

---

## 📋 Table of Contents

1. [Kernel Architecture](#kernel-architecture)
2. [Development Environment](#development-environment)
3. [Hello World Module](#hello-world-module)
4. [Character Device Drivers](#character-device-drivers)
5. [Interrupt Handlers](#interrupt-handlers)
6. [Memory Management](#memory-management)
7. [Synchronization](#synchronization)
8. [Debugging Techniques](#debugging-techniques)

---

## 1. Kernel Architecture

### SynOS Kernel Overview

```
SynOS Kernel (src/kernel/)
├── arch/           # Architecture-specific code
│   └── x86_64/    # x86-64 implementation
├── drivers/        # Device drivers
├── fs/            # File systems
├── kernel/        # Core kernel code
├── mm/            # Memory management
├── net/           # Network stack
└── security/      # Security modules
```

### Kernel vs Userspace

| Feature       | Kernel Space                   | User Space             |
| ------------- | ------------------------------ | ---------------------- |
| **Privilege** | Ring 0                         | Ring 3                 |
| **Memory**    | Direct hardware access         | Virtual memory         |
| **Errors**    | System crash (panic)           | Process crash          |
| **Libraries** | No libc, custom implementation | Full libc              |
| **Debugging** | Harder (printk, kgdb)          | Easier (gdb, valgrind) |

---

## 2. Development Environment

### Setup

```bash
# Install kernel headers
synpkg install linux-headers-$(uname -r)

# Install build tools
synpkg install build-essential gcc make

# Clone kernel source
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS/src/kernel

# Configure kernel
make menuconfig

# Build kernel
make -j$(nproc)

# Install
sudo make modules_install
sudo make install
```

### Development Tools

```bash
# Kernel configuration
make menuconfig          # ncurses interface
make xconfig            # Qt interface
make gconfig            # GTK interface

# Build targets
make                    # Build kernel
make modules           # Build modules only
make clean             # Clean build artifacts
make mrproper          # Deep clean (removes config)

# Static analysis
make C=1               # Sparse static analyzer
make W=1               # Extra warnings

# Documentation
make htmldocs          # Generate HTML docs
make pdfdocs           # Generate PDF docs
```

---

## 3. Hello World Module

### Basic Module Structure

```c
// hello.c - Simple kernel module
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

// Module metadata
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple Hello World module");
MODULE_VERSION("1.0");

// Module initialization function
static int __init hello_init(void) {
    printk(KERN_INFO "Hello, World! Module loaded.\n");
    return 0;  // 0 = success
}

// Module cleanup function
static void __exit hello_exit(void) {
    printk(KERN_INFO "Goodbye, World! Module unloaded.\n");
}

// Register init and exit functions
module_init(hello_init);
module_exit(hello_exit);
```

### Makefile

```makefile
# Makefile for kernel module
obj-m += hello.o

# Kernel build directory
KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
```

### Build and Load

```bash
# Build module
make

# Load module
sudo insmod hello.ko

# Check kernel log
dmesg | tail

# List loaded modules
lsmod | grep hello

# Module info
modinfo hello.ko

# Unload module
sudo rmmod hello

# Load with automatic dependencies
sudo modprobe hello
```

---

## 4. Character Device Drivers

### Device Driver Structure

```c
// chardev.c - Character device driver
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "mychardev"
#define CLASS_NAME "mychar"

static int major_number;
static struct class *chardev_class = NULL;
static struct device *chardev_device = NULL;
static char message[256] = {0};
static short message_size = 0;

// File operations prototypes
static int dev_open(struct inode *, struct file *);
static int dev_release(struct inode *, struct file *);
static ssize_t dev_read(struct file *, char __user *, size_t, loff_t *);
static ssize_t dev_write(struct file *, const char __user *, size_t, loff_t *);

// File operations structure
static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = dev_open,
    .read = dev_read,
    .write = dev_write,
    .release = dev_release,
};

// Module initialization
static int __init chardev_init(void) {
    printk(KERN_INFO "CharDev: Initializing\n");

    // Allocate major number
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        printk(KERN_ALERT "CharDev: Failed to register major number\n");
        return major_number;
    }
    printk(KERN_INFO "CharDev: Registered with major number %d\n", major_number);

    // Register device class
    chardev_class = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR(chardev_class)) {
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "CharDev: Failed to register device class\n");
        return PTR_ERR(chardev_class);
    }

    // Create device
    chardev_device = device_create(chardev_class, NULL,
                                    MKDEV(major_number, 0), NULL, DEVICE_NAME);
    if (IS_ERR(chardev_device)) {
        class_destroy(chardev_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "CharDev: Failed to create device\n");
        return PTR_ERR(chardev_device);
    }

    printk(KERN_INFO "CharDev: Device created successfully\n");
    return 0;
}

// Module cleanup
static void __exit chardev_exit(void) {
    device_destroy(chardev_class, MKDEV(major_number, 0));
    class_unregister(chardev_class);
    class_destroy(chardev_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    printk(KERN_INFO "CharDev: Goodbye!\n");
}

// Open device
static int dev_open(struct inode *inodep, struct file *filep) {
    printk(KERN_INFO "CharDev: Device opened\n");
    return 0;
}

// Read from device
static ssize_t dev_read(struct file *filep, char __user *buffer,
                        size_t len, loff_t *offset) {
    int error_count = 0;

    if (*offset >= message_size)
        return 0;

    if (*offset + len > message_size)
        len = message_size - *offset;

    // Copy to user space
    error_count = copy_to_user(buffer, message + *offset, len);

    if (error_count == 0) {
        printk(KERN_INFO "CharDev: Sent %zu bytes to user\n", len);
        *offset += len;
        return len;
    } else {
        printk(KERN_INFO "CharDev: Failed to send %d bytes\n", error_count);
        return -EFAULT;
    }
}

// Write to device
static ssize_t dev_write(struct file *filep, const char __user *buffer,
                         size_t len, loff_t *offset) {
    if (len > sizeof(message) - 1)
        len = sizeof(message) - 1;

    // Copy from user space
    if (copy_from_user(message, buffer, len)) {
        return -EFAULT;
    }

    message_size = len;
    message[len] = '\0';
    printk(KERN_INFO "CharDev: Received %zu bytes from user\n", len);
    return len;
}

// Release device
static int dev_release(struct inode *inodep, struct file *filep) {
    printk(KERN_INFO "CharDev: Device closed\n");
    return 0;
}

module_init(chardev_init);
module_exit(chardev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple character device driver");
MODULE_VERSION("1.0");
```

### Testing the Driver

```bash
# Build and load
make
sudo insmod chardev.ko

# Check device was created
ls -l /dev/mychardev

# Write to device
echo "Hello from userspace" | sudo tee /dev/mychardev

# Read from device
sudo cat /dev/mychardev

# Unload
sudo rmmod chardev
```

---

## 5. Interrupt Handlers

### Registering an Interrupt Handler

```c
// interrupt_handler.c
#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/kernel.h>

#define IRQ_NUMBER 1  // Keyboard interrupt

static int irq_counter = 0;

// Interrupt handler function
static irqreturn_t my_interrupt_handler(int irq, void *dev_id) {
    irq_counter++;
    printk(KERN_INFO "Interrupt! Counter: %d\n", irq_counter);

    // IRQ_HANDLED: interrupt was handled
    // IRQ_NONE: not our interrupt
    return IRQ_HANDLED;
}

static int __init interrupt_init(void) {
    int result;

    // Request interrupt line
    result = request_irq(IRQ_NUMBER,                 // IRQ number
                        my_interrupt_handler,        // Handler function
                        IRQF_SHARED,                 // Flags
                        "my_interrupt",              // Name
                        (void *)(my_interrupt_handler)); // dev_id

    if (result) {
        printk(KERN_ERR "Failed to request IRQ %d\n", IRQ_NUMBER);
        return result;
    }

    printk(KERN_INFO "Successfully requested IRQ %d\n", IRQ_NUMBER);
    return 0;
}

static void __exit interrupt_exit(void) {
    // Free interrupt line
    free_irq(IRQ_NUMBER, (void *)(my_interrupt_handler));
    printk(KERN_INFO "Freed IRQ %d. Total interrupts: %d\n",
           IRQ_NUMBER, irq_counter);
}

module_init(interrupt_init);
module_exit(interrupt_exit);

MODULE_LICENSE("GPL");
```

### Tasklets (Deferred Work)

```c
// Tasklet for bottom-half processing
#include <linux/interrupt.h>

static void my_tasklet_function(unsigned long data) {
    printk(KERN_INFO "Tasklet executed with data: %lu\n", data);
    // Perform time-consuming work here
}

DECLARE_TASKLET(my_tasklet, my_tasklet_function, 0);

// In interrupt handler (top-half)
static irqreturn_t my_irq_handler(int irq, void *dev_id) {
    // Minimal work in interrupt context
    printk(KERN_INFO "IRQ received, scheduling tasklet\n");

    // Schedule tasklet for later execution
    tasklet_schedule(&my_tasklet);

    return IRQ_HANDLED;
}
```

---

## 6. Memory Management

### Kernel Memory Allocation

```c
#include <linux/slab.h>
#include <linux/vmalloc.h>

// kmalloc - physically contiguous memory
void *ptr = kmalloc(1024, GFP_KERNEL);
if (!ptr) {
    printk(KERN_ERR "kmalloc failed\n");
    return -ENOMEM;
}
kfree(ptr);

// vmalloc - virtually contiguous memory
void *vptr = vmalloc(1024 * 1024);  // 1 MB
if (!vptr) {
    printk(KERN_ERR "vmalloc failed\n");
    return -ENOMEM;
}
vfree(vptr);

// GFP flags
// GFP_KERNEL: Normal allocation, may sleep
// GFP_ATOMIC: Cannot sleep (interrupt context)
// GFP_DMA: DMA-capable memory
```

### Memory Cache (Slab Allocator)

```c
#include <linux/slab.h>

static struct kmem_cache *my_cache;

// Create cache
my_cache = kmem_cache_create("my_cache",           // Name
                             sizeof(struct my_obj), // Size
                             0,                     // Align
                             SLAB_HWCACHE_ALIGN,    // Flags
                             NULL);                 // Constructor

// Allocate from cache
struct my_obj *obj = kmem_cache_alloc(my_cache, GFP_KERNEL);

// Free to cache
kmem_cache_free(my_cache, obj);

// Destroy cache
kmem_cache_destroy(my_cache);
```

### Page Allocation

```c
#include <linux/gfp.h>

// Allocate single page
struct page *page = alloc_page(GFP_KERNEL);
void *addr = page_address(page);

// Allocate multiple pages (2^order pages)
struct page *pages = alloc_pages(GFP_KERNEL, 2);  // 4 pages

// Free pages
__free_page(page);
__free_pages(pages, 2);
```

---

## 7. Synchronization

### Spinlocks

```c
#include <linux/spinlock.h>

static DEFINE_SPINLOCK(my_lock);

void critical_section(void) {
    unsigned long flags;

    // Acquire lock (disables interrupts on local CPU)
    spin_lock_irqsave(&my_lock, flags);

    // Critical section
    // ... protected code ...

    // Release lock
    spin_unlock_irqrestore(&my_lock, flags);
}
```

### Mutexes

```c
#include <linux/mutex.h>

static DEFINE_MUTEX(my_mutex);

void may_sleep_function(void) {
    // Acquire mutex (may sleep)
    mutex_lock(&my_mutex);

    // Critical section
    // ... protected code (can sleep) ...

    // Release mutex
    mutex_unlock(&my_mutex);
}
```

### Semaphores

```c
#include <linux/semaphore.h>

static DEFINE_SEMAPHORE(my_sem);

void limited_access(void) {
    // Acquire semaphore
    if (down_interruptible(&my_sem)) {
        return -ERESTARTSYS;
    }

    // Protected section
    // ...

    // Release semaphore
    up(&my_sem);
}
```

### Read-Write Locks

```c
#include <linux/rwlock.h>

static DEFINE_RWLOCK(my_rwlock);

void read_data(void) {
    read_lock(&my_rwlock);
    // Read data (multiple readers allowed)
    read_unlock(&my_rwlock);
}

void write_data(void) {
    write_lock(&my_rwlock);
    // Write data (exclusive access)
    write_unlock(&my_rwlock);
}
```

---

## 8. Debugging Techniques

### printk Debugging

```c
// Log levels
printk(KERN_EMERG   "Emergency\n");   // System unusable
printk(KERN_ALERT   "Alert\n");       // Action required
printk(KERN_CRIT    "Critical\n");    // Critical condition
printk(KERN_ERR     "Error\n");       // Error condition
printk(KERN_WARNING "Warning\n");     // Warning
printk(KERN_NOTICE  "Notice\n");      // Normal but significant
printk(KERN_INFO    "Info\n");        // Informational
printk(KERN_DEBUG   "Debug\n");       // Debug messages

// View messages
dmesg | tail
tail -f /var/log/kern.log

// Set log level
echo 8 > /proc/sys/kernel/printk  // Show all messages
```

### KGDB (Kernel Debugger)

```bash
# Enable KGDB in kernel config
CONFIG_KGDB=y
CONFIG_KGDB_SERIAL_CONSOLE=y

# Boot with kgdb
qemu-system-x86_64 \
    -kernel bzImage \
    -append "kgdboc=ttyS0,115200 kgdbwait" \
    -serial tcp::1234,server

# Connect GDB
gdb vmlinux
(gdb) target remote :1234
(gdb) break sys_open
(gdb) continue
```

### Dynamic Debug

```bash
# Enable dynamic debug for module
echo "module mymodule +p" > /sys/kernel/debug/dynamic_debug/control

# Enable for specific file
echo "file mydriver.c +p" > /sys/kernel/debug/dynamic_debug/control

# Enable for specific function
echo "func my_function +p" > /sys/kernel/debug/dynamic_debug/control
```

### Kernel Oops Analysis

```c
// Trigger oops (for testing)
static int cause_oops(void) {
    int *ptr = NULL;
    *ptr = 42;  // NULL pointer dereference
    return 0;
}

// Analyze oops
// 1. Check dmesg for oops
// 2. Note instruction pointer (RIP)
// 3. Use addr2line to find source line
addr2line -e vmlinux <RIP_address>

// 4. Or use gdb
gdb vmlinux
(gdb) list *0xffffffffa0001234
```

---

## 🧪 Practice Projects

### Project 1: Simple Character Device

**Goal**: Create `/dev/mycounter` that increments on each read  
**Skills**: Device files, file operations

### Project 2: Keyboard Logger Module

**Goal**: Log all keyboard input (ethical use only!)  
**Skills**: Interrupt handling, keyboard subsystem

### Project 3: Custom File System

**Goal**: Implement simple in-memory file system  
**Skills**: VFS, inodes, dentries

### Project 4: Network Packet Filter

**Goal**: Kernel module to filter network packets  
**Skills**: Netfilter hooks, packet processing

---

## 📚 Resources

**Documentation**:

-   Linux Kernel Documentation: `/usr/src/linux/Documentation/`
-   Kernel API: https://www.kernel.org/doc/html/latest/

**Books**:

-   "Linux Device Drivers" by Jonathan Corbet
-   "Linux Kernel Development" by Robert Love
-   "Understanding the Linux Kernel" by Daniel Bovet

**Online**:

-   https://kernelnewbies.org/
-   https://lwn.net/ (Linux Weekly News)
-   https://www.kernel.org/

**Tools**:

-   `ctags`, `cscope`: Code navigation
-   `sparse`: Static analyzer
-   `coccinelle`: Semantic patches
-   `perf`: Performance analysis

---

**Last Updated**: October 4, 2025  
**Difficulty**: Advanced  
**Prerequisites**: Strong C, OS concepts, patience  
**Estimated Learning Time**: 3-6 months

---

**⚠️ Warning**: Kernel bugs can crash your system. Always test in VMs!
