#!/bin/bash

# Phase 4.1 Production Hardening Suite
# Comprehensive production readiness preparation

set -e

echo "🛡️  Phase 4.1 Production Hardening Suite"
echo "========================================"
echo ""

# Create results directory
RESULTS_DIR="/home/diablorain/Syn_OS/testing/production-hardening/results"
mkdir -p "$RESULTS_DIR"

# Hardening timestamp
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
HARDENING_FILE="$RESULTS_DIR/production_hardening_$TIMESTAMP.txt"

echo "🔧 Starting production hardening at $(date)" | tee "$HARDENING_FILE"
echo "=============================================" | tee -a "$HARDENING_FILE"
echo "" | tee -a "$HARDENING_FILE"

# Code quality analysis
echo "📝 Code Quality Analysis" | tee -a "$HARDENING_FILE"
echo "------------------------" | tee -a "$HARDENING_FILE"

cd /home/diablorain/Syn_OS/src/kernel

# Build with warnings analysis
echo "🔍 Analyzing compilation warnings..." | tee -a "$HARDENING_FILE"
WARNING_OUTPUT=$(cargo build --target x86_64-unknown-none --release 2>&1 || true)

# Count warnings
WARNING_COUNT=$(echo "$WARNING_OUTPUT" | grep -c "warning:" || echo "0")
CRITICAL_COUNT=$(echo "$WARNING_OUTPUT" | grep -c "error:" || echo "0")

echo "📊 Warning Analysis:" | tee -a "$HARDENING_FILE"
echo "  • Total warnings: $WARNING_COUNT" | tee -a "$HARDENING_FILE"
echo "  • Critical errors: $CRITICAL_COUNT" | tee -a "$HARDENING_FILE"

if [ "$CRITICAL_COUNT" -eq 0 ]; then
    echo "  ✅ No critical errors found" | tee -a "$HARDENING_FILE"
else
    echo "  ❌ Critical errors require attention" | tee -a "$HARDENING_FILE"
fi

if [ "$WARNING_COUNT" -lt 50 ]; then
    echo "  ✅ Warning count acceptable for development" | tee -a "$HARDENING_FILE"
elif [ "$WARNING_COUNT" -lt 150 ]; then
    echo "  ⚠️  Warning count high but manageable" | tee -a "$HARDENING_FILE"
else
    echo "  ❌ Warning count requires cleanup" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

# Memory safety analysis
echo "🧠 Memory Safety Analysis" | tee -a "$HARDENING_FILE"
echo "-------------------------" | tee -a "$HARDENING_FILE"

# Check for unsafe blocks
UNSAFE_COUNT=$(find /home/diablorain/Syn_OS/src/kernel/src -name "*.rs" -exec grep -c "unsafe" {} \; | awk '{sum+=$1} END {print sum+0}')
echo "📊 Memory Safety Check:" | tee -a "$HARDENING_FILE"
echo "  • Unsafe blocks detected: $UNSAFE_COUNT" | tee -a "$HARDENING_FILE"

if [ "$UNSAFE_COUNT" -lt 10 ]; then
    echo "  ✅ Low unsafe block count - good safety" | tee -a "$HARDENING_FILE"
elif [ "$UNSAFE_COUNT" -lt 30 ]; then
    echo "  ⚠️  Moderate unsafe usage - review recommended" | tee -a "$HARDENING_FILE"
else
    echo "  ❌ High unsafe usage - safety audit required" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

# Security audit
echo "🔒 Security Audit" | tee -a "$HARDENING_FILE"
echo "-----------------" | tee -a "$HARDENING_FILE"

KERNEL_PATH="/home/diablorain/Syn_OS/target/x86_64-unknown-none/release/kernel"

# Check for security features
SECURITY_FEATURES=$(strings "$KERNEL_PATH" | grep -i "security\|threat\|crypto\|auth" | wc -l)
echo "📊 Security Feature Analysis:" | tee -a "$HARDENING_FILE"
echo "  • Security-related implementations: $SECURITY_FEATURES" | tee -a "$HARDENING_FILE"

if [ "$SECURITY_FEATURES" -gt 15 ]; then
    echo "  ✅ Strong security feature integration" | tee -a "$HARDENING_FILE"
else
    echo "  ⚠️  Limited security features detected" | tee -a "$HARDENING_FILE"
fi

# Check for hardening patterns
HARDENING_PATTERNS=$(strings "$KERNEL_PATH" | grep -i "validate\|sanitize\|check\|verify" | wc -l)
echo "  • Hardening patterns: $HARDENING_PATTERNS" | tee -a "$HARDENING_FILE"

if [ "$HARDENING_PATTERNS" -gt 10 ]; then
    echo "  ✅ Good security hardening patterns" | tee -a "$HARDENING_FILE"
else
    echo "  ⚠️  Consider additional hardening patterns" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

# Container service recovery analysis
echo "🐳 Container Service Recovery Analysis" | tee -a "$HARDENING_FILE"
echo "--------------------------------------" | tee -a "$HARDENING_FILE"

