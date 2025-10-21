#!/usr/bin/env python3
"""
ALFRED Security Tools Command Handler
Provides voice control for cybersecurity tools
"""

import subprocess
import os
from typing import Optional, Dict, List


class SecurityToolsHandler:
    """Handler for security tool voice commands"""

    def __init__(self, logger):
        self.logger = logger
        self.tools = {
            'nmap': self.launch_nmap,
            'metasploit': self.launch_metasploit,
            'wireshark': self.launch_wireshark,
            'burp': self.launch_burp_suite,
            'burpsuite': self.launch_burp_suite,
            'john': self.launch_john,
            'aircrack': self.launch_aircrack,
            'sqlmap': self.launch_sqlmap,
        }

    def handle_command(self, command: str) -> tuple[bool, str]:
        """
        Process security tool commands
        Returns: (success: bool, message: str)
        """
        command_lower = command.lower()

        # Pattern matching for different tools
        for tool_name, handler in self.tools.items():
            if tool_name in command_lower:
                return handler(command)

        return False, "Security tool not recognized"

    def launch_nmap(self, command: str) -> tuple[bool, str]:
        """Launch nmap with voice-specified parameters"""
        try:
            # Parse scan type
            scan_type = "-sV"  # Default: version detection
            if "stealth" in command.lower():
                scan_type = "-sS"
            elif "intense" in command.lower():
                scan_type = "-A"
            elif "quick" in command.lower():
                scan_type = "-F"
            elif "ping" in command.lower():
                scan_type = "-sn"

            # Extract target (simple extraction for now)
            target = "localhost"  # Default
            words = command.split()
            for i, word in enumerate(words):
                if word.lower() in ["scan", "target"] and i + 1 < len(words):
                    target = words[i + 1]
                    break

            # Launch in terminal
            cmd = f"xfce4-terminal -e 'nmap {scan_type} {target}' --title='Nmap Scan: {target}'"
            subprocess.Popen(cmd, shell=True)

            self.logger(f"Launched nmap {scan_type} scan on {target}")
            return True, f"Launching nmap {scan_type} scan on {target}"

        except Exception as e:
            self.logger(f"Error launching nmap: {e}")
            return False, f"Failed to launch nmap: {str(e)}"

    def launch_metasploit(self, command: str) -> tuple[bool, str]:
        """Launch Metasploit Framework"""
        try:
            # Determine mode
            if "gui" in command.lower() or "armitage" in command.lower():
                cmd = "armitage &"
                mode = "Armitage GUI"
            else:
                cmd = "xfce4-terminal -e 'msfconsole' --title='Metasploit Framework'"
                mode = "Console"

            subprocess.Popen(cmd, shell=True)
            self.logger(f"Launched Metasploit {mode}")
            return True, f"Launching Metasploit {mode}"

        except Exception as e:
            self.logger(f"Error launching Metasploit: {e}")
            return False, f"Failed to launch Metasploit: {str(e)}"

    def launch_wireshark(self, command: str) -> tuple[bool, str]:
        """Launch Wireshark packet analyzer"""
        try:
            # Extract interface if specified
            interface = ""
            if "interface" in command.lower():
                words = command.split()
                for i, word in enumerate(words):
                    if word.lower() == "interface" and i + 1 < len(words):
                        interface = f"-i {words[i + 1]}"
                        break

            cmd = f"wireshark {interface} &"
            subprocess.Popen(cmd, shell=True)

            msg = f"Launching Wireshark"
            if interface:
                msg += f" on {interface}"

            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error launching Wireshark: {e}")
            return False, f"Failed to launch Wireshark: {str(e)}"

    def launch_burp_suite(self, command: str) -> tuple[bool, str]:
        """Launch Burp Suite proxy"""
        try:
            cmd = "burpsuite &"
            subprocess.Popen(cmd, shell=True)

            self.logger("Launched Burp Suite")
            return True, "Launching Burp Suite Professional"

        except Exception as e:
            self.logger(f"Error launching Burp Suite: {e}")
            return False, f"Failed to launch Burp Suite: {str(e)}"

    def launch_john(self, command: str) -> tuple[bool, str]:
        """Launch John the Ripper"""
        try:
            cmd = "xfce4-terminal -e 'bash -c \"john --help; bash\"' --title='John the Ripper'"
            subprocess.Popen(cmd, shell=True)

            self.logger("Launched John the Ripper")
            return True, "Launching John the Ripper"

        except Exception as e:
            self.logger(f"Error launching John: {e}")
            return False, f"Failed to launch John: {str(e)}"

    def launch_aircrack(self, command: str) -> tuple[bool, str]:
        """Launch Aircrack-ng suite"""
        try:
            cmd = "xfce4-terminal -e 'bash -c \"aircrack-ng --help; bash\"' --title='Aircrack-ng'"
            subprocess.Popen(cmd, shell=True)

            self.logger("Launched Aircrack-ng")
            return True, "Launching Aircrack-ng suite"

        except Exception as e:
            self.logger(f"Error launching Aircrack: {e}")
            return False, f"Failed to launch Aircrack: {str(e)}"

    def launch_sqlmap(self, command: str) -> tuple[bool, str]:
        """Launch SQLMap"""
        try:
            cmd = "xfce4-terminal -e 'bash -c \"sqlmap --help; bash\"' --title='SQLMap'"
            subprocess.Popen(cmd, shell=True)

            self.logger("Launched SQLMap")
            return True, "Launching SQLMap"

        except Exception as e:
            self.logger(f"Error launching SQLMap: {e}")
            return False, f"Failed to launch SQLMap: {str(e)}"
