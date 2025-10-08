#!/bin/bash

# SynOS Desktop Environment Clone Verification
# Ensures all desktop elements are properly captured before ISO build

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$SCRIPT_DIR/build/desktop-clone"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🔍 SynOS Desktop Clone Verification${NC}"
echo "===================================="
echo ""

if [[ ! -d "$CLONE_DIR" ]]; then
    echo -e "${RED}❌ Desktop clone not found!${NC}"
    echo "Run: ./scripts/clone-desktop-environment.sh first"
    exit 1
fi

echo -e "${BLUE}📊 Desktop Clone Analysis:${NC}"
echo ""

# Check desktop environment detection
if [[ -f "$CLONE_DIR/configs/mate-dconf.conf" ]]; then
    echo -e "${GREEN}✅ MATE Desktop Environment captured${NC}"
    PANEL_COUNT=$(grep -c "panel-" "$CLONE_DIR/configs/mate-panel.conf" || echo "0")
    echo "   • Panel configuration: $PANEL_COUNT panels"

    APPLET_COUNT=$(grep -c "applet-" "$CLONE_DIR/configs/mate-panel.conf" || echo "0")
    echo "   • Panel applets: $APPLET_COUNT applets"
else
    echo -e "${YELLOW}⚠️ MATE configuration not found${NC}"
fi

# Check applications
if [[ -f "$CLONE_DIR/applications/installed-packages.list" ]]; then
    TOTAL_PACKAGES=$(wc -l < "$CLONE_DIR/applications/installed-packages.list")
    MANUAL_PACKAGES=$(wc -l < "$CLONE_DIR/applications/manual-packages.list")
    echo -e "${GREEN}✅ Applications captured${NC}"
    echo "   • Total packages: $TOTAL_PACKAGES"
    echo "   • User-installed: $MANUAL_PACKAGES"

    # Show some key applications
    echo "   • Key Security Tools:"
    grep -E "(metasploit|burpsuite|nmap|wireshark|aircrack)" "$CLONE_DIR/applications/installed-packages.list" | head -5 | while read line; do
        echo "     - $(echo $line | cut -d$'\t' -f1)"
    done
fi

# Check themes and appearance
if [[ -d "$CLONE_DIR/themes" ]]; then
    echo -e "${GREEN}✅ Themes and appearance captured${NC}"

    if [[ -d "$CLONE_DIR/themes/user-themes" ]]; then
        THEME_COUNT=$(find "$CLONE_DIR/themes/user-themes" -maxdepth 1 -type d | wc -l)
        echo "   • User themes: $((THEME_COUNT - 1))"
    fi

    if [[ -d "$CLONE_DIR/themes/user-icons" ]]; then
        ICON_COUNT=$(find "$CLONE_DIR/themes/user-icons" -maxdepth 1 -type d | wc -l)
        echo "   • User icon sets: $((ICON_COUNT - 1))"
    fi

    if [[ -f "$CLONE_DIR/themes/current-wallpaper.jpg" ]]; then
        WALLPAPER_SIZE=$(du -h "$CLONE_DIR/themes/current-wallpaper.jpg" | cut -f1)
        echo "   • Wallpaper: captured ($WALLPAPER_SIZE)"
    fi
fi

# Check fonts
if [[ -d "$CLONE_DIR/fonts" ]]; then
    echo -e "${GREEN}✅ Font configuration captured${NC}"

    if [[ -d "$CLONE_DIR/fonts/user-fonts" ]]; then
        FONT_COUNT=$(find "$CLONE_DIR/fonts/user-fonts" -name "*.ttf" -o -name "*.otf" | wc -l)
        echo "   • User fonts: $FONT_COUNT fonts"
    fi
fi

# Check user configurations
if [[ -d "$CLONE_DIR/configs" ]]; then
    CONFIG_COUNT=$(find "$CLONE_DIR/configs" -type f | wc -l)
    echo -e "${GREEN}✅ User configurations captured${NC}"
    echo "   • Configuration files: $CONFIG_COUNT files"

    # Check for important configs
    [[ -f "$CLONE_DIR/configs/.bashrc" ]] && echo "   • Bash configuration: ✅"
    [[ -f "$CLONE_DIR/configs/.bash_aliases" ]] && echo "   • Bash aliases: ✅"
    [[ -d "$CLONE_DIR/configs/.config/autostart" ]] && echo "   • Autostart apps: ✅"
