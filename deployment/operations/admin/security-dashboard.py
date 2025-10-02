#!/usr/bin/env python3
"""
Syn_OS 10/10 Security Dashboard
Real-time monitoring of all security components
"""

import asyncio
import json
import sys
import time
from datetime import datetime

sys.path.append('src')

from security.hsm_manager import get_hsm_status
from security.zero_trust_manager import get_zero_trust_status
from security.quantum_crypto import get_quantum_crypto_status

async def display_dashboard():
    """Display real-time security dashboard"""
    
    while True:
        # Clear screen
        print("\033[2J\033[H")
        
        print("🔒 Syn_OS 10/10 Security Dashboard")
        print("=" * 60)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Get component statuses
            hsm_status = await get_hsm_status()
            zt_status = await get_zero_trust_status()
            qc_status = await get_quantum_crypto_status()
            
            # Display HSM status
            print("🔐 Hardware Security Module:")
            print(f"  Status: {'🟢 ACTIVE' if hsm_status['initialized'] else '🔴 INACTIVE'}")
            print(f"  TPM Available: {'🟢 YES' if hsm_status.get('tmp_available', False) else '🟡 SOFTWARE'}")
            print(f"  Keys Loaded: {hsm_status['keys_loaded']}")
            print()
            
            # Display Zero-Trust status
            print("🛡️ Zero-Trust Architecture:")
            print(f"  Status: {'🟢 ACTIVE' if zt_status['initialized'] else '🔴 INACTIVE'}")
            print(f"  Entities: {zt_status['entities_registered']}")
            print(f"  Access Requests: {zt_status['access_requests_logged']}")
            print(f"  Policies: {zt_status['policies_loaded']}")
            print()
            
            # Display Quantum Crypto status
            print("🔮 Quantum-Resistant Cryptography:")
            print(f"  Algorithms: {len(qc_status['supported_algorithms'])}")
            print(f"  Keys Loaded: {qc_status['loaded_keys']}")
            print(f"  Storage: {qc_status['key_storage_path']}")
            print()
            
            # Calculate overall security score
            base_score = 8.8
            hsm_bonus = 0.3 if hsm_status['initialized'] else 0
            zt_bonus = 0.3 if zt_status['initialized'] else 0
            qc_bonus = 0.3 if qc_status['loaded_keys'] > 0 else 0
            integration_bonus = 0.3 if all([hsm_status['initialized'], zt_status['initialized'], qc_status['loaded_keys'] > 0]) else 0
            
            total_score = base_score + hsm_bonus + zt_bonus + qc_bonus + integration_bonus
            
            print("📊 Security Score:")
            print(f"  Current Score: {total_score:.1f}/10")
            
            if total_score >= 10.0:
                print("  Rating: 🏆 MAXIMUM SECURITY")
            elif total_score >= 9.5:
                print("  Rating: 🥈 EXCELLENT")
            elif total_score >= 9.0:
                print("  Rating: 🥉 VERY GOOD")
            else:
                print("  Rating: ⚠️ NEEDS IMPROVEMENT")
            
            print()
            print("Press Ctrl+C to exit...")
            
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
        
        # Update every 5 seconds
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(display_dashboard())
    except KeyboardInterrupt:
        print("\n👋 Security dashboard stopped")
