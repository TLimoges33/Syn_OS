#!/bin/bash
# Quick build monitor - shows current progress

LOGFILE=$(ls -t /tmp/full-distribution-build-*.log 2>/dev/null | head -1)

if [ -z "$LOGFILE" ]; then
    echo "No build log found"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           SynOS Full Distribution Build Monitor              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Log file: $LOGFILE"
echo ""

# Show current step
CURRENT_STEP=$(grep -oP '\[Step \K[0-9]+/[0-9]+' "$LOGFILE" | tail -1)
if [ -n "$CURRENT_STEP" ]; then
    echo "Current Progress: Step $CURRENT_STEP"
fi

# Show last phase
LAST_PHASE=$(grep -oP '╚.*╝' "$LOGFILE" | tail -1)
if [ -n "$LAST_PHASE" ]; then
    echo "$LAST_PHASE"
fi

echo ""
echo "Recent activity (last 30 lines):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -30 "$LOGFILE" | grep -v "^$"

echo ""
echo "Tool Installation Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -c "✓.*installed" "$LOGFILE" 2>/dev/null | xargs -I{} echo "  Tools installed: {}"
grep -c "⚠.*failed" "$LOGFILE" 2>/dev/null | xargs -I{} echo "  Tools failed: {}"

echo ""
echo "To watch live: tail -f $LOGFILE"
