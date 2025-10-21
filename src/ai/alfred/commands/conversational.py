#!/usr/bin/env python3
"""
ALFRED Conversational AI Handler
Time, date, weather, and general queries
"""

from datetime import datetime
import subprocess
import random


class ConversationalHandler:
    """Handler for conversational queries"""

    def __init__(self, logger):
        self.logger = logger

        # Personality responses
        self.greetings = [
            "Good day, sir.",
            "At your service.",
            "How may I assist you today?",
            "Yes, sir. What can I do for you?",
        ]

        self.acknowledgments = [
            "Very good, sir.",
            "As you wish.",
            "Of course, sir.",
            "Right away, sir.",
        ]

    def handle_command(self, command: str) -> tuple[bool, str]:
        """Process conversational queries"""
        command_lower = command.lower()

        if "time" in command_lower:
            return self.get_time()
        elif "date" in command_lower:
            return self.get_date()
        elif "hello" in command_lower or "hi" in command_lower:
            return self.greet()
        elif "thank" in command_lower:
            return self.acknowledge()
        elif "weather" in command_lower:
            return self.get_weather()
        elif "who are you" in command_lower or "what are you" in command_lower:
            return self.introduce()
        elif "help" in command_lower:
            return self.show_help()

        return False, "I'm afraid I don't understand that query, sir."

    def get_time(self) -> tuple[bool, str]:
        """Get current time"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")

        self.logger(f"Time query: {time_str}")
        return True, f"The time is {time_str}, sir."

    def get_date(self) -> tuple[bool, str]:
        """Get current date"""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")

        self.logger(f"Date query: {date_str}")
        return True, f"Today is {date_str}, sir."

    def greet(self) -> tuple[bool, str]:
        """Respond to greeting"""
        response = random.choice(self.greetings)
        self.logger("Greeting exchange")
        return True, response

    def acknowledge(self) -> tuple[bool, str]:
        """Acknowledge gratitude"""
        response = random.choice(self.acknowledgments)
        self.logger("Acknowledgment")
        return True, response

    def get_weather(self) -> tuple[bool, str]:
        """Get weather information (basic implementation)"""
        try:
            # Use wttr.in for weather
            cmd = "xfce4-terminal -e 'bash -c \"curl wttr.in; read -p \\\"Press Enter to close...\\\"\"' --title='Weather Report'"
            subprocess.Popen(cmd, shell=True)

            self.logger("Weather query")
            return True, "Fetching weather report, sir."

        except Exception as e:
            self.logger(f"Weather query failed: {e}")
            return False, "I'm unable to retrieve the weather at the moment, sir."

    def introduce(self) -> tuple[bool, str]:
        """Introduce ALFRED"""
        intro = ("I am ALFRED, your loyal digital butler. "
                "I'm here to assist with system operations, security tools, "
                "and general tasks. How may I be of service?")

        self.logger("Introduction")
        return True, intro

    def show_help(self) -> tuple[bool, str]:
        """Show available commands"""
        help_text = """
╔═══════════════════════════════════════════════════════════╗
║              ALFRED Voice Commands                        ║
╚═══════════════════════════════════════════════════════════╝

🔒 SECURITY TOOLS:
   • "Alfred, launch nmap [scan type] [target]"
   • "Alfred, open metasploit"
   • "Alfred, start wireshark"
   • "Alfred, launch burp suite"

🖥️  SYSTEM:
   • "Alfred, system health check"
   • "Alfred, check for updates"
   • "Alfred, open terminal [at path]"

🌐 APPLICATIONS:
   • "Alfred, open firefox [url]"
   • "Alfred, open code [file]"

📁 FILES:
   • "Alfred, find file [name]"
   • "Alfred, open [bookmark]"

💬 CONVERSATIONAL:
   • "What time is it?"
   • "What's the date?"
   • "Show weather"

Say "Alfred" followed by your command.
"""

        try:
            # Display in terminal
            escaped_help = help_text.replace('"', '\\"').replace('$', '\\$')
            cmd = f'xfce4-terminal -e \'bash -c "echo \\"{escaped_help}\\"; read -p \\"Press Enter to close...\\"\"\' --title=\'ALFRED Help\''
            subprocess.Popen(cmd, shell=True)

            self.logger("Help displayed")
            return True, "Displaying command reference, sir."

        except Exception as e:
            self.logger(f"Error displaying help: {e}")
            return False, "I'm having trouble displaying the help guide, sir."
