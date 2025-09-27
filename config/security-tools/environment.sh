#!/bin/bash
# Syn_OS Security Tools Environment Configuration

export SYNOS_SECURITY_TOOLSET="${PROJECT_ROOT}/tools/parrot-security-toolset"
export PATH="$SYNOS_SECURITY_TOOLSET/bin:$PATH"

# Tool-specific configurations
export WORDLIST_PATH="$SYNOS_SECURITY_TOOLSET/wordlists"
export MSF_PATH="$SYNOS_SECURITY_TOOLSET/config/metasploit-framework"
export JOHN_PATH="$SYNOS_SECURITY_TOOLSET/config/john"

# Aliases for common tools
alias synos-nmap='$SYNOS_SECURITY_TOOLSET/bin/nmap'
alias synos-sqlmap='$SYNOS_SECURITY_TOOLSET/bin/sqlmap'
alias synos-hydra='$SYNOS_SECURITY_TOOLSET/bin/hydra'
alias synos-aircrack='$SYNOS_SECURITY_TOOLSET/bin/aircrack-ng'
alias synos-security='$SYNOS_SECURITY_TOOLSET/synos-security-launcher.py'

# Utility functions
synos_security_status() {
    echo "Syn_OS Security Tools Status:"
    echo "Toolset Path: $SYNOS_SECURITY_TOOLSET"
    echo "Available Tools: $(ls -1 $SYNOS_SECURITY_TOOLSET/bin | wc -l)"
    echo "Wordlists: $(find $SYNOS_SECURITY_TOOLSET/wordlists -type f 2>/dev/null | wc -l)"
    echo "Configuration Dirs: $(ls -1 $SYNOS_SECURITY_TOOLSET/config | wc -l)"
}

synos_security_update() {
    echo "Updating Syn_OS security tools configuration..."
    source "$SYNOS_CONFIG_PATH/security-tools/environment.sh"
    echo "Security tools environment updated!"
}