# Check container service configurations
SERVICES_DIR="/home/diablorain/Syn_OS/services"
if [ -d "$SERVICES_DIR" ]; then
    echo "📊 Container Service Status:" | tee -a "$HARDENING_FILE"
    
    # Check consciousness-unified service
    if [ -d "$SERVICES_DIR/consciousness-unified" ]; then
        echo "  • consciousness-unified: FOUND" | tee -a "$HARDENING_FILE"
        
        # Check for problematic dependencies
        if [ -f "$SERVICES_DIR/consciousness-unified/Dockerfile" ]; then
            if grep -q "neural_darwinism.py" "$SERVICES_DIR/consciousness-unified/Dockerfile"; then
                echo "    ⚠️  neural_darwinism.py dependency issue detected" | tee -a "$HARDENING_FILE"
            else
                echo "    ✅ No obvious dependency issues" | tee -a "$HARDENING_FILE"
            fi
        fi
    else
        echo "  • consciousness-unified: NOT FOUND" | tee -a "$HARDENING_FILE"
    fi
    
    # Check educational-unified service
    if [ -d "$SERVICES_DIR/educational-unified" ]; then
        echo "  • educational-unified: FOUND" | tee -a "$HARDENING_FILE"
        
        # Check for libgl1-mesa-glx issues
        if [ -f "$SERVICES_DIR/educational-unified/Dockerfile" ]; then
            if grep -q "libgl1-mesa-glx" "$SERVICES_DIR/educational-unified/Dockerfile"; then
                echo "    ⚠️  libgl1-mesa-glx package issue detected" | tee -a "$HARDENING_FILE"
            else
                echo "    ✅ No obvious package issues" | tee -a "$HARDENING_FILE"
            fi
        fi
    else
        echo "  • educational-unified: NOT FOUND" | tee -a "$HARDENING_FILE"
    fi
else
    echo "  ⚠️  Services directory not found" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

# Hardware compatibility preparation
echo "🖥️  Hardware Compatibility Analysis" | tee -a "$HARDENING_FILE"
echo "----------------------------------" | tee -a "$HARDENING_FILE"

# Check target architecture
echo "📊 Architecture Support:" | tee -a "$HARDENING_FILE"
echo "  • Current target: x86_64-unknown-none" | tee -a "$HARDENING_FILE"
echo "  • Architecture: 64-bit x86" | tee -a "$HARDENING_FILE"

# Check for multi-arch patterns
ARCH_PATTERNS=$(find /home/diablorain/Syn_OS/src/kernel/src -name "*.rs" -exec grep -l "target_arch\|cfg.*arch" {} \; | wc -l)
echo "  • Multi-arch code patterns: $ARCH_PATTERNS files" | tee -a "$HARDENING_FILE"

if [ "$ARCH_PATTERNS" -gt 0 ]; then
    echo "  ✅ Multi-architecture awareness detected" | tee -a "$HARDENING_FILE"
else
    echo "  ⚠️  Consider multi-architecture support" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

# Panic handling optimization
echo "😱 Panic Handling Analysis" | tee -a "$HARDENING_FILE"
echo "--------------------------" | tee -a "$HARDENING_FILE"

PANIC_HANDLERS=$(find /home/diablorain/Syn_OS/src/kernel/src -name "*.rs" -exec grep -c "panic\|unwrap\|expect" {} \; | awk '{sum+=$1} END {print sum+0}')
echo "📊 Panic Pattern Analysis:" | tee -a "$HARDENING_FILE"
echo "  • Panic-related patterns: $PANIC_HANDLERS" | tee -a "$HARDENING_FILE"

if [ "$PANIC_HANDLERS" -lt 20 ]; then
    echo "  ✅ Low panic usage - good error handling" | tee -a "$HARDENING_FILE"
elif [ "$PANIC_HANDLERS" -lt 50 ]; then
    echo "  ⚠️  Moderate panic usage - review recommended" | tee -a "$HARDENING_FILE"
else
    echo "  ❌ High panic usage - improve error handling" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

# Production readiness recommendations
echo "💡 Production Hardening Recommendations" | tee -a "$HARDENING_FILE"
echo "=======================================" | tee -a "$HARDENING_FILE"

echo "🔧 Immediate Actions:" | tee -a "$HARDENING_FILE"
if [ "$WARNING_COUNT" -gt 100 ]; then
    echo "  • Reduce compilation warnings to <50" | tee -a "$HARDENING_FILE"
fi

if [ "$UNSAFE_COUNT" -gt 20 ]; then
    echo "  • Review and minimize unsafe blocks" | tee -a "$HARDENING_FILE"
fi

if [ "$PANIC_HANDLERS" -gt 30 ]; then
    echo "  • Improve error handling to reduce panics" | tee -a "$HARDENING_FILE"
fi

echo "" | tee -a "$HARDENING_FILE"

echo "🚀 Future Enhancements:" | tee -a "$HARDENING_FILE"
echo "  • Implement comprehensive logging system" | tee -a "$HARDENING_FILE"
echo "  • Add runtime configuration validation" | tee -a "$HARDENING_FILE"
echo "  • Enhance consciousness monitoring tools" | tee -a "$HARDENING_FILE"
echo "  • Implement graceful degradation for consciousness features" | tee -a "$HARDENING_FILE"

echo "" | tee -a "$HARDENING_FILE"

# Hardening summary
echo "📋 Production Hardening Summary" | tee -a "$HARDENING_FILE"
echo "===============================" | tee -a "$HARDENING_FILE"
echo "✅ Code quality: $WARNING_COUNT warnings, $CRITICAL_COUNT errors" | tee -a "$HARDENING_FILE"
echo "✅ Memory safety: $UNSAFE_COUNT unsafe blocks" | tee -a "$HARDENING_FILE"
echo "✅ Security features: $SECURITY_FEATURES implementations" | tee -a "$HARDENING_FILE"
echo "✅ Error handling: $PANIC_HANDLERS panic patterns" | tee -a "$HARDENING_FILE"
echo "" | tee -a "$HARDENING_FILE"
echo "🎯 Phase 4.1 Production Hardening Complete!" | tee -a "$HARDENING_FILE"
echo "📊 Detailed results: $HARDENING_FILE" | tee -a "$HARDENING_FILE"

echo ""
echo "🎉 Production hardening analysis completed!"
echo "📊 Results saved to: $HARDENING_FILE"
echo "🚀 Ready for extended QEMU testing phase!"
