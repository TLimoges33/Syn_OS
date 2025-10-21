#!/usr/bin/env python3
################################################################################
# SynOS ALFRED - AI Voice Assistant v1.1
# "Your Loyal Digital Butler" - Inspired by Batman's trusted companion
# v1.1 - Enhanced command system with modular handlers
# v1.4 Goal - Full audio experience (read anything, speak everything)
################################################################################

import os
import sys
import time
import subprocess
import threading
import queue
import signal
from pathlib import Path

# Add commands directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for required imports
try:
    import speech_recognition as sr
    import pyaudio
    import psutil
except ImportError:
    print("Installing required packages...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "SpeechRecognition",
            "pyaudio",
            "psutil",
        ],
        check=True,
    )
    import speech_recognition as sr
    import pyaudio
    import psutil

# Import command handlers
try:
    from commands import (
        SecurityToolsHandler,
        SystemHandler,
        ApplicationHandler,
        FileHandler,
        ConversationalHandler,
    )
except ImportError as e:
    print(f"Warning: Could not import command handlers: {e}")
    print("Basic functionality only")

# Import audio manager
try:
    from audio_manager import AudioManager

    AUDIO_MANAGER_AVAILABLE = True
except ImportError:
    print("Warning: AudioManager not available - audio optimization disabled")
    AUDIO_MANAGER_AVAILABLE = False

# Configuration
CONFIG = {
    "wake_word": "alfred",
    "language": "en-US",
    "listen_timeout": 5,
    "phrase_timeout": 3,
    "energy_threshold": 4000,
    "hotkey_transcribe": "ctrl+alt+t",
    "audio_feedback": True,
    "log_file": "/var/log/synos/alfred.log",
    "british_accent": True,  # Alfred should sound British!
    "version": "1.1.0",
}


class ALFREDAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.transcribe_mode = False
        self.command_queue = queue.Queue()

        # Configure recognizer
        self.recognizer.energy_threshold = CONFIG["energy_threshold"]
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Log file
        os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)

        # Initialize audio manager for optimization
        if AUDIO_MANAGER_AVAILABLE:
            try:
                self.audio_manager = AudioManager()
                self.log("AudioManager initialized - optimizing audio devices...")
                self.audio_manager.optimize_for_voice()
                self.log("Audio optimization complete")
            except Exception as e:
                self.log(f"Audio optimization failed: {e}")
                self.audio_manager = None
        else:
            self.audio_manager = None

        # Initialize command handlers
        try:
            self.security_handler = SecurityToolsHandler(self.log)
            self.system_handler = SystemHandler(self.log)
            self.app_handler = ApplicationHandler(self.log)
            self.file_handler = FileHandler(self.log)
            self.conv_handler = ConversationalHandler(self.log)
            self.handlers_available = True
            self.log("ALFRED v1.1 with enhanced command system initialized")
        except Exception as e:
            self.handlers_available = False
            self.log(f"Running in basic mode: {e}")

    def log(self, message):
        """Log message to file and console"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        try:
            with open(CONFIG["log_file"], "a") as f:
                f.write(log_msg + "\n")
        except:
            pass

    def play_sound(self, sound_type="beep"):
        """Play audio feedback"""
        if not CONFIG["audio_feedback"]:
            return

        try:
            if sound_type == "beep":
                subprocess.Popen(
                    ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif sound_type == "activated":
                # Try custom sound first, fall back to system sound
                custom_sound = "/usr/share/sounds/synos/boot/ai-online.ogg"
                if os.path.exists(custom_sound):
                    subprocess.Popen(
                        ["paplay", custom_sound],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.Popen(
                        ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
        except:
            pass

    def speak(self, text):
        """Text-to-speech using espeak (lightweight, British accent)"""
        self.log(f"ALFRED: {text}")
        try:
            # Use British English voice for Alfred
            voice = "en-gb+m3" if CONFIG["british_accent"] else "en+m3"
            subprocess.Popen(
                ["espeak", "-v", voice, "-s", "150", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            self.log(f"TTS Error: {e}")

    def listen_for_wake_word(self):
        """Listen for wake word in background"""
        self.log("Listening for wake word...")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.listening:
                try:
                    audio = self.recognizer.listen(
                        source, timeout=10, phrase_time_limit=5
                    )

                    # Use Google Speech Recognition (free tier)
                    text = self.recognizer.recognize_google(
                        audio, language=CONFIG["language"]
                    )
                    text_lower = text.lower()

                    self.log(f"Heard: {text}")

                    # Check for wake word
                    if CONFIG["wake_word"] in text_lower:
                        self.play_sound("activated")
                        self.speak("At your service, sir.")
                        self.process_command()

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.log(f"Speech recognition error: {e}")
                    time.sleep(5)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.log(f"Listen error: {e}")
                    time.sleep(1)

    def process_command(self):
        """Listen for command after wake word"""
        self.log("Listening for command...")

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source,
                    timeout=CONFIG["listen_timeout"],
                    phrase_time_limit=CONFIG["phrase_timeout"],
                )

                command = self.recognizer.recognize_google(
                    audio, language=CONFIG["language"]
                )
                self.log(f"Command: {command}")

                self.execute_command(command)

        except sr.WaitTimeoutError:
            self.speak("I didn't quite catch that, sir.")
        except sr.UnknownValueError:
            self.speak("Pardon me, I didn't understand.")
        except Exception as e:
            self.log(f"Command error: {e}")
            self.speak("My apologies, I encountered an error.")

    def execute_command(self, command):
        """Execute voice command using modular handlers"""

        if not self.handlers_available:
            # Fall back to basic command execution
            self.execute_basic_command(command)
            return

        command_lower = command.lower()
        success = False
        response = ""

        # Try each handler in priority order
        try:
            # 1. Conversational (greetings, time, help)
            if any(
                word in command_lower
                for word in [
                    "hello",
                    "hi",
                    "time",
                    "date",
                    "help",
                    "thank",
                    "who",
                    "what",
                    "weather",
                ]
            ):
                success, response = self.conv_handler.handle_command(command)
                if success:
                    self.speak(response)
                    return

            # 2. Security Tools
            if any(
                tool in command_lower
                for tool in [
                    "nmap",
                    "metasploit",
                    "wireshark",
                    "burp",
                    "john",
                    "aircrack",
                    "sqlmap",
                    "scan",
                ]
            ):
                success, response = self.security_handler.handle_command(command)
                if success:
                    self.speak(response)
                    return

            # 3. System Operations
            if any(
                op in command_lower
                for op in [
                    "health",
                    "status",
                    "update",
                    "terminal",
                    "shutdown",
                    "reboot",
                ]
            ):
                success, response = self.system_handler.handle_command(command)
                if success:
                    self.speak(response)
                    return

            # 4. Applications
            if any(
                app in command_lower
                for app in [
                    "firefox",
                    "chrome",
                    "brave",
                    "browser",
                    "code",
                    "vim",
                    "nano",
                    "editor",
                    "file manager",
                ]
            ):
                success, response = self.app_handler.handle_command(command)
                if success:
                    self.speak(response)
                    return

            # 5. File Operations
            if any(
                op in command_lower
                for op in ["find", "search", "navigate", "open home", "open documents"]
            ):
                success, response = self.file_handler.handle_command(command)
                if success:
                    self.speak(response)
                    return

            # If no handler matched
            if not success:
                self.log(f"No handler matched for: {command}")
                self.speak(
                    "I'm afraid I don't know how to do that yet, sir. Try saying 'help' for available commands."
                )

        except Exception as e:
            self.log(f"Error executing command: {e}")
            self.speak("I encountered an error processing your request, sir.")

    def execute_basic_command(self, command):
        """Fallback basic command execution (v1.0 compatibility)"""
        command_lower = command.lower()

        # Basic commands with Alfred's personality
        if "open" in command_lower:
            if "terminal" in command_lower:
                self.speak("Opening terminal for you")
                subprocess.Popen(["xfce4-terminal"])
            elif "nmap" in command_lower:
                self.speak("Initiating network scanner")
                subprocess.Popen(["xfce4-terminal", "-e", "nmap"])
            elif "metasploit" in command_lower:
                self.speak("Preparing the Metasploit Framework")
                subprocess.Popen(["xfce4-terminal", "-e", "msfconsole"])
            elif "wireshark" in command_lower:
                self.speak("Opening Wireshark")
                subprocess.Popen(["wireshark"])
            elif "burp" in command_lower:
                self.speak("Launching Burp Suite")
                subprocess.Popen(["burpsuite"])
            else:
                self.speak("I'm afraid I don't know how to open that yet, sir.")

        elif "what" in command_lower or "who" in command_lower:
            if "time" in command_lower:
                current_time = time.strftime("%I:%M %p")
                self.speak(f"The time is {current_time}, sir.")
            elif "date" in command_lower:
                current_date = time.strftime("%A, %B %d, %Y")
                self.speak(f"Today is {current_date}.")
            elif "are you" in command_lower:
                self.speak("I am ALFRED, your loyal digital butler.")

        elif "help" in command_lower:
            self.speak(
                "I can assist with security tools, system commands, or transcription. Try: open nmap, or what time is it."
            )

        elif "thank" in command_lower:
            self.speak("Always a pleasure to serve, sir.")

        else:
            self.log(f"Unknown command: {command}")
            self.speak("I'm afraid that's not in my repertoire yet, sir.")

    def transcribe_to_text(self):
        """Transcribe speech and insert into focused window"""
        self.log("Transcription mode activated")
        self.speak("Transcription mode active. Please proceed.")

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)

                # Transcribe
                text = self.recognizer.recognize_google(
                    audio, language=CONFIG["language"]
                )
                self.log(f"Transcribed: {text}")

                # Insert into focused window using xdotool
                subprocess.run(
                    ["xdotool", "type", "--clearmodifiers", text], check=True
                )

                self.play_sound("beep")

        except sr.WaitTimeoutError:
            self.speak("No speech detected, sir.")
        except sr.UnknownValueError:
            self.speak("I couldn't quite make that out.")
        except Exception as e:
            self.log(f"Transcription error: {e}")
            self.speak("Transcription failed, my apologies.")

    def start(self):
        """Start ALFRED assistant"""
        self.log("Starting ALFRED assistant...")
        self.speak("ALFRED at your service. I am ready for your commands, sir.")

        self.listening = True

        # Start wake word listener in background thread
        listener_thread = threading.Thread(
            target=self.listen_for_wake_word, daemon=True
        )
        listener_thread.start()

        # Main loop
        self.log("ALFRED is running. Press Ctrl+C to stop.")
        self.log("Say 'Hey Alfred' or 'Alfred' to activate voice commands.")
        self.log(
            f"Global hotkey {CONFIG['hotkey_transcribe']} for transcription (coming soon)"
        )

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("Shutting down ALFRED...")
            self.listening = False
            self.speak("Shutting down. Until next time, sir.")
            sys.exit(0)


def main():
    """Main entry point"""
    print("=" * 70)
    print("SynOS ALFRED - Your Loyal Digital Butler")
    print(f"v{CONFIG['version']} - Enhanced Command System")
    print("v1.4 Vision - Read Anything, Speak Everything")
    print("=" * 70)
    print()

    # Check for microphone
    try:
        mic = sr.Microphone()
        print(f"✅ Microphone detected: {mic.device_index}")
    except Exception as e:
        print(f"❌ No microphone detected: {e}")
        print("   ALFRED requires a microphone to function.")
        sys.exit(1)

    # Check for espeak (TTS)
    try:
        subprocess.run(["which", "espeak"], check=True, capture_output=True)
        print("✅ espeak TTS available")
    except:
        print("⚠️  espeak not found, installing...")
        try:
            subprocess.run(["sudo", "apt", "install", "-y", "espeak"], check=True)
        except:
            print("❌ Could not install espeak. Voice responses will not work.")

    # Check for xdotool
    try:
        subprocess.run(["which", "xdotool"], check=True, capture_output=True)
        print("✅ xdotool available for text insertion")
    except:
        print("⚠️  xdotool not found. Install with: sudo apt install xdotool")

    # Check for psutil
    try:
        import psutil

        print("✅ psutil available for system monitoring")
    except:
        print("⚠️  psutil not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)

    print()
    print("🔴 Starting ALFRED... 🔴")
    print()

    # Create and start assistant
    alfred = ALFREDAssistant()
    alfred.start()


if __name__ == "__main__":
    main()
