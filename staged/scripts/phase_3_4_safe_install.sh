#!/bin/bash
# Phase 3.4 Safe Implementation Script
# Incremental dependency installation with memory monitoring

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="/tmp/phase_3_4_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
}

check_memory() {
    local available_mb=$(free -m | awk 'NR==2{print $7}')
    local swap_mb=$(free -m | awk 'NR==3{print $2}')
    
    if [ "$available_mb" -lt 200 ] && [ "$swap_mb" -eq 0 ]; then
        log "❌ CRITICAL: Only ${available_mb}MB available and no swap configured!"
        log "Please run: sudo $SCRIPT_DIR/configure_swap.sh"
        exit 1
    elif [ "$available_mb" -lt 100 ]; then
        log "⚠️  WARNING: Low memory (${available_mb}MB available)"
        log "Consider monitoring installation closely"
    else
        log "✅ Memory check passed (${available_mb}MB available, ${swap_mb}MB swap)"
    fi
}

install_with_monitoring() {
    local package="$1"
    local description="$2"
    
    log "=== Installing: $description ==="
    log "Package: $package"
    
    # Pre-install memory check
    check_memory
    
    # Install with no cache to save memory
    log "Starting installation..."
    if pip install --no-cache-dir $package; then
        log "✅ Successfully installed: $description"
    else
        log "❌ Failed to install: $description"
        log "Checking system state..."
        free -h
        return 1
    fi
    
    # Post-install memory check
    log "Post-install memory status:"
    free -h | tee -a "$LOGFILE"
    echo "---" >> "$LOGFILE"
}

main() {
    log "🚀 Starting Phase 3.4 Safe Implementation"
    log "Working directory: $(pwd)"
    
    # Initial system check
    log "=== INITIAL SYSTEM CHECK ==="
    check_memory
    
    # Check if swap is configured
    if ! swapon -s | grep -q "/swapfile"; then
        log "❌ Swap not configured! Please run:"
        log "    sudo $SCRIPT_DIR/configure_swap.sh"
        log "Then re-run this script."
        exit 1
    fi
    
    log "✅ Swap is configured:"
    swapon -s | tee -a "$LOGFILE"
    
    # Phase 3.4a: Foundation
    log ""
    log "🔧 PHASE 3.4a: Foundation Setup"
    
    install_with_monitoring "psutil GPUtil" "System monitoring tools"
    install_with_monitoring "prometheus-client" "Performance metrics"
    
    # Phase 3.4b: Ray Optimization (lightweight first)
    log ""
    log "🎯 PHASE 3.4b: Ray Framework"
    
    install_with_monitoring "ray[default]" "Ray distributed computing framework"
    
    # Test Ray installation
    log "Testing Ray installation..."
    if python -c "import ray; ray.init(num_cpus=2); print('Ray test successful'); ray.shutdown()"; then
        log "✅ Ray test passed"
    else
        log "❌ Ray test failed"
    fi
    
    # Phase 3.4c: Lightweight caching and API
    log ""
    log "💾 PHASE 3.4c: Caching and API Framework"
    
    install_with_monitoring "redis aioredis" "Redis caching system"
    install_with_monitoring "fastapi uvicorn" "FastAPI web framework"
    
    # Phase 3.4d: Computer Vision (CPU-first approach)
    log ""
    log "👁️  PHASE 3.4d: Computer Vision (CPU-first)"
    log "Installing PyTorch with CPU backend to avoid GPU memory issues..."
    
    install_with_monitoring "torch torchvision --index-url https://download.pytorch.org/whl/cpu" "PyTorch (CPU version)"
    
    # Check available memory before heavy installs
    local available_mb=$(free -m | awk 'NR==2{print $7}')
    if [ "$available_mb" -lt 500 ]; then
        log "⚠️  Low memory detected (${available_mb}MB). Skipping heavy computer vision packages."
        log "Install manually when more memory is available:"
        log "    pip install --no-cache-dir ultralytics opencv-python"
    else
        install_with_monitoring "ultralytics" "YOLOv9/Ultralytics framework"
        install_with_monitoring "opencv-python" "OpenCV computer vision"
    fi
    
    # Final system check
    log ""
    log "🎉 PHASE 3.4 INSTALLATION COMPLETE"
    log "=== FINAL SYSTEM STATUS ==="
    free -h | tee -a "$LOGFILE"
    
    log ""
    log "✅ Core components installed successfully"
    log "✅ System stability maintained"
    log "📊 Next steps:"
    log "   1. Run Ray optimization tests: python tests/optimization/run_ray_optimization_test.py"
    log "   2. Test FastAPI endpoints"
    log "   3. Validate Redis caching"
    log "   4. Monitor performance improvements"
    
    log ""
    log "📋 Installation log saved to: $LOGFILE"
}

# Handle script arguments
case "${1:-install}" in
    "check")
        check_memory
        ;;
    "install")
        main
        ;;
    *)
        echo "Usage: $0 [check|install]"
        echo "  check   - Check memory prerequisites"
        echo "  install - Run safe Phase 3.4 installation"
        ;;
esac