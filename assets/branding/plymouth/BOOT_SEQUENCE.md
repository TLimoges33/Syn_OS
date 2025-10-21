# SynOS Boot Sequence Design

**Theme:** True Black + Scarlet + White
**Style:** Organic Neural → Cyberpunk Hacker Transition
**Created:** October 19, 2025

---

## Color Palette

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **True Black** | `#000000` | `0, 0, 0` | Backgrounds, primary surfaces |
| **Scarlet** | `#DC143C` | `220, 20, 60` | Primary accents, logo, progress |
| **Bright Scarlet** | `#FF2400` | `255, 36, 0` | High-contrast elements, gradients |
| **White** | `#FFFFFF` | `255, 255, 255` | Text, details, highlights |
| **Gray** | `#E0E0E0` | `224, 224, 224` | Secondary text |

---

## Boot Sequence Flow

### Complete Boot Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BIOS/UEFI POST                                           │
│    • Hardware initialization                                │
│    • Memory check                                           │
│    • Boot device detection                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. GRUB Bootloader                                          │
│    • SynOS themed menu                                      │
│    • Black background + Scarlet highlights                  │
│    • Options: SynOS, Advanced, Recovery                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Kernel Loading                                           │
│    • Brief kernel boot messages                             │
│    • Transition to Plymouth                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PLYMOUTH SPLASH - PHASE 1 (0-3 seconds)                  │
│    ╔═════════════════════════════════════════════════════╗  │
│    ║ ORGANIC NEURAL NETWORK                              ║  │
│    ║                                                     ║  │
│    ║  • True black background                           ║  │
│    ║  • Pulsing scarlet neural nodes                    ║  │
│    ║  • Flowing white connection lines                  ║  │
│    ║  • Organic, biological movement                    ║  │
│    ║  • SynOS logo fading in (transparency → opaque)    ║  │
│    ║                                                     ║  │
│    ║  Upper Right Corner:                               ║  │
│    ║  ┌─────────────────────────────────────┐           ║  │
│    ║  │ [  0.123] Loading kernel modules... │ ← 15 line ║  │
│    ║  │ [  0.456] Initializing hardware...  │   boot    ║  │
│    ║  │ [  0.789] Starting services...      │   log     ║  │
│    ║  │ ...                                 │   display ║  │
│    ║  └─────────────────────────────────────┘           ║  │
│    ╚═════════════════════════════════════════════════════╝  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. PLYMOUTH SPLASH - PHASE 2 (3s - boot complete)          │
│    ╔═════════════════════════════════════════════════════╗  │
│    ║ CYBERPUNK HACKER THEME                              ║  │
│    ║                                                     ║  │
│    ║  • SynOS logo now FULLY OPAQUE (scarlet on black)  ║  │
│    ║  • Neural nodes fade out                           ║  │
│    ║  • Sharp geometric cyberpunk elements appear:      ║  │
│    ║    - Horizontal scanning lines (scarlet)           ║  │
│    ║    - Matrix-style code rain (0s and 1s)            ║  │
│    ║    - Digital glitch effects                        ║  │
│    ║                                                     ║  │
│    ║  Center: SynOS Logo (scarlet + white)              ║  │
│    ║  Below: ▬▬▬▬▬▬▬▬▬▬ (scarlet progress bar)          ║  │
│    ║                                                     ║  │
│    ║  Upper Right: Boot log continues (white text)      ║  │
│    ╚═════════════════════════════════════════════════════╝  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Display Manager (LightDM)                                │
│    • Login screen with SynOS theme                          │
│    • Black background + scarlet accents                     │
│    • User selection and password entry                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Desktop Environment (MATE)                               │
│    • SynOS neural-cyber wallpaper                           │
│    • Black + scarlet + white theme throughout               │
│    • AI consciousness dashboard active                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Organic Neural (0-3 seconds)

### Visual Elements

**Neural Network Visualization:**
- 20 pulsing scarlet nodes (●) scattered across screen
- Organic, flowing movement (not rigid)
- Biological pulsing effect (using sine wave)
- White connection lines between nodes (optional, not in current script)

**Logo Animation:**
- SynOS logo starts at 0% opacity (transparent)
- Fades in linearly over 3 seconds
- Positioned in screen center
- Scarlet and white colors

**Boot Log:**
- Upper right corner (600px from right, 20px from top)
- 15 lines visible at a time
- White monospace text on black background
- Shows real boot messages from kernel/systemd
- Lines scroll up as new messages appear

### Animation Characteristics

