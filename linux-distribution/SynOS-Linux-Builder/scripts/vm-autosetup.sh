#!/bin/bash

# SynOS VM Auto-Setup Script
# Automatically downloads and sets up Kali Linux and BlackArch VMs on first boot

SCRIPT_DIR="/opt/synos"
VM_DIR="/home/user/VMs"
KALI_ISO_URL="https://cdimage.kali.org/kali-2023.3/kali-linux-2023.3-installer-amd64.iso"
BLACKARCH_ISO_URL="https://iso.blackarch.org/blackarch-linux-full-2023.04.01-x86_64.iso"

setup_vm_environment() {
    echo "[SynOS] Setting up VM environment..."

    # Create VM directories
    mkdir -p "$VM_DIR"/{kali,blackarch}

    # Setup libvirt
    systemctl enable libvirtd
    systemctl start libvirtd

    # Add user to libvirt group
    usermod -a -G libvirt user
    usermod -a -G kvm user

    # Setup default network
    virsh net-autostart default
    virsh net-start default
}

download_vm_images() {
    echo "[SynOS] Downloading VM images..."

    # Download Kali Linux ISO
    if [ ! -f "$VM_DIR/kali/kali-linux.iso" ]; then
        echo "Downloading Kali Linux ISO..."
        wget -O "$VM_DIR/kali/kali-linux.iso" "$KALI_ISO_URL" &
        KALI_PID=$!
    fi

    # Download BlackArch ISO
    if [ ! -f "$VM_DIR/blackarch/blackarch-linux.iso" ]; then
        echo "Downloading BlackArch ISO..."
        wget -O "$VM_DIR/blackarch/blackarch-linux.iso" "$BLACKARCH_ISO_URL" &
        BLACKARCH_PID=$!
    fi

    # Wait for downloads
    if [ ! -z "$KALI_PID" ]; then
        wait $KALI_PID
        echo "Kali Linux ISO downloaded"
    fi

    if [ ! -z "$BLACKARCH_PID" ]; then
        wait $BLACKARCH_PID
        echo "BlackArch ISO downloaded"
    fi
}

create_vm_configs() {
    echo "[SynOS] Creating VM configurations..."

    # Create Kali Linux VM
    virt-install \
        --name kali-linux \
        --memory 4096 \
        --vcpus 2 \
        --disk path="$VM_DIR/kali/kali-linux.qcow2",size=50 \
        --cdrom "$VM_DIR/kali/kali-linux.iso" \
        --os-variant linux2020 \
        --network bridge=virbr0 \
        --graphics spice \
        --noautoconsole \
        --autostart &

    # Create BlackArch VM
    virt-install \
        --name blackarch-linux \
        --memory 4096 \
        --vcpus 2 \
        --disk path="$VM_DIR/blackarch/blackarch-linux.qcow2",size=50 \
        --cdrom "$VM_DIR/blackarch/blackarch-linux.iso" \
        --os-variant linux2020 \
        --network bridge=virbr0 \
        --graphics spice \
        --noautoconsole \
        --autostart &

    wait
}

create_desktop_shortcuts() {
    echo "[SynOS] Creating desktop shortcuts..."

    # Kali Linux shortcut
    cat > /home/user/Desktop/Kali-Linux-VM.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Kali Linux VM
Comment=Launch Kali Linux Virtual Machine
Exec=virt-manager --connect qemu:///system --show-domain-console kali-linux
Icon=security-high
Terminal=false
Categories=Security;System;
EOF

    # BlackArch shortcut
    cat > /home/user/Desktop/BlackArch-VM.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BlackArch VM
Comment=Launch BlackArch Virtual Machine
Exec=virt-manager --connect qemu:///system --show-domain-console blackarch-linux
Icon=security-high
Terminal=false
Categories=Security;System;
EOF

    chmod +x /home/user/Desktop/*.desktop
    chown user:user /home/user/Desktop/*.desktop
}

install_additional_tools() {
    echo "[SynOS] Installing additional security tools..."

    # Install tools not available in Debian repos
    cd /tmp

    # Install Burp Suite Community
    wget "https://portswigger.net/burp/releases/download?product=community&version=2023.10.3.7&type=Linux" -O burpsuite.sh
    chmod +x burpsuite.sh
    ./burpsuite.sh -q -dir /opt/burpsuite

    # Install OWASP ZAP
    wget "https://github.com/zaproxy/zaproxy/releases/download/v2.14.0/ZAP_2_14_0_unix.sh" -O zap.sh
    chmod +x zap.sh
    ./zap.sh -q -dir /opt/zaproxy

    # Install Ghidra
    wget "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.4_build/ghidra_10.4_PUBLIC_20230928.zip" -O ghidra.zip
    unzip ghidra.zip -d /opt/
    mv /opt/ghidra_* /opt/ghidra

    # Install Metasploit Framework
    curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
    chmod 755 msfinstall
    ./msfinstall

    # Cleanup
    rm -f /tmp/*.sh /tmp/*.zip msfinstall
}

setup_networking() {
    echo "[SynOS] Setting up advanced networking..."

    # Enable IP forwarding
    echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf

    # Create bridge for VM networking
    cat > /etc/systemd/network/br0.netdev << EOF
[NetDev]
Name=br0
Kind=bridge
EOF

    cat > /etc/systemd/network/br0.network << EOF
[Match]
Name=br0

[Network]
DHCP=yes
IPForward=yes
EOF
}

main() {
    echo "[SynOS] Starting VM auto-setup..."

    setup_vm_environment
    download_vm_images
    create_vm_configs
    create_desktop_shortcuts
    install_additional_tools
    setup_networking

    echo "[SynOS] VM auto-setup completed!"
    echo "Kali Linux and BlackArch VMs are ready to use."
    echo "Access them via Applications > System Tools > Virtual Machine Manager"

    # Create notification
    sudo -u user DISPLAY=:0 notify-send "SynOS Setup Complete" "Kali Linux and BlackArch VMs are ready!" --icon=security-high
}

# Run main function
main "$@"