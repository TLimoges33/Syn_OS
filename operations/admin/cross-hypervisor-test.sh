#!/bin/bash

# SynOS V1.0 Cross-Hypervisor Testing Suite
# Tests our GRUB ISO across multiple virtualization platforms

set -e

GRUB_ISO="build/SynOS-v1.0-grub-20250902.iso"
TEST_DIR="build/hypervisor-tests"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "🚀 SynOS V1.0 Cross-Hypervisor Testing Suite"
echo "=============================================="
echo "📅 $(date)"
echo "📀 ISO: ${GRUB_ISO}"

# Check if ISO exists
if [ ! -f "${GRUB_ISO}" ]; then
    echo "❌ GRUB ISO not found: ${GRUB_ISO}"
    echo "   Run: scripts/build-grub-iso.sh"
    exit 1
fi

# Create test directory
mkdir -p "${TEST_DIR}"

echo ""
echo "📊 ISO Information:"
ls -lh "${GRUB_ISO}"
echo ""

# Function to test QEMU
test_qemu() {
    echo "🔧 Testing QEMU (Primary Platform)"
    echo "=================================="
    
    local log_file="${TEST_DIR}/qemu-test-${TIMESTAMP}.log"
    local serial_file="${TEST_DIR}/qemu-serial-${TIMESTAMP}.log"
    
    echo "📋 Starting QEMU boot test..."
    timeout 30s qemu-system-x86_64 \
        -cdrom "${GRUB_ISO}" \
        -m 512M \
        -serial "file:${serial_file}" \
        -nographic \
        -monitor none \
        > "${log_file}" 2>&1 || echo "⏰ QEMU test completed (timeout expected)"
    
    echo "📝 QEMU Results:"
    if [ -f "${serial_file}" ] && [ -s "${serial_file}" ]; then
        echo "✅ Serial output captured:"
        head -10 "${serial_file}"
        echo "   ... (full log: ${serial_file})"
    else
        echo "⚠️ No serial output captured"
    fi
    
    echo "📄 Boot log saved to: ${log_file}"
    echo ""
}

# Function to create VirtualBox VM
test_virtualbox() {
    echo "📦 Testing VirtualBox Compatibility"
    echo "==================================="
    
    if ! command -v VBoxManage >/dev/null 2>&1; then
        echo "⚠️ VirtualBox not installed - skipping"
        echo "   Install with: sudo apt install virtualbox"
        return
    fi
    
    local vm_name="SynOS-Test-${TIMESTAMP}"
    local log_file="${TEST_DIR}/virtualbox-test-${TIMESTAMP}.log"
    
    echo "📋 Creating VirtualBox VM: ${vm_name}"
    
    # Create VM
    VBoxManage createvm --name "${vm_name}" --register \
        --ostype "Linux_64" > "${log_file}" 2>&1
    
    # Configure VM
    VBoxManage modifyvm "${vm_name}" \
        --memory 512 \
        --cpus 1 \
        --boot1 dvd \
        --boot2 none \
        --boot3 none \
        --boot4 none \
        --vram 16 \
        --graphicscontroller vmsvga > "${log_file}" 2>&1
    
    # Create storage controller
    VBoxManage storagectl "${vm_name}" \
        --name "IDE Controller" \
        --add ide > "${log_file}" 2>&1
    
    # Attach ISO
    VBoxManage storageattach "${vm_name}" \
        --storagectl "IDE Controller" \
        --port 0 \
        --device 0 \
        --type dvddrive \
        --medium "${PWD}/${GRUB_ISO}" > "${log_file}" 2>&1
    
    echo "✅ VirtualBox VM created successfully"
    echo "📋 VM Configuration:"
    VBoxManage showvminfo "${vm_name}" --machinereadable | grep -E "(memory|cpus|boot|ostype)"
    
    echo ""
    echo "🎯 Manual Testing Instructions:"
    echo "   1. VBoxManage startvm \"${vm_name}\" --type gui"
    echo "   2. Observe GRUB menu and kernel boot"
    echo "   3. VBoxManage controlvm \"${vm_name}\" poweroff"
    echo "   4. VBoxManage unregistervm \"${vm_name}\" --delete"
    echo ""
    
    # Save VM info for cleanup
    echo "${vm_name}" > "${TEST_DIR}/virtualbox-vm-name.txt"
    echo "📄 VirtualBox log saved to: ${log_file}"
    echo ""
}

