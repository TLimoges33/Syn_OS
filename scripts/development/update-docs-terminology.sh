#!/bin/bash

# SynOS Documentation Terminology Update Script
# Date: September 18, 2025

echo "📚 SynOS Documentation Terminology Update"
echo "=========================================="

BASE_DIR="/home/diablorain/Syn_OS"
DOCS_DIR="$BASE_DIR/docs"
BACKUP_DIR="$BASE_DIR/archive/docs-terminology-backup-$(date +%Y%m%d-%H%M%S)"

echo "Creating documentation backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$DOCS_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true

# Function to update terminology in documentation
update_doc_terminology() {
    local file="$1"
    
    # Create terms mapping
    sed -i 's/consciousness engine/AI engine/gi' "$file"
    sed -i 's/consciousness system/AI system/gi' "$file"
    sed -i 's/consciousness integration/AI integration/gi' "$file"
    sed -i 's/consciousness-aware/AI-aware/gi' "$file"
    sed -i 's/consciousness level/AI processing level/gi' "$file"
    sed -i 's/neural consciousness/neural networks/gi' "$file"
    sed -i 's/quantum consciousness/advanced algorithms/gi' "$file"
    sed -i 's/consciousness update/AI update/gi' "$file"
    sed -i 's/consciousness metrics/AI metrics/gi' "$file"
    sed -i 's/consciousness dashboard/AI dashboard/gi' "$file"
    sed -i 's/galactic consciousness/[REMOVED - was pseudo-scientific]/gi' "$file"
    sed -i 's/universal consciousness/[REMOVED - was pseudo-scientific]/gi' "$file"
    
    echo "   Updated: $(basename "$file")"
}

# Update active documentation files (not archive)
echo "1. Updating user documentation..."
find "$DOCS_DIR" -name "*.md" -not -path "*/archive/*" | while read file; do
    if grep -qi "consciousness" "$file" 2>/dev/null; then
        update_doc_terminology "$file"
    fi
done

echo "2. Creating new AI terminology reference..."
cat > "$DOCS_DIR/AI_TERMINOLOGY_REFERENCE.md" << 'EOF'
# SynOS AI Terminology Reference

**Updated**: September 18, 2025  
**Purpose**: Proper AI/ML terminology for SynOS documentation

## ✅ **Approved AI Terminology**

### **Core AI Components**
- **AI Engine** - The main artificial intelligence system
- **Neural Networks** - Machine learning neural network implementations
- **Pattern Recognition** - ML pattern matching and classification
- **Decision Engine** - AI-powered decision making algorithms
- **Inference Engine** - Logical reasoning and inference systems

### **System Integration**
- **AI-aware** - Systems that integrate with AI functionality
- **AI Integration** - The process of incorporating AI into system components
- **AI Dashboard** - User interface for monitoring AI systems
- **AI Metrics** - Performance and operational measurements

### **Events and Monitoring**
- **AI Update** - Events related to AI system changes
- **AI Events** - General AI system event category
- **Neural Network Update** - Specific neural network changes

## ❌ **Deprecated Pseudo-Scientific Terms**

### **Removed Terms**
- ~~Consciousness~~ → AI System
- ~~Galactic Consciousness~~ → [REMOVED - pseudo-scientific]
- ~~Quantum Consciousness~~ → Advanced Algorithms
- ~~Universal Consciousness~~ → [REMOVED - pseudo-scientific]
- ~~Neural Evolution~~ → Neural Network Training
- ~~Consciousness Level~~ → AI Processing Level

### **Why These Were Removed**
- **Unscientific**: No basis in computer science or AI research
- **Misleading**: Implied impossible capabilities
- **Unprofessional**: Not suitable for technical documentation

## 📋 **Documentation Guidelines**

1. **Use precise technical terms** from AI/ML literature
2. **Avoid anthropomorphic language** (no "awakening", "thinking", etc.)
3. **Reference real capabilities** only
4. **Follow industry standards** for AI terminology
EOF

echo "3. Summary of files still containing old terminology:"
grep -r "consciousness\|galactic\|quantum.*substrate" "$DOCS_DIR" --include="*.md" -l 2>/dev/null | grep -v archive | head -5

echo ""
echo "✅ Documentation terminology update completed"
echo "📁 Backup stored in: $BACKUP_DIR"
echo "📖 New reference: $DOCS_DIR/AI_TERMINOLOGY_REFERENCE.md"
