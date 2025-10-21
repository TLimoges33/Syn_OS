#!/usr/bin/env python3
"""
ALFRED File Operations Command Handler
File search, navigation, and management
"""

import subprocess
import os
from pathlib import Path


class FileHandler:
    """Handler for file operation commands"""

    def __init__(self, logger):
        self.logger = logger
        self.bookmarks = {
            "home": os.path.expanduser("~"),
            "documents": os.path.expanduser("~/Documents"),
            "downloads": os.path.expanduser("~/Downloads"),
            "desktop": os.path.expanduser("~/Desktop"),
            "synos": "/home/diablorain/Syn_OS",
        }

    def handle_command(self, command: str) -> tuple[bool, str]:
        """Process file operation commands"""
        command_lower = command.lower()

        if "find" in command_lower or "search" in command_lower:
            return self.find_file(command)
        elif "open" in command_lower and any(
            loc in command_lower for loc in self.bookmarks.keys()
        ):
            return self.open_bookmark(command)
        elif "navigate" in command_lower or "go to" in command_lower:
            return self.navigate_to(command)

        return False, "File operation not recognized"

    def find_file(self, command: str) -> tuple[bool, str]:
        """Search for files"""
        try:
            # Extract filename
            words = command.split()
            filename = ""
            for i, word in enumerate(words):
                if word.lower() in ["find", "search", "file"] and i + 1 < len(words):
                    filename = words[i + 1]
                    break

            if not filename:
                return False, "No filename specified"

            # Determine search path
            search_path = os.path.expanduser("~")
            if "in" in command.lower():
                for i, word in enumerate(words):
                    if word.lower() == "in" and i + 1 < len(words):
                        path = words[i + 1]
                        if os.path.exists(path):
                            search_path = path
                        break

            # Execute search using find command
            cmd = f"""xfce4-terminal -e 'bash -c "
                echo \\"Searching for: {filename}\\";
                echo \\"Path: {search_path}\\";
                echo \\"\\";
                find {search_path} -iname \\"*{filename}*\\" 2>/dev/null;
                echo \\"\\";
                read -p \\"Press Enter to close...\\"
            "' --title='File Search: {filename}'"""

            subprocess.Popen(cmd, shell=True)

            msg = f"Searching for {filename} in {search_path}"
            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error searching for file: {e}")
            return False, f"File search failed: {str(e)}"

    def open_bookmark(self, command: str) -> tuple[bool, str]:
        """Open bookmarked location"""
        try:
            command_lower = command.lower()

            # Find matching bookmark
            location = None
            location_name = None
            for name, path in self.bookmarks.items():
                if name in command_lower:
                    location = path
                    location_name = name
                    break

            if not location:
                return False, "Bookmark not found"

            # Open in file manager
            cmd = f"caja '{location}' &"
            subprocess.Popen(cmd, shell=True)

            msg = f"Opening {location_name}"
            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error opening bookmark: {e}")
            return False, f"Failed to open bookmark: {str(e)}"

    def navigate_to(self, command: str) -> tuple[bool, str]:
        """Navigate to specified directory"""
        try:
            # Extract path
            words = command.split()
            path = None

            for i, word in enumerate(words):
                if word.lower() in ["to", "navigate"] and i + 1 < len(words):
                    potential_path = words[i + 1]
                    expanded_path = os.path.expanduser(potential_path)
                    if os.path.exists(expanded_path):
                        path = expanded_path
                    break

            if not path:
                return False, "Invalid or non-existent path"

            # Open in file manager
            cmd = f"caja '{path}' &"
            subprocess.Popen(cmd, shell=True)

            msg = f"Navigating to {path}"
            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error navigating: {e}")
            return False, f"Navigation failed: {str(e)}"
