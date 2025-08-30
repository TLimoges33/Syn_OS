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
        make \
        autotools-dev \
        automake \
        autoconf \
        libtool \
        # Compiler infrastructure
        llvm \
        clang \
        clang-tools \
        clang-tidy \
        clang-format \
        lld \
        gcc-multilib \
        g++-multilib \
        # Static analysis tools
        cppcheck \
        # Debugging tools
        gdb \
        gdb-multiarch \
        lldb \
        valgrind \
        strace \
        ltrace \
        # Performance and profiling
        linux-tools-common \
        linux-tools-generic \
        perf-tools-unstable \
        # Assembly and binary tools
        nasm \
        binutils \
        binutils-multiarch \
        bsdextrautils \
        objdump \
        nm \
        readelf \
        # Virtualization for kernel testing
        qemu-system-x86 \
        qemu-system-arm \
        qemu-utils \
        # Security tools
        fail2ban \
        rkhunter \
        chkrootkit \
        # Network analysis
        tcpdump \
        wireshark-common \
        tshark \
        nmap \
        netcat \
        # Monitoring tools
        htop \
        iotop \
        sysstat \
        dstat \
        # Network security
        curl \
        wget \
        gnupg \
        openssh-client \
        # Database tools
        sqlite3 \
        postgresql-client \
        # Documentation tools
        pandoc \
        graphviz \
        # File and text processing
        jq \
        yq \
        tree \
        ripgrep \
        fd-find \
        # Python development
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
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

# Install Go development tools
ENV PATH="/usr/local/go/bin:${PATH}"
RUN go install golang.org/x/tools/gopls@latest \
    && go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest \
    && go install github.com/securecodewarrior/shenron@latest \
    && go install github.com/aquasecurity/trivy@latest \
    && go install github.com/trufflesecurity/trufflehog/v3@latest

# Install additional security and development tools
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin \
    && curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
    && wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 \
    && chmod +x /usr/local/bin/hadolint

# Install Rust from builder stage
COPY --from=rust-builder /usr/local/cargo /usr/local/cargo
COPY --from=rust-builder /usr/local/rustup /usr/local/rustup

# Install Python security and development packages
RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir \
        # Core development tools
        capstone \
        keystone-engine \
        requests \
        pyyaml \
        # Security tools
        bandit \
        safety \
        semgrep \
        detect-secrets \
        # Code quality tools
        black \
        isort \
        mypy \
        pylint \
        flake8 \
        # Testing frameworks
        pytest \
        pytest-cov \
        # Documentation tools
        sphinx \
        mkdocs \
        # Data analysis
        pandas \
        numpy \
        # Container security
        trivy-operator

# Install comprehensive Rust toolchain
RUN cargo install --locked \
        # Security tools
        cargo-audit \
        cargo-deny \
        cargo-geiger \
        # Development tools
        cargo-watch \
        cargo-expand \
        cargo-tree \
        cargo-outdated \
        # Testing and benchmarking
        cargo-nextest \
        criterion \
        # Cross-compilation
        cross \
        # Documentation
        mdbook \
        # Code generation
        bindgen-cli

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