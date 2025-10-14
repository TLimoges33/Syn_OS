#!/bin/bash

# SynOS Testing Framework Update Script
# Date: September 18, 2025

echo "🧪 SynOS Testing Framework Update"
echo "================================="

BASE_DIR="/home/diablorain/Syn_OS"
TEST_BACKUP_DIR="$BASE_DIR/archive/test-updates-backup-$(date +%Y%m%d-%H%M%S)"

echo "Creating test backup: $TEST_BACKUP_DIR"
mkdir -p "$TEST_BACKUP_DIR"

# Function to update test files
update_test_file() {
    local file="$1"
    local backup_file="$TEST_BACKUP_DIR/$(basename "$file")"
    
    # Create backup
    cp "$file" "$backup_file"
    
    # Update test imports and references
    sed -i 's/syn-consciousness/syn-ai/g' "$file"
    sed -i 's/consciousness::/ai::/g' "$file"
    sed -i 's/ConsciousnessInterface/AIInterface/g' "$file"
    sed -i 's/consciousness_/ai_/g' "$file"
    sed -i 's/test_consciousness/test_ai/g' "$file"
    sed -i 's/#\[test\].*consciousness/#[test] // AI system test/g' "$file"
    
    echo "   Updated: $(basename "$file")"
}

echo "1. Updating test configuration files..."
find "$BASE_DIR/tests" -name "*.toml" -o -name "*.rs" | while read file; do
    if grep -q "consciousness" "$file" 2>/dev/null; then
        update_test_file "$file"
    fi
done

echo "2. Updating integration tests..."
find "$BASE_DIR" -name "*test*.rs" -not -path "*/archive/*" -not -path "*/target/*" | while read file; do
    if grep -q "consciousness" "$file" 2>/dev/null; then
        update_test_file "$file"
    fi
done

echo "3. Creating new AI module tests..."
mkdir -p "$BASE_DIR/tests/ai_module"

cat > "$BASE_DIR/tests/ai_module/mod.rs" << 'EOF'
//! AI Module Integration Tests
//! 
//! Tests for the SynOS AI system functionality

#[cfg(test)]
mod tests {
    use syn_ai::{AIState, init, get_state};

    #[test]
    fn test_ai_initialization() {
        // Test AI module initialization
        init();
        let state = get_state();
        assert!(state.optimization_level > 0);
    }

    #[test]
    fn test_ai_state_retrieval() {
        // Test AI state retrieval
        let state = get_state();
        assert!(matches!(state.security_level, syn_ai::security::SecurityLevel::_));
    }

    #[test]
    fn test_ai_inference() {
        // Test basic AI inference
        let input = vec![1.0, 2.0, 3.0];
        let output = syn_ai::process_inference(&input);
        assert_eq!(output.len(), input.len());
    }
}
EOF

cat > "$BASE_DIR/tests/ai_module/Cargo.toml" << 'EOF'
[package]
name = "ai_module_tests"
version.workspace = true
edition.workspace = true

[dependencies]
syn-ai = { path = "../../core/ai" }

[features]
default = []
EOF

echo "4. Summary of remaining test files with old terminology:"
find "$BASE_DIR" -name "*test*.rs" -not -path "*/archive/*" -not -path "*/target/*" -exec grep -l "consciousness" {} \; 2>/dev/null | head -5

echo ""
echo "✅ Testing framework update completed"
echo "📁 Backup stored in: $TEST_BACKUP_DIR"
echo "🧪 New AI tests: $BASE_DIR/tests/ai_module/"
