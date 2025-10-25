#!/bin/bash

# SynOS Developer & Cybersecurity Professional Tools Installer
# Installs all productivity and development tools for OS development and cybersecurity career

set -e

TOOLS_DIR="/opt/synos-tools"
USER_HOME="/home/user"

print_status() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

install_browsers() {
    print_status "Installing browsers and web tools..."

    # Google Chrome
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt update
    apt install -y google-chrome-stable

    # Microsoft Edge
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
    install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list
    apt update
    apt install -y microsoft-edge-stable

    # Brave Browser
    curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" > /etc/apt/sources.list.d/brave-browser-release.list
    apt update
    apt install -y brave-browser

    # Tor Browser
    cd /tmp
    wget https://www.torproject.org/dist/torbrowser/12.5.6/tor-browser-linux64-12.5.6_ALL.tar.xz
    tar -xf tor-browser-linux64-*.tar.xz -C /opt/
    mv /opt/tor-browser_* /opt/tor-browser
    chown -R user:user /opt/tor-browser
}

install_productivity_tools() {
    print_status "Installing productivity and note-taking tools..."

    # Notion (via web app + desktop wrapper)
    cd /tmp
    wget https://github.com/notion-enhancer/desktop/releases/download/v2.0.18/Notion-2.0.18.AppImage
    chmod +x Notion-*.AppImage
    mv Notion-*.AppImage /opt/notion
    chown user:user /opt/notion

    # Obsidian
    wget https://github.com/obsidianmd/obsidian-releases/releases/download/v1.4.16/obsidian_1.4.16_amd64.deb
    dpkg -i obsidian_*.deb || apt install -f -y

    # Typora (markdown editor)
    wget -qO - https://typora.io/linux/public-key.asc | apt-key add -
    echo 'deb https://typora.io/linux ./' > /etc/apt/sources.list.d/typora.list
    apt update
    apt install -y typora

    # LibreOffice (full suite)
    apt install -y libreoffice libreoffice-l10n-en-us

    # Zotero (research management)
    cd /tmp
    wget https://download.zotero.org/client/release/6.0.27/Zotero-6.0.27_linux-x86_64.tar.bz2
    tar -xf Zotero-*.tar.bz2 -C /opt/
    mv /opt/Zotero_* /opt/zotero
    chown -R user:user /opt/zotero

    # Joplin (note-taking)
    wget -O - https://raw.githubusercontent.com/laurent22/joplin/dev/Joplin_install_and_update.sh | bash
}

install_development_ides() {
    print_status "Installing development IDEs and editors..."

    # Visual Studio Code
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
    apt update
    apt install -y code

    # JetBrains Toolbox (for IntelliJ, PyCharm, CLion, etc.)
    cd /tmp
    wget https://download.jetbrains.com/toolbox/jetbrains-toolbox-1.28.1.13236.tar.gz
    tar -xzf jetbrains-toolbox-*.tar.gz
    mv jetbrains-toolbox-*/jetbrains-toolbox /opt/
    chown user:user /opt/jetbrains-toolbox

    # Sublime Text
    wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | apt-key add -
    echo "deb https://download.sublimetext.com/ apt/stable/" > /etc/apt/sources.list.d/sublime-text.list
    apt update
    apt install -y sublime-text

    # Atom (GitHub's editor)
    wget https://github.com/atom/atom/releases/download/v1.60.0/atom-amd64.deb
    dpkg -i atom-amd64.deb || apt install -f -y

    # Neovim (advanced vim)
    apt install -y neovim

    # Emacs
    apt install -y emacs

    # Brackets (web development)
    snap install brackets --classic
}

install_virtualization_tools() {
    print_status "Installing virtualization and container tools..."

    # VirtualBox (latest version)
    wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | apt-key add -
    echo "deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian bookworm contrib" > /etc/apt/sources.list.d/virtualbox.list
    apt update
    apt install -y virtualbox-7.0 virtualbox-ext-pack

    # VMware Workstation Player
    cd /tmp
    wget https://www.vmware.com/go/getworkstation-linux -O vmware-workstation.bundle
    chmod +x vmware-workstation.bundle
    ./vmware-workstation.bundle --console --required --eulas-agreed

    # Docker Desktop
    apt install -y ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Podman (Docker alternative)
    apt install -y podman

    # Kubernetes tools
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

    # Minikube
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    install minikube /usr/local/bin/
}

