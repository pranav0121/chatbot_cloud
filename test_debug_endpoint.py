#!/usr/bin/env python3
"""
Test debug database endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_debug_endpoint():
    session = requests.Session()
    
    # Login
    login_data = {
        'email': 'admin@youcloudtech.com', 
        'password': 'admin123'
    }
    
    login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data, allow_redirects=False)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 302:
        # Test the debug endpoint
        print("\nTesting /super-admin/api/debug/database")
        response = session.get(f"{BASE_URL}/super-admin/api/debug/database")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Debug response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_debug_endpoint()
