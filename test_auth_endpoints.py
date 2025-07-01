#!/usr/bin/env python3
"""
Test Super Admin API endpoints with authentication
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_with_auth():
    """Test API endpoints with authentication"""
    
    session = requests.Session()
    
    print("=== TESTING WITH AUTHENTICATION ===\n")
    
    # Try to simulate authentication by setting session cookie
    print("1. Attempting to set admin session...")
    
    # Method 1: Try to access login and post credentials
    login_response = session.get(f"{BASE_URL}/auth/admin/login")
    print(f"Login page status: {login_response.status_code}")
    
    # Try to login with working credentials
    login_data = {
        'email': 'admin@youcloudtech.com',
        'password': 'admin123'
    }
    
    login_post = session.post(f"{BASE_URL}/auth/admin/login", data=login_data, allow_redirects=False)
    print(f"Login attempt status: {login_post.status_code}")
    
    if login_post.status_code == 302:
        print(f"Redirect location: {login_post.headers.get('Location', 'None')}")
    
    # Now test API endpoints with session
    print("\n2. Testing API endpoints with session...")
    
    endpoints = [
        "/super-admin/api/dashboard/metrics",
        "/super-admin/api/escalation/dashboard", 
        "/super-admin/api/critical-alerts"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Success: {data.get('success', 'Unknown')}")
                    if isinstance(data, dict):
                        # Print key metrics if this is dashboard metrics
                        if 'activeTickets' in data:
                            print(f"   Active Tickets: {data.get('activeTickets')}")
                            print(f"   SLA Breaches: {data.get('slaBreaches')}")
                            print(f"   Active Partners: {data.get('activePartners')}")
                            print(f"   Bot Interactions: {data.get('botInteractions')}")
                        elif 'within_sla' in data:
                            print(f"   Within SLA: {data.get('within_sla')}")
                            print(f"   SLA Warning: {data.get('sla_warning')}")
                            print(f"   SLA Breached: {data.get('sla_breached')}")
                        elif 'alerts' in data:
                            print(f"   Alerts count: {len(data.get('alerts', []))}")
                except json.JSONDecodeError:
                    print(f"   Non-JSON response: {response.text[:100]}...")
            else:
                print(f"   Failed: {response.text[:100]}...")
        except Exception as e:
            print(f"   Exception: {e}")

def test_direct_session():
    """Test by directly setting session data"""
    print("\n=== TESTING WITH DIRECT SESSION ===\n")
    
    session = requests.Session()
    
    # Set session cookie manually (this simulates being logged in)
    session.cookies.set('admin_logged_in', 'true', domain='127.0.0.1')
    
    endpoints = [
        "/super-admin/api/dashboard/metrics",
        "/super-admin/api/escalation/dashboard"
    ]
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response received successfully")
                if isinstance(data, dict) and 'success' in data:
                    print(f"   Success: {data['success']}")
                    # Print some data if available
                    if 'activeTickets' in data:
                        print(f"   Dashboard metrics received")
                    elif 'within_sla' in data:
                        print(f"   Escalation data received")
            else:
                print(f"   Status {response.status_code}: {response.text[:100]}...")
        except Exception as e:
            print(f"   Exception: {e}")
        print()

if __name__ == "__main__":
    test_with_auth()
    test_direct_session()
