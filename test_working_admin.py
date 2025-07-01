#!/usr/bin/env python3
"""
Test force escalation with working admin credentials
"""

import requests
import json
import sys

def test_with_working_admin():
    base_url = "http://127.0.0.1:5000"
    
    print("=== TESTING WITH WORKING ADMIN CREDENTIALS ===")
    
    # Use working admin credentials
    working_credentials = [
        {'email': 'admin@youcloudtech.com', 'password': 'admin123'},
        {'email': 'admin@supportcenter.com', 'password': 'admin123'},
        {'email': 'admin@chatbot.com', 'password': 'admin123'},
    ]
    
    for creds in working_credentials:
        print(f"\n=== Testing with {creds['email']} ===")
        
        session = requests.Session()
        
        # Login
        print("1. Logging in...")
        login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
        print(f"Login status: {login_response.status_code}")
        print(f"Final URL: {login_response.url}")
        
        if 'admin' in login_response.url or 'dashboard' in login_response.url:
            print("Login successful!")
            
            # Test super admin API access
            print("2. Testing super admin API access...")
            api_response = session.get(f"{base_url}/super-admin/api/dashboard-metrics")
            print(f"Super admin API status: {api_response.status_code}")
            
            if api_response.status_code == 200:
                print("Super admin access works!")
                
                # Test force escalation
                print("3. Testing force escalation...")
                escalation_response = session.post(
                    f"{base_url}/super-admin/api/escalation/force/1",
                    json={'level': 1, 'comment': 'Test escalation'},
                    headers={'Content-Type': 'application/json'}
                )
                print(f"Escalation status: {escalation_response.status_code}")
                
                try:
                    escalation_data = escalation_response.json()
                    print(f"Escalation response: {json.dumps(escalation_data, indent=2)}")
                except:
                    print(f"Escalation response text: {escalation_response.text}")
                
                if escalation_response.status_code == 200:
                    print("SUCCESS! Force escalation worked!")
                    return session, creds
                else:
                    print("Force escalation failed")
            else:
                print(f"Super admin access denied: {api_response.text[:200]}")
        else:
            print("Login failed")
    
    print("All admin credentials failed for super admin access")
    return None, None

if __name__ == "__main__":
    test_with_working_admin()
