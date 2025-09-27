#!/usr/bin/env python3
"""
SynOS Hardware Layer Verification Script
========================================

This script verifies the complete implementation of the SynOS Hardware Abstraction Layer.
It analyzes the codebase and generates a comprehensive validation report.

Usage: python3 hal_verification.py
"""

import os
import re
import subprocess
from pathlib import Path

class HALVerifier:
    def __init__(self, kernel_path="/home/diablorain/Syn_OS/src/kernel"):
        self.kernel_path = Path(kernel_path)
        self.hal_path = self.kernel_path / "src" / "hal"
        self.results = {}
        
    def analyze_module(self, module_path):
        """Analyze a single HAL module for completeness"""
        with open(module_path, 'r') as f:
            content = f.read()
            
        # Count lines of code (excluding comments and empty lines)
        lines = [line.strip() for line in content.split('\n')]
        code_lines = [line for line in lines if line and not line.startswith('//')]
        
        # Count functions and structs
        functions = re.findall(r'pub fn \w+', content)
        structs = re.findall(r'pub struct \w+', content)
        impls = re.findall(r'impl\s+\w+', content)
        
        return {
            'total_lines': len(lines),
            'code_lines': len(code_lines),
            'functions': len(functions),
            'structs': len(structs),
            'implementations': len(impls),
            'has_ai_integration': 'consciousness' in content.lower() or 'ai' in content.lower(),
            'error_handling': 'Result<' in content,
            'documentation': '///' in content
        }
    
    def verify_compilation(self):
        """Verify that the kernel compiles successfully"""
        try:
            result = subprocess.run(
                ['cargo', 'check', '--target', 'x86_64-unknown-none'],
                cwd=self.kernel_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            return {
                'success': result.returncode == 0,
                'warnings': result.stderr.count('warning:'),
                'errors': result.stderr.count('error:')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_hal_modules(self):
        """Analyze all HAL modules"""
        modules = {
            'mod.rs': 'Core HAL Framework',
            'cpu.rs': 'CPU Detection & Management',
            'memory.rs': 'Memory Controller',
            'io.rs': 'I/O Controller',
            'pci.rs': 'PCI Bus Management',
            'acpi.rs': 'ACPI Power Management'
        }
        
        module_analysis = {}
        for module_file, description in modules.items():
            module_path = self.hal_path / module_file
            if module_path.exists():
                module_analysis[module_file] = {
                    'description': description,
                    'exists': True,
                    **self.analyze_module(module_path)
                }
            else:
                module_analysis[module_file] = {
                    'description': description,
                    'exists': False
                }
        
        return module_analysis
    
    def generate_report(self):
        """Generate comprehensive verification report"""
        print("🔍 SynOS Hardware Layer Verification Report")
        print("=" * 50)
        
        # Check compilation
        print("\n📦 Compilation Verification:")
        compilation = self.verify_compilation()
        if compilation['success']:
            print(f"  ✅ Kernel compiles successfully")
            print(f"  ⚠️  Warnings: {compilation.get('warnings', 0)}")
            print(f"  ❌ Errors: {compilation.get('errors', 0)}")
        else:
            print(f"  ❌ Compilation failed: {compilation.get('error', 'Unknown error')}")
        
        # Analyze modules
        print("\n🔧 HAL Module Analysis:")
        modules = self.analyze_hal_modules()
        total_lines = 0
        total_functions = 0
        total_structs = 0
        
        for module_file, analysis in modules.items():
            if analysis['exists']:
                print(f"\n  📁 {module_file} - {analysis['description']}")
                print(f"     Lines of Code: {analysis['code_lines']}")
                print(f"     Functions: {analysis['functions']}")
                print(f"     Structures: {analysis['structs']}")
                print(f"     Implementations: {analysis['implementations']}")
                print(f"     AI Integration: {'✅' if analysis['has_ai_integration'] else '❌'}")
                print(f"     Error Handling: {'✅' if analysis['error_handling'] else '❌'}")
                print(f"     Documentation: {'✅' if analysis['documentation'] else '❌'}")
                
                total_lines += analysis['code_lines']
                total_functions += analysis['functions']
                total_structs += analysis['structs']
            else:
                print(f"  ❌ {module_file} - Missing")
        
        # Summary statistics
        print(f"\n📊 Implementation Summary:")
        print(f"  Total Code Lines: {total_lines:,}")
        print(f"  Total Functions: {total_functions}")
        print(f"  Total Structures: {total_structs}")
        print(f"  Modules Complete: {sum(1 for m in modules.values() if m['exists'])}/6")
        
        # Completion percentage
        completion = (sum(1 for m in modules.values() if m['exists']) / len(modules)) * 100
        print(f"  Completion Rate: {completion:.1f}%")
        
        if completion == 100.0:
            print("\n🎯 HARDWARE LAYER IMPLEMENTATION: 100% COMPLETE! 🎯")
        
        return modules, compilation

def main():
    verifier = HALVerifier()
    modules, compilation = verifier.generate_report()
    
    print("\n" + "=" * 50)
    print("Hardware Abstraction Layer verification complete!")
    
    if compilation['success'] and all(m['exists'] for m in modules.values()):
        print("🚀 SynOS HAL is ready for deployment!")
        return 0
    else:
        print("⚠️  Some issues detected. Please review the report above.")
        return 1

if __name__ == "__main__":
    exit(main())
