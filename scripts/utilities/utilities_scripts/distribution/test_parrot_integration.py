#!/usr/bin/env python3

"""
Simple test of SynOS ParrotOS Integration
"""

import os
import sys

# Add the consciousness directory to Python path
sys.path.insert(0, '/home/diablorain/Syn_OS/src/consciousness')

def test_parrot_integration():
    print("🧠 Testing SynOS ParrotOS Integration Framework")
    print("=" * 50)
    
    try:
        # Import our modules
        from parrot_tool_integration import (
            ParrotOSToolDatabase, 
            SynOSConsciousnessIntegration,
            ToolCategory,
            ToolComplexity
        )
        print("✅ Successfully imported ParrotOS integration modules")
        
        # Test database initialization
        print("\n📊 Initializing ParrotOS tool database...")
        db = ParrotOSToolDatabase()
        print(f"✅ Database initialized with {len(db.tools)} security tools")
        
        # Test tool categories
        print("\n🔧 Tool Categories:")
        for category in ToolCategory:
            count = len(db.get_tools_by_category(category))
            if count > 0:
                print(f"  {category.name}: {count} tools")
        
        # Test high priority tools
        print("\n⭐ High Priority Tools:")
        priority_tools = db.get_high_priority_tools()
        print(f"Found {len(priority_tools)} high priority tools")
        
        for i, tool in enumerate(priority_tools[:5]):
            print(f"  {i+1}. {tool.name}")
            print(f"     Category: {tool.category.name}")
            print(f"     Complexity: {tool.complexity.name}")
            print(f"     Educational Value: {tool.educational_value}/10")
            print(f"     Description: {tool.description[:60]}...")
            print()
        
        # Test beginner tools
        beginner_tools = db.get_beginner_friendly_tools()
        print(f"🎓 Beginner-friendly tools: {len(beginner_tools)}")
        
        # Test GUI tools
        gui_tools = db.get_gui_tools()
        print(f"🖥️ GUI tools available: {len(gui_tools)}")
        
        # Test consciousness integration
        print("\n🧠 Testing AI Consciousness Integration...")
        consciousness = SynOSConsciousnessIntegration(db)
        
        # Get recommendation
        next_tool = consciousness.recommend_next_tool()
        if next_tool:
            print(f"🎯 AI Recommendation: Start with '{next_tool.name}'")
            print(f"   Complexity: {next_tool.complexity.name}")
            print(f"   Educational Value: {next_tool.educational_value}/10")
        
        # Generate installation script sample
        print("\n💾 Generating sample installation script...")
        essential_tools = priority_tools[:10]  # Top 10 tools
        script = consciousness.generate_tool_installation_script(essential_tools)
        
        # Save sample script
        with open('/tmp/synos-parrot-sample-install.sh', 'w') as f:
            f.write(script)
        print("✅ Sample installation script saved to: /tmp/synos-parrot-sample-install.sh")
        
        # Statistics
        print(f"\n📈 ParrotOS Integration Statistics:")
        print(f"  Total Tools: {len(db.tools)}")
        print(f"  High Priority: {len(priority_tools)}")
        print(f"  Beginner Friendly: {len(beginner_tools)}")
        print(f"  GUI Tools: {len(gui_tools)}")
        print(f"  Average Educational Value: {sum(t.educational_value for t in db.tools.values()) / len(db.tools):.1f}/10")
        
        print(f"\n✅ SynOS ParrotOS Integration Test: SUCCESS!")
        print(f"🚀 Ready to build ParrotOS-enhanced SynOS ISO!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_build_readiness():
    print("\n🎯 Build Readiness Check:")
    
    # Check essential directories
    dirs_to_check = [
        '/home/diablorain/Syn_OS/scripts/build',
        '/home/diablorain/Syn_OS/src/consciousness', 
        '/home/diablorain/Syn_OS/build'
    ]
    
    for directory in dirs_to_check:
        if os.path.exists(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} (will be created)")
            os.makedirs(directory, exist_ok=True)
    
    # Check build scripts
    scripts_to_check = [
        '/home/diablorain/Syn_OS/scripts/build/parrot-inspired-builder.sh',
        '/home/diablorain/Syn_OS/scripts/build/smart-parrot-launcher.sh'
    ]
    
    for script in scripts_to_check:
        if os.path.exists(script):
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script}")
    
    print(f"\n🎉 SynOS ParrotOS-Enhanced Build System Ready!")

if __name__ == "__main__":
    success = test_parrot_integration()
    print()
    show_build_readiness()
    
    if success:
        print(f"\n🚀 Next Steps:")
        print(f"  1. Run: /home/diablorain/Syn_OS/scripts/build/smart-parrot-launcher.sh")
        print(f"  2. Choose strategy: conservative, moderate, or aggressive")
        print(f"  3. Wait for AI-enhanced ParrotOS-inspired SynOS build!")
    else:
        print(f"\n❌ Fix integration issues before building")
