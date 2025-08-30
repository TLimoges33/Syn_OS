#!/usr/bin/env python3
"""
Environment Configuration Validation Script
Validates that all required environment variables are present and valid
"""

import os
import sys
from typing import Dict, List, Any

def validate_environment(env_name: str = 'development') -> Dict[str, Any]:
    """Validate environment configuration"""
    
    required_vars = [
        'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD',
        'REDIS_HOST', 'REDIS_PORT', 'NATS_URL', 'JWT_SECRET'
    ]
    
    missing_vars = []
    invalid_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif var.endswith('_PORT'):
            try:
                port = int(value)
                if not (1 <= port <= 65535):
                    invalid_vars.append(f"{var}: port {port} out of range")
            except ValueError:
                invalid_vars.append(f"{var}: not a valid port number")
    
    # Validate database connection
    try:
        import psycopg2
        conn_string = f"host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')} dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}"
        conn = psycopg2.connect(conn_string)
        conn.close()
        db_connection = True
    except Exception as e:
        db_connection = False
        invalid_vars.append(f"Database connection failed: {str(e)}")
    
    return {
        'environment': env_name,
        'valid': len(missing_vars) == 0 and len(invalid_vars) == 0,
        'missing_variables': missing_vars,
        'invalid_variables': invalid_vars,
        'database_connection': db_connection
    }

if __name__ == "__main__":
    env_name = sys.argv[1] if len(sys.argv) > 1 else 'development'
    result = validate_environment(env_name)
    
    print(f"Environment Validation Report: {env_name}")
    print("=" * 50)
    print(f"Status: {'VALID' if result['valid'] else 'INVALID'}")
    
    if result['missing_variables']:
        print(f"Missing Variables: {', '.join(result['missing_variables'])}")
    
    if result['invalid_variables']:
        print("Invalid Variables:")
        for var in result['invalid_variables']:
            print(f"  - {var}")
    
    print(f"Database Connection: {'OK' if result['database_connection'] else 'FAILED'}")
    
    sys.exit(0 if result['valid'] else 1)
