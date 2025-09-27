#!/bin/bash

# SynOS Asset Creation Script
# Creates visual assets for SynOS branding using ImageMagick and system tools

set -e

BRANDING_DIR="/home/diablorain/Syn_OS/SynOS-Branding"
FILESYSTEM_ROOT="/home/diablorain/Syn_OS/SynOS-Linux-Builder/filesystem-extract"

echo "🎨 Creating SynOS Visual Assets..."

# Check if ImageMagick is available
if ! command -v convert &> /dev/null; then
    echo "📦 Installing ImageMagick..."
    sudo apt update && sudo apt install -y imagemagick
fi

cd "$BRANDING_DIR"

# Function to create a gradient background
create_gradient_bg() {
    local filename="$1"
    local width="$2"
    local height="$3"
    local color1="$4"
    local color2="$5"

    convert -size "${width}x${height}" gradient:"${color1}-${color2}" "$filename"
}

# Function to add SynOS logo text to image
add_synos_logo() {
    local input_file="$1"
    local output_file="$2"

    convert "$input_file" \
        -gravity center \
        -pointsize 120 \
        -fill '#00ffff' \
        -font Liberation-Sans-Bold \
        -annotate +0-200 'SynOS' \
        -pointsize 36 \
        -fill '#ffffff' \
        -annotate +0-100 'Neural Darwinism Operating System' \
        -pointsize 24 \
        -fill '#aaaaaa' \
        -annotate +0+0 'AI-Enhanced • Consciousness Computing • Cybersecurity' \
        "$output_file"
}

echo "🖼️  Creating desktop backgrounds..."

# Create main SynOS background (neural network inspired)
create_gradient_bg "temp_gradient.png" "1920" "1080" "#000011" "#001133"
convert temp_gradient.png \
    -fill '#00ffff22' \
    -draw 'circle 300,200 350,250' \
    -draw 'circle 800,400 900,500' \
    -draw 'circle 1200,700 1350,850' \
    -draw 'circle 600,800 700,900' \
    backgrounds/synos-neural-dark.jpg

add_synos_logo backgrounds/synos-neural-dark.jpg backgrounds/synos-neural-dark.jpg

# Create light variant
create_gradient_bg "temp_gradient_light.png" "1920" "1080" "#f0f0f0" "#e0e0ff"
convert temp_gradient_light.png \
    -fill '#0066cc22' \
    -draw 'circle 300,200 350,250' \
    -draw 'circle 800,400 900,500' \
    -draw 'circle 1200,700 1350,850' \
    -draw 'circle 600,800 700,900' \
    backgrounds/synos-neural-light.jpg

add_synos_logo backgrounds/synos-neural-light.jpg backgrounds/synos-neural-light.jpg

# Create abstract circuit pattern
create_gradient_bg "temp_circuit.png" "1920" "1080" "#000022" "#002200"
convert temp_circuit.png \
    -fill '#00ff0033' \
    -draw 'rectangle 100,100 1820,120' \
    -draw 'rectangle 100,200 1820,220' \
    -draw 'rectangle 100,300 1820,320' \
    -draw 'rectangle 200,100 220,980' \
    -draw 'rectangle 500,100 520,980' \
    -draw 'rectangle 800,100 820,980' \
    -draw 'rectangle 1200,100 1220,980' \
    backgrounds/synos-circuit-matrix.jpg

add_synos_logo backgrounds/synos-circuit-matrix.jpg backgrounds/synos-circuit-matrix.jpg

echo "🏷️  Creating logos..."

# Create main SynOS logo
convert -size 512x512 xc:transparent \
    -fill '#00ffff' \
    -pointsize 180 \
    -font Liberation-Sans-Bold \
    -gravity center \
    -annotate +0-50 'S' \
    -pointsize 120 \
    -annotate +80+50 'OS' \
    -fill '#ffffff' \
    -pointsize 24 \
    -annotate +0+120 'NEURAL' \
    logos/synos-logo-512.png

# Create smaller variants
convert logos/synos-logo-512.png -resize 256x256 logos/synos-logo-256.png
convert logos/synos-logo-512.png -resize 128x128 logos/synos-logo-128.png
convert logos/synos-logo-512.png -resize 64x64 logos/synos-logo-64.png
convert logos/synos-logo-512.png -resize 32x32 logos/synos-logo-32.png

echo "🚀 Creating GRUB backgrounds..."

# GRUB 16:9 background
create_gradient_bg grub/synos-grub-16x9.png "1920" "1080" "#000033" "#003333"
convert grub/synos-grub-16x9.png \
    -gravity center \
    -pointsize 80 \
    -fill '#00ffff' \
    -font Liberation-Sans-Bold \
    -annotate +0-100 'SynOS' \
    -pointsize 32 \
    -fill '#ffffff' \
    -annotate +0-50 'Neural Darwinism Operating System' \
    -pointsize 20 \
    -fill '#aaaaaa' \
    -annotate +0+50 'Loading AI-Enhanced Security Framework...' \
    grub/synos-grub-16x9.png

