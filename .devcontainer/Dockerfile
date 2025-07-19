# Syn_OS Secure Development Container
# Multi-stage build for security and efficiency

FROM rust:1.75-bullseye as rust-builder

# Security hardening
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Install Rust targets for kernel development
RUN rustup target add x86_64-unknown-none \
    && rustup target add i686-unknown-none \
    && rustup component add rust-src \
    && rustup component add llvm-tools-preview \
    && rustup component add clippy \
    && rustup component add rustfmt

FROM mcr.microsoft.com/vscode/devcontainers/base:bullseye

# Security: Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install system dependencies with security focus
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Core development tools
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        libssl-dev \
        libudev-dev \
        # Compiler infrastructure
        llvm \
        clang \
        lld \
        # Debugging tools
        gdb \
        lldb \
        valgrind \
        strace \
        ltrace \
        # Assembly and binary tools
        nasm \
        binutils \
        bsdextrautils \
        # Virtualization for kernel testing
        qemu-system-x86 \
        qemu-utils \
        # Security tools
        fail2ban \
        rkhunter \
        chkrootkit \
        # Monitoring tools
        htop \
        iotop \
        tcpdump \
        # Network security
        curl \
        wget \
        gnupg \
        # Python development
        python3 \
        python3-pip \
        python3-venv \
        # Go development placeholder
        software-properties-common \
        # Node.js LTS
        && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
        && apt-get install -y nodejs \
    # Clean up to reduce attack surface
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Go with version pinning for security
RUN GO_VERSION="1.21.5" \
    && wget -q "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz" \
    && echo "e2bc0b3e4b64111ec117295c088bde5f00eeed1567999ff77bc859d7df70078e  go${GO_VERSION}.linux-amd64.tar.gz" | sha256sum -c - \
    && tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz" \
    && rm "go${GO_VERSION}.linux-amd64.tar.gz"

# Install Rust from builder stage
COPY --from=rust-builder /usr/local/cargo /usr/local/cargo
COPY --from=rust-builder /usr/local/rustup /usr/local/rustup

# Install Python security packages
RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir \
        capstone \
        keystone-engine \
        requests \
        pyyaml \
        bandit \
        safety \
        semgrep

# Install additional security tools
RUN cargo install cargo-audit cargo-deny

# Security: File system permissions
RUN mkdir -p /workspace \
    && chown -R $USERNAME:$USERNAME /workspace \
    && chmod 755 /workspace

# Security: Configure environment
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTUP_HOME=/usr/local/rustup
ENV PATH="/usr/local/cargo/bin:/usr/local/go/bin:${PATH}"

# Security: Drop privileges
USER $USERNAME

# Set working directory
WORKDIR /workspace

# Security: Verify installation integrity
RUN rustc --version \
    && cargo --version \
    && go version \
    && python3 --version \
    && node --version \
    && qemu-system-x86_64 --version

# Security: Create necessary directories with proper permissions
RUN mkdir -p ~/.cargo \
    && mkdir -p ~/.config \
    && mkdir -p ~/.local/bin

# Development environment validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD cargo --version && rustc --version && go version || exit 1

# Default command
CMD ["/bin/bash"]