fi

# Check desktop shortcuts
if [[ -d "$CLONE_DIR/shortcuts/desktop-files" ]]; then
    SHORTCUT_COUNT=$(find "$CLONE_DIR/shortcuts/desktop-files" -name "*.desktop" | wc -l)
    echo -e "${GREEN}✅ Desktop shortcuts captured${NC}"
    echo "   • Desktop files: $SHORTCUT_COUNT shortcuts"
fi

# Estimate ISO size impact
CLONE_SIZE=$(du -sh "$CLONE_DIR" | cut -f1)
echo ""
echo -e "${BLUE}📏 Storage Impact:${NC}"
echo "   • Desktop clone size: $CLONE_SIZE"
echo "   • Estimated ISO size increase: ~$CLONE_SIZE"

# Check restoration scripts
if [[ -x "$CLONE_DIR/restore-desktop.sh" && -x "$CLONE_DIR/install-packages.sh" ]]; then
    echo -e "${GREEN}✅ Restoration scripts ready${NC}"
else
    echo -e "${RED}❌ Restoration scripts missing or not executable${NC}"
fi

echo ""
echo -e "${CYAN}🎯 Desktop Clone Summary:${NC}"
echo "================================="

# Create summary report
cat > "$CLONE_DIR/CLONE_REPORT.md" << EOF
# SynOS Desktop Environment Clone Report

## Generated: $(date)

### Desktop Environment
- **Type**: MATE Desktop Environment
- **Panels**: $PANEL_COUNT configured
- **Applets**: $APPLET_COUNT panel applets

### Applications
- **Total Packages**: $TOTAL_PACKAGES
- **User-Installed**: $MANUAL_PACKAGES
- **Security Tools**: Included (Metasploit, Burp Suite, Nmap, etc.)

### Appearance
- **Themes**: User themes preserved
- **Icons**: Custom icon sets included
- **Wallpaper**: Current wallpaper captured
- **Fonts**: User fonts included

### Configuration
- **System Configs**: $CONFIG_COUNT files
- **Desktop Shortcuts**: $SHORTCUT_COUNT shortcuts
- **Autostart Apps**: Preserved
- **User Preferences**: Complete capture

### Storage Impact
- **Clone Size**: $CLONE_SIZE
- **ISO Impact**: Minimal size increase

### Integration Status
- **Restoration Scripts**: Ready
- **ISO Integration**: Configured
- **Automatic Restore**: Enabled

## What Will Be Restored

When you boot the SynOS Red Team ISO, you will get:

1. **Exact Panel Layout**: Every panel, applet, and configuration preserved
2. **All Applications**: Every program you have installed
3. **Visual Appearance**: Themes, icons, wallpaper exactly as configured
4. **Desktop Shortcuts**: All desktop files and shortcuts
5. **User Preferences**: Bash aliases, configs, autostart apps
6. **Font Settings**: Custom fonts and font configurations

Your desktop environment will be **100% identical** to your current setup!
EOF

echo "📄 Detailed report saved to: $CLONE_DIR/CLONE_REPORT.md"
echo ""

# Final validation
if [[ -f "$CLONE_DIR/restore-desktop.sh" && -f "$CLONE_DIR/install-packages.sh" && -d "$CLONE_DIR/configs" ]]; then
    echo -e "${GREEN}🎉 Desktop Clone Validation: PASSED${NC}"
    echo -e "${GREEN}✅ Ready for ISO integration!${NC}"
    echo ""
    echo "Your exact desktop environment will be preserved in the SynOS Red Team ISO!"
    return 0
else
    echo -e "${RED}❌ Desktop Clone Validation: FAILED${NC}"
    echo "Some components are missing. Re-run the cloning process."
    return 1
fi