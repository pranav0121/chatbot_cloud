#!/usr/bin/env python3
"""
Simple test to check if the route exists
"""

import requests

BASE_URL = "http://127.0.0.1:5001"

def simple_test():
    """Simple test of the route"""
    
    # Create session for admin login
    session = requests.Session()
    
    # Login first
    login_data = {
        'email': 'superadmin@youcloudtech.com', 
        'password': 'superadmin123'
    }
    
    login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code not in [200, 302]:
        print("Login failed")
        return
    
    # Test the specific route
    test_ticket_id = 51
    escalate_url = f"{BASE_URL}/super-admin/api/escalation/test-force/{test_ticket_id}"
    
    print(f"Testing URL: {escalate_url}")
    
    # Try GET first to see if route exists
    get_response = session.get(escalate_url)
    print(f"GET response: {get_response.status_code}")
    if get_response.status_code != 405:  # Method not allowed is expected
        print(f"GET response text: {get_response.text}")
    
    # Try POST
    post_data = {'level': 1, 'comment': 'test'}
    post_response = session.post(escalate_url, json=post_data)
    print(f"POST response: {post_response.status_code}")
    print(f"POST response text: {post_response.text}")

if __name__ == "__main__":
    simple_test()
