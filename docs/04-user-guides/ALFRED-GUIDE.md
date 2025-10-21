# ALFRED Voice Assistant - User Guide

**Version:** 1.1.0  
**SynOS Component:** AI Voice Interface  
**Status:** Active Development

---

## 🎤 Overview

ALFRED (Adaptive Learning Framework for Responsive Executive Decisions) is your loyal digital butler for SynOS. Inspired by Batman's trusted companion, ALFRED provides voice-controlled access to security tools, system operations, and general computing tasks with a sophisticated British personality.

---

## 🚀 Quick Start

### Launching ALFRED

**Desktop Launcher:**

```bash
# From applications menu
Applications → System → ALFRED Voice Assistant

# Or from terminal
python3 /usr/share/synos/alfred/alfred-daemon-v1.1.py
```

**Systemd Service:**

```bash
# Enable on boot
sudo systemctl enable alfred

# Start now
sudo systemctl start alfred

# Check status
sudo systemctl status alfred
```

### First Use

1. **Microphone Setup**: Ensure your microphone is connected and working
2. **Wake Word**: Say "Alfred" to activate
3. **Command**: Speak your request clearly
4. **Response**: ALFRED will acknowledge and execute

---

## 🗣️ Voice Commands Reference

### 🔒 Security Tools

| Command                               | Action                      | Example                                   |
| ------------------------------------- | --------------------------- | ----------------------------------------- |
| `Alfred, launch nmap [type] [target]` | Run Nmap scan               | "Alfred, launch nmap stealth 192.168.1.1" |
| `Alfred, open metasploit`             | Launch Metasploit Framework | "Alfred, open metasploit"                 |
| `Alfred, start wireshark [interface]` | Start packet capture        | "Alfred, start wireshark on eth0"         |
| `Alfred, launch burp suite`           | Open Burp Suite             | "Alfred, launch burp suite"               |
| `Alfred, open john the ripper`        | Launch John                 | "Alfred, open john"                       |
| `Alfred, start aircrack`              | Launch Aircrack-ng          | "Alfred, start aircrack"                  |
| `Alfred, open sqlmap`                 | Launch SQLMap               | "Alfred, open sqlmap"                     |

**Nmap Scan Types:**

-   `quick` - Fast scan (-F)
-   `stealth` - SYN scan (-sS)
-   `intense` - Aggressive scan (-A)
-   `ping` - Ping sweep (-sn)
-   Default: Version detection (-sV)

### 🖥️ System Operations

| Command                           | Action                  | Example                          |
| --------------------------------- | ----------------------- | -------------------------------- |
| `Alfred, system health check`     | Show system status      | "Alfred, system health check"    |
| `Alfred, check for updates`       | Check & install updates | "Alfred, check for updates"      |
| `Alfred, open terminal [at path]` | Open terminal           | "Alfred, open terminal at /home" |
| `Alfred, open root terminal`      | Open terminal as root   | "Alfred, open root terminal"     |
| `Alfred, shutdown`                | Shutdown system         | "Alfred, shutdown"               |
| `Alfred, reboot`                  | Reboot system           | "Alfred, reboot"                 |

**System Health Check Shows:**

-   CPU usage and core count
-   Memory usage (GB and %)
-   Disk usage (GB and %)
-   Network statistics
-   System uptime

### 🌐 Applications

| Command                        | Action            | Example                                  |
| ------------------------------ | ----------------- | ---------------------------------------- |
| `Alfred, open firefox [url]`   | Launch Firefox    | "Alfred, open firefox"                   |
| `Alfred, open chrome [url]`    | Launch Chrome     | "Alfred, open chrome https://google.com" |
| `Alfred, open brave [url]`     | Launch Brave      | "Alfred, open brave"                     |
| `Alfred, open firefox private` | Private browsing  | "Alfred, open firefox private"           |
| `Alfred, open code [file]`     | Launch VS Code    | "Alfred, open code /path/to/file"        |
| `Alfred, open vim [file]`      | Launch Vim        | "Alfred, open vim config.txt"            |
| `Alfred, open nano [file]`     | Launch Nano       | "Alfred, open nano"                      |
| `Alfred, open file manager`    | Open file browser | "Alfred, open file manager"              |

### 📁 File Operations

| Command                              | Action              | Example                             |
| ------------------------------------ | ------------------- | ----------------------------------- |
| `Alfred, find file [name]`           | Search for files    | "Alfred, find file report.pdf"      |
| `Alfred, find file [name] in [path]` | Search in directory | "Alfred, find file log in /var/log" |
| `Alfred, open home`                  | Open home directory | "Alfred, open home"                 |
| `Alfred, open documents`             | Open Documents      | "Alfred, open documents"            |
| `Alfred, open downloads`             | Open Downloads      | "Alfred, open downloads"            |
| `Alfred, open desktop`               | Open Desktop        | "Alfred, open desktop"              |
| `Alfred, navigate to [path]`         | Navigate to path    | "Alfred, navigate to /etc"          |

### 💬 Conversational

| Command            | Response       | Example            |
| ------------------ | -------------- | ------------------ |
| `What time is it?` | Current time   | "What time is it?" |
| `What's the date?` | Current date   | "What's the date?" |
| `Show weather`     | Weather report | "Show weather"     |
| `Hello Alfred`     | Greeting       | "Hello Alfred"     |
| `Thank you`        | Acknowledgment | "Thank you"        |
| `Who are you?`     | Introduction   | "Who are you?"     |
| `Help`             | Show commands  | "Help"             |

---

## ⚙️ Configuration

### Config File Location

```bash
~/.config/synos/alfred/config.json
```

### Available Settings

