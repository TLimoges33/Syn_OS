# Makefile for SynapticOS Kernel Modules

obj-m += synapticos_microprocess.o

KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean

install:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules_install
	depmod -a

load:
	insmod synapticos_microprocess.ko

unload:
	rmmod synapticos_microprocess

test:
	@echo "Testing SynapticOS microprocess module..."
	@cat /proc/synapticos_stats
	@echo "AI_REQ:test request" > /dev/synapticos
	@cat /proc/synapticos_stats

.PHONY: all clean install load unload test