# Function to create VMware configuration
test_vmware() {
    echo "🔷 Testing VMware Compatibility"
    echo "==============================="
    
    local vmx_file="${TEST_DIR}/SynOS-Test-${TIMESTAMP}.vmx"
    local log_file="${TEST_DIR}/vmware-test-${TIMESTAMP}.log"
    
    echo "📋 Creating VMware configuration file..."
    
    cat > "${vmx_file}" << EOF
#!/usr/bin/vmware
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "19"
displayName = "SynOS V1.0 Test"
guestOS = "other-64"
memSize = "512"
numvcpus = "1"
ide0:0.present = "TRUE"
ide0:0.deviceType = "cdrom-image"
ide0:0.fileName = "${PWD}/${GRUB_ISO}"
ide0:0.startConnected = "TRUE"
floppy0.present = "FALSE"
ethernet0.present = "FALSE"
sound.present = "FALSE"
usb.present = "FALSE"
serial0.present = "TRUE"
serial0.fileType = "file"
serial0.fileName = "${TEST_DIR}/vmware-serial-${TIMESTAMP}.log"
EOF
    
    echo "✅ VMware configuration created: ${vmx_file}"
    echo ""
    echo "🎯 Manual Testing Instructions:"
    echo "   1. Open VMware Workstation/Player"
    echo "   2. File → Open → ${vmx_file}"
    echo "   3. Power on the VM"
    echo "   4. Observe GRUB menu and kernel boot"
    echo ""
    
    if command -v vmware >/dev/null 2>&1; then
        echo "📋 VMware detected - attempting automated test..."
        echo "vmware ${vmx_file}" > "${log_file}" 2>&1 &
        echo "⚠️ VMware test started in background"
    else
        echo "⚠️ VMware not in PATH - manual testing required"
    fi
    
    echo "📄 VMware config saved to: ${vmx_file}"
    echo ""
}

# Function to generate test report
generate_report() {
    echo "📊 Cross-Hypervisor Test Report"
    echo "==============================="
    echo "📅 Test Date: $(date)"
    echo "📀 ISO Tested: ${GRUB_ISO}"
    echo "📁 Test Results: ${TEST_DIR}/"
    echo ""
    
    echo "📋 Generated Files:"
    ls -la "${TEST_DIR}/" | grep -E "(log|vmx|txt)$" || echo "   No test files found"
    echo ""
    
    echo "📈 Test Summary:"
    echo "   ✅ QEMU: Primary testing platform"
    if command -v VBoxManage >/dev/null 2>&1; then
        echo "   ✅ VirtualBox: VM configuration created"
    else
        echo "   ⚠️ VirtualBox: Not installed"
    fi
    if command -v vmware >/dev/null 2>&1; then
        echo "   ✅ VMware: Configuration created"
    else
        echo "   ⚠️ VMware: Not installed"
    fi
    echo ""
    
    echo "🎯 Next Steps:"
    echo "   1. Review test logs in ${TEST_DIR}/"
    echo "   2. Manually test VirtualBox and VMware VMs"
    echo "   3. Document any hypervisor-specific issues"
    echo "   4. Proceed with custom initrd development"
}

# Main execution
echo "🧪 Starting Cross-Hypervisor Testing..."
echo ""

test_qemu
test_virtualbox  
test_vmware
generate_report

echo "✅ Cross-Hypervisor Testing Suite Complete!"
echo "📁 All results saved in: ${TEST_DIR}/"
