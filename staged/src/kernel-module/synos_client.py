#!/usr/bin/env python3
"""
SynOS Phase 4.2: Advanced Logging Client
Command-line interface for interacting with the SynOS consciousness monitoring system
"""

import os
import sys
import json
import socket
import argparse
import struct
import fcntl
from datetime import datetime

# Configuration
DEVICE_PATH = "/dev/synos"
PROC_PATH = "/proc/synos_consciousness"
SOCKET_PATH = "/var/run/synos_consciousness.sock"

# IOCTL definitions (matching kernel module)
SYNOS_IOC_MAGIC = ord('S')
SYNOS_GET_CONSCIOUSNESS_LEVEL = (0x40000000 | (8 << 16) | (SYNOS_IOC_MAGIC << 8) | 1)
SYNOS_RESET_METRICS = (0x00000000 | (0 << 16) | (SYNOS_IOC_MAGIC << 8) | 2)
SYNOS_GET_COMPONENT_COUNT = (0x40000000 | (8 << 16) | (SYNOS_IOC_MAGIC << 8) | 3)
SYNOS_SET_MONITORING_LEVEL = (0x80000000 | (4 << 16) | (SYNOS_IOC_MAGIC << 8) | 4)

class SynOSClient:
    def __init__(self):
        self.device_fd = None
        
    def check_module(self):
        """Check if kernel module is loaded"""
        try:
            with open("/proc/modules", "r") as f:
                modules = f.read()
                return "synos_consciousness" in modules
        except:
            return False
    
    def check_daemon(self):
        """Check if daemon is running"""
        return os.path.exists(SOCKET_PATH)
    
    def open_device(self):
        """Open device for direct communication"""
        try:
            self.device_fd = os.open(DEVICE_PATH, os.O_RDWR)
            return True
        except Exception as e:
            print(f"Error opening device: {e}")
            return False
    
    def close_device(self):
        """Close device"""
        if self.device_fd is not None:
            os.close(self.device_fd)
            self.device_fd = None
    
    def send_socket_command(self, command):
        """Send command via Unix socket to daemon"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(SOCKET_PATH)
            sock.send(command.encode())
            response = sock.recv(4096).decode()
            sock.close()
            return response
        except Exception as e:
            print(f"Error communicating with daemon: {e}")
            return None
    
    def send_device_command(self, command):
        """Send command directly to device"""
        if self.device_fd is None:
            if not self.open_device():
                return False
        
        try:
            os.write(self.device_fd, command.encode())
            return True
        except Exception as e:
            print(f"Error sending command to device: {e}")
            return False
    
    def read_device_status(self):
        """Read status from device"""
        if self.device_fd is None:
            if not self.open_device():
                return None
        
        try:
            os.lseek(self.device_fd, 0, os.SEEK_SET)
            data = os.read(self.device_fd, 4096)
            return data.decode()
        except Exception as e:
            print(f"Error reading device status: {e}")
            return None
    
    def read_proc_status(self):
        """Read status from proc interface"""
        try:
            with open(PROC_PATH, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading proc status: {e}")
            return None
    
    def get_consciousness_level(self):
        """Get consciousness level via IOCTL"""
        if self.device_fd is None:
            if not self.open_device():
                return None
        
        try:
            result = fcntl.ioctl(self.device_fd, SYNOS_GET_CONSCIOUSNESS_LEVEL, struct.pack('Q', 0))
            level = struct.unpack('Q', result)[0]
            return level
        except Exception as e:
            print(f"Error getting consciousness level: {e}")
            return None
    
    def get_component_count(self):
        """Get component count via IOCTL"""
        if self.device_fd is None:
            if not self.open_device():
                return None
        
        try:
            result = fcntl.ioctl(self.device_fd, SYNOS_GET_COMPONENT_COUNT, struct.pack('Q', 0))
            count = struct.unpack('Q', result)[0]
            return count
        except Exception as e:
            print(f"Error getting component count: {e}")
            return None
    
    def set_monitoring_level(self, level):
        """Set monitoring level via IOCTL"""
        if self.device_fd is None:
            if not self.open_device():
                return False
        
        try:
            fcntl.ioctl(self.device_fd, SYNOS_SET_MONITORING_LEVEL, level)
            return True
        except Exception as e:
            print(f"Error setting monitoring level: {e}")
            return False
    
    def reset_metrics(self):
        """Reset metrics via IOCTL"""
        if self.device_fd is None:
            if not self.open_device():
                return False
        
        try:
            fcntl.ioctl(self.device_fd, SYNOS_RESET_METRICS, 0)
            return True
        except Exception as e:
            print(f"Error resetting metrics: {e}")
            return False
    
    def status(self, detailed=False):
        """Show system status"""
        print("=== SynOS Phase 4.2: System Status ===")
        print()
        
        # Check module
        module_loaded = self.check_module()
        print(f"Kernel Module: {'✓ LOADED' if module_loaded else '✗ NOT LOADED'}")
        
        # Check daemon
        daemon_running = self.check_daemon()
        print(f"Daemon: {'✓ RUNNING' if daemon_running else '✗ NOT RUNNING'}")
        
        # Check interfaces
        device_available = os.path.exists(DEVICE_PATH)
        proc_available = os.path.exists(PROC_PATH)
        print(f"Device Interface: {'✓ AVAILABLE' if device_available else '✗ NOT AVAILABLE'} ({DEVICE_PATH})")
        print(f"Proc Interface: {'✓ AVAILABLE' if proc_available else '✗ NOT AVAILABLE'} ({PROC_PATH})")
        
        if not module_loaded:
            print("\nTo load the module:")
            print("  cd /path/to/kernel-module && sudo ./build.sh install")
            return
        
        print()
        
        # Get metrics via daemon if available
        if daemon_running:
            print("=== Daemon Status ===")
            response = self.send_socket_command("STATUS")
            if response:
                try:
                    data = json.loads(response)
                    print(f"Consciousness Level: {data['consciousness_level']}%")
                    print(f"Component Count: {data['component_count']}")
                    print(f"Last Update: {datetime.fromtimestamp(data['last_update'])}")
                except:
                    print("Failed to parse daemon response")
            print()
        
        # Get direct metrics
        print("=== Direct Kernel Metrics ===")
        consciousness_level = self.get_consciousness_level()
        component_count = self.get_component_count()
        
        if consciousness_level is not None:
            print(f"Consciousness Level: {consciousness_level}%")
        if component_count is not None:
            print(f"Component Count: {component_count}")
        
        # Show detailed status if requested
        if detailed:
            print("\n=== Device Status ===")
            device_status = self.read_device_status()
            if device_status:
                print(device_status)
            
            print("\n=== Proc Interface ===")
            proc_status = self.read_proc_status()
            if proc_status:
                print(proc_status)
        
        self.close_device()
    
    def register_component(self, name):
        """Register a consciousness component"""
        print(f"Registering component: {name}")
        
        # Try daemon first, then direct
        if self.check_daemon():
            response = self.send_socket_command(f"REGISTER:{name}")
            if response and response.strip() == "True":
                print("✓ Component registered via daemon")
                return True
            else:
                print("✗ Failed to register via daemon")
        
        # Try direct device communication
        if self.send_device_command(f"REGISTER:{name}"):
            print("✓ Component registered via device")
            return True
        else:
            print("✗ Failed to register via device")
            return False
    
    def log_message(self, message):
        """Send log message"""
        print(f"Logging message: {message}")
        
        # Try daemon first, then direct
        if self.check_daemon():
            response = self.send_socket_command(f"LOG:{message}")
            if response and response.strip() == "True":
                print("✓ Message logged via daemon")
                return True
            else:
                print("✗ Failed to log via daemon")
        
        # Try direct device communication
        if self.send_device_command(f"LOG:{message}"):
            print("✓ Message logged via device")
            return True
        else:
            print("✗ Failed to log via device")
            return False
    
    def send_event(self, event):
        """Send consciousness event"""
        print(f"Sending event: {event}")
        
        # Try daemon first, then direct
        if self.check_daemon():
            response = self.send_socket_command(f"EVENT:{event}")
            if response and response.strip() == "True":
                print("✓ Event sent via daemon")
                return True
            else:
                print("✗ Failed to send event via daemon")
        
        # Try direct device communication
        if self.send_device_command(f"EVENT:{event}"):
            print("✓ Event sent via device")
            return True
        else:
            print("✗ Failed to send event via device")
            return False
    
    def monitor(self, interval=5):
        """Monitor consciousness metrics"""
        print(f"Monitoring SynOS consciousness (Ctrl+C to exit)")
        print(f"Update interval: {interval} seconds")
        print()
        
        try:
            import time
            
            while True:
                # Clear screen (optional)
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"=== SynOS Live Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                print()
                
                # Get current metrics
                consciousness_level = self.get_consciousness_level()
                component_count = self.get_component_count()
                
                if consciousness_level is not None:
                    # Create simple progress bar
                    bar_length = 40
                    filled_length = int(bar_length * consciousness_level // 100)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    print(f"Consciousness: [{bar}] {consciousness_level}%")
                else:
                    print("Consciousness: ERROR")
                
                if component_count is not None:
                    print(f"Components: {component_count}")
                else:
                    print("Components: ERROR")
                
                # Get daemon status if available
                if self.check_daemon():
                    response = self.send_socket_command("STATUS")
                    if response:
                        try:
                            data = json.loads(response)
                            print(f"Last Update: {datetime.fromtimestamp(data['last_update'])}")
                        except:
                            pass
                
                print()
                print("Press Ctrl+C to exit...")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
        
        self.close_device()
    
    def test_system(self):
        """Run system tests"""
        print("=== SynOS Phase 4.2: System Test ===")
        print()
        
        # Check prerequisites
        if not self.check_module():
            print("✗ Kernel module not loaded")
            return False
        
        print("✓ Kernel module loaded")
        
        # Test device access
        if not self.open_device():
            print("✗ Cannot open device")
            return False
        
        print("✓ Device accessible")
        
        # Test IOCTL operations
        consciousness_level = self.get_consciousness_level()
        if consciousness_level is not None:
            print(f"✓ IOCTL read consciousness level: {consciousness_level}%")
        else:
            print("✗ Failed to read consciousness level")
        
        component_count = self.get_component_count()
        if component_count is not None:
            print(f"✓ IOCTL read component count: {component_count}")
        else:
            print("✗ Failed to read component count")
        
        # Test component registration
        test_component = f"test_client_{datetime.now().strftime('%H%M%S')}"
        if self.send_device_command(f"REGISTER:{test_component}"):
            print(f"✓ Component registration: {test_component}")
        else:
            print("✗ Component registration failed")
        
        # Test logging
        test_message = f"Test log message at {datetime.now()}"
        if self.send_device_command(f"LOG:{test_message}"):
            print("✓ Log message sent")
        else:
            print("✗ Log message failed")
        
        # Test events
        test_event = f"Test event at {datetime.now()}"
        if self.send_device_command(f"EVENT:{test_event}"):
            print("✓ Event sent")
        else:
            print("✗ Event failed")
        
        # Test daemon communication if available
        if self.check_daemon():
            response = self.send_socket_command("STATUS")
            if response:
                print("✓ Daemon communication")
            else:
                print("✗ Daemon communication failed")
        else:
            print("ℹ Daemon not running (optional)")
        
        print()
        print("=== Test Summary ===")
        print("✓ Basic functionality verified")
        print("ℹ Check proc interface: cat /proc/synos_consciousness")
        print("ℹ Monitor kernel messages: dmesg | grep -i synos")
        
        self.close_device()
        return True

def main():
    parser = argparse.ArgumentParser(description="SynOS Phase 4.2 Advanced Logging Client")
    parser.add_argument('--status', '-s', action='store_true', help='Show system status')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed status')
    parser.add_argument('--register', '-r', metavar='NAME', help='Register component')
    parser.add_argument('--log', '-l', metavar='MESSAGE', help='Send log message')
    parser.add_argument('--event', '-e', metavar='EVENT', help='Send event')
    parser.add_argument('--monitor', '-m', action='store_true', help='Monitor consciousness')
    parser.add_argument('--interval', '-i', type=int, default=5, help='Monitor interval (seconds)')
    parser.add_argument('--test', '-t', action='store_true', help='Run system tests')
    parser.add_argument('--consciousness', '-c', action='store_true', help='Get consciousness level')
    parser.add_argument('--components', action='store_true', help='Get component count')
    parser.add_argument('--reset', action='store_true', help='Reset metrics')
    parser.add_argument('--monitoring-level', type=int, metavar='LEVEL', help='Set monitoring level (0-3)')
    
    args = parser.parse_args()
    
    client = SynOSClient()
    
    if args.status:
        client.status(args.detailed)
    elif args.register:
        client.register_component(args.register)
    elif args.log:
        client.log_message(args.log)
    elif args.event:
        client.send_event(args.event)
    elif args.monitor:
        client.monitor(args.interval)
    elif args.test:
        client.test_system()
    elif args.consciousness:
        level = client.get_consciousness_level()
        if level is not None:
            print(f"Consciousness Level: {level}%")
        else:
            print("Failed to get consciousness level")
    elif args.components:
        count = client.get_component_count()
        if count is not None:
            print(f"Component Count: {count}")
        else:
            print("Failed to get component count")
    elif args.reset:
        if client.reset_metrics():
            print("✓ Metrics reset")
        else:
            print("✗ Failed to reset metrics")
    elif args.monitoring_level is not None:
        if client.set_monitoring_level(args.monitoring_level):
            print(f"✓ Monitoring level set to {args.monitoring_level}")
        else:
            print("✗ Failed to set monitoring level")
    else:
        # Default action - show status
        client.status()

if __name__ == "__main__":
    main()
