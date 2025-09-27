# SynOS Boot Graphics Specifications
# Professional cybersecurity boot experience assets

## GRUB Theme Assets Required

### Background Images
1. **background.png** (1920x1080, 1280x720, 1024x768 variants)
   - **Design**: Solid black background with subtle red neural network pattern
   - **Elements**: 
     - Faint red circuit traces in corners
     - Consciousness nodes connected by red lines
     - SynOS logo watermark (10% opacity) in bottom right
     - Gradient from pure black to very dark red at edges
   - **Style**: Professional, not distracting from menu text
   - **Format**: PNG with transparency support

2. **consciousness_logo.png** (64x64)
   - **Design**: SynOS consciousness symbol
   - **Elements**:
     - Neural network brain outline in red
     - Digital circuit patterns within brain shape
     - Pulsing effect-ready (multiple frames if animated)
   - **Colors**: Primary red (#FF0000), secondary dark red (#800000)
   - **Style**: Professional icon suitable for corporate environments

### Menu Elements
3. **menu_c.png, menu_e.png, menu_n.png, menu_ne.png, menu_nw.png, menu_s.png, menu_se.png, menu_sw.png, menu_w.png** (Menu border components)
   - **Design**: Cybersecurity-themed menu borders
   - **Style**: 
     - Black background with red borders
     - Subtle circuit trace patterns
     - Professional gradient effects
     - Corner pieces with consciousness motifs
   - **Dimensions**: Scalable 9-slice components

4. **select_c.png, select_e.png, etc.** (Selection highlight components)
   - **Design**: Red highlight overlay for selected menu items
   - **Style**:
     - Semi-transparent red overlay (#FF0000 at 30% opacity)
     - Subtle glow effect
     - Professional highlight that doesn't obscure text
   - **Behavior**: Smooth selection indication

5. **terminal_box_c.png, etc.** (Terminal window border)
   - **Design**: Terminal window styling for GRUB console
   - **Style**:
     - Black terminal background
     - Red border with cyber aesthetic
     - Monospace font compatibility
     - Professional appearance

## Plymouth Boot Splash Assets

### Logo Assets
6. **synos_logo.png** (256x256, 128x128, 64x64 variants)
   - **Design**: Main SynOS logo for boot splash
   - **Elements**:
     - "SYN_OS" text in cybersecurity font
     - Consciousness symbol integrated
     - Version indicator space
   - **Animation**: Pulsing/breathing effect ready
   - **Colors**: Red on transparent background

### Animation Elements
7. **neural_node.png** (8x8, 16x16 variants)
   - **Design**: Individual neural network nodes
   - **Style**: Red dots with subtle glow
   - **Usage**: Animated network connections during boot
   - **Variants**: Different intensities for animation frames

8. **connection_line.png** (Various lengths)
   - **Design**: Neural network connection lines
   - **Style**: Red lines with fade-in effect
   - **Usage**: Connecting nodes in consciousness visualization
   - **Animation**: Growing/pulsing connections

### Progress Elements
9. **progress_bar_bg.png** (600x8)
   - **Design**: Progress bar background
   - **Style**: Dark gray background with red border
   - **Professional**: Subtle but visible progress indication

10. **progress_bar_fg.png** (Variable width x 8)
    - **Design**: Progress bar foreground
    - **Style**: Red gradient fill
    - **Animation**: Smooth filling during boot process

## Boot Menu Text Styling

### Font Specifications
- **Primary Font**: Courier New (monospace for cybersecurity aesthetic)
- **Menu Title**: 20pt Bold, Red (#FF0000)
- **Menu Items**: 14pt Regular, White (#FFFFFF)
- **Selected Items**: 14pt Bold, Red (#FF0000)
- **Status Text**: 12pt Regular, Gray (#CCCCCC)
- **System Info**: 10pt Regular, Dark Red (#800000)

### Menu Item Icons
11. **boot_standard.png** (24x24)
    - Standard boot option icon
    - Computer with consciousness symbol

12. **boot_forensics.png** (24x24)
    - Digital forensics mode icon
    - Magnifying glass with digital elements

13. **boot_persistence.png** (24x24)
    - Persistence mode icon
    - Hard drive with save symbol

14. **boot_consciousness.png** (24x24)
    - Consciousness mode icon (recommended option)
    - Brain with neural network pattern

15. **boot_safe.png** (24x24)
    - Safe mode icon
    - Shield with warning symbol

16. **boot_emergency.png** (24x24)
    - Emergency mode icon
    - First aid cross with tools

## Color Specifications

### Primary Palette
- **Background**: Black (#000000)
- **Primary Accent**: Red (#FF0000)
- **Secondary Accent**: Dark Red (#800000)
- **Text Primary**: White (#FFFFFF)
- **Text Secondary**: Light Gray (#CCCCCC)
- **Text Tertiary**: Dark Gray (#808080)

### Status Colors
- **Success/Active**: Green (#00FF00)
- **Warning**: Yellow (#FFFF00)
- **Error**: Bright Red (#FF4444)
- **Info**: Cyan (#00FFFF)

### Transparency Effects
- **Menu Overlays**: 30% opacity
- **Backgrounds**: 80% opacity for readability
- **Highlights**: 50% opacity for selection
- **Watermarks**: 10% opacity for subtle branding

## Animation Specifications

### GRUB Animations
- **Logo Pulse**: 2-second cycle, breathing effect
- **Network Pattern**: Subtle flowing connections
- **Status Indicators**: Blinking for active states
- **Selection**: Smooth fade-in/out transitions

### Plymouth Animations
- **Consciousness Initialization**: 
  - Neural nodes appearing sequentially
  - Connections forming between nodes
  - Pulsing network activity
  - Progress bar with consciousness theme
- **Security Components**: 
  - Sequential activation display
  - Status checks with visual feedback
  - Component ready indicators
- **Boot Phases**:
  - Hardware initialization (red progress)
  - Kernel loading (neural network activation)
  - Services starting (component activation)
  - Ready state (full consciousness active)

## Professional Considerations

### Corporate Environment Compatibility
- **Subtle Branding**: Not overpowering or distracting
- **Professional Colors**: Dark theme suitable for business
- **Clear Text**: High contrast for readability
- **Quick Boot**: Animations don't delay boot process
- **Accessibility**: Color-blind friendly design

### Technical Requirements
- **Resolution Support**: 1920x1080, 1280x720, 1024x768
- **Color Depth**: 24-bit color minimum
- **File Formats**: PNG for images, standard fonts for text
- **Size Optimization**: Compressed images for faster loading
- **Compatibility**: Works with UEFI and Legacy BIOS

## Implementation Notes

### GRUB Theme Structure
```
/boot/grub/themes/synos/
├── theme.txt
├── background.png
├── consciousness_logo.png
├── menu_*.png (9-slice components)
├── select_*.png (selection highlights)
├── terminal_box_*.png
└── icons/
    ├── boot_standard.png
    ├── boot_forensics.png
    ├── boot_persistence.png
    ├── boot_consciousness.png
    ├── boot_safe.png
    └── boot_emergency.png
```

### Plymouth Theme Structure
```
/usr/share/plymouth/themes/synos/
├── synos.plymouth
├── synos.script
├── synos_logo.png
├── neural_node.png
├── connection_line.png
├── progress_bar_bg.png
└── progress_bar_fg.png
```

This comprehensive boot experience provides a professional, cybersecurity-focused first impression that reinforces the SynOS brand while maintaining usability and corporate appropriateness.
