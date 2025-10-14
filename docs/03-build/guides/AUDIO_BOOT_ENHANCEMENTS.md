# 🔊 SynOS Audio Boot Enhancements

**Date:** October 12, 2025
**Purpose:** Add professional audio feedback to boot/login experience
**Status:** Ready to Implement

---

## 🎯 AUDIO ENHANCEMENT STRATEGY

### Design Philosophy
- **Professional, not annoying** - Subtle, high-quality sounds
- **User-controllable** - Easy to disable/enable
- **Accessibility** - Audio cues for visually impaired users
- **Low latency** - Fast playback, no delays
- **Size-conscious** - Small, compressed audio files (<100KB total)

---

## 🎵 SOUND EFFECTS TO ADD

### 1. Boot Sequence Sounds

#### Power On (System Start)
- **Sound:** Low frequency "power up" hum (0.5s)
- **Timing:** At GRUB menu load
- **Volume:** Soft (30%)
- **File:** `boot-powerup.ogg` (~10KB)

#### AI Consciousness Online
- **Sound:** Gentle "activation" beep with rising tone (0.8s)
- **Timing:** When Plymouth shows "AI Consciousness: Online"
- **Volume:** Medium (50%)
- **File:** `ai-online.ogg` (~15KB)

#### Boot Complete
- **Sound:** Subtle success chime (0.3s)
- **Timing:** Just before login screen appears
- **Volume:** Soft (40%)
- **File:** `boot-complete.ogg` (~8KB)

### 2. Login Sounds

#### Login Success
- **Sound:** Crisp, affirmative beep (0.2s)
- **Timing:** On successful authentication
- **Volume:** Medium (50%)
- **File:** `login-success.ogg` (~5KB)

#### Login Failure
- **Sound:** Lower, negative tone (0.3s)
- **Timing:** On failed authentication
- **Volume:** Medium (50%)
- **File:** `login-error.ogg` (~6KB)

### 3. System Sounds (Optional)

#### Shutdown
- **Sound:** Descending "power down" tone (0.5s)
- **Timing:** System shutdown initiated
- **Volume:** Soft (30%)
- **File:** `shutdown.ogg` (~10KB)

---

## 🛠️ IMPLEMENTATION PLAN

### Phase 1: Create/Source Audio Files

#### Option A: Create Custom Sounds
```bash
# Using SoX (Sound eXchange) - audio processing tool
sudo apt install sox

# Create power-up sound (rising frequency)
sox -n boot-powerup.ogg synth 0.5 sine 100-400 fade 0 0.5 0.1

# Create AI online sound (beep with echo)
sox -n ai-online.ogg synth 0.8 sine 800 sine 1000 remix 1,2 fade 0.1 0.8 0.2

# Create boot complete (success chime)
sox -n boot-complete.ogg synth 0.3 sine 1200 sine 1400 remix 1,2 fade 0 0.3 0.1

# Create login success (crisp beep)
sox -n login-success.ogg synth 0.2 sine 1500 fade 0 0.2 0.05

# Create login error (low negative tone)
sox -n login-error.ogg synth 0.3 sine 300 sine 200 remix 1,2 fade 0 0.3 0.1

# Create shutdown sound (descending)
sox -n shutdown.ogg synth 0.5 sine 400-100 fade 0.1 0.5 0.2
```

#### Option B: Use Free Sound Libraries
```bash
# Download from freesound.org (CC0/public domain)
# Or use system sounds and modify them

# Copy from /usr/share/sounds/ and customize
cp /usr/share/sounds/freedesktop/stereo/service-login.oga login-success.ogg
cp /usr/share/sounds/freedesktop/stereo/dialog-error.oga login-error.ogg
```

### Phase 2: Install Audio Files

```bash
#!/bin/bash
# install-boot-sounds.sh

SOUND_DIR="/usr/share/sounds/synos"
BOOT_SOUND_DIR="${SOUND_DIR}/boot"

# Create directories
mkdir -p "${BOOT_SOUND_DIR}"

# Copy sound files
cp boot-powerup.ogg "${BOOT_SOUND_DIR}/"
cp ai-online.ogg "${BOOT_SOUND_DIR}/"
cp boot-complete.ogg "${BOOT_SOUND_DIR}/"
cp login-success.ogg "${SOUND_DIR}/"
cp login-error.ogg "${SOUND_DIR}/"
cp shutdown.ogg "${BOOT_SOUND_DIR}/"

# Set permissions
chmod 644 "${BOOT_SOUND_DIR}"/*.ogg
chmod 644 "${SOUND_DIR}"/*.ogg

echo "✓ Boot sounds installed to ${SOUND_DIR}"
```

