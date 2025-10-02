#!/bin/bash

# SynOS Simple Asset Creation Script
# Creates basic visual assets for SynOS branding using available tools

set -e

BRANDING_DIR="/home/diablorain/Syn_OS/SynOS-Branding"
FILESYSTEM_ROOT="/home/diablorain/Syn_OS/SynOS-Linux-Builder/filesystem-extract"

echo "🎨 Creating SynOS Simple Assets..."

cd "$BRANDING_DIR"

# Create basic solid color backgrounds using GraphicsMagick
echo "🖼️  Creating desktop backgrounds..."

# Dark neural theme background
convert -size 1920x1080 'gradient:#000011-#001133' backgrounds/synos-neural-dark.jpg

# Light theme background
convert -size 1920x1080 'gradient:#2a2a4a-#4a4a6a' backgrounds/synos-neural-blue.jpg

# Abstract matrix theme
convert -size 1920x1080 xc:'#001122' backgrounds/synos-matrix.jpg

echo "🚀 Creating GRUB backgrounds..."

# GRUB backgrounds (simpler gradients)
convert -size 1920x1080 'gradient:#000033-#003333' grub/synos-grub-16x9.png
convert -size 1024x768 'gradient:#000033-#003333' grub/synos-grub-4x3.png

echo "🏷️  Creating simple logo placeholders..."

# Create simple colored square logos
convert -size 512x512 xc:'#00ffff' logos/synos-logo-512.png
convert -size 256x256 xc:'#00ffff' logos/synos-logo-256.png
convert -size 128x128 xc:'#00ffff' logos/synos-logo-128.png
convert -size 64x64 xc:'#00ffff' logos/synos-logo-64.png
convert -size 32x32 xc:'#00ffff' logos/synos-logo-32.png

echo "🔐 Creating Plymouth boot theme..."

mkdir -p plymouth/synos-neural

# Create Plymouth theme configuration
cat > plymouth/synos-neural/synos-neural.plymouth << 'EOF'
[Plymouth Theme]
Name=SynOS Neural
Description=SynOS Neural Darwinism boot theme
ModuleName=text

[text]
title=SynOS Neural - Loading AI Framework...
black=0x001122
white=0x00ffff
brown=0xffffff
blue=0x0066cc
EOF

echo "🖥️  Creating desktop theme structure..."

mkdir -p themes/synos-mate/{gtk-3.0,metacity-1}

# Create enhanced GTK3 theme
cat > themes/synos-mate/gtk-3.0/gtk.css << 'EOF'
/* SynOS MATE Theme - Neural Dark */

@define-color theme_bg_color #1a1a2e;
@define-color theme_fg_color #e0e0e0;
@define-color theme_selected_bg_color #00ffff;
@define-color theme_selected_fg_color #000000;
@define-color theme_base_color #16213e;
@define-color theme_text_color #ffffff;
@define-color theme_unfocused_bg_color #15152a;
@define-color theme_unfocused_fg_color #c0c0c0;

/* Window styling */
window {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
    font-family: "Liberation Sans";
}

/* Header bars */
headerbar {
    background: linear-gradient(to bottom, #2a2a4a, #1a1a2e);
    color: @theme_fg_color;
    border-bottom: 1px solid #00ffff22;
}

/* Panel styling */
.mate-panel {
    background: linear-gradient(to bottom, #1a1a2e, #0f0f23);
    color: #e0e0e0;
    border: 1px solid #00ffff33;
}

/* Menu styling */
menubar {
    background: linear-gradient(to bottom, #1a1a2e, #16213e);
    color: #e0e0e0;
    border-bottom: 1px solid #00ffff22;
}

menu {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
    border: 1px solid #00ffff44;
}

menuitem:hover {
    background-color: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}

/* Button styling */
button {
    background: linear-gradient(to bottom, #2a2a4a, #1a1a2e);
    color: @theme_fg_color;
    border: 1px solid #00ffff44;
    border-radius: 3px;
}

button:hover {
    background: linear-gradient(to bottom, #3a3a5a, #2a2a4a);
    border-color: #00ffff88;
}

button:active {
    background: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}

/* Entry/Input styling */
entry {
    background-color: @theme_base_color;
    color: @theme_text_color;
    border: 1px solid #00ffff44;
    border-radius: 3px;
}

entry:focus {
    border-color: @theme_selected_bg_color;
    box-shadow: 0 0 3px #00ffff44;
}

/* Selection styling */
*:selected,
selection {
    background-color: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}

/* Scrollbar styling */
scrollbar {
    background-color: #16213e;
}

scrollbar slider {
    background-color: #00ffff44;
    border-radius: 3px;
}

scrollbar slider:hover {
    background-color: #00ffff66;
}

/* Tooltip styling */
tooltip {
    background-color: #0f0f23;
    color: #e0e0e0;
    border: 1px solid #00ffff44;
    border-radius: 3px;
}
EOF

# Create metacity window theme
cat > themes/synos-mate/metacity-1/metacity-theme-3.xml << 'EOF'
<?xml version="1.0"?>
<metacity_theme>
<info>
  <name>SynOS Neural</name>
  <author>SynOS Project</author>
  <date>2025</date>
  <description>Neural Darwinism window theme for SynOS</description>
</info>

<frame_geometry name="normal">
  <distance name="left_width" value="4"/>
  <distance name="right_width" value="4"/>
  <distance name="bottom_height" value="4"/>
  <distance name="left_titlebar_edge" value="4"/>
  <distance name="right_titlebar_edge" value="4"/>
  <distance name="title_vertical_pad" value="6"/>
  <border name="title_border" left="4" right="4" top="4" bottom="2"/>
  <border name="button_border" left="2" right="2" top="2" bottom="2"/>
</frame_geometry>

<draw_ops name="title_bg">
  <gradient type="horizontal" x="0" y="0" width="width" height="height">
    <color value="#2a2a4a"/>
    <color value="#1a1a2e"/>
  </gradient>
  <rectangle color="#00ffff22" x="0" y="height-1" width="width" height="1"/>
</draw_ops>

<draw_ops name="title_bg_unfocused">
  <gradient type="horizontal" x="0" y="0" width="width" height="height">
    <color value="#15152a"/>
    <color value="#0f0f1e"/>
  </gradient>
</draw_ops>

<frame_style name="normal_focused" geometry="normal">
  <piece position="titlebar" draw_ops="title_bg"/>
</frame_style>

<frame_style name="normal_unfocused" geometry="normal">
  <piece position="titlebar" draw_ops="title_bg_unfocused"/>
</frame_style>

<frame_style_set name="normal">
  <frame focus="yes" state="normal" style="normal_focused"/>
  <frame focus="no" state="normal" style="normal_unfocused"/>
</frame_style_set>

<window type="normal" style_set="normal"/>

</metacity_theme>
EOF

echo "✅ SynOS Simple Assets Created Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Assets Location: $BRANDING_DIR"
echo "🖼️  Backgrounds: $(ls backgrounds/ 2>/dev/null | wc -l) files"
echo "🏷️  Logos: $(ls logos/ 2>/dev/null | wc -l) files"
echo "🚀 GRUB themes: $(ls grub/ 2>/dev/null | wc -l) files"
echo "🔐 Plymouth theme: Complete"
echo "🖥️  Desktop theme: Complete with neural styling"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"