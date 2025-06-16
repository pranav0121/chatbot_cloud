#!/usr/bin/env python3
"""
Quick Flask Health Check
"""

import requests
import time

def check_flask_health():
    """Check if Flask is running and responding"""
    try:
        print("🔍 Checking Flask application health...")
        
        # Test basic endpoint
        response = requests.get("http://localhost:5000/test", timeout=5)
        if response.status_code == 200:
            print("✅ Flask application is running and responding")
            return True
        else:
            print(f"❌ Flask responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask application")
        return False
    except Exception as e:
        print(f"❌ Error checking Flask: {e}")
        return False

if __name__ == "__main__":
    # Give Flask a moment to start up
    print("⏳ Waiting for Flask to start...")
    time.sleep(3)
    
    if check_flask_health():
        print("🎉 Flask is ready!")
    else:
        print("⚠️  Flask may still be starting up...")
