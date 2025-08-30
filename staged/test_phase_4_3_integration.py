#!/usr/bin/env python3
"""
Test AI Engine Integration with Kernel Module
This script demonstrates bidirectional communication between the AI engine and kernel module
"""

import sys
import os
sys.path.append('/home/diablorain/Syn_OS/src/ai-consciousness')
sys.path.append('/home/diablorain/Syn_OS/src/kernel-module')

from synos_ai_engine_fixed import SynOSAIEngine
import time
import json

def test_ai_kernel_integration():
    """Test full integration between AI engine and kernel module"""
    print("=== SynOS Phase 4.3: AI-Kernel Integration Test ===\n")
    
    # Initialize AI engine
    print("1. Initializing AI Engine...")
    ai_engine = SynOSAIEngine()
    
    # Connect to kernel
    print("2. Connecting to kernel module...")
    connected = ai_engine.connect_to_kernel()
    if not connected:
        print("❌ Kernel connection failed!")
        return False
    
    print("✅ Connected to kernel module")
    
    # Get initial status
    print("\n3. Reading kernel status...")
    kernel_status = ai_engine.get_kernel_status()
    print(f"Kernel Status: {json.dumps(kernel_status, indent=2)}")
    
    # Analyze consciousness
    print("\n4. Running AI consciousness analysis...")
    consciousness_state = ai_engine.analyze_consciousness_state()
    print(f"Consciousness Analysis:")
    print(f"  - Level: {consciousness_state.level:.2f}")
    print(f"  - Coherence: {consciousness_state.coherence:.2f}")
    print(f"  - Stability: {consciousness_state.stability:.2f}")
    print(f"  - Complexity: {consciousness_state.complexity:.2f}")
    print(f"  - Components: {consciousness_state.components}")
    
    # Make AI decision
    print("\n5. AI decision making...")
    decision = ai_engine.make_decision(consciousness_state)
    if decision:
        print(f"AI Decision Made:")
        print(f"  - Action: {decision.action}")
        print(f"  - Target: {decision.target}")
        print(f"  - Confidence: {decision.confidence:.2f}")
        print(f"  - Reasoning: {decision.reasoning}")
        
        # Execute the decision
        print("\n6. Executing AI decision...")
        success = ai_engine.execute_decision(decision)
        if success:
            print("✅ Decision executed successfully")
        else:
            print("❌ Decision execution failed")
    else:
        print("No decision needed - system optimal")
    
    # Test monitoring loop for a few iterations
    print("\n7. Testing short monitoring loop...")
    ai_engine.start_monitoring()
    
    print("Monitoring for 5 seconds...")
    time.sleep(5)
    
    ai_engine.stop_monitoring()
    
    # Final status report
    print("\n8. Final status report...")
    status_report = ai_engine.get_status_report()
    print(f"Final Status: {json.dumps(status_report, indent=2)}")
    
    print("\n✅ Integration test complete!")
    return True

if __name__ == "__main__":
    success = test_ai_kernel_integration()
    sys.exit(0 if success else 1)
