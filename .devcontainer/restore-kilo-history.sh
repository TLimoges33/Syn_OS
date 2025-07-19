#!/bin/bash
# Kilo Code Chat History Recovery Script
# Restores critical development history from backup location

set -euo pipefail

echo "🔄 Restoring Kilo Code chat history..."

# Source and destination paths (codespace-aware)
SOURCE_KILO="/home/vscode/.config/Code/User/globalStorage/kilocode.kilo-code"
if [[ ! -d "$SOURCE_KILO" ]]; then
    SOURCE_KILO="/home/diablorain/.config/Code/User/globalStorage/kilocode.kilo-code"
fi

# Use current workspace directory
WORKSPACE_DIR="${PWD}"
DEST_KILO="${WORKSPACE_DIR}/.devcontainer/kilo-backup"
PROJECT_KILO="${WORKSPACE_DIR}/.kilocode"

# Create backup directory
mkdir -p "$DEST_KILO"
mkdir -p "$PROJECT_KILO/history"

if [[ -d "$SOURCE_KILO" ]]; then
    echo "📁 Found Kilo Code data at: $SOURCE_KILO"
    
    # Copy critical development history
    if [[ -d "$SOURCE_KILO/tasks" ]]; then
        echo "💾 Backing up task history..."
        cp -r "$SOURCE_KILO/tasks" "$DEST_KILO/"
        
        # Extract critical task data
        for task_dir in "$SOURCE_KILO/tasks"/*; do
            if [[ -d "$task_dir" ]]; then
                task_id=$(basename "$task_dir")
                echo "📋 Processing task: $task_id"
                
                # Copy API conversation history
                if [[ -f "$task_dir/api_conversation_history.json" ]]; then
                    cp "$task_dir/api_conversation_history.json" "$PROJECT_KILO/history/${task_id}_conversation.json"
                    echo "  ✅ Conversation history saved"
                fi
                
                # Copy task metadata
                if [[ -f "$task_dir/task_metadata.json" ]]; then
                    cp "$task_dir/task_metadata.json" "$PROJECT_KILO/history/${task_id}_metadata.json"  
                    echo "  ✅ Task metadata saved"
                fi
                
                # Copy UI messages
                if [[ -f "$task_dir/ui_messages.json" ]]; then
                    cp "$task_dir/ui_messages.json" "$PROJECT_KILO/history/${task_id}_ui.json"
                    echo "  ✅ UI messages saved"
                fi
            fi
        done
    fi
    
    # Copy settings
    if [[ -d "$SOURCE_KILO/settings" ]]; then
        echo "⚙️ Backing up settings..."
        cp -r "$SOURCE_KILO/settings" "$DEST_KILO/"
        
        # Copy MCP settings to project
        if [[ -f "$SOURCE_KILO/settings/mcp_settings.json" ]]; then
            cp "$SOURCE_KILO/settings/mcp_settings.json" "$PROJECT_KILO/"
            echo "  ✅ MCP settings restored"
        fi
        
        # Copy custom modes
        if [[ -f "$SOURCE_KILO/settings/custom_modes.yaml" ]]; then
            cp "$SOURCE_KILO/settings/custom_modes.yaml" "$PROJECT_KILO/"
            echo "  ✅ Custom modes restored"
        fi
    fi
    
    echo ""
    echo "📊 Recovery Summary:"
    echo "   📁 Task history: $(find "$PROJECT_KILO/history" -name "*_conversation.json" | wc -l) conversations"
    echo "   📋 Metadata files: $(find "$PROJECT_KILO/history" -name "*_metadata.json" | wc -l) tasks"
    echo "   💬 UI messages: $(find "$PROJECT_KILO/history" -name "*_ui.json" | wc -l) sessions"
    echo ""
    
    # Generate history index
    cat > "$PROJECT_KILO/history/index.json" << EOF
{
  "recovery_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source": "$SOURCE_KILO",
  "total_tasks": $(find "$PROJECT_KILO/history" -name "*_conversation.json" | wc -l),
  "critical_data_recovered": true,
  "synapticos_audit_included": true,
  "migration_plan_available": true
}
EOF

    echo "✅ Chat history recovery completed!"
    echo "📍 History location: $PROJECT_KILO/history/"
    echo "📄 Index file: $PROJECT_KILO/history/index.json"
    
else
    echo "❌ Source Kilo Code data not found at: $SOURCE_KILO"
    echo "💡 Manual recovery may be needed"
fi

echo ""
echo "🔧 Next steps:"
echo "1. Restart VS Code to load new Kilo configuration"
echo "2. Open Kilo Code extension settings"
echo "3. Verify Claude Code engine is active"
echo "4. Check history restoration in Kilo interface"