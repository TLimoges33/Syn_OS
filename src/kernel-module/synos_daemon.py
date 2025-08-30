#!/usr/bin/env python3
"""
SynOS Phase 4.2: Consciousness Monitoring Userspace Daemon
Advanced Logging and Debugging Infrastructure - Userspace Component

This daemon provides the userspace component for the SynOS consciousness
monitoring system, interfacing with the kernel module to provide advanced
logging, debugging, and consciousness state management.
"""

import os
import sys
import time
import json
import signal
import socket
import threading
import logging
import argparse
from datetime import datetime
from pathlib import Path
import fcntl
import struct
import select

# Configuration
DEVICE_PATH = "/dev/synos"
PROC_PATH = "/proc/synos_consciousness"
CONFIG_FILE = "/etc/synos/consciousness.conf"
LOG_FILE = "/var/log/synos_consciousness.log"
PID_FILE = "/var/run/synos_consciousness.pid"
SOCKET_PATH = "/var/run/synos_consciousness.sock"

# IOCTL definitions (matching kernel module)
SYNOS_IOC_MAGIC = ord('S')
SYNOS_GET_CONSCIOUSNESS_LEVEL = (0x40000000 | (8 << 16) | (SYNOS_IOC_MAGIC << 8) | 1)
SYNOS_RESET_METRICS = (0x00000000 | (0 << 16) | (SYNOS_IOC_MAGIC << 8) | 2)
SYNOS_GET_COMPONENT_COUNT = (0x40000000 | (8 << 16) | (SYNOS_IOC_MAGIC << 8) | 3)
SYNOS_SET_MONITORING_LEVEL = (0x80000000 | (4 << 16) | (SYNOS_IOC_MAGIC << 8) | 4)

# Log levels (matching kernel module)
LOG_LEVELS = {
    0: "EMERGENCY",
    1: "ALERT", 
    2: "CRITICAL",
    3: "ERROR",
    4: "WARNING",
    5: "NOTICE",
    6: "INFO",
    7: "DEBUG",
    8: "TRACE"
}

# Log categories (matching kernel module)
LOG_CATEGORIES = {
    0: "KERNEL",
    1: "MEMORY",
    2: "SECURITY", 
    3: "AI",
    4: "CONSCIOUSNESS",
    5: "PERFORMANCE",
    6: "DEBUG",
    7: "SYSTEM",
    8: "NETWORK",
    9: "STORAGE",
    10: "USER"
}

