#!/usr/bin/env python3
"""
Direct test of specific API endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_specific_endpoint():
    session = requests.Session()
    
    # First get the login page to establish session
    get_login = session.get(f"{BASE_URL}/auth/admin/login")
    print(f"Get login page status: {get_login.status_code}")
    
    # Login first
    login_data = {
        'email': 'admin@youcloudtech.com', 
        'password': 'admin123'
    }
    
    login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data, allow_redirects=False)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 302:
        print(f"Redirect to: {login_response.headers.get('Location')}")
        
        # Test the specific dashboard metrics endpoint
        print("\nTesting /super-admin/api/dashboard/metrics")
        response = session.get(f"{BASE_URL}/super-admin/api/dashboard/metrics")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Full response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Login failed. Response: {login_response.text[:200]}...")

if __name__ == "__main__":
    test_specific_endpoint()
