#!/usr/bin/env python3
"""
Run the MSSQL setup script and capture output
"""

import subprocess
import sys

def run_setup():
    try:
        print("Starting MSSQL setup...")
        result = subprocess.run([sys.executable, 'setup_mssql.py'], 
                               capture_output=True, text=True, timeout=120)
        
        print("=== STDOUT ===")
        print(result.stdout)
        print("\n=== STDERR ===")
        print(result.stderr)
        print(f"\n=== Return Code: {result.returncode} ===")
        
        if result.returncode == 0:
            print("✅ Setup completed successfully!")
        else:
            print("❌ Setup failed!")
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out after 120 seconds")
    except Exception as e:
        print(f"❌ Error running script: {e}")

if __name__ == "__main__":
    run_setup()