install_cybersecurity_career_tools() {
    print_status "Installing cybersecurity career development tools..."

    # Certification Study Tools
    apt install -y anki  # Flashcard software

    # GNS3 (network simulation)
    add-apt-repository ppa:gns3/ppa -y
    apt update
    apt install -y gns3-gui gns3-server

    # Packet Tracer (Cisco)
    # Note: Requires manual download from Cisco NetAcad
    print_warning "Cisco Packet Tracer requires manual download from netacad.com"

    # Cyber ranges and labs
    cd /tmp
    git clone https://github.com/rapid7/metasploitable3.git /opt/metasploitable3
    git clone https://github.com/vulhub/vulhub.git /opt/vulhub
    chown -R user:user /opt/metasploitable3 /opt/vulhub

    # OWASP WebGoat and other practice labs
    docker pull webgoat/goatandwolf
    docker pull vulnerables/web-dvwa
    docker pull citizenstig/nowasp
    docker pull ismisepaul/securityshepherd

    # Vulnerable VMs download scripts
    cat > /opt/synos-tools/download-vuln-vms.sh << 'EOF'
#!/bin/bash
# Download vulnerable VMs for practice

mkdir -p /home/user/VulnLabs

cd /home/user/VulnLabs

# Metasploitable 2
wget https://sourceforge.net/projects/metasploitable/files/Metasploitable2/metasploitable-linux-2.0.0.zip

# VulnHub VMs (popular ones)
wget https://download.vulnhub.com/kioptrix/Kioptrix_Level_1.rar
wget https://download.vulnhub.com/stapler/Stapler.ova
wget https://download.vulnhub.com/basic-pentesting/BasicPentesting.zip

echo "Vulnerable VMs downloaded to /home/user/VulnLabs"
EOF
    chmod +x /opt/synos-tools/download-vuln-vms.sh
}

install_communication_tools() {
    print_status "Installing communication and collaboration tools..."

    # Discord
    wget "https://discord.com/api/download?platform=linux&format=deb" -O discord.deb
    dpkg -i discord.deb || apt install -f -y

    # Slack
    wget https://downloads.slack-edge.com/releases/linux/4.33.90/prod/x64/slack-desktop-4.33.90-amd64.deb
    dpkg -i slack-desktop-*.deb || apt install -f -y

    # Microsoft Teams
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
    install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/ms-teams stable main" > /etc/apt/sources.list.d/teams.list
    apt update
    apt install -y teams

    # Zoom
    wget https://zoom.us/client/latest/zoom_amd64.deb
    dpkg -i zoom_amd64.deb || apt install -f -y

    # Telegram
    apt install -y telegram-desktop

    # Element (Matrix client)
    wget -O /usr/share/keyrings/element-io-archive-keyring.gpg https://packages.element.io/debian/element-io-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/element-io-archive-keyring.gpg] https://packages.element.io/debian/ default main" > /etc/apt/sources.list.d/element-io.list
    apt update
    apt install -y element-desktop
}

install_advanced_dev_tools() {
    print_status "Installing advanced development tools..."

    # Database tools
    apt install -y dbeaver-ce pgadmin4 mysql-workbench-community

    # API testing
    snap install postman
    snap install insomnia

    # Git tools
    apt install -y git-lfs git-flow gitg meld

    # Terminal multiplexers and shells
    apt install -y tmux screen zsh fish
    # Oh My Zsh
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" --unattended

    # Cloud CLIs
    # AWS CLI
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install

    # Azure CLI
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash

    # Google Cloud CLI
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" > /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    apt update
    apt install -y google-cloud-cli

    # Infrastructure as Code
    # Terraform
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main" > /etc/apt/sources.list.d/hashicorp.list
    apt update
    apt install -y terraform

    # Ansible
    apt install -y ansible

    # Monitoring tools
    # Prometheus node exporter
    cd /tmp
    wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
    tar xvfz node_exporter-*.tar.gz
    cp node_exporter-*/node_exporter /usr/local/bin/

    # Grafana
    wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
    echo "deb https://packages.grafana.com/oss/deb stable main" > /etc/apt/sources.list.d/grafana.list
    apt update
    apt install -y grafana
}

install_multimedia_tools() {
    print_status "Installing multimedia and content creation tools..."

    # Screen recording and streaming
    apt install -y obs-studio simplescreenrecorder kazam

    # Image editing
    apt install -y gimp inkscape krita blender

    # Video editing
    apt install -y kdenlive openshot pitivi

    # Audio editing
    apt install -y audacity ardour

    # 3D modeling
    apt install -y freecad openscad

    # Document conversion
    apt install -y pandoc texlive-full
}