class SynOSConsciousnessDaemon:
    def __init__(self, config_file=None):
        self.running = False
        self.device_fd = None
        self.socket_server = None
        self.threads = []
        self.consciousness_level = 0
        self.component_count = 0
        self.last_update = 0
        
        # Configuration
        self.config = {
            'monitoring_interval': 5.0,
            'log_level': 'INFO',
            'auto_register_components': True,
            'consciousness_threshold': 50,
            'alert_on_degradation': True,
            'save_metrics': True,
            'metrics_file': '/var/log/synos_metrics.json'
        }
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        # Setup logging
        self.setup_logging()
        
        # Signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('SynOSConsciousness')
        
    def load_config(self, config_file):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                self.config.update(config_data)
            self.logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            self.logger.warning(f"Failed to load config: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        
    def check_kernel_module(self):
        """Check if the kernel module is loaded"""
        try:
            with open("/proc/modules", "r") as f:
                modules = f.read()
                if "synos_consciousness" not in modules:
                    self.logger.error("SynOS consciousness kernel module not loaded")
                    return False
            
            # Check device file
            if not os.path.exists(DEVICE_PATH):
                self.logger.error(f"Device file {DEVICE_PATH} not found")
                return False
                
            # Check proc interface
            if not os.path.exists(PROC_PATH):
                self.logger.error(f"Proc interface {PROC_PATH} not found")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking kernel module: {e}")
            return False
    
    def open_device(self):
        """Open the kernel module device"""
        try:
            self.device_fd = os.open(DEVICE_PATH, os.O_RDWR)
            self.logger.info("Successfully opened SynOS device")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open device {DEVICE_PATH}: {e}")
            return False
    
    def close_device(self):
        """Close the kernel module device"""
        if self.device_fd is not None:
            try:
                os.close(self.device_fd)
                self.device_fd = None
                self.logger.info("Device closed")
            except Exception as e:
                self.logger.error(f"Error closing device: {e}")
    
    def send_command(self, command):
        """Send command to kernel module"""
        if self.device_fd is None:
            return False
            
        try:
            os.write(self.device_fd, command.encode())
            return True
        except Exception as e:
            self.logger.error(f"Failed to send command '{command}': {e}")
            return False
    
    def read_device_status(self):
        """Read status from kernel module"""
        if self.device_fd is None:
            return None
            
        try:
            # Reset file position
            os.lseek(self.device_fd, 0, os.SEEK_SET)
            data = os.read(self.device_fd, 4096)
            return data.decode()
        except Exception as e:
            self.logger.error(f"Failed to read device status: {e}")
            return None
    
    def read_proc_status(self):
        """Read status from proc interface"""
        try:
            with open(PROC_PATH, 'r') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read proc status: {e}")
            return None
    
    def get_consciousness_level(self):
        """Get consciousness level via IOCTL"""
        if self.device_fd is None:
            return None
            
        try:
            result = fcntl.ioctl(self.device_fd, SYNOS_GET_CONSCIOUSNESS_LEVEL, struct.pack('Q', 0))
            level = struct.unpack('Q', result)[0]
            return level
        except Exception as e:
            self.logger.error(f"Failed to get consciousness level: {e}")
            return None
    
    def get_component_count(self):
        """Get component count via IOCTL"""
        if self.device_fd is None:
            return None
            
        try:
            result = fcntl.ioctl(self.device_fd, SYNOS_GET_COMPONENT_COUNT, struct.pack('Q', 0))
            count = struct.unpack('Q', result)[0]
            return count
        except Exception as e:
            self.logger.error(f"Failed to get component count: {e}")
            return None
    
    def set_monitoring_level(self, level):
        """Set monitoring level via IOCTL"""
        if self.device_fd is None:
            return False
            
        try:
            fcntl.ioctl(self.device_fd, SYNOS_SET_MONITORING_LEVEL, level)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set monitoring level: {e}")
            return False
    
    def register_component(self, name):
        """Register a consciousness component"""
        command = f"REGISTER:{name}"
        if self.send_command(command):
            self.logger.info(f"Registered component: {name}")
            return True
        return False
    
    def log_message(self, message):
        """Send log message to kernel module"""
        command = f"LOG:{message}"
        if self.send_command(command):
            self.logger.debug(f"Logged message: {message}")
            return True
        return False
    
    def send_event(self, event):
        """Send event to kernel module"""
        command = f"EVENT:{event}"
        if self.send_command(command):
            self.logger.debug(f"Sent event: {event}")
            return True
        return False
    
    def monitoring_thread(self):
        """Main monitoring thread"""
        self.logger.info("Consciousness monitoring thread started")
        
        while self.running:
            try:
                # Update consciousness metrics
                self.consciousness_level = self.get_consciousness_level() or 0
                self.component_count = self.get_component_count() or 0
                self.last_update = time.time()
                
                # Check for alerts
                if self.config['alert_on_degradation'] and self.consciousness_level < self.config['consciousness_threshold']:
                    self.logger.warning(f"Consciousness level below threshold: {self.consciousness_level}%")
                
                # Save metrics if enabled
                if self.config['save_metrics']:
                    self.save_metrics()
                
                # Log periodic status
                self.logger.info(f"Consciousness: {self.consciousness_level}%, Components: {self.component_count}")
                
                time.sleep(self.config['monitoring_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring thread: {e}")
                time.sleep(1)
        
        self.logger.info("Consciousness monitoring thread stopped")
    
    def save_metrics(self):
        """Save current metrics to file"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'consciousness_level': self.consciousness_level,
                'component_count': self.component_count,
                'last_update': self.last_update
            }
            
            # Read existing metrics
            metrics_data = []
            if os.path.exists(self.config['metrics_file']):
                with open(self.config['metrics_file'], 'r') as f:
                    metrics_data = json.load(f)
            
            # Add new metrics
            metrics_data.append(metrics)
            
            # Keep only last 1000 entries
            if len(metrics_data) > 1000:
                metrics_data = metrics_data[-1000:]
            
            # Save updated metrics
            os.makedirs(os.path.dirname(self.config['metrics_file']), exist_ok=True)
            with open(self.config['metrics_file'], 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    def setup_socket_server(self):
        """Setup Unix socket server for external communication"""
        try:
            # Remove existing socket
            if os.path.exists(SOCKET_PATH):
                os.unlink(SOCKET_PATH)
            
            self.socket_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket_server.bind(SOCKET_PATH)
            self.socket_server.listen(5)
            
            # Set permissions
            os.chmod(SOCKET_PATH, 0o666)
            
            self.logger.info(f"Socket server listening on {SOCKET_PATH}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup socket server: {e}")
            return False
    
    def socket_thread(self):
        """Handle socket connections"""
        self.logger.info("Socket server thread started")
        
        while self.running:
            try:
                # Use select with timeout for clean shutdown
                ready, _, _ = select.select([self.socket_server], [], [], 1.0)
                if not ready:
                    continue
                
                client_socket, addr = self.socket_server.accept()
                self.logger.debug("Client connected to socket")
                
                # Handle client in separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    self.logger.error(f"Error in socket thread: {e}")
                break
        
        self.logger.info("Socket server thread stopped")
    
    def handle_client(self, client_socket):
        """Handle individual client connections"""
        try:
            with client_socket:
                data = client_socket.recv(1024).decode().strip()
                
                if data == "STATUS":
                    response = {
                        'consciousness_level': self.consciousness_level,
                        'component_count': self.component_count,
                        'last_update': self.last_update,
                        'running': self.running
                    }
                    client_socket.send(json.dumps(response).encode())
                
                elif data.startswith("REGISTER:"):
                    component_name = data[9:]
                    success = self.register_component(component_name)
                    client_socket.send(str(success).encode())
                
                elif data.startswith("LOG:"):
                    message = data[4:]
                    success = self.log_message(message)
                    client_socket.send(str(success).encode())
                
                elif data.startswith("EVENT:"):
                    event = data[6:]
                    success = self.send_event(event)
                    client_socket.send(str(success).encode())
                
                elif data == "PROC":
                    proc_data = self.read_proc_status()
                    if proc_data:
                        client_socket.send(proc_data.encode())
                    else:
                        client_socket.send(b"ERROR: Failed to read proc status")
                
                else:
                    client_socket.send(b"ERROR: Unknown command")
                
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
    
    def create_pid_file(self):
        """Create PID file"""
        try:
            os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
            with open(PID_FILE, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create PID file: {e}")
            return False
    
    def remove_pid_file(self):
        """Remove PID file"""
        try:
            if os.path.exists(PID_FILE):
                os.unlink(PID_FILE)
        except Exception as e:
            self.logger.error(f"Failed to remove PID file: {e}")
    
    def start(self):
        """Start the daemon"""
        self.logger.info("Starting SynOS Phase 4.2 Consciousness Daemon")
        
        # Check if already running
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # Check if process exists
                self.logger.error(f"Daemon already running with PID {pid}")
                return False
            except OSError:
                # Process doesn't exist, remove stale PID file
                os.unlink(PID_FILE)
        
        # Check kernel module
        if not self.check_kernel_module():
            self.logger.error("Kernel module check failed")
            return False
        
        # Open device
        if not self.open_device():
            self.logger.error("Failed to open device")
            return False
        
        # Create PID file
        if not self.create_pid_file():
            self.logger.error("Failed to create PID file")
            return False
        
        # Setup socket server
        if not self.setup_socket_server():
            self.logger.error("Failed to setup socket server")
            return False
        
        # Register daemon components
        if self.config['auto_register_components']:
            self.register_component("consciousness_daemon")
            self.register_component("advanced_logger_daemon")
            self.register_component("debug_infrastructure_daemon")
        
        # Start threads
        self.running = True
        
        monitoring_thread = threading.Thread(target=self.monitoring_thread)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        self.threads.append(monitoring_thread)
        
        socket_thread = threading.Thread(target=self.socket_thread)
        socket_thread.daemon = True
        socket_thread.start()
        self.threads.append(socket_thread)
        
        self.logger.info("SynOS Consciousness Daemon started successfully")
        self.logger.info(f"PID: {os.getpid()}")
        self.logger.info(f"Device: {DEVICE_PATH}")
        self.logger.info(f"Socket: {SOCKET_PATH}")
        
        return True
    
    def stop(self):
        """Stop the daemon"""
        self.logger.info("Stopping SynOS Consciousness Daemon")
        
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        # Close resources
        self.close_device()
        
        if self.socket_server:
            self.socket_server.close()
            if os.path.exists(SOCKET_PATH):
                os.unlink(SOCKET_PATH)
        
        # Remove PID file
        self.remove_pid_file()
        
        self.logger.info("SynOS Consciousness Daemon stopped")
    
    def run(self):
        """Run the daemon (blocking)"""
        if not self.start():
            return False
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        
        self.stop()
        return True

def main():
    parser = argparse.ArgumentParser(description="SynOS Phase 4.2 Consciousness Daemon")
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    parser.add_argument('--status', '-s', action='store_true', help='Check daemon status')
    parser.add_argument('--stop', action='store_true', help='Stop running daemon')
    
    args = parser.parse_args()
    
    if args.status:
        # Check daemon status
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                print(f"SynOS Consciousness Daemon is running (PID: {pid})")
                
                # Try to get status via socket
                try:
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.connect(SOCKET_PATH)
                    sock.send(b"STATUS")
                    response = sock.recv(1024).decode()
                    data = json.loads(response)
                    print(f"Consciousness Level: {data['consciousness_level']}%")
                    print(f"Component Count: {data['component_count']}")
                    print(f"Last Update: {datetime.fromtimestamp(data['last_update'])}")
                    sock.close()
                except:
                    pass
                    
                return 0
            except OSError:
                print("SynOS Consciousness Daemon is not running (stale PID file)")
                return 1
        else:
            print("SynOS Consciousness Daemon is not running")
            return 1
    
    if args.stop:
        # Stop daemon
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Sent SIGTERM to PID {pid}")
                return 0
            except OSError:
                print("Process not found")
                return 1
        else:
            print("Daemon not running")
            return 1
    
    # Run daemon
    daemon = SynOSConsciousnessDaemon(args.config)
    
    if args.daemon:
        # Fork to background
        if os.fork() > 0:
            sys.exit(0)
        os.setsid()
        if os.fork() > 0:
            sys.exit(0)
        
        # Redirect stdin/stdout/stderr
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
    
    success = daemon.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
