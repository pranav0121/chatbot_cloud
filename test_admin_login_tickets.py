#!/usr/bin/env python3
"""
Test script to login as admin and test the tickets API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_admin_login_and_tickets():
    """Login as admin and test the tickets API"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Step 1: Testing admin login...")
    
    # Test login with known admin credentials
    login_data = {
        'email': 'admin@youcloudtech.com',
        'password': 'admin123'  # Default password
    }
    
    try:
        # First, get the login page to establish session
        login_page = session.get(f"{BASE_URL}/auth/admin/login")
        print(f"Login page status: {login_page.status_code}")
        
        # Attempt login
        login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data)
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response headers: {dict(login_response.headers)}")
        
        # Check if redirected (successful login usually redirects)
        if login_response.status_code == 302:
            print("✓ Login appears successful (redirect received)")
        elif login_response.status_code == 200:
            print("⚠ Login returned 200, checking content...")
            if "dashboard" in login_response.text.lower() or "admin" in login_response.text.lower():
                print("✓ Login appears successful (admin content detected)")
            else:
                print("✗ Login may have failed")
                print(f"Response snippet: {login_response.text[:500]}")
        
        print("\nStep 2: Testing admin tickets API...")
        
        # Now test the tickets API with the authenticated session
        tickets_response = session.get(f"{BASE_URL}/api/admin/tickets")
        print(f"Tickets API status: {tickets_response.status_code}")
        
        if tickets_response.status_code == 200:
            data = tickets_response.json()
            print(f"✓ Tickets API successful!")
            print(f"Response structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict):
                tickets = data.get('tickets', [])
                print(f"Number of tickets: {len(tickets)}")
                
                if tickets:
                    print(f"\nFirst ticket example:")
                    print(json.dumps(tickets[0], indent=2))
                    print(f"\nAll ticket IDs: {[t.get('id') for t in tickets[:10]]}")  # Show first 10
                else:
                    print("No tickets found in response")
                    
                print(f"Pagination info: {data.get('pagination', 'N/A')}")
            else:
                print(f"Unexpected response format")
                print(f"Full response: {data}")
                
        elif tickets_response.status_code == 401:
            print("✗ Still getting authentication error")
            print(f"Response: {tickets_response.text}")
        else:
            print(f"✗ Unexpected status code: {tickets_response.status_code}")
            print(f"Response: {tickets_response.text}")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_admin_login_and_tickets()