create_desktop_shortcuts() {
    print_status "Creating desktop shortcuts and application menu..."

    mkdir -p "$USER_HOME/.local/share/applications/Development"
    mkdir -p "$USER_HOME/.local/share/applications/Security"
    mkdir -p "$USER_HOME/.local/share/applications/Productivity"

    # Development shortcuts
    cat > "$USER_HOME/.local/share/applications/Development/VSCode.desktop" << EOF
[Desktop Entry]
Name=Visual Studio Code
Comment=Code Editor
Exec=code
Icon=vscode
Terminal=false
Type=Application
Categories=Development;IDE;
EOF

    cat > "$USER_HOME/.local/share/applications/Development/JetBrains-Toolbox.desktop" << EOF
[Desktop Entry]
Name=JetBrains Toolbox
Comment=JetBrains IDE Manager
Exec=/opt/jetbrains-toolbox
Icon=jetbrains-toolbox
Terminal=false
Type=Application
Categories=Development;IDE;
EOF

    # Productivity shortcuts
    cat > "$USER_HOME/.local/share/applications/Productivity/Obsidian.desktop" << EOF
[Desktop Entry]
Name=Obsidian
Comment=Knowledge Management
Exec=obsidian
Icon=obsidian
Terminal=false
Type=Application
Categories=Office;
EOF

    cat > "$USER_HOME/.local/share/applications/Productivity/Notion.desktop" << EOF
[Desktop Entry]
Name=Notion
Comment=All-in-one workspace
Exec=/opt/notion
Icon=notion
Terminal=false
Type=Application
Categories=Office;
EOF

    # Set ownership
    chown -R user:user "$USER_HOME/.local/share/applications"
}

setup_development_environment() {
    print_status "Setting up development environment..."

    # Install programming languages and runtimes
    # Node.js LTS
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
    apt install -y nodejs

    # Python environments
    apt install -y python3-pip python3-venv python3-dev pipenv poetry

    # Ruby with rbenv
    apt install -y rbenv ruby-build

    # Go
    cd /tmp
    wget https://go.dev/dl/go1.21.3.linux-amd64.tar.gz
    tar -C /usr/local -xzf go*.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile

    # Rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

    # Java Development Kit (multiple versions)
    apt install -y openjdk-8-jdk openjdk-11-jdk openjdk-17-jdk

    # .NET
    wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    dpkg -i packages-microsoft-prod.deb
    apt update
    apt install -y dotnet-sdk-7.0

    # Flutter
    cd /opt
    wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.13.6-stable.tar.xz
    tar xf flutter_linux_*.tar.xz
    chown -R user:user /opt/flutter
    echo 'export PATH="$PATH:/opt/flutter/bin"' >> /etc/profile

    # Android SDK
    cd /opt
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
    unzip commandlinetools-linux-*.zip -d android-sdk
    chown -R user:user /opt/android-sdk
    echo 'export ANDROID_HOME=/opt/android-sdk' >> /etc/profile
    echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/bin:$ANDROID_HOME/platform-tools' >> /etc/profile
}

main() {
    print_status "Installing comprehensive developer and cybersecurity professional tools..."

    # Create tools directory
    mkdir -p "$TOOLS_DIR"

    # Update system
    apt update && apt upgrade -y

    # Install all tool categories
    install_browsers
    install_productivity_tools
    install_development_ides
    install_virtualization_tools
    install_cybersecurity_career_tools
    install_communication_tools
    install_advanced_dev_tools
    install_multimedia_tools
    create_desktop_shortcuts
    setup_development_environment

    print_status "All tools installed successfully!"
    print_status "Your SynOS system now includes:"
    echo "  • All major browsers (Chrome, Edge, Brave, Tor)"
    echo "  • Productivity suite (Notion, Obsidian, LibreOffice)"
    echo "  • Full development environment (VS Code, JetBrains, etc.)"
    echo "  • Complete virtualization stack (VirtualBox, VMware, Docker)"
    echo "  • Cybersecurity career tools and practice labs"
    echo "  • Communication tools (Discord, Slack, Teams, Zoom)"
    echo "  • Advanced development tools and cloud CLIs"
    echo "  • Multimedia content creation suite"
    echo
    print_status "Perfect for OS development and cybersecurity career advancement!"
}

# Run main function
main "$@"