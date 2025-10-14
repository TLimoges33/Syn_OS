#!/bin/bash

# SynOS AI Module Refactoring Script
# Rename "consciousness" to proper AI terminology

echo "🔄 SynOS AI Module Refactoring"
echo "==============================="

BASE_DIR="/home/diablorain/Syn_OS"

# Step 1: Create new AI module structure
echo "Creating new AI module structure..."
mkdir -p "$BASE_DIR/core/ai"
mkdir -p "$BASE_DIR/core/ai/src"
mkdir -p "$BASE_DIR/core/ai/src/decision"
mkdir -p "$BASE_DIR/core/ai/src/pattern_recognition" 
mkdir -p "$BASE_DIR/core/ai/src/neural"
mkdir -p "$BASE_DIR/core/ai/src/inference"
mkdir -p "$BASE_DIR/core/ai/src/security"

# Step 2: Copy legitimate modules (excluding quantum pseudoscience)
echo "Copying legitimate AI modules..."
cp -r "$BASE_DIR/core/consciousness/src/decision/"* "$BASE_DIR/core/ai/src/decision/"
cp -r "$BASE_DIR/core/consciousness/src/pattern_recognition/"* "$BASE_DIR/core/ai/src/pattern_recognition/"
cp -r "$BASE_DIR/core/consciousness/src/inference/"* "$BASE_DIR/core/ai/src/inference/"
cp -r "$BASE_DIR/core/consciousness/src/security/"* "$BASE_DIR/core/ai/src/security/"

# Copy neural but will need to clean it
cp -r "$BASE_DIR/core/consciousness/src/neural/"* "$BASE_DIR/core/ai/src/neural/"

echo "✅ Module structure created"
echo "🔧 Manual refactoring of individual files required next"
