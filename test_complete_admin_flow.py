#!/usr/bin/env python3
"""
Test the complete admin flow: login -> admin panel -> tickets API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_complete_admin_flow():
    """Test the complete admin authentication and ticket loading flow"""
    
    session = requests.Session()
    
    print("=== COMPLETE ADMIN FLOW TEST ===\n")
    
    print("Step 1: Access admin panel without authentication (should redirect)")
    try:
        admin_page = session.get(f"{BASE_URL}/admin", allow_redirects=False)
        print(f"Admin page status: {admin_page.status_code}")
        if admin_page.status_code == 302:
            print(f"✓ Correctly redirected to: {admin_page.headers.get('Location', 'unknown')}")
        elif admin_page.status_code == 200:
            print("⚠ Admin page accessible without login - this may be incorrect")
        else:
            print(f"Unexpected status: {admin_page.status_code}")
    except Exception as e:
        print(f"Error accessing admin page: {e}")
    
    print("\nStep 2: Get admin login page")
    try:
        login_page = session.get(f"{BASE_URL}/auth/admin/login")
        print(f"Login page status: {login_page.status_code}")
        if login_page.status_code == 200:
            print("✓ Login page accessible")
        else:
            print(f"✗ Login page error: {login_page.status_code}")
    except Exception as e:
        print(f"Error getting login page: {e}")
    
    print("\nStep 3: Submit admin login credentials")
    login_data = {
        'email': 'admin@youcloudtech.com',
        'password': 'admin123'
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {login_response.status_code}")
        print(f"Set cookies: {login_response.headers.get('Set-Cookie', 'None')}")
        
        if login_response.status_code == 302:
            redirect_location = login_response.headers.get('Location', '')
            print(f"✓ Login successful, redirecting to: {redirect_location}")
            
            # Follow the redirect
            if redirect_location:
                if redirect_location.startswith('/'):
                    redirect_url = f"{BASE_URL}{redirect_location}"
                else:
                    redirect_url = redirect_location
                    
                print(f"\nStep 4: Following redirect to admin dashboard")
                dashboard_response = session.get(redirect_url)
                print(f"Dashboard status: {dashboard_response.status_code}")
                if dashboard_response.status_code == 200:
                    print("✓ Admin dashboard accessible after login")
                    if "tickets" in dashboard_response.text.lower():
                        print("✓ Dashboard contains tickets-related content")
                    else:
                        print("⚠ Dashboard may not have tickets section")
                else:
                    print(f"✗ Dashboard error: {dashboard_response.status_code}")
        else:
            print(f"✗ Login failed with status: {login_response.status_code}")
            print(f"Response: {login_response.text[:500]}")
            
    except Exception as e:
        print(f"Error during login: {e}")
    
    print("\nStep 5: Test tickets API with authenticated session")
    try:
        tickets_response = session.get(f"{BASE_URL}/api/admin/tickets")
        print(f"Tickets API status: {tickets_response.status_code}")
        
        if tickets_response.status_code == 200:
            data = tickets_response.json()
            tickets = data.get('tickets', [])
            print(f"✓ Tickets API working! Found {len(tickets)} tickets")
            
            if tickets:
                print(f"Sample ticket: ID {tickets[0].get('id')}, Subject: '{tickets[0].get('subject', 'No subject')}'")
            else:
                print("⚠ No tickets found (this may be normal if database is empty)")
                
        elif tickets_response.status_code == 401:
            print("✗ Tickets API still requires authentication - session issue")
        else:
            print(f"✗ Tickets API error: {tickets_response.status_code}")
            print(f"Response: {tickets_response.text}")
            
    except Exception as e:
        print(f"Error testing tickets API: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_complete_admin_flow()
