# Syn_OS Development Environment Dockerfile
# Optimized for AI-enhanced cybersecurity OS development

FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Build arguments
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV RUST_BACKTRACE=1
ENV CARGO_TERM_COLOR=always
ENV GO111MODULE=on
ENV PATH="/home/${USERNAME}/.cargo/bin:/home/${USERNAME}/.local/bin:${PATH}"

# System dependencies installation
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core development tools
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libssl-dev \
    libudev-dev \
    autotools-dev \
    automake \
    autoconf \
    libtool \
    # Compiler infrastructure
    llvm-14 \
    llvm-14-dev \
    clang-14 \
    clang-tools-14 \
    clang-tidy-14 \
    clang-format-14 \
    lld-14 \
    gcc-multilib \
    g++-multilib \
    # Static analysis and security
    cppcheck \
    valgrind \
    gdb \
    gdb-multiarch \
    lldb-14 \
    strace \
    ltrace \
    # Performance profiling
    linux-tools-common \
    linux-tools-generic \
    perf-tools-unstable \
    # Assembly and binary analysis
    nasm \
    binutils \
    binutils-multiarch \
    objdump \
    readelf \
    hexdump \
    xxd \
    # Virtualization and emulation
    qemu-system-x86 \
    qemu-system-arm \
    qemu-utils \
    qemu-user-static \
    # Kernel development
    linux-headers-generic \
    linux-source \
    libelf-dev \
    # Network security tools
    tcpdump \
    wireshark-common \
    tshark \
    nmap \
    netcat-openbsd \
    socat \
    # Container and orchestration
    docker.io \
    docker-compose \
    # Database tools
    sqlite3 \
    postgresql-client \
    redis-tools \
    # Documentation and markup
    pandoc \
    graphviz \
    plantuml \
    # Security scanning
    lynis \
    chkrootkit \
    rkhunter \
    # Monitoring and system tools
    htop \
    iotop \
    sysstat \
    dstat \
    tree \
    jq \
    yq \
    # Development utilities
    curl \
    wget \
    git \
    git-lfs \
    openssh-client \
    gnupg \
    zip \
    unzip \
    # Python development
    python3-dev \
    python3-pip \
    python3-venv \
    # Node.js (updated version)
    nodejs \
    npm \
    # Go development tools
    golang-go \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for the vscode user
USER $USERNAME
WORKDIR /home/$USERNAME

# Rust installation with targets
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable \
    && . ~/.cargo/env \
    && rustup target add x86_64-unknown-none \
    && rustup target add i686-unknown-none \
    && rustup target add wasm32-unknown-unknown \
    && rustup component add rust-src \
    && rustup component add llvm-tools-preview \
    && rustup component add clippy \
    && rustup component add rustfmt \
    && rustup component add rust-analyzer \
    && cargo install --locked cargo-audit \
    && cargo install --locked cargo-deny \
    && cargo install --locked cargo-outdated \
    && cargo install --locked cargo-edit \
    && cargo install --locked cargo-watch \
    && cargo install --locked cargo-expand \
    && cargo install --locked cargo-bloat \
    && cargo install --locked cargo-udeps \
    && cargo install --locked flamegraph \
    && cargo install --locked bootimage

# Python package installation
RUN python3 -m pip install --user --upgrade pip setuptools wheel \
    && python3 -m pip install --user \
        # Core development
        black \
        pylint \
        mypy \
        bandit \
        safety \
        # Testing
        pytest \
        pytest-cov \
        pytest-xdist \
        # Security analysis
        semgrep \
        # AI/ML libraries
        numpy \
        scipy \
        scikit-learn \
        torch \
        # Web development
        fastapi \
        uvicorn \
        aiohttp \
        requests \
        # Data handling
        pandas \
        matplotlib \
        seaborn \
        # Documentation
        sphinx \
        mkdocs \
        # Jupyter
        jupyterlab \
        notebook

# Go tools installation
ENV GOPATH=/home/$USERNAME/go
ENV PATH="${PATH}:${GOPATH}/bin"
RUN mkdir -p $GOPATH/bin \
    && go install golang.org/x/tools/gopls@latest \
    && go install golang.org/x/tools/cmd/goimports@latest \
    && go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest \
    && go install honnef.co/go/tools/cmd/staticcheck@latest \
    && go install github.com/securego/gosec/v2/cmd/gosec@latest

# Node.js global packages
RUN npm install -g \
    typescript \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    eslint \
    prettier \
    npm-check-updates \
    create-react-app \
    vite \
    @vitejs/plugin-react

# Development environment setup
USER root

# Create development directories with proper permissions
RUN mkdir -p /workspace \
    && chown -R $USERNAME:$USERNAME /workspace \
    && mkdir -p /opt/synapticos \
    && chown -R $USERNAME:$USERNAME /opt/synapticos

# Install additional security tools
RUN wget -qO- https://github.com/aquasecurity/trivy/releases/latest/download/trivy_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/').tar.gz | tar -xzC /usr/local/bin trivy \
    && chmod +x /usr/local/bin/trivy

# Install eBPF development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libbpf-dev \
    bpftool \
    && rm -rf /var/lib/apt/lists/*

# Setup sudoers for development
RUN echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Configure git safe directory
RUN git config --system --add safe.directory '*'

# Set up development environment
USER $USERNAME
WORKDIR /workspace

# Create configuration directories
RUN mkdir -p ~/.config/Code/User \
    && mkdir -p ~/.local/bin \
    && mkdir -p ~/.ssh

# Health check script
COPY --chown=$USERNAME:$USERNAME dev-environment/healthcheck.sh /home/$USERNAME/.local/bin/
RUN chmod +x /home/$USERNAME/.local/bin/healthcheck.sh

# Default command
CMD ["/bin/bash"]

# Labels for image metadata
LABEL maintainer="Syn_OS Development Team"
LABEL description="Comprehensive development environment for AI-enhanced cybersecurity OS"
LABEL version="2025.01"
