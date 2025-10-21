#!/usr/bin/env python3
"""
ALFRED System Operations Command Handler
System health, updates, terminal, and resource management
"""

import subprocess
import os
import psutil
from datetime import datetime


class SystemHandler:
    """Handler for system operation commands"""

    def __init__(self, logger):
        self.logger = logger

    def handle_command(self, command: str) -> tuple[bool, str]:
        """Process system commands"""
        command_lower = command.lower()

        if "health" in command_lower or "status" in command_lower:
            return self.system_health_check()
        elif "update" in command_lower:
            return self.check_updates()
        elif "terminal" in command_lower:
            return self.open_terminal(command)
        elif "shutdown" in command_lower:
            return self.shutdown_system()
        elif "reboot" in command_lower or "restart" in command_lower:
            return self.reboot_system()

        return False, "System command not recognized"

    def system_health_check(self) -> tuple[bool, str]:
        """Perform comprehensive system health check"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory Usage
            memory = psutil.virtual_memory()
            mem_total_gb = memory.total / (1024**3)
            mem_used_gb = memory.used / (1024**3)
            mem_percent = memory.percent

            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_used_gb = disk.used / (1024**3)
            disk_percent = disk.percent

            # Network
            net_io = psutil.net_io_counters()
            bytes_sent_mb = net_io.bytes_sent / (1024**2)
            bytes_recv_mb = net_io.bytes_recv / (1024**2)

            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            # Build report
            report = f"""
╔══════════════════════════════════════════════════════════╗
║           SynOS System Health Report                     ║
╚══════════════════════════════════════════════════════════╝

🖥️  CPU:
   └─ Usage: {cpu_percent}% ({cpu_count} cores)

🧠 Memory:
   └─ Used: {mem_used_gb:.2f} GB / {mem_total_gb:.2f} GB ({mem_percent}%)

💾 Disk:
   └─ Used: {disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB ({disk_percent}%)

🌐 Network:
   ├─ Sent: {bytes_sent_mb:.2f} MB
   └─ Received: {bytes_recv_mb:.2f} MB

⏱️  Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m

✅ All systems operational
"""

            # Display in terminal
            cmd = f"xfce4-terminal -e 'bash -c \"echo \\\"{report}\\\"; read -p \\\"Press Enter to close...\\\"\"' --title='System Health Check'"
            subprocess.Popen(cmd, shell=True)

            # Voice summary
            health_status = "healthy"
            if cpu_percent > 80 or mem_percent > 85 or disk_percent > 90:
                health_status = "under stress"

            summary = f"System is {health_status}. CPU at {cpu_percent:.0f}%, memory at {mem_percent:.0f}%, disk at {disk_percent:.0f}%"

            self.logger(f"Health check completed: {health_status}")
            return True, summary

        except Exception as e:
            self.logger(f"Error during health check: {e}")
            return False, f"Health check failed: {str(e)}"

    def check_updates(self) -> tuple[bool, str]:
        """Check for system updates"""
        try:
            cmd = """xfce4-terminal -e 'bash -c "
                echo \\"Checking for updates...\\";
                sudo apt update;
                echo \\"\\";
                echo \\"Available updates:\\";
                apt list --upgradable;
                echo \\"\\";
                read -p \\"Install updates? (y/n): \\" choice;
                if [ \\"\\$choice\\" = \\"y\\" ]; then
                    sudo apt upgrade -y;
                fi;
                read -p \\"Press Enter to close...\\"
            "' --title='System Updates'"""

            subprocess.Popen(cmd, shell=True)

            self.logger("Checking for system updates")
            return True, "Checking for system updates"

        except Exception as e:
            self.logger(f"Error checking updates: {e}")
            return False, f"Failed to check updates: {str(e)}"

    def open_terminal(self, command: str) -> tuple[bool, str]:
        """Open terminal, optionally at specific path or as root"""
        try:
            # Check for root request
            is_root = "root" in command.lower() or "sudo" in command.lower()

            # Check for path
            path = os.path.expanduser("~")
            if "at" in command.lower():
                words = command.split()
                for i, word in enumerate(words):
                    if word.lower() == "at" and i + 1 < len(words):
                        path = words[i + 1]
                        if not os.path.exists(path):
                            path = os.path.expanduser("~")
                        break

            # Build command
            if is_root:
                cmd = f"xfce4-terminal --working-directory='{path}' -e 'sudo -i' --title='Root Terminal'"
                msg = "Opening root terminal"
            else:
                cmd = f"xfce4-terminal --working-directory='{path}'"
                msg = f"Opening terminal at {path}"

            subprocess.Popen(cmd, shell=True)

            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error opening terminal: {e}")
            return False, f"Failed to open terminal: {str(e)}"

    def shutdown_system(self) -> tuple[bool, str]:
        """Shutdown the system"""
        try:
            self.logger("Initiating system shutdown")
            subprocess.Popen("shutdown -h now", shell=True)
            return True, "Shutting down system now"
        except Exception as e:
            self.logger(f"Error during shutdown: {e}")
            return False, f"Failed to shutdown: {str(e)}"

    def reboot_system(self) -> tuple[bool, str]:
        """Reboot the system"""
        try:
            self.logger("Initiating system reboot")
            subprocess.Popen("shutdown -r now", shell=True)
            return True, "Rebooting system now"
        except Exception as e:
            self.logger(f"Error during reboot: {e}")
            return False, f"Failed to reboot: {str(e)}"
