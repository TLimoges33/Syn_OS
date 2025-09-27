#!/bin/bash

# ==================================================================
# SynOS Codespace Setup Script
# ==================================================================
# Initial setup when creating the codespace container
# ==================================================================

set -euo pipefail

echo "🚀 Setting up SynOS development environment..."

# Update package lists
sudo apt-get update

# Install essential development tools
sudo apt-get install -y \
  build-essential \
  pkg-config \
  libssl-dev \
  libudev-dev \
  llvm-dev \
  libclang-dev \
  clang \
  curl \
  wget \
  unzip \
  jq \
  htop \
  tree \
  fd-find \
  ripgrep \
  bat \
  exa

# Install additional security tools
sudo apt-get install -y \
  nmap \
  netcat-traditional \
  tcpdump \
  strace \
  ltrace

# Install Rust components
rustup component add clippy rustfmt
rustup target add x86_64-unknown-none

# Install cargo tools for development
cargo install cargo-watch cargo-edit cargo-audit

# Set up Rust environment optimizations
echo 'export CARGO_BUILD_JOBS=2' >> ~/.bashrc
echo 'export RUST_BACKTRACE=0' >> ~/.bashrc

# Install Node.js tools
npm install -g npm@latest

# Setup Git optimizations
git config --global init.defaultBranch main
git config --global core.autocrlf input
git config --global core.safecrlf false
git config --global pull.rebase false

echo "✅ SynOS development environment setup complete!"
echo "📋 Available tools:"
echo "  - Rust with clippy, rustfmt, cargo-watch"
echo "  - Security tools: nmap, netcat, tcpdump"
echo "  - Development utilities: fd, ripgrep, bat, exa"
echo "  - Node.js latest LTS with npm"