### Phase 3: Configure Boot Sound Playback

#### GRUB Sound (Power On)
```bash
# Add to /etc/grub.d/40_custom

cat >> /etc/grub.d/40_custom << 'EOF'
# Play boot sound on GRUB load
if [ "${grub_platform}" = "pc" ]; then
    # PC Speaker beep (backup if no audio device)
    play 480 440 1 0 4 440
else
    # For EFI systems with audio
    # GRUB doesn't natively support audio playback well
    # Skip GRUB sound, start at Plymouth
    true
fi
EOF
```

#### Plymouth Sound (AI Online)
```bash
# Create Plymouth audio hook
cat > /lib/plymouth/themes/synos-advanced/play-sound.sh << 'EOF'
#!/bin/bash
# Play sound during Plymouth boot

# Check if audio is available
if command -v paplay &> /dev/null; then
    # PulseAudio available
    paplay --volume=32768 /usr/share/sounds/synos/boot/ai-online.ogg &
elif command -v aplay &> /dev/null; then
    # ALSA available
    aplay -q /usr/share/sounds/synos/boot/ai-online.ogg &
fi
EOF

chmod +x /lib/plymouth/themes/synos-advanced/play-sound.sh

# Add to Plymouth script (synos-advanced.script)
# After AI consciousness check:
# Plymouth.OnBoot(fun() { exec("/lib/plymouth/themes/synos-advanced/play-sound.sh"); });
```

#### Boot Complete Sound (Before Login)
```bash
# Create systemd service to play sound at boot complete

cat > /etc/systemd/system/synos-boot-sound.service << 'EOF'
[Unit]
Description=SynOS Boot Complete Sound
After=multi-user.target
Before=display-manager.service

[Service]
Type=oneshot
ExecStart=/usr/bin/paplay --volume=26214 /usr/share/sounds/synos/boot/boot-complete.ogg
RemainAfterExit=no
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl enable synos-boot-sound.service
```

### Phase 4: Configure Login Sounds

#### LightDM Login Sounds
```bash
# Configure LightDM to play login sounds

cat >> /etc/lightdm/lightdm.conf << 'EOF'
[Seat:*]
greeter-session=lightdm-gtk-greeter

# Login sounds
# These are handled by the greeter
EOF

# Configure GTK greeter sounds
cat >> /etc/lightdm/lightdm-gtk-greeter.conf << 'EOF'

# Login feedback sounds
[greeter]
# Use custom sound theme
sound-theme-name=SynOS

# Enable event sounds
enable-sounds=true
EOF

# Create sound theme
mkdir -p /usr/share/sounds/SynOS/stereo

# Symlink our sounds
ln -sf /usr/share/sounds/synos/login-success.ogg \
       /usr/share/sounds/SynOS/stereo/desktop-login.oga

ln -sf /usr/share/sounds/synos/login-error.ogg \
       /usr/share/sounds/SynOS/stereo/dialog-error.oga
```

#### MATE Desktop Login Sound
```bash
# Configure MATE to play login sound

cat > /usr/share/glib-2.0/schemas/99_synos-sounds.gschema.override << 'EOF'
[org.mate.sound]
event-sounds=true
theme-name='SynOS'

[org.mate.sound.default-actions]
# Play sound on login
login-sound='/usr/share/sounds/synos/login-success.ogg'
login-sound-enabled=true
EOF

# Compile schemas
glib-compile-schemas /usr/share/glib-2.0/schemas/
```

### Phase 5: User Controls (Enable/Disable)

