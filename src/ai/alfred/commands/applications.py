#!/usr/bin/env python3
"""
ALFRED Application Control Command Handler
Browser, editor, and application launching
"""

import subprocess
import os


class ApplicationHandler:
    """Handler for application control commands"""

    def __init__(self, logger):
        self.logger = logger

    def handle_command(self, command: str) -> tuple[bool, str]:
        """Process application commands"""
        command_lower = command.lower()

        if any(
            browser in command_lower
            for browser in ["firefox", "chrome", "brave", "browser"]
        ):
            return self.open_browser(command)
        elif any(
            editor in command_lower
            for editor in ["code", "vscode", "vim", "nano", "editor"]
        ):
            return self.open_editor(command)
        elif "file manager" in command_lower or "files" in command_lower:
            return self.open_file_manager(command)

        return False, "Application command not recognized"

    def open_browser(self, command: str) -> tuple[bool, str]:
        """Open web browser with optional URL"""
        try:
            # Determine browser
            browser = "firefox"  # Default
            if "chrome" in command.lower():
                browser = "google-chrome"
            elif "brave" in command.lower():
                browser = "brave-browser"

            # Check for private/incognito mode
            private_flag = ""
            if "private" in command.lower() or "incognito" in command.lower():
                if browser == "firefox":
                    private_flag = "--private-window"
                else:
                    private_flag = "--incognito"

            # Extract URL if present
            url = ""
            if "url" in command.lower() or "http" in command.lower():
                words = command.split()
                for word in words:
                    if word.startswith("http"):
                        url = word
                        break

            # Build and execute command
            cmd = f"{browser} {private_flag} {url} &"
            subprocess.Popen(cmd, shell=True)

            mode = "private" if private_flag else "normal"
            msg = f"Opening {browser} in {mode} mode"
            if url:
                msg += f" at {url}"

            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error opening browser: {e}")
            return False, f"Failed to open browser: {str(e)}"

    def open_editor(self, command: str) -> tuple[bool, str]:
        """Open text editor with optional file"""
        try:
            # Determine editor
            editor = "code"  # Default to VS Code
            if "vim" in command.lower():
                editor = "vim"
            elif "nano" in command.lower():
                editor = "nano"

            # Extract file path if present
            file_path = ""
            words = command.split()
            for i, word in enumerate(words):
                if word.lower() in ["open", "edit", "file"] and i + 1 < len(words):
                    potential_path = words[i + 1]
                    if os.path.exists(potential_path):
                        file_path = potential_path
                    break

            # Build command
            if editor == "code":
                cmd = f"code {file_path} &"
            else:
                if file_path:
                    cmd = f"xfce4-terminal -e '{editor} {file_path}'"
                else:
                    cmd = f"xfce4-terminal -e '{editor}'"

            subprocess.Popen(cmd, shell=True)

            msg = f"Opening {editor}"
            if file_path:
                msg += f" with {file_path}"

            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error opening editor: {e}")
            return False, f"Failed to open editor: {str(e)}"

    def open_file_manager(self, command: str) -> tuple[bool, str]:
        """Open file manager at optional path"""
        try:
            # Extract path
            path = os.path.expanduser("~")
            words = command.split()
            for i, word in enumerate(words):
                if word.lower() in ["at", "in"] and i + 1 < len(words):
                    potential_path = words[i + 1]
                    if os.path.exists(potential_path):
                        path = potential_path
                    break

            cmd = f"caja '{path}' &"
            subprocess.Popen(cmd, shell=True)

            msg = f"Opening file manager at {path}"
            self.logger(msg)
            return True, msg

        except Exception as e:
            self.logger(f"Error opening file manager: {e}")
            return False, f"Failed to open file manager: {str(e)}"