```json
{
    "wake_word": "alfred",
    "language": "en-US",
    "listen_timeout": 5,
    "phrase_timeout": 3,
    "energy_threshold": 4000,
    "audio_feedback": true,
    "british_accent": true,
    "log_level": "INFO"
}
```

### Microphone Calibration

```bash
# Test microphone
arecord -d 5 test.wav
aplay test.wav

# Adjust input level
alsamixer
# Navigate to 'Capture' and adjust with arrow keys

# PulseAudio volume control
pavucontrol
# Go to 'Input Devices' tab and adjust
```

### Voice Calibration

The first time you run ALFRED, it calibrates for ambient noise. For best results:

1. Launch ALFRED in your typical working environment
2. Wait 5 seconds for calibration (don't speak)
3. Speak clearly at normal volume, 1-2 feet from mic
4. If recognition is poor, increase `energy_threshold` in config

---

## 🎯 Advanced Usage

### Chaining Commands

You can speak multiple commands in sequence:

```
"Alfred, system health check"
[wait for completion]
"Alfred, open terminal"
[wait for ALFRED to respond]
"Alfred, launch nmap"
```

### Custom Bookmarks

Edit `src/ai/alfred/commands/files.py` to add custom bookmarks:

```python
self.bookmarks = {
    "home": os.path.expanduser("~"),
    "documents": os.path.expanduser("~/Documents"),
    "projects": "/home/user/projects",  # Add custom paths
    "synos": "/home/diablorain/Syn_OS",
}
```

### Transcription Mode (Coming in v1.2)

Global hotkey `Ctrl+Alt+T` will activate transcription:

1. Press hotkey
2. Speak
3. Text appears in focused window

---

## 🔧 Troubleshooting

### ALFRED Doesn't Respond to Wake Word

**Check microphone:**

```bash
arecord -l  # List recording devices
pactl list sources  # PulseAudio sources
```

**Test wake word detection:**

```bash
# Check log for recognition
tail -f /var/log/synos/alfred.log
```

**Adjust sensitivity:**

-   Increase `energy_threshold` if too sensitive
-   Decrease if not sensitive enough
-   Default: 4000

### Voice Not Recognized

**Install language support:**

```bash
sudo apt install espeak espeak-data
```

**Check internet connection:**

-   Google Speech Recognition requires internet
-   Offline STT coming in future versions

### Audio Feedback Not Working

**Check PulseAudio:**

```bash
pulseaudio --check
pulseaudio --start

# Test sound
paplay /usr/share/sounds/freedesktop/stereo/complete.oga
```

### Commands Not Executing

**Check dependencies:**

```bash
# Install missing tools
sudo apt install xfce4-terminal xdotool

# Check Python dependencies
pip3 install SpeechRecognition pyaudio psutil
```

---

## 📊 Performance Tips

### Reduce CPU Usage

1. **Increase `listen_timeout`**: Less frequent checks
2. **Disable audio feedback**: Set `audio_feedback: false`
3. **Adjust ambient noise calibration**: Shorter duration

### Improve Accuracy

1. **Reduce background noise**: Quiet environment works best
2. **Use quality microphone**: USB microphones recommended
3. **Clear pronunciation**: Speak clearly, not too fast
4. **Consistent distance**: 1-2 feet from microphone

### Battery Saving (Laptops)

```bash
# Run only when needed (don't enable systemd service)
python3 /usr/share/synos/alfred/alfred-daemon-v1.1.py

# Stop when not in use
Ctrl+C
```

---

## 🛠️ Development

### Adding Custom Commands

1. **Create handler** in `src/ai/alfred/commands/`
2. **Import handler** in `commands/__init__.py`
3. **Register handler** in `alfred-daemon-v1.1.py`

Example:

```python
# commands/my_commands.py
class MyCommandHandler:
    def __init__(self, logger):
        self.logger = logger

    def handle_command(self, command: str) -> tuple[bool, str]:
        if "my command" in command.lower():
            # Do something
            return True, "Command executed"
        return False, "Not my command"
```

### Testing Commands

```python
# Test individual handlers
from commands import SecurityToolsHandler

handler = SecurityToolsHandler(print)
success, msg = handler.handle_command("launch nmap localhost")
print(f"Success: {success}, Message: {msg}")
```

---

## 🔮 Roadmap

### v1.1 (Current) - November 2025

-   ✅ Enhanced command system
-   ✅ Security tool integration
-   ✅ System health monitoring
-   ✅ File operations
-   ✅ Conversational AI

### v1.2 - December 2025

-   [ ] Offline speech recognition
-   [ ] Global hotkey transcription
-   [ ] Custom wake words
-   [ ] Multi-language support

### v1.3 - January 2026

-   [ ] Context awareness
-   [ ] Command history
-   [ ] Smart suggestions
-   [ ] Voice profiles

### v1.4 - February 2026 🎯 **MAJOR MILESTONE**

-   [ ] Read anything (screen reader)
-   [ ] Speak everything (full TTS)
-   [ ] Natural conversations
-   [ ] Continuous listening mode

---

## 📞 Support

**Documentation:**

-   [SynOS Docs](../../README.md)
-   [TODO.md](../06-project-status/TODO.md)
-   [v1.1 Development Plan](../06-project-status/V1.1-DEVELOPMENT-PLAN.md)

**Logs:**

```bash
# ALFRED logs
tail -f /var/log/synos/alfred.log

# System logs
journalctl -u alfred -f
```

**GitHub:**

-   Report issues: https://github.com/TLimoges33/Syn_OS/issues
-   Discussions: https://github.com/TLimoges33/Syn_OS/discussions

---

## 📜 License

ALFRED is part of SynOS and is licensed under the MIT License.

---

**"At your service, sir."** - ALFRED
