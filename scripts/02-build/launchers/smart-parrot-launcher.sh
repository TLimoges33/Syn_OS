#!/bin/bash

# SynOS Smart ParrotOS-Inspired Build Launcher
# Uses comprehensive ParrotOS analysis for intelligent build decisions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNOS_ROOT="/home/diablorain/Syn_OS"
BUILD_DIR="${SYNOS_ROOT}/build"
TOOLS_INTEGRATION="${SYNOS_ROOT}/src/consciousness/parrot_tool_integration.py"

print_smart_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║         🧠 SynOS Smart ParrotOS-Inspired Builder 🧠         ║"
    echo "║                                                              ║"
    echo "║    Leveraging comprehensive ParrotOS 6.4 security analysis  ║"
    echo "║       500+ tools • AI consciousness • Educational focus     ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

analyze_system_resources() {
    echo -e "${CYAN}🔍 Analyzing system resources for optimal build strategy...${NC}"
    
    local memory_gb=$(free -g | awk 'NR==2{printf "%.1f", $2}')
    local available_gb=$(df /tmp | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    local cpu_cores=$(nproc)
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    echo "  💾 Memory: ${memory_gb}GB"
    echo "  💽 Available Space: ${available_gb}GB"
    echo "  🔢 CPU Cores: ${cpu_cores}"
    echo "  📊 Load Average: ${load_avg}"
    
    # Determine build strategy based on resources
    local build_strategy="conservative"
    
    if (( $(echo "$memory_gb >= 8" | bc -l) )) && (( available_gb >= 12 )); then
        if (( cpu_cores >= 4 )) && (( $(echo "$load_avg <= 2.0" | bc -l) )); then
            build_strategy="aggressive"
        else
            build_strategy="moderate"
        fi
    fi
    
    echo -e "  🎯 Recommended Strategy: ${GREEN}${build_strategy}${NC}"
    echo "$build_strategy"
}

check_parrotos_integration() {
    echo -e "${CYAN}📋 Checking ParrotOS integration framework...${NC}"
    
    if [[ -f "$TOOLS_INTEGRATION" ]]; then
        echo -e "  ✅ ParrotOS tool integration: ${GREEN}Available${NC}"
        
        # Run integration check
        if python3 "$TOOLS_INTEGRATION" > /tmp/parrot-integration-check.log 2>&1; then
            local tool_count=$(grep "Total tools in database:" /tmp/parrot-integration-check.log | awk '{print $6}')
            echo -e "  📊 Security tools available: ${GREEN}${tool_count}${NC}"
            
            local priority_count=$(grep -A 20 "High Priority Tools" /tmp/parrot-integration-check.log | grep -c "Priority:" || echo "0")
            echo -e "  ⭐ High priority tools: ${GREEN}${priority_count}${NC}"
            
            local gui_count=$(grep "GUI Tools:" /tmp/parrot-integration-check.log | awk '{print $3}')
            echo -e "  🖥️ GUI tools: ${GREEN}${gui_count}${NC}"
            
            return 0
        else
            echo -e "  ⚠️ Integration check failed - continuing with basic build"
            return 1
        fi
    else
        echo -e "  ❌ ParrotOS integration: ${RED}Not found${NC}"
        return 1
    fi
}

create_build_config() {
    local strategy="$1"
    local config_file="${BUILD_DIR}/build-config.json"
    
    echo -e "${CYAN}⚙️ Creating build configuration for ${strategy} strategy...${NC}"
    
    mkdir -p "$BUILD_DIR"
    
    case "$strategy" in
        "aggressive")
            cat > "$config_file" << 'EOF'
{
    "build_strategy": "aggressive",
    "parallel_downloads": 4,
    "compression_level": "fast",
    "tool_selection": "comprehensive",
    "educational_modules": "full",
    "gui_tools": true,
    "consciousness_features": "enhanced",
    "target_size_gb": 8,
    "build_timeout_hours": 4,
    "resource_monitoring": true
}
EOF
            ;;
        "moderate")
            cat > "$config_file" << 'EOF'
{
    "build_strategy": "moderate", 
    "parallel_downloads": 2,
    "compression_level": "balanced",
    "tool_selection": "priority",
    "educational_modules": "essential",
    "gui_tools": true,
    "consciousness_features": "standard",
    "target_size_gb": 6,
    "build_timeout_hours": 3,
    "resource_monitoring": true
}
EOF
            ;;
        "conservative")
            cat > "$config_file" << 'EOF'
{
    "build_strategy": "conservative",
    "parallel_downloads": 1,
    "compression_level": "maximum",
    "tool_selection": "essential",
    "educational_modules": "core",
    "gui_tools": "selective",
    "consciousness_features": "lightweight",
    "target_size_gb": 4,
    "build_timeout_hours": 2,
    "resource_monitoring": true
}
EOF
            ;;
    esac
    
    echo -e "  📄 Configuration saved: ${GREEN}$config_file${NC}"
}