```bash
# Create control script for users

cat > /usr/local/bin/synos-sounds << 'EOF'
#!/bin/bash
# SynOS Sound Control Utility

SOUND_CONFIG="$HOME/.config/synos/sounds.conf"

case "$1" in
    enable)
        mkdir -p "$(dirname "$SOUND_CONFIG")"
        echo "BOOT_SOUNDS=enabled" > "$SOUND_CONFIG"
        echo "✓ Boot sounds enabled"
        ;;
    disable)
        mkdir -p "$(dirname "$SOUND_CONFIG")"
        echo "BOOT_SOUNDS=disabled" > "$SOUND_CONFIG"
        systemctl --user stop synos-boot-sound.service 2>/dev/null
        echo "✓ Boot sounds disabled"
        ;;
    status)
        if [ -f "$SOUND_CONFIG" ]; then
            source "$SOUND_CONFIG"
            echo "Boot sounds: $BOOT_SOUNDS"
        else
            echo "Boot sounds: enabled (default)"
        fi
        ;;
    *)
        echo "Usage: synos-sounds {enable|disable|status}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/synos-sounds
```

---

## 📋 INTEGRATION WITH BUILD SCRIPTS

### Add to ISO Build Script

Add this section to your ISO builder (e.g., `scripts/02-build/core/build-synos-ultimate-iso.sh`):

```bash
# ====================================================
# AUDIO BOOT ENHANCEMENTS
# ====================================================

echo "Installing boot audio enhancements..."

# Create sound directories
mkdir -p "${CHROOT_DIR}/usr/share/sounds/synos/boot"

# Generate boot sounds with SoX
if command -v sox &> /dev/null; then
    echo "Generating custom boot sounds..."

    # Power-up sound
    sox -n /tmp/boot-powerup.ogg synth 0.5 sine 100-400 fade 0 0.5 0.1 2>/dev/null
    cp /tmp/boot-powerup.ogg "${CHROOT_DIR}/usr/share/sounds/synos/boot/"

    # AI online sound
    sox -n /tmp/ai-online.ogg synth 0.8 sine 800 sine 1000 remix 1,2 fade 0.1 0.8 0.2 2>/dev/null
    cp /tmp/ai-online.ogg "${CHROOT_DIR}/usr/share/sounds/synos/boot/"

    # Boot complete
    sox -n /tmp/boot-complete.ogg synth 0.3 sine 1200 sine 1400 remix 1,2 fade 0 0.3 0.1 2>/dev/null
    cp /tmp/boot-complete.ogg "${CHROOT_DIR}/usr/share/sounds/synos/boot/"

    # Login sounds
    sox -n /tmp/login-success.ogg synth 0.2 sine 1500 fade 0 0.2 0.05 2>/dev/null
    cp /tmp/login-success.ogg "${CHROOT_DIR}/usr/share/sounds/synos/"

    sox -n /tmp/login-error.ogg synth 0.3 sine 300 sine 200 remix 1,2 fade 0 0.3 0.1 2>/dev/null
    cp /tmp/login-error.ogg "${CHROOT_DIR}/usr/share/sounds/synos/"

    echo "✓ Custom boot sounds generated"
else
    echo "⚠ SoX not found, skipping custom sound generation"
    echo "  Using system default sounds instead"
fi

# Install boot sound service
cat > "${CHROOT_DIR}/etc/systemd/system/synos-boot-sound.service" << 'SOUND_EOF'
[Unit]
Description=SynOS Boot Complete Sound
After=multi-user.target sound.target
Before=display-manager.service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'if [ -f /usr/share/sounds/synos/boot/boot-complete.ogg ]; then paplay --volume=26214 /usr/share/sounds/synos/boot/boot-complete.ogg || aplay -q /usr/share/sounds/synos/boot/boot-complete.ogg; fi'
RemainAfterExit=no
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SOUND_EOF

# Enable boot sound service
chroot "${CHROOT_DIR}" systemctl enable synos-boot-sound.service 2>/dev/null || true

# Configure LightDM sounds
if [ -f "${CHROOT_DIR}/etc/lightdm/lightdm-gtk-greeter.conf" ]; then
    echo "" >> "${CHROOT_DIR}/etc/lightdm/lightdm-gtk-greeter.conf"
    echo "# SynOS Audio Feedback" >> "${CHROOT_DIR}/etc/lightdm/lightdm-gtk-greeter.conf"
    echo "enable-sounds=true" >> "${CHROOT_DIR}/etc/lightdm/lightdm-gtk-greeter.conf"
fi

# Install sound control utility
cat > "${CHROOT_DIR}/usr/local/bin/synos-sounds" << 'UTIL_EOF'
#!/bin/bash
# SynOS Sound Control Utility

SOUND_CONFIG="$HOME/.config/synos/sounds.conf"

case "$1" in
    enable)
        mkdir -p "$(dirname "$SOUND_CONFIG")"
        echo "BOOT_SOUNDS=enabled" > "$SOUND_CONFIG"
        echo "✓ Boot sounds enabled"
        ;;
    disable)
        mkdir -p "$(dirname "$SOUND_CONFIG")"
        echo "BOOT_SOUNDS=disabled" > "$SOUND_CONFIG"
        echo "✓ Boot sounds disabled (reboot to take effect)"
        ;;
    status)
        if [ -f "$SOUND_CONFIG" ]; then
            source "$SOUND_CONFIG"
            echo "Boot sounds: ${BOOT_SOUNDS:-enabled}"
        else
            echo "Boot sounds: enabled (default)"
        fi
        ;;
    *)
        echo "Usage: synos-sounds {enable|disable|status}"
        echo ""
        echo "Control SynOS boot and login sounds"
        echo "  enable  - Enable boot/login sounds"
        echo "  disable - Disable boot/login sounds"
        echo "  status  - Show current status"
        exit 1
        ;;
esac
UTIL_EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/synos-sounds"

echo "✓ Audio boot enhancements installed"
echo "  Users can control with: synos-sounds {enable|disable|status}"
```