# GRUB 4:3 background
create_gradient_bg grub/synos-grub-4x3.png "1024" "768" "#000033" "#003333"
convert grub/synos-grub-4x3.png \
    -gravity center \
    -pointsize 60 \
    -fill '#00ffff' \
    -font Liberation-Sans-Bold \
    -annotate +0-80 'SynOS' \
    -pointsize 24 \
    -fill '#ffffff' \
    -annotate +0-40 'Neural Darwinism OS' \
    -pointsize 16 \
    -fill '#aaaaaa' \
    -annotate +0+40 'Loading AI Framework...' \
    grub/synos-grub-4x3.png

echo "🔐 Creating Plymouth boot theme..."

mkdir -p plymouth/synos-neural/{16x16,22x22,24x24,32x32}

# Create Plymouth theme configuration
cat > plymouth/synos-neural/synos-neural.plymouth << 'EOF'
[Plymouth Theme]
Name=SynOS Neural
Description=SynOS Neural Darwinism boot theme with AI consciousness indicators
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos-neural
ScriptFile=/usr/share/plymouth/themes/synos-neural/synos-neural.script
EOF

# Create Plymouth boot script
cat > plymouth/synos-neural/synos-neural.script << 'EOF'
# SynOS Plymouth Boot Theme Script

# Background setup
background_image = Image("background.png");
screen_width = Window.GetWidth();
screen_height = Window.GetHeight();
background_image = background_image.Scale(screen_width, screen_height);
sprite_background = Sprite(background_image);

# Logo setup
logo_image = Image("synos-logo.png");
logo_sprite = Sprite(logo_image);
logo_sprite.SetPosition((screen_width - logo_image.GetWidth()) / 2, screen_height * 0.2);

# Progress bar
progress_box_image = Image("progress_box.png");
progress_box_sprite = Sprite(progress_box_image);
progress_box_sprite.SetPosition((screen_width - progress_box_image.GetWidth()) / 2, screen_height * 0.7);

# Neural network animation dots
for (i = 0; i < 5; i++) {
    neural_dot[i] = Sprite();
    neural_dot[i].SetImage(Image("neural_dot.png"));
    neural_dot[i].SetPosition(screen_width * 0.3 + i * 80, screen_height * 0.5);
}

# Animation counter
animation_counter = 0;

# Boot progress callback
fun boot_progress_cb(duration, progress) {
    if (progress_box_image.GetWidth() > 0) {
        progress_pixmap = Image("progress_bar.png");
        progress_pixmap = progress_pixmap.Scale(progress_box_image.GetWidth() * progress, progress_pixmap.GetHeight());
        progress_sprite.SetImage(progress_pixmap);
    }
}

Plymouth.SetBootProgressFunction(boot_progress_cb);

# Refresh callback for animation
fun refresh_cb() {
    animation_counter++;

    # Animate neural dots
    for (i = 0; i < 5; i++) {
        alpha = Math.Sin(animation_counter * 0.1 + i * 0.5) * 0.5 + 0.5;
        neural_dot[i].SetOpacity(alpha);
    }
}

Plymouth.SetRefreshFunction(refresh_cb);
EOF

# Copy logo for Plymouth
cp logos/synos-logo-128.png plymouth/synos-neural/synos-logo.png

# Create simple colored rectangles for Plymouth elements
convert -size 400x20 xc:"#003366" plymouth/synos-neural/progress_box.png
convert -size 400x20 xc:"#00ffff" plymouth/synos-neural/progress_bar.png
convert -size 20x20 xc:"#00ffff" plymouth/synos-neural/neural_dot.png
cp backgrounds/synos-neural-dark.jpg plymouth/synos-neural/background.png

echo "🖥️  Creating desktop theme assets..."

mkdir -p themes/synos-mate/{gtk-3.0,metacity-1,icons}

# Create basic GTK3 theme
cat > themes/synos-mate/gtk-3.0/gtk.css << 'EOF'
/* SynOS MATE Theme - Neural Dark */

@define-color theme_bg_color #1a1a2e;
@define-color theme_fg_color #e0e0e0;
@define-color theme_selected_bg_color #00ffff;
@define-color theme_selected_fg_color #000000;
@define-color theme_base_color #16213e;
@define-color theme_text_color #ffffff;

/* Window styling */
window {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

/* Panel styling */
.mate-panel {
    background: linear-gradient(to bottom, #1a1a2e, #0f0f23);
    color: #e0e0e0;
}

/* Menu styling */
menubar {
    background: linear-gradient(to bottom, #1a1a2e, #16213e);
    color: #e0e0e0;
}

/* Selection styling */
*:selected {
    background-color: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}
EOF

rm -f temp_*.png

echo "✅ SynOS Visual Assets Created Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Assets Location: $BRANDING_DIR"
echo "🖼️  Backgrounds: $(ls backgrounds/ | wc -l) files"
echo "🏷️  Logos: $(ls logos/ | wc -l) files"
echo "🚀 GRUB themes: $(ls grub/ | wc -l) files"
echo "🔐 Plymouth theme: Complete"
echo "🖥️  Desktop theme: Basic structure created"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"