generate_tool_selection() {
    local strategy="$1"
    local output_file="${BUILD_DIR}/selected-tools.txt"
    
    echo -e "${CYAN}🔧 Generating tool selection based on ParrotOS analysis...${NC}"
    
    if [[ -f "$TOOLS_INTEGRATION" ]]; then
        python3 -c "
import sys
sys.path.append('$SYNOS_ROOT/src/consciousness')
from parrot_tool_integration import ParrotOSToolDatabase, ToolComplexity

# Initialize database
db = ParrotOSToolDatabase()

# Strategy-based selection
strategy = '$strategy'
selected_tools = []

if strategy == 'aggressive':
    # Include all high-priority tools
    selected_tools = db.get_high_priority_tools()
elif strategy == 'moderate':
    # Top 30 tools by priority and educational value
    all_tools = list(db.tools.values())
    selected_tools = sorted(all_tools, 
                          key=lambda x: (x.installation_priority, x.educational_value), 
                          reverse=True)[:30]
else:  # conservative
    # Essential beginner-friendly tools only
    selected_tools = [t for t in db.get_beginner_friendly_tools() 
                     if t.installation_priority >= 4][:15]

# Output tool list
for tool in selected_tools:
    print(f'{tool.name}:{tool.debian_package}:{tool.category.name}:{tool.complexity.name}')
" > "$output_file"
        
        local tool_count=$(wc -l < "$output_file")
        echo -e "  📦 Selected ${GREEN}${tool_count}${NC} tools for ${strategy} build"
        
        # Show top 5 tools
        echo -e "  🔝 Top tools:"
        head -5 "$output_file" | while IFS=: read -r name package category complexity; do
            echo -e "    • ${GREEN}$name${NC} ($category, $complexity)"
        done
        
    else
        echo -e "  ⚠️ Using fallback tool selection"
        # Fallback essential tools
        cat > "$output_file" << 'EOF'
nmap:nmap:INFORMATION_GATHERING:BEGINNER
wireshark:wireshark:SNIFFING_SPOOFING:INTERMEDIATE
burpsuite:burpsuite:WEB_APPLICATION_ANALYSIS:INTERMEDIATE
metasploit-framework:metasploit-framework:EXPLOITATION_TOOLS:ADVANCED
aircrack-ng:aircrack-ng:WIRELESS_ATTACKS:INTERMEDIATE
john:john:PASSWORD_ATTACKS:INTERMEDIATE
EOF
    fi
}