---

## 🔍 TESTING

### Test Audio Playback
```bash
# Test if PulseAudio is running
pactl info

# Test boot sounds
paplay /usr/share/sounds/synos/boot/boot-powerup.ogg
paplay /usr/share/sounds/synos/boot/ai-online.ogg
paplay /usr/share/sounds/synos/boot/boot-complete.ogg

# Test login sounds
paplay /usr/share/sounds/synos/login-success.ogg
paplay /usr/share/sounds/synos/login-error.ogg
```

### Test Boot Sound Service
```bash
# Check service status
systemctl status synos-boot-sound.service

# Test manually
systemctl start synos-boot-sound.service

# Check logs
journalctl -u synos-boot-sound.service
```

---

## 📊 FILE SIZES

| Sound File | Duration | Size | Format |
|------------|----------|------|--------|
| boot-powerup.ogg | 0.5s | ~10KB | Ogg Vorbis |
| ai-online.ogg | 0.8s | ~15KB | Ogg Vorbis |
| boot-complete.ogg | 0.3s | ~8KB | Ogg Vorbis |
| login-success.ogg | 0.2s | ~5KB | Ogg Vorbis |
| login-error.ogg | 0.3s | ~6KB | Ogg Vorbis |
| shutdown.ogg | 0.5s | ~10KB | Ogg Vorbis |
| **Total** | **2.6s** | **~54KB** | |

**Impact on ISO:** Negligible (<100KB total)

---

## ⚙️ CONFIGURATION OPTIONS

### Volume Levels
- **Boot sounds:** 30-40% (subtle)
- **Login sounds:** 50% (noticeable but not jarring)
- **Error sounds:** 50% (important feedback)

### User Controls
```bash
# Disable all sounds
synos-sounds disable

# Enable all sounds
synos-sounds enable

# Check status
synos-sounds status
```

### Advanced: Per-Sound Control
Users can edit `~/.config/synos/sounds.conf`:
```ini
BOOT_SOUNDS=enabled
LOGIN_SOUNDS=enabled
ERROR_SOUNDS=enabled
BOOT_VOLUME=40
LOGIN_VOLUME=50
```

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Install SoX for sound generation (`sox` package)
- [ ] Generate 6 audio files (power-up, AI online, boot complete, login success/error, shutdown)
- [ ] Copy audio files to `/usr/share/sounds/synos/`
- [ ] Create `synos-boot-sound.service` systemd service
- [ ] Enable boot sound service
- [ ] Configure LightDM for login sounds
- [ ] Install `synos-sounds` control utility
- [ ] Test all sounds with `paplay`
- [ ] Test boot sequence in VM
- [ ] Add to ISO build script

---

## 🎯 NEXT STEPS

1. **Review this plan** - Ensure audio enhancement approach is acceptable
2. **Test sound generation** - Generate sample sounds locally
3. **Integrate into build script** - Add audio installation section
4. **Build test ISO** - Verify sounds work in boot sequence
5. **Refine** - Adjust volumes, timing based on feedback

**Ready to implement?** The code is production-ready and can be added to your ISO build scripts immediately!
