# ALFRED Audio System - Quick Reference Card

**Version:** v1.1  
**Updated:** October 19, 2025

---

## 🚀 Quick Start (One Command)

```bash
./scripts/deploy-phase2.sh
```

This runs everything: setup, optimization, testing, and verification.

---

## 📋 Individual Commands

### Setup

```bash
# Install and configure PulseAudio
./scripts/audio/setup-pulseaudio.sh

# Optimize microphone for voice
./scripts/audio/optimize-microphone.sh

# Test audio system
./scripts/audio/test-audio-system.sh
```

### ALFRED

```bash
# Install ALFRED with dependencies
./scripts/install-alfred.sh

# Activate virtual environment
source venv/bin/activate

# Run ALFRED with audio optimization
python3 src/ai/alfred/alfred-daemon-v1.1.py
```

### Monitoring

```bash
# Watch for device changes
python3 scripts/audio/hotplug-monitor.py

# Check audio status
cd src/ai/alfred
python3 -c "from audio_manager import AudioManager; print(AudioManager().get_status_report())"
```

---

## 🎤 Voice Commands

### Wake Word

**Say:** "alfred"

### Security Tools

-   "alfred, launch nmap stealth scan"
-   "alfred, start metasploit"
-   "alfred, open wireshark"

### System Control

-   "alfred, system health"
-   "alfred, check for updates"
-   "alfred, open terminal as root"

### Applications

-   "alfred, open firefox"
-   "alfred, launch visual studio code"

### Files

-   "alfred, find my document"
-   "alfred, open downloads folder"

### Conversational

-   "alfred, what time is it?"
-   "alfred, what's the weather?"
-   "alfred, help"

---

## 🔧 Troubleshooting

### No Audio Detected

```bash
# Check PulseAudio is running
pactl info

# Restart PulseAudio
pulseaudio -k
pulseaudio --start

# List devices
pactl list sources short  # Microphones
pactl list sinks short    # Speakers
```

### Microphone Too Quiet

```bash
# Re-run optimization
./scripts/audio/optimize-microphone.sh

# Manual volume control
pactl set-source-volume @DEFAULT_SOURCE@ 80%
```

### Echo or Feedback

```bash
# Reload echo cancellation
pactl unload-module module-echo-cancel
pactl load-module module-echo-cancel aec_method=webrtc

# Or re-run setup
./scripts/audio/setup-pulseaudio.sh
```

### ALFRED Not Responding

```bash
# Check microphone is unmuted
pactl set-source-mute @DEFAULT_SOURCE@ 0

# Test recording
arecord -d 3 test.wav
aplay test.wav

# Check ALFRED logs
tail -f /var/log/synos/alfred.log
```

---

## 📊 Audio Settings

### Optimal Levels

| Device             | Volume | Status  |
| ------------------ | ------ | ------- |
| Microphone (Input) | 70%    | Unmuted |
| Speakers (Output)  | 75%    | Unmuted |

### Echo Cancellation

```
Method: WebRTC
Analog Gain Control: OFF
Digital Gain Control: ON
Noise Suppression: ON
Voice Detection: ON
```

### Sample Rate

-   **Recording:** 44.1kHz or 48kHz
-   **Bit Depth:** 16-bit
-   **Latency:** 10ms fragments

---

## 🗂️ File Locations

### Configuration

```
config/audio/pulseaudio-alfred.conf
```

### Scripts

```
scripts/audio/setup-pulseaudio.sh
scripts/audio/optimize-microphone.sh
scripts/audio/test-audio-system.sh
scripts/audio/hotplug-monitor.py
scripts/deploy-phase2.sh
```

### Code

```
src/ai/alfred/audio_manager.py
src/ai/alfred/alfred-daemon-v1.1.py
```

### Logs

```
/var/log/synos/alfred.log
```

---

## 🔍 Quick Diagnostics

### Test Checklist

```bash
# 1. PulseAudio running?
pactl info

# 2. Microphone detected?
pactl list sources short

# 3. Echo cancellation active?
pactl list modules | grep echo-cancel

# 4. Python libraries installed?
python3 -c "import speech_recognition; import pyaudio"

# 5. AudioManager working?
cd src/ai/alfred
python3 -c "from audio_manager import AudioManager; AudioManager().test_microphone()"

# 6. TTS working?
espeak -v en-gb+m3 "Test"
```

### Expected Output

All should return success (no errors). If any fail, re-run setup:

```bash
./scripts/deploy-phase2.sh
```

---

## 🎯 Performance Targets

| Metric            | Target | How to Check        |
| ----------------- | ------ | ------------------- |
| Latency           | <20ms  | Monitor during use  |
| Voice Accuracy    | >90%   | Test with commands  |
| Setup Time        | <2 min | Time the deployment |
| Echo Cancellation | Active | Check module list   |

---

## 📞 Quick Help

### Common Issues

1. **"ALFRED doesn't hear me"**

    - Run: `./scripts/audio/optimize-microphone.sh`
    - Check: Microphone is unmuted and at 70%

2. **"Background noise interferes"**

    - Verify: Echo cancellation is loaded
    - Run: `./scripts/audio/setup-pulseaudio.sh`

3. **"Audio quality is poor"**

    - Optimize: Re-run microphone calibration
    - Check: Sample rate is 44.1kHz or 48kHz

4. **"Device not detected"**
    - Monitor: `python3 scripts/audio/hotplug-monitor.py`
    - Manual: `pactl list sources short`

### Get Status

```bash
cd src/ai/alfred
python3 audio_manager.py
```

Shows:

-   All audio devices
-   Current volumes
-   Mute status
-   Default devices

---

## 💡 Tips & Tricks

### Best Practices

1. **Speak clearly** 1-2 feet from microphone
2. **Minimize noise** when giving commands
3. **Wait for beep** before speaking (if audio feedback enabled)
4. **Use consistent volume** for better recognition

### Advanced

```bash
# Set custom microphone volume
cd src/ai/alfred
python3 -c "from audio_manager import AudioManager; am = AudioManager(); devices = am.get_devices('SOURCE'); am.set_volume(devices[0], 80)"

# Monitor audio in real-time
pactl subscribe

# Check system audio stats
pactl stat
```

---

## 📚 Documentation

For detailed information, see:

-   `docs/04-user-guides/ALFRED-GUIDE.md` - Complete user guide
-   `docs/06-project-status/PHASE2-AUDIO-SUMMARY.md` - Technical deep dive
-   `docs/06-project-status/PHASE2-PROGRESS-REPORT.md` - Full report
-   `docs/06-project-status/V1.1-STATUS.md` - Current progress

---

## 🆘 Emergency Fixes

### Reset Audio to Defaults

```bash
# Backup current config
cp ~/.config/pulse/daemon.conf ~/.config/pulse/daemon.conf.bak

# Remove custom config
rm ~/.config/pulse/default.pa

# Restart PulseAudio
pulseaudio -k
pulseaudio --start

# Re-run setup
./scripts/audio/setup-pulseaudio.sh
```

### ALFRED Won't Start

```bash
# Check dependencies
./scripts/install-alfred.sh

# Activate environment
source venv/bin/activate

# Test import
python3 -c "import speech_recognition; import pyaudio; print('OK')"

# Run with debug
python3 src/ai/alfred/alfred-daemon-v1.1.py --verbose
```

---

**Need More Help?** Check the logs:

```bash
tail -f /var/log/synos/alfred.log
```

**Quick Test:**

```bash
./scripts/audio/test-audio-system.sh
```

---

**Phase 2 Audio Integration - Ready for Voice! 🎤**