create_consciousness_config() {
    local strategy="$1"
    local config_file="${BUILD_DIR}/consciousness-config.py"
    
    echo -e "${CYAN}🧠 Configuring AI consciousness system...${NC}"
    
    cat > "$config_file" << EOF
#!/usr/bin/env python3

# SynOS Consciousness Configuration - ParrotOS Enhanced
# Strategy: $strategy

CONSCIOUSNESS_CONFIG = {
    'strategy': '$strategy',
    'web_port': 8080,
    'auto_start': True,
    'education_mode': True,
    'parrot_integration': True,
    'ai_recommendations': True,
    'progress_tracking': True,
    'tool_tutorials': True,
    'security_challenges': True,
    'network_labs': True
}

# Tool categories to emphasize based on strategy
if '$strategy' == 'aggressive':
    CONSCIOUSNESS_CONFIG.update({
        'advanced_tools': True,
        'expert_modules': True,
        'research_features': True,
        'multi_user': True
    })
elif '$strategy' == 'moderate':
    CONSCIOUSNESS_CONFIG.update({
        'intermediate_tools': True,
        'guided_learning': True,
        'practical_labs': True
    })
else:  # conservative
    CONSCIOUSNESS_CONFIG.update({
        'beginner_mode': True,
        'step_by_step': True,
        'safety_features': True,
        'simple_interface': True
    })

print("SynOS Consciousness configured for", CONSCIOUSNESS_CONFIG['strategy'], "strategy")
EOF
    
    echo -e "  🧠 Consciousness configuration: ${GREEN}Ready${NC}"
}

estimate_build_time() {
    local strategy="$1"
    local cpu_cores=$(nproc)
    local memory_gb=$(free -g | awk 'NR==2{printf "%.0f", $2}')
    
    echo -e "${CYAN}⏱️ Estimating build time...${NC}"
    
    # Base times in minutes for single core, 4GB RAM
    local base_times=(["aggressive"]=180 ["moderate"]=120 ["conservative"]=80)
    local base_time=${base_times[$strategy]}
    
    # Adjust for CPU cores (diminishing returns)
    local cpu_factor=$(echo "scale=2; 1 / (1 + 0.3 * ($cpu_cores - 1))" | bc)
    
    # Adjust for memory (more memory helps with parallel operations)
    local memory_factor=1.0
    if (( memory_gb >= 8 )); then
        memory_factor=0.8
    elif (( memory_gb >= 16 )); then
        memory_factor=0.6
    fi
    
    local estimated_minutes=$(echo "scale=0; $base_time * $cpu_factor * $memory_factor" | bc)
    local hours=$((estimated_minutes / 60))
    local minutes=$((estimated_minutes % 60))
    
    echo -e "  ⏰ Estimated time: ${GREEN}${hours}h ${minutes}m${NC}"
    echo -e "  🎯 Strategy: ${GREEN}$strategy${NC} build"
    
    return $estimated_minutes
}

confirm_build() {
    local strategy="$1"
    local estimated_time="$2"
    
    echo ""
    echo -e "${YELLOW}🚨 Build Confirmation${NC}"
    echo -e "${YELLOW}════════════════════${NC}"
    echo -e "Strategy: ${GREEN}$strategy${NC}"
    echo -e "Estimated Time: ${GREEN}$estimated_time minutes${NC}"
    echo -e "ParrotOS Tools: ${GREEN}Integrated${NC}"
    echo -e "AI Consciousness: ${GREEN}Enhanced${NC}"
    echo ""
    
    read -p "$(echo -e ${CYAN}Continue with SynOS ParrotOS-inspired build? [y/N]: ${NC})" -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        echo -e "${YELLOW}Build cancelled by user${NC}"
        return 1
    fi
}

