
# SynBoot Makefile
CC = gcc
CFLAGS = -ffreestanding -fno-stack-protector -fpic -fshort-wchar -mno-red-zone
LDFLAGS = -nostdlib -znocombreloc -T gnu-efi.lds -shared -Bsymbolic
INCLUDES = -I/usr/include/efi -I/usr/include/efi/x86_64

OBJCOPY = objcopy
EFILIB = /usr/lib/gnuefi/crt0-efi-x86_64.o /usr/lib/gnuefi/libgnuefi.a

TARGET = synboot.efi
SOURCES = synboot_main.c consciousness_init.c kernel_loader.c

all: $(TARGET)

synboot.efi: synboot.so
	$(OBJCOPY) -j .text -j .sdata -j .data -j .dynamic \
		-j .dynsym -j .rel -j .rela -j .reloc \
		--target=efi-app-x86_64 $^ $@

synboot.so: $(SOURCES:.c=.o)
	$(CC) $(LDFLAGS) $^ $(EFILIB) -o $@

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f *.o *.so *.efi

install: $(TARGET)
	cp $(TARGET) /boot/efi/EFI/synos/

.PHONY: all clean install