- **Organic**: Smooth, flowing, biological
- **Gentle pulsing**: Neural nodes breathe (sine wave animation)
- **Soft movement**: Particles drift slowly
- **Fade transitions**: No harsh cuts

---

## Phase 2: Cyberpunk Hacker (3+ seconds)

### Visual Elements

**Logo:**
- Now at 100% opacity (fully opaque)
- No longer animating
- Remains centered

**Scanning Lines:**
- 3 horizontal scarlet lines
- Move from top to bottom at different speeds
- Create "scanning" effect
- 30% opacity
- Blur/glow effect

**Matrix Code Rain:**
- 30 particles falling from top
- Random "0" and "1" characters
- Scarlet color
- Different fall speeds for depth
- Reset to top when reaching bottom

**Progress Bar:**
- Positioned below logo (center-bottom)
- 400px wide × 4px tall
- Background: Dark gray (#333333)
- Foreground: Scarlet gradient with glow
- Fills left-to-right based on actual boot progress

**Boot Log:**
- Continues in upper right corner
- Same format as Phase 1
- Provides technical feedback

### Animation Characteristics

- **Sharp**: Geometric, precise movements
- **Digital**: Matrix effects, code rain
- **Glitch effects**: (Future enhancement)
- **Scanning**: Horizontal line sweeps

---

## Boot Log Display

### Technical Implementation

**Position:**
- X: `screen_width - 600` (600px from right edge)
- Y: `20` (20px from top)
- Z-order: `15000` (always on top)

**Format:**
- Font: Monospace 10pt
- Color: White (#FFFFFF)
- Opacity: 90%
- Max lines: 15
- Line height: 18px

**Message Sources:**
- Kernel boot messages (dmesg)
- Systemd service starts
- Hardware initialization
- Filesystem checks
- Network setup

**Behavior:**
- FIFO queue (First In, First Out)
- Oldest messages scroll off top
- New messages appear at bottom
- Messages include timestamps: `[ 0.123]`

### Example Log Output

```
[  0.000123] Initializing cgroup subsys cpuset
[  0.000456] Linux version 6.5.0-synos...
[  0.001234] Command line: BOOT_IMAGE=/boot/vmlinuz...
[  0.012345] x86/fpu: Supporting XSAVE feature 0x001
[  0.023456] ACPI: Core revision 20230628
[  0.098765] Freeing SMP alternatives memory
[  0.123456] smpboot: CPU0: Intel Core i7 (family: 0x6)
[  1.234567] Starting SynOS AI Consciousness...
[  1.345678] Loading neural network models...
[  1.456789] Initializing security framework...
[  2.567890] Mounting filesystems...
[  2.678901] Starting network services...
[  3.789012] Activating AI daemon...
[  4.890123] Desktop environment ready
[  5.901234] Boot complete
```

---

## Plymouth Theme Files

### Directory Structure

```
/usr/share/plymouth/themes/synos-neural-cyber/
├── synos-neural-cyber.plymouth     # Theme metadata
├── synos-neural-cyber.script       # Animation logic (480+ lines)
├── synos-logo-256.png              # Main logo (scarlet on black)
├── scan-line.png                   # Horizontal scanning line
├── progress-bg.png                 # Progress bar background
├── progress-fg.png                 # Progress bar foreground (scarlet gradient)
├── neural-node.png                 # Neural node dot (optional)
└── create-assets.sh                # Asset generator script
```

### Installation Commands

```bash
# Copy theme to system
sudo cp -r assets/branding/plymouth/synos-neural-cyber \
    /usr/share/plymouth/themes/

# Set as default theme
sudo plymouth-set-default-theme synos-neural-cyber

# Update initramfs to include theme
sudo update-initramfs -u

# Test theme (requires Plymouth)
sudo plymouthd --debug --debug-file=/tmp/plymouth-debug.log
sudo plymouth --show-splash
# ... wait a few seconds to see both phases ...
sudo plymouth --quit
```

---

## GRUB Theme Integration

### GRUB Configuration

**File:** `/boot/grub/themes/synos/theme.txt`

```
# SynOS GRUB Theme
# True Black + Scarlet + White

# Background
desktop-image: "synos-grub-16x9.png"
desktop-color: "#000000"

# Title text
title-text: "SynOS - Neural Consciousness Operating System"
title-color: "#DC143C"  # Scarlet
title-font: "DejaVu Sans Bold 20"

# Menu
+ boot_menu {
    left = 15%
    top = 35%
    width = 70%
    height = 50%

    item_color = "#FFFFFF"           # White
    selected_item_color = "#DC143C"  # Scarlet
    item_font = "DejaVu Sans 16"
    item_height = 32
    item_padding = 8
    item_spacing = 4

    selected_item_pixmap_style = "select_*.png"
}

# Progress bar
+ progress_bar {
    id = "__timeout__"
    left = 15%
    top = 85%
    width = 70%
    height = 20

    fg_color = "#DC143C"  # Scarlet
    bg_color = "#333333"  # Dark gray
    border_color = "#FFFFFF"  # White

    text = "@TIMEOUT_NOTIFICATION_SHORT@"
    text_color = "#FFFFFF"
    font = "DejaVu Sans 12"
}
```

---

## Desktop Theme Continuation

After Plymouth → LightDM → MATE Desktop, the theme continues:

### Wallpaper
- **Primary:** `synos-neural-dark.jpg` (black background, scarlet neural network)
- **Alternate:** `synos-cyber-grid.jpg` (cyberpunk grid, scarlet accents)

### Window Manager Theme
- **Borders:** Thin, black with scarlet highlights
- **Title bars:** Black background, scarlet active, white text
- **Buttons:** Minimalist, scarlet on hover

### Panel Theme
- **Background:** True black with 90% opacity
- **Icons:** White with scarlet accents
- **System tray:** Scarlet indicators for alerts

### Application Theme (GTK)
- **Primary color:** Scarlet (#DC143C)
- **Background:** Black (#000000)
- **Text:** White (#FFFFFF)
- **Accent:** Bright scarlet (#FF2400)

---

## Future Enhancements

### Audio Integration (Planned)

**Phase 1 (Organic Neural):**
- Soft ambient drone
- Subtle neural "pulse" sounds
- Gentle, organic audio texture

**Phase 2 (Cyberpunk):**
- Digital beeps/chirps
- Matrix-style "data stream" sounds
- Sharp, electronic audio

**Transition:**
- Smooth crossfade between audio themes
- Synchronized with visual transition at 3s mark

### Advanced Visual Effects

1. **Glitch Transitions:**
   - RGB split effects
   - Scanline artifacts
   - Digital corruption visuals

2. **Neural Network Lines:**
   - Draw white lines between nearby nodes
   - Pulsing connection strength
   - Organic flow animation

3. **3D Depth:**
   - Parallax scrolling layers
   - Depth-based blur
   - Z-axis particle movement

4. **Particle Systems:**
   - More complex neural activity
   - Cyberpunk data streams
   - Procedural visual generation

---

## Testing & Debugging

### Test in QEMU

```bash
# Build ISO with Plymouth theme
sudo lb build

# Boot in QEMU to see boot splash
qemu-system-x86_64 \
    -cdrom live-image-amd64.hybrid.iso \
    -m 4096 \
    -smp 2 \
    -enable-kvm \
    -vga std
```

### Debug Plymouth

```bash
# Enable debug logging
sudo plymouth --debug

# View debug output
sudo plymouth --debug-file=/tmp/plymouth.log

# Check theme syntax
sudo plymouth-set-default-theme --list
sudo plymouth-set-default-theme synos-neural-cyber --rebuild-initrd
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Theme not appearing | Rebuild initramfs: `sudo update-initramfs -u` |
| Assets not loading | Check paths in .plymouth file |
| Script errors | Check syntax: `/usr/share/plymouth/themes/synos-neural-cyber/synos-neural-cyber.script` |
| Boot messages not showing | Verify `/etc/default/grub` has `quiet splash` removed for testing |

---

## Implementation Status

- [x] Color palette defined (Black, Scarlet, White)
- [x] Plymouth script created (480+ lines, dual-phase animation)
- [x] Visual assets generated (logo, progress bars, scan lines)
- [x] Boot log display configured (upper right, 15 lines)
- [x] Phase 1 animation (organic neural network)
- [x] Phase 2 animation (cyberpunk hacker)
- [x] Logo fade-in transition
- [x] Documentation complete
- [ ] GRUB theme integration (assets exist, config needed)
- [ ] LightDM theme (needs styling)
- [ ] GTK theme (MATE desktop customization)
- [ ] Audio integration (planned)
- [ ] Testing in live environment
- [ ] ISO build integration

---

**Next Steps:**

1. ✅ Copy Plymouth theme to ISO build: `config/includes.chroot/usr/share/plymouth/themes/`
2. Configure GRUB theme in ISO
3. Test boot sequence in VM
4. Refine animations based on visual feedback
5. Add audio layer (future release)

---

**Created:** October 19, 2025
**Designer:** SynOS Development Team
**Status:** Visual implementation complete, testing pending