launch_build() {
    local strategy="$1"
    local builder_script="${SYNOS_ROOT}/scripts/build/parrot-inspired-builder.sh"
    
    echo -e "${GREEN}🚀 Launching SynOS ParrotOS-inspired build...${NC}"
    
    if [[ ! -f "$builder_script" ]]; then
        echo -e "${RED}❌ Builder script not found: $builder_script${NC}"
        return 1
    fi
    
    # Make script executable
    chmod +x "$builder_script"
    
    # Create build log
    local build_log="${BUILD_DIR}/parrot-build-$(date +%Y%m%d-%H%M%S).log"
    
    echo -e "📝 Build log: ${GREEN}$build_log${NC}"
    echo -e "🎯 Strategy: ${GREEN}$strategy${NC}"
    echo ""
    
    # Launch with strategy configuration
    SYNOS_BUILD_STRATEGY="$strategy" sudo -E "$builder_script" 2>&1 | tee "$build_log"
    
    local build_result=${PIPESTATUS[0]}
    
    if [[ $build_result -eq 0 ]]; then
        echo -e "${GREEN}✅ SynOS ParrotOS-enhanced build completed successfully!${NC}"
        
        # Show final ISO location
        local iso_file=$(find "$BUILD_DIR" -name "SynOS-*.iso" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
        if [[ -f "$iso_file" ]]; then
            local iso_size=$(du -h "$iso_file" | cut -f1)
            echo -e "📀 ISO Ready: ${GREEN}$iso_file${NC} (${iso_size})"
            
            # Generate checksums
            cd "$(dirname "$iso_file")"
            sha256sum "$(basename "$iso_file")" > "${iso_file}.sha256"
            echo -e "🔒 Checksum: ${GREEN}${iso_file}.sha256${NC}"
        fi
        
    else
        echo -e "${RED}❌ Build failed with exit code: $build_result${NC}"
        echo -e "📝 Check build log: ${YELLOW}$build_log${NC}"
        return 1
    fi
}

show_parrotos_insights() {
    echo -e "${CYAN}🦜 ParrotOS Insights Applied:${NC}"
    echo "  • 500+ security tools from comprehensive analysis"
    echo "  • Educational progression from beginner to expert"
    echo "  • AI-powered tool recommendations"
    echo "  • MATE desktop environment (ParrotOS default)"
    echo "  • Debian base with Kali security repositories" 
    echo "  • Live boot with persistence support"
    echo "  • Forensics mode for investigations"
    echo "  • Anonymity tools integration"
    echo "  • Web-based consciousness dashboard"
    echo "  • Modular learning system"
    echo ""
}

main() {
    print_smart_banner
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}❌ Don't run this launcher as root${NC}"
        echo -e "The launcher will use sudo when needed"
        exit 1
    fi
    
    show_parrotos_insights
    
    # Analyze system and determine strategy
    local strategy=$(analyze_system_resources)
    echo ""
    
    # Check ParrotOS integration
    check_parrotos_integration
    echo ""
    
    # Generate configurations
    create_build_config "$strategy"
    generate_tool_selection "$strategy"
    create_consciousness_config "$strategy"
    echo ""
    
    # Estimate build time
    local estimated_time
    estimated_time=$(estimate_build_time "$strategy")
    echo ""
    
    # Confirm and launch
    if confirm_build "$strategy" "$estimated_time"; then
        echo ""
        launch_build "$strategy"
    fi
}

# Handle script arguments
case "${1:-}" in
    "conservative"|"moderate"|"aggressive")
        strategy="$1"
        print_smart_banner
        show_parrotos_insights
        create_build_config "$strategy"
        generate_tool_selection "$strategy" 
        create_consciousness_config "$strategy"
        estimate_build_time "$strategy"
        echo ""
        launch_build "$strategy"
        ;;
    "help"|"-h"|"--help")
        echo "SynOS Smart ParrotOS-Inspired Builder"
        echo ""
        echo "Usage: $0 [strategy]"
        echo ""
        echo "Strategies:"
        echo "  conservative  - Minimal resource usage, essential tools only"
        echo "  moderate      - Balanced approach, priority tools" 
        echo "  aggressive    - Full ParrotOS-inspired build with all tools"
        echo "  (none)        - Auto-detect optimal strategy"
        echo ""
        echo "The builder leverages comprehensive ParrotOS 6.4 analysis to create"
        echo "an enhanced SynOS with 500+ security tools and AI consciousness."
        ;;
    *)
        main
        ;;
esac
