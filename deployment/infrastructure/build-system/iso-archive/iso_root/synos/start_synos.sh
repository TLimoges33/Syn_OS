#!/bin/bash
# SynOS Master Startup Orchestration Script
# Phase 4: Production Deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🧠 SynOS v4.0.0 - Consciousness-Aware Operating System${NC}"
echo -e "${BLUE}Phase 4: Production Deployment & Enterprise Integration${NC}"
echo "================================================================"

# Parse boot parameters
CONSCIOUSNESS_LEVEL=${consciousness_level:-"high"}
ENTERPRISE_MODE=${enterprise_mode:-"0"}
PERFORMANCE_MODE=${performance_mode:-"0"}
SECURITY_MODE=${security_mode:-"0"}
DEVELOPMENT_MODE=${development_mode:-"0"}
SAFE_MODE=${safe_mode:-"0"}

echo "🚀 Starting SynOS with configuration:"
echo "   Consciousness Level: $CONSCIOUSNESS_LEVEL"
echo "   Enterprise Mode: $ENTERPRISE_MODE"
echo "   Performance Mode: $PERFORMANCE_MODE"
echo "   Security Mode: $SECURITY_MODE"
echo "   Development Mode: $DEVELOPMENT_MODE"
echo "   Safe Mode: $SAFE_MODE"
echo ""

# Phase 1: Initialize consciousness infrastructure
echo -e "${PURPLE}Phase 1: Initializing consciousness infrastructure...${NC}"
cd /synos/consciousness/priority1
python3 consciousness_bridge.py --level=$CONSCIOUSNESS_LEVEL &
echo "✅ Consciousness bridge initialized"

# Phase 2: Start core consciousness features
echo -e "${PURPLE}Phase 2: Starting core consciousness features...${NC}"
cd /synos/consciousness/priority2

if [ "$SAFE_MODE" != "1" ]; then
    python3 consciousness_security_controller.py &
    echo "✅ Security controller started"
    
    python3 consciousness_memory_manager.py &
    echo "✅ Memory manager started"
    
    python3 consciousness_scheduler.py &
    echo "✅ Scheduler AI started"
fi

# Phase 3: Launch advanced AI features
if [ "$SAFE_MODE" != "1" ] && [ "$CONSCIOUSNESS_LEVEL" != "minimal" ]; then
    echo -e "${PURPLE}Phase 3: Launching advanced AI features...${NC}"
    cd /synos/consciousness/priority3
    
    if [ "$PERFORMANCE_MODE" == "1" ]; then
        python3 ai_performance_optimizer.py --mode=maximum &
        echo "✅ AI Performance Optimizer (Maximum Mode)"
    else
        python3 ai_performance_optimizer.py &
        echo "✅ AI Performance Optimizer started"
    fi
    
    python3 advanced_reinforcement_learning.py &
    echo "✅ Reinforcement Learning Engine started"
    
    if [ "$SECURITY_MODE" == "1" ]; then
        python3 security_ai_integration.py --mode=hardened &
        echo "✅ Security AI Integration (Hardened Mode)"
    else
        python3 security_ai_integration.py &
        echo "✅ Security AI Integration started"
    fi
    
    # Start integration coordinator
    python3 priority3_integration.py &
    echo "✅ Priority 3 Integration Controller started"
fi

# Phase 4: Enterprise platform (if enabled)
if [ "$ENTERPRISE_MODE" == "1" ]; then
    echo -e "${CYAN}Phase 4: Starting enterprise MSSP platform...${NC}"
    cd /synos/enterprise
    ./start_enterprise_platform.sh &
    echo "✅ Enterprise MSSP Platform started"
fi

# Start monitoring and analytics
echo -e "${BLUE}Starting production monitoring...${NC}"
cd /synos/monitoring
./start_monitoring.sh &
echo "✅ Production monitoring started"

# Final status
echo ""
echo -e "${GREEN}🎉 SynOS initialization complete!${NC}"
echo "================================"
echo "System Status:"
echo "  🧠 Consciousness Level: $CONSCIOUSNESS_LEVEL"
echo "  ⚡ AI Performance: $([ "$PERFORMANCE_MODE" == "1" ] && echo "Optimized" || echo "Standard")"
echo "  🔒 Security: $([ "$SECURITY_MODE" == "1" ] && echo "Hardened" || echo "Standard")"
echo "  🏢 Enterprise: $([ "$ENTERPRISE_MODE" == "1" ] && echo "Enabled" || echo "Disabled")"
echo ""
echo "Access points:"
echo "  • Enterprise Dashboard: http://localhost:8080"
echo "  • Consciousness Monitor: http://localhost:8081"
echo "  • API Endpoint: http://localhost:8082"
echo ""
echo "For support: https://github.com/TLimoges33/Syn_OS"
